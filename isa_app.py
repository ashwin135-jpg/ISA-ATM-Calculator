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
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Welcome to ISA Master Tool")
        st.markdown(
            """
            A growing library of aerospace engineering tools for:

            - ✈ Atmosphere & flight regimes  
            - 🧮 Aerodynamics & performance  
            - 🛰 Mission planning & routing  

            Use the cards below or the sidebar to open a tool.
            """
        )

    with col2:
        if lottie_common:
            st_lottie(lottie_common, height=220, key="home_lottie")

    st.markdown("---")
    st.markdown("### Available Tools")

    # Create cards in a grid
    cols = st.columns(3)
    for i, t in enumerate(TOOLS):
        c = cols[i % 3]
        with c:
            st.markdown(f"**{t['name']}**")
            st.caption(t["category"])
            st.write(t["short"])
            if st.button("Open", key=f"open_{t['name']}"):
                st.session_state["tool"] = t["name"]
                st.query_params["tool"] = t["name"]
                st.experimental_rerun()


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
