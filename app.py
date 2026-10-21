import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="District Skill Intelligence Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #F5F7FA;
    color: #1F2937;
}

[data-testid="stSidebar"] {
    background-color: #0F2D46;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
    font-weight: 500;
}

[data-testid="stSidebar"] div[role="radiogroup"] label,
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="popover"] * {
    color: #FFFFFF !important;
}

.main-title {
    font-size: 30px;
    font-weight: 750;
    color: #0F2A43;
}

.subtitle {
    color: #4B5A6B;
    font-size: 14px;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #123B5D;
}

.kpi {
    background: #FFFFFF;
    border: 1px solid #D8E0EA;
    border-radius: 12px;
    padding: 18px;
    min-height: 120px;
    color: #1F2937;
}

.kpi-label {
    color: #55677A;
    font-size: 13px;
}

.kpi-value {
    color: #0F2A43;
    font-size: 28px;
    font-weight: 750;
}

.kpi-note {
    color: #1F7A4D;
    font-size: 12px;
}

div[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 15px;
    border: 1px solid #D8E0EA;
    border-radius: 12px;
    color: #1F2937;
}

div[data-testid="stMetricLabel"] p {
    color: #55677A !important;
}

div[data-testid="stMetricValue"] {
    color: #0F2A43 !important;
}

[data-testid="stDataFrame"],
[data-testid="stDataFrame"] * {
    color: #1F2937 !important;
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color: #4B5A6B !important;
}

.stButton button {
    border-radius: 8px;
    background-color: #1F6FEB;
    color: #FFFFFF;
    border: none;
}

