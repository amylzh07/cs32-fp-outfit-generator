## app.py — Streamlit interface for the outfit generator

import base64
import streamlit as st

from wardrobe import make_item, SAMPLE_WARDROBE
from outfit import suggest_outfit, suggest_week
from weather import get_week_weather, get_today_weather


st.set_page_config(page_title="Wardrobe Chooser", layout="wide")
st.title("wardrobe chooser")

st.markdown("""
<style>
    /* App background */
    .stApp {
        background-color: #ffffff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ede8f7;
    }

    /* Primary buttons */
    .stButton > button {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #dddddd;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #f5f5f5;
        color: #333333;
    }

    /* Tab labels */
    .stTabs [data-baseweb="tab"] {
        color: #333333;
        font-weight: 600;
    }

    /* Active tab underline */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #333333;
    }

    /* Section headers */
    h2, h3 {
        color: #111111;
    }

    header[data-testid="stHeader"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
# CURRENT
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = SAMPLE_WARDROBE.copy()

# ── helpers ────────────────────────────────────────────────────────────────────
def image_to_data_url(uploaded_file):
    """
    Convert a Streamlit UploadedFile to a base64 data URL so it can be
    stored in the wardrobe dict and displayed with st.image() later.
    """
    data   = uploaded_file.read()
    b64    = base64.b64encode(data).decode()
    mime   = uploaded_file.type  # e.g. "image/jpeg"
    return f"data:{mime};base64,{b64}"


def color_score_label(score):
    """Return an emoji label summarising the outfit's color harmony score."""
    if score >= 4:
        return "🎨 great color harmony"
    elif score >= 0:
        return "👍 colors work"
    else:
        return "⚠️ potential color clash"


def display_outfit(outfit, compact=False):
    """
    Render a single outfit dict to the current Streamlit context.

    Args:
        outfit:  dict returned by suggest_outfit()
        compact: if True, use a tighter 2-row layout (for the weekly planner)
    """
    if outfit.get("error"):
        st.warning(outfit["error"])
        return

    slots = ["top", "bottom", "layer", "shoes"]
    items = [(slot, outfit[slot]) for slot in slots if outfit.get(slot)]

    if compact:
        # In the weekly view, show a small image + name per slot
        for slot, item in items:
            src = item.get("image_path") or f"https://placehold.co/80x80/e8e6f0/9e9ab8?text={slot}"
            st.image(src, use_container_width=True)
            st.caption(f"**{slot}** {item['name']}")
    else:
        # Full layout: one row per slot with image + details
        for slot, item in items:
            img_col, text_col = st.columns([1, 2])
            with img_col:
                src = item.get("image_path") or f"https://placehold.co/120x120/e8e6f0/9e9ab8?text={slot}"
                st.image(src, use_container_width=True)
            with text_col:
                st.markdown(f"**{slot}** — {item['name']}")
                st.caption(f"{item['color']}  ·  {' · '.join(item['vibes'])}")

    # Color harmony score badge
    score = outfit.get("color_score", 0)
    st.caption(color_score_label(score) + f"  (score: {score:+d})")


# ── location sidebar (used by weather API) ─────────────────────────────────────
with st.sidebar:
    st.subheader("📍 your location")
    st.caption("Used to fetch real weather forecasts via Open-Meteo.")
    latitude  = st.number_input("latitude",  value=42.3744, format="%.4f")
    longitude = st.number_input("longitude", value=-71.1169, format="%.4f")


# ── tabs ───────────────────────────────────────────────────────────────────────
tab_wardrobe, tab_outfit, tab_week = st.tabs(
    ["my wardrobe", "today's outfit", "weekly planner"]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MY WARDROBE
# ══════════════════════════════════════════════════════════════════════════════
with tab_wardrobe:
    col_sidebar, col_items = st.columns([1, 3])

    with col_sidebar:
        st.subheader("filters")
        type_filter    = st.selectbox("type", ["all", "top", "bottom", "layer", "shoes", "accessory"])
        vibe_filter    = st.selectbox("vibe", ["any", "professional", "smart_casual", "business_casual", "cocktail", "casual"])
        weather_filter = st.selectbox("weather", ["any", "cold", "mild", "sunny"])

        st.divider()
        st.subheader("add item")

        with st.form("add_item_form", clear_on_submit=True):
            new_name    = st.text_input("name (e.g. white_dress_shirt)")
            new_type    = st.selectbox("type", ["top", "bottom", "layer", "shoes", "accessory"])
            new_color   = st.text_input("color")
            new_vibes   = st.multiselect(
                "vibes",
                ["professional", "smart_casual", "business_casual", "cocktail", "casual"],
            )
            new_weather = st.multiselect("weather", ["any", "cold", "mild", "sunny"])

            # Image upload — optional, stored as a base64 data URL in the item dict
            uploaded_img = st.file_uploader(
                "photo (optional)",
                type=["jpg", "jpeg", "png", "webp"],
                help="Upload a photo of this item. It will appear in outfit suggestions.",
            )

            submitted = st.form_submit_button("+ add to wardrobe")
            if submitted and new_name:
                img_path = image_to_data_url(uploaded_img) if uploaded_img else None

                item = make_item(
                    name=new_name,
                    item_type=new_type,
                    color=new_color,
                    vibes=new_vibes or ["casual"],
                    weather=new_weather or ["any"],
                    image_path=img_path,
                )

                st.session_state.wardrobe[new_name] = item
                st.success(f"added {new_name}!")

    with col_items:
        items = list(st.session_state.wardrobe.values())

        # Apply filters
        if type_filter != "all":
            items = [i for i in items if i["type"] == type_filter]
        if vibe_filter != "any":
            items = [i for i in items if vibe_filter in i["vibes"]]
        if weather_filter != "any":
            items = [i for i in items if weather_filter in i["weather"] or "any" in i["weather"]]

        if not items:
            st.info("no items match these filters.")
        else:
            cols = st.columns(3)
            for idx, item in enumerate(items):
                with cols[idx % 3]:
                    src = item.get("image_path") or "https://placehold.co/200x200/e8e6f0/9e9ab8?text=no+photo"
                    st.image(src, use_container_width=True)
                    st.caption(f"**{item['name']}**  \n{item['color']} · {item['type']}")
                    st.caption(" · ".join(item["vibes"]))


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TODAY'S OUTFIT
# ══════════════════════════════════════════════════════════════════════════════
with tab_outfit:
    col_controls, col_result = st.columns([1, 2])

    with col_controls:
        st.subheader("parameters")
        occasion = st.selectbox("occasion", ["interview", "school", "social", "date", "casual"])

        # Auto-detect today's weather; allow manual override
        auto_weather    = get_today_weather(latitude, longitude)
        weather_options = ["cold", "mild", "sunny"]
        default_idx     = weather_options.index(auto_weather) if auto_weather in weather_options else 1

        today_weather = st.selectbox(
            "weather",
            weather_options,
            index=default_idx,
            help=f"Auto-detected: {auto_weather}. You can override this.",
        )

        if st.button("suggest outfit", use_container_width=True):
            st.session_state.last_outfit = suggest_outfit(
                wardrobe=st.session_state.wardrobe,
                occasion=occasion,
                weather=today_weather,
            )

        # Reshuffle button — re-runs suggestion without touching the weekly plan
        if st.session_state.get("last_outfit") and not st.session_state.last_outfit.get("error"):
            if st.button("🔀 reshuffle", use_container_width=True):
                st.session_state.last_outfit = suggest_outfit(
                    wardrobe=st.session_state.wardrobe,
                    occasion=occasion,
                    weather=today_weather,
                )

    with col_result:
        st.subheader("suggested outfit")
        outfit = st.session_state.get("last_outfit")

        if not outfit:
            st.info("set parameters and click 'suggest outfit'.")
        else:
            display_outfit(outfit)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEEKLY PLANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab_week:
    st.subheader("plan your week")

    days          = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    occasion_opts = ["none", "interview", "school", "social", "date", "casual"]
    weather_opts  = ["mild", "cold", "sunny"]

    # Fetch the real week forecast once; use as default per-day value
    with st.spinner("fetching weather forecast…"):
        real_forecast = get_week_weather(latitude, longitude)

    if "error" in real_forecast:
        st.warning(f"Could not fetch live weather ({real_forecast['error']}). Defaulting to mild.")

    day_cols = st.columns(5)
    for col, day in zip(day_cols, days):
        with col:
            st.markdown(f"**{day[:3]}**")
            real_tag   = real_forecast.get(day.capitalize(), "mild")
            default_wi = weather_opts.index(real_tag) if real_tag in weather_opts else 0
            st.selectbox("event",   occasion_opts, key=f"occ_{day}",  label_visibility="collapsed")
            st.selectbox("weather", weather_opts,  key=f"wthr_{day}", label_visibility="collapsed", index=default_wi)

    if st.button("generate week", use_container_width=True):
        schedule         = {day.capitalize(): st.session_state[f"occ_{day}"]  for day in days if st.session_state[f"occ_{day}"] != "none"}
        weather_forecast = {day.capitalize(): st.session_state[f"wthr_{day}"] for day in days}
        st.session_state.week_plan = suggest_week(
            wardrobe=st.session_state.wardrobe,
            schedule=schedule,
            weather_forecast=weather_forecast,
        )

    week_plan = st.session_state.get("week_plan", {})
    if week_plan:
        st.divider()
        plan_cols = st.columns(5)
        for col, day in zip(plan_cols, days):
            with col:
                outfit = week_plan.get(day)
                if not outfit:
                    st.caption(f"**{day[:3]}** — no event")
                    continue

                st.markdown(f"**{day[:3]}**")
                display_outfit(outfit, compact=True)