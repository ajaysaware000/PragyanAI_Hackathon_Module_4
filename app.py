import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Labour & Skill Planning",
    page_icon="🎯",
    layout="wide"
)

# ==========================================
# 2. LOAD DISTRICT_SKILLS CSV
# ==========================================

CSV_FILE = "district_skills.csv"

try:
    skill_data = None

    # Try comma, semicolon and tab separators automatically
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

    # Show detected columns in sidebar
    with st.sidebar:
        st.caption("CSV columns detected:")
        st.write(", ".join(skill_data.columns))

    # Rename common alternative column names
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

    # Create missing columns with demo defaults
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
        skill_data[column] = skill_data[column].astype(str).str.strip()

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

# ==========================================
# 3. CREATE DATA FROM CSV
# ==========================================

np.random.seed(42)

# Skill demand
skill_demand = (
    skill_data
    .groupby("skill", as_index=False)["demand_score"]
    .mean()
    .round(1)
    .rename(columns={
        "skill": "Skill",
        "demand_score": "Demand Score"
    })
    .sort_values("Demand Score", ascending=False)
)

# Sector demand
sector_demand = (
    skill_data
    .groupby("sector", as_index=False)["demand_score"]
    .mean()
    .round(1)
    .rename(columns={
        "sector": "Sector",
        "demand_score": "Demand Score"
    })
    .sort_values("Demand Score", ascending=False)
)

# District summary
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

# Simulated employment data based on CSV scores
district_data = district_summary.copy()
district_data["Employed Students"] = (
    district_data["Average Demand Score"] * 15
).astype(int)

district_data["Unemployed Students"] = (
    district_data["Average Skill Gap"] * 8
).astype(int)

district_data["Job Openings"] = (
    district_data["Average Demand Score"] * 7
).astype(int)

district_data = district_data[[
    "District",
    "Employed Students",
    "Unemployed Students",
    "Job Openings"
]]

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
        "Job Fairs Conducted": fairs,
        "Students Participated": students_participated,
        "Students Placed": students_placed,
        "Companies Participated": companies_participated,
        "Companies Hired": companies_hired
    })

job_fair_data = pd.DataFrame(job_fair_rows)

# Simulated institute data
institute_templates = [
    "Government Skill Centre",
    "District Training Institute",
    "Technical Training Centre"
]

institute_rows = []

for index, row in district_summary.iterrows():
    district = row["District"]
    base_enrolment = int(row["Average Training Access"] * 5) + 80

    for institute in institute_templates:
        enrolled = max(
            50,
            base_enrolment + np.random.randint(-20, 40)
        )
        skilled = int(enrolled * np.random.uniform(0.60, 0.90))
        placed = int(skilled * np.random.uniform(0.45, 0.85))

        institute_rows.append({
            "Institute": institute,
            "District": district,
            "Students Enrolled": enrolled,
            "Students Skilled": skilled,
            "Students Placed": placed
        })

institute_data = pd.DataFrame(institute_rows)

# Simulated hiring companies
company_templates = [
    "ABC Technologies",
    "Digital Solutions Pvt Ltd",
    "Karnataka Manufacturing Ltd.",
    "Precision Engineering Works",
    "HealthFirst Services",
    "SolarWorks India"
]

hiring_companies = (
    skill_data
    .groupby(["district", "sector", "skill"], as_index=False)
    .agg(
        Average_Demand=("demand_score", "mean"),
        Average_Gap=("gap_score", "mean")
    )
    .round(1)
)

hiring_companies["Company"] = np.random.choice(
    company_templates,
    size=len(hiring_companies)
)

hiring_companies["Openings"] = (
    hiring_companies["Average_Demand"] * np.random.uniform(0.2, 0.6, len(hiring_companies))
).astype(int)

hiring_companies = hiring_companies.rename(columns={
    "district": "District",
    "sector": "Sector",
    "skill": "Skill Required",
    "Average_Demand": "Average Demand Score",
    "Average_Gap": "Average Skill Gap"
})

hiring_companies = hiring_companies[[
    "Company", "District", "Sector",
    "Skill Required", "Openings",
    "Average Demand Score", "Average Skill Gap"
]]

# ==========================================
# 4. SESSION STATE
# ==========================================

if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Explore Dashboard"

if "plans" not in st.session_state:
    st.session_state.plans = []

if "executions" not in st.session_state:
    st.session_state.executions = []

