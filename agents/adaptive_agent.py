learning_path = {
    "session hijacking": "CSRF",
    "csrf": "XSS",
    "xss": "SQL Injection",
    "sql injection": "Authentication Security"
}

def suggest_next_topic(history):
    if not history:
        return {"action": "start", "message": "Start learning basics"}

    last = history[-1]
    topic = last["topic"].lower()

    if last["score"] < 0.6:
        return {
            "action": "reteach",
            "topic": topic,
            "message": f"Revise '{topic}'"
        }

    next_topic = learning_path.get(topic, "Explore advanced topics")

    return {
        "action": "advance",
        "topic": next_topic,
        "message": f"Next topic: {next_topic}"
    }