import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from components.ui import page_header, key_insight_row, html_block, chart_card, empty_state
from utils.data import validate_required_columns, has_rows


def render(df: pd.DataFrame) -> None:
    required_columns = ['director', 'production_company']
    valid_columns, missing_columns = validate_required_columns(df, required_columns)
    if not valid_columns:
        empty_state(
            "Missing Required Data",
            "The Industry Players page cannot be rendered because required columns are missing: "
            + ", ".join(missing_columns)
            + ".",
        )
        return

    if not has_rows(df):
        empty_state(
            "No Data Available",
            "The dataset is empty, so industry rankings cannot be displayed.",
        )
        return

    page_header(
        "Industry Players",
        "Top directors and production companies in Dominican cinema (2018–2025)"
    )

    # ── Prepare data ──
    top_directors = df['director'].value_counts().head(5)
    if top_directors.empty:
        empty_state(
            "No Director Data",
            "There are no valid director values to render the top directors ranking.",
        )
        return

    director_names: list[str] = [str(x) for x in top_directors.index.tolist()]
    director_values: list[int] = [int(x) for x in top_directors.values.astype(int).tolist()]
    director_pcts: list[float] = [round(v / len(df) * 100, 1) for v in director_values]

    top_companies = df['production_company'].value_counts().head(5)
    if top_companies.empty:
        empty_state(
            "No Production Company Data",
            "There are no valid production company values to render the top companies ranking.",
        )
        return

    company_names: list[str] = [str(x) for x in top_companies.index.tolist()]
    company_values: list[int] = [int(x) for x in top_companies.values.astype(int).tolist()]
    company_pcts: list[float] = [round(v / len(df) * 100, 1) for v in company_values]

    dir_labels = [f"#{i+1}  {n}" for i, n in enumerate(director_names)]
    comp_labels = [f"#{i+1}  {n}" for i, n in enumerate(company_names)]

    # ── Charts Row ──
    col_left, col_right = st.columns(2, vertical_alignment="top")

    with col_left:
        with chart_card(
            title="Top 5 Directors",
            subtitle=(
                "Most prolific directors by total number of productions. "
                "Percentage reflects share of total registered films."
            ),
        ):
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
                    "left": "3%", "right": "18%",
                    "bottom": "3%", "top": "3%",
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
                        "formatter": "{c} films"
                    }
                }]
            }
            st_echarts(options=option_directors, height="350px")

        st.markdown("<br>", unsafe_allow_html=True)
        for i, (name, value, pct) in enumerate(zip(
                director_names, director_values, director_pcts)):
            html_block(f"""
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
            """)

    with col_right:
        with chart_card(
            title="Top 5 Production Companies",
            subtitle=(
                "Most active production companies by total number of films. "
                "Percentage reflects share of total registered films."
            ),
        ):
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
                    "left": "3%", "right": "18%",
                    "bottom": "3%", "top": "3%",
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

        st.markdown("<br>", unsafe_allow_html=True)
        for i, (name, value, pct) in enumerate(zip(
                company_names, company_values, company_pcts)):
            html_block(f"""
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
            """)

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    top_dir = director_names[0]
    top_dir_count = director_values[0]
    top_company = company_names[0].replace(", SRL", "").replace(" SRL", "")
    top_company_count = company_values[0]

    key_insight_row(
        insights=[
            f"<strong>{top_dir}</strong> is the most prolific director "
            f"with <strong>{top_dir_count} films</strong> in the dataset.",
            f"<strong>{top_company}</strong> leads production output "
            f"with <strong>{top_company_count} films</strong> produced."
        ],
        columns="1fr 1fr"
    )