import streamlit as st
import pandas as pd

from utils.pdf_loader import load_pdf
from utils.embeddings import create_vector_store
from utils.llm import query_llm
from utils.storage import load_data, save_data

from agents.teacher import teach
from agents.assessment import generate_questions
from agents.retriever import retrieve_context

# 🔥 NEW IMPORTS
from agents.student_model import StudentModel
from agents.planner import planner_agent

from utils.quiz_session import QuizSession
from utils.followup_chat import render_followup_chat
from utils.analysis import detect_weak_topics, generate_ai_analysis, detect_weak_concepts


# ========================
# 🧠 SESSION STATE
# ========================
if "stage" not in st.session_state:
    st.session_state.stage = "learn"

if "quiz_session" not in st.session_state:
    st.session_state.quiz_session = None

if "prev_topic" not in st.session_state:
    st.session_state.prev_topic = ""

if "result_saved" not in st.session_state:
    st.session_state.result_saved = False

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "learn"

# 🔥 NEW
if "student_model" not in st.session_state:
    st.session_state.student_model = StudentModel()

if "plan" not in st.session_state:
    st.session_state.plan = None


# ========================
# 🎨 HEADER
# ========================
st.markdown("""
# 🎓 Agentic AI Learning System
### Autonomous Adaptive Learning
""")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])


# ========================
# 🧭 NAVIGATION
# ========================
tab = st.radio(
    "Navigation",
    ["📖 Learn", "📊 Analysis"],
    index=0 if st.session_state.active_tab == "learn" else 1,
    horizontal=True
)


# =========================================================
# 📖 LEARN TAB
# =========================================================
if tab == "📖 Learn":

    st.session_state.active_tab = "learn"

    if uploaded_file:
        text = load_pdf(uploaded_file)

        chunks = [
            text[i:i+500]
            for i in range(0, len(text), 500)
            if len(text[i:i+500].strip()) > 100
        ]

        index, chunks, model = create_vector_store(chunks)

        topic = st.text_input("Enter topic", value=st.session_state.prev_topic)

        st.divider()

        # Reset on topic change
        if topic and st.session_state.prev_topic != topic:
            st.session_state.stage = "learn"
            st.session_state.quiz_session = None
            st.session_state.result_saved = False
            st.session_state.prev_topic = topic

        if topic:

            sm = st.session_state.student_model
            sm.init_topic(topic)
            student_state = sm.get_state(topic)

            # 🔥 TRUE PLANNER
            plan = planner_agent(topic, student_state)
            st.session_state.plan = plan

            st.write("### 🧠 Planner Decision")
            st.json(plan)

            decision = plan["action"]

            # ========================
            # 📖 LEARNING
            # ========================
            if st.session_state.stage == "learn":

                weak_areas = student_state.get("weak_areas", [])
                if weak_areas:
                    st.warning(f"Focusing on weak areas: {', '.join(set(weak_areas))}")

                explanation, context = teach(topic, index, chunks, model)

                st.subheader("📖 Learning")
                st.markdown(explanation)

                with st.expander("📄 Source Context"):
                    st.write(context)

                render_followup_chat(
                    topic,
                    retriever=lambda q: retrieve_context(q, index, chunks, model),
                    llm=query_llm
                )

                if st.button("➡️ Continue to Test"):
                    st.session_state.stage = "quiz"
                    st.rerun()

            # ========================
            # 📝 QUIZ
            # ========================
            if st.session_state.stage == "quiz":

                # 🔥 Planner controls difficulty
                difficulty = plan.get("difficulty", "medium")

                # regenerate quiz if needed
                if st.session_state.quiz_session is None:
                    _, context = teach(topic, index, chunks, model)

                    questions = generate_questions(
                        topic,
                        context,
                        difficulty
                    )

                    st.session_state.quiz_session = QuizSession(questions, 10)

                quiz = st.session_state.quiz_session

                st.subheader(f"📝 Quiz ({difficulty.upper()})")

                for i, q in enumerate(quiz.questions):
                    st.write(f"Q{i+1}. {q['question']}")
                    st.caption(f"Concept: {q.get('concept', 'general')}")

                    ans = st.radio("Select", q["options"], key=f"q_{i}")
                    quiz.answers[i] = ans

                if st.button("Submit Quiz"):
                    quiz.submit()
                    st.session_state.stage = "results"
                    st.rerun()

            # ========================
            # 📊 RESULTS
            # ========================
            if st.session_state.stage == "results":

                quiz = st.session_state.quiz_session

                if quiz is None:
                    st.session_state.stage = "learn"
                    st.rerun()

                correct, total = quiz.get_score()
                score = correct / total if total > 0 else 0

                st.subheader("📊 Results")
                st.write(f"Score: {correct}/{total}")
                st.progress(score)

                mistakes = []

                for i, q in enumerate(quiz.questions):
                    user_ans = quiz.answers.get(i)
                    correct_ans = q["answer"]
                    concept = q.get("concept", "general")

                    if user_ans == correct_ans:
                        st.success(f"✅ {q['question']} (Concept: {concept})")
                    else:
                        st.error(f"❌ {q['question']} (Concept: {concept})")
                        st.write(f"Correct Answer: {correct_ans}")
                        mistakes.append(concept)

                # 🔥 UPDATE STUDENT MODEL
                sm.update(topic, score, mistakes)

                st.subheader("🧠 Student Model Update")
                st.json(sm.get_state(topic))

                # save history
                if not st.session_state.result_saved:
                    data = load_data()
                    data.setdefault("history", [])

                    for i, q in enumerate(quiz.questions):
                        user_ans = quiz.answers.get(i)
                        correct_flag = user_ans == q["answer"]

                        concept = q.get("concept", "general")

                        data["history"].append({
                            "topic": topic,
                            "concept": concept,
                            "score": 1 if correct_flag else 0,
                            "difficulty": plan.get("difficulty", "medium")
                        })

                    save_data(data)
                    st.session_state.result_saved = True

                if st.button("Continue"):
                    st.session_state.stage = "learn"
                    st.session_state.quiz_session = None
                    st.session_state.result_saved = False
                    st.rerun()