.stButton button:hover {
    background-color: #1858C4;
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. LOAD AND CLEAN CSV
# =====================================================

CSV_FILE = "district_skills.csv"

try:
    skill_data = None

    # Automatically try comma, semicolon and tab separators
    for separator in [",", ";", "\t"]:
        try:
            temp_df = pd.read_csv(
                CSV_FILE,
                sep=separator,
                encoding="utf-8-sig",
                skip_blank_lines=True
            )

            if len(temp_df.columns) >= 5:
                skill_data = temp_df
                break

        except Exception:
            continue

    if skill_data is None:
        st.error(
            "Could not read district_skills.csv. "
            "Please check that it is a valid CSV file."
        )
        st.stop()

    # Clean column names
    skill_data.columns = (
        skill_data.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Show detected columns in sidebar for troubleshooting
    with st.sidebar:
        st.caption("CSV columns detected:")
        st.write(", ".join(skill_data.columns))

    # Map common alternative column names
    column_aliases = {
        "district_name": "district",
        "districts": "district",
        "sector_name": "sector",
        "sectors": "sector",
        "skill_name": "skill",
        "skills": "skill",
        "demand": "demand_score",
        "demand_index": "demand_score",
        "gap": "gap_score",
        "gap_index": "gap_score",
        "training": "training_access",
        "training_score": "training_access",
        "momentum_score": "momentum",
        "year": "period",
        "data_source": "source"
    }

    skill_data = skill_data.rename(columns=column_aliases)

    required_columns = [
        "district", "sector", "skill",
        "demand_score", "gap_score",
        "training_access", "momentum",
        "period", "source"
    ]

    # Create missing columns automatically
    defaults = {
        "district": "Unknown District",
        "sector": "General",
        "skill": "General Skill",
        "demand_score": 50,
        "gap_score": 50,
        "training_access": 50,
        "momentum": 50,
        "period": "2025",
        "source": "Demo data"
    }

    missing_columns = []

    for column in required_columns:
        if column not in skill_data.columns:
            skill_data[column] = defaults[column]
            missing_columns.append(column)

    if missing_columns:
        st.warning(
            "These columns were missing and were filled with demo values: "
            f"{', '.join(missing_columns)}"
        )

    # Clean text columns
    for column in ["district", "sector", "skill", "period", "source"]:
        skill_data[column] = (
            skill_data[column]
            .astype(str)
            .str.strip()
        )

    # Clean numeric columns
    numeric_columns = [
        "demand_score", "gap_score",
        "training_access", "momentum"
    ]

    for column in numeric_columns:
        skill_data[column] = pd.to_numeric(
            skill_data[column],
            errors="coerce"
        ).fillna(50)

    for column in numeric_columns:
        skill_data[column] = skill_data[column].clip(0, 100)

except FileNotFoundError:
    st.error(
        "Could not find `district_skills.csv`. "
        "Please place it in the same folder as this app."
    )
    st.stop()

# =====================================================
# 4. CREATE SUMMARY DATA FROM CSV
# =====================================================

district_summary = (
    skill_data
    .groupby("district", as_index=False)
    .agg(
        Average_Demand=("demand_score", "mean"),
        Average_Gap=("gap_score", "mean"),
        Average_Training_Access=("training_access", "mean"),
        Average_Momentum=("momentum", "mean"),
        Skill_Records=("skill", "count")
    )
    .round(1)
)

district_summary = district_summary.rename(columns={
    "district": "District",
    "Average_Demand": "Average Demand Score",
    "Average_Gap": "Average Skill Gap",
    "Average_Training_Access": "Average Training Access",
    "Average_Momentum": "Average Momentum",
    "Skill_Records": "Skill Records"
})

sector_summary = (
    skill_data
    .groupby("sector", as_index=False)
    .agg(
        Average_Demand=("demand_score", "mean"),
        Average_Gap=("gap_score", "mean"),
        Average_Training_Access=("training_access", "mean"),
        Average_Momentum=("momentum", "mean")
    )
    .round(1)
)

sector_summary = sector_summary.rename(columns={
    "sector": "Sector",
    "Average_Demand": "Average Demand Score",
    "Average_Gap": "Average Skill Gap",
    "Average_Training_Access": "Average Training Access",
    "Average_Momentum": "Average Momentum"
})

skill_summary = (
    skill_data
    .groupby(["sector", "skill"], as_index=False)
    .agg(
        Average_Demand=("demand_score", "mean"),
        Average_Gap=("gap_score", "mean"),
        Average_Training_Access=("training_access", "mean"),
        Average_Momentum=("momentum", "mean")
    )
    .round(1)
)

skill_summary = skill_summary.rename(columns={
    "sector": "Sector",
    "skill": "Skill",
    "Average_Demand": "Average Demand Score",
    "Average_Gap": "Average Skill Gap",
    "Average_Training_Access": "Average Training Access",
    "Average_Momentum": "Average Momentum"
})

# Simulated district employment indicators
district_employment = district_summary.copy()
district_employment["Employed"] = (
    district_employment["Average Demand Score"] * 80
).astype(int)

district_employment["Unemployed"] = (
    district_employment["Average Skill Gap"] * 45
).astype(int)

district_employment["Job Openings"] = (
    district_employment["Average Demand Score"] * 35
).astype(int)

district_employment["Training Enrolment"] = (
    district_employment["Average Training Access"] * 25
).astype(int)

district_employment = district_employment[[
    "District", "Employed", "Unemployed",
    "Job Openings", "Training Enrolment"
]]

# Simulated training institute data
institute_templates = [
    "District Skill Centre",
    "Government ITI",
    "Technical Training Institute",
    "Advanced Skills Academy",
    "Community Training Centre"
]

np.random.seed(42)

institute_rows = []

for index, row in district_summary.iterrows():
    district = row["District"]
    base_enrolment = int(row["Average Training Access"] * 8) + 100

    for institute in institute_templates:
        enrolled = max(
            50,
            base_enrolment + np.random.randint(-30, 50)
        )
        skilled = int(enrolled * np.random.uniform(0.60, 0.90))
        placed = int(skilled * np.random.uniform(0.45, 0.85))

        institute_rows.append({
            "Institute": institute,
            "District": district,
            "Enrolled": enrolled,
            "Skilled": skilled,
            "Placed": placed
        })

institutes = pd.DataFrame(institute_rows)

# Simulated company data
company_templates = [
    "ABC Technologies",
    "Digital Solutions Pvt Ltd",
    "Karnataka Manufacturing Ltd.",
    "Precision Engineering Works",
    "HealthFirst Services",
    "SolarWorks India"
]

company_rows = []

for index, row in skill_data.iterrows():
    company_rows.append({
        "Company": np.random.choice(company_templates),
        "Sector": row["sector"],
        "District": row["district"],
        "Skill Required": row["skill"],
        "Vacancies": int(
            row["demand_score"] * np.random.uniform(0.15, 0.45)
        ),
        "Participated in Job Fair": np.random.choice(["Yes", "No"]),
        "Students Hired": int(
            row["demand_score"] * np.random.uniform(0.05, 0.25)
        )
    })

companies = pd.DataFrame(company_rows)

# Simulated job fair data
job_fair_rows = []

for index, row in district_summary.iterrows():
    district = row["District"]

    fairs = np.random.randint(3, 10)
    students_participated = int(
        row["Average Momentum"] * np.random.uniform(8, 15)
    )
    students_placed = int(
        students_participated * np.random.uniform(0.35, 0.70)
    )
    companies_participated = np.random.randint(12, 45)
    companies_hired = int(
        companies_participated * np.random.uniform(0.45, 0.85)
    )

    job_fair_rows.append({
        "District": district,
        "Fairs Conducted": fairs,
        "Students Participated": students_participated,
        "Students Placed": students_placed,
        "Companies Participated": companies_participated,
        "Companies Hired": companies_hired
    })

job_fairs = pd.DataFrame(job_fair_rows)

# =====================================================
# 5. SESSION STATE
# =====================================================

defaults = {
    "logged_in": False,
    "username": "",
    "role": "District Admin - Labour & Skill",
    "users": {},
    "plans": [],
    "executions": [],
    "activities": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =====================================================
# 6. LOGIN AND REGISTRATION
# =====================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">District Skill Intelligence Portal</div>',
        unsafe_allow_html=True
    )
    st.write("Labour, Employment and Skill Development Administration")
    st.divider()

    login_tab, register_tab = st.tabs(["Login", "Create Account"])

    with register_tab:
        st.subheader("Create your account")

        reg_name = st.text_input("Username", key="reg_name")
        reg_password = st.text_input(
            "Password", type="password", key="reg_password"
        )
        reg_role = st.selectbox(
            "Select role",
            [
                "District Admin - Labour & Skill",
                "State Admin - Labour & Skill",
                "Training Institute",
                "Job Fair Company"
            ],
            key="reg_role"
        )

        if st.button("Register", key="register_button"):
            if not reg_name.strip() or not reg_password:
                st.error("Enter a username and password.")
            elif reg_name in st.session_state.users:
                st.error("Username already exists.")
            else:
                st.session_state.users[reg_name] = {
                    "password": reg_password,
                    "role": reg_role
                }
                st.success("Account created. Please open the Login tab.")

    with login_tab:
        st.subheader("Sign in")

        login_name = st.text_input("Username", key="login_name")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )

        if st.button("Login", key="login_button"):
            account = st.session_state.users.get(login_name)

            if account and account["password"] == login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_name
                st.session_state.role = account["role"]
                st.rerun()
            else:
                st.error(
                    "Account not found or password incorrect. "
                    "Register first if needed."
                )

    st.info(
        "Demo version: accounts are stored only in the current session. "
        "A production portal needs secure authentication and a database."
    )
    st.stop()

# =====================================================
# 7. SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("## 🏛️ SKILL INTELLIGENCE")
    st.caption("LABOUR & SKILL PORTAL")
    st.divider()

    st.write("SIGNED IN AS")
    st.markdown(f"**{st.session_state.username}**")
    st.caption(st.session_state.role)

    st.divider()

    page = st.selectbox(
        "Open page",
        [
            "Explore Dashboard",
            "Users",
            "District Admin Dashboard",
            "State Admin",
            "Training Institutes",
            "Job Fair Companies",
            "Analytics - AI Skill Planning",
            "Plans",
            "Executed",
            "Results"
        ],
        key="selected_page"
    )

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# =====================================================
# 8. SHARED HEADER AND HELPERS
# =====================================================

st.markdown(
    '<div class="main-title">District Labour & Skill Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Employment monitoring • Skill-gap analysis • '
    'Training coordination • Outcome tracking</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Signed in as {st.session_state.username} | "
    f"{st.session_state.role} | "
    f"{date.today().strftime('%d %b %Y')}"
)

st.divider()


def kpi(label, value, note="Generated from district_skills.csv"):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def page_title(title, description):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )
    st.caption(description)

