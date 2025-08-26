# config/settings.py
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "chatbot_db"
COLLECTION_NAME = "leads"

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Seuil de qualification
QUALIFICATION_THRESHOLD = 70

# Environnement
ENV = os.getenv("ENV", "dev")