# =========================================================
# 📊 ANALYSIS TAB (UNCHANGED)
# =========================================================
if tab == "📊 Analysis":

    st.session_state.active_tab = "analysis"

    st.header("📊 Learning Analysis")

    data = load_data()

    if "history" not in data or len(data["history"]) == 0:
        st.info("No learning data yet.")
    else:
        df = pd.DataFrame(data["history"])

        st.subheader("📈 Score Trend")
        st.line_chart(df["score"])

        st.subheader("📊 Topic Performance")
        topic_scores = df.groupby("topic")["score"].mean()
        st.bar_chart(topic_scores)

        st.subheader("⚠️ Weak Topics")
        weak_topics = detect_weak_topics(data["history"])

        for t, s in weak_topics:
            st.error(f"{t} → {s}")

            if st.button(f"Revise {t}", key=f"revise_{t}"):
                st.session_state.prev_topic = t
                st.session_state.stage = "learn"
                st.session_state.active_tab = "learn"
                st.session_state.quiz_session = None
                st.rerun()

        st.subheader("🧠 Weak Concepts")
        weak_concepts = detect_weak_concepts(data["history"])

        if len(weak_concepts) == 0:
            st.success("No weak concepts!")
        else:
            for c, s in weak_concepts:
                st.error(f"{c} → {s}")

                if st.button(f"Revise Concept: {c}", key=f"revise_concept_{c}"):
                    st.session_state.prev_topic = c
                    st.session_state.stage = "learn"
                    st.session_state.active_tab = "learn"
                    st.session_state.quiz_session = None
                    st.rerun()

        st.subheader("📊 Concept Performance")
        concept_scores = df.groupby("concept")["score"].mean()
        st.bar_chart(concept_scores)

        st.subheader("🧠 AI Learning Insights")
        st.info(generate_ai_analysis(data["history"]))

        st.subheader("🏗️ System Architecture")
        st.markdown("""
User Input
↓
Retriever Agent (FAISS)
↓
Teacher Agent (Explanation)
↓
Assessment Agent (Quiz Generation)
↓
Evaluation Agent (Scoring)
↓
Planner Agent (Dynamic Decision)
↓
Student Model (Mastery + Weak Concepts)
↓
Adaptive Loop (Continuous Learning)
        """)