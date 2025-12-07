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
)
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
)

# Page settings
st.set_page_config(
    page_title="ISA Master Tool",
    page_icon="✈",
    layout="wide",
)

# Global dark-ish styling
st.markdown(
    """
    <style>
    /* Make main background darker */
    .main {
        background-color: #000000;
    }

    /* Center content a bit and limit width */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Tool cards grid */
    .tool-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1.5rem;
        margin-top: 1rem;
    }

    .tool-card {
        background: #111111;
        border-radius: 16px;
        padding: 18px 20px;
        border: 1px solid #262626;
    }

    .tool-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #ffffff;
    }

    .tool-category {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888888;
        margin-bottom: 0.4rem;
    }

    .tool-desc {
        font-size: 0.9rem;
        color: #dddddd;
        margin-bottom: 0.9rem;
    }

    /* Make buttons look like your big black pills */
    .stButton>button {
        border-radius: 999px;
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #444444;
        padding: 0.4rem 1.5rem;
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
# Tool definitions (single source of truth)
# -------------------------
TOOLS = [
    {
        "name": "ISA Atmosphere Calculator",
        "category": "Atmosphere",
        "short": "Standard atmosphere properties vs altitude.",
    },
    {
        "name": "Mach Number Calculator",
        "category": "Flight Regime",
        "short": "Compute Mach and classify flow regime.",
    },
    {
        "name": "Lift and Drag Calculator",
        "category": "Aerodynamics",
        "short": "Estimate lift, drag, and coefficients.",
    },
    {
        "name": "Fuel Consumption & Range Estimator",
        "category": "Performance",
        "short": "Breguet range, endurance, and fuel burn.",
    },
    {
        "name": "Mission Planner",
        "category": "Performance",
        "short": "Simple mission performance and fuel usage.",
    },
    {
        "name": "City-to-City Flight Estimator",
        "category": "Operations",
        "short": "Suggest aircraft for a given route.",
    },
]

tool_names = [t["name"] for t in TOOLS]

# -------------------------
# Sidebar / query param setup
# -------------------------
tool_options = ["Home"] + tool_names

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
# Lottie animation
# -------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

# -------------------------
# HOME PAGE (Streamlit, no redirect)
# -------------------------
def render_home():
    # Top hero section
    left, right = st.columns([2, 3])

    with left:
        st.markdown("## ✈ ISA Master Tool")
        st.markdown(
            """
            A growing library of aerospace engineering tools for:

            - ✈ Atmosphere & flight regimes  
            - 🧮 Aerodynamics & performance  
            - 🛰 Mission planning & routing  

            Use the cards below or the sidebar to open a tool.
            """
        )

    with right:
        # Show your "world map" feeling – using the Lottie we already load
        if lottie_common:
            st_lottie(lottie_common, height=260, key="home_lottie")

    st.markdown("---")
    st.markdown("### Available Tools")

    # Tool cards grid
    st.markdown('<div class="tool-grid">', unsafe_allow_html=True)

    for t in TOOLS:
        # Start card
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)

        st.markdown(f'<div class="tool-title">{t["name"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="tool-category">{t["category"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="tool-desc">{t["short"]}</div>',
            unsafe_allow_html=True,
        )

        # Button inside the card
        if st.button("Open", key=f"open_{t['name']}"):
            st.session_state["tool"] = t["name"]
            st.query_params["tool"] = t["name"]
            st.experimental_rerun()

        # End card
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)



# -------------------------
# ROUTING
# -------------------------
if tool == "Home":
    render_home()

else:
    # Lottie for tool pages
    if lottie_common:
        st_lottie(lottie_common, height=200, key=tool.replace(" ", "_"))

    if tool == "ISA Atmosphere Calculator":
        isa_tool.render()

    elif tool == "Mach Number Calculator":
        mach_tool.render()

    elif tool == "Lift and Drag Calculator":
        lift_drag_tool.render()

    elif tool == "Fuel Consumption & Range Estimator":
        fuel_range_tool.render()

    elif tool == "Mission Planner":
        mission_planner_tool.render()

    elif tool == "City-to-City Flight Estimator":
        city_to_city_tool.render()
