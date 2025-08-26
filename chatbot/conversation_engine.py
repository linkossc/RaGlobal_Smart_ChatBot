# chatbot/conversation_engine.py
import json, os
from datetime import datetime
from .response_retriever import ResponseRetriever
from .gemini_assistant import GeminiAssistant
from models.scoring_system import calculate_score_answer
from models.predictor import StatusPredictor

class QualificationChatbot:
    def __init__(self, questions_file=None):
        if questions_file is None:
            questions_file = os.path.join(os.path.dirname(__file__), "questions.json")
        self.questions_file = questions_file
        self.load_questions()

        # État
        self.client_score = 0
        self.conversation_log = []
        self.context = ""
        self.client_messages = []
        self.current_question_index = 0
        self.phase = "service"
        self.pending_question = None

        # Modules IA
        self.gemini = GeminiAssistant()
        self.retriever = ResponseRetriever(gemini_assistant=self.gemini)
        self.predictor = StatusPredictor()  # Pour prédire le statut

    def load_questions(self):
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data["questions"]
                self.threshold = data.get("qualification_threshold", 60)
                self.greeting = data.get("greeting_tn", "Salam !")
                self.final_qualified = data.get("final_qualified_tn", "✅ Mabrouk !")
                self.final_followup = data.get("final_followup_tn", "ℹ️ À suivre…")
                self.final_not_qualified = data.get("final_not_qualified_tn", "❌ Non qualifié.")
        except Exception as e:
            print(f"❌ Erreur de chargement des questions : {e}")
            raise

    def _is_qualification_request(self, user_message):
        triggers = [
            "bourse", "scholarship", "qualifié", "eligible", "chance",
            "score", "moyenne", "10 wla akther", "bac", "baccalauréat",
            "est-ce que je peux", "puis-je", "je suis eligible", "je peux avoir"
        ]
        return any(trigger in user_message.lower() for trigger)

    def _is_rejecting_qualification(self, user_message):
        return any(word in user_message.lower() for word in ["non respond", "repond", "ignore", "pas maintenant"])

    def process_message(self, user_message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conversation_log.append({
            "timestamp": timestamp,
            "sender": "user",
            "text": user_message
        })
        self.context += f"\nClient: {user_message}"
        self.client_messages.append(user_message)

        response_data = {
            "response": "",
            "score": self.client_score,
            "current_question": self.current_question_index + 1,
            "total_questions": len(self.questions),
            "phase": self.phase
        }

        # 🔮 Prédiction IA
        if len(self.client_messages) >= 2 and self.predictor.is_loaded:
            partial = " ||| ".join(self.client_messages)
            status, confidence = self.predictor.predict(partial)
            response_data["prediction"] = {"status": status, "confidence": float(confidence)}

        # PHASE 1 : Greeting
        if len(self.client_messages) == 1:
            response_data["response"] = self.greeting
            return response_data

        # PHASE 2 : Refus de qualification
        if self._is_rejecting_qualification(user_message):
            if self.pending_question:
                answer = self.retriever.find_response(self.pending_question['text_tn'])
                if answer:
                    response_data["response"] = answer
                    self.pending_question = None
                else:
                    response_data["response"] = "On va te répondre bientôt, merci pour ta patience !"
            return response_data

        # PHASE 3 : Démarrer qualification
        if self.phase == "service" and self._is_qualification_request(user_message):
            self.phase = "qualification"
            self.current_question_index = 0
            next_q = self.questions[0]["text_tn"]
            prompt = f"Reformule naturellement : '{next_q}'"
            try:
                response_data["response"] = self.gemini.generate_response(prompt)
            except:
                response_data["response"] = next_q
            return response_data

        # PHASE 4 : Qualification
        if self.phase == "qualification":
            if self.current_question_index < len(self.questions):
                q = self.questions[self.current_question_index]
                points = calculate_score_answer(q, user_message)
                self.client_score += points
                response_data["score"] = self.client_score

                self.current_question_index += 1

                if self.current_question_index < len(self.questions):
                    next_q = self.questions[self.current_question_index]["text_tn"]
                    self.pending_question = self.questions[self.current_question_index]
                    prompt = f"Reformule naturellement : '{next_q}'"
                    try:
                        response_data["response"] = self.gemini.generate_response(prompt)
                    except:
                        response_data["response"] = next_q
                else:
                    if self.client_score >= self.threshold:
                        final_msg = self.final_qualified
                        final_status = "Qualified"
                    elif self.client_score >= self.threshold * 0.5:
                        final_msg = self.final_followup
                        final_status = "To follow up"
                    else:
                        final_msg = self.final_not_qualified
                        final_status = "Unqualified"

                    response_data["response"] = f"{final_msg}\n📊 Score final: {self.client_score}"
                    response_data["status"] = final_status
                    self.phase = "post_qualification"
            return response_data

        # PHASE 5 : Post-qualification ou service
        if self.phase in ["service", "post_qualification"]:
            answer = self.retriever.find_response(user_message)
            if answer:
                prompt = f"Reformule en tunisien latin naturel : '{answer}'"
                try:
                    response_data["response"] = self.gemini.generate_response(prompt)
                except:
                    response_data["response"] = answer
            else:
                response_data["response"] = "On va te répondre bientôt, merci pour ta patience !"

        return response_data