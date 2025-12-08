import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are ISA AI, an aerospace engineering assistant integrated into the ISA Master Tool.

- You help with: atmosphere, aerodynamics, performance, missions, units, and basic aircraft design.
- Explain things clearly for students, but be technically correct.
- When relevant, refer to the tools the user has: ISA Atmosphere Calculator, Mach Number Calculator, Lift & Drag Calculator, Fuel & Range, Mission Planner, City-to-City Estimator.
"""

def render():
    st.subheader("🤖 ISA AI Assistant")
    st.markdown(
        "Ask questions about atmosphere, aerodynamics, performance, "
        "mission planning, or how to use the tools in this app."
    )

    if "isa_ai_history" not in st.session_state:
        st.session_state["isa_ai_history"] = []

    for msg in st.session_state["isa_ai_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask ISA AI something...")
    if not user_input:
        return

    st.session_state["isa_ai_history"].append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",  # or another model you choose
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state["isa_ai_history"],
                ],
            )
            reply = response.choices[0].message.content

            st.markdown(reply)

    st.session_state["isa_ai_history"].append({"role": "assistant", "content": reply})
