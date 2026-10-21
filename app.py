import streamlit as st
import pandas as pd

# ==========================================
# LOAD CSV WITH AUTOMATIC COLUMN FIXING
# ==========================================

CSV_FILE = "district_skills.csv"

try:
    df = None

    # Try comma, semicolon and tab separators
    for separator in [",", ";", "\t"]:
        try:
            temp_df = pd.read_csv(
                CSV_FILE,
                sep=separator,
                encoding="utf-8-sig",
                skip_blank_lines=True
            )

            if len(temp_df.columns) >= 3:
                df = temp_df
                break

        except Exception:
            continue

    if df is None:
        st.error(
            "Could not read district_skills.csv. "
            "Please check that it is a valid CSV file."
        )
        st.stop()

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("%", "percent", regex=False)
    )

    # Show the actual columns found in the CSV
    st.info(
        "CSV columns found: "
        + ", ".join(df.columns)
    )

    # Rename common alternative header names
    column_aliases = {
        "district_name": "district",
        "districts": "district",
        "sector_name": "sector",
        "sectors": "sector",
        "skill_name": "skill",
        "skills": "skill",
        "employment": "employed",
        "employed_students": "employed",
        "unemployed_students": "unemployed",
        "openings": "job_openings",
        "vacancies": "job_openings",
        "job_vacancies": "job_openings",
        "demand": "skill_demand",
        "demand_score": "skill_demand",
        "available": "available_candidates",
        "candidates_available": "available_candidates",
        "gap": "skill_gap",
        "gap_score": "skill_gap"
    }

    df = df.rename(columns=column_aliases)

    # Required columns
    required_columns = [
        "district", "sector", "skill",
        "employed", "unemployed", "job_openings",
        "skill_demand", "available_candidates", "skill_gap"
    ]

    # Default values for missing columns
    defaults = {
        "district": "Unknown District",
        "sector": "General",
        "skill": "General Skill",
        "employed": 0,
        "unemployed": 0,
        "job_openings": 0,
        "skill_demand": 0,
        "available_candidates": 0,
        "skill_gap": 0
    }

    missing_columns = []

    for column in required_columns:
        if column not in df.columns:
            df[column] = defaults[column]
            missing_columns.append(column)

    if missing_columns:
        st.warning(
            "These columns were missing and were filled with default values: "
            f"{', '.join(missing_columns)}"
        )

    # Clean text columns
    for column in ["district", "sector", "skill"]:
        df[column] = df[column].astype(str).str.strip()

    # Clean numeric columns
    numeric_columns = [
        "employed", "unemployed", "job_openings",
        "skill_demand", "available_candidates", "skill_gap"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

except FileNotFoundError:
    st.error(
        "Could not find `district_skills.csv`. "
        "Please place it in the same folder as this app."
    )
    st.stop()
