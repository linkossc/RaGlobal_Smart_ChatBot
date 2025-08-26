# chatbot/gemini_assistant.py
import requests
from config.settings import GEMINI_API_KEY
import json

# 🔗 URL de l'API Gemini (REST)
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class GeminiAssistant:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY non trouvée dans .env")

    def _call_api(self, prompt):
        """
        Appelle l'API Gemini via REST
        """
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500,
                "topP": 0.95,
                "topK": 40
            }
        }

        try:
            response = requests.post(
                f"{API_URL}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"❌ Erreur API Gemini : {e}")
            return "N7eb net2akd m3a l'équipe w n3awdou n9olk"

    def generate_response(self, question, context=""):
        """
        Génère une réponse en tunisien latin basée sur le contexte
        """
        prompt = f"""
        Tu es un conseiller académique pour des études en Malaisie.
        Un étudiant tunisien te pose cette question en dialecte :
        "{question}"

        Contexte de la conversation :
        {context}

        Règles :
        - Réponds en tunisien latin (pas en arabe ni en français formel)
        - Sois naturel, proche du langage parlé (ex: "ya", "belehi", "n7eb")
        - Si tu ne connais pas la réponse, dis "N7eb net2akd m3a l'équipe w n3awdou n9olk"
        - Ne donne pas d'informations fausses
        - Garde un ton professionnel mais chaleureux

        Réponds UNIQUEMENT avec la réponse, pas d'explication.
        """

        return self._call_api(prompt)