import streamlit as st
import pandas as pd

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Labour & Skill Planning",
    page_icon="🎯",
    layout="wide"
)

# ==========================================
# 2. SAMPLE DATA
# Replace this with real district data later
# ==========================================

skill_demand = pd.DataFrame({
    "Skill": ["Python", "Data Analytics", "Electrician", "Welding", "Healthcare"],
    "Openings": [250, 180, 200, 120, 160]
})

sector_demand = pd.DataFrame({
    "Sector": ["IT", "Manufacturing", "Healthcare", "Construction", "Retail"],
    "Openings": [300, 220, 180, 150, 100]
})

district_data = pd.DataFrame({
    "District": ["Bengaluru Urban", "Belagavi", "Mysuru", "Kalaburagi"],
    "Employed Students": [1200, 850, 900, 600],
    "Unemployed Students": [300, 420, 350, 500],
    "Job Openings": [800, 450, 520, 300]
})

job_fair_data = pd.DataFrame({
    "District": ["Bengaluru Urban", "Belagavi", "Mysuru", "Kalaburagi"],
    "Job Fairs Conducted": [8, 5, 6, 3],
    "Students Participated": [800, 450, 600, 300],
    "Students Placed": [500, 260, 350, 140],
    "Companies Participated": [40, 25, 30, 15],
    "Companies Hired": [32, 18, 22, 10]
})

institute_data = pd.DataFrame({
    "Institute": [
        "Government Skill Centre",
        "District Training Institute",
        "Technical Training Centre"
    ],
    "Students Enrolled": [300, 250, 200],
    "Students Skilled": [260, 210, 170],
    "Students Placed": [180, 140, 110]
})

# ==========================================
# 3. SESSION STATE
# Demo authentication only; not production security
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
# 7. PHASE 1: EXPLORE DASHBOARD
# ==========================================

if st.session_state.page == "Explore Dashboard":

    st.header("Phase 1: Explore")
    st.write(
        "Explore the users and organisations involved in "
        "district-level Labour & Skill planning."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("User Groups", "4")
    col2.metric("Districts in Sample", len(district_data))
    col3.metric("Skill Categories", len(skill_demand))
    col4.metric("Sectors", len(sector_demand))

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

    st.subheader("District Overview — Sample Data")
    st.dataframe(district_data, use_container_width=True)

# ==========================================
# 8. USERS PAGE
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
# 9. DISTRICT ADMIN DASHBOARD
# ==========================================

elif st.session_state.page == "District Admin Dashboard":

    st.header("District Admin - Labour & Skill")
    st.write(
        "Understand district-level employment, skill demand, "
        "job openings, hiring companies and training outcomes."
    )

    # District filter
    selected_district = st.selectbox(
        "Select District",
        district_data["District"].tolist()
    )

    selected_row = district_data[
        district_data["District"] == selected_district
    ].iloc[0]

    st.subheader("Employment and Job Openings")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Employed Students",
        int(selected_row["Employed Students"])
    )

    c2.metric(
        "Unemployed Students",
        int(selected_row["Unemployed Students"])
    )

    c3.metric(
        "Job Openings",
        int(selected_row["Job Openings"])
    )

    st.divider()

    # Pain 1: Growing sectors and skills
    st.subheader("1. Which Sectors and Skills Are Growing?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill-wise Demand")
        st.bar_chart(
            skill_demand.set_index("Skill")["Openings"]
        )

    with col2:
        st.markdown("#### Sector-wise Demand")
        st.bar_chart(
            sector_demand.set_index("Sector")["Openings"]
        )

    # Pain 2: Employment and unemployment
    st.divider()
    st.subheader("2. Employed and Unemployed Students")

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

    st.bar_chart(
        district_data.set_index("District")[
            ["Employed Students", "Unemployed Students"]
        ]
    )

    # Pain 3: Openings by district
    st.divider()
    st.subheader("3. Job Openings — District-wise")

    st.bar_chart(
        district_data.set_index("District")["Job Openings"]
    )

    # Pain 4: Hiring companies
    st.divider()
    st.subheader("4. Hiring Companies")

    st.write(
        "This section will display company details, sectors, "
        "skills required, vacancies and hiring activity."
    )

    hiring_companies = pd.DataFrame({
        "Company": [
            "ABC Technologies",
            "Karnataka Manufacturing Ltd.",
            "Healthcare Services Ltd."
        ],
        "Sector": [
            "IT",
            "Manufacturing",
            "Healthcare"
        ],
        "Skill Required": [
            "Python and Data Analytics",
            "Welding and Electrical",
            "Healthcare Support"
        ],
        "Openings": [50, 35, 25]
    })

    st.dataframe(hiring_companies, use_container_width=True)

    # Pain 5: Job fairs
    st.divider()
    st.subheader("5. Job Fair Performance")

    st.dataframe(job_fair_data, use_container_width=True)

    fair_row = job_fair_data[
        job_fair_data["District"] == selected_district
    ].iloc[0]

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

    # Pain 6: Training institutes
    st.divider()
    st.subheader("6. Training Institute Performance")

    st.dataframe(institute_data, use_container_width=True)

    st.bar_chart(
        institute_data.set_index("Institute")[
            ["Students Enrolled", "Students Skilled", "Students Placed"]
        ]
    )

# ==========================================
# 10. STATE ADMIN
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

# ==========================================
# 11. TRAINING INSTITUTES
# ==========================================

elif st.session_state.page == "Training Institutes":

    st.header("Training Institutes")

    st.write(
        "Track student enrolment, students who complete training, "
        "and students who get placed."
    )

    st.dataframe(institute_data, use_container_width=True)

    st.subheader("Student Training Outcomes")

    st.bar_chart(
        institute_data.set_index("Institute")[
            ["Students Enrolled", "Students Skilled", "Students Placed"]
        ]
    )

# ==========================================
# 12. JOB FAIR COMPANIES
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

# ==========================================
# 13. ANALYTICS - AI SKILL PLANNING
# ==========================================

elif st.session_state.page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")

    st.write(
        "This module will help district administrators create "
        "skill plans based on unemployment, skill gaps and demand."
    )

    st.subheader("Generate a Skill Planning Report")

    district = st.selectbox(
        "Choose District",
        district_data["District"].tolist(),
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
        row = district_data[
            district_data["District"] == district
        ].iloc[0]

        st.subheader("Sample Skill Planning Report")

        st.write(f"**District:** {district}")
        st.write(f"**Planning Focus:** {focus}")
        st.write(
            f"**Unemployed Students:** "
            f"{int(row['Unemployed Students'])}"
        )
        st.write(
            f"**Available Job Openings:** "
            f"{int(row['Job Openings'])}"
        )

        st.info(
            "This is a basic sample report generated from demo data. "
            "AI-generated skill-gap analysis and recommendations "
            "will be added in the next development step."
        )

    st.divider()

    st.subheader("Planned Analytics Features")

    st.markdown("""
    - Skill Gap Report
    - Skill Trend Report
    - AI-generated Skill Plans
    - Training Institute Ranking
    - Job Fair Company Selection
    - Hiring Company Recommendations
    - Sector Recommendations for Hiring
    """)

# ==========================================
# 14. PLANS
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
# 15. EXECUTED
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
# 16. RESULTS
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
# 17. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | Initial Development Version"
)
