
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from io import BytesIO

# ============================================================
# K-SIWAP
# Karnataka Skill Intelligence & Workforce Analytics Platform
# Module 4: District-Level Skill Planning and Recommendations
# ============================================================

st.set_page_config(
    page_title="K-SIWAP | Module 4",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------
# 1. Constants
# ------------------------------------------------------------

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "district_data.csv"

REQUIRED_COLUMNS = [
    "District",
    "Sector",
    "Employer_Demand",
    "Skill_Gap",
    "Training_Access",
    "Demand_Momentum"
]

NUMERIC_COLUMNS = [
    "Employer_Demand",
    "Skill_Gap",
    "Training_Access",
    "Demand_Momentum",
    "Training_Capacity",
    "Evidence_Confidence"
]

SAMPLE_DATA = pd.DataFrame({
    "District": [
        "Bengaluru Urban",
        "Mysuru",
        "Belagavi",
        "Mangaluru",
        "Kalaburagi",
        "Hubballi-Dharwad"
    ],
    "Sector": [
        "IT",
        "Manufacturing",
        "Manufacturing",
        "Logistics",
        "Healthcare",
        "IT"
    ],
    "Employer_Demand": [90, 78, 70, 75, 68, 82],
    "Skill_Gap": [65, 72, 80, 60, 75, 68],
    "Training_Access": [85, 70, 62, 72, 55, 76],
    "Demand_Momentum": [88, 72, 68, 80, 74, 79],
    "Training_Capacity": [80, 65, 60, 70, 50, 72],
    "Evidence_Confidence": [90, 80, 75, 78, 65, 82]
})


# ------------------------------------------------------------
# 2. Helper functions
# ------------------------------------------------------------

def make_unique_columns(df):
    """
    Ensure every DataFrame column name is unique.
    Example: Evidence_Confidence, Evidence_Confidence__2
    """
    df = df.copy()
    seen = {}
    new_columns = []

    for column in df.columns:
        name = str(column).strip()

        if name == "":
            name = "Unnamed_Column"

        if name not in seen:
            seen[name] = 1
            new_columns.append(name)
        else:
            seen[name] += 1
            new_columns.append(f"{name}__{seen[name]}")

    df.columns = new_columns
    return df


def prepare_data(raw_data):
    """
    Clean data and prepare the columns required by the dashboard.
    """
    df = make_unique_columns(raw_data)

    # Remove surrounding spaces from column names.
    df.columns = [str(c).strip() for c in df.columns]

    # Check required columns.
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    # Normalize text columns.
    df["District"] = (
        df["District"].fillna("Unknown").astype(str).str.strip()
    )
    df["Sector"] = (
        df["Sector"].fillna("Unknown").astype(str).str.strip()
    )

    # Add optional columns if they do not exist.
    if "Training_Capacity" not in df.columns:
        df["Training_Capacity"] = 50

    if "Evidence_Confidence" not in df.columns:
        df["Evidence_Confidence"] = 50

    # Convert numeric columns safely.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        df[column] = df[column].fillna(0).clip(0, 100)

    # Keep the required district and sector information.
    df = df[df["District"].ne("") & df["Sector"].ne("")].copy()

    # Final safeguard against duplicate column names.
    df = make_unique_columns(df)

    return df


def calculate_priorities(df, weights):
    """
    Calculate a weighted priority score from 0 to 100.
    """
    result = df.copy()

    result["Priority_Score"] = (
        result["Employer_Demand"] * weights["Employer_Demand"]
        + result["Skill_Gap"] * weights["Skill_Gap"]
        + result["Training_Access"] * weights["Training_Access"]
        + result["Demand_Momentum"] * weights["Demand_Momentum"]
    ).round(2)

    result["Priority_Level"] = np.select(
        [
            result["Priority_Score"] >= 75,
            result["Priority_Score"] >= 50
        ],
        ["High", "Medium"],
        default="Low"
    )

    result["Recommendation"] = np.select(
        [
            (result["Priority_Level"] == "High")
            & (result["Training_Capacity"] < 60),

            result["Priority_Level"] == "High",
            result["Priority_Level"] == "Medium"
        ],
        [
            "Assess additional training capacity and employer partnerships",
            "Prioritize targeted training and employer partnerships",
            "Review skill gaps and improve training alignment"
        ],
        default="Monitor demand and review evidence before expanding training"
    )

    return make_unique_columns(result)


def show_table(df, columns=None):
    """
    Display a table with unique columns only.
    """
    safe_df = make_unique_columns(df)

    if columns is not None:
        # Preserve the requested order and avoid repeated column names.
        columns = list(dict.fromkeys(columns))
        columns = [c for c in columns if c in safe_df.columns]
        safe_df = safe_df.loc[:, columns]

    # Final duplicate-column protection.
    safe_df = safe_df.loc[:, ~safe_df.columns.duplicated()]

    st.dataframe(
        safe_df,
        use_container_width=True,
        hide_index=True
    )


def build_excel_report(df):
    """
    Create an Excel report in memory.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        make_unique_columns(df).to_excel(
            writer,
            sheet_name="Priority Report",
            index=False
        )

    output.seek(0)
    return output.getvalue()


# ------------------------------------------------------------
# 3. Application header
# ------------------------------------------------------------

st.title("📊 K-SIWAP")
st.subheader(
    "Module 4: District-Level Skill Planning and Recommendations"
)

st.caption(
    "Karnataka Skill Intelligence & Workforce Analytics Platform"
)

st.info(
    "Demo data is illustrative only. Replace it with verified data "
    "before using results for actual district-level planning."
)


# ------------------------------------------------------------
# 4. Load data
# ------------------------------------------------------------

if DATA_FILE.exists():
    try:
        raw_data = pd.read_csv(DATA_FILE)
        data_source = f"Loaded data from {DATA_FILE}"
    except Exception as error:
        st.warning(
            f"Could not load {DATA_FILE}. Using sample data. "
            f"Details: {error}"
        )
        raw_data = SAMPLE_DATA.copy()
        data_source = "Sample demo data"
else:
    raw_data = SAMPLE_DATA.copy()
    data_source = "Sample demo data"

try:
    data = prepare_data(raw_data)
except ValueError as error:
    st.error(f"Data validation failed: {error}")
    st.markdown("Use this sample CSV structure:")
    show_table(SAMPLE_DATA)
    st.stop()

st.caption(f"Data source: {data_source}")


# ------------------------------------------------------------
# 5. Sidebar settings
# ------------------------------------------------------------

st.sidebar.title("⚙️ Planning Settings")
st.sidebar.subheader("Priority Score Weights")

w_demand = st.sidebar.slider(
    "Employer demand (%)",
    min_value=0,
    max_value=100,
    value=40
)

w_gap = st.sidebar.slider(
    "Skill gap (%)",
    min_value=0,
    max_value=100,
    value=30
)

w_access = st.sidebar.slider(
    "Training access (%)",
    min_value=0,
    max_value=100,
    value=20
)

w_momentum = st.sidebar.slider(
    "Demand momentum (%)",
    min_value=0,
    max_value=100,
    value=10
)

weight_total = w_demand + w_gap + w_access + w_momentum

if weight_total == 0:
    st.sidebar.error("At least one weight must be greater than zero.")
    st.stop()

weights = {
    "Employer_Demand": w_demand / weight_total,
    "Skill_Gap": w_gap / weight_total,
    "Training_Access": w_access / weight_total,
    "Demand_Momentum": w_momentum / weight_total
}

st.sidebar.caption(
    f"Weights are normalized automatically. Total entered: {weight_total}%."
)

st.sidebar.divider()
st.sidebar.subheader("District Filter")

district_options = sorted(data["District"].unique().tolist())

selected_districts = st.sidebar.multiselect(
    "Select districts",
    options=district_options,
    default=district_options
)

# Calculate scores for the full dataset.
scored_data = calculate_priorities(data, weights)

# Apply the district filter.
filtered = scored_data[
    scored_data["District"].isin(selected_districts)
].copy()

if filtered.empty:
    st.warning("Select at least one district in the sidebar.")
    st.stop()


# ------------------------------------------------------------
# 6. Main dashboard metrics
# ------------------------------------------------------------

st.header("District Planning Dashboard")

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "District-Sector Records",
    f"{len(filtered)}"
)

metric2.metric(
    "High Priority Records",
    f"{int((filtered['Priority_Level'] == 'High').sum())}"
)

metric3.metric(
    "Average Priority Score",
    f"{filtered['Priority_Score'].mean():.1f}/100"
)

metric4.metric(
    "Average Evidence Confidence",
    f"{filtered['Evidence_Confidence'].mean():.1f}/100"
)


# ------------------------------------------------------------
# 7. Dashboard tabs
# ------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "District Comparison",
    "Recommendations",
    "Evidence & Skill Indicators",
    "Upload & Export"
])


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab1:
    st.header("Priority Overview")

    chart_data = filtered.sort_values(
        "Priority_Score",
        ascending=False
    )

    fig = px.bar(
        chart_data,
        x="District",
        y="Priority_Score",
        color="Priority_Level",
        hover_data=["Sector", "Employer_Demand", "Skill_Gap"],
        title="District-Sector Priority Scores",
        range_y=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Priority Ranking")

    show_table(
        chart_data,
        [
            "District",
            "Sector",
            "Employer_Demand",
            "Skill_Gap",
            "Training_Access",
            "Demand_Momentum",
            "Priority_Score",
            "Priority_Level"
        ]
    )


# ============================================================
# TAB 2: DISTRICT COMPARISON
# ============================================================

with tab2:
    st.header("Compare District Indicators")

    available_metrics = [
        "Employer_Demand",
        "Skill_Gap",
        "Training_Access",
        "Demand_Momentum",
        "Training_Capacity",
        "Evidence_Confidence",
        "Priority_Score"
    ]

    chosen_metrics = st.multiselect(
        "Choose indicators to compare",
        options=available_metrics,
        default=[
            "Employer_Demand",
            "Skill_Gap",
            "Priority_Score"
        ]
    )

    if chosen_metrics:
        comparison_data = filtered[
            ["District", "Sector"] + chosen_metrics
        ].copy()

        long_data = comparison_data.melt(
            id_vars=["District", "Sector"],
            value_vars=chosen_metrics,
            var_name="Indicator",
            value_name="Score"
        )

        comparison_fig = px.bar(
            long_data,
            x="District",
            y="Score",
            color="Indicator",
            barmode="group",
            title="District Indicator Comparison",
            range_y=[0, 100],
            hover_data=["Sector"]
        )

        st.plotly_chart(
            comparison_fig,
            use_container_width=True
        )

        st.subheader("Comparison Data")
        show_table(comparison_data)

    else:
        st.info("Select at least one indicator to compare.")


# ============================================================
# TAB 3: RECOMMENDATIONS
# ============================================================

with tab3:
    st.header("District-Level Recommendations")

    show_table(
        filtered.sort_values(
            "Priority_Score",
            ascending=False
        ),
        [
            "District",
            "Sector",
            "Priority_Score",
            "Priority_Level",
            "Training_Capacity",
            "Evidence_Confidence",
            "Recommendation"
        ]
    )

    st.divider()
    st.subheader("Why is this record prioritized?")

    record_options = filtered.index.tolist()

    selected_index = st.selectbox(
        "Select a district-sector record",
        options=record_options,
        format_func=lambda index: (
            f"{filtered.loc[index, 'District']} — "
            f"{filtered.loc[index, 'Sector']}"
        )
    )

    selected_record = filtered.loc[selected_index]

    a, b, c = st.columns(3)

    a.metric(
        "Priority Score",
        f"{selected_record['Priority_Score']:.2f}/100"
    )

    b.metric(
        "Priority Level",
        selected_record["Priority_Level"]
    )

    c.metric(
        "Evidence Confidence",
        f"{selected_record['Evidence_Confidence']:.0f}/100"
    )

    st.write("**Recommendation:**")
    st.write(selected_record["Recommendation"])

    st.write("**Weighted score breakdown:**")

    contribution_rows = []

    for indicator, weight in weights.items():
        contribution_rows.append({
            "Indicator": indicator,
            "Raw Score": selected_record[indicator],
            "Weight (%)": round(weight * 100, 1),
            "Weighted Contribution": round(
                selected_record[indicator] * weight, 2
            )
        })

    contribution_df = pd.DataFrame(contribution_rows)
    show_table(contribution_df)

    st.caption(
        "Priority weights are configurable demo assumptions, not official "
        "government policy weights."
    )


# ============================================================
# TAB 4: EVIDENCE & SKILL INDICATORS
# ============================================================

with tab4:
    st.header("Evidence Confidence and Skill Indicators")

    indicator = st.selectbox(
        "Select an indicator",
        options=[
            "Employer_Demand",
            "Skill_Gap",
            "Training_Access",
            "Demand_Momentum",
            "Training_Capacity",
            "Evidence_Confidence"
        ],
        format_func=lambda value: value.replace("_", " ")
    )

    indicator_data = filtered.sort_values(
        indicator,
        ascending=False
    )

    indicator_fig = px.bar(
        indicator_data,
        x="District",
        y=indicator,
        color="Sector",
        hover_data=["Evidence_Confidence"],
        title=f"{indicator.replace('_', ' ')} by District",
        range_y=[0, 100]
    )

    st.plotly_chart(
        indicator_fig,
        use_container_width=True
    )

    st.subheader("Evidence Confidence Table")

    show_table(
        filtered,
        [
            "District",
            "Sector",
            "Evidence_Confidence",
            "Employer_Demand",
            "Skill_Gap",
            "Priority_Score"
        ]
    )

    st.markdown("### How to interpret Evidence Confidence")

    st.write(
        "- **80–100:** Higher confidence in the supplied evidence score."
    )
    st.write(
        "- **50–79:** Moderate confidence; additional verification may help."
    )
    st.write(
        "- **0–49:** Lower confidence; verify source data before acting."
    )

    st.warning(
        "These confidence bands are illustrative. Evidence confidence "
        "must be calculated from actual source quality, recency, coverage, "
        "and completeness; it is not the same as model accuracy."
    )


# ============================================================
# TAB 5: UPLOAD & EXPORT
# ============================================================

with tab5:
    st.header("Upload District Data")

    st.write(
        "Upload a CSV containing the required district and sector "
        "indicators. Optional columns are Training_Capacity and "
        "Evidence_Confidence."
    )

    st.markdown("**Required columns:**")
    st.code(
        "District, Sector, Employer_Demand, Skill_Gap, "
        "Training_Access, Demand_Momentum"
    )

    uploaded_file = st.file_uploader(
        "Upload district data CSV",
        type=["csv"],
        key="district_csv_upload"
    )

    if uploaded_file is not None:
        try:
            uploaded_raw = pd.read_csv(uploaded_file)
            uploaded_data = prepare_data(uploaded_raw)

            uploaded_scored = calculate_priorities(
                uploaded_data,
                weights
            )

            st.success("CSV uploaded and validated successfully.")

            st.subheader("Uploaded Data Preview")
            show_table(uploaded_scored.head(50))

            st.download_button(
                "Download uploaded data with priority scores",
                data=uploaded_scored.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="KSIWAP_uploaded_priority_results.csv",
                mime="text/csv"
            )

        except Exception as error:
            st.error(f"Could not process the uploaded CSV: {error}")

    st.divider()
    st.subheader("Export Current Dashboard Results")

    export_columns = [
        "District",
        "Sector",
        "Employer_Demand",
        "Skill_Gap",
        "Training_Access",
        "Demand_Momentum",
        "Training_Capacity",
        "Evidence_Confidence",
        "Priority_Score",
        "Priority_Level",
        "Recommendation"
    ]

    export_columns = [
        col for col in export_columns if col in filtered.columns
    ]

    export_df = make_unique_columns(
        filtered.loc[:, export_columns].copy()
    ).sort_values("Priority_Score", ascending=False)

    csv_bytes = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Priority Report (CSV)",
        data=csv_bytes,
        file_name="KSIWAP_district_priority_report.csv",
        mime="text/csv"
    )

    try:
        excel_bytes = build_excel_report(export_df)

        st.download_button(
            "📥 Download Priority Report (Excel)",
            data=excel_bytes,
            file_name="KSIWAP_district_priority_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
    except Exception as error:
        st.warning(f"Excel export is unavailable: {error}")

    st.download_button(
        "📥 Download Sample Data Template",
        data=SAMPLE_DATA.to_csv(index=False).encode("utf-8"),
        file_name="KSIWAP_sample_data_template.csv",
        mime="text/csv"
    )


# ------------------------------------------------------------
# 8. Footer
# ------------------------------------------------------------

st.divider()

st.caption(
    "K-SIWAP | Module 4 | District-Level Skill Planning. "
    "Validate data sources, dates, definitions, and geographic coverage "
    "before making real-world planning decisions."
)