# ==========================================
# 5. APPLICATION HEADER
# ==========================================

st.title("🎯 Labour & Skill Planning System")
st.caption(
    "District-level employment, skill demand and training planning "
    "powered by district_skills.csv"
)

# ==========================================
# 6. REGISTER AND LOGIN
# ==========================================

if not st.session_state.logged_in:

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with register_tab:
        st.subheader("Create an Account")

        new_username = st.text_input(
            "Username",
            key="register_username"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        role = st.selectbox(
            "Select Role",
            [
                "District Admin - Labour & Skill",
                "State Admin - Labour & Skill",
                "Training Institute",
                "Job Fair Company"
            ]
        )

        if st.button("Register", use_container_width=True):
            if not new_username.strip() or not new_password:
                st.error("Please enter a username and password.")

            elif new_username in st.session_state.users:
                st.error("This username already exists.")

            else:
                st.session_state.users[new_username] = {
                    "password": new_password,
                    "role": role
                }

                st.success("Registration successful. Open the Login tab.")

    with login_tab:
        st.subheader("Login to Your Account")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):
            user = st.session_state.users.get(username)

            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "Explore Dashboard"
                st.rerun()

            else:
                st.error(
                    "Invalid username or password. "
                    "Register first if you do not have an account."
                )

    st.info(
        "This is a demonstration login. Accounts exist only during "
        "the current Streamlit session. Production use requires "
        "secure password hashing and a persistent database."
    )

    st.stop()

# ==========================================
# 7. SIDEBAR NAVIGATION
# ==========================================

user = st.session_state.users[st.session_state.username]

st.sidebar.title("Navigation")
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {user['role']}")

pages = [
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
]

st.session_state.page = st.sidebar.radio(
    "Select a Page",
    pages,
    index=pages.index(st.session_state.page)
)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ==========================================
# 8. EXPLORE DASHBOARD
# ==========================================

