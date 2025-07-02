import streamlit as st
import math
from streamlit_lottie import st_lottie
import requests

# Handle incoming query param
default_tool = st.query_params.get("tool", "Home")
if "tool" not in st.session_state:
    st.session_state["tool"] = default_tool

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Load Lottie animations
lottie_home = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_isa = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_mach = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_lift = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_fuel = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_mission = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")
lottie_city = load_lottieurl("https://lottie.host/68ecc80f-3865-4071-89bf-1db845e65c6e/O67It7eqk8.json")


def isa_atmosphere(altitude_m):
    R = 287  # Specific gas constant for dry air in J/(kg
    g = 9.81  # Standard acceleration of gravity in m/s^2
    gamma = 1.4  # Ratio of specific heats for air
    T0 = 273.15  # Standard temperature at sea level in K

    if altitude_m < 11000:  # Troposphere
        T = 15.04 - 0.00649 * altitude_m
        P = 101325 * ((T + 273.1)/288.08)**5.256
        
    
    elif altitude_m < 25000:  # Lower Stratosphere
        T = -56.46
        P = 22.65*1000 * math.exp(1.73 - 0.000157 * altitude_m)

    elif altitude_m < 47000:  # Upper Stratosphere
        T = -131.21 + 0.00299 * altitude_m
        P = 2.488 *1000 * ((T + 273.15) / 216.6)**-11.388
        
    else:
        return None
    rho = P / (R * (T + 273.15))
    T_absolute = T + T0
    a = math.sqrt(gamma * R * T_absolute)
    return T, P, rho, a


def convert_altitude(value, from_unit, to_unit):
    if from_unit == "meters":
        value_m = value
    elif from_unit == "feet":
        value_m = value * 0.3048
    elif from_unit == "kilometers":
        value_m = value * 1000
    else:
        raise ValueError("Invalid from_unit. Use 'meters', 'feet', or 'kilometers'.")
    
    if to_unit == "meters":
        return value_m
    elif to_unit == "feet":
        return value_m / 0.3048
    elif to_unit == "kilometers":
        return value_m / 1000
    else:
        raise ValueError("Invalid to_unit. Use 'meters', 'feet', or 'kilometers'.")
       
st.title("✈ ISA Master Tool")

tool_options = [
    "Home",
    "ISA Atmosphere Calculator",
    "Mach Number Calculator",
    "Lift and Drag Calculator",
    "Fuel Consumption & Range Estimator",
    "Mission Planner",
    "City-to-City Flight Estimator"
]

tool = st.sidebar.selectbox("Select a Tool", tool_options, index=tool_options.index(st.session_state["tool"]))
st.session_state["tool"] = tool  # keep session state in sync
st.query_params["tool"] = tool


if tool == "ISA Atmosphere Calculator" and lottie_isa:
    st_lottie(lottie_isa, height=250, key="isa")
elif tool == "Mach Number Calculator" and lottie_mach:
    st_lottie(lottie_mach, height=250, key="mach")
elif tool == "Lift and Drag Calculator" and lottie_lift:
    st_lottie(lottie_lift, height=250, key="lift")
elif tool == "Fuel Consumption & Range Estimator" and lottie_fuel:
    st_lottie(lottie_fuel, height=250, key="fuel")
elif tool == "Mission Planner" and lottie_mission:
    st_lottie(lottie_mission, height=250, key="mission")
elif tool == "City-to-City Flight Estimator" and lottie_city:
    st_lottie(lottie_city, height=250, key="city")


# Home Page===========================================================================================================================
if tool == "Home":
    # Redirect to external HTML homepage
    homepage_url = "file:///Users/ashwinganesh/Documents/sample/my%20tool/%3C!DOCTYPE%20html%3E.html"  
    st.markdown(f"""
        <meta http-equiv="refresh" content="0; url={homepage_url}">
        <script>
            window.location.href = "{homepage_url}";
        </script>
        <p>If you are not redirected, <a href="{homepage_url}">click here</a>.</p>
    """, unsafe_allow_html=True)

