import streamlit as st
import requests
from utils import convert_altitude


BACKEND_URL = "http://127.0.0.1:8000"


def call_backend_isa(altitude_m: float):
    """
    Call the ISA backend endpoint with altitude in meters.
    Returns (data_dict, error_message).
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/isa",
            params={"altitude_m": altitude_m},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


def render():
    st.subheader("ISA Air Properties")

    # -----------------------
    # Input: altitude + unit
    # -----------------------
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

    # Convert to meters for backend
    alt_m = convert_altitude(user_alt, unit, "meters")

    # For now, backend is implemented for troposphere (0–11 km).
    # You previously allowed up to 47 km; we'll expand the backend later.
    if alt_m > 11000.0:
        st.error(
            "Backend ISA model currently supports up to 11,000 m. "
            "Please enter an altitude <= 11 km for now."
        )
        return

    # -----------------------
    # Unit system selection
    # -----------------------
    unit_system = st.radio("Select unit system", ["Metric", "Imperial"])

    # -----------------------
    # Trigger calculation
    # -----------------------
    if st.button("Calculate ISA Air Properties"):
        with st.spinner("Querying ISA backend..."):
            data, error = call_backend_isa(alt_m)

        if error:
            st.error(f"Error calling ISA backend: {error}")
            return

        if not data:
            st.error("No data returned from backend.")
            return

        # Backend returns:
        # altitude_m, temperature_K, pressure_Pa, density_kg_m3, speed_of_sound_m_s
        T_K = data.get("temperature_K")
        P = data.get("pressure_Pa")
        rho = data.get("density_kg_m3")
        a = data.get("speed_of_sound_m_s")

        # -----------------------
        # Convert for output
        # -----------------------
        if unit_system == "Imperial":
            # K → °F
            T_display = (T_K - 273.15) * 9.0 / 5.0 + 32.0
            # Pa → psi
            P_display = P / 6894.76
            # kg/m³ → slug/ft³
            rho_display = rho / 515.3788
            # m/s → ft/s
            a_display = a * 3.28084

            T_unit, P_unit, rho_unit, a_unit = "°F", "psi", "slug/ft³", "ft/s"
        else:
            T_display, P_display, rho_display, a_display = T_K, P, rho, a
            T_unit, P_unit, rho_unit, a_unit = "K", "Pa", "kg/m³", "m/s"

        # -----------------------
        # Display results
        # -----------------------
        st.subheader("Results")
        st.markdown(
            f"Input Altitude: {user_alt:0.2f} {unit}  \n"
            f"**Converted Altitude used by backend:** {alt_m:0.0f} m"
        )
        st.metric(f"Temperature ({T_unit})", f"{T_display:0.2f}")
        st.metric(f"Pressure ({P_unit})", f"{P_display:0.2f}")
        st.metric(f"Density ({rho_unit})", f"{rho_display:0.6f}")
        st.metric(f"Speed of Sound ({a_unit})", f"{a_display:0.2f}")
