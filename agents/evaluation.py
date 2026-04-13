from utils.llm import query_llm

def evaluate_answers(question, user_answer, context):
    from utils.llm import query_llm

    prompt = f"""
Evaluate the answer ONLY using context.

---

Context:
{context}

Question:
{question}

User Answer:
{user_answer}

---

Say:
Correct or Incorrect + short explanation
"""

    return query_llm(prompt)