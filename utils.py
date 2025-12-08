# utils.py
import requests
import streamlit as st
import math

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# -------------------------
# ISA atmosphere model
# -------------------------
def isa_atmosphere(altitude_m: float):
    """
    Simple ISA model up to ~47 km.

    Returns:
        T (K), P (Pa), rho (kg/m^3), a (m/s)

    Returns None if altitude is out of model range.
    """
    R = 287.0       # J/(kg·K)
    g = 9.80665     # m/s^2
    gamma = 1.4     # ratio of specific heats

    if altitude_m < 0 or altitude_m > 47000:
        return None

    if altitude_m <= 11000:  # Troposphere
        T = 288.15 - 0.0065 * altitude_m
        P = 101325 * (T / 288.15) ** (g / (-0.0065 * R))
    elif altitude_m <= 20000:  # Lower Stratosphere
        T = 216.65
        P = 22632.06 * math.exp(-g * (altitude_m - 11000) / (R * T))
    elif altitude_m <= 32000:  # Mid Stratosphere
        T = 216.65 + 0.001 * (altitude_m - 20000)
        P = 5474.89 * (T / 216.65) ** (-g / (0.001 * R))
    else:  # 32–47 km, simplified
        T = 228.65 + 0.0028 * (altitude_m - 32000)
        P = 868.02 * (T / 228.65) ** (-g / (0.0028 * R))

    rho = P / (R * T)
    a = math.sqrt(gamma * R * T)

    return T, P, rho, a


# -------------------------
# Altitude conversion
# -------------------------
def convert_altitude(value: float, from_unit: str, to_unit: str) -> float:
    """Convert altitude between meters, feet, and kilometers."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # normalize to meters
    if from_unit in ["meters", "m"]:
        value_m = value
    elif from_unit in ["feet", "ft"]:
        value_m = value * 0.3048
    elif from_unit in ["kilometers", "km"]:
        value_m = value * 1000.0
    else:
        raise ValueError("Invalid from_unit. Use 'meters', 'feet', or 'kilometers'.")

    # convert to target
    if to_unit in ["meters", "m"]:
        return value_m
    elif to_unit in ["feet", "ft"]:
        return value_m / 0.3048
    elif to_unit in ["kilometers", "km"]:
        return value_m / 1000.0
    else:
        raise ValueError("Invalid to_unit. Use 'meters', 'feet', or 'kilometers'.")
