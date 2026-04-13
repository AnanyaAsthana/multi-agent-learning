import streamlit as st

def render_followup_chat(topic, retriever, llm):
    """
    topic: current topic string
    retriever: function(query) -> list[str]
    llm: function(prompt, history=None) -> str
    """

    # ========================
    # 🔁 Reset chat on topic change
    # ========================
    if "chat_topic" not in st.session_state:
        st.session_state.chat_topic = topic
        st.session_state.chat_history = []

    if st.session_state.chat_topic != topic:
        st.session_state.chat_topic = topic
        st.session_state.chat_history = []

    # ========================
    # 🧹 Clear chat button
    # ========================
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # ========================
    # 💬 Display history
    # ========================
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ========================
    # 💬 Input
    # ========================
    user_input = st.chat_input("Ask a follow-up question...")

    if user_input:
        # Save user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # ========================
        # 🔍 Retrieve context
        # ========================
        retrieved_chunks = retriever(user_input)
        context = "\n".join(retrieved_chunks[:3])

        # ========================
        # 🧠 System Prompt
        # ========================
        system_prompt = f"""
You are a helpful tutor.

The student just learned about "{topic}".

Answer their follow-up question using ONLY the context below.
If the answer is not in the context, say so honestly.
Keep answers under 150 words.

Context:
{context}
"""

        # ========================
        # 🧠 Use last 6 messages
        # ========================
        history = st.session_state.chat_history[-6:]

        # Format history for LLM
        history_text = ""
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        prompt = f"""
{system_prompt}

Conversation:
{history_text}

User: {user_input}
Assistant:
"""

        # ========================
        # 🤖 LLM Call
        # ========================
        response = llm(prompt)

        # Save assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        # Display response
        with st.chat_message("assistant"):
            st.write(response)