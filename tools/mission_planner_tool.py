import math
import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def render():
    st.subheader("Mission Planner")
    st.markdown(
        "Estimate **range**, **fuel used**, and **flight time** "
        "based on aircraft weight and fuel availability."
    )

    # --- Unit system selector ---
    unit_system = st.radio("Select unit system", ["SI (Metric)", "Imperial (English)"])

    # --- Unit conversion helpers ---
    def to_kg(lb):
        return lb * 0.453592

    def to_mps(knots):
        return knots * 0.514444

    def from_kg(kg):
        return kg / 0.453592

    def from_km(km):
        return km / 1.852

    # --- Inputs ---
    if unit_system == "SI (Metric)":
        W_total = st.number_input(
            "Total aircraft weight (kg)", value=35000.0, min_value=0.0
        )
        fuel_weight = st.number_input(
            "Fuel available (kg)", value=10000.0, min_value=0.0
        )
        cruise_speed = st.number_input(
            "Cruise speed (m/s)", value=230.0, min_value=0.0
        )
    else:
        W_total_lb = st.number_input(
            "Total aircraft weight (lb)", value=77162.0, min_value=0.0
        )
        fuel_weight_lb = st.number_input(
            "Fuel available (lb)", value=22046.0, min_value=0.0
        )
        cruise_speed_kt = st.number_input(
            "Cruise speed (knots)", value=450.0, min_value=0.0
        )

        W_total = to_kg(W_total_lb)
        fuel_weight = to_kg(fuel_weight_lb)
        cruise_speed = to_mps(cruise_speed_kt)

    c = st.number_input(
        "Specific fuel consumption (1/hr)", value=0.6, min_value=0.01
    )
    LD = st.number_input("Lift-to-drag ratio (L/D)", value=15.0, min_value=1.0)

    # --- Basic sanity check (same as before) ---
    Wi = W_total
    Wf = Wi - fuel_weight
    if Wf <= 0 or Wi <= Wf:
        st.error(
            "Invalid weight combination. Make sure fuel_weight < total weight "
            "and greater than zero."
        )
        return

    # --- Call backend instead of doing math here ---
    if st.button("Compute Mission Performance"):
        payload = {
            "Wi_kg": Wi,
            "fuel_weight_kg": fuel_weight,
            "cruise_speed_ms": cruise_speed,
            "c_per_hr": c,
            "LD": LD,
        }

        try:
            with st.spinner("Querying backend for mission estimate..."):
                resp = requests.post(
                    f"{BACKEND_URL}/api/mission-planner/estimate",
                    json=payload,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            st.error(f"Error calling Mission Planner backend: {e}")
            return

        # --- Extract backend results ---
        Wi_kg = data.get("Wi_kg", Wi)
        Wf_kg = data.get("Wf_kg", Wf)
        fuel_kg = data.get("fuel_weight_kg", fuel_weight)

        R_km = data.get("range_km")
        R_nm = data.get("range_nm")
        R_mi = data.get("range_mi")
        time_hr = data.get("time_hr")

        # --- Outputs (same behavior as before) ---
        st.markdown("### 📊 Estimated Mission Performance")

        col1, col2 = st.columns(2)
        with col1:
            if unit_system == "SI (Metric)":
                st.metric("Fuel Used", f"{fuel_kg:.1f} kg")
            else:
                st.metric("Fuel Used", f"{from_kg(fuel_kg):.1f} lb")
            st.metric("Flight Time", f"{time_hr:.2f} hr" if time_hr is not None else "—")

        with col2:
            if unit_system == "SI (Metric)":
                st.metric("Range", f"{R_km:.1f} km" if R_km is not None else "—")
            else:
                if R_mi is not None and R_nm is not None:
                    st.metric("Range", f"{R_mi:.1f} mi / {R_nm:.1f} nmi")
                else:
                    st.metric("Range", "—")
