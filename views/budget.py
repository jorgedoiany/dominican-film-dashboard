import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
from components.ui import page_header, key_insight_row, chart_card


def render(df: pd.DataFrame) -> None:
    page_header(
        "Budget Analysis",
        "Investment trends in Dominican film production (2018–2025)"
    )

    # ── Prepare data ──
    budget_df = df[df['approx_budget'].notna()].copy()
    budget_df['production_year'] = budget_df['production_year'].astype(int)

    avg_budget_year = budget_df.groupby('production_year')['approx_budget'].mean().reset_index()
    avg_budget_year.columns = ['year', 'avg_budget']

    avg_budget_millions = (avg_budget_year['avg_budget'] / 1e6).round(1).tolist()

    # ── Charts Row ──
    col_left, col_right = st.columns(2, vertical_alignment="top")

    with col_left:
        with chart_card(
            title="Average Budget by Year",
            subtitle=(
                "Evolution of average production budget from 2018 to 2025. "
                "Shaded area highlights the investment trend over time."
            ),
        ):
            option_area = {
                "tooltip": {
                    "trigger": "axis",
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
                    "lineStyle": {"color": "#002D62", "width": 3},
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
        with chart_card(
            title="Budget Distribution by Year",
            subtitle=(
                "Box plot showing budget spread per year. "
                "Box is IQR, line is median, dots are outliers."
            ),
        ):
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

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    avg_budget = budget_df['approx_budget'].mean()
    max_budget = budget_df['approx_budget'].max()
    peak_budget_year = int(
        avg_budget_year['year'].iloc[
            avg_budget_year['avg_budget'].to_numpy().argmax()
        ]
    )
    peak_budget_value = avg_budget_year['avg_budget'].max()

    key_insight_row(
        insights=[
            f"The overall average production budget is "
            f"<strong>RD${avg_budget/1e6:.1f}M</strong>, with a maximum "
            f"of <strong>RD${max_budget/1e6:.1f}M</strong> recorded "
            f"in the dataset.",
            f"<strong>{peak_budget_year}</strong> recorded the highest "
            f"average budget at <strong>RD${peak_budget_value/1e6:.1f}M</strong>, "
            f"reflecting peak investment in Dominican film production."
        ],
        columns="1fr 1fr"
    )