#ISA Atmosphere Calculator====================================================================================================================
if tool == "ISA Atmosphere Calculator":
    st.subheader("ISA Atmosphere Calculator")
    unit = st.selectbox("Select input unit", ["meters", "feet", "kilometers"])

    if unit == "meters":
        user_alt = st.number_input("Enter altitude (m)", min_value = 0.0, max_value = 47000.0, step=500.0)
    elif unit == "feet":
        user_alt = st.number_input("Enter altitude (ft)", min_value = 0.0, max_value = 154200.0, step=10000.0)
    elif unit == "kilometers":
        user_alt = st.number_input("Enter altitude (km)", min_value = 0.0, max_value = 47.0, step=0.5)

    alt_m = convert_altitude(user_alt, unit, "meters")
    results = isa_atmosphere(alt_m)

    if results:
        T, P, rho, a = results
        unit_system = st.radio("Select unit system", ["Metric", "Imperial"])
        if unit_system == "Imperial":
            T_display = (T - 273.15) * 9/5 + 32
            P_display = P / 6894.76 
            rho_display = rho / 515.3788
            a_display = a * 3.28084

            T_unit = "°F"
            P_unit = "psi"
            rho_unit = "slugs/ft³"
            a_unit = "ft/s"
        else:
            T_display = T
            P_display = P
            rho_display = rho
            a_display = a

            T_unit = "K"
            P_unit = "Pa"
            rho_unit = "kg/m³"
            a_unit = "m/s"

        st.subheader("Results")
        st.markdown(f"Input Altitude: {user_alt:0.2f} {unit} \n"
                    f"**Converted Altitude :** {alt_m: 0.0f} m")
        st.metric(f"Temperature ({T_unit})", f"{T_display:0.2f}")
        st.metric(f"Pressure ({P_unit})", f"{P_display:0.2f}")
        st.metric(f"Density ({rho_unit})", f"{rho_display:0.6f}")
        st.metric(f"Speed of Sound ({a_unit})", f"{a_display:0.2f}")
    else:
        st.error("Altitude must be less than 47,000 meters for the ISA model.")

#Mach Number Calculator===================================================================================================================
elif tool == "Mach Number Calculator":
    st.subheader("Mach Number Calculator")
    st.markdown("Calculate Mach number based on altitude and airspeed.")


    alt_unit = st.selectbox("Select altitude unit", ["meters", "feet", "kilometers"])
    speed_unit = st.selectbox("Select airspeed unit", ["m/s", "ft/s", "knots"])


    user_alt = st.number_input("Enter altitude", min_value=0.0, max_value=47000.0, step=500.0)
    V = st.number_input("Enter airspeed", min_value=0.0, value=250.0)


    alt_m = convert_altitude(user_alt, alt_unit, "meters")

    
    if speed_unit == "m/s":
        V_ms = V
    elif speed_unit == "ft/s":
        V_ms = V / 3.28084
    elif speed_unit == "knots":
        V_ms = V * 0.514444

    # Get speed of sound from ISA
    results = isa_atmosphere(alt_m)
    if results:
        _, _, _, a = results
        mach = V_ms / a

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

        # Output
        st.markdown(f"**ISA Speed of Sound at {user_alt:.0f} {alt_unit}:** {a:.2f} m/s")
        st.metric("Mach Number", f"{mach:.3f}")
        st.success(f"Flow Regime: {regime}")
    else:
        st.error("Altitude must be less than 47,000 meters for ISA model.")

