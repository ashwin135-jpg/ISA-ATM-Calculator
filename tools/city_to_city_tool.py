import math
import time

import pandas as pd
import streamlit as st
import requests
from geopy.distance import geodesic
from streamlit_echarts import st_echarts  # <-- 3D globe


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


def great_circle_path(coord1, coord2, n_points: int = 200):
    """
    Compute intermediate points along the great-circle between coord1 and coord2.

    coord1, coord2: (lat, lon) in degrees
    Returns: list of (lat, lon) in degrees
    """
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    # Convert to Cartesian
    def to_xyz(lat, lon):
        return [
            math.cos(lat) * math.cos(lon),
            math.cos(lat) * math.sin(lon),
            math.sin(lat),
        ]

    p1 = to_xyz(lat1, lon1)
    p2 = to_xyz(lat2, lon2)

    # Angle between the points
    dot = sum(a * b for a, b in zip(p1, p2))
    dot = max(-1.0, min(1.0, dot))  # numerical safety
    omega = math.acos(dot)
    sin_omega = math.sin(omega)

    if sin_omega == 0:
        # Points are identical or extremely close
        return [coord1, coord2]

    points = []
    for i in range(n_points + 1):
        t = i / n_points
        k1 = math.sin((1 - t) * omega) / sin_omega
        k2 = math.sin(t * omega) / sin_omega
        x = k1 * p1[0] + k2 * p2[0]
        y = k1 * p1[1] + k2 * p2[1]
        z = k1 * p1[2] + k2 * p2[2]
        lat = math.atan2(z, (x * x + y * y) ** 0.5)
        lon = math.atan2(y, x)
        points.append((math.degrees(lat), math.degrees(lon)))

    return points


def render_globe(coords_1, coords_2, progress: float):
    """
    Renders a 3D globe showing a great-circle route between two coordinates.
    progress: 0.0 → departure, 1.0 → arrival
    """
    lat1, lon1 = coords_1
    lat2, lon2 = coords_2

    path = great_circle_path(coords_1, coords_2, n_points=200)
    idx = int(progress * (len(path) - 1))
    plane_lat, plane_lon = path[idx]

    # NO external textures – just colored, shaded sphere
    option = {
        "backgroundColor": "#000000",
        "globe": {
            "shading": "lambert",
            "baseColor": "#1b4f72",      # ocean blue
            "environment": "#000000",
            "displacementScale": 0.0,    # smooth sphere
            "light": {
                "ambient": {"intensity": 0.6},
                "main": {"intensity": 0.8},
            },
            "viewControl": {
                "autoRotate": False,
                "autoRotateAfterStill": 5,
                "distance": 180,
            },
        },
        "series": [
            {
                "type": "lines3D",
                "coordinateSystem": "globe",
                "blendMode": "lighter",
                "effect": {
                    "show": True,
                    "trailWidth": 4,
                    "trailOpacity": 0.7,
                    "trailLength": 0.3,
                },
                "lineStyle": {
                    "width": 2,
                    "color": "#00aaff",
                    "opacity": 0.9,
                },
                "data": [
                    {
                        "coords": [
                            [lon1, lat1],
                            [lon2, lat2],
                        ]
                    }
                ],
            },
            {
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "symbol": "pin",
                "symbolSize": 26,
                "itemStyle": {"color": "yellow"},
                "data": [[plane_lon, plane_lat, 0]],
            },
        ],
    }

    st_echarts(option, height="600px")



def render():
    st.subheader("City to City Travel")
    st.markdown(
        "Given two cities, estimate which aircraft in a simple database "
        "can complete the route, along with approximate flight time and fuel, "
        "and visualize the great-circle route on a **3D globe**."
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

        # Great-circle distance (geodesic)
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

        # --- 3D Globe ---
        st.markdown("### 🌍 3D Globe Route Visualization")
        progress = st.slider(
            "Route progress (0 = departure, 1 = arrival)",
            0.0,
            1.0,
            0.0,
            0.01,
        )
        render_globe(coords_1, coords_2, progress)

    except Exception as e:
        st.error(f"🌐 Location lookup failed: {e}")
