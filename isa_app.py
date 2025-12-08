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
# Page config & global style
# -------------------------
st.set_page_config(
    page_title="ISA Master Tool",
    page_icon="✈",
    layout="wide",
)

# Dark / modern styling similar to your HTML landing page
st.markdown(
    """
    <style>
    /* Make main background dark */
    .main {
        background-color: #000000;
    }

    /* Tighter, centered content */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero card */
    .hero-card {
        background: #111111;
        border-radius: 20px;
        padding: 2.2rem 2.4rem;
        border: 1px solid #262626;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }

    .hero-sub {
        color: #cccccc;
        margin-bottom: 1.2rem;
    }

    .hero-list {
        color: #dddddd;
        padding-left: 1.2rem;
    }

    .hero-list li {
        margin-bottom: 0.2rem;
    }

    /* AI search panel */
    .ai-box {
        margin-top: 2.2rem;
        background: #111111;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        border: 1px solid #262626;
    }

    .ai-label {
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
        color: #ffffff;
    }

    .ai-help {
        font-size: 0.9rem;
        color: #bbbbbb;
        margin-bottom: 0.6rem;
    }

    /* Make the text input look more like a search bar */
    .stTextInput > div > div > input {
        border-radius: 999px;
    }

    /* Optional: darken buttons a bit */
    .stButton>button {
        border-radius: 999px;
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #444444;
        padding: 0.35rem 1.3rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #222222;
        border-color: #aaaaaa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

tool = st.sidebar.selectbox(
    "Select a Tool",
    tool_options,
    index=tool_options.index(st.session_state["tool"]),
)
st.session_state["tool"] = tool
st.query_params["tool"] = tool

# Global title (shows on all pages)
st.title("✈ ISA Master Tool")

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
    # --- HERO CARD ---
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 4])

    with col_left:
        st.markdown(
            """
<div class="hero-title">ISA Master Tool</div>
<div class="hero-sub">
A growing library of aerospace engineering tools with an integrated AI assistant.
</div>
<ul class="hero-list">
  <li>✈ ISA Atmosphere & flight regimes</li>
  <li>🧮 Aerodynamics & performance</li>
  <li>🛰 Mission planning & routing</li>
  <li>🤖 AI help for students and professionals</li>
</ul>
<p style="color:#bbbbbb;margin-top:0.7rem;">
Use the <strong>sidebar</strong> to open a tool, or ask ISA AI below.
</p>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        if lottie_common:
            st_lottie(lottie_common, height=230, key="home_lottie")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- AI SEARCH BOX ---
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown('<div class="ai-label">🔎 Ask ISA AI (Home Search)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ai-help">'
        "Ask how to use a tool, which calculator to choose, or a basic question about "
        "atmosphere, aerodynamics, or performance."
        "</div>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "",
        placeholder="Example: “Which tool should I use to estimate range?”",
    )

    if query:
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

    st.markdown("</div>", unsafe_allow_html=True)

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
