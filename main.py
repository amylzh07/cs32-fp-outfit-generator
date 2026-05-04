## main.py — wardrobe data and weekly schedule/weather examples
#
# This file serves as the central data store and demo runner.
# All clothing items use make_item() to ensure consistent structure.

from wardrobe import make_item, SAMPLE_WARDROBE
from outfit import suggest_outfit


# ── sample wardrobe ────────────────────────────────────────────────────────────
# Starts from the shared SAMPLE_WARDROBE defined in wardrobe.py.
# Add extra items here using make_item() — never raw dicts.

wardrobe = SAMPLE_WARDROBE.copy()

wardrobe["blue_jeans"] = make_item(
    "blue_jeans", "bottom", "blue",
    ["casual", "smart_casual"], ["any"]
)
wardrobe["black_turtleneck"] = make_item(
    "black_turtleneck", "top", "black",
    ["professional", "business_casual", "smart_casual"], ["cold"]
)


# ── sample weekly schedule & weather ──────────────────────────────────────────
# These mirror what the Streamlit UI collects from the user.
# Weather values must be: "cold", "mild", or "sunny"

schedule = {
    "Monday":    "interview",
    "Tuesday":   "school",
    "Wednesday": "social",
    "Thursday":  "casual",
    "Friday":    "date",
}

weather = {
    "Monday":    "cold",
    "Tuesday":   "mild",
    "Wednesday": "sunny",
    "Thursday":  "mild",
    "Friday":    "cold",
}


# ── demo: generate a week of outfits ──────────────────────────────────────────
if __name__ == "__main__":
    print("=== weekly outfit plan ===\n")
    for day, occasion in schedule.items():
        day_weather = weather[day]
        outfit = suggest_outfit(wardrobe, occasion, day_weather)

        if outfit.get("error"):
            print(f"{day}: ERROR — {outfit['error']}")
        else:
            top    = outfit.get("top",    {}).get("name", "—")
            bottom = outfit.get("bottom", {}).get("name", "—")
            layer  = outfit.get("layer",  {}).get("name", "none")
            shoes  = outfit.get("shoes",  {}).get("name", "—")
            print(f"{day} [{occasion}, {day_weather}]")
            print(f"  top: {top}  |  bottom: {bottom}  |  layer: {layer}  |  shoes: {shoes}\n")