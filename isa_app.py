import streamlit as st
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components  # ⬅ make sure this is here

from utils import load_lottieurl
from tools import (
    isa_tool,
    mach_tool,
    lift_drag_tool,
    fuel_range_tool,
    mission_planner_tool,
    city_to_city_tool,
)

GITHUB_HOME = "https://ashwin135-jpg.github.io/ISA-ATM-Calculator/"

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
# Lottie animation (one for now)
# -------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

# -------------------------
# Routing
# -------------------------
if tool == "Home":
    # Render a tiny HTML page whose only job is to redirect
    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0; url={GITHUB_HOME}" />
            <script type="text/javascript">
                // Try JS redirect
                window.top.location.href = "{GITHUB_HOME}";
            </script>
        </head>
        <body>
            <p>
                Redirecting to
                <a href="{GITHUB_HOME}" target="_top">
                    ISA Master Tool Homepage
                </a>...
            </p>
        </body>
        </html>
        """,
        height=100,
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
