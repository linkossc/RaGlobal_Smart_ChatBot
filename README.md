ChatBot_RaGlobal 🤖 Description du projet Ce projet est un chatbot alimenté par Flask et plusieurs modèles de machine learning, conçu pour automatiser les réponses aux questions des étudiants et des parents. Il intègre des fonctionnalités de nettoyage de données, de fusion de datasets, de génération de données synthétiques, et d'entraînement de plusieurs algorithmes de classification (Random Forest, Naive Bayes, Régression Logistique, et LSTM) pour déterminer l'intention des messages entrants et fournir une réponse appropriée.

Le but est de créer un système de support client intelligent et scalable pour RaGlobal.

✨ Fonctionnalités clés Préparation de données automatisée : Nettoyage et transformation de fichiers CSV en JSON, et fusion de différents datasets pour la formation.

Génération de données synthétiques : Création et enrichissement de conversations synthétiques pour augmenter la taille du dataset de formation.

Multiples modèles de ML : Entraînement de quatre modèles différents pour la classification de texte, permettant une comparaison de leurs performances.

Architecture Flask : Un serveur web léger pour héberger l'application et les endpoints de l'API.

API REST : Endpoint /predict pour interagir avec le chatbot.

🚀 Démarrage rapide Suivez ces instructions pour lancer le projet en local.

Prérequis Assurez-vous d'avoir Python 3.8 ou une version plus récente et pip installés sur votre machine.
