# models/predictor.py
import joblib
import os
from pathlib import Path
from .scoring_system import calculate_score_answer
from chatbot.conversation_engine import QualificationChatbot

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "saved" / "status_predictor.pkl"

class StatusPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        try:
            if not MODEL_PATH.exists():
                print(f"❌ Modèle non trouvé : {MODEL_PATH}")
                return

            data = joblib.load(MODEL_PATH)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
            self.is_loaded = True
            print("✅ Modèle de prédiction chargé (LogisticRegression + TF-IDF)")
        except Exception as e:
            print(f"❌ Erreur de chargement du modèle : {e}")

    def predict(self, partial_conversation):
        """
        Prédit le statut du client
        partial_conversation : "msg1 ||| msg2 ||| ..."
        """
        if not self.is_loaded:
            return "En cours", 0.0

        try:
            X = self.vectorizer.transform([partial_conversation])
            proba = self.model.predict_proba(X)[0]
            status = self.model.predict(X)[0]
            confidence = max(proba)
            return status, confidence
        except:
            return "En cours", 0.0