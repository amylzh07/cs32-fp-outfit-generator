## wardrobe.py

# Each item is a dictionary with keys:
# name: (str) specific name "white_dress_shirt"
# type: (str) category "top", "bottom", "layer", "shoes", "accessory"
# color: (str) color "red", "blue", "gold"
# vibes: (list) category "professional", "smart_casual", "business_casual", "cocktail"
# weather: (list) category "cold", "sunny", "any"
# image_path: (str) path to item's image file

def make_item(name, item_type, color, vibes, weather, image_path=None):
    """Helper to create a clothing item dict with validated structure."""
    return {
        "name": name,
        "type": item_type,
        "color": color,
        "vibes": vibes if isinstance(vibes, list) else [vibes],
        "weather": weather if isinstance(weather, list) else [weather],
        "image_path": image_path,
    }


# sample wardrobe so the app isn't empty on first run
SAMPLE_WARDROBE = {
    "white_dress_shirt": make_item(
        "white_dress_shirt", "top", "white",
        ["professional", "business_casual", "cocktail"], ["any"]
    ),
    "black_jeans": make_item(
        "black_jeans", "bottom", "black",
        ["smart_casual", "casual"], ["any"]
    ),
    "navy_chinos": make_item(
        "navy_chinos", "bottom", "navy",
        ["professional", "business_casual", "smart_casual"], ["any"]
    ),
    "black_blazer": make_item(
        "black_blazer", "layer", "black",
        ["professional", "business_casual", "cocktail"], ["cold"]
    ),
    "grey_tee": make_item(
        "grey_tee", "top", "grey",
        ["casual", "smart_casual"], ["any"]
    ),
    "white_sneakers": make_item(
        "white_sneakers", "shoes", "white",
        ["casual", "smart_casual"], ["any"]
    ),
    "black_oxfords": make_item(
        "black_oxfords", "shoes", "black",
        ["professional", "business_casual", "cocktail"], ["any"]
    ),
}