import os

import pandas as pd
import streamlit as st


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Labour & Skill Planning",
    page_icon="🎯",
    layout="wide"
)


# ==========================================
# 2. LOAD CSV DATA
# ==========================================

CSV_FILE = "district_skills.csv"


@st.cache_data
def load_data():
    if not os.path.exists(CSV_FILE):
        st.error(f"CSV file not found: {CSV_FILE}")
        st.info("Please keep district_skills.csv in the same folder as app.py.")
        st.stop()

    return pd.read_csv(CSV_FILE)


data = load_data()


# ==========================================
# 3. SESSION STATE
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
# 4. APPLICATION HEADER
# ==========================================

st.title("🎯 Labour & Skill Planning System")
st.caption("District-level employment, skill demand and training planning")


# ==========================================
# 5. REGISTER AND LOGIN
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
# 6. SIDEBAR NAVIGATION
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
# 7. HELPER FUNCTIONS
# ==========================================

def get_column(df, possible_names):
    """Return the first matching column name from a list of possible names."""

    for name in possible_names:
        if name in df.columns:
            return name

    return None


district_col = get_column(
    data,
    ["District", "District Name", "district"]
)

skill_col = get_column(
    data,
    ["Skill", "Skill Name", "skill"]
)

sector_col = get_column(
    data,
    ["Sector", "Sector Name", "sector"]
)

institute_col = get_column(
    data,
    ["Institute", "Institute Name", "Training Institute"]
)


# ==========================================
# 8. EXPLORE DASHBOARD
# ==========================================

