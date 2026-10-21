import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

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
    df = pd.read_csv(
        CSV_FILE,
        encoding="utf-8-sig",
        skip_blank_lines=True
    )

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("(%)", "percent", regex=False)
        .str.replace("(inr)", "inr", regex=False)
    )

    required_columns = [
        "record_id", "district", "skill", "sector",
        "employed", "unemployed", "job_openings",
        "training_enrolment", "skill_demand",
        "available_candidates", "skill_gap",
        "training_institute", "students_enrolled",
        "students_skilled", "students_placed",
        "placement_rate_percent", "company",
        "company_sector", "company_vacancies",
        "participated_in_job_fair", "students_hired_by_company",
        "job_fairs_conducted", "students_participated_in_fairs",
        "students_placed_through_fairs",
        "companies_participated_in_fairs",
        "companies_hired_through_fairs", "plan_id",
        "plan_status", "target_students",
        "students_trained_under_plan",
        "students_placed_under_plan", "expenditure_inr"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(
            "The CSV file is missing these required columns: "
            f"{', '.join(missing_columns)}"
        )
        st.stop()

    # Clean text columns
    text_columns = [
        "record_id", "district", "skill", "sector",
        "training_institute", "company", "company_sector",
        "participated_in_job_fair", "plan_id", "plan_status"
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    # Clean numeric columns
    numeric_columns = [
        "employed", "unemployed", "job_openings",
        "training_enrolment", "skill_demand",
        "available_candidates", "skill_gap",
        "students_enrolled", "students_skilled",
        "students_placed", "placement_rate_percent",
        "company_vacancies", "students_hired_by_company",
        "job_fairs_conducted", "students_participated_in_fairs",
        "students_placed_through_fairs",
        "companies_participated_in_fairs",
        "companies_hired_through_fairs",
        "target_students", "students_trained_under_plan",
        "students_placed_under_plan", "expenditure_inr"
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

# ==========================================
# 3. CREATE SUMMARY DATA
# ==========================================

district_data = (
    df
    .groupby("district", as_index=False)
    .agg(
        Employed=("employed", "sum"),
        Unemployed=("unemployed", "sum"),
        Job_Openings=("job_openings", "sum"),
        Training_Enrolment=("training_enrolment", "sum")
    )
)

district_data = district_data.rename(columns={
    "district": "District",
    "Employed": "Employed Students",
    "Unemployed": "Unemployed Students",
    "Job_Openings": "Job Openings",
    "Training_Enrolment": "Training Enrolment"
})

skill_demand = (
    df
    .groupby("skill", as_index=False)
    .agg(
        Openings=("job_openings", "sum"),
        Demand=("skill_demand", "sum"),
        Skill_Gap=("skill_gap", "sum")
    )
    .rename(columns={"skill": "Skill"})
    .sort_values("Demand", ascending=False)
)

sector_demand = (
    df
    .groupby("sector", as_index=False)
    .agg(
        Openings=("job_openings", "sum"),
        Demand=("skill_demand", "sum"),
        Skill_Gap=("skill_gap", "sum")
    )
    .rename(columns={"sector": "Sector"})
    .sort_values("Demand", ascending=False)
)

job_fair_data = (
    df
    .groupby("district", as_index=False)
    .agg(
        Job_Fairs_Conducted=("job_fairs_conducted", "sum"),
        Students_Participated=("students_participated_in_fairs", "sum"),
        Students_Placed=("students_placed_through_fairs", "sum"),
        Companies_Participated=("companies_participated_in_fairs", "sum"),
        Companies_Hired=("companies_hired_through_fairs", "sum")
    )
    .rename(columns={
        "district": "District",
        "Job_Fairs_Conducted": "Job Fairs Conducted",
        "Students_Participated": "Students Participated",
        "Students_Placed": "Students Placed",
        "Companies_Participated": "Companies Participated",
        "Companies_Hired": "Companies Hired"
    })
)

institute_data = (
    df
    .groupby(["district", "training_institute"], as_index=False)
    .agg(
        Students_Enrolled=("students_enrolled", "sum"),
        Students_Skilled=("students_skilled", "sum"),
        Students_Placed=("students_placed", "sum")
    )
    .rename(columns={
        "district": "District",
        "training_institute": "Institute",
        "Students_Enrolled": "Students Enrolled",
        "Students_Skilled": "Students Skilled",
        "Students_Placed": "Students Placed"
    })
)

hiring_companies = (
    df
    .groupby(
        ["district", "company", "company_sector", "skill"],
        as_index=False
    )
    .agg(
        Company_Vacancies=("company_vacancies", "sum"),
        Students_Hired=("students_hired_by_company", "sum"),
        Job_Fair_Participation=("participated_in_job_fair", lambda x: ", ".join(x.unique()))
    )
    .rename(columns={
        "district": "District",
        "company": "Company",
        "company_sector": "Sector",
        "skill": "Skill Required",
        "Company_Vacancies": "Openings",
        "Students_Hired": "Students Hired",
        "Job_Fair_Participation": "Participated in Job Fair"
    })
)

plan_data = df[
    [
        "plan_id", "district", "skill",
        "plan_status", "target_students",
        "students_trained_under_plan",
        "students_placed_under_plan",
        "expenditure_inr"
    ]
].copy()

plan_data = plan_data.rename(columns={
    "plan_id": "Plan ID",
    "district": "District",
    "skill": "Skill",
    "plan_status": "Status",
    "target_students": "Target Students",
    "students_trained_under_plan": "Students Trained",
    "students_placed_under_plan": "Students Placed",
    "expenditure_inr": "Expenditure (INR)"
})

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
        "Explore users, districts, sectors, skills and planning "
        "records from your CSV dataset."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("User Groups", "4")
    col2.metric("Districts", df["district"].nunique())
    col3.metric("Skills", df["skill"].nunique())
    col4.metric("Sectors", df["sector"].nunique())

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

    st.subheader("CSV Records")
    st.dataframe(df, use_container_width=True)

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
        sorted(df["district"].unique())
    )

    district_records = df[
        df["district"] == selected_district
    ]

    district_row = district_data[
        district_data["District"] == selected_district
    ].iloc[0]

    fair_row = job_fair_data[
        job_fair_data["District"] == selected_district
    ].iloc[0]

    st.subheader("Employment and Job Openings")

    c1, c2, c3, c4 = st.columns(4)

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

    c4.metric(
        "Training Enrolment",
        int(district_row["Training Enrolment"])
    )

    st.divider()

    st.subheader("1. Which Sectors and Skills Are Growing?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill-wise Demand")

        district_skill_demand = (
            district_records
            .groupby("skill", as_index=False)
            .agg(
                Openings=("job_openings", "sum"),
                Demand=("skill_demand", "sum")
            )
            .set_index("skill")
        )

        st.bar_chart(district_skill_demand[["Openings", "Demand"]])

    with col2:
        st.markdown("#### Sector-wise Demand")

        district_sector_demand = (
            district_records
            .groupby("sector", as_index=False)
            .agg(
                Openings=("job_openings", "sum"),
                Demand=("skill_demand", "sum")
            )
            .set_index("sector")
        )

        st.bar_chart(district_sector_demand[["Openings", "Demand"]])

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
            [
                "Employed Students",
                "Unemployed Students",
                "Job Openings"
            ]
        ]
    )

    st.subheader("Districts Requiring Attention")

    priority_districts = district_data.sort_values(
        "Unemployed Students",
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
        ["All Districts"] + sorted(df["district"].unique()),
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
        sorted(df["district"].unique()),
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

    district_records = df[
        df["district"] == district
    ]

    if district_records.empty:
        st.warning("No CSV records available for this district.")
    else:
        st.subheader("Skill Gap Report")

        planning_report = (
            district_records
            .groupby(["sector", "skill"], as_index=False)
            .agg(
                Skill_Demand=("skill_demand", "sum"),
                Available_Candidates=("available_candidates", "sum"),
                Skill_Gap=("skill_gap", "sum"),
                Job_Openings=("job_openings", "sum")
            )
            .sort_values("Skill_Gap", ascending=False)
        )

        planning_report["Priority"] = planning_report["Skill_Gap"].apply(
            lambda gap: "High" if gap >= 300
            else ("Medium" if gap >= 150 else "Monitor")
        )

        planning_report = planning_report.rename(columns={
            "sector": "Sector",
            "skill": "Skill",
            "Skill_Demand": "Skill Demand",
            "Available_Candidates": "Available Candidates",
            "Skill_Gap": "Skill Gap",
            "Job_Openings": "Job Openings"
        })

        st.dataframe(planning_report, use_container_width=True)

        st.bar_chart(
            planning_report.set_index("Skill")["Skill Gap"]
        )

        if st.button("Generate Skill Planning Report"):

            highest_gap = planning_report.iloc[0]

            st.success("Skill planning report generated.")

            st.write(f"**District:** {district}")
            st.write(f"**Planning Focus:** {focus}")
            st.write(
                f"**Highest-gap skill:** {highest_gap['Skill']}"
            )
            st.write(
                f"**Sector:** {highest_gap['Sector']}"
            )
            st.write(
                f"**Total skill gap:** {int(highest_gap['Skill Gap'])}"
            )

            st.markdown("#### Recommended Actions")

            st.write(
                f"1. Assess training capacity for "
                f"{highest_gap['Skill']} in {district}."
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

# ==========================================
# 15. PLANS
# ==========================================

elif st.session_state.page == "Plans":

    st.header("Skill Plans")

    st.write(
        "Review skill planning records available in the CSV "
        "and create new plans."
    )

    st.subheader("Plans from CSV")

    st.dataframe(plan_data, use_container_width=True)

    st.download_button(
        "Download CSV Plans",
        plan_data.to_csv(index=False),
        file_name="csv_skill_plans.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("Create New Plan")

    with st.form("create_plan_form"):

        plan_name = st.text_input(
            "Plan Title",
            placeholder="Example: Python Training Plan"
        )

        plan_district = st.selectbox(
            "District",
            sorted(df["district"].unique())
        )

        district_skills = sorted(
            df[
                df["district"] == plan_district
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
            sorted(df["training_institute"].unique())
        )

        target_date = st.date_input("Target Completion Date")

        notes = st.text_area("Plan Notes")

        save_plan = st.form_submit_button("Save Skill Plan")

    if save_plan:
        if not plan_name.strip():
            st.error("Please enter a plan title.")
        else:
            new_plan = {
                "Plan ID": f"NEW-{len(st.session_state.plans) + 1:03}",
                "Plan Title": plan_name,
                "District": plan_district,
                "Skill": plan_skill,
                "Target Students": int(target_students),
                "Training Institute": institute,
                "Target Date": str(target_date),
                "Status": "Planned",
                "Notes": notes
            }

            st.session_state.plans.append(new_plan)
            st.success("Skill plan saved for this session.")

    if st.session_state.plans:
        st.subheader("Newly Created Plans")

        st.dataframe(
            pd.DataFrame(st.session_state.plans),
            use_container_width=True
        )

# ==========================================
# 16. EXECUTED
# ==========================================

elif st.session_state.page == "Executed":

    st.header("Executed Plans")

    st.subheader("Plan Status from CSV")

    status_summary = (
        df
        .groupby("plan_status", as_index=False)
        .agg(
            Plans=("plan_id", "count"),
            Target_Students=("target_students", "sum"),
            Students_Trained=("students_trained_under_plan", "sum"),
            Students_Placed=("students_placed_under_plan", "sum"),
            Expenditure=("expenditure_inr", "sum")
        )
        .rename(columns={
            "plan_status": "Plan Status",
            "Plans": "Plans",
            "Target_Students": "Target Students",
            "Students_Trained": "Students Trained",
            "Students_Placed": "Students Placed",
            "Expenditure": "Expenditure (INR)"
        })
    )

    st.dataframe(status_summary, use_container_width=True)

    st.bar_chart(
        status_summary.set_index("Plan Status")[
            ["Students Trained", "Students Placed"]
        ]
    )

    st.subheader("Plan Records")

    st.dataframe(plan_data, use_container_width=True)

# ==========================================
# 17. RESULTS
# ==========================================

elif st.session_state.page == "Results":

    st.header("Results")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Target Students",
        int(df["target_students"].sum())
    )

    c2.metric(
        "Students Trained",
        int(df["students_trained_under_plan"].sum())
    )

    c3.metric(
        "Students Placed",
        int(df["students_placed_under_plan"].sum())
    )

    c4.metric(
        "Total Expenditure",
        f"₹{int(df['expenditure_inr'].sum()):,}"
    )

    st.subheader("Training and Placement by District")

    result_by_district = (
        df
        .groupby("district", as_index=False)
        .agg(
            Target_Students=("target_students", "sum"),
            Students_Trained=("students_trained_under_plan", "sum"),
            Students_Placed=("students_placed_under_plan", "sum")
        )
        .rename(columns={
            "district": "District",
            "Target_Students": "Target Students",
            "Students_Trained": "Students Trained",
            "Students_Placed": "Students Placed"
        })
    )

    st.dataframe(result_by_district, use_container_width=True)

    st.bar_chart(
        result_by_district.set_index("District")[
            ["Students Trained", "Students Placed"]
        ]
    )

    st.subheader("Skill Gap by Skill")

    st.bar_chart(
        skill_demand.set_index("Skill")["Skill_Gap"]
    )

# ==========================================
# 18. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | "
    "Powered by district_skills.csv | Demonstration Version"
)
