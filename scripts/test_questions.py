# scripts/test_questions.py
import json
import os

# 🔧 Chemin relatif depuis scripts/ vers chatbot/questions.json
file_path = os.path.join("..", "chatbot", "questions.json")  # ← ".." remonte d'un niveau

print(f"📁 Chemin absolu : {os.path.abspath(file_path)}")

if not os.path.exists(file_path):
    print("❌ Fichier non trouvé !")
    print("   → Vérifie que le fichier existe dans : ../chatbot/questions.json")
else:
    print("✅ Fichier trouvé")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("❌ Le fichier est vide !")
            else:
                print(f"📄 Contenu (50 premiers caractères) : {content[:50]}...")
                f.seek(0)
                data = json.load(f)
                print(f"✅ JSON chargé ! {len(data['questions'])} questions")
    except Exception as e:
        print(f"❌ Erreur : {e}")