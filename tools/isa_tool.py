import streamlit as st
from utils import isa_atmosphere, convert_altitude


def render():
    st.subheader("ISA Air Properties")

    unit = st.selectbox("Select input unit", ["meters", "feet", "kilometers"])

    if unit == "meters":
        user_alt = st.number_input(
            "Enter altitude (m)", min_value=0.0, max_value=47000.0, step=500.0
        )
    elif unit == "feet":
        user_alt = st.number_input(
            "Enter altitude (ft)", min_value=0.0, max_value=154200.0, step=10000.0
        )
    else:
        user_alt = st.number_input(
            "Enter altitude (km)", min_value=0.0, max_value=47.0, step=0.5
        )

    alt_m = convert_altitude(user_alt, unit, "meters")
    results = isa_atmosphere(alt_m)

    if results is None:
        st.error("Altitude must be less than 47,000 meters for the ISA model.")
        return

    T_K, P, rho, a = results

    unit_system = st.radio("Select unit system", ["Metric", "Imperial"])

    if unit_system == "Imperial":
        T_display = (T_K - 273.15) * 9.0 / 5.0 + 32.0  # K → °F
        P_display = P / 6894.76                        # Pa → psi
        rho_display = rho / 515.3788                   # kg/m³ → slug/ft³
        a_display = a * 3.28084                        # m/s → ft/s
        T_unit, P_unit, rho_unit, a_unit = "°F", "psi", "slug/ft³", "ft/s"
    else:
        T_display, P_display, rho_display, a_display = T_K, P, rho, a
        T_unit, P_unit, rho_unit, a_unit = "K", "Pa", "kg/m³", "m/s"

    st.subheader("Results")
    st.markdown(
        f"Input Altitude: {user_alt:0.2f} {unit}  \n"
        f"**Converted Altitude:** {alt_m:0.0f} m"
    )
    st.metric(f"Temperature ({T_unit})", f"{T_display:0.2f}")
    st.metric(f"Pressure ({P_unit})", f"{P_display:0.2f}")
    st.metric(f"Density ({rho_unit})", f"{rho_display:0.6f}")
    st.metric(f"Speed of Sound ({a_unit})", f"{a_display:0.2f}")
