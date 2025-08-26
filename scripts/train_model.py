# scripts/train_model.py
from models.train_predictor import train_predictor


def main():
    print("🚀 Démarrage de l'entraînement du modèle de prédiction")
    print("   → Dataset utilisé : data/cleaned_synthetic_conversations.json")
    print("   → Modèle sauvegardé : models/saved/status_predictor.pkl\n")

    try:
        train_predictor()
        print("\n✅ Entraînement terminé avec succès !")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'entraînement : {str(e)}")
        print("   Vérifie que :")
        print("   - Le fichier data/raw_conversations.json existe")
        print("   - Il contient des conversations valides")


if __name__ == "__main__":
    main()