if st.session_state.page == "Explore Dashboard":

    st.header("Phase 1: Explore")
    st.write(
        "Explore users, districts, sectors and skills using your "
        "district_skills.csv dataset."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("User Groups", "4")
    col2.metric("Districts", skill_data["district"].nunique())
    col3.metric("Skills", skill_data["skill"].nunique())
    col4.metric("Sectors", skill_data["sector"].nunique())

    st.divider()

    st.subheader("Explore User Groups")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🏢 District Admin")
        st.write(
            "Monitor employment, unemployment, skill demand, "
            "job openings, job fairs and training institutes."
        )

        st.markdown("### 🏛️ State Admin")
        st.write(
            "Review district-level information and compare "
            "skill and employment trends across districts."
        )

    with c2:
        st.markdown("### 🎓 Training Institutes")
        st.write(
            "Track student enrolment, skill training and "
            "student placement outcomes."
        )

        st.markdown("### 🤝 Job Fair Companies")
        st.write(
            "Explore job fair participation, hiring activity "
            "and employment opportunities."
        )

    st.divider()

    st.subheader("District Overview")
    st.dataframe(district_data, use_container_width=True)

    st.subheader("CSV Data Preview")
    st.dataframe(skill_data, use_container_width=True)

# ==========================================
# 9. USERS PAGE
# ==========================================

elif st.session_state.page == "Users":

    st.header("Users")

    user_groups = pd.DataFrame({
        "User Group": [
            "District Admin - Labour & Skill",
            "State Admin - Labour & Skill",
            "Training Institutes",
            "Job Fair Companies"
        ],
        "Main Responsibility": [
            "District skill and employment planning",
            "State-level monitoring and coordination",
            "Student training and placement",
            "Recruitment and hiring"
        ]
    })

    st.dataframe(user_groups, use_container_width=True)

    if st.session_state.users:
        st.subheader("Registered Users")

        registered_users = pd.DataFrame([
            {
                "Username": name,
                "Role": details["role"]
            }
            for name, details in st.session_state.users.items()
        ])

        st.dataframe(registered_users, use_container_width=True)
    else:
        st.info("No users registered in this session.")

# ==========================================
# 10. DISTRICT ADMIN DASHBOARD
# ==========================================

elif st.session_state.page == "District Admin Dashboard":

    st.header("District Admin - Labour & Skill")
    st.write(
        "Understand district-level employment, skill demand, "
        "job openings, hiring companies and training outcomes."
    )

    selected_district = st.selectbox(
        "Select District",
        sorted(skill_data["district"].unique())
    )

    district_records = skill_data[
        skill_data["district"] == selected_district
    ]

    district_row = district_data[
        district_data["District"] == selected_district
    ].iloc[0]

    fair_row = job_fair_data[
        job_fair_data["District"] == selected_district
    ].iloc[0]

    st.subheader("Employment and Job Openings")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Employed Students",
        int(district_row["Employed Students"])
    )

    c2.metric(
        "Unemployed Students",
        int(district_row["Unemployed Students"])
    )

    c3.metric(
        "Job Openings",
        int(district_row["Job Openings"])
    )

    st.divider()

    st.subheader("1. Which Sectors and Skills Are Growing?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill-wise Demand")

        district_skill_demand = (
            district_records
            .groupby("skill", as_index=False)["demand_score"]
            .mean()
            .round(1)
            .set_index("skill")
        )

        st.bar_chart(district_skill_demand["demand_score"])

    with col2:
        st.markdown("#### Sector-wise Demand")

        district_sector_demand = (
            district_records
            .groupby("sector", as_index=False)["demand_score"]
            .mean()
            .round(1)
            .set_index("sector")
        )

        st.bar_chart(district_sector_demand["demand_score"])

    st.divider()

    st.subheader("2. Employed and Unemployed Students")

    st.bar_chart(
        district_data.set_index("District")[
            ["Employed Students", "Unemployed Students"]
        ]
    )

    st.dataframe(
        district_data[
            [
                "District",
                "Employed Students",
                "Unemployed Students"
            ]
        ],
        use_container_width=True
    )

    st.divider()

    st.subheader("3. Job Openings — District-wise")

    st.bar_chart(
        district_data.set_index("District")["Job Openings"]
    )

    st.divider()

    st.subheader("4. Hiring Companies")

    district_companies = hiring_companies[
        hiring_companies["District"] == selected_district
    ]

    st.dataframe(district_companies, use_container_width=True)

    st.divider()

    st.subheader("5. Job Fair Performance")

    st.dataframe(job_fair_data, use_container_width=True)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Job Fairs Conducted",
        int(fair_row["Job Fairs Conducted"])
    )

    c2.metric(
        "Students Participated",
        int(fair_row["Students Participated"])
    )

    c3.metric(
        "Students Placed",
        int(fair_row["Students Placed"])
    )

    c4, c5 = st.columns(2)

    c4.metric(
        "Companies Participated",
        int(fair_row["Companies Participated"])
    )

    c5.metric(
        "Companies That Hired",
        int(fair_row["Companies Hired"])
    )

    st.divider()

    st.subheader("6. Training Institute Performance")

    district_institutes = institute_data[
        institute_data["District"] == selected_district
    ]

    st.dataframe(district_institutes, use_container_width=True)

    st.bar_chart(
        district_institutes.set_index("Institute")[
            ["Students Enrolled", "Students Skilled", "Students Placed"]
        ]
    )

# ==========================================
# 11. STATE ADMIN
# ==========================================

elif st.session_state.page == "State Admin":

    st.header("State Admin - Labour & Skill")

    st.write(
        "State-level view of district employment, unemployment "
        "and job openings."
    )

    st.dataframe(district_data, use_container_width=True)

    st.subheader("Compare Districts")

    st.bar_chart(
        district_data.set_index("District")[
            ["Employed Students", "Unemployed Students", "Job Openings"]
        ]
    )

    st.subheader("District Skill Indicators")

    st.dataframe(district_summary, use_container_width=True)

    st.subheader("Districts Requiring Attention")

    priority_districts = district_summary.sort_values(
        "Average Skill Gap",
        ascending=False
    ).head(3)

    st.dataframe(priority_districts, use_container_width=True)

# ==========================================
# 12. TRAINING INSTITUTES
# ==========================================

