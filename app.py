import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import numpy as np

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
# DESIGN TOKENS
# ─────────────────────────────────────────
bg          = '#FFFFFF'
sidebar_bg  = '#F8F9FA'
card_bg     = '#FFFFFF'
text        = '#1A1A2E'
subtext     = '#6B7280'
border      = '#E5E7EB'
accent      = '#002D62'
accent2     = '#CE1126'

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown(f"""
    <style>
        /* ── Global ── */
        .stApp {{
            background-color: {bg};
            color: {text};
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border};
        }}
        [data-testid="stSidebar"] * {{
            color: {text} !important;
        }}

        /* ── Radio buttons (navigation) ── */
        [data-testid="stSidebar"] .stRadio label {{
            color: {text} !important;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 12px;
            border-radius: 8px;
            display: block;
            cursor: pointer;
            transition: all 0.2s;
        }}
        [data-testid="stSidebar"] .stRadio label:hover {{
            background-color: {border};
            color: {accent} !important;
        }}

        /* ── KPI Cards ── */
        .kpi-card {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        .kpi-label {{
            font-size: 11px;
            font-weight: 600;
            color: {subtext};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 10px;
        }}
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            color: {accent};
            margin-bottom: 6px;
            line-height: 1;
        }}
        .kpi-subtitle {{
            font-size: 12px;
            color: {subtext};
        }}
        .kpi-accent {{
            display: inline-block;
            width: 4px;
            height: 32px;
            background-color: {accent2};
            border-radius: 2px;
            margin-right: 12px;
            vertical-align: middle;
        }}

        /* ── Section titles ── */
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: {text};
            margin: 32px 0 16px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid {accent};
        }}

        /* ── Chart containers ── */
        .chart-container {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin: 8px 0;
        }}

        /* ── Page title ── */
        .page-title {{
            font-size: 28px;
            font-weight: 800;
            color: {text};
            margin-bottom: 4px;
        }}
        .page-subtitle {{
            font-size: 14px;
            color: {subtext};
            margin-bottom: 24px;
        }}

        /* ── Divider ── */
        .divider {{
            border: none;
            border-top: 1px solid {border};
            margin: 16px 0;
        }}

        /* ── Hide streamlit branding ── */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* ── Sidebar text ── */
        .sidebar-logo {{
            font-size: 16px;
            font-weight: 700;
            color: {accent} !important;
            margin-bottom: 4px;
        }}
        .sidebar-meta {{
            font-size: 11px;
            color: {subtext} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('data/01_movies.csv', sep=';', encoding='utf-8-sig')
    df['film_type'] = df['genre'].apply(
        lambda x: 'Documentary' if isinstance(x, str)
        and 'documentary' in x.lower() else 'Non-Documentary'
    )
    return df

df = load_data()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <div class='sidebar-logo'>Dominican Film Industry</div>
        <div class='sidebar-meta'>Executive Dashboard · 2018–2025</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown(f"""
        <div style='font-size:11px;font-weight:600;color:{subtext};
        text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>
        Navigation</div>
    """, unsafe_allow_html=True)

    # Navigation state
    if 'page' not in st.session_state:
        st.session_state.page = 'Overview'

    pages = [
        "Overview",
        "Genres",
        "Industry Players",
        "Co-productions",
        "Budget",
        "Film Catalog"
    ]

    for p in pages:
        is_active = st.session_state.page == p
        btn_style = f"""
            background-color: {'#002D62' if is_active else 'transparent'};
            color: {'#FFFFFF' if is_active else '#1A1A2E'};
            border: 1px solid {'#002D62' if is_active else '#E5E7EB'};
            border-radius: 8px;
            padding: 8px 12px;
            width: 100%;
            text-align: left;
            font-size: 14px;
            font-weight: {'600' if is_active else '400'};
            margin-bottom: 4px;
            cursor: pointer;
        """
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
            st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='sidebar-meta'>
            Total films: {len(df):,}<br>
            Period: 2018 — 2025<br>
            Last updated: 2025
        </div>
    """, unsafe_allow_html=True)

