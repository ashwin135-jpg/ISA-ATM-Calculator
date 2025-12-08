import math
import time

import pandas as pd
import streamlit as st
import requests
from geopy.distance import geodesic
from streamlit_folium import st_folium
import folium


def geocode_city(city_name: str):
    """
    Geocode a city name using the free Open-Meteo geocoding API.

    Returns (lat, lon) tuple or None if not found.
    """
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city_name}&count=1&language=en&format=json"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "results" in data and len(data["results"]) > 0:
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            return (lat, lon)
        return None
    except Exception as e:
        # Let the caller handle the error message
        st.error(f"🌐 Geocoding error for '{city_name}': {e}")
        return None


def render():
    st.subheader("🌍 City-to-City Aircraft Suggestion Tool")
    st.markdown(
        "Given two cities, estimate which aircraft in a simple database "
        "can complete the route, along with approximate flight time and fuel."
    )

    # --- Aircraft database (very simplified) ---
    aircraft_data = {
        "Boeing 737-800": {
            "cruise_speed": 230,  # m/s
            "SFC": 0.58,          # 1/hr
            "LD": 15,
            "fuel_capacity": 26000,   # kg (approx)
            "max_takeoff_weight": 79015,
        },
        "Boeing 787-9": {
            "cruise_speed": 250,
            "SFC": 0.52,
            "LD": 19,
            "fuel_capacity": 101000,
            "max_takeoff_weight": 254000,
        },
        "Airbus A320neo": {
            "cruise_speed": 230,
            "SFC": 0.57,
            "LD": 16,
            "fuel_capacity": 24210,
            "max_takeoff_weight": 79000,
        },
        "Airbus A350-900": {
            "cruise_speed": 250,
            "SFC": 0.50,
            "LD": 20,
            "fuel_capacity": 140000,
            "max_takeoff_weight": 280000,
        },
        "Airbus A330-300": {
            "cruise_speed": 240,
            "SFC": 0.55,
            "LD": 18,
            "fuel_capacity": 97530,
            "max_takeoff_weight": 242000,
        },
        "Embraer E190": {
            "cruise_speed": 220,
            "SFC": 0.60,
            "LD": 14,
            "fuel_capacity": 13000,
            "max_takeoff_weight": 51000,
        },
        "Bombardier CRJ900": {
            "cruise_speed": 220,
            "SFC": 0.62,
            "LD": 13,
            "fuel_capacity": 12000,
            "max_takeoff_weight": 38400,
        },
        "Gulfstream G650": {
            "cruise_speed": 250,
            "SFC": 0.54,
            "LD": 18,
            "fuel_capacity": 18300,
            "max_takeoff_weight": 45000,
        },
        "Cessna Citation X": {
            "cruise_speed": 260,
            "SFC": 0.65,
            "LD": 15,
            "fuel_capacity": 5600,
            "max_takeoff_weight": 16000,
        },
        "F-16 Fighting Falcon": {
            "cruise_speed": 270,
            "SFC": 1.2,
            "LD": 6,
            "fuel_capacity": 3000,
            "max_takeoff_weight": 12000,
        },
        "C-130 Hercules": {
            "cruise_speed": 180,
            "SFC": 0.75,
            "LD": 11,
            "fuel_capacity": 19000,
            "max_takeoff_weight": 70300,
        },
    }

    # --- Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        departure_city = st.text_input("Departure City", value="Singapore")
    with col2:
        destination_city = st.text_input("Destination City", value="Los Angeles")

    if not (departure_city and destination_city):
        st.info("Enter both a departure and destination city to begin.")
        return

    try:
        with st.spinner("Geocoding cities..."):
            coords_1 = geocode_city(departure_city)
            time.sleep(0.3)  # tiny pause, not strictly needed
            coords_2 = geocode_city(destination_city)

        if not coords_1 or not coords_2:
            st.error("❌ Could not locate one or both cities. Try more specific names.")
            return

        distance_km = geodesic(coords_1, coords_2).kilometers
        distance_m = distance_km * 1000.0

        # --- Evaluate each aircraft ---
        output_rows = []
        for name, ac in aircraft_data.items():
            V = ac["cruise_speed"]        # m/s
            c = ac["SFC"]                 # 1/hr
            LD = ac["LD"]
            fuel_capacity = ac["fuel_capacity"]           # kg
            MTOW = ac["max_takeoff_weight"]               # kg (approx)
            c_sec = c / 3600.0

            try:
                # Max range using Breguet with MTOW and MTOW - fuel_capacity
                R_max_m = (V / c_sec) * LD * math.log(
                    MTOW / (MTOW - fuel_capacity)
                )

                if distance_m <= R_max_m:
                    # Fuel needed for this specific distance
                    Wf = MTOW / math.exp((c_sec * distance_m) / (V * LD))
                    fuel_needed = MTOW - Wf

                    # Effective speed ~ 85% of cruise
                    effective_speed_ms = V * 0.85
                    time_hr = distance_km * 1000.0 / effective_speed_ms / 3600.0

                    output_rows.append(
                        {
                            "Aircraft": name,
                            "Flight Time (hr)": round(time_hr, 2),
                            "Fuel Needed (kg)": round(fuel_needed, 1),
                        }
                    )
            except (ValueError, ZeroDivisionError):
                # Skip aircraft with invalid parameters
                continue

        if not output_rows:
            st.warning("❌ No aircraft in the database can complete this journey.")
            return

        df_results = pd.DataFrame(output_rows)

        # --- Summary stats ---
        avg_time = df_results["Flight Time (hr)"].mean()

        st.markdown("### ✈️ Route Summary")
        colA, colB = st.columns(2)
        with colA:
            st.metric(label="📏 Route Distance", value=f"{distance_km:.1f} km")
        with colB:
            st.metric(label="⏱ Average Flight Time", value=f"{avg_time:.2f} hr")

        st.subheader(
            f"{departure_city} → {destination_city}  "
            f"({distance_km:.1f} km)"
        )

        st.dataframe(
            df_results.sort_values("Fuel Needed (kg)").reset_index(drop=True),
            use_container_width=True,
        )

        # --- Route map ---
        theme = st.get_option("theme.base")
        tiles = "CartoDB dark_matter" if theme == "dark" else "CartoDB positron"

        mid_lat = (coords_1[0] + coords_2[0]) / 2.0
        mid_lon = (coords_1[1] + coords_2[1]) / 2.0

        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=3, tiles=tiles)

        folium.Marker(
            coords_1,
            popup=f"Departure: {departure_city}",
            icon=folium.Icon(color="green"),
        ).add_to(m)
        folium.Marker(
            coords_2,
            popup=f"Destination: {destination_city}",
            icon=folium.Icon(color="red"),
        ).add_to(m)
        folium.PolyLine(
            [coords_1, coords_2],
            color="blue",
            weight=3,
            opacity=0.8,
        ).add_to(m)

        st.subheader("🗺 Route Map")
        st_folium(m, width=700, height=300)

    except Exception as e:
        st.error(f"🌐 Location lookup failed: {e}")
