## outfit.py — outfit recommendation logic
 
# maps occasion names to the vibes that fit them
OCCASION_TO_VIBES = {
    "interview":  ["professional"],
    "school":     ["smart_casual", "casual"],
    "social":     ["smart_casual", "casual", "cocktail"],
    "date":       ["cocktail", "smart_casual"],
    "casual":     ["casual"],
}
 
 
def suggest_outfit(wardrobe, occasion, weather):
    """
    Pick one item per slot (top, bottom, layer, shoes) from the wardrobe
    that matches the occasion's vibes and the given weather.
 
    Returns a dict with keys: top, bottom, layer, shoes, error.
    """
    vibes = OCCASION_TO_VIBES.get(occasion, ["casual"])
    outfit = {}
 
    for slot in ["top", "bottom", "layer", "shoes"]:
        candidates = [
            item for item in wardrobe.values()
            if item["type"] == slot
            # item must share at least one vibe with the occasion
            and any(v in item["vibes"] for v in vibes)
            # item weather must be "any" or match the current weather
            and ("any" in item["weather"] or weather in item["weather"])
        ]
 
        # Layer is optional — skip if nothing matches rather than erroring
        if candidates:
            outfit[slot] = candidates[0]   # TODO: randomize or score for variety
        elif slot != "layer":
            outfit["error"] = f"no {slot} found for '{occasion}' in {weather} weather"
            return outfit
 
    return outfit