# ── Page routing ──
page = st.session_state.page

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def kpi_card(label, value, subtitle=""):
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div style='display:flex;align-items:center;'>
                <span class='kpi-accent'></span>
                <span class='kpi-value'>{value}</span>
            </div>
            <div class='kpi-subtitle'>{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def section_title(title):
    st.markdown(f"<div class='section-title'>{title}</div>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────
if page == "Overview":
    st.markdown("<div class='page-title'>Dominican Film Industry Dashboard</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Executive overview of Dominican Republic film production (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── KPI Cards ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Films", f"{len(df):,}", "Registered productions")
    with col2:
        kpi_card("Total Directors", f"{df['director'].nunique():,}", "Unique directors")
    with col3:
        kpi_card("Peak Year", "2022", "68 films produced")
    with col4:
        avg_budget = df['approx_budget'].mean()
        kpi_card("Avg Budget", f"RD${avg_budget/1e6:.1f}M", "Per production")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Prepare data ──
    films_by_year = df['production_year'].value_counts().sort_index()
    years = [str(y) for y in films_by_year.index.tolist()]
    values = films_by_year.values.tolist()
    peak_year = int(films_by_year.idxmax())
    peak_value = int(films_by_year.max())

    status_counts = df['status'].value_counts()
    status_data = [
        {"value": int(v), "name": str(k).replace("_", " ").title()}
        for k, v in status_counts.items()
    ]
    top_status = status_counts.index[0].replace("_", " ").title()
    top_value = int(status_counts.values[0])
    pct = round(top_value / len(df) * 100, 1)

    # ── Charts Row ──
    col_left, col_right = st.columns([2, 1])

    with col_left:
        section_title("Films by Year")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Annual volume of Dominican film productions registered
                between 2018 and 2025. Hover over each bar for details.
            </div>
        """, unsafe_allow_html=True)

        option_bar = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": years,
                "axisLine": {"lineStyle": {"color": "#E5E7EB"}},
                "axisLabel": {"color": "#6B7280", "fontSize": 12}
            },
            "yAxis": {
                "type": "value",
                "axisLine": {"lineStyle": {"color": "#E5E7EB"}},
                "axisLabel": {"color": "#6B7280", "fontSize": 12},
                "splitLine": {"lineStyle": {"color": "#F3F4F6"}}
            },
            "series": [{
                "type": "bar",
                "data": values,
                "barMaxWidth": 50,
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "#002D62"},
                            {"offset": 1, "color": "#1565C0"}
                        ]
                    },
                    "borderRadius": [6, 6, 0, 0]
                },
                "emphasis": {
                    "itemStyle": {"color": "#CE1126"}
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#6B7280",
                    "fontSize": 11
                }
            }]
        }
        st_echarts(options=option_bar, height="400px")

    with col_right:
        section_title("Status Distribution")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Current distribution of production statuses across
                all registered Dominican films.
            </div>
        """, unsafe_allow_html=True)

        option_pie = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)",
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "textStyle": {"color": "#6B7280", "fontSize": 11}
            },
            "color": [
                "#002D62", "#CE1126", "#1565C0",
                "#E53935", "#42A5F5", "#90CAF9"
            ],
            "series": [{
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["60%", "50%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 6,
                    "borderColor": "#FFFFFF",
                    "borderWidth": 2
                },
                "label": {"show": False},
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 13,
                        "fontWeight": "bold"
                    }
                },
                "data": status_data
            }]
        }
        st_echarts(options=option_pie, height="400px")

    # ── Key Insights Row — fuera de las columnas ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='display:grid;grid-template-columns:2fr 1fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                {peak_year} was the most productive year with
                <strong>{peak_value} films</strong>,
                reflecting a post-pandemic surge in Dominican film production.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{top_status}</strong> is the most common status,
                representing <strong>{pct}%</strong> of all registered productions.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Genres":
    st.markdown("<div class='page-title'>Genre Analysis</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Distribution of film genres in Dominican cinema (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Prepare data ──
    genres = df['genre'].dropna().str.split('|').explode().str.strip()
    genre_counts = genres.value_counts()
    genre_names = genre_counts.index.tolist()
    genre_values = [int(x) for x in genre_counts.values]

    doc_count = int(df['film_type'].value_counts().get('Documentary', 0))
    non_doc_count = int(df['film_type'].value_counts().get('Non-Documentary', 0))

    top_genre = genre_names[0].title()
    top_genre_count = genre_values[0]
    doc_pct = round(doc_count / len(df) * 100, 1)

    # ── Charts Row ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_title("Genre Distribution")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Each rectangle represents a genre — size is proportional
                to the number of films. A film can belong to multiple genres.
                Hover for details.
            </div>
        """, unsafe_allow_html=True)

        # Treemap data
        treemap_data = [
            {"value": v, "name": k.title()}
            for k, v in zip(genre_names, genre_values)
        ]

        option_treemap = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} films",
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "series": [{
                "type": "treemap",
                "data": treemap_data,
                "width": "100%",
                "height": "100%",
                "roam": False,
                "nodeClick": False,
                "breadcrumb": {"show": False},
                "label": {
                    "show": True,
                    "formatter": "{b}\n{c}",
                    "fontSize": 12,
                    "fontWeight": "bold",
                    "color": "#FFFFFF"
                },
                "itemStyle": {
                    "borderColor": "#FFFFFF",
                    "borderWidth": 2,
                    "gapWidth": 2
                },
                "levels": [{
                    "itemStyle": {
                        "borderColor": "#FFFFFF",
                        "borderWidth": 2,
                        "gapWidth": 2
                    },
                    "colorSaturation": [0.4, 0.8]
                }],
                "colorMappingBy": "value",
                "color": [
                    "#002D62", "#1565C0", "#1976D2",
                    "#CE1126", "#E53935", "#42A5F5",
                    "#0D47A1", "#1E88E5", "#90CAF9",
                    "#B71C1C", "#EF5350", "#BBDEFB"
                ]
            }]
        }
        st_echarts(options=option_treemap, height="550px")

    with col_right:
        section_title("Documentary vs Non-Documentary")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Share of documentary productions vs all other genres
                in the Dominican film industry.
            </div>
        """, unsafe_allow_html=True)

        option_donut = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)",
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "legend": {
                "orient": "horizontal",
                "bottom": "5%",
                "textStyle": {"color": "#6B7280", "fontSize": 12}
            },
            "color": ["#002D62", "#CE1126"],
            "series": [{
                "type": "pie",
                "radius": ["45%", "72%"],
                "center": ["50%", "45%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 6,
                    "borderColor": "#FFFFFF",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}\n{d}%",
                    "fontSize": 12,
                    "color": "#1A1A2E"
                },
                "data": [
                    {"value": doc_count, "name": "Documentary"},
                    {"value": non_doc_count, "name": "Non-Documentary"}
                ]
            }]
        }
        st_echarts(options=option_donut, height="550px")

    # ── Key Insights Row ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='display:grid;grid-template-columns:3fr 2fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{top_genre}</strong> is the dominant genre with
                <strong>{top_genre_count} films</strong>, representing the
                majority of Dominican film production.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{doc_pct}%</strong> of Dominican productions are
                documentaries, making it the defining format of the local industry.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Industry Players":
    st.markdown("<div class='page-title'>Industry Players</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Top directors and production companies in Dominican cinema (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Prepare data ──
    top_directors = df['director'].value_counts().head(5)
    director_names = top_directors.index.tolist()
    director_values = [int(x) for x in top_directors.values]
    director_pcts = [round(v / len(df) * 100, 1) for v in director_values]

    top_companies = df['production_company'].value_counts().head(5)
    company_names = top_companies.index.tolist()
    company_values = [int(x) for x in top_companies.values]
    company_pcts = [round(v / len(df) * 100, 1) for v in company_values]

    # Add ranking numbers
    dir_labels = [f"#{i+1}  {n}" for i, n in enumerate(director_names)]
    comp_labels = [f"#{i+1}  {n}" for i, n in enumerate(company_names)]

    # ── Charts Row ──
    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Top 5 Directors")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Most prolific directors by total number of productions.
                Percentage reflects share of total registered films.
            </div>
        """, unsafe_allow_html=True)

        option_directors = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "none"},
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"},
                "formatter": "{b0}: {c0} films"
            },
            "grid": {
                "left": "3%",
                "right": "18%",
                "bottom": "3%",
                "top": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "value",
                "axisLabel": {"color": "#6B7280", "fontSize": 11},
                "splitLine": {"lineStyle": {"color": "#F3F4F6"}},
                "axisLine": {"show": False},
                "axisTick": {"show": False}
            },
            "yAxis": {
                "type": "category",
                "data": dir_labels[::-1],
                "axisLabel": {
                    "color": "#1A1A2E",
                    "fontSize": 11,
                    "fontWeight": "bold"
                },
                "axisLine": {"show": False},
                "axisTick": {"show": False}
            },
            "series": [{
                "type": "bar",
                "data": [
                    {
                        "value": v,
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 1, "y2": 0,
                                "colorStops": [
                                    {"offset": 0, "color": "#1565C0"},
                                    {"offset": 1, "color": "#002D62"}
                                ]
                            },
                            "borderRadius": [0, 6, 6, 0]
                        }
                    }
                    for v in director_values[::-1]
                ],
                "barMaxWidth": 40,
                "label": {
                    "show": True,
                    "position": "right",
                    "color": "#6B7280",
                    "fontSize": 11,
                    "formatter": [
                        f"{v} films ({p}%)"
                        for v, p in zip(director_values[::-1],
                                        director_pcts[::-1])
                    ]
                }
            }]
        }

        # Fix label formatter as list doesn't work — use function approach
        option_directors["series"][0]["label"]["formatter"] = "{c} films"
        st_echarts(options=option_directors, height="350px")

        # Custom ranking cards below chart
        st.markdown("<br>", unsafe_allow_html=True)
        for i, (name, value, pct) in enumerate(zip(
                director_names, director_values, director_pcts)):
            st.markdown(f"""
                <div style='display:flex;align-items:center;
                padding:8px 12px;margin-bottom:6px;
                background-color:#F8F9FA;border-radius:8px;
                border-left:3px solid {"#002D62" if i == 0 else "#E5E7EB"};'>
                    <span style='font-size:16px;font-weight:800;
                    color:{"#002D62" if i == 0 else "#9CA3AF"};
                    min-width:32px;'>#{i+1}</span>
                    <span style='font-size:13px;color:#1A1A2E;
                    font-weight:{"600" if i == 0 else "400"};
                    flex:1;'>{name}</span>
                    <span style='font-size:13px;color:#6B7280;'>
                    {value} films</span>
                    <span style='font-size:11px;color:#FFFFFF;
                    background-color:{"#002D62" if i == 0 else "#9CA3AF"};
                    border-radius:12px;padding:2px 8px;margin-left:8px;'>
                    {pct}%</span>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        section_title("Top 5 Production Companies")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Most active production companies by total number of films.
                Percentage reflects share of total registered films.
            </div>
        """, unsafe_allow_html=True)

        option_companies = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "none"},
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"},
                "formatter": "{b0}: {c0} films"
            },
            "grid": {
                "left": "3%",
                "right": "18%",
                "bottom": "3%",
                "top": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "value",
                "axisLabel": {"color": "#6B7280", "fontSize": 11},
                "splitLine": {"lineStyle": {"color": "#F3F4F6"}},
                "axisLine": {"show": False},
                "axisTick": {"show": False}
            },
            "yAxis": {
                "type": "category",
                "data": comp_labels[::-1],
                "axisLabel": {
                    "color": "#1A1A2E",
                    "fontSize": 11,
                    "fontWeight": "bold",
                    "width": 140,
                    "overflow": "truncate"
                },
                "axisLine": {"show": False},
                "axisTick": {"show": False}
            },
            "series": [{
                "type": "bar",
                "data": [
                    {
                        "value": v,
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 1, "y2": 0,
                                "colorStops": [
                                    {"offset": 0, "color": "#E53935"},
                                    {"offset": 1, "color": "#CE1126"}
                                ]
                            },
                            "borderRadius": [0, 6, 6, 0]
                        }
                    }
                    for v in company_values[::-1]
                ],
                "barMaxWidth": 40,
                "label": {
                    "show": True,
                    "position": "right",
                    "color": "#6B7280",
                    "fontSize": 11,
                    "formatter": "{c} films"
                }
            }]
        }
        st_echarts(options=option_companies, height="350px")

        # Custom ranking cards below chart
        st.markdown("<br>", unsafe_allow_html=True)
        for i, (name, value, pct) in enumerate(zip(
                company_names, company_values, company_pcts)):
            st.markdown(f"""
                <div style='display:flex;align-items:center;
                padding:8px 12px;margin-bottom:6px;
                background-color:#F8F9FA;border-radius:8px;
                border-left:3px solid {"#CE1126" if i == 0 else "#E5E7EB"};'>
                    <span style='font-size:16px;font-weight:800;
                    color:{"#CE1126" if i == 0 else "#9CA3AF"};
                    min-width:32px;'>#{i+1}</span>
                    <span style='font-size:13px;color:#1A1A2E;
                    font-weight:{"600" if i == 0 else "400"};
                    flex:1;'>{name}</span>
                    <span style='font-size:13px;color:#6B7280;'>
                    {value} films</span>
                    <span style='font-size:11px;color:#FFFFFF;
                    background-color:{"#CE1126" if i == 0 else "#9CA3AF"};
                    border-radius:12px;padding:2px 8px;margin-left:8px;'>
                    {pct}%</span>
                </div>
            """, unsafe_allow_html=True)

    # ── Key Insights Row ──
    st.markdown("<br>", unsafe_allow_html=True)
    top_dir = director_names[0]
    top_dir_count = director_values[0]
    top_company = company_names[0].replace(", SRL", "").replace(" SRL", "")
    top_company_count = company_values[0]

    st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{top_dir}</strong> is the most prolific director
                with <strong>{top_dir_count} films</strong> in the dataset.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{top_company}</strong> leads production output
                with <strong>{top_company_count} films</strong> produced.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Co-productions":
    st.markdown("<div class='page-title'>Co-production Analysis</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>International co-production partnerships in Dominican cinema (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    import plotly.express as px

    # ── Prepare data ──
    df['is_coproduction'] = df['coproduction_country'].apply(
        lambda x: 'Co-production' if isinstance(x, str) and '|' in x
        else 'Dominican Only'
    )
    coprod_counts = df['is_coproduction'].value_counts()

    countries = df['coproduction_country'].dropna().str.split('|').explode()
    countries = countries[countries != 'DO'].value_counts()

    # ISO alpha-2 to alpha-3 conversion
    iso2_to_iso3 = {
        'ES': 'ESP', 'MX': 'MEX', 'FR': 'FRA',
        'CO': 'COL', 'AR': 'ARG', 'US': 'USA',
        'PR': 'PRI', 'IT': 'ITA', 'BR': 'BRA',
        'CU': 'CUB', 'HT': 'HTI', 'PE': 'PER',
        'DE': 'DEU', 'NAM': 'NAM'
    }

    iso_to_name = {
        'ES': 'Spain', 'MX': 'Mexico', 'FR': 'France',
        'CO': 'Colombia', 'AR': 'Argentina', 'US': 'United States',
        'PR': 'Puerto Rico', 'IT': 'Italy', 'BR': 'Brazil',
        'CU': 'Cuba', 'HT': 'Haiti', 'PE': 'Peru',
        'DE': 'Germany', 'NAM': 'Namibia'
    }

    country_df = pd.DataFrame({
        'iso': [iso2_to_iso3.get(c, c) for c in countries.index],
        'count': countries.values,
        'country': [iso_to_name.get(c, c) for c in countries.index]
    })

    # ── Charts Row ──
    col_left, col_right = st.columns([1, 2])

    with col_left:
        section_title("Dominican Only vs Co-productions")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Share of 100% Dominican productions vs international
                co-productions.
            </div>
        """, unsafe_allow_html=True)

        coprod_data = [
            {"value": int(v), "name": k}
            for k, v in coprod_counts.items()
        ]

        option_donut = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)",
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "legend": {
                "orient": "horizontal",
                "bottom": "5%",
                "textStyle": {"color": "#6B7280", "fontSize": 12}
            },
            "color": ["#002D62", "#CE1126"],
            "series": [{
                "type": "pie",
                "radius": ["45%", "72%"],
                "center": ["50%", "45%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 6,
                    "borderColor": "#FFFFFF",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}\n{d}%",
                    "fontSize": 12,
                    "color": "#1A1A2E"
                },
                "data": coprod_data
            }]
        }
        st_echarts(options=option_donut, height="400px")

    with col_right:
        section_title("Co-production Partner Countries")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                World map showing countries that have co-produced films
                with the Dominican Republic. Darker color = more films.
                Hover for details.
            </div>
        """, unsafe_allow_html=True)

        fig_map = px.choropleth(
            country_df,
            locations='iso',
            locationmode='ISO-3',
            color='count',
            hover_name='country',
            hover_data={'iso': False, 'count': True},
            color_continuous_scale=[
                [0, '#BBDEFB'],
                [0.5, '#1565C0'],
                [1, '#002D62']
            ],
            labels={'count': 'Films'},
        )
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            coloraxis_colorbar=dict(
                title="Films",
                tickfont=dict(color="#6B7280", size=10),
                thickness=12,
                len=0.5
            ),
            geo=dict(
                projection_type='natural earth',
                bgcolor='#FFFFFF',
                lakecolor='#FFFFFF',
                landcolor='#F3F4F6',
                showland=True,
                showlakes=True,
                showcoastlines=True,
                coastlinecolor='#E5E7EB',
                showframe=False,
                showcountries=True,
                countrycolor='#E5E7EB'
            )
        )
        fig_map.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>Films: %{z}<extra></extra>'
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # ── Key Insights Row ──
    st.markdown("<br>", unsafe_allow_html=True)
    coprod_total = int(coprod_counts.get('Co-production', 0))
    coprod_pct = round(coprod_total / len(df) * 100, 1)
    top_partner = country_df.iloc[0]['country'] if len(country_df) > 0 else 'N/A'
    top_partner_count = int(country_df.iloc[0]['count']) if len(country_df) > 0 else 0

    st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 2fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{coprod_pct}%</strong> of Dominican productions
                involve at least one international co-production partner.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{top_partner}</strong> is the most frequent co-production
                partner with <strong>{top_partner_count} films</strong>,
                reflecting strong cultural and industry ties.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Budget":
    st.markdown("<div class='page-title'>Budget Analysis</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Investment trends in Dominican film production (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    import plotly.graph_objects as go
    import numpy as np

    # ── Prepare data ──
    budget_df = df[df['approx_budget'].notna()].copy()
    budget_df['production_year'] = budget_df['production_year'].astype(int)

    avg_budget_year = budget_df.groupby('production_year')['approx_budget'].mean().reset_index()
    avg_budget_year.columns = ['year', 'avg_budget']

    # Convert to millions
    avg_budget_millions = (avg_budget_year['avg_budget'] / 1e6).round(1).tolist()

    # ── Charts Row ──
    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Average Budget by Year")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Evolution of average production budget from 2018 to 2025.
                Shaded area highlights the investment trend over time.
            </div>
        """, unsafe_allow_html=True)

        option_area = {
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "#FFFFFF",
                "borderColor": "#E5E7EB",
                "textStyle": {"color": "#1A1A2E"}
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": avg_budget_year['year'].astype(str).tolist(),
                "axisLabel": {"color": "#6B7280", "fontSize": 11},
                "axisLine": {"lineStyle": {"color": "#E5E7EB"}},
                "axisTick": {"show": False}
            },
            "yAxis": {
                "type": "value",
                "name": "RD$ Millions",
                "nameTextStyle": {"color": "#6B7280", "fontSize": 11},
                "axisLabel": {
                    "color": "#6B7280",
                    "fontSize": 11,
                    "formatter": "{value}M"
                },
                "splitLine": {"lineStyle": {"color": "#F3F4F6"}},
                "axisLine": {"show": False}
            },
            "series": [{
                "type": "line",
                "data": avg_budget_millions,
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 8,
                "lineStyle": {
                    "color": "#002D62",
                    "width": 3
                },
                "itemStyle": {
                    "color": "#002D62",
                    "borderColor": "#FFFFFF",
                    "borderWidth": 2
                },
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(0,45,98,0.3)"},
                            {"offset": 1, "color": "rgba(0,45,98,0.02)"}
                        ]
                    }
                }
            }]
        }
        st_echarts(options=option_area, height="400px")

    with col_right:
        section_title("Budget Distribution by Year")
        st.markdown("""
            <div style='font-size:13px;color:#6B7280;margin-bottom:16px;'>
                Box plot showing budget spread per year. Box = interquartile range,
                line = median, dots = outliers.
            </div>
        """, unsafe_allow_html=True)

        fig_box = go.Figure()

        years_available = sorted(budget_df['production_year'].unique().tolist())
        colors_box = [
            '#002D62', '#1565C0', '#1976D2', '#1E88E5',
            '#42A5F5', '#90CAF9', '#BBDEFB', '#CE1126', '#E53935'
        ]

        for i, year in enumerate(years_available):
            year_data = budget_df[
                budget_df['production_year'] == year
            ]['approx_budget'] / 1e6
            fig_box.add_trace(go.Box(
                y=year_data,
                name=str(year),
                marker_color=colors_box[i % len(colors_box)],
                boxmean=True,
                line=dict(width=1.5)
            ))

        fig_box.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            showlegend=False,
            yaxis=dict(
                title="Budget (RD$ Millions)",
                gridcolor='#F3F4F6',
                tickfont=dict(color="#6B7280", size=10),
                title_font=dict(color="#6B7280", size=11),
                tickformat='.1f',
                tickprefix='RD$',
                ticksuffix='M'
            ),
            xaxis=dict(
                title="Year",
                tickfont=dict(color="#6B7280", size=11),
                title_font=dict(color="#6B7280", size=11)
            ),
            height=400
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Key Insights Row ──
    st.markdown("<br>", unsafe_allow_html=True)
    avg_budget = budget_df['approx_budget'].mean()
    max_budget = budget_df['approx_budget'].max()
    peak_budget_year = int(
        avg_budget_year['year'].iloc[
            avg_budget_year['avg_budget'].to_numpy().argmax()
        ]
    )
    peak_budget_value = avg_budget_year['avg_budget'].max()

    st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                The overall average production budget is
                <strong>RD${avg_budget/1e6:.1f}M</strong>, with a maximum
                of <strong>RD${max_budget/1e6:.1f}M</strong> recorded
                in the dataset.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{peak_budget_year}</strong> recorded the highest
                average budget at <strong>RD${peak_budget_value/1e6:.1f}M</strong>,
                reflecting peak investment in Dominican film production.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Film Catalog":
    st.markdown("<div class='page-title'>Film Catalog</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Complete searchable catalog of Dominican film productions (2018–2025)</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Filters Row ──
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        years_options = ['All'] + sorted(
            df['production_year'].dropna().astype(int).unique().tolist()
        )
        selected_year = st.selectbox("Year", options=years_options)

    with col_f2:
        genres_options = ['All'] + sorted(
            df['genre'].dropna().str.split('|').explode().str.strip().unique().tolist()
        )
        selected_genre = st.selectbox("Genre", options=genres_options)

    with col_f3:
        status_options = ['All'] + sorted(df['status'].dropna().unique().tolist())
        selected_status = st.selectbox("Status", options=status_options)

    with col_f4:
        search_term = st.text_input("Search by title or director", placeholder="Type to search...")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Apply filters ──
    filtered_df = df.copy()

    if selected_year != 'All':
        filtered_df = filtered_df[
            filtered_df['production_year'] == int(selected_year)
        ]

    if selected_genre != 'All':
        filtered_df = filtered_df[
            filtered_df['genre'].str.contains(selected_genre, na=False)
        ]

    if selected_status != 'All':
        filtered_df = filtered_df[
            filtered_df['status'] == selected_status
        ]

    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['director'].str.contains(search_term, case=False, na=False)
        ]

    # ── Results counter ──
    st.markdown(f"""
        <div style='font-size:13px;color:#6B7280;margin-bottom:12px;'>
            Showing <strong style='color:#002D62;'>{len(filtered_df)}</strong>
            of <strong style='color:#002D62;'>{len(df)}</strong> films
        </div>
    """, unsafe_allow_html=True)

    # ── Table ──
    display_cols = {
        'title': 'Title',
        'production_year': 'Year',
        'genre': 'Genre',
        'director': 'Director',
        'production_company': 'Production Company',
        'status': 'Status',
        'approx_budget': 'Budget (RD$M)'
    }

    table_df = filtered_df[list(display_cols.keys())].copy()
    table_df.columns = list(display_cols.values())

    # Format budget
    table_df['Budget (RD$M)'] = table_df['Budget (RD$M)'].apply(
        lambda x: f"RD${x/1e6:.1f}M" if pd.notna(x) else "—"
    )

    # Format status
    table_df['Status'] = table_df['Status'].str.replace('_', ' ').str.title()

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            'Title': st.column_config.TextColumn('Title', width='large'),
            'Year': st.column_config.NumberColumn('Year', format='%d', width='small'),
            'Genre': st.column_config.TextColumn('Genre', width='medium'),
            'Director': st.column_config.TextColumn('Director', width='medium'),
            'Production Company': st.column_config.TextColumn('Production Company', width='medium'),
            'Status': st.column_config.TextColumn('Status', width='small'),
            'Budget (RD$M)': st.column_config.TextColumn('Budget (RD$M)', width='small')
        }
    )

    # ── Key Insights Row ──
    st.markdown("<br>", unsafe_allow_html=True)
    released_count = len(df[df['status'] == 'released'])
    in_prod_count = len(df[df['status'] == 'in_production'])

    st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{released_count} films</strong> have been commercially
                released, representing the commercially distributed output
                of the Dominican film industry.
                </span>
            </div>
            <div style='background-color:#F0F4FF;border-left:4px solid #002D62;
            border-radius:0 8px 8px 0;padding:12px 16px;'>
                <span style='font-size:12px;font-weight:600;color:#002D62;
                text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>
                <span style='font-size:13px;color:#1A1A2E;'>
                <strong>{in_prod_count} films</strong> are currently in production,
                signaling continued growth and activity in the local industry.
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)