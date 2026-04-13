#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

from groq import Groq

client = Groq(api_key="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")  # 🔥 paste your Groq API key

def query_llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content