
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="District Skill Planner",
    page_icon="📍",
    layout="wide"
)

st.title("District Skill Planner")
st.write(
    "Explore district-level skills evidence, compare indicators, "
    "and identify candidate training priorities."
)

st.info(
    "Demo mode: sample data is illustrative only. "
    "Replace it with verified data before drawing conclusions."
)

# ------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)

default_path = Path("data/district_skills.csv")

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

elif default_path.exists():
    df = pd.read_csv(default_path)

else:
    st.error("Upload a dataset to continue.")
    st.stop()

# ------------------------------------------------
# 2. VALIDATE COLUMNS
# ------------------------------------------------

required_columns = [
    "district",
    "sector",
    "skill",
    "demand_score",
    "gap_score",
    "training_access",
    "momentum",
    "period",
    "source"
]

df.columns = df.columns.str.strip()

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {missing_columns}"
    )
    st.stop()

# Convert numeric columns safely
numeric_columns = [
    "demand_score",
    "gap_score",
    "training_access",
    "momentum"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    )

# Clean basic text fields
for col in ["district", "sector", "skill", "source"]:
    df[col] = df[col].astype("string").str.strip()
    df[col] = df[col].replace("", pd.NA)

# Check invalid indicator values
invalid_rows = (
    df[numeric_columns].lt(0)
    | df[numeric_columns].gt(100)
).any(axis=1)

# A valid row must have all four indicators
complete_rows = df[numeric_columns].notna().all(axis=1)

valid_rows = (
    ~invalid_rows
    & complete_rows
    & df["district"].notna()
    & df["skill"].notna()
)

df["data_status"] = np.where(
    valid_rows, "Valid", "Needs review"
)

# Preserve original rows for quality reporting
quality_df = df.copy()

# Calculate scores only for valid rows
df["priority_score"] = np.nan

df.loc[valid_rows, "priority_score"] = (
    df.loc[valid_rows, "demand_score"] * 0.40
    + df.loc[valid_rows, "gap_score"] * 0.30
    + df.loc[valid_rows, "training_access"] * 0.20
    + df.loc[valid_rows, "momentum"] * 0.10
)

# ------------------------------------------------
# 3. SIDEBAR FILTERS
# ------------------------------------------------

st.sidebar.header("Planner Filters")

district_options = sorted(
    df["district"].dropna().unique().tolist()
)

if not district_options:
    st.error("No valid district names were found.")
    st.stop()

selected_district = st.sidebar.selectbox(
    "Select district",
    district_options
)

period_options = sorted(
    df["period"].dropna().astype(str).unique().tolist()
)

selected_period = st.sidebar.selectbox(
    "Reporting period",
    ["All"] + period_options
)

selected_df = df[
    (df["district"] == selected_district)
    & df["data_status"].eq("Valid")
].copy()

if selected_period != "All":
    selected_df = selected_df[
        selected_df["period"].astype(str)
        == selected_period
    ]

# ------------------------------------------------
# 4. OVERVIEW
# ------------------------------------------------

st.subheader("District Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Districts in dataset", len(district_options))
c2.metric("Skills recorded", df["skill"].nunique())
c3.metric("Rows needing review", int((~valid_rows).sum()))

st.caption(
    "Counts refer to uploaded records, not total employment."
)

# ------------------------------------------------
# 5. DISTRICT SKILL PRIORITIES
# ------------------------------------------------

st.subheader(
    f"Candidate Skill Priorities — {selected_district}"
)

if selected_df.empty:
    st.warning(
        "No complete, valid records match these filters. "
        "Check the source data before making recommendations."
    )
else:
    skill_summary = (
        selected_df
        .groupby(["skill", "sector"], as_index=False)
        .agg(
            priority_score=("priority_score", "mean"),
            demand_score=("demand_score", "mean"),
            gap_score=("gap_score", "mean"),
            training_access=("training_access", "mean"),
            momentum=("momentum", "mean"),
            records=("priority_score", "size")
        )
        .sort_values("priority_score", ascending=False)
    )

    st.dataframe(
        skill_summary.round(2),
        use_container_width=True
    )

    fig = px.bar(
        skill_summary,
        x="skill",
        y="priority_score",
        color="sector",
        title="Weighted Skill-Priority Scores",
        labels={
            "skill": "Skill",
            "priority_score": "Score out of 100",
            "sector": "Sector"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Explain the top row without claiming causation
    top = skill_summary.iloc[0]

    st.markdown("### Why is this skill prioritised?")

    st.write(
        f"**Skill:** {top['skill']}"
    )
    st.write(
        f"**Sector:** {top['sector']}"
    )
    st.write(
        f"**Weighted score:** {top['priority_score']:.1f}/100"
    )
    st.write(
        f"Demand indicator: {top['demand_score']:.1f}; "
        f"gap indicator: {top['gap_score']:.1f}; "
        f"training-access indicator: {top['training_access']:.1f}; "
        f"momentum indicator: {top['momentum']:.1f}."
    )

    st.caption(
        "This is a score-based candidate priority, not proof "
        "that the district has a measured skills shortage."
    )

# ------------------------------------------------
# 6. DISTRICT COMPARISON
# ------------------------------------------------

st.subheader("Compare Districts")

comparison_df = df[
    df["data_status"].eq("Valid")
].copy()

if selected_period != "All":
    comparison_df = comparison_df[
        comparison_df["period"].astype(str)
        == selected_period
    ]

comparison_df = (
    comparison_df.groupby("district", as_index=False)
    .agg(
        average_priority=("priority_score", "mean"),
        valid_records=("priority_score", "count")
    )
    .sort_values("average_priority", ascending=False)
)

if not comparison_df.empty:
    fig2 = px.bar(
        comparison_df,
        x="district",
        y="average_priority",
        title="Average Candidate Priority Score by District",
        labels={
            "district": "District",
            "average_priority": "Average score"
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        comparison_df.round(2),
        use_container_width=True
    )

    st.caption(
        "Compare districts only after confirming that the "
        "indicators, periods, and coverage are comparable."
    )

# ------------------------------------------------
# 7. DATA QUALITY
# ------------------------------------------------

st.subheader("Data Quality Report")

quality_report = pd.DataFrame({
    "Column": quality_df.columns,
    "Missing values": [
        int(quality_df[col].isna().sum())
        for col in quality_df.columns
    ]
})

st.dataframe(
    quality_report,
    use_container_width=True
)

review_df = quality_df[
    quality_df["data_status"] == "Needs review"
]

st.write("Records requiring review")

st.dataframe(
    review_df,
    use_container_width=True
)

# ------------------------------------------------
# 8. SOURCE EVIDENCE
# ------------------------------------------------

st.subheader("Source Information")

source_columns = [
    "district", "skill", "sector", "period", "source"
]

st.dataframe(
    df[source_columns].drop_duplicates(),
    use_container_width=True
)

# ------------------------------------------------
# 9. DOWNLOAD REPORT
# ------------------------------------------------

st.subheader("Export Results")

if not selected_df.empty:
    export_df = selected_df.sort_values(
        "priority_score", ascending=False
    )

    csv_data = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download district report (CSV)",
        data=csv_data,
        file_name="district_skill_planner_report.csv",
        mime="text/csv"
    )

st.caption(
    "Recommendations require verified evidence, "
    "documented scoring methods, and human review."
)
