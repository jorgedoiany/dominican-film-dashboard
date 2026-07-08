import streamlit as st
import pandas as pd
from components.ui import page_header, key_insight_row
from components.ui import html_block


def render(df: pd.DataFrame) -> None:
    page_header(
        "Film Catalog",
        "Complete searchable catalog of Dominican film productions (2018–2025)"
    )

    # ── Filters Row ──
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        years_options = ['All'] + sorted(
            df['production_year'].dropna().astype(int).unique().tolist()
        )
        selected_year = st.selectbox("Year", options=years_options)

    with col_f2:
        genres_options = ['All'] + sorted(
            df['genre'].dropna().str.split('|').explode()
            .str.strip().unique().tolist()
        )
        selected_genre = st.selectbox("Genre", options=genres_options)

    with col_f3:
        status_options = ['All'] + sorted(
            df['status'].dropna().unique().tolist()
        )
        selected_status = st.selectbox("Status", options=status_options)

    with col_f4:
        search_term = st.text_input(
            "Search by title or director",
            placeholder="Type to search..."
        )

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
            filtered_df['title'].str.contains(
                search_term, case=False, na=False
            ) |
            filtered_df['director'].str.contains(
                search_term, case=False, na=False
            )
        ]

    # ── Results counter ──
    html_block(f"""
        <div style='font-size:13px;color:#6B7280;margin-bottom:12px;'>
            Showing <strong style='color:#002D62;'>{len(filtered_df)}</strong>
            of <strong style='color:#002D62;'>{len(df)}</strong> films
        </div>
    """)

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

    table_df['Budget (RD$M)'] = table_df['Budget (RD$M)'].apply(
        lambda x: f"RD${x/1e6:.1f}M" if pd.notna(x) else "—"
    )
    table_df['Status'] = table_df['Status'].str.replace(
        '_', ' '
    ).str.title()

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            'Title': st.column_config.TextColumn('Title', width='large'),
            'Year': st.column_config.NumberColumn(
                'Year', format='%d', width='small'
            ),
            'Genre': st.column_config.TextColumn('Genre', width='medium'),
            'Director': st.column_config.TextColumn(
                'Director', width='medium'
            ),
            'Production Company': st.column_config.TextColumn(
                'Production Company', width='medium'
            ),
            'Status': st.column_config.TextColumn('Status', width='small'),
            'Budget (RD$M)': st.column_config.TextColumn(
                'Budget (RD$M)', width='small'
            )
        }
    )

    # ── Key Insights ──
    st.markdown("<br>", unsafe_allow_html=True)
    released_count = len(df[df['status'] == 'released'])
    in_prod_count = len(df[df['status'] == 'in_production'])

    key_insight_row(
        insights=[
            f"<strong>{released_count} films</strong> have been commercially "
            f"released, representing the commercially distributed output "
            f"of the Dominican film industry.",
            f"<strong>{in_prod_count} films</strong> are currently in production, "
            f"signaling continued growth and activity in the local industry."
        ],
        columns="1fr 1fr"
    )