#Lift & Drag Calculator==================================================================================================================
elif tool == "Lift and Drag Calculator":
    st.subheader("✈️ Lift and Drag Calculator")
    st.markdown("Estimate aerodynamic forces and coefficients at different altitudes assuming level flight (Lift = Weight).")

    # Unit system selector
    unit_system = st.radio("Select unit system", ["Metric (SI)", "Imperial (English)"])

    # Altitude
    alt_unit = st.selectbox("Altitude unit", ["meters", "feet", "kilometers"])
    user_alt = st.number_input("Enter altitude", min_value=0.0, max_value=47000.0, step=500.0)
    alt_m = convert_altitude(user_alt, alt_unit, "meters")

    # Input fields (unit-dependent)
    if unit_system == "Imperial (English)":
        V_input = st.number_input("Enter airspeed (ft/s)", value=300.0)
        V = V_input / 3.28084  # ft/s → m/s

        weight_lb = st.number_input("Enter aircraft weight (lb)", value=1650.0)
        W = weight_lb * 4.44822  # lb → N
        mass = W / 9.81

        S_input = st.number_input("Wing area (ft²)", value=175.0)
        S = S_input * 0.092903  # ft² → m²

        b_input = st.number_input("Wingspan (ft)", value=36.0)
        b = b_input * 0.3048  # ft → m
    else:
        V = st.number_input("Enter airspeed (m/s)", value=100.0)
        mass = st.number_input("Enter aircraft mass (kg)", value=750.0)
        W = mass * 9.81

        S = st.number_input("Wing area (m²)", value=16.2)
        b = st.number_input("Wingspan (m)", value=10.9)

    # Drag parameters
    CD0 = st.number_input("Zero-lift drag coefficient (CD₀)", min_value=0.0, value=0.02)
    e = st.number_input("Oswald efficiency factor (e)", min_value=0.1, max_value=1.0, value=0.8)

    # ISA atmosphere
    results = isa_atmosphere(alt_m)
    if results:
        _, _, rho, _ = results
        q = 0.5 * rho * V**2
        CL = W / (q * S)
        AR = b**2 / S
        k = 1 / (math.pi * e * AR)
        CD = CD0 + k * CL**2
        D = q * S * CD

        # Convert results to imperial if needed
        if unit_system == "Imperial (English)":
            L_out = W / 4.44822         # N → lb
            D_out = D / 4.44822
            rho_out = rho / 515.3788
            speed_out = V * 3.28084
            force_unit = "lb"
            area_unit = "ft²"
            rho_unit = "slug/ft³"
            speed_unit = "ft/s"
        else:
            L_out = W
            D_out = D
            rho_out = rho
            speed_out = V
            force_unit = "N"
            area_unit = "m²"
            rho_unit = "kg/m³"
            speed_unit = "m/s"

    # Output
    st.markdown("### 📊 Results Dashboard")

    # Group 1: Forces
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Lift", value=f"{L_out:.1f} {force_unit}")
        st.metric(label="Drag", value=f"{D_out:.1f} {force_unit}")
    with col2:
        st.metric(label="Airspeed", value=f"{speed_out:.1f} {speed_unit}")
        st.metric(label="Air Density", value=f"{rho_out:.4f} {rho_unit}")

    # Divider
    st.markdown("---")

    # Group 2: Coefficients
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label="Lift Coefficient", value=f"{CL:.4f}")
        st.metric(label="Drag Coefficient", value=f"{CD:.4f}")
    with col4:
        st.metric(label="Aspect Ratio (AR)", value=f"{AR:.2f}")
        st.metric(label="Induced Drag Factor (k)", value=f"{k:.5f}")

