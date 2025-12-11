import streamlit as st
from streamlit_lottie import st_lottie
import requests 

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


BACKEND_URL = "http://127.0.0.1:8000"  

st.set_page_config(
    page_title="ISA Master Tool",
    page_icon="✈",
    layout="centered",
)

# ---------------------------------
# Sidebar setup  (NO query params)
# ---------------------------------
tool_options = [
    "ISA Air Properties",   
    "Mach Number Calculator",
    "Lift and Drag Calculator",
    "Fuel Consumption & Range Estimator",
    "Mission Planner",
    "City to City Flight Estimator",
    "AI Assistant",
]

# Default tool on first load
if "tool" not in st.session_state:
    st.session_state["tool"] = "ISA Air Properties"

st.markdown(
    "## [✈ ISA Master Tool](https://ashwin135-jpg.github.io/ISA-ATM-Calculator/)"
)
tool = st.sidebar.selectbox(
    "Select a Tool",
    tool_options,
    index=tool_options.index(st.session_state["tool"]),
)

st.session_state["tool"] = tool

# ---------------------------------
# Lottie animation
# ---------------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

if lottie_common:
    st_lottie(lottie_common, height=250, key=tool.replace(" ", "_"))

# ---------------------------------
# Routing
# ---------------------------------
if tool == "ISA Air Properties":       
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

# ---------------------------------
# Backend connectivity test
# ---------------------------------
st.markdown("---")
st.subheader("🛠 Backend Connection (Developer Test)")

col1, col2 = st.columns(2)

with col1:
    if st.button("Ping ISA Backend"):
        try:
            resp = requests.get(f"{BACKEND_URL}/ping", timeout=5)
            st.write("Response from /ping:")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Error talking to backend: {e}")

with col2:
    altitude_m = st.number_input("Test altitude (m) [backend]", value=1000.0)
    if st.button("Run ISA Atmosphere via Backend"):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/isa/atmosphere",
                json={"altitude_m": altitude_m},
                timeout=10,
            )
            st.write("Response from /api/isa/atmosphere:")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Error calling ISA backend: {e}")
