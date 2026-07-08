import streamlit as st
from utils.data import load_data
from components.ui import apply_css, render_sidebar

# ─────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Dominican Film Industry Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# LOAD DATA & APPLY STYLES
# ─────────────────────────────────────────
df = load_data()
apply_css()

# ─────────────────────────────────────────
# SIDEBAR & NAVIGATION
# ─────────────────────────────────────────
page = render_sidebar(df)

# ─────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────
if page == "Overview":
    from views.overview import render
    render(df)

elif page == "Genres":
    from views.genres import render
    render(df)

elif page == "Industry Players":
    from views.industry_players import render
    render(df)

elif page == "Co-productions":
    from views.coproductions import render
    render(df)

elif page == "Budget":
    from views.budget import render
    render(df)

elif page == "Film Catalog":
    from views.film_catalog import render
    render(df)