import re
from utils.llm import query_llm


def generate_questions(topic, context, difficulty="medium"):

    difficulty_instruction = {
        "easy": "Focus on basic definitions and simple recall.",
        "medium": "Include conceptual understanding and application.",
        "hard": "Include scenario-based and tricky questions."
    }

    prompt = f"""
Create EXACTLY 3 MCQs.

Topic: {topic}
Difficulty: {difficulty.upper()}
Instruction: {difficulty_instruction[difficulty]}

For EACH question:
- Include the concept being tested
- Ensure options are distinct and meaningful

Use ONLY the context.

Format STRICTLY:

Q1. Question
Concept: <concept name>
A. option
B. option
C. option
D. option
Answer: A

---

Context:
{context}

If format is not followed EXACTLY, output will be rejected.
"""

    response = query_llm(prompt)

    questions = []
    blocks = re.split(r"Q\d+\.", response)[1:]

    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]

        if len(lines) < 6:
            continue

        question = lines[0]
        options = []
        answer_letter = ""
        concept = "general"

        for line in lines[1:]:
            if line.startswith("Concept:"):
                concept = line.replace("Concept:", "").strip()

            elif line.startswith(("A.", "B.", "C.", "D.")):
                options.append(line[3:].strip())

            elif "Answer:" in line:
                answer_letter = line.split("Answer:")[1].strip()

        index_map = {"A": 0, "B": 1, "C": 2, "D": 3}

        # ✅ VALIDATION IMPROVEMENT
        if answer_letter in index_map and len(options) == 4:
            answer = options[index_map[answer_letter]]
        else:
            continue  # skip bad question

        questions.append({
            "question": question,
            "options": options,
            "answer": answer,
            "difficulty": difficulty,
            "concept": concept
        })

    # ✅ SAFETY: ensure exactly 3 questions
    if len(questions) != 3:
        return []

    return questions