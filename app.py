
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# K-SIWAP: Module 4
# District-Level Skill Planning and Recommendations
# --------------------------------------------------

st.set_page_config(
    page_title="K-SIWAP | District Skill Planning",
    page_icon="📊",
    layout="wide"
)

st.title("K-SIWAP")
st.subheader("Module 4: District-Level Skill Planning and Recommendations")

st.info(
    "Demo application: the sample values below are illustrative, "
    "not official Karnataka government statistics."
)

# --------------------------------------------------
# 1. Sample data
# --------------------------------------------------

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "district_data.csv"

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
        "IT", "Manufacturing", "Manufacturing",
        "Logistics", "Healthcare", "IT"
    ],
    "Employer_Demand": [90, 78, 70, 75, 68, 82],
    "Skill_Gap": [65, 72, 80, 60, 75, 68],
    "Training_Access": [85, 70, 62, 72, 55, 76],
    "Demand_Momentum": [88, 72, 68, 80, 74, 79],
    "Training_Capacity": [80, 65, 60, 70, 50, 72],
    "Evidence_Confidence": [90, 80, 75, 78, 65, 82]
})

# Allow the app to run even if the data folder/file is absent.
if DATA_FILE.exists():
    try:
        data = pd.read_csv(DATA_FILE)
    except Exception as exc:
        st.warning(f"Could not read the saved CSV. Using demo data. Details: {exc}")
        data = SAMPLE_DATA.copy()
else:
    data = SAMPLE_DATA.copy()

# --------------------------------------------------
# 2. Validate and normalize columns
# --------------------------------------------------

required_columns = [
    "District",
    "Sector",
    "Employer_Demand",
    "Skill_Gap",
    "Training_Access",
    "Demand_Momentum"
]

missing_columns = [
    col for col in required_columns if col not in data.columns
]

if missing_columns:
    st.error(
        "Your CSV is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.markdown("Use the sample CSV template shown below.")
    st.dataframe(SAMPLE_DATA, use_container_width=True)
    st.stop()

data["District"] = data["District"].fillna("Unknown").astype(str)
data["Sector"] = data["Sector"].fillna("Unknown").astype(str)

numeric_columns = [
    "Employer_Demand",
    "Skill_Gap",
    "Training_Access",
    "Demand_Momentum"
]

for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data[numeric_columns] = data[numeric_columns].fillna(0)
data[numeric_columns] = data[numeric_columns].clip(0, 100)

if "Training_Capacity" not in data.columns:
    data["Training_Capacity"] = 50

if "Evidence_Confidence" not in data.columns:
    data["Evidence_Confidence"] = 50

for col in ["Training_Capacity", "Evidence_Confidence"]:
    data[col] = pd.to_numeric(data[col], errors="coerce")
    data[col] = data[col].fillna(0).clip(0, 100)

# --------------------------------------------------
# 3. Sidebar: adjustable priority weights
# --------------------------------------------------

st.sidebar.header("Priority Score Settings")
st.sidebar.caption("Adjust weights for your planning scenario.")

w_demand = st.sidebar.slider(
    "Employer demand (%)", 0, 100, 40
)
w_gap = st.sidebar.slider(
    "Skill gap (%)", 0, 100, 30
)
w_access = st.sidebar.slider(
    "Training access (%)", 0, 100, 20
)
w_momentum = st.sidebar.slider(
    "Demand momentum (%)", 0, 100, 10
)

weight_total = w_demand + w_gap + w_access + w_momentum

if weight_total == 0:
    st.sidebar.error("At least one weight must be greater than zero.")
    st.stop()

st.sidebar.write(f"Total weight: {weight_total}%")

# --------------------------------------------------
# 4. Calculate priority score
# --------------------------------------------------

# Normalize weights so their total is 100%.
weights = {
    "Employer_Demand": w_demand / weight_total,
    "Skill_Gap": w_gap / weight_total,
    "Training_Access": w_access / weight_total,
    "Demand_Momentum": w_momentum / weight_total
}

data["Priority_Score"] = (
    data["Employer_Demand"] * weights["Employer_Demand"]
    + data["Skill_Gap"] * weights["Skill_Gap"]
    + data["Training_Access"] * weights["Training_Access"]
    + data["Demand_Momentum"] * weights["Demand_Momentum"]
).round(2)

def priority_label(score):
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    return "Low"

data["Priority_Level"] = data["Priority_Score"].apply(priority_label)

data["Recommendation"] = np.select(
    [
        (data["Priority_Level"] == "High")
        & (data["Training_Capacity"] < 60),

        data["Priority_Level"] == "High",

        data["Priority_Level"] == "Medium",

        data["Priority_Level"] == "Low"
    ],
    [
        "High priority: assess additional training capacity",
        "Prioritize targeted training and employer partnerships",
        "Review skill gaps and strengthen training alignment",
        "Monitor demand before expanding training"
    ],
    default="Review the available evidence"
)

# --------------------------------------------------
# 5. Dashboard filters
# --------------------------------------------------

st.sidebar.header("District Filters")

district_options = sorted(data["District"].unique().tolist())

selected_districts = st.sidebar.multiselect(
    "Select districts",
    options=district_options,
    default=district_options
)

filtered = data[data["District"].isin(selected_districts)].copy()

if filtered.empty:
    st.warning("Select at least one district from the sidebar.")
    st.stop()

# --------------------------------------------------
# 6. Summary metrics
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("District-Sector Records", len(filtered))
col2.metric("High Priority Records", int((filtered["Priority_Level"] == "High").sum()))
col3.metric("Average Priority Score", f"{filtered['Priority_Score'].mean():.1f}/100")
col4.metric("Average Evidence Confidence", f"{filtered['Evidence_Confidence'].mean():.1f}/100")

# --------------------------------------------------
# 7. Tabs
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "District Comparison",
    "Recommendations",
    "Skill Indicators",
    "Upload & Export"
])

