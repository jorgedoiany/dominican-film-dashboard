import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_echarts import st_echarts
from components.ui import page_header, key_insight_row, chart_card, empty_state
from utils.data import validate_required_columns, has_rows


def render(df: pd.DataFrame) -> None:
    required_columns = ['coproduction_country']
    valid_columns, missing_columns = validate_required_columns(df, required_columns)
    if not valid_columns:
        empty_state(
            "Missing Required Data",
            "The Co-productions page cannot be rendered because required columns are missing: "
            + ", ".join(missing_columns)
            + ".",
        )
        return

    if not has_rows(df):
        empty_state(
            "No Data Available",
            "The dataset is empty, so co-production analysis cannot be displayed.",
        )
        return

    page_header(
        "Co-production Analysis",
        "International co-production partnerships in Dominican cinema (2018–2025)"
    )

    # ── Prepare data ──
    df = df.copy()
    df['is_coproduction'] = df['coproduction_country'].apply(
        lambda x: 'Co-production' if isinstance(x, str) and '|' in x
        else 'Dominican Only'
    )
    coprod_counts = df['is_coproduction'].value_counts()

    countries = df['coproduction_country'].dropna().str.split('|').explode()
    countries = countries[countries != 'DO'].value_counts()

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

    if coprod_counts.empty:
        empty_state(
            "No Co-production Status Data",
            "There are no co-production values available to build the distribution chart.",
        )
        return

    # ── Charts Row ──
    col_left, col_right = st.columns([1, 2], vertical_alignment="top")

    with col_left:
        with chart_card(
            title="Dominican Only vs Co-productions",
            subtitle=(
                "Share of 100% Dominican productions versus international "
                "co-productions."
            ),
        ):
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
        with chart_card(
            title="Co-production Partner Countries",
            subtitle=(
                "World map showing countries that have co-produced films "
                "with the Dominican Republic. Darker color means more films."
            ),
        ):
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
                height=400,
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

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    coprod_total = int(coprod_counts.get('Co-production', 0))
    coprod_pct = round(coprod_total / len(df) * 100, 1)
    top_partner = country_df.iloc[0]['country'] if len(country_df) > 0 else 'N/A'
    top_partner_count = int(country_df.iloc[0]['count']) if len(country_df) > 0 else 0

    key_insight_row(
        insights=[
            f"<strong>{coprod_pct}%</strong> of Dominican productions "
            f"involve at least one international co-production partner.",
            f"<strong>{top_partner}</strong> is the most frequent co-production "
            f"partner with <strong>{top_partner_count} films</strong>, "
            f"reflecting strong cultural and industry ties."
        ],
        columns="1fr 2fr"
    )