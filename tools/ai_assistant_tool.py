import streamlit as st
from openai import OpenAI

def get_client():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "OPENAI_API_KEY is not set in Streamlit secrets. "
            "Go to Settings → Secrets and add it."
        )
        return None
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are ISA AI, an aerospace engineering assistant integrated into the ISA Master Tool.

- You help with: atmosphere, aerodynamics, performance, mission planning,
  units, and basic aircraft design.
- Explain things clearly for students, but be technically correct.
- When relevant, refer to the tools the user has:
  ISA Atmosphere Calculator, Mach Number Calculator, Lift & Drag Calculator,
  Fuel & Range Estimator, Mission Planner, City-to-City Flight Estimator.
"""

def render():
    st.subheader("🤖 ISA AI Assistant")
    st.markdown(
        "Ask questions about atmosphere, aerodynamics, performance, "
        "mission planning, or how to use the tools in this app."
    )

    client = get_client()
    if client is None:
        return  # stop if no API key

    if "isa_ai_history" not in st.session_state:
        st.session_state["isa_ai_history"] = []

    # show history
    for msg in st.session_state["isa_ai_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask ISA AI something...")
    if not user_input:
        return

    st.session_state["isa_ai_history"].append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # ✅ valid lightweight model
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state["isa_ai_history"],
                    ],
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state["isa_ai_history"].append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as e:
                # show the raw error message so you know what's wrong
                st.error(f"API error: {e}")
