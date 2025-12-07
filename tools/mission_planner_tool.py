import math
import streamlit as st


def render():
    st.subheader("Simple Mission Planner")
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

    # --- Basic sanity check ---
    Wi = W_total
    Wf = Wi - fuel_weight
    if Wf <= 0 or Wi <= Wf:
        st.error(
            "Invalid weight combination. Make sure fuel_weight < total weight "
            "and greater than zero."
        )
        return

    # --- Calculations ---
    c_sec = c / 3600.0  # 1/s

    try:
        # Breguet range (mass form; g cancels in Wi/Wf)
        R_m = (cruise_speed / c_sec) * LD * math.log(Wi / Wf)
        R_km = R_m / 1000.0
        R_nm = R_km * 0.539957
        R_mi = R_km * 0.621371

        # Flight time (seconds → hours)
        time_hr = R_m / cruise_speed / 3600.0

        # --- Outputs ---
        st.markdown("### 📊 Estimated Mission Performance")

        col1, col2 = st.columns(2)
        with col1:
            if unit_system == "SI (Metric)":
                st.metric("Fuel Used", f"{fuel_weight:.1f} kg")
            else:
                st.metric("Fuel Used", f"{from_kg(fuel_weight):.1f} lb")
            st.metric("Flight Time", f"{time_hr:.2f} hr")

        with col2:
            if unit_system == "SI (Metric)":
                st.metric("Range", f"{R_km:.1f} km")
            else:
                st.metric("Range", f"{R_mi:.1f} mi / {R_nm:.1f} nmi")

    except ValueError:
        st.error("Invalid input combination. Ensure Wi > Wf and values are realistic.")