if st.session_state.page == "Explore Dashboard":

    st.header("Phase 1: Explore")
    st.write(
        "Explore the users and organisations involved in "
        "district-level Labour & Skill planning."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("User Groups", "4")
    col2.metric("CSV Rows", len(data))
    col3.metric(
        "Districts",
        data[district_col].nunique() if district_col else 0
    )
    col4.metric(
        "Skills",
        data[skill_col].nunique() if skill_col else 0
    )

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

    st.subheader("Uploaded CSV Data")
    st.dataframe(data, use_container_width=True)


# ==========================================
# 9. USERS
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


# ==========================================
# 10. DISTRICT ADMIN DASHBOARD
# ==========================================

elif st.session_state.page == "District Admin Dashboard":

    st.header("District Admin - Labour & Skill")
    st.write(
        "Understand district-level employment, skill demand, "
        "job openings, job fairs and training outcomes."
    )

    if not district_col:
        st.error("The CSV must contain a 'District' column.")
        st.stop()

    selected_district = st.selectbox(
        "Select District",
        data[district_col].dropna().unique().tolist()
    )

    district_rows = data[data[district_col] == selected_district]

    st.subheader("District Data")

    st.dataframe(district_rows, use_container_width=True)

    st.divider()

    st.subheader("1. Skill Demand")

    skill_opening_col = get_column(
        data,
        ["Skill Openings", "Openings", "Job Openings"]
    )

    if skill_col and skill_opening_col:
        skill_chart_data = (
            district_rows[[skill_col, skill_opening_col]]
            .dropna()
            .groupby(skill_col, as_index=False)[skill_opening_col]
            .sum()
        )

        st.bar_chart(
            skill_chart_data.set_index(skill_col)[skill_opening_col]
        )
    else:
        st.info("Skill columns were not found in the CSV.")

    st.divider()

    st.subheader("2. Sector Demand")

    sector_opening_col = get_column(
        data,
        ["Sector Openings", "Openings", "Job Openings"]
    )

    if sector_col and sector_opening_col:
        sector_chart_data = (
            district_rows[[sector_col, sector_opening_col]]
            .dropna()
            .groupby(sector_col, as_index=False)[sector_opening_col]
            .sum()
        )

        st.bar_chart(
            sector_chart_data.set_index(sector_col)[sector_opening_col]
        )
    else:
        st.info("Sector columns were not found in the CSV.")

    st.divider()

    st.subheader("3. Employment and Unemployment")

    employed_col = get_column(data, ["Employed Students", "Employed"])
    unemployed_col = get_column(data, ["Unemployed Students", "Unemployed"])
    openings_col = get_column(data, ["Job Openings", "Openings"])

    if employed_col and unemployed_col:
        employment_data = (
            data[[district_col, employed_col, unemployed_col]]
            .dropna()
            .groupby(district_col, as_index=False)[[employed_col, unemployed_col]]
            .sum()
        )

        st.bar_chart(
            employment_data.set_index(district_col)[
                [employed_col, unemployed_col]
            ]
        )
    else:
        st.info("Employment columns were not found in the CSV.")

    st.divider()

    st.subheader("4. Job Openings by District")

    if openings_col:
        opening_data = (
            data[[district_col, openings_col]]
            .dropna()
            .groupby(district_col, as_index=False)[openings_col]
            .sum()
        )

        st.bar_chart(
            opening_data.set_index(district_col)[openings_col]
        )
    else:
        st.info("Job Openings column was not found in the CSV.")

    st.divider()

    st.subheader("5. Job Fair Performance")

    job_fair_columns = [
        "Job Fairs Conducted",
        "Students Participated",
        "Students Placed",
        "Companies Participated",
        "Companies Hired"
    ]

    available_job_fair_columns = [
        column for column in job_fair_columns if column in data.columns
    ]

    if available_job_fair_columns:
        st.dataframe(
            district_rows[[district_col] + available_job_fair_columns],
            use_container_width=True
        )
    else:
        st.info("Job fair columns were not found in the CSV.")

    st.divider()

    st.subheader("6. Training Institute Performance")

    institute_columns = [
        "Students Enrolled",
        "Students Skilled",
        "Students Placed"
    ]

    available_institute_columns = [
        column for column in institute_columns if column in data.columns
    ]

    if institute_col and available_institute_columns:
        st.dataframe(
            district_rows[[institute_col] + available_institute_columns],
            use_container_width=True
        )
    else:
        st.info("Training institute columns were not found in the CSV.")


# ==========================================
# 11. STATE ADMIN
# ==========================================

elif st.session_state.page == "State Admin":

    st.header("State Admin - Labour & Skill")

    st.write(
        "State-level view of district employment, unemployment "
        "and job openings."
    )

    st.dataframe(data, use_container_width=True)

    if district_col:
        numeric_columns = data.select_dtypes(include="number").columns.tolist()

        if numeric_columns:
            state_summary = (
                data[[district_col] + numeric_columns]
                .groupby(district_col, as_index=False)
                .sum()
            )

            st.subheader("District Comparison")

            st.dataframe(state_summary, use_container_width=True)

            chart_columns = st.multiselect(
                "Select columns to compare",
                numeric_columns,
                default=numeric_columns[:3]
            )

            if chart_columns:
                st.bar_chart(
                    state_summary.set_index(district_col)[chart_columns]
                )


# ==========================================
# 12. TRAINING INSTITUTES
# ==========================================

elif st.session_state.page == "Training Institutes":

    st.header("Training Institutes")

    st.write(
        "Track student enrolment, students who complete training, "
        "and students who get placed."
    )

    institute_columns = [
        "Students Enrolled",
        "Students Skilled",
        "Students Placed"
    ]

    available_columns = [
        column for column in institute_columns if column in data.columns
    ]

    if institute_col and available_columns:
        institute_summary = (
            data[[institute_col] + available_columns]
            .dropna()
            .groupby(institute_col, as_index=False)[available_columns]
            .sum()
        )

        st.dataframe(institute_summary, use_container_width=True)

        st.bar_chart(
            institute_summary.set_index(institute_col)[available_columns]
        )
    else:
        st.info("Training institute columns were not found in the CSV.")


# ==========================================
# 13. JOB FAIR COMPANIES
# ==========================================

elif st.session_state.page == "Job Fair Companies":

    st.header("Job Fair Companies")

    st.write(
        "Review job fair participation and hiring outcomes "
        "by district."
    )

    job_fair_columns = [
        "Job Fairs Conducted",
        "Students Participated",
        "Students Placed",
        "Companies Participated",
        "Companies Hired"
    ]

    available_columns = [
        column for column in job_fair_columns if column in data.columns
    ]

    if available_columns:
        job_fair_summary = (
            data[[district_col] + available_columns]
            .dropna()
            .groupby(district_col, as_index=False)[available_columns]
            .sum()
        )

        st.dataframe(job_fair_summary, use_container_width=True)

        st.bar_chart(
            job_fair_summary.set_index(district_col)[available_columns]
        )
    else:
        st.info("Job fair columns were not found in the CSV.")


# ==========================================
# 14. ANALYTICS - AI SKILL PLANNING
# ==========================================

elif st.session_state.page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")

    st.write(
        "This module will help district administrators create "
        "skill plans based on unemployment, skill gaps and demand."
    )

    st.subheader("Generate a Skill Planning Report")

    if district_col:
        district = st.selectbox(
            "Choose District",
            data[district_col].dropna().unique().tolist(),
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

        if st.button("Generate Sample Report"):
            district_rows = data[data[district_col] == district]

            st.subheader("Sample Skill Planning Report")

            st.write(f"**District:** {district}")
            st.write(f"**Planning Focus:** {focus}")
            st.write(f"**CSV Rows for District:** {len(district_rows)}")

            st.dataframe(district_rows, use_container_width=True)

            st.info(
                "This is a basic report generated from your CSV data. "
                "AI-generated skill-gap analysis and recommendations "
                "can be added in the next development step."
            )


# ==========================================
# 15. PLANS
# ==========================================

elif st.session_state.page == "Plans":

    st.header("Skill Plans")

    st.write(
        "Display and manage skill planning reports created "
        "by the District Admin."
    )

    st.info(
        "The plan creation, saving and report display workflow "
        "will be implemented in the next step."
    )


# ==========================================
# 16. EXECUTED
# ==========================================

elif st.session_state.page == "Executed":

    st.header("Executed Plans")

    st.write(
        "Track which planned activities have actually been executed."
    )

    execution_data = pd.DataFrame({
        "Activity": [
            "Python Training",
            "Electrical Training",
            "Job Fair"
        ],
        "Status": [
            "Planned",
            "In Progress",
            "Planned"
        ]
    })

    st.dataframe(execution_data, use_container_width=True)

    st.info(
        "Execution dates, completion status and actual results "
        "will be connected to saved plans later."
    )


# ==========================================
# 17. RESULTS
# ==========================================

elif st.session_state.page == "Results":

    st.header("Results")

    st.write(
        "Monitor changes in unemployment and skill gaps "
        "after skill plans are executed."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Unemployment Trend")
        st.write(
            "Historical unemployment data will be displayed here."
        )

    with c2:
        st.subheader("Skill Gap Trend")
        st.write(
            "Historical skill-demand and training-gap data "
            "will be displayed here."
        )

    st.info(
        "Trend analysis requires historical data. "
        "The next development step will add a way to save "
        "and compare results over time."
    )


# ==========================================
# 18. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | Initial Development Version"
)
