# chatbot/response_retriever.py
import joblib
import numpy as np
from pathlib import Path
from .gemini_assistant import GeminiAssistant
from database.mongo_client import leads_collection
import re

# Chemin du modèle
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "saved" / "status_predictor.pkl"

# Normalisation dialectale
NORMALIZATION_MAP = {
    r'\b3andi\b': '3andi', r'\bma3andich\b': 'ma3andich', r'\bma3andi\b': 'ma3andich',
    r'\b3andek\b': '3andek', r'\bma3andek\b': 'ma3andek',
    r'\b3andi bac\b': 'bac', r'\bkhdhitou\b': 'bac', r'\bfinich\b': 'bac',
    r'\bboursa\b': 'bourse', r'\bboursat\b': 'bourse',
    r'\bmastere\b': 'master', r'\bmaster\b': 'master',
    r'\binformatique\b': 'info', r'\bcomputer science\b': 'info',
    r'\b9dim\b': '9dim', r'\ble 9dim\b': '9dim',
    r'\ble 3andi\b': '3andi', r'\ble ma3andich\b': 'ma3andich',
    r'\bey\b': 'oui', r'\beyy\b': 'oui', r'\bna3am\b': 'oui',
    r'\bla\b': 'non', r'\lem\b': 'non', r'\bma\b': 'non',
    r'\bbch\b': 'bch', r'\bnheb\b': 'nheb', r'\bn7eb\b': 'nheb',
    r'\b3ala9a\b': '3ala9a', r'\bw9fou\b': '3ala9a',
    r'\benglish\b': 'anglais', r'\bielts\b': 'anglais', r'\btoefl\b': 'anglais',
    r'\bvisa\b': 'visa', r'\bflywire\b': 'flywire'
}


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    for pattern, replacement in NORMALIZATION_MAP.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class ResponseRetriever:
    def __init__(self, gemini_assistant=None):
        self.gemini = gemini_assistant or GeminiAssistant()
        self.conversations = self.load_from_mongodb()
        self.vectorizer, self.prediction_model = self.load_predictor()

        if self.vectorizer and self.conversations:
            self.question_vectors = self._precompute_vectors()
        else:
            self.question_vectors = []

    def load_predictor(self):
        try:
            if not MODEL_PATH.exists():
                print(f"❌ Modèle non trouvé : {MODEL_PATH}")
                return None, None
            data = joblib.load(MODEL_PATH)
            print(f"✅ Modèle chargé depuis : {MODEL_PATH}")
            return data["vectorizer"], data["model"]
        except Exception as e:
            print(f"❌ Erreur : {e}")
            return None, None

    def load_from_mongodb(self):
        try:
            db_conversations = list(leads_collection.find({}))
            knowledge = []
            for conv in db_conversations:
                messages = conv.get("messages", [])
                for i, msg in enumerate(messages):
                    if (msg.get("sender_type") == "contact"
                            and i + 1 < len(messages)
                            and messages[i + 1].get("sender_type") == "user"):
                        question = msg["text"].strip()
                        answer = messages[i + 1]["text"].strip()
                        if question and answer:
                            knowledge.append({
                                "question": question,
                                "answer": answer
                            })
            print(f"✅ {len(knowledge)} paires Q/R chargées")
            return knowledge
        except Exception as e:
            print(f"❌ Erreur MongoDB : {e}")
            return []

    def _precompute_vectors(self):
        if not self.vectorizer or not self.conversations:
            return []
        questions = [clean_text(item["question"]) for item in self.conversations]
        return self.vectorizer.transform(questions)

    def find_response(self, user_message):
        """
        Trouve la meilleure réponse avec plusieurs niveaux de fallback
        """
        if not self.conversations or not self.vectorizer:
            return None

        cleaned_query = clean_text(user_message)
        if not cleaned_query:
            return None

        # 🔍 1. Recherche TF-IDF
        try:
            query_vec = self.vectorizer.transform([cleaned_query])
            query_norm = np.linalg.norm(query_vec.toarray()[0])
            if query_norm == 0:
                return None
        except:
            return None

        best_score = -1
        best_idx = -1
        query_array = query_vec.toarray()[0]

        for idx, item_vec in enumerate(self.question_vectors):
            item_array = item_vec.toarray()[0]
            item_norm = np.linalg.norm(item_array)
            if item_norm == 0:
                continue
            cosine_sim = np.dot(query_array, item_array) / (query_norm * item_norm)
            if cosine_sim > best_score:
                best_score = cosine_sim
                best_idx = idx

        # ✅ Bonne similarité → retourne la réponse
        if best_score >= 0.25:
            return self.conversations[best_idx]["answer"]

        # 🔁 2. Fallback : Recherche par mots-clés simples
        keywords = ["bourse", "bac", "master", "info", "anglais", "flywire", "visa", "engineering"]
        for kw in keywords:
            if kw in cleaned_query:
                for item in self.conversations:
                    if kw in clean_text(item["question"]):
                        return item["answer"]

        # 🚨 3. Fallback : Gemini cherche sémantiquement
        kb_sample = "\n".join([
            f"Q: {item['question']}\nR: {item['answer']}\n---"
            for item in self.conversations[:20]
        ])
        prompt = f"""
        Trouve la meilleure réponse parmi celles-ci :
        {kb_sample}

        Question du client : "{user_message}"

        Règles :
        1. Ne réponds qu'avec une réponse de la base
        2. Reformule-la en tunisien latin naturel
        3. Si aucune pertinente, dis : "On va te répondre bientôt, merci pour ta patience !"
        """
        try:
            return self.gemini.generate_response(prompt)
        except:
            return None