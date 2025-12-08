# tools/ai_assistant_tool.py

import math
import time

import streamlit as st
from groq import Groq
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


# -----------------------------
# Groq client
# -----------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# -----------------------------
# System prompt for ISA AI
# -----------------------------
SYSTEM_PROMPT = """
You are ISA AI, the official assistant of the ISA Master Tool platform.

You help aerospace engineering students and professionals with:
- ISA atmosphere properties
- Mach number, compressibility, and flow regimes
- Lift, drag, and aerodynamic coefficients
- Breguet range, endurance, and mission planning
- City-to-city flight duration, aircraft selection, and basic ops

IMPORTANT CONSISTENCY RULES:

1. When estimating flight time between two cities, follow the ISA City-to-City
   Flight Estimator logic:
   - Use geodesic distance between cities (great-circle distance).
   - Assume a typical jet cruise speed around 230–260 m/s (~450–500 knots).
   - Use an effective average speed of 0.85 × cruise speed to account for
     climb, descent, routing, and winds.
   Your answers should be close to what the ISA City-to-City tool would compute.

2. If the user wants precise numbers, say explicitly:
   "For exact numbers, use the City-to-City Flight Estimator tool in this app."

3. If your verbal estimate differs slightly from a provided calculator result,
   explain that:
   - Real routes and winds vary,
   - Airlines may fly conservatively,
   - The calculator uses fixed performance assumptions.

4. Always keep explanations clear and step-by-step.
   Include units consistently and warn when assumptions are simplified.

5. If the user provides calculator outputs (Mach, CL, CD, range, etc.),
   help interpret them physically: what they mean, whether they look reasonable,
   and how changing parameters would affect the result.
"""


# -----------------------------
# Helper: city-to-city estimate
# -----------------------------
def estimate_city_flight(departure_city: str, destination_city: str):
    """
    Roughly replicate the logic of the City-to-City Flight Estimator,
    but simplified for the AI page.

    Returns dict with distance_km, time_hr, eff_speed_kmh or None on failure.
    """
    if not departure_city or not destination_city:
        return None

    try:
        geolocator = Nominatim(user_agent="isa_ai_city_lookup")

        loc1 = geolocator.geocode(departure_city, timeout=10)
        time.sleep(1)  # be gentle with the service
        loc2 = geolocator.geocode(destination_city, timeout=10)

        if not loc1 or not loc2:
            return None

        coords1 = (loc1.latitude, loc1.longitude)
        coords2 = (loc2.latitude, loc2.longitude)

        distance_km = geodesic(coords1, coords2).kilometers

        # Reference aircraft assumption (similar to your City-to-City tool)
        cruise_speed_ms = 230.0  # m/s, ~A320 / 737 typical cruise
        eff_speed_ms = 0.85 * cruise_speed_ms
        eff_speed_kmh = eff_speed_ms * 3.6

        time_hr = distance_km / eff_speed_kmh

        return {
            "distance_km": distance_km,
            "time_hr": time_hr,
            "eff_speed_kmh": eff_speed_kmh,
        }

    except Exception:
        return None


# -----------------------------
# Main render function
# -----------------------------
def render():
    st.subheader("🤖 ISA AI Assistant")

    # Keep simple chat history
    if "isa_ai_history" not in st.session_state:
        st.session_state["isa_ai_history"] = []

    # Optional: city pair context for better answers
    with st.expander("Optional: include a city-to-city estimate in the context"):
        dep = st.text_input("Departure city", key="ai_dep_city", value="")
        dest = st.text_input("Destination city", key="ai_dest_city", value="")

        city_context = None
        if dep and dest:
            est = estimate_city_flight(dep, dest)
            if est:
                st.markdown(
                    f"**Estimated distance:** ~{est['distance_km']:.0f} km  \n"
                    f"**Assumed average speed:** ~{est['eff_speed_kmh']:.0f} km/h  \n"
                    f"**Estimated flight time:** ~{est['time_hr']:.2f} hr"
                )
                city_context = (
                    f"For reference, using ISA's internal assumptions "
                    f"(geodesic distance and ~0.85×cruise average speed), "
                    f"the estimated flight from {dep} to {dest} is about "
                    f"{est['time_hr']:.2f} hours over {est['distance_km']:.0f} km."
                )
            else:
                st.warning("Could not resolve one or both cities. The AI will still answer generically.")

    # Show previous messages
    for role, content in st.session_state["isa_ai_history"]:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(content)

    # User input
    user_input = st.chat_input("Ask about atmosphere, performance, missions, etc.")
    if not user_input:
        return

    # Add user message to history and display it
    st.session_state["isa_ai_history"].append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build message list for Groq
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # If we computed a concrete city-to-city estimate, feed that in as context
    if city_context is not None:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Context from ISA calculators: "
                    + city_context
                ),
            }
        )

    # Add chat history
    for role, content in st.session_state["isa_ai_history"]:
        messages.append({"role": role, "content": content})

    # Call Groq
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
            )
            answer = completion.choices[0].message.content
            placeholder.markdown(answer)
            st.session_state["isa_ai_history"].append(("assistant", answer))
        except Exception as e:
            placeholder.markdown("")
            st.error(f"Groq API error: {e}")
