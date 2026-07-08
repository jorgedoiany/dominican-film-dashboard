import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from components.ui import page_header, key_insight_row, chart_card, empty_state
from utils.data import validate_required_columns, has_rows


def render(df: pd.DataFrame) -> None:
    required_columns = ['genre', 'film_type']
    valid_columns, missing_columns = validate_required_columns(df, required_columns)
    if not valid_columns:
        empty_state(
            "Missing Required Data",
            "The Genres page cannot be rendered because required columns are missing: "
            + ", ".join(missing_columns)
            + ".",
        )
        return

    if not has_rows(df):
        empty_state(
            "No Data Available",
            "The dataset is empty, so genre analysis cannot be displayed.",
        )
        return

    page_header(
        "Genre Analysis",
        "Distribution of film genres in Dominican cinema (2018–2025)"
    )

    # ── Prepare data ──
    genres = df['genre'].dropna().str.split('|').explode().str.strip()
    genre_counts = genres.value_counts()
    if genre_counts.empty:
        empty_state(
            "No Genre Data",
            "There are no valid genre values to render genre visualizations.",
        )
        return

    genre_names = genre_counts.index.tolist()
    genre_values = genre_counts.values.tolist()

    doc_count = int(df['film_type'].value_counts().get('Documentary', 0))
    non_doc_count = int(df['film_type'].value_counts().get('Non-Documentary', 0))

    top_genre = genre_names[0].title()
    top_genre_count = genre_values[0]
    doc_pct = round(doc_count / len(df) * 100, 1)

    # ── Charts Row ──
    col_left, col_right = st.columns([3, 2], vertical_alignment="top")

    with col_left:
        with chart_card(
            title="Genre Distribution",
            subtitle=(
                "Each rectangle represents a genre. Size is proportional "
                "to the number of films, and a film can belong to multiple genres."
            ),
            header_height=34,
        ):
            treemap_data = [
                {"value": int(float(str(v))), "name": str(k).title()}
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
        with chart_card(
            title="Documentary vs Non-Documentary",
            subtitle=(
                "Share of documentary productions versus all other genres "
                "in the Dominican film industry."
            ),
            header_height=34,
        ):
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
                        "show": False
                    },
                    "labelLine": {"show": False},
                    "data": [
                        {"value": doc_count, "name": "Documentary"},
                        {"value": non_doc_count, "name": "Non-Documentary"}
                    ]
                }]
            }
            st_echarts(options=option_donut, height="550px")

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    key_insight_row(
        insights=[
            f"<strong>{top_genre}</strong> is the dominant genre with "
            f"<strong>{top_genre_count} films</strong>, representing the "
            f"majority of Dominican film production.",
            f"<strong>{doc_pct}%</strong> of Dominican productions are "
            f"documentaries, making it the defining format of the local industry."
        ],
        columns="3fr 2fr"
    )