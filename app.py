# app.py
from flask import Flask
import os
from scripts.auto_train_monitor import start_monitor
from routes.route import register_routes

# ─────────────────────────────────────────────
# 🔧 Démarrer le moniteur d'entraînement
# ─────────────────────────────────────────────
print("🤖 Démarrage du moniteur d'entraînement en arrière-plan...")
try:
    start_monitor()
    print("✅ Auto-Trainer démarré")
except Exception as e:
    print(f"❌ Échec du démarrage du moniteur : {e}")

# ─────────────────────────────────────────────
# 🌐 Initialiser Flask
# ─────────────────────────────────────────────
app = Flask(__name__)

# 🔐 Clé secrète (essentielle pour les sessions)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "raglobal_default_secret_key")

# ─────────────────────────────────────────────
# 📌 Enregistrer les routes
# ─────────────────────────────────────────────
try:
    register_routes(app)
    print("✅ Routes enregistrées avec succès")
except Exception as e:
    print(f"❌ Erreur lors de l'enregistrement des routes : {e}")
    raise

# ─────────────────────────────────────────────
# 🚀 Lancer l'application
# ─────────────────────────────────────────────
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("FLASK_PORT", 5000))

    print(f"🚀 Démarrage de l'application Flask sur http://127.0.0.1:{port}")
    print(f"🔧 Mode debug : {'Activé' if debug_mode else 'Désactivé'}")
    print("💡 Appuyez sur CTRL+C pour arrêter le serveur")

    app.run(
        debug=debug_mode,
        host="0.0.0.0",  # Pour accès local et réseau
        port=port
    )