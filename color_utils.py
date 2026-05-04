## color_utils.py — color compatibility rules for outfit scoring
#
# Colors are grouped into families. Compatibility is determined by three rules
# applied in order:
#   1. Neutrals (black, white, grey, navy, beige, tan, cream) go with everything.
#   2. Monochromatic pairs (same family) are always compatible.
#   3. A curated COMPATIBLE_PAIRS set defines cross-family pairings that work well.
#
# Any pair not covered by these rules is considered a clash and penalizes the score.


# Colors that pair with absolutely anything
NEUTRALS = {"black", "white", "grey", "gray", "navy", "beige", "tan", "cream", "charcoal", "brown"}

# Color families — used for monochromatic matching
COLOR_FAMILIES = {
    "red":    {"red", "crimson", "burgundy", "maroon", "wine", "coral"},
    "blue":   {"blue", "sky_blue", "cobalt", "royal_blue", "powder_blue", "denim"},
    "green":  {"green", "olive", "forest_green", "sage", "mint", "emerald", "khaki"},
    "yellow": {"yellow", "gold", "mustard", "lemon"},
    "purple": {"purple", "lavender", "violet", "plum", "lilac"},
    "pink":   {"pink", "blush", "rose", "hot_pink", "mauve"},
    "orange": {"orange", "rust", "terracotta", "peach"},
    "white":  {"white", "cream", "ivory", "off_white"},
    "grey":   {"grey", "gray", "charcoal", "silver"},
    "brown":  {"brown", "tan", "beige", "camel", "chocolate"},
}

# Curated cross-family pairs that work well together.
# Each entry is a frozenset of two color family names — order doesn't matter.
COMPATIBLE_PAIRS = {
    frozenset({"blue",   "grey"}),
    frozenset({"blue",   "white"}),
    frozenset({"blue",   "brown"}),
    frozenset({"blue",   "yellow"}),
    frozenset({"red",    "grey"}),
    frozenset({"red",    "white"}),
    frozenset({"red",    "blue"}),
    frozenset({"green",  "brown"}),
    frozenset({"green",  "white"}),
    frozenset({"green",  "grey"}),
    frozenset({"purple", "grey"}),
    frozenset({"purple", "white"}),
    frozenset({"purple", "pink"}),
    frozenset({"yellow", "grey"}),
    frozenset({"yellow", "white"}),
    frozenset({"orange", "blue"}),
    frozenset({"orange", "white"}),
    frozenset({"orange", "brown"}),
    frozenset({"pink",   "grey"}),
    frozenset({"pink",   "white"}),
    frozenset({"pink",   "blue"}),
}

# Bonus score awarded for a compatible color pair
COLOR_BONUS = 2

# Penalty applied for a clashing color pair
COLOR_CLASH_PENALTY = 3


def _get_family(color):
    """
    Return the color family name for a given color string, or None if unknown.
    Normalizes to lowercase and strips whitespace before lookup.
    """
    color = color.lower().strip().replace(" ", "_")
    for family, members in COLOR_FAMILIES.items():
        if color in members:
            return family
    return None


def is_neutral(color):
    """Return True if the color is a neutral that pairs with anything."""
    return color.lower().strip() in NEUTRALS


def color_compatibility_score(color_a, color_b):
    """
    Return a numeric compatibility score for two colors:
      +2  if they are a known good pairing (or either is neutral / same family)
       0  if the relationship is unknown
      -3  if they are a known clash

    Args:
        color_a: str — e.g. "navy"
        color_b: str — e.g. "white"

    Returns:
        int — COLOR_BONUS, 0, or -COLOR_CLASH_PENALTY
    """
    a = color_a.lower().strip()
    b = color_b.lower().strip()

    # Neutrals pair with everything
    if is_neutral(a) or is_neutral(b):
        return COLOR_BONUS

    fam_a = _get_family(a)
    fam_b = _get_family(b)

    # Same color family = monochromatic — always works
    if fam_a and fam_b and fam_a == fam_b:
        return COLOR_BONUS

    # Check the curated compatible pairs table
    if fam_a and fam_b:
        pair = frozenset({fam_a, fam_b})
        if pair in COMPATIBLE_PAIRS:
            return COLOR_BONUS
        else:
            # Known families but not in the compatible list — penalize
            return -COLOR_CLASH_PENALTY

    # At least one color is unrecognized — no penalty, no bonus
    return 0


def outfit_color_score(outfit):
    """
    Score the overall color harmony of a completed outfit dict.

    Compares every pair of filled slots (top, bottom, layer, shoes) and
    sums their pairwise compatibility scores. A higher score means better
    color coordination.

    Args:
        outfit: dict with optional keys "top", "bottom", "layer", "shoes",
                each being a clothing item dict with a "color" key.

    Returns:
        int — total color harmony score (can be negative for clashing outfits)
    """
    # Collect colors only from slots that were actually filled
    filled_slots = [
        outfit[slot]["color"]
        for slot in ("top", "bottom", "layer", "shoes")
        if outfit.get(slot)
    ]

    total = 0
    # Compare every unique pair of colors in the outfit
    for i in range(len(filled_slots)):
        for j in range(i + 1, len(filled_slots)):
            total += color_compatibility_score(filled_slots[i], filled_slots[j])

    return total