# =====================================================
# 9. EXPLORE DASHBOARD
# =====================================================

if page == "Explore Dashboard":

    page_title(
        "Explore Dashboard",
        "Overview generated from your district_skills.csv dataset."
    )

    total_records = len(skill_data)
    total_districts = skill_data["district"].nunique()
    total_skills = skill_data["skill"].nunique()
    average_gap = round(skill_data["gap_score"].mean(), 1)

    a, b, c, d = st.columns(4)

    with a:
        kpi("CSV Records", f"{total_records:,}")

    with b:
        kpi("Districts Covered", total_districts)

    with c:
        kpi("Unique Skills", total_skills)

    with d:
        kpi("Average Skill Gap", average_gap)

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Average Demand and Skill Gap by District")

        district_chart = district_summary.set_index("District")[
            ["Average Demand Score", "Average Skill Gap"]
        ]

        st.bar_chart(district_chart)

    with right:
        st.subheader("Top Skills by Demand")

        top_skills = (
            skill_summary
            .sort_values("Average Demand Score", ascending=False)
            .head(10)
        )

        st.bar_chart(
            top_skills.set_index("Skill")["Average Demand Score"]
        )

    st.subheader("District Summary")
    st.dataframe(
        district_summary,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Raw CSV Records")
    st.dataframe(
        skill_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Recent Portal Activity")

    if st.session_state.activities:
        st.dataframe(
            pd.DataFrame(st.session_state.activities),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No activities recorded yet. Saved plans and execution updates "
            "will appear here."
        )

# =====================================================
# 10. USERS
# =====================================================

elif page == "Users":

    page_title(
        "Users & Access",
        "Review registered demo accounts and their assigned roles."
    )

    if st.session_state.users:
        user_rows = [
            {
                "Username": name,
                "Role": details["role"],
                "Account Status": "Registered"
            }
            for name, details in st.session_state.users.items()
        ]

        st.dataframe(
            pd.DataFrame(user_rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No registered accounts found in this session.")

    st.subheader("Role Responsibilities")

    roles = pd.DataFrame({
        "Role": [
            "District Admin - Labour & Skill",
            "State Admin - Labour & Skill",
            "Training Institute",
            "Job Fair Company"
        ],
        "Responsibility": [
            "Monitor district demand and coordinate skill plans",
            "Compare districts and review state-wide progress",
            "Track training, completion and placements",
            "Share vacancies and report hiring outcomes"
        ]
    })

    st.dataframe(roles, use_container_width=True, hide_index=True)

    st.warning(
        "This is not a secure user-management system. Role-based permissions "
        "and database-backed accounts must be added before deployment."
    )

# =====================================================
# 11. DISTRICT ADMIN DASHBOARD
# =====================================================

elif page == "District Admin Dashboard":

    page_title(
        "District Admin Dashboard",
        "Monitor district skill demand, gaps and training access."
    )

    selected_district = st.selectbox(
        "Select district",
        sorted(skill_data["district"].unique())
    )

    district_data = skill_data[
        skill_data["district"] == selected_district
    ]

    district_metrics = district_summary[
        district_summary["District"] == selected_district
    ].iloc[0]

    employment_row = district_employment[
        district_employment["District"] == selected_district
    ].iloc[0]

    fair_row = job_fairs[
        job_fairs["District"] == selected_district
    ].iloc[0]

    a, b, c, d = st.columns(4)

    with a:
        kpi(
            "Average Demand Score",
            district_metrics["Average Demand Score"]
        )

    with b:
        kpi(
            "Average Skill Gap",
            district_metrics["Average Skill Gap"]
        )

    with c:
        kpi(
            "Average Training Access",
            district_metrics["Average Training Access"]
        )

    with d:
        kpi(
            "Average Momentum",
            district_metrics["Average Momentum"]
        )

    st.subheader("Skill-wise Performance")

    skill_filter = st.multiselect(
        "Filter skills",
        sorted(district_data["skill"].unique()),
        default=sorted(district_data["skill"].unique())
    )

    filtered_district_data = district_data[
        district_data["skill"].isin(skill_filter)
    ]

    if filtered_district_data.empty:
        st.info("No matching skill records found.")
    else:
        skill_chart = (
            filtered_district_data
            .groupby("skill", as_index=False)[
                [
                    "demand_score", "gap_score",
                    "training_access", "momentum"
                ]
            ]
            .mean()
            .round(1)
            .set_index("skill")
        )

        st.bar_chart(skill_chart)

        st.dataframe(
            filtered_district_data,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Sector-wise Demand")

    district_sector_summary = (
        district_data
        .groupby("sector", as_index=False)["demand_score"]
        .mean()
        .round(1)
        .sort_values("demand_score", ascending=False)
    )

    st.bar_chart(
        district_sector_summary.set_index("sector")["demand_score"]
    )

    st.subheader("Employment and Training Indicators")

    a, b, c, d = st.columns(4)

    with a:
        kpi("Employed", f"{employment_row['Employed']:,}")

    with b:
        kpi("Unemployed", f"{employment_row['Unemployed']:,}")

    with c:
        kpi("Job Openings", f"{employment_row['Job Openings']:,}")

    with d:
        kpi(
            "Training Enrolment",
            f"{employment_row['Training Enrolment']:,}"
        )

    st.subheader("Job Fair Outcomes")

    a, b, c = st.columns(3)

    with a:
        kpi("Fairs Conducted", int(fair_row["Fairs Conducted"]))

    with b:
        kpi(
            "Students Participated",
            f"{int(fair_row['Students Participated']):,}"
        )

    with c:
        kpi(
            "Students Placed",
            f"{int(fair_row['Students Placed']):,}"
        )

    st.subheader("Companies and Openings")

    district_companies = companies[
        companies["District"] == selected_district
    ]

    st.dataframe(
        district_companies,
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# 12. STATE ADMIN
# =====================================================

elif page == "State Admin":

    page_title(
        "State Admin",
        "Compare districts and identify priority areas."
    )

    a, b, c = st.columns(3)

    with a:
        kpi("Districts Monitored", skill_data["district"].nunique())

    with b:
        kpi(
            "Highest Average Gap",
            district_summary["Average Skill Gap"].max()
        )

    with c:
        kpi(
            "Lowest Training Access",
            district_summary["Average Training Access"].min()
        )

    st.subheader("Compare Districts")

    indicator = st.selectbox(
        "Choose indicator",
        [
            "Average Demand Score",
            "Average Skill Gap",
            "Average Training Access",
            "Average Momentum"
        ]
    )

    comparison = district_summary.sort_values(
        indicator, ascending=False
    )

    st.bar_chart(comparison.set_index("District")[indicator])
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.subheader("Districts Requiring Attention")

    priority = district_summary.sort_values(
        "Average Skill Gap", ascending=False
    ).head(3)

    st.dataframe(
        priority[
            [
                "District", "Average Skill Gap",
                "Average Training Access", "Average Momentum"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Priority is calculated from the gap score in district_skills.csv. "
        "Use validated administrative data before making policy decisions."
    )

# =====================================================
# 13. TRAINING INSTITUTES
# =====================================================

elif page == "Training Institutes":

    page_title(
        "Training Institutes",
        "Monitor enrolment, skill completion and placement outcomes."
    )

    selected_district = st.selectbox(
        "Filter district",
        ["All Districts"] + sorted(skill_data["district"].unique())
    )

    institute_view = institutes.copy()

    if selected_district != "All Districts":
        institute_view = institute_view[
            institute_view["District"] == selected_district
        ]

    total_enrolled = institute_view["Enrolled"].sum()
    total_skilled = institute_view["Skilled"].sum()
    total_placed = institute_view["Placed"].sum()

    a, b, c = st.columns(3)

    with a:
        kpi("Students Enrolled", f"{total_enrolled:,}")

    with b:
        kpi("Students Skilled", f"{total_skilled:,}")

    with c:
        kpi("Students Placed", f"{total_placed:,}")

    if total_enrolled:
        st.metric(
            "Placement as % of Enrolment",
            f"{100 * total_placed / total_enrolled:.1f}%"
        )

    st.subheader("Institute Performance")
    st.dataframe(institute_view, use_container_width=True, hide_index=True)

    st.bar_chart(
        institute_view.set_index("Institute")[
            ["Enrolled", "Skilled", "Placed"]
        ]
    )

    st.subheader("Training Institute Rankings")

    ranked = institute_view.copy()
    ranked["Placement Rate (%)"] = (
        100 * ranked["Placed"] / ranked["Enrolled"]
    ).round(1)

    ranked = ranked.sort_values(
        "Placement Rate (%)", ascending=False
    )
    ranked.insert(0, "Rank", range(1, len(ranked) + 1))

    st.dataframe(ranked, use_container_width=True, hide_index=True)

# =====================================================
# 14. JOB FAIR COMPANIES
# =====================================================

elif page == "Job Fair Companies":

    page_title(
        "Job Fair Companies",
        "Track hiring demand, participation and recruitment results."
    )

    sector_filter = st.selectbox(
        "Sector",
        ["All Sectors"] + sorted(skill_data["sector"].unique())
    )

    company_view = companies.copy()

    if sector_filter != "All Sectors":
        company_view = company_view[
            company_view["Sector"] == sector_filter
        ]

    a, b, c = st.columns(3)

    with a:
        kpi("Companies Listed", company_view["Company"].nunique())

    with b:
        kpi("Vacancies Listed", f"{company_view['Vacancies'].sum():,}")

    with c:
        kpi("Students Hired", f"{company_view['Students Hired'].sum():,}")

    st.subheader("Company Register")
    st.dataframe(company_view, use_container_width=True, hide_index=True)

    st.subheader("Vacancies by Sector")

    sector_vacancies = (
        company_view
        .groupby("Sector", as_index=False)["Vacancies"]
        .sum()
    )

    st.bar_chart(
        sector_vacancies.set_index("Sector")["Vacancies"]
    )

    st.subheader("Job Fair Performance by District")

    st.dataframe(job_fairs, use_container_width=True, hide_index=True)

    st.bar_chart(
        job_fairs.set_index("District")[
            ["Companies Participated", "Companies Hired"]
        ]
    )

# =====================================================
# 15. ANALYTICS - AI SKILL PLANNING
# =====================================================

elif page == "Analytics - AI Skill Planning":

    page_title(
        "AI Skill Planning & Analytics",
        "Generate a preliminary skill-gap report from your CSV data."
    )

    selected_district = st.selectbox(
        "Planning district",
        sorted(skill_data["district"].unique()),
        key="planning_district"
    )

    planning_focus = st.selectbox(
        "Planning objective",
        [
            "Reduce unemployment",
            "Address skill gaps",
            "Focus on growing sectors",
            "Prepare for upcoming vacancies"
        ]
    )

    district_planning_data = skill_data[
        skill_data["district"] == selected_district
    ].copy()

    if district_planning_data.empty:
        st.warning("No records available for this district.")
    else:
        st.subheader("Skill Gap Report")

        planning_report = (
            district_planning_data
            .groupby(["sector", "skill"], as_index=False)[
                [
                    "demand_score", "gap_score",
                    "training_access", "momentum"
                ]
            ]
            .mean()
            .round(1)
            .sort_values("gap_score", ascending=False)
        )

        planning_report["Priority"] = planning_report["gap_score"].apply(
            lambda gap: "High" if gap >= 70
            else ("Medium" if gap >= 45 else "Monitor")
        )

        st.dataframe(
            planning_report,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            planning_report.set_index("skill")["gap_score"]
        )

        st.subheader("Generate Planning Recommendations")

        if st.button("Generate Recommendations", type="primary"):

            highest_gap = planning_report.iloc[0]

            st.success("Preliminary report generated.")

            st.markdown(f"**District:** {selected_district}")
            st.markdown(f"**Objective:** {planning_focus}")
            st.markdown(
                f"**Highest-gap skill:** {highest_gap['skill']}"
            )
            st.markdown(
                f"**Sector:** {highest_gap['sector']}"
            )
            st.markdown(
                f"**Average gap score:** {highest_gap['gap_score']}"
            )

            st.markdown("#### Suggested Actions")

            st.write(
                f"1. Assess training capacity for "
                f"{highest_gap['skill']} in {selected_district}."
            )
            st.write(
                "2. Contact employers and companies with vacancies "
                "matching this skill."
            )
            st.write(
                "3. Review institute placement performance before "
                "selecting training providers."
            )
            st.write(
                "4. Track enrolment, completion and placement outcomes "
                "after implementation."
            )

            st.warning(
                "These are rule-based planning suggestions generated from "
                "your CSV scores. They are not verified policy recommendations."
            )

# =====================================================
# 16. PLANS
# =====================================================

elif page == "Plans":

    page_title(
        "Skill Plans & Reports",
        "Create a plan, define targets and review saved planning records."
    )

    with st.form("create_plan_form"):
        plan_name = st.text_input(
            "Plan title",
            placeholder="Example: District Python Training Plan"
        )

        plan_district = st.selectbox(
            "District",
            sorted(skill_data["district"].unique())
        )

        district_skills = sorted(
            skill_data[
                skill_data["district"] == plan_district
            ]["skill"].unique()
        )

        plan_skill = st.selectbox(
            "Target skill",
            district_skills
        )

        target_students = st.number_input(
            "Target students to train",
            min_value=1,
            max_value=100000,
            value=100
        )

        training_institute = st.selectbox(
            "Proposed training institute",
            institute_templates
        )

        target_date = st.date_input("Target completion date")

        plan_notes = st.text_area(
            "Plan notes",
            placeholder="Describe the skill gap and planned actions."
        )

        save_plan = st.form_submit_button("Save Skill Plan")

    if save_plan:
        if not plan_name.strip():
            st.error("Please enter a plan title.")
        else:
            new_plan = {
                "Plan ID": f"PLAN-{len(st.session_state.plans) + 1:03}",
                "Plan Title": plan_name,
                "District": plan_district,
                "Skill": plan_skill,
                "Target Students": int(target_students),
                "Training Institute": training_institute,
                "Target Date": str(target_date),
                "Status": "Planned",
                "Notes": plan_notes
            }

            st.session_state.plans.append(new_plan)

            st.session_state.activities.append({
                "Date": str(date.today()),
                "Activity": f"Created plan: {plan_name}",
                "User": st.session_state.username
            })

            st.success("Skill plan saved for this session.")

    st.subheader("Saved Plans")

    if st.session_state.plans:
        st.dataframe(
            pd.DataFrame(st.session_state.plans),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Plans as CSV",
            pd.DataFrame(st.session_state.plans).to_csv(index=False),
            file_name="skill_plans.csv",
            mime="text/csv"
        )
    else:
        st.info("No plans saved yet. Create your first skill plan above.")

# =====================================================
# 17. EXECUTED
# =====================================================

elif page == "Executed":

    page_title(
        "Execution Tracking",
        "Record plan progress and outcomes."
    )

    if not st.session_state.plans:
        st.info(
            "Create a skill plan first, then track its execution here."
        )
    else:
        plan_options = [
            plan["Plan ID"] + " — " + plan["Plan Title"]
            for plan in st.session_state.plans
        ]

        chosen_plan = st.selectbox("Select skill plan", plan_options)

        selected_index = plan_options.index(chosen_plan)
        selected_plan_record = st.session_state.plans[selected_index]

        with st.form("execution_form"):
            execution_status = st.selectbox(
                "Execution status",
                ["Not Started", "In Progress", "Completed", "On Hold"]
            )

            actual_start = st.date_input(
                "Actual start date",
                value=date.today()
            )

            students_trained = st.number_input(
                "Students trained so far",
                min_value=0,
                max_value=int(selected_plan_record["Target Students"]),
                value=0
            )

            students_placed = st.number_input(
                "Students placed so far",
                min_value=0,
                max_value=int(selected_plan_record["Target Students"]),
                value=0
            )

            actual_spend = st.number_input(
                "Actual expenditure (INR)",
                min_value=0,
                value=0,
                step=1000
            )

            execution_notes = st.text_area("Execution notes")

            save_execution = st.form_submit_button(
                "Save Execution Update"
            )

        if save_execution:
            execution = {
                "Plan ID": selected_plan_record["Plan ID"],
                "Plan Title": selected_plan_record["Plan Title"],
                "District": selected_plan_record["District"],
                "Status": execution_status,
                "Actual Start": str(actual_start),
                "Students Trained": int(students_trained),
                "Students Placed": int(students_placed),
                "Actual Expenditure (INR)": int(actual_spend),
                "Notes": execution_notes
            }

            st.session_state.executions.append(execution)
            selected_plan_record["Status"] = execution_status

            st.session_state.activities.append({
                "Date": str(date.today()),
                "Activity": (
                    "Execution updated: "
                    f"{selected_plan_record['Plan Title']}"
                ),
                "User": st.session_state.username
            })

            st.success("Execution update saved.")

    st.subheader("Execution Register")

    if st.session_state.executions:
        st.dataframe(
            pd.DataFrame(st.session_state.executions),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Execution Report",
            pd.DataFrame(st.session_state.executions).to_csv(index=False),
            file_name="execution_report.csv",
            mime="text/csv"
        )
    else:
        st.info("No execution updates recorded yet.")

# =====================================================
# 18. RESULTS
# =====================================================

elif page == "Results":

    page_title(
        "Outcomes & Results",
        "Review training outputs, placements and skill-gap indicators."
    )

    if st.session_state.executions:
        result_data = pd.DataFrame(st.session_state.executions)

        target_students_total = sum(
            plan["Target Students"] for plan in st.session_state.plans
        )

        trained_total = int(result_data["Students Trained"].sum())
        placed_total = int(result_data["Students Placed"].sum())
        spend_total = int(
            result_data["Actual Expenditure (INR)"].sum()
        )

        a, b, c, d = st.columns(4)

        with a:
            kpi(
                "Planned Student Targets",
                f"{target_students_total:,}"
            )

        with b:
            kpi("Students Trained", f"{trained_total:,}")

        with c:
            kpi("Students Placed", f"{placed_total:,}")

        with d:
            kpi("Reported Expenditure", f"₹{spend_total:,}")

        st.subheader("Execution Outcomes")
        st.dataframe(result_data, use_container_width=True, hide_index=True)

        st.bar_chart(
            result_data.set_index("Plan Title")[
                ["Students Trained", "Students Placed"]
            ]
        )
    else:
        st.info(
            "No execution results are available yet. Create a plan, record "
            "an execution update, and return here to review outcomes."
        )

    st.subheader("Skill Gap by District")

    st.bar_chart(
        district_summary.set_index("District")["Average Skill Gap"]
    )

    st.subheader("Skill Demand by Skill")

    top_demand_skills = skill_summary.sort_values(
        "Average Demand Score", ascending=False
    ).head(15)

    st.bar_chart(
        top_demand_skills.set_index("Skill")["Average Demand Score"]
    )

    st.warning(
        "Employment, institute, company and job-fair figures are derived "
        "from your CSV scores for demonstration purposes. Replace them with "
        "verified administrative records for production use."
    )

# =====================================================
# 19. FOOTER
# =====================================================

st.divider()

st.caption(
    "District Labour & Skill Intelligence Portal | "
    "Powered by district_skills.csv | Demonstration build"
)
