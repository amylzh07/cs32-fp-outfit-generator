import streamlit as st

# import from other python files
from wardrobe import make_item, SAMPLE_WARDROBE
from outfit import suggest_outfit
 
st.set_page_config(page_title="Wardrobe Chooser", layout="wide")
st.title("wardrobe chooser")
 
# ── session state ──────────────────────────────────────────────────────────────
# persist the wardrobe across reruns within the session
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = SAMPLE_WARDROBE.copy()
 
# ── tabs ───────────────────────────────────────────────────────────────────────
tab_wardrobe, tab_outfit, tab_week = st.tabs(
    ["my wardrobe", "today's outfit", "weekly planner"]
)
 
# ══════════════════════════════════════════════════════════════════════════════
# tab 1 — MY WARDROBE
# ══════════════════════════════════════════════════════════════════════════════
with tab_wardrobe:
    col_sidebar, col_items = st.columns([1, 3])
 
    with col_sidebar:
        st.subheader("filters")
 
        # Filter controls
        type_filter = st.selectbox(
            "type", ["all", "top", "bottom", "layer", "shoes", "accessory"]
        )
        vibe_filter = st.selectbox(
            "vibe", ["any", "professional", "smart_casual", "business_casual", "cocktail"]
        )
        weather_filter = st.selectbox("weather", ["any", "cold", "sunny"])
 
        st.divider()
        st.subheader("add item")
 
        # Form to add a new clothing item
        with st.form("add_item_form", clear_on_submit=True):
            new_name = st.text_input("name (e.g. white_dress_shirt)")
            new_type = st.selectbox(
                "type", ["top", "bottom", "layer", "shoes", "accessory"]
            )
            new_color = st.text_input("color")
            new_vibes = st.multiselect(
                "vibes",
                ["professional", "smart_casual", "business_casual", "cocktail", "casual"],
            )
            new_weather = st.multiselect("weather", ["any", "cold", "sunny"])
 
            submitted = st.form_submit_button("+ add to wardrobe")
            if submitted and new_name:
                item = make_item(
                    name=new_name,
                    item_type=new_type,
                    color=new_color,
                    vibes=new_vibes or ["casual"],
                    weather=new_weather or ["any"],
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
            # Display items in a 3-column grid
            cols = st.columns(3)
            for idx, item in enumerate(items):
                with cols[idx % 3]:
                    if item.get("image_path"):
                        st.image(item["image_path"], use_container_width=True)
                    else:
                        # Placeholder when no image is available
                        st.image(
                            "https://placehold.co/200x200/e8e6f0/9e9ab8?text=no+photo",
                            use_container_width=True,
                        )
                    st.caption(f"**{item['name']}**  \n{item['color']} · {item['type']}")
                    st.caption(" · ".join(item["vibes"]))
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TODAY'S OUTFIT
# ══════════════════════════════════════════════════════════════════════════════
with tab_outfit:
    col_controls, col_result = st.columns([1, 2])
 
    with col_controls:
        st.subheader("parameters")
        occasion = st.selectbox(
            "occasion",
            ["interview", "school", "social", "date", "casual"],
        )
        today_weather = st.selectbox("weather", ["cold", "mild", "sunny"])
 
        if st.button("suggest outfit", use_container_width=True):
            outfit = suggest_outfit(
                wardrobe=st.session_state.wardrobe,
                occasion=occasion,
                weather=today_weather,
            )
            st.session_state.last_outfit = outfit
 
    with col_result:
        st.subheader("suggested outfit")
        outfit = st.session_state.get("last_outfit")
 
        if not outfit:
            st.info("set parameters and click 'suggest outfit'.")
        elif outfit.get("error"):
            st.warning(outfit["error"])
        else:
            # Display each slot: top, bottom, layer, shoes
            for slot in ["top", "bottom", "layer", "shoes"]:
                item = outfit.get(slot)
                if item:
                    img_col, text_col = st.columns([1, 2])
                    with img_col:
                        if item.get("image_path"):
                            st.image(item["image_path"], use_container_width=True)
                        else:
                            st.image(
                                "https://placehold.co/120x120/e8e6f0/9e9ab8?text=" + slot,
                                use_container_width=True,
                            )
                    with text_col:
                        st.markdown(f"**{slot}** — {item['name']}")
                        st.caption(item["color"])
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEEKLY PLANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab_week:
    st.subheader("plan your week")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    occasions_opts = ["none", "interview", "school", "social", "date", "casual"]
    weather_opts = ["mild", "cold", "sunny"]
 
    day_cols = st.columns(5)
    for col, day in zip(day_cols, days):
        with col:
            st.markdown(f"**{day[:3]}**")
            occ = st.selectbox("event", occasions_opts, key=f"occ_{day}", label_visibility="collapsed")
            wthr = st.selectbox("weather", weather_opts, key=f"wthr_{day}", label_visibility="collapsed")
 
    if st.button("generate week", use_container_width=True):
        st.session_state.week_plan = {}
        for day in days:
            occ = st.session_state[f"occ_{day}"]
            wthr = st.session_state[f"wthr_{day}"]
            if occ != "none":
                outfit = suggest_outfit(
                    wardrobe=st.session_state.wardrobe,
                    occasion=occ,
                    weather=wthr,
                )
                st.session_state.week_plan[day] = outfit
 
    week_plan = st.session_state.get("week_plan", {})
    if week_plan:
        st.divider()
        plan_cols = st.columns(5)
        for col, day in zip(plan_cols, days):
            with col:
                outfit = week_plan.get(day)
                if outfit and not outfit.get("error"):
                    top = outfit.get("top")
                    bottom = outfit.get("bottom")
                    st.caption(day[:3])
                    if top:
                        st.caption(f"top: {top['name']}")
                    if bottom:
                        st.caption(f"bottom: {bottom['name']}")
                else:
                    st.caption(f"{day[:3]}: no event")

