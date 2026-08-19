import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


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


@st.cache_data
def load_cipac_data() -> pd.DataFrame:
    """Load all CIPAC resolutions from Supabase."""
    engine = create_engine(os.getenv('SUPABASE_DB_URL') or '')
    df = pd.read_sql("""
        SELECT
            resolution_number,
            year,
            incentive_article,
            resolution_type,
            investor_name,
            investor_rnc,
            producer_rnc,
            film_title,
            local_company,
            pur_number,
            cpnd_number,
            request_date,
            resolution_date,
            validated_expenses_dop,
            tax_credit_dop,
            tax_credit_pct,
            total_budget_approved,
            total_budget_executed
        FROM cipac_resolutions
        ORDER BY year, resolution_number
    """, engine)
    return df