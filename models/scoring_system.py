# models/scoring_system.py
def calculate_score_answer(question_data, user_answer):
    user_answer = user_answer.lower()
    keywords = question_data["keywords"]
    default_score = question_data.get("default_score", 0)

    for keyword, score in keywords.items():
        if keyword in user_answer:
            return score
    return default_score