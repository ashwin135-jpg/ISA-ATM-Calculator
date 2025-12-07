import math
import streamlit as st
from utils import isa_atmosphere, convert_altitude


def render():
    st.subheader("✈️ Lift and Drag Calculator")
    st.markdown(
        "Estimate aerodynamic forces and coefficients at different altitudes "
        "assuming level flight (Lift = Weight)."
    )

    # --- Unit system selector ---
    unit_system = st.radio("Select unit system", ["Metric (SI)", "Imperial (English)"])

    # --- Altitude input ---
    alt_unit = st.selectbox("Altitude unit", ["meters", "feet", "kilometers"])
    user_alt = st.number_input(
        "Enter altitude",
        min_value=0.0,
        max_value=47000.0,
        step=500.0,
        value=0.0,
    )
    alt_m = convert_altitude(user_alt, alt_unit, "meters")

    # --- Aircraft inputs (unit-dependent) ---
    if unit_system == "Imperial (English)":
        V_input = st.number_input("Airspeed (ft/s)", value=300.0)
        V = V_input / 3.28084  # ft/s → m/s

        weight_lb = st.number_input("Aircraft weight (lb)", value=1650.0)
        W = weight_lb * 4.44822  # lb → N

        S_input = st.number_input("Wing area (ft²)", value=175.0)
        S = S_input * 0.092903  # ft² → m²

        b_input = st.number_input("Wingspan (ft)", value=36.0)
        b = b_input * 0.3048  # ft → m
    else:
        V = st.number_input("Airspeed (m/s)", value=100.0)
        mass = st.number_input("Aircraft mass (kg)", value=750.0)
        W = mass * 9.81  # N

        S = st.number_input("Wing area (m²)", value=16.2)
        b = st.number_input("Wingspan (m)", value=10.9)

    # --- Drag model inputs ---
    CD0 = st.number_input("Zero-lift drag coefficient (CD₀)", min_value=0.0, value=0.02)
    e = st.number_input(
        "Oswald efficiency factor (e)",
        min_value=0.1,
        max_value=1.0,
        value=0.8,
    )

    # --- Atmosphere ---
    results = isa_atmosphere(alt_m)
    if results is None:
        st.error("Altitude must be less than 47,000 meters for the ISA model.")
        return

    _, _, rho, _ = results

    # --- Aerodynamic calculations ---
    q = 0.5 * rho * V**2               # dynamic pressure
    CL = W / (q * S)                   # lift coefficient (Lift = Weight)
    AR = b**2 / S                      # aspect ratio
    k = 1.0 / (math.pi * e * AR)       # induced drag factor
    CD = CD0 + k * CL**2               # total drag coefficient
    D = q * S * CD                     # drag force [N]

    # --- Convert to imperial outputs if needed ---
    if unit_system == "Imperial (English)":
        L_out = W / 4.44822            # N → lb
        D_out = D / 4.44822
        rho_out = rho / 515.3788       # kg/m³ → slug/ft³
        speed_out = V * 3.28084        # m/s → ft/s
        force_unit = "lb"
        rho_unit = "slug/ft³"
        speed_unit = "ft/s"
    else:
        L_out = W
        D_out = D
        rho_out = rho
        speed_out = V
        force_unit = "N"
        rho_unit = "kg/m³"
        speed_unit = "m/s"

    # --- Output dashboard ---
    st.markdown("### 📊 Results Dashboard")

    # Forces
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"Lift ({force_unit})", value=f"{L_out:.1f}")
        st.metric(label=f"Drag ({force_unit})", value=f"{D_out:.1f}")
    with col2:
        st.metric(label=f"Airspeed ({speed_unit})", value=f"{speed_out:.1f}")
        st.metric(label=f"Air Density ({rho_unit})", value=f"{rho_out:.4f}")

    st.markdown("---")

    # Coefficients
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label="Lift Coefficient (CL)", value=f"{CL:.4f}")
        st.metric(label="Drag Coefficient (CD)", value=f"{CD:.4f}")
    with col4:
        st.metric(label="Aspect Ratio (AR)", value=f"{AR:.2f}")
        st.metric(label="Induced Drag Factor (k)", value=f"{k:.5f}")
