import json
from utils.llm import query_llm

def planner_agent(topic, student_state):
    prompt = f"""
You are a planning agent in an adaptive learning system.

Student state:
{student_state}

Decide the next best action.

Rules:
- mastery < 0.4 → teach
- 0.4 to 0.7 → medium quiz
- > 0.7 → hard quiz or revision

Return ONLY JSON:
{{
  "action": "teach" | "quiz" | "revise",
  "difficulty": "easy" | "medium" | "hard",
  "reason": "short explanation"
}}
"""

    response = query_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "action": "teach",
            "difficulty": "easy",
            "reason": "fallback"
        }