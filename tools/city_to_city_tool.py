import math
import time

import pandas as pd
import requests
import streamlit as st
from geopy.distance import geodesic


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
        st.error(f"🌐 Geocoding error for '{city_name}': {e}")
        return None


def get_weather(lat: float, lon: float):
    """
    Fetch current weather at a given lat/lon using Open-Meteo.

    Returns a dict with temperature (°C), wind speed (m/s), wind direction (deg),
    or None on error.
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        current = data.get("current_weather")
        if not current:
            return None

        return {
            "temperature_C": current.get("temperature"),
            "windspeed_ms": current.get("windspeed"),
            "winddirection_deg": current.get("winddirection"),
        }
    except Exception as e:
        st.warning(f"🌦 Weather lookup failed at ({lat:.2f}, {lon:.2f}): {e}")
        return None


def render():
    st.subheader("City to City Travel")
    st.markdown(
        "Given two cities, estimate which aircraft in a simple database "
        "can complete the route, with approximate **flight time**, **fuel** and "
        "**current weather** at each end."
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
            time.sleep(0.3)
            coords_2 = geocode_city(destination_city)

        if not coords_1 or not coords_2:
            st.error("❌ Could not locate one or both cities. Try more specific names.")
            return

        # Great-circle distance
        distance_km = geodesic(coords_1, coords_2).kilometers
        distance_m = distance_km * 1000.0

        # --- Evaluate each aircraft ---
        output_rows = []
        for name, ac in aircraft_data.items():
            V = ac["cruise_speed"]        # m/s
            c = ac["SFC"]                 # 1/hr
            LD = ac["LD"]
            fuel_capacity = ac["fuel_capacity"]     # kg
            MTOW = ac["max_takeoff_weight"]         # kg (approx)
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

                    # Effective cruise ~ 85% of nominal cruise
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
                continue

        if not output_rows:
            st.warning("❌ No aircraft in the database can complete this journey.")
            return

        df_results = pd.DataFrame(output_rows)
        avg_time = df_results["Flight Time (hr)"].mean()

        # --- Summary ---
        st.markdown("### ✈️ Route Summary")
        colA, colB = st.columns(2)
        with colA:
            st.metric("📏 Route Distance", f"{distance_km:.1f} km")
        with colB:
            st.metric("⏱ Average Flight Time", f"{avg_time:.2f} hr")

        st.subheader(
            f"{departure_city} → {destination_city} "
            f"({distance_km:.1f} km)"
        )

        st.dataframe(
            df_results.sort_values("Fuel Needed (kg)").reset_index(drop=True),
            use_container_width=True,
        )

        # --- Weather at departure and destination ---
        st.subheader("🌦 Weather at Departure & Destination")

        dep_weather = get_weather(*coords_1)
        arr_weather = get_weather(*coords_2)

        colW1, colW2 = st.columns(2)

        if dep_weather:
            with colW1:
                st.markdown(f"**{departure_city}**")
                st.metric("Temperature (°C)", f"{dep_weather['temperature_C']:.1f}")
                st.metric("Wind Speed (m/s)", f"{dep_weather['windspeed_ms']:.1f}")
                st.metric(
                    "Wind Direction (°)",
                    f"{dep_weather['winddirection_deg']:.0f}",
                )
        else:
            with colW1:
                st.markdown(f"**{departure_city}**")
                st.info("No weather data available.")

        if arr_weather:
            with colW2:
                st.markdown(f"**{destination_city}**")
                st.metric("Temperature (°C)", f"{arr_weather['temperature_C']:.1f}")
                st.metric("Wind Speed (m/s)", f"{arr_weather['windspeed_ms']:.1f}")
                st.metric(
                    "Wind Direction (°)",
                    f"{arr_weather['winddirection_deg']:.0f}",
                )
        else:
            with colW2:
                st.markdown(f"**{destination_city}**")
                st.info("No weather data available.")

    except Exception as e:
        st.error(f"🌐 Location or route computation failed: {e}")
