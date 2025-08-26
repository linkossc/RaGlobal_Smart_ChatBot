# scripts/test_model.py
import joblib
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import numpy as np
from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "saved" / "status_predictor.pkl"

# Importer la connexion à MongoDB
from database.mongo_client import get_all_leads

def load_model():
    """Charge le modèle sauvegardé"""
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Modèle non trouvé : {MODEL_PATH}")
        print("   → Lance d'abord : python scripts/train_model.py")
        return None, None

    try:
        data = joblib.load(MODEL_PATH)
        model = data["model"]
        vectorizer = data["vectorizer"]
        print(f"✅ Modèle chargé depuis : {MODEL_PATH}")
        return model, vectorizer
    except Exception as e:
        print(f"❌ Erreur de chargement : {e}")
        return None, None


def generate_test_data():
    """Génère les données de test depuis MongoDB"""
    print("🔍 Chargement des données de test depuis MongoDB...")

    conversations = get_all_leads()
    if not conversations:
        print("❌ Aucune conversation trouvée dans MongoDB")
        return None, None

    X, y_true = [], []

    valid_statuses = {"Qualified", "To follow up", "Unqualified"}

    for conv in conversations:
        status = conv.get("status")
        if not status or status not in valid_statuses:
            continue

        client_msgs = [
            msg["text"] for msg in conv.get("messages", [])
            if isinstance(msg, dict) and msg.get("sender_type") == "contact" and msg.get("text")
        ]

        if not client_msgs:
            continue

        # Utiliser toute la conversation du client
        full_conversation = " ||| ".join(client_msgs)
        X.append(full_conversation)
        y_true.append(status)

    if not X:
        print("❌ Aucune donnée valide extraite")
        return None, None

    print(f"✅ {len(X)} conversations chargées pour le test")
    return X, y_true


def test_model():
    """Teste le modèle et affiche les métriques"""
    print("🧪 Démarrage du test du modèle de prédiction\n")

    # 1. Charger le modèle
    model, vectorizer = load_model()
    if not model or not vectorizer:
        return

    # 2. Charger les données
    X, y_true = generate_test_data()
    if not X or not y_true:
        return

    # 3. Vectoriser les données
    try:
        X_vec = vectorizer.transform(X)
    except Exception as e:
        print(f"❌ Échec de vectorisation : {e}")
        return

    # 4. Prédire
    y_pred = model.predict(X_vec)

    # 5. Calculer les métriques
    accuracy = accuracy_score(y_true, y_pred)
    print("📊 RÉSULTATS DE L'ÉVALUATION\n")
    print(f"🎯 Accuracy : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\n📋 Classification Report :")
    print(classification_report(y_true, y_pred, target_names=sorted(list(set(y_true)))))

    print("\n🔢 Matrice de confusion :")
    labels = sorted(list(set(y_true)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print(f"{'':<15} {'Predicted':<}")
    print(f"{'Actual':<15} {' '.join([f'{lbl:>12}' for lbl in labels])}")
    for i, row in enumerate(cm):
        print(f"{labels[i]:<15} {' '.join([f'{val:>12}' for val in row])}")

    # 6. Confiance moyenne (optionnel, si tu veux plus tard)
    if hasattr(model, "predict_proba"):
        probas = model.predict_proba(X_vec)
        avg_confidence = np.max(probas, axis=1).mean()
        print(f"\n💡 Confiance moyenne : {avg_confidence:.4f}")


if __name__ == "__main__":
    test_model()