elif tool == "Fuel Consumption & Range Estimator":
    st.subheader("⛽ Jet Fuel Consumption & Range Estimator")
    st.markdown("Estimate aircraft **range**, **endurance**, and **fuel burn time** using the Breguet Jet Range Equation and a thrust-based fuel model.")

    # --- Unit system selector ---
    unit_system = st.radio("Select unit system", ["SI (Metric)", "Imperial (English)"])

    # --- USER INPUTS ---
    if unit_system == "SI (Metric)":
        V = st.number_input("Cruise speed (m/s)", min_value=10.0, value=230.0)
        pax = st.number_input("Number of passengers", min_value=0, value=100)
        pax_wt = st.number_input("Avg passenger weight (kg)", min_value=50.0, value=80.0)
        W_empty = st.number_input("Empty aircraft weight (kg)", min_value=0.0, value=25000.0)
        W_fuel = st.number_input("Fuel weight (kg)", min_value=0.0, value=10000.0)
    else:
        V_ft = st.number_input("Cruise speed (ft/s)", min_value=30.0, value=755.0)
        V = V_ft / 3.28084  # convert to m/s
        pax = st.number_input("Number of passengers", min_value=0, value=100)
        pax_wt_lb = st.number_input("Avg passenger weight (lb)", min_value=110.0, value=176.0)
        pax_wt = pax_wt_lb * 0.453592  # to kg
        W_empty_lb = st.number_input("Empty aircraft weight (lb)", min_value=0.0, value=55115.6)
        W_empty = W_empty_lb * 0.453592
        W_fuel_lb = st.number_input("Fuel weight (lb)", min_value=0.0, value=22046.2)
        W_fuel = W_fuel_lb * 0.453592

    W_pax = pax * pax_wt
    Wi = W_empty + W_fuel + W_pax
    Wf = Wi - W_fuel
    g = 9.81

    c = st.number_input("Specific fuel consumption (1/hr)", min_value=0.1, value=0.6)
    c_sec = c / 3600  # convert to 1/sec
    LD = st.number_input("Lift-to-drag ratio (L/D)", min_value=5.0, value=15.0)
    S = st.number_input("Wing area S (m²)", min_value=5.0, value=30.0)
    b = st.number_input("Wingspan b (m)", min_value=5.0, value=28.0)
    CD0 = st.number_input("Zero-lift drag coefficient (CD₀)", min_value=0.0, value=0.02)
    e = st.number_input("Oswald efficiency factor (e)", min_value=0.1, max_value=1.0, value=0.8)

    # --- CALCULATIONS ---
    # Breguet Jet Range
    range_m = (V / c_sec) * LD * math.log(Wi / Wf)
    range_km = range_m / 1000
    range_nm = range_km * 0.539957

    # Endurance
    endurance_hr = (1 / c) * LD * math.log(Wi / Wf)

    # Thrust ≈ Drag model
    rho = 1.225  # Approximate sea level density
    q = 0.5 * rho * V**2
    L = Wi * g
    CL = L / (q * S)
    AR = b**2 / S
    k = 1 / (math.pi * e * AR)
    CD = CD0 + k * CL**2
    D = q * S * CD
    fuel_burn_rate = c_sec * D
    t_sec = (W_fuel * g) / fuel_burn_rate
    t_min = t_sec / 60
    t_hr = t_sec / 3600

    # --- UNIT CONVERSIONS (if needed) ---
    if unit_system == "Imperial (English)":
        Wi_disp = Wi / 0.453592
        Wf_disp = Wf / 0.453592
        W_pax_disp = W_pax / 0.453592
        range_disp = f"{range_km * 0.621371:.1f} mi / {range_nm:.1f} nmi"
        speed_disp = f"{V * 3.28084:.1f} ft/s"
    else:
        Wi_disp = Wi
        Wf_disp = Wf
        W_pax_disp = W_pax
        range_disp = f"{range_km:.1f} km / {range_nm:.1f} nmi"
        speed_disp = f"{V:.1f} m/s"

    # --- OUTPUTS ---
    st.markdown("### 📊 Summary of Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Initial Weight", f"{Wi_disp:.1f} {'lb' if unit_system == 'Imperial (English)' else 'kg'}")
        st.metric("Final Weight", f"{Wf_disp:.1f} {'lb' if unit_system == 'Imperial (English)' else 'kg'}")
        st.metric("Passenger Mass", f"{W_pax_disp:.1f} {'lb' if unit_system == 'Imperial (English)' else 'kg'}")
    with col2:
        st.metric("Cruise Speed", speed_disp)
        st.metric("Range", range_disp)
        st.metric("Endurance", f"{endurance_hr:.2f} hr")
        st.metric("Fuel Burn Time", f"{t_hr:.2f} hr ({t_min:.0f} min)")

