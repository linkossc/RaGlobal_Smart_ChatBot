# database/mongo_client.py
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
leads_collection = db[COLLECTION_NAME]

def save_lead(lead_data):
    return leads_collection.insert_one(lead_data).inserted_id

def get_all_leads():
    """Récupère toutes les conversations depuis MongoDB"""
    return list(leads_collection.find({}))