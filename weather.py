## weather.py — fetch real weather forecasts via Open-Meteo (no API key required)
#
# Open-Meteo docs: https://open-meteo.com/en/docs
# Returns free daily forecasts using WMO weather interpretation codes.

import datetime
import urllib.request
import json


# WMO weather code → internal weather tag used by outfit.py
# Full code list: https://open-meteo.com/en/docs#weathervariables
_WMO_TO_TAG = {
    0:  "sunny",   # clear sky
    1:  "sunny",   # mainly clear
    2:  "mild",    # partly cloudy
    3:  "mild",    # overcast
    45: "mild",    # fog
    48: "mild",    # icy fog
    51: "mild",    # light drizzle
    53: "mild",    # moderate drizzle
    55: "mild",    # dense drizzle
    61: "mild",    # slight rain
    63: "mild",    # moderate rain
    65: "cold",    # heavy rain
    71: "cold",    # slight snow
    73: "cold",    # moderate snow
    75: "cold",    # heavy snow
    77: "cold",    # snow grains
    80: "mild",    # slight showers
    81: "mild",    # moderate showers
    82: "cold",    # violent showers
    85: "cold",    # slight snow showers
    86: "cold",    # heavy snow showers
    95: "mild",    # thunderstorm
    96: "cold",    # thunderstorm with hail
    99: "cold",    # thunderstorm with heavy hail
}

# Temperature thresholds (°C) used to override weather tag if it's cold
_COLD_THRESHOLD_C = 10
_WARM_THRESHOLD_C = 22


def _temp_tag(temp_c):
    """Map a temperature in Celsius to a weather tag."""
    if temp_c < _COLD_THRESHOLD_C:
        return "cold"
    elif temp_c > _WARM_THRESHOLD_C:
        return "sunny"
    else:
        return "mild"


def get_week_weather(latitude, longitude):
    """
    Fetch the next 7 days of weather for a given location and return
    a dict mapping day-of-week names to weather tags ("cold"/"mild"/"sunny").

    Uses both WMO weather codes and daily max temperature to determine the tag —
    temperature takes priority because a clear cold day should still be "cold".

    Args:
        latitude:  float — e.g. 42.3744 for Cambridge, MA
        longitude: float — e.g. -71.1169

    Returns:
        dict like {"Monday": "cold", "Tuesday": "mild", ...}
        or {"error": "..."} if the request fails
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&daily=weathercode,temperature_2m_max"
        f"&temperature_unit=celsius"
        f"&forecast_days=7"
        f"&timezone=auto"
    )

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"weather fetch failed: {e}"}

    dates    = data["daily"]["time"]            # list of "YYYY-MM-DD" strings
    codes    = data["daily"]["weathercode"]     # WMO codes
    max_temps = data["daily"]["temperature_2m_max"]

    forecast = {}
    for date_str, code, temp in zip(dates, codes, max_temps):
        day_name = datetime.date.fromisoformat(date_str).strftime("%A")  # e.g. "Monday"

        # Combine WMO code and temperature — temperature wins on cold days
        code_tag = _WMO_TO_TAG.get(code, "mild")
        temp_tag = _temp_tag(temp)

        # If temperature says cold, always use cold; otherwise trust the code
        tag = "cold" if temp_tag == "cold" else code_tag
        forecast[day_name] = tag

    return forecast


def get_today_weather(latitude, longitude):
    """
    Convenience wrapper — returns just today's weather tag as a string,
    or "mild" if the fetch fails.
    """
    forecast = get_week_weather(latitude, longitude)
    if "error" in forecast:
        return "mild"
    today = datetime.date.today().strftime("%A")
    return forecast.get(today, "mild")