#Mission Planner=========================================================================================================================
elif tool == "Mission Planner":
    st.subheader("🛫 Simple Mission Planner")
    st.markdown("Estimate **range**, **fuel used**, and **flight time** based on aircraft weight and fuel availability.")

    # --- Unit system selector ---
    unit_system = st.radio("Select unit system", ["SI (Metric)", "Imperial (English)"])

    # --- Unit conversion functions ---
    def to_kg(lb): return lb * 0.453592
    def to_mps(knots): return knots * 0.514444
    def to_km(nm): return nm * 1.852
    def from_kg(kg): return kg / 0.453592
    def from_km(km): return km / 1.852
    def from_mps(mps): return mps / 0.514444

    # --- Inputs ---
    if unit_system == "SI (Metric)":
        W_total = st.number_input("Total aircraft weight (kg)", value=35000.0)
        fuel_weight = st.number_input("Fuel available (kg)", value=10000.0)
        cruise_speed = st.number_input("Cruise speed (m/s)", value=230.0)
    else:
        W_total = to_kg(st.number_input("Total aircraft weight (lb)", value=77162.0))
        fuel_weight = to_kg(st.number_input("Fuel available (lb)", value=22046.0))
        cruise_speed = to_mps(st.number_input("Cruise speed (knots)", value=450.0))

    c = st.number_input("Specific fuel consumption (1/hr)", value=0.6)
    LD = st.number_input("Lift-to-drag ratio (L/D)", value=15.0)

    # --- Calculations ---
    Wi = W_total
    Wf = Wi - fuel_weight
    c_sec = c / 3600

    try:
        R_m = (cruise_speed / c_sec) * LD * math.log(Wi / Wf)
        R_km = R_m / 1000
        R_nm = R_km * 0.539957
        R_mi = R_km * 0.621371

        time_hr = R_m / cruise_speed / 3600  # seconds → hours

        # --- Outputs ---
        st.markdown("### 📊 Estimated Mission Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Fuel Used", f"{fuel_weight:.1f} {'kg' if unit_system == 'SI (Metric)' else f'{from_kg(fuel_weight):.1f} lb'}")
            st.metric("Flight Time", f"{time_hr:.2f} hr")

        with col2:
            if unit_system == "SI (Metric)":
                st.metric("Range", f"{R_km:.1f} km")
            else:
                st.metric("Range", f"{R_mi:.1f} mi / {R_nm:.1f} nmi")
    except:
        st.error("Invalid input combination. Make sure Wi > Wf and values are realistic.")

