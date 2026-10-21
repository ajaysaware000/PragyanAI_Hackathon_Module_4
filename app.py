
import streamlit as st
import pandas as pd
from datetime import date

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="District Labour & Skill Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. PROFESSIONAL DESIGN
# ==================================================

st.markdown("""
<style>
.stApp {
    background-color: #F4F7FB;
}
[data-testid="stSidebar"] {
    background-color: #102D46;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 5px 4px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: #234D6B;
    border-radius: 6px;
}
.portal-title {
    font-size: 28px;
    font-weight: 750;
    color: #123B5D;
}
.portal-subtitle {
    color: #65788A;
    font-size: 14px;
}
.kpi-card {
    background: white;
    border: 1px solid #DFE7F0;
    border-radius: 12px;
    padding: 18px;
}
.kpi-label {
    color: #60758A;
    font-size: 13px;
}
.kpi-value {
    color: #123B5D;
    font-size: 27px;
    font-weight: 750;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DFE7F0;
    border-radius: 10px;
    padding: 14px;
}
.stButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 3. SAMPLE DATA
# These figures are for demonstration only.
# ==================================================

districts = pd.DataFrame({
    "District": [
        "Bengaluru Urban", "Belagavi", "Mysuru",
        "Kalaburagi", "Dharwad"
    ],
    "Employed": [7200, 4800, 5600, 3100, 4200],
    "Unemployed": [1800, 2200, 1600, 2900, 2100],
    "Vacancies": [3200, 1400, 1900, 900, 1300],
    "Training Enrolment": [1600, 1200, 1100, 950, 1000]
})

skills = pd.DataFrame({
    "Skill": [
        "Python", "Data Analytics", "Electrician",
        "Welding", "Healthcare Support", "Solar Technician"
    ],
    "Sector": [
        "IT", "IT", "Manufacturing",
        "Manufacturing", "Healthcare", "Renewable Energy"
    ],
    "Demand": [850, 700, 620, 480, 550, 420],
    "Available Candidates": [420, 380, 500, 360, 300, 190]
})

institutes = pd.DataFrame({
    "Institute": [
        "District Skill Centre",
        "Government ITI",
        "Technical Training Institute",
        "Advanced Skills Academy",
        "Community Training Centre"
    ],
    "District": [
        "Bengaluru Urban", "Belagavi", "Mysuru",
        "Kalaburagi", "Dharwad"
    ],
    "Enrolled": [500, 420, 380, 300, 350],
    "Skilled": [430, 350, 320, 240, 290],
    "Placed": [310, 230, 220, 150, 210]
})

companies = pd.DataFrame({
    "Company": [
        "ABC Technologies",
        "Karnataka Manufacturing Ltd.",
        "HealthFirst Services",
        "SolarWorks India",
        "Digital Solutions Pvt Ltd"
    ],
    "Sector": [
        "IT", "Manufacturing", "Healthcare",
        "Renewable Energy", "IT"
    ],
    "District": [
        "Bengaluru Urban", "Belagavi", "Mysuru",
        "Kalaburagi", "Dharwad"
    ],
    "Skill Required": [
        "Python", "Welding", "Healthcare Support",
        "Solar Technician", "Data Analytics"
    ],
    "Vacancies": [150, 90, 70, 60, 110],
    "Students Hired": [82, 45, 0, 24, 0]
})

job_fairs = pd.DataFrame({
    "District": districts["District"],
    "Fairs Conducted": [8, 5, 6, 3, 4],
    "Students Participated": [900, 560, 680, 320, 440],
    "Students Placed": [540, 300, 390, 160, 250],
    "Companies Participated": [42, 28, 32, 16, 22],
    "Companies Hired": [31, 19, 23, 11, 16]
})

# ==================================================
# 4. SESSION STATE
# ==================================================

defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "users": {},
    "plans": [],
    "executions": [],
    "activities": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==================================================
# 5. LOGIN AND REGISTRATION
# ==================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="portal-title">'
        'District Labour & Skill Intelligence Portal</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="portal-subtitle">'
        'Employment • Skill Development • District Planning</div>',
        unsafe_allow_html=True
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with register_tab:
        st.subheader("Create an Account")

        reg_username = st.text_input(
            "Username", key="register_username"
        )
        reg_password = st.text_input(
            "Password", type="password", key="register_password"
        )
        reg_role = st.selectbox(
            "Select Role",
            [
                "District Admin - Labour & Skill",
                "State Admin - Labour & Skill",
                "Training Institute",
                "Job Fair Company"
            ],
            key="register_role"
        )

        if st.button("Register", use_container_width=True):
            if not reg_username.strip() or not reg_password:
                st.error("Enter both username and password.")
            elif reg_username in st.session_state.users:
                st.error("This username already exists.")
            else:
                st.session_state.users[reg_username] = {
                    "password": reg_password,
                    "role": reg_role
                }
                st.success(
                    "Account created. Open the Login tab to continue."
                )

    with login_tab:
        st.subheader("Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input(
            "Password", type="password", key="login_password"
        )

        if st.button("Login", use_container_width=True):
            account = st.session_state.users.get(username)

            if account and account["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = account["role"]
                st.rerun()
            else:
                st.error(
                    "Invalid login. Register an account first "
                    "or check your credentials."
                )

    st.info(
        "Demo authentication only. Accounts are held in the current "
        "session. Secure authentication and a database are needed "
        "before production deployment."
    )

    st.stop()

# ==================================================
# 6. SINGLE SIDEBAR NAVIGATION
# This replaces the conflicting radio menus and dropdown.
# ==================================================

PAGES = [
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

with st.sidebar:
    st.markdown("## 🏛️ SKILL PORTAL")
    st.caption("LABOUR & SKILL ADMINISTRATION")
    st.divider()

    st.markdown("### OVERVIEW")

    overview_page = st.radio(
        "Overview pages",
        ["Explore Dashboard", "Users"],
        key="overview_navigation",
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### MONITORING")

    monitoring_page = st.radio(
        "Monitoring pages",
        [
            "District Admin Dashboard",
            "State Admin",
            "Training Institutes",
            "Job Fair Companies"
        ],
        key="monitoring_navigation",
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### INTELLIGENCE & ACTION")

    action_page = st.radio(
        "Planning pages",
        [
            "Analytics - AI Skill Planning",
            "Plans",
            "Executed",
            "Results"
        ],
        key="action_navigation",
        label_visibility="collapsed"
    )

    # Determine the selected page from the one active menu.
    # Use separate menus with their own selected values.
    # The final selected page is resolved using the last changed menu.
    if "active_section" not in st.session_state:
        st.session_state.active_section = "overview"

    # A single unified selector is provided below as the source
    # of truth for navigation, avoiding conflicting page states.
    st.divider()
    st.caption(f"Signed in: {st.session_state.username}")
    st.caption(st.session_state.role)

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

# ==================================================
# 7. RESOLVE NAVIGATION
# One page selector controls the entire application.
# ==================================================

# We use one actual navigation selector, grouped by category.
# Streamlit radio options can be changed without duplicate keys.

with st.sidebar:
    st.markdown("### OPEN PAGE")

    page = st.selectbox(
        "Choose a page",
        PAGES,
        key="active_page",
        label_visibility="collapsed"
    )

# ==================================================
# 8. SHARED HEADER
# ==================================================

st.markdown(
    '<div class="portal-title">'
    'District Labour & Skill Intelligence</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="portal-subtitle">'
    'Employment monitoring | Skill demand | Training | Hiring outcomes'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    f"User: {st.session_state.username}  |  "
    f"Role: {st.session_state.role}  |  "
    f"Date: {date.today().strftime('%d %b %Y')}"
)
st.divider()

def show_kpi(label, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def add_activity(message):
    st.session_state.activities.append({
        "Date": str(date.today()),
        "Activity": message,
        "User": st.session_state.username
    })

# ==================================================
# 9. EXPLORE DASHBOARD
# ==================================================

if page == "Explore Dashboard":

    st.header("Explore Dashboard")
    st.write(
        "Overview of district employment, skill demand and "
        "training activity."
    )

    a, b, c, d = st.columns(4)

    with a:
        show_kpi("Districts", len(districts))
    with b:
        show_kpi("Employed Students", f"{districts['Employed'].sum():,}")
    with c:
        show_kpi("Unemployed Students",
                 f"{districts['Unemployed'].sum():,}")
    with d:
        show_kpi("Job Vacancies", f"{districts['Vacancies'].sum():,}")

    st.subheader("Employment by District")

    st.bar_chart(
        districts.set_index("District")[["Employed", "Unemployed"]]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Skill Demand")
        st.bar_chart(skills.set_index("Skill")["Demand"])

    with col2:
        st.subheader("Job Openings by District")
        st.bar_chart(districts.set_index("District")["Vacancies"])

    st.subheader("District Summary")
    st.dataframe(districts, use_container_width=True, hide_index=True)

    st.subheader("Recent Activity")
    if st.session_state.activities:
        st.dataframe(
            pd.DataFrame(st.session_state.activities),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Activity will appear here when you create plans or updates.")

# ==================================================
# 10. USERS
# ==================================================

elif page == "Users":

    st.header("Users & Access")
    st.write("Review accounts registered during this demo session.")

    if st.session_state.users:
        rows = [
            {
                "Username": name,
                "Role": data["role"],
                "Status": "Registered"
            }
            for name, data in st.session_state.users.items()
        ]
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No accounts registered in this session.")

    st.subheader("Role Responsibilities")

    roles = pd.DataFrame({
        "Role": [
            "District Admin - Labour & Skill",
            "State Admin - Labour & Skill",
            "Training Institute",
            "Job Fair Company"
        ],
        "Responsibility": [
            "District-level skill and employment planning",
            "State-wide monitoring and district comparison",
            "Training, student progress and placement",
            "Vacancies, recruitment and hiring outcomes"
        ]
    })

    st.dataframe(roles, use_container_width=True, hide_index=True)

# ==================================================
# 11. DISTRICT ADMIN DASHBOARD
# ==================================================

elif page == "District Admin Dashboard":

    st.header("District Admin Dashboard")

    selected_district = st.selectbox(
        "Select District",
        districts["District"].tolist()
    )

    row = districts[districts["District"] == selected_district].iloc[0]
    fair = job_fairs[job_fairs["District"] == selected_district].iloc[0]

    a, b, c, d = st.columns(4)

    with a:
        show_kpi("Employed", f"{row['Employed']:,}")
    with b:
        show_kpi("Unemployed", f"{row['Unemployed']:,}")
    with c:
        show_kpi("Job Openings", f"{row['Vacancies']:,}")
    with d:
        show_kpi("Training Enrolment", f"{row['Training Enrolment']:,}")

    st.subheader("Skill Demand vs Available Candidates")

    st.bar_chart(
        skills.set_index("Skill")[["Demand", "Available Candidates"]]
    )

    st.subheader("Sector-wise Demand")

    sector_data = skills.groupby("Sector")["Demand"].sum()
    st.bar_chart(sector_data)

    st.subheader("Hiring Companies")

    district_companies = companies[
        companies["District"] == selected_district
    ]

    st.dataframe(
        district_companies,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Job Fair Outcomes")

    a, b, c = st.columns(3)

    with a:
        show_kpi("Fairs Conducted", int(fair["Fairs Conducted"]))
    with b:
        show_kpi("Students Participated",
                 int(fair["Students Participated"]))
    with c:
        show_kpi("Students Placed", int(fair["Students Placed"]))

    st.subheader("All Districts")
    st.dataframe(districts, use_container_width=True, hide_index=True)

# ==================================================
# 12. STATE ADMIN
# ==================================================

elif page == "State Admin":

    st.header("State Admin")
    st.write("Compare employment and skill indicators across districts.")

    indicator = st.selectbox(
        "Select Indicator",
        ["Employed", "Unemployed", "Vacancies", "Training Enrolment"]
    )

    st.bar_chart(districts.set_index("District")[indicator])

    st.subheader("District Comparison")
    st.dataframe(
        districts.sort_values(indicator, ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Districts with Highest Unemployment")

    st.dataframe(
        districts.sort_values("Unemployed", ascending=False).head(3),
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# 13. TRAINING INSTITUTES
# ==================================================

elif page == "Training Institutes":

    st.header("Training Institutes")

    selected_district = st.selectbox(
        "Filter by District",
        ["All Districts"] + districts["District"].tolist()
    )

    view = institutes.copy()

    if selected_district != "All Districts":
        view = view[view["District"] == selected_district]

    a, b, c = st.columns(3)

    with a:
        show_kpi("Students Enrolled", f"{view['Enrolled'].sum():,}")
    with b:
        show_kpi("Students Skilled", f"{view['Skilled'].sum():,}")
    with c:
        show_kpi("Students Placed", f"{view['Placed'].sum():,}")

    st.subheader("Institute Performance")
    st.dataframe(view, use_container_width=True, hide_index=True)

    st.bar_chart(view.set_index("Institute")[["Enrolled", "Skilled", "Placed"]])

    ranking = view.copy()
    ranking["Placement Rate (%)"] = (
        100 * ranking["Placed"] / ranking["Enrolled"]
    ).round(1)

    ranking = ranking.sort_values("Placement Rate (%)", ascending=False)
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))

    st.subheader("Institute Ranking")
    st.dataframe(ranking, use_container_width=True, hide_index=True)

# ==================================================
# 14. JOB FAIR COMPANIES
# ==================================================

elif page == "Job Fair Companies":

    st.header("Job Fair Companies")

    sector = st.selectbox(
        "Select Sector",
        ["All Sectors"] + sorted(companies["Sector"].unique().tolist())
    )

    view = companies.copy()

    if sector != "All Sectors":
        view = view[view["Sector"] == sector]

    a, b, c = st.columns(3)

    with a:
        show_kpi("Companies", len(view))
    with b:
        show_kpi("Vacancies", f"{view['Vacancies'].sum():,}")
    with c:
        show_kpi("Students Hired", f"{view['Students Hired'].sum():,}")

    st.subheader("Company Register")
    st.dataframe(view, use_container_width=True, hide_index=True)

    st.subheader("Vacancies by Sector")
    st.bar_chart(view.groupby("Sector")["Vacancies"].sum())

    st.subheader("Job Fair Performance")
    st.dataframe(job_fairs, use_container_width=True, hide_index=True)

# ==================================================
# 15. AI SKILL PLANNING
# ==================================================

elif page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")

    district = st.selectbox(
        "Select District",
        districts["District"].tolist()
    )

    objective = st.selectbox(
        "Planning Objective",
        [
            "Reduce unemployment",
            "Address skill gaps",
            "Focus on growing sectors",
            "Prepare for job openings"
        ]
    )

    gap_data = skills.copy()
    gap_data["Skill Gap"] = (
        gap_data["Demand"] - gap_data["Available Candidates"]
    )

    st.subheader("Skill Gap Report")
    st.dataframe(
        gap_data.sort_values("Skill Gap", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(gap_data.set_index("Skill")["Skill Gap"])

    if st.button("Generate Recommendations", type="primary"):
        largest_gap = gap_data.sort_values(
            "Skill Gap", ascending=False
        ).iloc[0]

        district_row = districts[districts["District"] == district].iloc[0]

        st.success("Sample planning report generated.")

        st.write(f"**District:** {district}")
        st.write(f"**Objective:** {objective}")
        st.write(f"**Unemployed students in sample:** {district_row['Unemployed']:,}")
        st.write(f"**Largest skill gap:** {largest_gap['Skill']}")

        st.subheader("Suggested Actions")
        st.write(f"1. Assess training capacity for {largest_gap['Skill']}.")
        st.write("2. Contact companies with matching vacancies.")
        st.write("3. Review institute placement outcomes.")
        st.write("4. Monitor training completion and placements.")

        st.warning(
            "This is a rule-based demonstration, not a real AI model. "
            "The figures are illustrative."
        )

# ==================================================
# 16. PLANS
# ==================================================

elif page == "Plans":

    st.header("Plans & Reports")
    st.write("Create and review district skill development plans.")

    with st.form("plan_form"):
        name = st.text_input("Plan Title")
        district = st.selectbox(
            "District", districts["District"].tolist()
        )
        skill = st.selectbox("Target Skill", skills["Skill"].tolist())
        target = st.number_input(
            "Target Students", min_value=1, value=100
        )
        institute = st.selectbox(
            "Training Institute", institutes["Institute"].tolist()
        )
        company = st.selectbox(
            "Hiring Company", companies["Company"].tolist()
        )
        deadline = st.date_input("Target Completion Date")
        notes = st.text_area("Plan Description")

        submitted = st.form_submit_button("Save Plan")

    if submitted:
        if not name.strip():
            st.error("Enter a plan title.")
        else:
            plan = {
                "Plan ID": f"PLAN-{len(st.session_state.plans) + 1:03}",
                "Title": name,
                "District": district,
                "Skill": skill,
                "Target Students": int(target),
                "Institute": institute,
                "Company": company,
                "Deadline": str(deadline),
                "Status": "Planned",
                "Notes": notes
            }

            st.session_state.plans.append(plan)
            add_activity(f"Created skill plan: {name}")
            st.success("Plan saved for this session.")

    st.subheader("Saved Plans")

    if st.session_state.plans:
        st.dataframe(
            pd.DataFrame(st.session_state.plans),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "Download Plans CSV",
            pd.DataFrame(st.session_state.plans).to_csv(index=False),
            "skill_plans.csv",
            "text/csv"
        )
    else:
        st.info("No plans yet. Create a plan using the form above.")

# ==================================================
# 17. EXECUTED
# ==================================================

elif page == "Executed":

    st.header("Execution Tracking")

    if not st.session_state.plans:
        st.info("Create a plan first, then record its execution.")
    else:
        plan_labels = [
            f"{p['Plan ID']} — {p['Title']}"
            for p in st.session_state.plans
        ]

        chosen = st.selectbox("Select Plan", plan_labels)
        plan_index = plan_labels.index(chosen)
        selected_plan = st.session_state.plans[plan_index]

        with st.form("execution_form"):
            status = st.selectbox(
                "Execution Status",
                ["Not Started", "In Progress", "Completed", "On Hold"]
            )
            start_date = st.date_input("Actual Start Date")
            trained = st.number_input(
                "Students Trained",
                min_value=0,
                max_value=int(selected_plan["Target Students"]),
                value=0
            )
            placed = st.number_input(
                "Students Placed",
                min_value=0,
                max_value=int(selected_plan["Target Students"]),
                value=0
            )
            expenditure = st.number_input(
                "Expenditure (INR)",
                min_value=0,
                value=0,
                step=1000
            )
            notes = st.text_area("Execution Notes")

            save = st.form_submit_button("Save Execution Update")

        if save:
            execution = {
                "Plan ID": selected_plan["Plan ID"],
                "Plan Title": selected_plan["Title"],
                "District": selected_plan["District"],
                "Status": status,
                "Start Date": str(start_date),
                "Students Trained": int(trained),
                "Students Placed": int(placed),
                "Expenditure (INR)": int(expenditure),
                "Notes": notes
            }

            st.session_state.executions.append(execution)
            selected_plan["Status"] = status
            add_activity(f"Updated execution: {selected_plan['Title']}")
            st.success("Execution update saved.")

    st.subheader("Execution Register")

    if st.session_state.executions:
        st.dataframe(
            pd.DataFrame(st.session_state.executions),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "Download Execution CSV",
            pd.DataFrame(st.session_state.executions).to_csv(index=False),
            "execution_report.csv",
            "text/csv"
        )
    else:
        st.info("No execution updates have been recorded.")

# ==================================================
# 18. RESULTS
# ==================================================

elif page == "Results":

    st.header("Outcomes & Results")

    if st.session_state.executions:
        result = pd.DataFrame(st.session_state.executions)

        a, b, c = st.columns(3)

        with a:
            show_kpi(
                "Students Trained",
                f"{result['Students Trained'].sum():,}"
            )
        with b:
            show_kpi(
                "Students Placed",
                f"{result['Students Placed'].sum():,}"
            )
        with c:
            show_kpi(
                "Reported Expenditure",
                f"₹{result['Expenditure (INR)'].sum():,}"
            )

        st.subheader("Execution Outcomes")
        st.dataframe(result, use_container_width=True, hide_index=True)

        st.bar_chart(
            result.set_index("Plan Title")[
                ["Students Trained", "Students Placed"]
            ]
        )
    else:
        st.info(
            "Results will appear after you create plans and save "
            "execution updates."
        )

    st.subheader("Unemployment by District")
    st.bar_chart(districts.set_index("District")["Unemployed"])

    gap_data = skills.copy()
    gap_data["Skill Gap"] = (
        gap_data["Demand"] - gap_data["Available Candidates"]
    )

    st.subheader("Skill Gap by Skill")
    st.bar_chart(gap_data.set_index("Skill")["Skill Gap"])

    st.warning(
        "Historical records are needed to calculate real trends. "
        "The current charts show illustrative sample data only."
    )

# ==================================================
# 19. FOOTER
# ==================================================

st.divider()

st.caption(
    "District Labour & Skill Intelligence Portal | "
    "Demonstration Version | Sample Data"
)
