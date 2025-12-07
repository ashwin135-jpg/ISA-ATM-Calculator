import streamlit as st
from utils import isa_atmosphere, convert_altitude


def render():
    st.subheader("Mach Number Calculator")
    st.markdown("Calculate Mach number based on altitude and airspeed.")

    # --- Inputs ---
    col1, col2 = st.columns(2)

    with col1:
        alt_unit = st.selectbox("Altitude unit", ["meters", "feet", "kilometers"])
        user_alt = st.number_input(
            "Altitude",
            min_value=0.0,
            max_value=47000.0,
            step=500.0,
            value=0.0,
        )

    with col2:
        speed_unit = st.selectbox("Airspeed unit", ["m/s", "ft/s", "knots"])
        V_input = st.number_input(
            "Airspeed",
            min_value=0.0,
            value=250.0,
        )

    # Convert altitude to meters
    alt_m = convert_altitude(user_alt, alt_unit, "meters")

    # Convert speed to m/s
    if speed_unit == "m/s":
        V_ms = V_input
    elif speed_unit == "ft/s":
        V_ms = V_input / 3.28084
    else:  # knots
        V_ms = V_input * 0.514444

    # --- Atmosphere & Mach ---
    results = isa_atmosphere(alt_m)
    if results is None:
        st.error("Altitude must be less than 47,000 meters for the ISA model.")
        return

    _, _, _, a = results  # speed of sound [m/s]
    mach = V_ms / a if a > 0 else 0.0

    # Flow regime classification
    if mach < 0.3:
        regime = "Incompressible"
    elif mach < 0.8:
        regime = "Subsonic"
    elif mach < 1.2:
        regime = "Transonic"
    elif mach < 5.0:
        regime = "Supersonic"
    else:
        regime = "Hypersonic"

    # --- Outputs ---
    st.markdown(
        f"**ISA Speed of Sound at {user_alt:.0f} {alt_unit}:** {a:.2f} m/s"
    )

    st.metric("Mach Number", f"{mach:.3f}")
    st.success(f"Flow Regime: {regime}")
