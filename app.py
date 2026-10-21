
import streamlit as st
import pandas as pd
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
    background-color: #F4F7FB;
}
[data-testid="stSidebar"] {
    background-color: #102D46;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
.main-title {
    font-size: 30px;
    font-weight: 750;
    color: #123B5D;
}
.subtitle {
    color: #63758A;
    font-size: 14px;
}
.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #173D5B;
}
.kpi {
    background: white;
    border: 1px solid #E1E8F0;
    border-radius: 12px;
    padding: 18px;
    min-height: 120px;
}
.kpi-label {
    color: #60758A;
    font-size: 13px;
}
.kpi-value {
    color: #123B5D;
    font-size: 28px;
    font-weight: 750;
}
.kpi-note {
    color: #27805C;
    font-size: 12px;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border: 1px solid #E1E8F0;
    border-radius: 12px;
}
.stButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. SAMPLE DATA
# All numbers below are illustrative, not official data.
# =====================================================

districts = pd.DataFrame({
    "District": [
        "Bengaluru Urban", "Belagavi",
        "Mysuru", "Kalaburagi", "Dharwad"
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
        "ABC Technologies", "Karnataka Manufacturing Ltd.",
        "HealthFirst Services", "SolarWorks India",
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
    "Participated in Job Fair": ["Yes", "Yes", "No", "Yes", "No"],
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

# =====================================================
# 4. SESSION STATE
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
# 5. LOGIN AND REGISTRATION
# Demo authentication only; do not use for production.
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
        "Demo version: accounts are stored in the current session. "
        "A production portal needs secure authentication and a database."
    )
    st.stop()

# =====================================================
# 6. SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("## 🏛️ SKILL INTELLIGENCE")
    st.caption("LABOUR & SKILL PORTAL")
    st.divider()

    st.write("SIGNED IN AS")
    st.markdown(f"**{st.session_state.username}**")
    st.caption(st.session_state.role)

    st.divider()
    st.caption("OVERVIEW")

    page = st.radio(
        "Overview",
        ["Explore Dashboard", "Users"],
        label_visibility="collapsed"
    )

    st.caption("MONITORING")

    monitoring_page = st.radio(
        "Monitoring",
        [
            "District Admin Dashboard",
            "State Admin",
            "Training Institutes",
            "Job Fair Companies"
        ],
        label_visibility="collapsed"
    )

    st.caption("INTELLIGENCE & ACTION")

    action_page = st.radio(
        "Intelligence and Action",
        [
            "Analytics - AI Skill Planning",
            "Plans",
            "Executed",
            "Results"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# Resolve selected page
# The first radio is the default page; other menus take priority
# when their current selection is changed.
if "last_page" not in st.session_state:
    st.session_state.last_page = "Explore Dashboard"

# Read the radio widget values
overview_value = st.session_state.get("Overview", "Explore Dashboard")
monitoring_value = st.session_state.get(
    "Monitoring", "District Admin Dashboard"
)
action_value = st.session_state.get(
    "Intelligence and Action", "Analytics - AI Skill Planning"
)

# Use a single effective page selected by the changed menu.
# The sidebar also offers direct selection below for clarity.
with st.sidebar:
    st.caption("QUICK PAGE SELECT")
    selected_page = st.selectbox(
        "Open page",
        [
            "Explore Dashboard", "Users",
            "District Admin Dashboard", "State Admin",
            "Training Institutes", "Job Fair Companies",
            "Analytics - AI Skill Planning", "Plans",
            "Executed", "Results"
        ],
        key="quick_page"
    )

page = selected_page

# =====================================================
# 7. SHARED HEADER AND HELPERS
# =====================================================

st.markdown(
    '<div class="main-title">District Labour & Skill Intelligence</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Employment monitoring • Skill-gap analysis '
    '• Training coordination • Outcome tracking</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Signed in as {st.session_state.username}  |  "
    f"{st.session_state.role}  |  {date.today().strftime('%d %b %Y')}"
)
st.divider()

def kpi(label, value, note="Illustrative demo data"):
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
    st.markdown(f'<div class="section-title">{title}</div>',
                unsafe_allow_html=True)
    st.caption(description)

def get_placement_rate(frame):
    total = frame["Enrolled"].sum()
    placed = frame["Placed"].sum()
    return round(100 * placed / total, 1) if total else 0

# =====================================================
# 8. PAGE 1: EXPLORE DASHBOARD
# =====================================================

if page == "Explore Dashboard":

    page_title(
        "Explore Dashboard",
        "A consolidated overview of employment, skill demand and training."
    )

    total_employed = districts["Employed"].sum()
    total_unemployed = districts["Unemployed"].sum()
    total_vacancies = districts["Vacancies"].sum()
    total_placed = institutes["Placed"].sum()

    a, b, c, d = st.columns(4)
    with a:
        kpi("Districts Covered", len(districts))
    with b:
        kpi("Employed Students", f"{total_employed:,}")
    with c:
        kpi("Unemployed Students", f"{total_unemployed:,}")
    with d:
        kpi("Reported Vacancies", f"{total_vacancies:,}")

    st.write("")
    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Employment by District")
        chart_data = districts.set_index("District")[
            ["Employed", "Unemployed"]
        ]
        st.bar_chart(chart_data)

    with right:
        st.subheader("Highest Skill Demand")
        top_skills = skills.sort_values("Demand", ascending=False).head(5)
        st.bar_chart(top_skills.set_index("Skill")["Demand"])

    st.subheader("District Performance Register")
    st.dataframe(districts, use_container_width=True, hide_index=True)

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

    st.caption("All figures on this demo screen are illustrative.")

# =====================================================
# 9. PAGE 2: USERS
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
        "This is not a secure user-management system. "
        "Role-based page permissions and database-backed accounts "
        "must be added before deployment."
    )

# =====================================================
# 10. PAGE 3: DISTRICT ADMIN DASHBOARD
# =====================================================

elif page == "District Admin Dashboard":

    page_title(
        "District Admin Dashboard",
        "Monitor district employment conditions and identify priority skills."
    )

    selected_district = st.selectbox(
        "District",
        districts["District"].tolist()
    )

    district_row = districts[
        districts["District"] == selected_district
    ].iloc[0]

    district_fair = job_fairs[
        job_fairs["District"] == selected_district
    ].iloc[0]

    a, b, c, d = st.columns(4)

    with a:
        kpi("Employed", f"{district_row['Employed']:,}")
    with b:
        kpi("Unemployed", f"{district_row['Unemployed']:,}")
    with c:
        kpi("Job Vacancies", f"{district_row['Vacancies']:,}")
    with d:
        kpi("Training Enrolment", f"{district_row['Training Enrolment']:,}")

    st.subheader("Skill Demand vs Candidate Availability")

    skill_filter = st.multiselect(
        "Filter by skill",
        skills["Skill"].tolist(),
        default=skills["Skill"].tolist()
    )

    filtered_skills = skills[skills["Skill"].isin(skill_filter)]

    st.bar_chart(
        filtered_skills.set_index("Skill")[
            ["Demand", "Available Candidates"]
        ]
    )

    st.subheader("Sector-wise Demand")

    sector_summary = (
        skills.groupby("Sector", as_index=False)["Demand"]
        .sum()
        .sort_values("Demand", ascending=False)
    )

    st.bar_chart(sector_summary.set_index("Sector")["Demand"])

    st.subheader("Job Fair Outcomes")

    a, b, c = st.columns(3)
    with a:
        kpi("Fairs Conducted", int(district_fair["Fairs Conducted"]))
    with b:
        kpi("Students Participated",
            f"{int(district_fair['Students Participated']):,}")
    with c:
        kpi("Students Placed",
            f"{int(district_fair['Students Placed']):,}")

    st.subheader("Hiring Companies and Openings")

    company_filter = companies[
        companies["District"] == selected_district
    ]

    st.dataframe(
        company_filter,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("District Summary")
    st.dataframe(districts, use_container_width=True, hide_index=True)

# =====================================================
# 11. PAGE 4: STATE ADMIN
# =====================================================

elif page == "State Admin":

    page_title(
        "State Admin",
        "Compare district indicators and identify where support is needed."
    )

    a, b, c = st.columns(3)
    with a:
        kpi("Districts Monitored", len(districts))
    with b:
        kpi("Total Unemployed", f"{districts['Unemployed'].sum():,}")
    with c:
        kpi("Total Vacancies", f"{districts['Vacancies'].sum():,}")

    st.subheader("Compare Districts")

    indicator = st.selectbox(
        "Choose indicator",
        ["Employed", "Unemployed", "Vacancies", "Training Enrolment"]
    )

    comparison = districts.sort_values(indicator, ascending=False)

    st.bar_chart(comparison.set_index("District")[indicator])
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.subheader("Districts Requiring Attention")

    priority = districts.sort_values("Unemployed", ascending=False).head(3)

    st.dataframe(
        priority[["District", "Unemployed", "Vacancies"]],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Priority is based on the sample unemployment count only. "
        "Real policy decisions need validated population and employment data."
    )

# =====================================================
# 12. PAGE 5: TRAINING INSTITUTES
# =====================================================

elif page == "Training Institutes":

    page_title(
        "Training Institutes",
        "Monitor enrolment, skill completion and employment outcomes."
    )

    selected_institute_district = st.selectbox(
        "Filter district",
        ["All Districts"] + districts["District"].tolist()
    )

    institute_view = institutes.copy()

    if selected_institute_district != "All Districts":
        institute_view = institute_view[
            institute_view["District"] == selected_institute_district
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

    ranked = ranked.sort_values("Placement Rate (%)", ascending=False)
    ranked.insert(0, "Rank", range(1, len(ranked) + 1))

    st.dataframe(ranked, use_container_width=True, hide_index=True)

# =====================================================
# 13. PAGE 6: JOB FAIR COMPANIES
# =====================================================

elif page == "Job Fair Companies":

    page_title(
        "Job Fair Companies",
        "Track hiring demand, company participation and recruitment results."
    )

    sector_filter = st.selectbox(
        "Sector",
        ["All Sectors"] + sorted(companies["Sector"].unique().tolist())
    )

    company_view = companies.copy()

    if sector_filter != "All Sectors":
        company_view = company_view[
            company_view["Sector"] == sector_filter
        ]

    a, b, c = st.columns(3)

    with a:
        kpi("Companies Listed", len(company_view))
    with b:
        kpi("Vacancies Listed", f"{company_view['Vacancies'].sum():,}")
    with c:
        kpi("Students Hired", f"{company_view['Students Hired'].sum():,}")

    st.subheader("Company Register")
    st.dataframe(company_view, use_container_width=True, hide_index=True)

    st.subheader("Vacancies by Sector")

    sector_vacancies = (
        company_view.groupby("Sector", as_index=False)["Vacancies"]
        .sum()
    )

    st.bar_chart(sector_vacancies.set_index("Sector")["Vacancies"])

    st.subheader("Job Fair Performance by District")

    st.dataframe(job_fairs, use_container_width=True, hide_index=True)

    st.bar_chart(
        job_fairs.set_index("District")[
            ["Companies Participated", "Companies Hired"]
        ]
    )

# =====================================================
# 14. PAGE 7: ANALYTICS - AI SKILL PLANNING
# =====================================================

elif page == "Analytics - AI Skill Planning":

    page_title(
        "AI Skill Planning & Analytics",
        "Generate a preliminary skill-gap report and planning suggestions."
    )

    selected_district = st.selectbox(
        "Planning district",
        districts["District"].tolist(),
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

    skill_analysis = skills.copy()

    skill_analysis["Skill Gap"] = (
        skill_analysis["Demand"]
        - skill_analysis["Available Candidates"]
    )

    skill_analysis["Priority"] = skill_analysis["Skill Gap"].apply(
        lambda gap: "High" if gap >= 300
        else ("Medium" if gap >= 150 else "Monitor")
    )

    st.subheader("Skill Gap Report")

    st.dataframe(
        skill_analysis.sort_values("Skill Gap", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        skill_analysis.set_index("Skill")["Skill Gap"]
    )

    st.subheader("Generate Planning Recommendations")

    if st.button("Generate Recommendations", type="primary"):

        highest_gap = skill_analysis.sort_values(
            "Skill Gap", ascending=False
        ).iloc[0]

        district_row = districts[
            districts["District"] == selected_district
        ].iloc[0]

        st.success("Preliminary report generated.")

        st.markdown(f"**District:** {selected_district}")
        st.markdown(f"**Objective:** {planning_focus}")
        st.markdown(
            f"**Unemployed students in sample:** "
            f"{int(district_row['Unemployed']):,}"
        )
        st.markdown(
            f"**Largest sample skill gap:** {highest_gap['Skill']}"
        )

        st.markdown("#### Suggested Actions")

        st.write(
            f"1. Assess training capacity for {highest_gap['Skill']}."
        )
        st.write(
            "2. Contact companies with vacancies matching the identified skills."
        )
        st.write(
            "3. Review institute placement performance before selecting providers."
        )
        st.write(
            "4. Track enrolment, training completion and placements after execution."
        )

        st.warning(
            "These are rule-based suggestions from illustrative data, "
            "not AI-generated or verified policy recommendations."
        )

    st.subheader("Potential Planning Actions")

    st.markdown("""
    - Identify high-demand skills with limited candidate availability.
    - Rank training institutes using placement and completion outcomes.
    - Match hiring companies to training plans.
    - Recommend sectors for upcoming job fairs.
    - Produce skill-gap and skill-trend reports.
    """)

# =====================================================
# 15. PAGE 8: PLANS
# =====================================================

elif page == "Plans":

    page_title(
        "Skill Plans & Reports",
        "Create a plan, define targets and review saved planning records."
    )

    with st.form("create_plan_form"):
        plan_name = st.text_input(
            "Plan title",
            placeholder="Example: District Data Analytics Training Plan"
        )

        plan_district = st.selectbox(
            "District",
            districts["District"].tolist()
        )

        plan_skill = st.selectbox(
            "Target skill",
            skills["Skill"].tolist()
        )

        target_students = st.number_input(
            "Target students to train",
            min_value=1,
            max_value=100000,
            value=100
        )

        training_institute = st.selectbox(
            "Proposed training institute",
            institutes["Institute"].tolist()
        )

        hiring_company = st.selectbox(
            "Proposed hiring company",
            companies["Company"].tolist()
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
                "Hiring Company": hiring_company,
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
    else:
        st.info("No plans saved yet. Create your first skill plan above.")

    if st.session_state.plans:
        st.download_button(
            "Download Plans as CSV",
            pd.DataFrame(st.session_state.plans).to_csv(index=False),
            file_name="skill_plans.csv",
            mime="text/csv"
        )

# =====================================================
# 16. PAGE 9: EXECUTED
# =====================================================

elif page == "Executed":

    page_title(
        "Execution Tracking",
        "Record when a plan starts, track progress and document outcomes."
    )

    if not st.session_state.plans:
        st.info("Create a skill plan first, then track its execution here.")
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

            save_execution = st.form_submit_button("Save Execution Update")

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
                "Activity": f"Execution updated: {selected_plan_record['Plan Title']}",
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
# 17. PAGE 10: RESULTS
# =====================================================

elif page == "Results":

    page_title(
        "Outcomes & Results",
        "Review training outputs, placements and indicators requiring follow-up."
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
            kpi("Planned Student Targets", f"{target_students_total:,}")
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
            "No execution results are available yet. Create a plan, "
            "record an execution update, and return here to review outcomes."
        )

    st.subheader("Employment and Skill-Gap Indicators")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Unemployment by District")
        st.bar_chart(districts.set_index("District")["Unemployed"])

    with right:
        st.markdown("#### Skill Gap by Skill")

        result_skills = skills.copy()
        result_skills["Skill Gap"] = (
            result_skills["Demand"]
            - result_skills["Available Candidates"]
        )

        st.bar_chart(result_skills.set_index("Skill")["Skill Gap"])

    st.warning(
        "Actual trends require dated historical records. "
        "These charts show sample current values, not verified trends "
        "or proof that a plan caused a change in unemployment."
    )

# =====================================================
# 18. FOOTER
# =====================================================

st.divider()

st.caption(
    "District Labour & Skill Intelligence Portal | "
    "Demonstration build | Sample data only"
)
