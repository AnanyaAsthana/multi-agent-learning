def detect_weak_topics(history):
    topic_scores = {}

    for h in history:
        topic = h["topic"]
        score = h["score"]

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(score)

    weak = []

    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        if avg < 0.6:
            weak.append((topic, round(avg, 2)))

    return weak

from utils.llm import query_llm

def generate_ai_analysis(history):
    prompt = f"""
You are an AI learning analyst.

Analyze this student performance data:

{history}

Give:
1. Weak areas
2. Strong areas
3. Personalized study plan (3 steps)
Keep it short.
"""
    return query_llm(prompt)

def detect_weak_concepts(history):
    concept_scores = {}

    for h in history:
        concept = h.get("concept", "general")
        score = h["score"]

        if concept not in concept_scores:
            concept_scores[concept] = []

        concept_scores[concept].append(score)

    weak = []

    for concept, scores in concept_scores.items():
        avg = sum(scores) / len(scores)
        if avg < 0.6:
            weak.append((concept, round(avg, 2)))

    return weak