elif st.session_state.page == "Training Institutes":

    st.header("Training Institutes")

    st.write(
        "Track student enrolment, students who complete training, "
        "and students who get placed."
    )

    selected_district = st.selectbox(
        "Filter District",
        ["All Districts"] + sorted(skill_data["district"].unique()),
        key="institute_district"
    )

    institute_view = institute_data.copy()

    if selected_district != "All Districts":
        institute_view = institute_view[
            institute_view["District"] == selected_district
        ]

    st.dataframe(institute_view, use_container_width=True)

    st.subheader("Student Training Outcomes")

    st.bar_chart(
        institute_view.set_index("Institute")[
            ["Students Enrolled", "Students Skilled", "Students Placed"]
        ]
    )

    st.subheader("Placement Rate")

    institute_view["Placement Rate (%)"] = (
        100 * institute_view["Students Placed"]
        / institute_view["Students Enrolled"]
    ).round(1)

    st.dataframe(
        institute_view[
            [
                "Institute", "District",
                "Students Enrolled", "Students Placed",
                "Placement Rate (%)"
            ]
        ],
        use_container_width=True
    )

# ==========================================
# 13. JOB FAIR COMPANIES
# ==========================================

elif st.session_state.page == "Job Fair Companies":

    st.header("Job Fair Companies")

    st.write(
        "Review job fair participation and hiring outcomes "
        "by district."
    )

    st.dataframe(job_fair_data, use_container_width=True)

    st.subheader("Job Fair Hiring Results")

    st.bar_chart(
        job_fair_data.set_index("District")[
            ["Companies Participated", "Companies Hired"]
        ]
    )

    st.subheader("Company Openings by Sector")

    sector_openings = (
        hiring_companies
        .groupby("Sector", as_index=False)["Openings"]
        .sum()
    )

    st.bar_chart(
        sector_openings.set_index("Sector")["Openings"]
    )

# ==========================================
# 14. ANALYTICS - AI SKILL PLANNING
# ==========================================

