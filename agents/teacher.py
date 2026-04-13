from utils.llm import query_llm

from agents.retriever import retrieve_context
from utils.llm import query_llm

def teach(topic, index, chunks, model):
    context = retrieve_context(topic, index, chunks, model)

    # 🔥 CLEAN CONTEXT (avoid overload)
    context = context[:1500]   # limit tokens

    prompt = f"""
You are an excellent teacher.

Explain the topic clearly and in a structured way using the context below.

IMPORTANT:
- Prefer using the context
- If context is incomplete, you may use general knowledge BUT keep it accurate
- Do NOT copy raw text
- Make it easy to understand

---

Topic: {topic}

Context:
{context}

---

Format your answer like this:

📌 Definition:
(2-3 lines)

🧠 Explanation:
(simple and clear, avoid jargon)

💡 Example:
(real-world or intuitive)

⚠️ Key Point:
(one important takeaway)
"""

    response = query_llm(prompt)

    return response, context