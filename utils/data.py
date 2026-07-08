import pandas as pd
import streamlit as st


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv('data/01_movies.csv', sep=';', encoding='utf-8-sig')
    df['film_type'] = df['genre'].apply(
        lambda x: 'Documentary' if isinstance(x, str)
        and 'documentary' in x.lower() else 'Non-Documentary'
    )
    return df