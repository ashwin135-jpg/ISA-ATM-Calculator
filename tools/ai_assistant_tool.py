# tools/ai_assistant_tool.py

import streamlit as st
from groq import Groq

# Use your secret key from Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """
You are ISA AI, the official assistant of the ISA Master Tool platform.

Your job is to give:
- Clear aerospace engineering explanations,
- Guidance on using ISA tools,
- Performance and mission insights,
- Basic flight-time estimates,
- Help interpreting ISA Atmosphere, Mach, Lift/Drag, Fuel & Range, and Mission Planner outputs.

IMPORTANT RULES FOR CONSISTENCY:

1. When users ask for **flight time between two cities**, do NOT guess.
   - Use the logic of the ISA City-to-City Estimator:
     • Geodesic distance between cities,
     • Typical jet cruise speed ~230–260 m/s,
     • Effective average speed = 0.85 × cruise speed to account for routing,
       climb/descent, and winds.
   - Your answers should be close to what the City to City tool would compute. This should be the same for all the tools.

2. If the user wants a precise answer, tell them:
   “For exact numbers, use the City-to-City Flight Estimator tool in the sidebar.”

3. If your estimate differs slightly from the tool’s output, explain:
   - AI uses simplified assumptions,
   - Actual routing and winds vary,
   - The tool uses structured aircraft parameters.

4. Keep tone professional, friendly, and technically accurate.
5. Tailor explanations to engineering students and practicing aerospace engineers.
6. Whenever useful, offer to compute Mach, Lift/Drag, simple performance metrics,
   or explain ISA properties in plain language.
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
