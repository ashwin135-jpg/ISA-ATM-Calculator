import streamlit as st
from streamlit_lottie import st_lottie
from utils import load_lottieurl
from tools import isa_tool, mach_tool, lift_drag_tool, fuel_range_tool, mission_planner_tool,city_to_city_tool,ai_assistant_tool

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

st.markdown(
    "## [✈ ISA Master Tool](https://ashwin135-jpg.github.io/ISA-ATM-Calculator/)"
)


tool = st.sidebar.selectbox(
    "Select a Tool",
    tool_options,
    index=tool_options.index(st.session_state["tool"]),
)
st.session_state["tool"] = tool
st.query_params["tool"] = tool

# -------------------------
# Lottie animation for tool pages
# -------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

if lottie_common and tool != "Home":
    st_lottie(lottie_common, height=250, key=tool.replace(" ", "_"))

# -------------------------
# Routing
# -------------------------
if tool == "Home":
    st.markdown(
        """
        <script>
            window.location.href = "https://ashwin135-jpg.github.io/ISA-ATM-Calculator/";
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

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
