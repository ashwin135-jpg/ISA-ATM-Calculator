# tools/ai_assistant_tool.py

import streamlit as st
from groq import Groq

# Use your secret key from Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """
You are the ISA Master Tool AI assistant.

You help aerospace engineering students and professionals with:
- ISA atmosphere properties
- Mach number, compressibility, and flow regimes
- Lift, drag, performance, Breguet range/endurance
- Mission planning and simple aircraft ops questions

Be clear, step-by-step, and explain units.
If the user asks for something outside your domain, you can still answer
but keep responses concise.
"""


def render():
    st.subheader("🤖 ISA AI Assistant")

    # Keep simple memory in session (optional)
    if "ai_history" not in st.session_state:
        st.session_state["ai_history"] = []

    # Show chat history
    for role, content in st.session_state["ai_history"]:
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)

    # Input box at the bottom
    user_input = st.chat_input("Ask a question about atmosphere, performance, etc.")
    if not user_input:
        return

    # Add user message to history
    st.session_state["ai_history"].append(("user", user_input))

    # Show the user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("_Thinking..._")

        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # fast + strong general model
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *[
                        {"role": r, "content": c}
                        for (r, c) in st.session_state["ai_history"]
                    ],
                ],
            )

            answer = chat_completion.choices[0].message.content
            message_placeholder.markdown(answer)

            # Save assistant reply in history
            st.session_state["ai_history"].append(("assistant", answer))

        except Exception as e:
            message_placeholder.markdown("")
            st.error(f"Groq API error: {e}")