elif st.session_state.page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")

    st.write(
        "Create skill plans based on unemployment, skill gaps "
        "and demand from district_skills.csv."
    )

    district = st.selectbox(
        "Choose District",
        sorted(skill_data["district"].unique()),
        key="analytics_district"
    )

    focus = st.selectbox(
        "Planning Focus",
        [
            "Reduce Unemployment",
            "Address Skill Gaps",
            "Growing Skills",
            "Growing Sectors"
        ]
    )

    district_records = skill_data[
        skill_data["district"] == district
    ]

    if district_records.empty:
        st.warning("No CSV records available for this district.")
    else:
        st.subheader("Skill Gap Report")

        planning_report = (
            district_records
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

        st.dataframe(planning_report, use_container_width=True)

        st.bar_chart(
            planning_report.set_index("skill")["gap_score"]
        )

        if st.button("Generate Skill Planning Report"):

            highest_gap = planning_report.iloc[0]

            st.success("Skill planning report generated.")

            st.write(f"**District:** {district}")
            st.write(f"**Planning Focus:** {focus}")
            st.write(
                f"**Highest-gap skill:** {highest_gap['skill']}"
            )
            st.write(
                f"**Sector:** {highest_gap['sector']}"
            )
            st.write(
                f"**Average gap score:** {highest_gap['gap_score']}"
            )

            st.markdown("#### Recommended Actions")

            st.write(
                f"1. Assess training capacity for "
                f"{highest_gap['skill']} in {district}."
            )
            st.write(
                "2. Contact companies with openings in the "
                "matching sector."
            )
            st.write(
                "3. Review training institute placement performance."
            )
            st.write(
                "4. Track enrolment, completion and placement "
                "after implementation."
            )

            st.warning(
                "This report is generated from CSV scores and is "
                "intended for demonstration and planning support only."
            )

# ==========================================
# 15. PLANS
# ==========================================

elif st.session_state.page == "Plans":

    st.header("Skill Plans")

    st.write(
        "Create and manage skill planning records for districts."
    )

    with st.form("create_plan_form"):

        plan_name = st.text_input(
            "Plan Title",
            placeholder="Example: Python Training Plan"
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
            "Target Skill",
            district_skills
        )

        target_students = st.number_input(
            "Target Students",
            min_value=1,
            max_value=100000,
            value=100
        )

        institute = st.selectbox(
            "Training Institute",
            institute_templates
        )

        target_date = st.date_input("Target Completion Date")

        notes = st.text_area("Plan Notes")

        save_plan = st.form_submit_button("Save Skill Plan")

    if save_plan:
        if not plan_name.strip():
            st.error("Please enter a plan title.")
        else:
            plan = {
                "Plan ID": f"PLAN-{len(st.session_state.plans) + 1:03}",
                "Plan Title": plan_name,
                "District": plan_district,
                "Skill": plan_skill,
                "Target Students": int(target_students),
                "Training Institute": institute,
                "Target Date": str(target_date),
                "Status": "Planned",
                "Notes": notes
            }

            st.session_state.plans.append(plan)
            st.success("Skill plan saved.")

    st.subheader("Saved Plans")

    if st.session_state.plans:
        st.dataframe(
            pd.DataFrame(st.session_state.plans),
            use_container_width=True
        )

        st.download_button(
            "Download Plans as CSV",
            pd.DataFrame(st.session_state.plans).to_csv(index=False),
            file_name="skill_plans.csv",
            mime="text/csv"
        )
    else:
        st.info("No plans saved yet.")

# ==========================================
# 16. EXECUTED
# ==========================================

elif st.session_state.page == "Executed":

    st.header("Executed Plans")

    if not st.session_state.plans:
        st.info("Create a skill plan first.")
    else:
        plan_options = [
            plan["Plan ID"] + " — " + plan["Plan Title"]
            for plan in st.session_state.plans
        ]

        selected_plan = st.selectbox(
            "Select Plan",
            plan_options
        )

        selected_index = plan_options.index(selected_plan)
        selected_plan_record = st.session_state.plans[selected_index]

        with st.form("execution_form"):

            status = st.selectbox(
                "Execution Status",
                [
                    "Not Started",
                    "In Progress",
                    "Completed",
                    "On Hold"
                ]
            )

            start_date = st.date_input("Actual Start Date")

            students_trained = st.number_input(
                "Students Trained",
                min_value=0,
                max_value=int(selected_plan_record["Target Students"]),
                value=0
            )

            students_placed = st.number_input(
                "Students Placed",
                min_value=0,
                max_value=int(selected_plan_record["Target Students"]),
                value=0
            )

            expenditure = st.number_input(
                "Expenditure (INR)",
                min_value=0,
                value=0,
                step=1000
            )

            execution_notes = st.text_area("Execution Notes")

            save_execution = st.form_submit_button(
                "Save Execution Update"
            )

        if save_execution:
            execution = {
                "Plan ID": selected_plan_record["Plan ID"],
                "Plan Title": selected_plan_record["Plan Title"],
                "District": selected_plan_record["District"],
                "Status": status,
                "Start Date": str(start_date),
                "Students Trained": int(students_trained),
                "Students Placed": int(students_placed),
                "Expenditure (INR)": int(expenditure),
                "Notes": execution_notes
            }

            st.session_state.executions.append(execution)
            selected_plan_record["Status"] = status

            st.success("Execution update saved.")

    st.subheader("Execution Records")

    if st.session_state.executions:
        st.dataframe(
            pd.DataFrame(st.session_state.executions),
            use_container_width=True
        )

        st.download_button(
            "Download Execution Report",
            pd.DataFrame(st.session_state.executions).to_csv(index=False),
            file_name="execution_report.csv",
            mime="text/csv"
        )
    else:
        st.info("No execution updates saved yet.")

# ==========================================
# 17. RESULTS
# ==========================================

elif st.session_state.page == "Results":

    st.header("Results")

    if st.session_state.executions:

        result_data = pd.DataFrame(st.session_state.executions)

        total_target = sum(
            plan["Target Students"]
            for plan in st.session_state.plans
        )

        total_trained = int(result_data["Students Trained"].sum())
        total_placed = int(result_data["Students Placed"].sum())
        total_spend = int(result_data["Expenditure (INR)"].sum())

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Target Students", total_target)
        c2.metric("Students Trained", total_trained)
        c3.metric("Students Placed", total_placed)
        c4.metric("Expenditure", f"₹{total_spend:,}")

        st.subheader("Execution Results")

        st.dataframe(result_data, use_container_width=True)

        st.bar_chart(
            result_data.set_index("Plan Title")[
                ["Students Trained", "Students Placed"]
            ]
        )

    else:
        st.info(
            "No execution results available. Create and execute "
            "a skill plan first."
        )

    st.subheader("District Skill Gap")

    st.bar_chart(
        district_summary.set_index("District")["Average Skill Gap"]
    )

    st.subheader("Top Skills by Demand")

    top_skills = skill_demand.head(10)

    st.bar_chart(
        top_skills.set_index("Skill")["Demand Score"]
    )

# ==========================================
# 18. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | "
    "Powered by district_skills.csv | Demonstration Version"
)
