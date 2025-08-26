# scripts/auto_train_monitor.py
import time
import threading
from models.train_predictor import train_predictor
from database.mongo_client import leads_collection

# Configuration
CHECK_INTERVAL = 300  # Vérifie toutes les 60 secondes
MIN_NEW_CONVERSATIONS = 10
last_count = 0  # Nombre initial de conversations


def monitor_loop():
    """Boucle principale de surveillance"""
    global last_count
    print("🤖 Auto-Trainer démarré")

    # Compte initial
    last_count = leads_collection.count_documents({})
    print(f"📦 Base initiale : {last_count} conversations")

    while True:
        try:
            current_count = leads_collection.count_documents({})
            new_count = current_count - last_count

            if new_count >= MIN_NEW_CONVERSATIONS:
                print(f"\n🆕 {new_count} nouvelles conversations détectées !")
                print("🔄 Démarrage du ré-entraînement...")

                success = train_predictor()

                if success:
                    last_count = current_count
                    print(f"✅ Entraînement terminé. Prochaine vérification dans {CHECK_INTERVAL}s.")
                else:
                    print("⚠️  Échec de l'entraînement. Nouvelle tentative dans 1 minute.")
            else:
                print(f"⏳ {new_count}/{MIN_NEW_CONVERSATIONS} nouvelles conversations (en attente)")

        except Exception as e:
            print(f"❌ Erreur de surveillance : {e}")

        time.sleep(CHECK_INTERVAL)


def start_monitor():
    """Démarre le moniteur dans un thread"""
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    print("✅ Moniteur d'entraînement lancé en arrière-plan")
    return thread