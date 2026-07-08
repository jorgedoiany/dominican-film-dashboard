import pandas as pd
import streamlit as st


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> tuple[bool, list[str]]:
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def has_rows(df: pd.DataFrame) -> bool:
    return not df.empty


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv('data/01_movies.csv', sep=';', encoding='utf-8-sig')
    df['film_type'] = df['genre'].apply(
        lambda x: 'Documentary' if isinstance(x, str)
        and 'documentary' in x.lower() else 'Non-Documentary'
    )
    return df