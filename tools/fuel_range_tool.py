import math
import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def render():
    st.subheader("Fuel Consumption & Range Estimator")
    st.markdown(
        "Estimate aircraft **range**, **endurance**, and **fuel burn time** using "
        "the Breguet Jet Range Equation and a simple thrust-based fuel model."
    )

    # --- Unit system selector ---
    unit_system = st.radio("Select unit system", ["SI (Metric)", "Imperial (English)"])

    # --- USER INPUTS ---
    if unit_system == "SI (Metric)":
        V = st.number_input("Cruise speed (m/s)", min_value=10.0, value=230.0)
        pax = st.number_input("Number of passengers", min_value=0, value=100)
        pax_wt = st.number_input("Avg passenger weight (kg)", min_value=50.0, value=80.0)
        W_empty = st.number_input(
            "Empty aircraft weight (kg)", min_value=0.0, value=25000.0
        )
        W_fuel = st.number_input("Fuel weight (kg)", min_value=0.0, value=10000.0)
    else:
        V_ft = st.number_input(
            "Cruise speed (ft/s)", min_value=30.0, value=755.0
        )
        V = V_ft / 3.28084  # ft/s → m/s

        pax = st.number_input("Number of passengers", min_value=0, value=100)
        pax_wt_lb = st.number_input(
            "Avg passenger weight (lb)", min_value=110.0, value=176.0
        )
        pax_wt = pax_wt_lb * 0.453592  # lb → kg

        W_empty_lb = st.number_input(
            "Empty aircraft weight (lb)", min_value=0.0, value=55115.6
        )
        W_empty = W_empty_lb * 0.453592  # lb → kg

        W_fuel_lb = st.number_input(
            "Fuel weight (lb)", min_value=0.0, value=22046.2
        )
        W_fuel = W_fuel_lb * 0.453592  # lb → kg

    # Derived weights (for validation + display)
    W_pax = pax * pax_wt                    # kg
    Wi = W_empty + W_fuel + W_pax           # initial mass [kg]
    Wf = Wi - W_fuel                        # final mass [kg] after fuel burned

    # Performance inputs
    c = st.number_input(
        "Specific fuel consumption (1/hr)", min_value=0.1, value=0.6
    )
    LD = st.number_input(
        "Lift-to-drag ratio (L/D)", min_value=5.0, value=15.0
    )
    S = st.number_input("Wing area S (m²)", min_value=5.0, value=30.0)
    b = st.number_input("Wingspan b (m)", min_value=5.0, value=28.0)
    CD0 = st.number_input(
        "Zero-lift drag coefficient (CD₀)", min_value=0.0, value=0.02
    )
    e = st.number_input(
        "Oswald efficiency factor (e)",
        min_value=0.1,
        max_value=1.0,
        value=0.8,
    )

    # --- SAFETY CHECK (same logic as before) ---
    if Wf <= 0 or Wi <= Wf:
        st.error(
            "Invalid weight combination. Make sure fuel weight is positive and "
            "initial weight is greater than final weight."
        )
        return

    # --- Call backend for Breguet + drag math ---
    if st.button("Compute Fuel & Range"):
        payload = {
            "V_ms": V,
            "pax": int(pax),
            "pax_wt_kg": pax_wt,
            "W_empty_kg": W_empty,
            "W_fuel_kg": W_fuel,
            "c_per_hr": c,
            "LD": LD,
            "S_m2": S,
            "b_m": b,
            "CD0": CD0,
            "e": e,
        }

        try:
            with st.spinner("Querying ISA backend for fuel & range..."):
                resp = requests.post(
                    f"{BACKEND_URL}/api/fuel-range/estimate",
                    json=payload,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as ex:
            st.error(f"Error calling Fuel & Range backend: {ex}")
            return

        # Unpack backend results
        Wi_kg = data.get("Wi_kg", Wi)
        Wf_kg = data.get("Wf_kg", Wf)
        W_pax_kg = data.get("W_pax_kg", W_pax)

        range_km = data.get("range_km")
        range_nm = data.get("range_nm")
        endurance_hr = data.get("endurance_hr")
        t_hr = data.get("fuel_burn_time_hr")
        t_min = data.get("fuel_burn_time_min")

        V_ms = data.get("V_ms", V)

        # --- UNIT CONVERSIONS FOR DISPLAY (same format as original) ---
        if unit_system == "Imperial (English)":
            Wi_disp = Wi_kg / 0.453592
            Wf_disp = Wf_kg / 0.453592
            W_pax_disp = W_pax_kg / 0.453592
            range_disp = f"{range_km * 0.621371:.1f} mi / {range_nm:.1f} nmi"
            speed_disp = f"{V_ms * 3.28084:.1f} ft/s"
            weight_unit = "lb"
        else:
            Wi_disp = Wi_kg
            Wf_disp = Wf_kg
            W_pax_disp = W_pax_kg
            range_disp = f"{range_km:.1f} km / {range_nm:.1f} nmi"
            speed_disp = f"{V_ms:.1f} m/s"
            weight_unit = "kg"

        # --- OUTPUTS (same layout as before) ---
        st.markdown("### 📊 Summary of Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Initial Weight", f"{Wi_disp:.1f} {weight_unit}")
            st.metric("Final Weight", f"{Wf_disp:.1f} {weight_unit}")
            st.metric("Passenger Mass", f"{W_pax_disp:.1f} {weight_unit}")
        with col2:
            st.metric("Cruise Speed", speed_disp)
            st.metric("Range", range_disp)
            st.metric(
                "Endurance",
                f"{endurance_hr:.2f} hr" if endurance_hr is not None else "—",
            )
            st.metric(
                "Fuel Burn Time",
                f"{t_hr:.2f} hr ({t_min:.0f} min)"
                if t_hr is not None and t_min is not None
                else "—",
            )
