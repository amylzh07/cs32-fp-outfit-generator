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