with tab1:
    st.header("District Skill Planning Overview")

    chart = px.bar(
        filtered.sort_values("Priority_Score", ascending=False),
        x="District",
        y="Priority_Score",
        color="Priority_Level",
        hover_data=["Sector", "Employer_Demand", "Skill_Gap"],
        title="District-Sector Priority Scores",
        range_y=[0, 100]
    )
    st.plotly_chart(chart, use_container_width=True)

    st.subheader("Priority Ranking")
    st.dataframe(
        filtered.sort_values("Priority_Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.header("Compare Districts")

    compare_metrics = st.multiselect(
        "Choose indicators",
        options=[
            "Employer_Demand",
            "Skill_Gap",
            "Training_Access",
            "Demand_Momentum",
            "Training_Capacity",
            "Priority_Score"
        ],
        default=["Employer_Demand", "Skill_Gap", "Priority_Score"]
    )

    if compare_metrics:
        comparison = filtered.melt(
            id_vars=["District", "Sector"],
            value_vars=compare_metrics,
            var_name="Indicator",
            value_name="Score"
        )

        fig = px.bar(
            comparison,
            x="District",
            y="Score",
            color="Indicator",
            barmode="group",
            facet_col="Indicator",
            facet_col_wrap=2,
            title="District Indicator Comparison",
            range_y=[0, 100]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "If a district contains multiple sectors, each district-sector record "
        "appears separately in the underlying data."
    )

with tab3:
    st.header("District-Level Recommendations")

    st.dataframe(
        filtered[
            [
                "District",
                "Sector",
                "Priority_Score",
                "Priority_Level",
                "Training_Capacity",
                "Recommendation",
                "Evidence_Confidence"
            ]
        ].sort_values("Priority_Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Why was this record prioritized?")

    selected_record = st.selectbox(
        "Choose a district-sector record",
        filtered.index.tolist(),
        format_func=lambda i: (
            f"{data.loc[i, 'District']} — {data.loc[i, 'Sector']}"
        )
    )

    record = data.loc[selected_record]

    st.write(f"**Priority score:** {record['Priority_Score']}/100")
    st.write(f"**Priority level:** {record['Priority_Level']}")
    st.write("**Score contributions:**")

    contribution_rows = []
    for name, weight in weights.items():
        contribution_rows.append({
            "Indicator": name,
            "Raw Score": record[name],
            "Normalized Weight (%)": round(weight * 100, 1),
            "Weighted Contribution": round(record[name] * weight, 2)
        })

    st.dataframe(
        pd.DataFrame(contribution_rows),
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "These recommendations are rule-based planning suggestions. "
        "They are not verified hiring forecasts or official policy decisions."
    )

with tab4:
    st.header("Skill and Training Indicators")

    indicator = st.selectbox(
        "Select indicator",
        [
            "Employer_Demand",
            "Skill_Gap",
            "Training_Access",
            "Demand_Momentum",
            "Training_Capacity",
            "Evidence_Confidence"
        ]
    )

    fig = px.bar(
        filtered.sort_values(indicator, ascending=False),
        x="District",
        y=indicator,
        color="Sector",
        title=f"{indicator.replace('_', ' ')} by District",
        range_y=[0, 100]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        filtered[
            [
                "District", "Sector", indicator,
                "Evidence_Confidence", "Recommendation"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

with tab5:
    st.header("Upload Your Data and Export Results")

    st.markdown("### Required CSV columns")
    st.dataframe(
        SAMPLE_DATA.head(3),
        use_container_width=True,
        hide_index=True
    )

    uploaded_file = st.file_uploader(
        "Upload a district planning CSV",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            upload_df = pd.read_csv(uploaded_file)
            missing = [
                c for c in required_columns if c not in upload_df.columns
            ]

            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                st.success("CSV structure looks valid.")
                st.dataframe(upload_df.head(20), use_container_width=True)
                st.download_button(
                    "Download uploaded CSV copy",
                    data=upload_df.to_csv(index=False).encode("utf-8"),
                    file_name="uploaded_district_data.csv",
                    mime="text/csv"
                )
        except Exception as exc:
            st.error(f"Could not process this CSV: {exc}")

    st.divider()
    st.subheader("Export current priority results")

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

    export_df = filtered[export_columns].sort_values(
        "Priority_Score", ascending=False
    )

    st.download_button(
        "Download priority report (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="KSIWAP_district_priority_report.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download data template (CSV)",
        data=SAMPLE_DATA.to_csv(index=False).encode("utf-8"),
        file_name="KSIWAP_district_data_template.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# 8. Footer
# --------------------------------------------------

st.divider()
st.caption(
    "K-SIWAP | Module 4 | Demo scoring weights are configurable. "
    "Validate data sources, dates, geographic coverage, and definitions "
    "before using results for real-world planning."
)
