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

# ---------------------------------
# Mapping between internal keys and labels
# ---------------------------------
tool_keys = [
    "home",
    "isa",
    "mach",
    "lift",
    "fuel",
    "mission",
    "city",
    "ai",
]

key_to_label = {
    "home": "Home",
    "isa": "ISA Atmosphere Calculator",
    "mach": "Mach Number Calculator",
    "lift": "Lift and Drag Calculator",
    "fuel": "Fuel Consumption & Range Estimator",
    "mission": "Mission Planner",
    "city": "City to City Flight Estimator",
    "ai": "AI Assistant",
}

label_to_key = {label: key for key, label in key_to_label.items()}

# ---------------------------------
# Read default from query param (for GitHub links)
# ---------------------------------
default_label = st.query_params.get("tool", key_to_label["isa"])
default_key = label_to_key.get(default_label, "isa")

if "tool_key" not in st.session_state:
    st.session_state["tool_key"] = default_key

st.title("✈ ISA Master Tool")

# ---------------------------------
# Sidebar selectbox (shows labels, stores keys)
# ---------------------------------
tool_key = st.sidebar.selectbox(
    "Select a Tool",
    options=tool_keys,
    index=tool_keys.index(st.session_state["tool_key"]),
    format_func=lambda k: key_to_label[k],
)

st.session_state["tool_key"] = tool_key
# Keep query param in sync for deep links
st.query_params["tool"] = key_to_label[tool_key]

# ---------------------------------
# Lottie animation for tool pages
# ---------------------------------
lottie_url = "https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json"
lottie_common = load_lottieurl(lottie_url)

# Show animation on all tools except Home
if lottie_common and tool_key != "home":
    st_lottie(lottie_common, height=250, key=key_to_label[tool_key].replace(" ", "_"))

# ---------------------------------
# Routing
# ---------------------------------
if tool_key == "home":
    # Redirect back to your GitHub landing page
    github_url = "https://ashwin135-jpg.github.io/ISA-ATM-Calculator/"

    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url={github_url}">
        <script>
            window.location.href = "{github_url}";
        </script>
        <p>If you are not redirected automatically, 
        <a href="{github_url}">click here to go to the ISA Master Tool home page</a>.</p>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

elif tool_key == "isa":
    isa_tool.render()

elif tool_key == "mach":
    mach_tool.render()

elif tool_key == "lift":
    lift_drag_tool.render()

elif tool_key == "fuel":
    fuel_range_tool.render()

elif tool_key == "mission":
    mission_planner_tool.render()

elif tool_key == "city":
    city_to_city_tool.render()

elif tool_key == "ai":
    ai_assistant_tool.render()
