# routes/route.py
from flask import render_template, request, jsonify, session
from chatbot.conversation_engine import QualificationChatbot

# Stockage simple des sessions par IP
sessions = {}

def get_session():
    session_id = request.remote_addr
    if session_id not in sessions:
        sessions[session_id] = QualificationChatbot()
    return sessions[session_id]

def register_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/chat", methods=["POST"])
    def chat():
        sess = get_session()
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message vide"}), 400

        result = sess.process_message(user_message)
        return jsonify(result)

    # ✅ NOUVELLE : API Endpoint (version publique)
    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        """
        API publique pour intégrer le chatbot dans d'autres apps
        """
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Champ 'message' requis"}), 400

        # Optionnel : clé API pour sécuriser
        # api_key = request.headers.get("X-API-Key")
        # if api_key != "ton_api_key_secrete":
        #     return jsonify({"error": "Accès refusé"}), 401

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Message vide"}), 400

        try:
            sess = get_session()
            result = sess.process_message(user_message)

            # Format API clair
            api_response = {
                "success": True,
                "data": {
                    "response": result.get("response", "Désolé, je n'ai pas compris."),
                    "score": result.get("score", 0),
                    "phase": result.get("phase", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            return jsonify(api_response)

        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Erreur interne du serveur",
                "details": str(e) if app.debug else None
            }), 500

    @app.route("/api/status")
    def api_status():
        """Vérifie si l'API est en marche"""
        return jsonify({
            "status": "running",
            "service": "RaGlobal Chatbot API",
            "version": "1.0"
        })