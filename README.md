# cs32-fp-outfit-generator

Given a list of clothing items stored as dictionaries with attributes such as clothing type, vibe, and weather-appropriateness, as well as a dataset of weather for the week, our project is an algorithm that generates a weekly outfit plan for the user. The user inputs their desired vibes for the week, scheduled events (i.e. interview, school, work, social) and our project will output a list of outfit combinations and potentially folders containing an image of the clothing pieces in each week's outfits.

**Inputs:**
- Your wardrobe — added through the UI with optional photo upload, or pre-loaded from `wardrobe.py`
- A weekly schedule — assign an occasion (interview, school, social, date, casual) to each day
- Weather — fetched automatically from Open-Meteo, or set manually per day

**Outputs:**
- A suggested outfit (top, bottom, optional layer, shoes) per scheduled day
- Outfits are scored by vibe match + color harmony and randomized among top candidates
- Cross-day repeat avoidance: the same item won't appear twice in one week
- A color harmony score badge on every outfit

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI — wardrobe browser, single-day suggester, weekly planner |
| `outfit.py` | Recommendation logic — filtering, combined vibe+color scoring, randomization |
| `color_utils.py` | Color compatibility rules — neutral detection, family grouping, pairwise scores |
| `wardrobe.py` | Wardrobe data model — `make_item()` constructor and sample wardrobe |
| `weather.py` | Weather API integration — fetches forecasts from Open-Meteo |
| `main.py` | Demo runner — prints a sample weekly plan to the terminal |

## Running the app

**Requirements:** Python 3.8+, an internet connection (for weather), and a local IDE or terminal (not compatible with CS50 Codespace due to Streamlit's server requirements).

1. Install Streamlit:
   ```
   pip install streamlit
   ```

2. Run the app:
   ```
   streamlit run app.py
   ```
   This opens the app in a new browser tab at `http://localhost:8501`.

3. (Optional) Run the terminal demo:
   ```
   python main.py
   ```

**No API key is required.** Weather data is fetched from [Open-Meteo](https://open-meteo.com/), a free open-source weather API.

## Key features

### Color compatibility scoring (`color_utils.py`)
Each clothing item has a color. When assembling an outfit, every new item is scored against items already chosen using pairwise compatibility rules:
- **Neutrals** (black, white, grey, navy, beige…) pair with anything → `+2`
- **Same color family** (e.g. two shades of blue) → `+2`
- **Known compatible cross-family pairs** (e.g. blue + brown, red + white) → `+2`
- **Known clashing pairs** (unrecognized cross-family combinations) → `−3`

The outfit's total color score is displayed as a badge ("🎨 great color harmony", "👍 colors work", "⚠️ potential color clash").

### Image upload
When adding a clothing item in the "my wardrobe" tab, you can optionally upload a photo (JPG, PNG, or WebP). The image is stored as a base64 data URL inside the item dict and displayed throughout the app — in the wardrobe browser, outfit suggestions, and the weekly planner grid.

### Weather integration
The app uses the [Open-Meteo Forecast API](https://open-meteo.com/en/docs) to fetch 7 days of daily forecasts for a lat/long you set in the sidebar. Each day is mapped to `cold`, `mild`, or `sunny` based on WMO weather codes and maximum temperature. Weather defaults in the planner are pre-populated from the forecast; you can override any day manually.

Default location: Cambridge, MA (42.3744, −71.1169).

## External sources and AI attribution

**External libraries:**
- [Streamlit](https://streamlit.io/) — UI framework
- [Open-Meteo](https://open-meteo.com/) — weather forecast API (no key required)

**Generative AI:**
Claude (Anthropic) was used to assist with the following:
- Designing and writing `weather.py` in full, including WMO code → weather tag mapping
- Designing and writing `color_utils.py` in full, including the color family taxonomy, `COMPATIBLE_PAIRS` table, and `color_compatibility_score` / `outfit_color_score` functions
- Rewriting `outfit.py` to integrate color scoring into `_pick_item`, add `suggest_week`, and replace first-match selection with scored + randomized picking
- Updating `app.py` to add `st.file_uploader` image support, the `display_outfit` helper, color score badges, the reshuffle button, and weekly plan image display
- Refactoring `main.py` to use `make_item()` consistently

All other code — the Streamlit UI layout, wardrobe data model, `make_item()`, the original filtering logic in `suggest_outfit`, and the initial app structure — was written by the project authors.