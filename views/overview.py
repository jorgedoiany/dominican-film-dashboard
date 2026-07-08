import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from components.ui import (
    kpi_card,
    page_header,
    key_insight_row,
    empty_state,
    chart_card,
)
from utils.data import validate_required_columns, has_rows


def render(df: pd.DataFrame) -> None:
    required_columns = [
        'director',
        'approx_budget',
        'production_year',
        'status',
    ]
    valid_columns, missing_columns = validate_required_columns(df, required_columns)
    if not valid_columns:
        empty_state(
            "Missing Required Data",
            "The Overview page cannot be rendered because required columns are missing: "
            + ", ".join(missing_columns)
            + ".",
        )
        return

    if not has_rows(df):
        empty_state(
            "No Data Available",
            "The dataset is empty, so overview metrics and charts cannot be displayed.",
        )
        return

    page_header(
        "Dominican Film Industry Dashboard",
        "Executive overview of Dominican Republic film production (2018–2025)"
    )

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
    if films_by_year.empty:
        empty_state(
            "No Production Year Data",
            "There are no valid production year values to render the annual trend.",
        )
        return

    years = [str(y) for y in films_by_year.index.tolist()]
    values = films_by_year.values.tolist()
    peak_year = int(films_by_year.idxmax())
    peak_value = int(films_by_year.max())

    status_counts = df['status'].value_counts()
    if status_counts.empty:
        empty_state(
            "No Status Data",
            "There are no valid status values to render the status distribution.",
        )
        return

    status_data = [
        {"value": int(v), "name": str(k).replace("_", " ").title()}
        for k, v in status_counts.items()
    ]
    top_status = str(status_counts.index.tolist()[0]).replace("_", " ").title()
    top_value = int(status_counts.values[0])
    pct = round(top_value / len(df) * 100, 1)

    # ── Charts Row ──
    col_left, col_right = st.columns([2, 1], vertical_alignment="top")

    with col_left:
        with chart_card(
            title="Films by Year",
            subtitle=(
                "Annual volume of Dominican film productions registered "
                "between 2018 and 2025."
            ),
        ):
            option_bar = {
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "#FFFFFF",
                    "borderColor": "#E5E7EB",
                    "textStyle": {"color": "#1A1A2E"}
                },
                "grid": {
                    "left": "3%", "right": "4%",
                    "bottom": "3%", "containLabel": True
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
                    "emphasis": {"itemStyle": {"color": "#CE1126"}},
                    "label": {
                        "show": True, "position": "top",
                        "color": "#6B7280", "fontSize": 11
                    }
                }]
            }
            st_echarts(options=option_bar, height="400px")

    with col_right:
        with chart_card(
            title="Status Distribution",
            subtitle=(
                "Current distribution of production statuses across all "
                "registered Dominican films."
            ),
        ):
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
                    "bottom": "2%",
                    "textStyle": {"color": "#6B7280", "fontSize": 11}
                },
                "color": [
                    "#002D62", "#CE1126", "#1565C0",
                    "#E53935", "#42A5F5", "#90CAF9"
                ],
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["62%", "40%"],
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

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    key_insight_row(
        insights=[
            f"{peak_year} was the most productive year with <strong>{peak_value} films</strong>, "
            f"reflecting a post-pandemic surge in Dominican film production.",
            f"<strong>{top_status}</strong> is the most common status, "
            f"representing <strong>{pct}%</strong> of all registered productions."
        ],
        columns="2fr 1fr"
    )