#City-to-City Flight Estimator================================================================================================================
elif tool == "City-to-City Flight Estimator":
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    import math
    import time
    import pandas as pd
    import altair as alt

    st.subheader("City-to-City Aircraft Suggestion Tool")

    # Aircraft database
    aircraft_data = {
        "Boeing 737-800": {"cruise_speed": 230, "SFC": 0.58, "LD": 15, "fuel_capacity": 26000, "max_takeoff_weight": 79015},
        "Boeing 787-9": {"cruise_speed": 250, "SFC": 0.52, "LD": 19, "fuel_capacity": 101000, "max_takeoff_weight": 254000},
        "Airbus A320neo": {"cruise_speed": 230, "SFC": 0.57, "LD": 16, "fuel_capacity": 24210, "max_takeoff_weight": 79000},
        "Airbus A350-900": {"cruise_speed": 250, "SFC": 0.50, "LD": 20, "fuel_capacity": 140000, "max_takeoff_weight": 280000},
        "Airbus A330-300": {"cruise_speed": 240, "SFC": 0.55, "LD": 18, "fuel_capacity": 97530, "max_takeoff_weight": 242000},
        "Embraer E190": {"cruise_speed": 220, "SFC": 0.60, "LD": 14, "fuel_capacity": 13000, "max_takeoff_weight": 51000},
        "Bombardier CRJ900": {"cruise_speed": 220, "SFC": 0.62, "LD": 13, "fuel_capacity": 12000, "max_takeoff_weight": 38400},
        "Gulfstream G650": {"cruise_speed": 250, "SFC": 0.54, "LD": 18, "fuel_capacity": 18300, "max_takeoff_weight": 45000},
        "Cessna Citation X": {"cruise_speed": 260, "SFC": 0.65, "LD": 15, "fuel_capacity": 5600, "max_takeoff_weight": 16000},
        "F-16 Fighting Falcon": {"cruise_speed": 270, "SFC": 1.2, "LD": 6, "fuel_capacity": 3000, "max_takeoff_weight": 12000},
        "C-130 Hercules": {"cruise_speed": 180, "SFC": 0.75, "LD": 11, "fuel_capacity": 19000, "max_takeoff_weight": 70300}
    }

    # Inputs
    departure_city = st.text_input("Departure City", value="Singapore")
    destination_city = st.text_input("Destination City", value="Los Angeles")

    if departure_city and destination_city:
        geolocator = Nominatim(user_agent="flight_estimator")
        try:
            loc1 = geolocator.geocode(departure_city, timeout=10)
            time.sleep(1)
            loc2 = geolocator.geocode(destination_city, timeout=10)

            if loc1 and loc2:
                coords_1 = (loc1.latitude, loc1.longitude)
                coords_2 = (loc2.latitude, loc2.longitude)
                distance_km = geodesic(coords_1, coords_2).kilometers
                distance_m = distance_km * 1000

                output_rows = []
                for name, ac in aircraft_data.items():
                    V = ac["cruise_speed"]
                    c = ac["SFC"]
                    LD = ac["LD"]
                    fuel_capacity = ac["fuel_capacity"]
                    MTOW = ac["max_takeoff_weight"]
                    c_sec = c / 3600

                    try:
                        R_max_m = (V / c_sec) * LD * math.log(MTOW / (MTOW - fuel_capacity))
                        if distance_m <= R_max_m:
                            Wf = MTOW / math.exp((c_sec * distance_m) / (V * LD))
                            fuel_needed = MTOW - Wf
                            effective_speed = V * 0.85  # 85% of cruise speed
                            time_hr = distance_km / (effective_speed * 3.6)

                            output_rows.append({
                                "Aircraft": name,
                                "Flight Time (hr)": round(time_hr, 2),
                                "Fuel Needed (kg)": round(fuel_needed, 1)
                            })
                    except:
                        continue

                if output_rows:
                    df_results = pd.DataFrame(output_rows)
                   
                    # Summary stats
                    avg_time = df_results["Flight Time (hr)"].mean()
                    min_fuel = df_results["Fuel Needed (kg)"].min()
                    st.markdown(" Route Summary")
                    colA, colB = st.columns(2)

                    with colA:
                        st.metric(label="📏 Route Distance", value=f"{distance_km:.1f} km")

                    with colB:
                        st.metric(label="⏱ Average Flight Time", value=f"{avg_time:.2f} hr")
                    
                    st.subheader(f" {departure_city} → {destination_city} ({distance_km:.1f} km)")
                    st.dataframe(df_results.sort_values("Fuel Needed (kg)").reset_index(drop=True),use_container_width=True)
                    
                    from streamlit_folium import st_folium
                    import folium

                    theme = st.get_option("theme.base")

                    if theme == "dark":
                        tiles = "CartoDB dark_matter"
                    else:
                        tiles = "CartoDB positron"

                    mid_lat = (coords_1[0] + coords_2[0]) / 2
                    mid_lon = (coords_1[1] + coords_2[1]) / 2

                    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=3, tiles=tiles)

                    folium.Marker(coords_1, popup=f"Departure: {departure_city}", icon=folium.Icon(color="green")).add_to(m)
                    folium.Marker(coords_2, popup=f"Destination: {destination_city}", icon=folium.Icon(color="red")).add_to(m)
                    folium.PolyLine([coords_1, coords_2], color="blue", weight=3, opacity=0.8).add_to(m)

                    st.subheader(" Route Map")
                    st_folium(m, width=700, height=250)

                else:
                    st.warning("❌ No aircraft in the database can complete this journey.")
            else:
                st.error("❌ Could not locate one or both cities.")
        except Exception as e:
            st.error(f"🌐 Location lookup failed: {e}")
            
            

# else:
#     st.error("Altitude must be less than 47,000 meters for the ISA model.")