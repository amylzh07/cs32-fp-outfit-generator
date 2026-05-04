## outfit.py — outfit recommendation logic

import random

from color_utils import color_compatibility_score, outfit_color_score


# Maps occasion names to the vibes that suit them.
# Used to filter wardrobe items before scoring.
OCCASION_TO_VIBES = {
    "interview":  ["professional"],
    "school":     ["smart_casual", "casual"],
    "social":     ["smart_casual", "casual", "cocktail"],
    "date":       ["cocktail", "smart_casual"],
    "casual":     ["casual"],
}


def _vibe_score(item, vibes):
    """
    Score a single item by how many of the target vibes it matches.
    More overlap = higher score = better fit for the occasion.
    """
    return sum(1 for v in vibes if v in item["vibes"])


def _pick_item(candidates, vibes, used_names, chosen_so_far):
    """
    Choose one item from candidates using a combined vibe + color score,
    preferring items not already worn this week.

    Scoring:
      - Vibe match:  +1 per matching vibe (measures occasion fit)
      - Color bonus: pairwise compatibility score against each already-chosen item
                     (rewards color harmony, penalizes clashes)

    Args:
        candidates:     list of items passing weather/type filtering
        vibes:          target vibes for the occasion
        used_names:     set of item names already picked earlier in the week
        chosen_so_far:  dict of slot → item already selected for this outfit
                        (used to compute color compatibility against partial outfit)

    Returns:
        A single item dict, or None if candidates is empty.
    """
    if not candidates:
        return None

    def score(item):
        s = _vibe_score(item, vibes)
        # Add color compatibility score against each already-chosen piece
        for picked in chosen_so_far.values():
            s += color_compatibility_score(item["color"], picked["color"])
        return s

    scored = sorted(candidates, key=score, reverse=True)

    # Prefer items not yet worn this week to avoid repetition
    fresh = [item for item in scored if item["name"] not in used_names]
    pool  = fresh if fresh else scored  # fall back if wardrobe is small

    # Pick randomly among the top-3 scorers for variety
    top_n = pool[: min(3, len(pool))]
    return random.choice(top_n)


def suggest_outfit(wardrobe, occasion, weather, used_names=None):
    """
    Build one outfit (top, bottom, optional layer, shoes) from the wardrobe
    that matches the occasion's vibes, the day's weather, and color harmony.

    Slots are filled in order: top → bottom → layer → shoes. Each new item
    is scored against items already chosen, so color compatibility compounds
    as the outfit is assembled.

    Args:
        wardrobe:    dict of {name: item} — the user's full wardrobe
        occasion:    str — one of the keys in OCCASION_TO_VIBES
        weather:     str — "cold", "mild", or "sunny"
        used_names:  set of item names already used earlier in the week
                     (pass this in from the weekly planner to avoid repeats)

    Returns:
        dict with keys: top, bottom, layer (optional), shoes,
                        color_score (int), error (str, only on failure)
    """
    if used_names is None:
        used_names = set()

    vibes         = OCCASION_TO_VIBES.get(occasion, ["casual"])
    outfit        = {}
    chosen_so_far = {}  # tracks items selected so far for color scoring

    for slot in ["top", "bottom", "layer", "shoes"]:
        # Filter: correct type + at least one matching vibe + weather-appropriate
        candidates = [
            item for item in wardrobe.values()
            if item["type"] == slot
            and any(v in item["vibes"] for v in vibes)
            and ("any" in item["weather"] or weather in item["weather"])
        ]

        chosen = _pick_item(candidates, vibes, used_names, chosen_so_far)

        if chosen:
            outfit[slot]        = chosen
            chosen_so_far[slot] = chosen
            used_names.add(chosen["name"])  # mark used to prevent weekly repeats
        elif slot != "layer":
            # Layer is optional — all other slots are required
            outfit["error"] = f"no {slot} found for '{occasion}' in {weather} weather"
            return outfit

    # Attach a human-readable color harmony score to the finished outfit
    outfit["color_score"] = outfit_color_score(outfit)
    return outfit


def suggest_week(wardrobe, schedule, weather_forecast):
    """
    Generate a full week of non-repeating, color-harmonious outfits.

    Args:
        wardrobe:         dict of {name: item}
        schedule:         dict of {day: occasion}   e.g. {"Monday": "interview"}
        weather_forecast: dict of {day: weather}    e.g. {"Monday": "cold"}

    Returns:
        dict of {day: outfit_dict}
    """
    used_names = set()  # shared across the week to prevent item repetition
    week_plan  = {}

    for day, occasion in schedule.items():
        day_weather    = weather_forecast.get(day, "mild")
        week_plan[day] = suggest_outfit(wardrobe, occasion, day_weather, used_names)

    return week_plan