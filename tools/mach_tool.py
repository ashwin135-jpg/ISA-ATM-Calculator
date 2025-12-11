import streamlit as st
import requests
from utils import convert_altitude

BACKEND_URL = "http://127.0.0.1:8000"


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
        # Match backend units: "m/s", "ft/s", "knots"
        speed_unit = st.selectbox("Airspeed unit", ["m/s", "ft/s", "knots"])
        V_input = st.number_input(
            "Airspeed",
            min_value=0.0,
            value=250.0,
        )

    # Convert altitude to meters for backend
    alt_m = convert_altitude(user_alt, alt_unit, "meters")

    # Limitation aligned with backend & ISA endpoint
    if alt_m > 11000.0:
        st.error(
            "Backend Mach model currently supports up to 11,000 m (11 km). "
            "Please enter an altitude <= 11 km for now."
        )
        return

    # --- Backend call ---
    if st.button("Calculate Mach Number"):
        payload = {
            "altitude_m": alt_m,
            "speed_value": V_input,
            "speed_unit": speed_unit,
        }

        try:
            with st.spinner("Querying ISA backend for Mach..."):
                resp = requests.post(
                    f"{BACKEND_URL}/api/mach/compute",
                    json=payload,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            st.error(f"Error calling Mach backend: {e}")
            return

        # --- Unpack backend result ---
        mach = data.get("mach")
        a = data.get("speed_of_sound_m_s")
        regime = data.get("flow_regime")
        T_K = data.get("temperature_K")
        V_ms = data.get("speed_m_s")

        T_C = T_K - 273.15 if T_K is not None else None

        # --- Outputs ---
        if a is not None:
            st.markdown(
                f"**ISA Speed of Sound at {user_alt:.0f} {alt_unit}:** {a:.2f} m/s"
            )

        st.metric("Mach Number", f"{mach:.3f}" if mach is not None else "—")

        if regime:
            st.success(f"Flow Regime: {regime}")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Static Temperature**")
            if T_K is not None:
                st.write(f"{T_K:,.2f} K")
            if T_C is not None:
                st.write(f"{T_C:,.2f} °C")

        with col_right:
            st.markdown("**True Airspeed (normalized)**")
            if V_ms is not None:
                st.write(f"{V_ms:,.2f} m/s")

        st.caption(
            "Mach is computed as V/a, where a is the ISA speed of sound at the given altitude. "
            "Core physics are computed by the private ISA backend."
        )
