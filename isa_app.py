import streamlit as st
from streamlit_lottie import st_lottie

from utils import load_lottieurl
from tools import isa_tool, mach_tool, lift_drag_tool  

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
    "City-to-City Flight Estimator",
]

default_tool = st.query_params.get("tool", "Home")
if default_tool not in tool_options:
    default_tool = "Home"

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
# Lottie animation (one for now)
# -------------------------
lottie_url = (
    "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
)
lottie_common = load_lottieurl(lottie_url)

if tool == "Home":
    st.markdown("""
    ## ISA Master Tool

    This is the backend calculator app.

    - Use the sidebar to choose a tool, or  
    - [Click here to return to the main landing page](https://ashwin135-jpg.github.io/ISA-ATM-Calculator/)
    """)

elif tool == "ISA Atmosphere Calculator":
    isa_tool.render()

elif tool == "Mach Number Calculator":
    mach_tool.render()

elif tool == "Lift and Drag Calculator":
    lift_drag_tool.render()

elif tool == "Fuel Consumption & Range Estimator":
    st.info("Fuel & Range page not split yet. Still in old code – coming soon!")

elif tool == "Mission Planner":
    st.info("Mission Planner page not split yet. Still in old code – coming soon!")

elif tool == "City-to-City Flight Estimator":
    st.info("City-to-City page not split yet. Still in old code – coming soon!")

