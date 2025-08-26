# models/train_predictor.py
import joblib
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression  # ← Changé ici

# Importer la fonction depuis mongo_client
from database.mongo_client import get_all_leads

# 🔧 Définir le chemin absolu du projet
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_SAVE_PATH = PROJECT_ROOT / "models" / "saved" / "status_predictor.pkl"

def generate_training_data():
    """
    Génère les données d'entraînement depuis MongoDB
    X = ["msg1", "msg1 ||| msg2", ...]
    y = [statut]
    """
    print("🔍 Chargement des conversations depuis MongoDB...")
    try:
        conversations = get_all_leads()
    except Exception as e:
        raise Exception(f"❌ Échec de chargement depuis MongoDB : {e}")

    if not conversations:
        raise Exception("❌ Aucune conversation trouvée. As-tu importé les données ?")

    X, y = [], []
    valid_statuses = {"Qualified", "To follow up", "Unqualified"}

    for conv in conversations:
        status = conv.get("status")
        if not status or status not in valid_statuses:
            continue

        client_msgs = [
            msg["text"] for msg in conv.get("messages", [])
            if isinstance(msg, dict)
            and msg.get("sender_type") == "contact"
            and msg.get("text")
        ]

        if not client_msgs:
            continue

        for i in range(1, len(client_msgs) + 1):
            partial = " ||| ".join(client_msgs[:i])
            X.append(partial)
            y.append(status)

    print(f"✅ {len(X)} exemples générés à partir de {len(conversations)} conversations")
    return X, y


def train_predictor():
    """
    Entraîne un modèle LogisticRegression avec un TF-IDF optimisé
    """
    try:
        X, y = generate_training_data()

        if len(X) < 5:
            raise ValueError("❌ Pas assez de données pour entraîner (minimum 5 exemples)")

        # ✅ TF-IDF optimisé pour le dialecte tunisien
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),              # ← 1,2,3-grams pour capturer les phrases
            max_features=10000,              # ← Plus de features
            lowercase=True,
            stop_words=None,
            token_pattern=r'\b[a-zA-Z0-9]+\b'  # ← Garde les mots avec chiffres (ex: "10.5", "bac")
        )
        X_vec = vectorizer.fit_transform(X)

        # ✅ Modèle : Logistic Regression (meilleure calibration que RF)
        model = LogisticRegression(
            random_state=42,
            class_weight="balanced",         # ← Compense les déséquilibres de classes
            max_iter=1000,
            C=1.0                            # ← Régularisation standard
        )
        model.fit(X_vec, y)

        # ✅ Sauvegarde
        MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": model,
            "vectorizer": vectorizer,
            "classes": sorted(list(set(y)))
        }, MODEL_SAVE_PATH)

        print(f"✅ Modèle LR entraîné avec succès !")
        print(f"   → Échantillons : {len(X)}")
        print(f"   → Classes : {sorted(list(set(y)))}")
        print(f"   → N-grams : {vectorizer.ngram_range}")
        print(f"   → Sauvegardé dans : {MODEL_SAVE_PATH}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement : {str(e)}")
        return False