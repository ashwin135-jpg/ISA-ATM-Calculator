import streamlit as st
from streamlit_lottie import st_lottie
from utils import load_lottieurl
from tools import (
    isa_tool,
    mach_tool,
    lift_drag_tool,
    fuel_range_tool,
    mission_planner_tool,
    city_to_city_tool,
    ai_assistant_tool,
)
from groq import Groq

# -------------------------
# Home AI system prompt
# -------------------------
HOME_AI_SYSTEM_PROMPT = """
You are ISA AI on the home page of the ISA Master Tool app.

Your main job here is to:
- Help users understand which tool to use (ISA Atmosphere, Mach Number, Lift & Drag,
  Fuel Range, Mission Planner, City-to-City Flight Estimator, AI Assistant).
- Explain how to use each tool: what inputs mean, what outputs mean, and typical use cases.
- Answer basic aerospace questions related to atmosphere, aerodynamics, and missions,
  but always try to connect your answer back to how the user could use one of the tools.

If the user asks something like "how long from city A to city B", tell them to use
the City-to-City Flight Estimator tool, and optionally give a rough explanation.

Keep answers clear, student-friendly, and technically correct.
"""

# -------------------------
# Sidebar / query param setup
# -------------------------
tool_options = [
    "Home",
    "ISA Atmosphere Calculator",
    "Mach Number Calculator",
    "Lift and Drag Calculator",
    "Fuel Consumption & Range Estimator",
    "Mission Planner",
    "City to City Flight Estimator",
    "AI Assistant",
]

default_tool = st.query_params.get("tool", "ISA Atmosphere Calculator")
if default_tool not in tool_options:
    default_tool = "ISA Atmosphere Calculator"

if "tool" not in st.session_state:
    st.session_state["tool"] = default_tool

st.title("✈ ISA Master Tool")

tool = st.sidebar.selectbox(
    "Select a Tool",
    tool_options,
    index=tool_options.index(st.session_state["tool"]),
)
st.session_state["tool"] = tool
st.query_params["tool"] = tool

# -------------------------
# Lottie animation (shared)
# -------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

if lottie_common and tool != "Home":
    # Show on tool pages
    st_lottie(lottie_common, height=250, key=tool.replace(" ", "_"))

# -------------------------
# Routing
# -------------------------
if tool == "Home":
    # --- Hero / intro ---
    st.markdown(
        """
Welcome to **ISA Master Tool** — a growing library of aerospace engineering tools and an integrated AI assistant.

Use the sidebar to open:

- ISA Atmosphere Calculator  
- Mach Number Calculator  
- Lift and Drag Calculator  
- Fuel Consumption & Range Estimator  
- Mission Planner  
- City to City Flight Estimator  
- AI Assistant  
        """
    )

    # Optional: Lottie on Home page
    if lottie_common:
        st_lottie(lottie_common, height=250, key="home_lottie")

    st.markdown("---")
    st.subheader("Ask ISA AI (Home Search)")
    st.markdown(
        "Ask how to use a tool, which calculator is right for your problem, "
        "or basic questions about atmosphere, aerodynamics, and performance."
    )

    query = st.text_input(
        "Ask a question about ISA Master Tool or basic aerospace topics:"
    )

    if query:
        # Call Groq for a one-shot answer
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except KeyError:
            st.error("GROQ_API_KEY is not set in Streamlit secrets.")
        else:
            with st.spinner("Thinking..."):
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": HOME_AI_SYSTEM_PROMPT},
                            {"role": "user", "content": query},
                        ],
                    )
                    answer = completion.choices[0].message.content
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"Groq API error: {e}")

    st.markdown("---")
    st.markdown(
        " For a full chat experience, open the **AI Assistant** tool in the sidebar."
    )

elif tool == "ISA Atmosphere Calculator":
    isa_tool.render()

elif tool == "Mach Number Calculator":
    mach_tool.render()

elif tool == "Lift and Drag Calculator":
    lift_drag_tool.render()

elif tool == "Fuel Consumption & Range Estimator":
    fuel_range_tool.render()

elif tool == "Mission Planner":
    mission_planner_tool.render()

elif tool == "City to City Flight Estimator":
    city_to_city_tool.render()

elif tool == "AI Assistant":
    ai_assistant_tool.render()
