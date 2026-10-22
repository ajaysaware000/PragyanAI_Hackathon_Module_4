import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Labour & Skill Planning with AI Chart Bot",
    page_icon="🎯",
    layout="wide"
)

# ==========================================
# 2. SAMPLE DATA
# Real-world calibrated district intelligence
# ==========================================

skill_demand = pd.DataFrame({
    "Skill": ["Python & AI", "Data Analytics", "Industrial Automation", "Electrician", "Solar PV Tech", "Welding & CNC", "Healthcare Support"],
    "Openings": [320, 240, 210, 200, 180, 150, 160],
    "Growth Rate (%)": [38.5, 24.0, 28.5, 12.0, 34.0, 14.5, 18.0]
})

sector_demand = pd.DataFrame({
    "Sector": ["IT & Deep Tech", "Advanced Manufacturing", "Clean Energy", "Healthcare", "Construction & Infra", "Agro-Logistics"],
    "Openings": [450, 310, 240, 180, 150, 190],
    "Growth Rate (%)": [32.0, 18.5, 36.0, 15.0, 9.5, 21.0]
})

district_data = pd.DataFrame({
    "District": ["Bengaluru Urban", "Belagavi", "Mysuru", "Kalaburagi", "Dharwad", "Raichur"],
    "Employed Students": [1200, 850, 900, 600, 780, 480],
    "Unemployed Students": [300, 420, 350, 500, 320, 450],
    "Job Openings": [1400, 650, 720, 420, 580, 310]
})

job_fair_data = pd.DataFrame({
    "District": ["Bengaluru Urban", "Belagavi", "Mysuru", "Kalaburagi", "Dharwad", "Raichur"],
    "Job Fairs Conducted": [8, 5, 6, 3, 4, 3],
    "Students Participated": [800, 450, 600, 300, 410, 280],
    "Students Placed": [500, 260, 350, 140, 240, 110],
    "Companies Participated": [40, 25, 30, 15, 22, 14],
    "Companies Hired": [32, 18, 22, 10, 17, 9]
})

institute_data = pd.DataFrame({
    "Institute": [
        "Government Model ITI",
        "GTTC Toolroom & Training Centre",
        "Karnataka Govt Polytechnic",
        "Tata-KSDC Advanced Technology Centre",
        "District Vocational Centre"
    ],
    "District": ["Kalaburagi", "Belagavi", "Mysuru", "Dharwad", "Bengaluru Urban"],
    "Students Enrolled": [350, 280, 310, 240, 420],
    "Students Skilled": [310, 250, 270, 220, 390],
    "Students Placed": [230, 205, 190, 185, 340]
})
institute_data["Placement Rate (%)"] = ((institute_data["Students Placed"] / institute_data["Students Skilled"]) * 100).round(1)

hiring_companies = pd.DataFrame({
    "Company": [
        "ABC Technologies", "Karnataka Manufacturing Ltd.", "Healthcare Services Ltd.",
        "KREDL Solar Energy", "Tata Technologies", "Bosch India", "Aequs Aerospace"
    ],
    "District": ["Bengaluru Urban", "Belagavi", "Mysuru", "Kalaburagi", "Dharwad", "Bengaluru Urban", "Belagavi"],
    "Sector": ["IT & Deep Tech", "Manufacturing", "Healthcare", "Clean Energy", "Manufacturing", "IT & Deep Tech", "Aerospace"],
    "Skill Required": [
        "Python and Data Analytics", "Welding and CNC", "Healthcare Support",
        "Solar PV and Inverters", "Industrial Automation", "Cloud DevOps", "Precision Tooling"
    ],
    "Openings": [120, 65, 40, 85, 70, 95, 55]
})

# ==========================================
# 3. SESSION STATE
# Pre-populated with demo credentials
# ==========================================

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "State Admin - Labour & Skill"},
        "district_officer": {"password": "pass123", "role": "District Admin - Labour & Skill"},
        "iti_principal": {"password": "pass123", "role": "Training Institute"},
        "hr_lead": {"password": "pass123", "role": "Job Fair Company"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Demo login active

if "username" not in st.session_state:
    st.session_state.username = "district_officer"

if "page" not in st.session_state:
    st.session_state.page = "Explore Dashboard"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am your AI Chart & Labour Intelligence Bot.**\n\nAsk me any question about Karnataka districts, skill demand, unemployment, job fairs, or training institutes. I can generate text answers **and plot interactive visual charts** for you instantly!\n\n*Try asking:*\n- *'Plot job openings by sector'*\n- *'Show employed vs unemployed students by district'*\n- *'Compare job fair placements'*\n- *'Rank training institutes'*",
            "chart": None
        }
    ]

# ==========================================
# 4. APPLICATION HEADER
# ==========================================

st.title("🎯 Labour & Skill Planning System")
st.caption("District-level employment, skill demand, training planning & AI Chart Bot")

# ==========================================
# 5. REGISTER AND LOGIN
# ==========================================

if not st.session_state.logged_in:

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with register_tab:
        st.subheader("Create an Account")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
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
                st.success("Registration successful! Open the Login tab to sign in.")

    with login_tab:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username", value="district_officer")
        password = st.text_input("Password", type="password", key="login_password", value="pass123")

        st.caption("💡 **Demo Accounts**: `admin` / `admin123` (State Admin) | `district_officer` / `pass123` (District Admin)")

        if st.button("Login", use_container_width=True):
            user = st.session_state.users.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "Explore Dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password. Register first if you do not have an account.")

    st.info("Demonstration session authentication. Accounts persist in memory during the app lifecycle.")
    st.stop()

# ==========================================
# 6. SIDEBAR NAVIGATION
# ==========================================

user = st.session_state.users.get(st.session_state.username, {"role": "District Admin - Labour & Skill"})

st.sidebar.title("Navigation")
st.sidebar.markdown(f"**Logged in as:** `{st.session_state.username}`")
st.sidebar.markdown(f"**Role:** `{user['role']}`")

pages = [
    "Explore Dashboard",
    "🤖 AI Chart Bot",
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
    index=pages.index(st.session_state.page) if st.session_state.page in pages else 0
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
    st.write("Explore the users and organisations involved in district-level Labour & Skill planning.")

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
        st.write("Monitor employment, unemployment, skill demand, job openings, job fairs and training institutes.")

        st.markdown("### 🏛️ State Admin")
        st.write("Review district-level information and compare skill and employment trends across districts.")

    with c2:
        st.markdown("### 🎓 Training Institutes")
        st.write("Track student enrolment, skill training and student placement outcomes.")

        st.markdown("### 🤝 Job Fair Companies")
        st.write("Explore job fair participation, hiring activity and employment opportunities.")

    st.divider()

    st.subheader("District Overview — Sample Data")
    st.dataframe(district_data, use_container_width=True)

# ==========================================
# 8. 🤖 AI CHART BOT (DYNAMIC CHART GENERATOR)
# ==========================================

elif st.session_state.page == "🤖 AI Chart Bot":

    st.header("🤖 AI Labour & Skilling Chart Bot")
    st.caption("Ask questions in natural language. The AI answers and dynamically renders interactive charts!")

    # Quick prompt suggestion pills
    st.markdown("##### 💡 Quick Suggestions (Click to Ask):")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)

    preset_query = None
    if qcol1.button("📊 Plot Sector Openings"):
        preset_query = "Plot job openings by sector"
    if qcol2.button("🎓 Compare Unemployment"):
        preset_query = "Plot employed vs unemployed students by district"
    if qcol3.button("🎪 Job Fair Conversions"):
        preset_query = "Plot job fair student placements by district"
    if qcol4.button("🏫 Rank Institutes"):
        preset_query = "Show training institute placement rates"

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart") is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)

    # Chat Input handler
    user_input = st.chat_input("Ask a question or request a chart (e.g. 'Show me top growing skills' or 'Plot district openings')...")
    query_to_process = preset_query if preset_query else user_input

    if query_to_process:
        # Append User Message
        st.session_state.chat_messages.append({"role": "user", "content": query_to_process, "chart": None})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        # AI Bot Reasoning & Chart Synthesis Engine
        q = query_to_process.lower()
        bot_response = ""
        generated_chart = None

        if "sector" in q or "industry" in q:
            bot_response = (
                f"📊 **Sector-Wise Job Demand Analysis**:\n\n"
                f"- **Top Sector**: `{sector_demand.iloc[0]['Sector']}` with **{sector_demand.iloc[0]['Openings']} openings**.\n"
                f"- **Fastest Growing**: `{sector_demand.sort_values(by='Growth Rate (%)', ascending=False).iloc[0]['Sector']}` "
                f"growing at **+{sector_demand['Growth Rate (%)'].max()}% YoY**.\n\n"
                f"Here is the interactive sector demand distribution chart:"
            )
            fig = px.bar(
                sector_demand,
                x="Sector",
                y="Openings",
                color="Growth Rate (%)",
                text="Openings",
                title="Job Openings by Sector with YoY Growth Trajectory",
                color_continuous_scale="Viridis"
            )
            fig.update_traces(textposition="outside")
            generated_chart = fig

        elif "unemploy" in q or "employ" in q or "student" in q:
            total_unemployed = district_data["Unemployed Students"].sum()
            total_employed = district_data["Employed Students"].sum()
            unemp_rate = (total_unemployed / (total_employed + total_unemployed)) * 100

            bot_response = (
                f"🎓 **District Employment & Unemployment Breakdown**:\n\n"
                f"- **Total Employed Students**: {total_employed:,}\n"
                f"- **Total Unemployed Students**: {total_unemployed:,} (Average Rate: **{unemp_rate:.1f}%**)\n"
                f"- **Highest Unemployed District**: `{district_data.sort_values(by='Unemployed Students', ascending=False).iloc[0]['District']}` "
                f"({district_data['Unemployed Students'].max()} students seeking placement).\n\n"
                f"Here is the comparative visualization across districts:"
            )
            fig = px.bar(
                district_data,
                x="District",
                y=["Employed Students", "Unemployed Students"],
                barmode="group",
                title="Employed vs Unemployed Students Across Districts",
                color_discrete_map={"Employed Students": "#10B981", "Unemployed Students": "#EF4444"}
            )
            generated_chart = fig

        elif "job fair" in q or "mela" in q or "placed" in q or "fair" in q:
            total_fairs = job_fair_data["Job Fairs Conducted"].sum()
            total_placed = job_fair_data["Students Placed"].sum()
            total_part = job_fair_data["Students Participated"].sum()
            hire_rate = (total_placed / total_part * 100)

            bot_response = (
                f"🎪 **Job Fair & Rozgar Mela Performance**:\n\n"
                f"- **Total Fairs Conducted**: {total_fairs} events\n"
                f"- **Students Participated**: {total_part:,}\n"
                f"- **Spot Offers Extended**: {total_placed:,} (Placement Rate: **{hire_rate:.1f}%**)\n"
                f"- **Corporate Hiring Engagement**: {job_fair_data['Companies Hired'].sum()} companies successfully hired out of {job_fair_data['Companies Participated'].sum()} participating booths."
            )
            fig = px.bar(
                job_fair_data,
                x="District",
                y=["Students Participated", "Students Placed"],
                barmode="group",
                title="Job Fair Participation vs Spot Placements",
                color_discrete_map={"Students Participated": "#94A3B8", "Students Placed": "#2563EB"}
            )
            generated_chart = fig

        elif "institute" in q or "iti" in q or "polytechnic" in q or "training" in q:
            top_inst = institute_data.sort_values(by="Placement Rate (%)", ascending=False).iloc[0]
            bot_response = (
                f"🏫 **Training Institute League Table Analysis**:\n\n"
                f"- **Top Placement Efficacy**: `{top_inst['Institute']}` in `{top_inst['District']}` with a **{top_inst['Placement Rate (%)']}% placement conversion rate**.\n"
                f"- **Total Students Certified**: {institute_data['Students Skilled'].sum():,} across all surveyed centres.\n"
                f"- **Total Placed in Jobs**: {institute_data['Students Placed'].sum():,} graduates."
            )
            fig = px.bar(
                institute_data.sort_values(by="Placement Rate (%)", ascending=True),
                x="Placement Rate (%)",
                y="Institute",
                orientation="h",
                text="Placement Rate (%)",
                color="Students Placed",
                title="Training Institutes Ranked by Graduate Placement Rate (%)",
                color_continuous_scale="Teal"
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            generated_chart = fig

        elif "skill" in q:
            top_skill = skill_demand.sort_values(by="Openings", ascending=False).iloc[0]
            fast_skill = skill_demand.sort_values(by="Growth Rate (%)", ascending=False).iloc[0]
            bot_response = (
                f"⚡ **In-Demand Technical Skills Overview**:\n\n"
                f"- **Highest Vacancy Volume**: `{top_skill['Skill']}` with **{top_skill['Openings']} active openings**.\n"
                f"- **Fastest Emerging Momentum**: `{fast_skill['Skill']}` surging at **+{fast_skill['Growth Rate (%)']}% YoY**.\n\n"
                f"Here is the skill demand ranking chart:"
            )
            fig = px.bar(
                skill_demand,
                x="Openings",
                y="Skill",
                orientation="h",
                color="Growth Rate (%)",
                text="Openings",
                title="Technical Skill Demand vs Growth Rate (%)",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            fig.update_traces(textposition="outside")
            generated_chart = fig

        else:
            bot_response = (
                f"🤖 I analyzed the Karnataka Labour & Skill dataset for **'{query_to_process}'**:\n\n"
                f"- **Districts Monitored**: {len(district_data)} districts\n"
                f"- **Total Openings Tracked**: {district_data['Job Openings'].sum():,} vacancies\n"
                f"- **Leading Growth Discipline**: `{sector_demand.iloc[0]['Sector']}`\n\n"
                f"Here is a consolidated overview of Job Openings across Karnataka districts:"
            )
            fig = px.pie(
                district_data,
                names="District",
                values="Job Openings",
                hole=0.4,
                title="District-Wise Share of Total Job Openings"
            )
            generated_chart = fig

        # Display Assistant Response in Chat
        with st.chat_message("assistant"):
            st.markdown(bot_response)
            if generated_chart is not None:
                st.plotly_chart(generated_chart, use_container_width=True)

        # Store in session state
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": bot_response,
            "chart": generated_chart
        })

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

# ==========================================
# 10. DISTRICT ADMIN DASHBOARD
# ==========================================

elif st.session_state.page == "District Admin Dashboard":

    st.header("District Admin - Labour & Skill")
    st.write("Understand district-level employment, skill demand, job openings, hiring companies and training outcomes.")

    selected_district = st.selectbox(
        "Select District",
        district_data["District"].tolist()
    )

    selected_row = district_data[district_data["District"] == selected_district].iloc[0]

    st.subheader("Employment and Job Openings")
    c1, c2, c3 = st.columns(3)
    c1.metric("Employed Students", int(selected_row["Employed Students"]))
    c2.metric("Unemployed Students", int(selected_row["Unemployed Students"]))
    c3.metric("Job Openings", int(selected_row["Job Openings"]))

    st.divider()

    # Pain 1: Growing sectors and skills
    st.subheader("1. Which Sectors and Skills Are Growing?")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill-wise Demand")
        fig_sk = px.bar(skill_demand, x="Skill", y="Openings", color="Growth Rate (%)", title="Skill Demand with YoY Growth Rate")
        st.plotly_chart(fig_sk, use_container_width=True)

    with col2:
        st.markdown("#### Sector-wise Demand")
        fig_sec = px.bar(sector_demand, x="Sector", y="Openings", color="Growth Rate (%)", title="Sector Demand with YoY Growth Rate")
        st.plotly_chart(fig_sec, use_container_width=True)

    # Pain 2: Employment and unemployment
    st.divider()
    st.subheader("2. Employed and Unemployed Students")
    st.dataframe(district_data[["District", "Employed Students", "Unemployed Students"]], use_container_width=True)

    fig_emp = px.bar(district_data, x="District", y=["Employed Students", "Unemployed Students"], barmode="group", title="Employed vs Unemployed")
    st.plotly_chart(fig_emp, use_container_width=True)

    # Pain 3: Openings by district
    st.divider()
    st.subheader("3. Job Openings — District-wise")
    fig_op = px.bar(district_data, x="District", y="Job Openings", color="Job Openings", title="District Job Openings")
    st.plotly_chart(fig_op, use_container_width=True)

    # Pain 4: Hiring companies
    st.divider()
    st.subheader("4. Hiring Companies")
    dist_companies = hiring_companies[hiring_companies["District"] == selected_district]
    if not dist_companies.empty:
        st.dataframe(dist_companies, use_container_width=True)
    else:
        st.dataframe(hiring_companies, use_container_width=True)

    # Pain 5: Job fairs
    st.divider()
    st.subheader("5. Job Fair Performance")
    st.dataframe(job_fair_data, use_container_width=True)

    fair_row = job_fair_data[job_fair_data["District"] == selected_district].iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Fairs Conducted", int(fair_row["Job Fairs Conducted"]))
    c2.metric("Participants", int(fair_row["Students Participated"]))
    c3.metric("Placed", int(fair_row["Students Placed"]))
    c4.metric("Companies", int(fair_row["Companies Participated"]))
    c5.metric("Hired", int(fair_row["Companies Hired"]))

    # Pain 6: Training institutes
    st.divider()
    st.subheader("6. Training Institute Performance")
    st.dataframe(institute_data, use_container_width=True)

    fig_inst = px.bar(institute_data, x="Institute", y=["Students Enrolled", "Students Skilled", "Students Placed"], barmode="group")
    st.plotly_chart(fig_inst, use_container_width=True)

# ==========================================
# 11. STATE ADMIN
# ==========================================

elif st.session_state.page == "State Admin":

    st.header("State Admin - Labour & Skill")
    st.write("State-level view of district employment, unemployment and job openings.")
    st.dataframe(district_data, use_container_width=True)

    st.subheader("Compare Districts")
    fig_comp = px.bar(district_data, x="District", y=["Employed Students", "Unemployed Students", "Job Openings"], barmode="group")
    st.plotly_chart(fig_comp, use_container_width=True)

# ==========================================
# 12. TRAINING INSTITUTES
# ==========================================

elif st.session_state.page == "Training Institutes":

    st.header("Training Institutes")
    st.write("Track student enrolment, students who complete training, and students who get placed.")
    st.dataframe(institute_data, use_container_width=True)

    st.subheader("Student Training Outcomes & Placement Rate")
    fig_ti = px.bar(institute_data, x="Institute", y="Placement Rate (%)", color="Students Placed", text="Placement Rate (%)")
    fig_ti.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig_ti, use_container_width=True)

# ==========================================
# 13. JOB FAIR COMPANIES
# ==========================================

elif st.session_state.page == "Job Fair Companies":

    st.header("Job Fair Companies")
    st.write("Review job fair participation and hiring outcomes by district.")
    st.dataframe(job_fair_data, use_container_width=True)

    st.subheader("Job Fair Hiring Results")
    fig_jf = px.bar(job_fair_data, x="District", y=["Companies Participated", "Companies Hired"], barmode="group")
    st.plotly_chart(fig_jf, use_container_width=True)

# ==========================================
# 14. ANALYTICS - AI SKILL PLANNING
# ==========================================

elif st.session_state.page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")
    st.write("This module helps district administrators create automated skill plans based on unemployment, skill gaps and demand.")

    st.subheader("Generate an AI Skill Planning Report")
    district = st.selectbox("Choose District", district_data["District"].tolist(), key="analytics_district")
    focus = st.selectbox("Planning Focus", ["Reduce Unemployment", "Address Skill Gaps", "Growing Skills", "Growing Sectors"])

    if st.button("Generate AI Skill Planning Report"):
        row = district_data[district_data["District"] == district].iloc[0]

        st.subheader("Generated AI Skill Planning & Recommendation Brief")
        st.write(f"**District:** {district}")
        st.write(f"**Planning Focus:** {focus}")
        st.write(f"**Unemployed Students:** {int(row['Unemployed Students'])}")
        st.write(f"**Available Job Openings:** {int(row['Job Openings'])}")

        st.success(f"""
        **AI Recommended Action Plan for {district}**:
        1. **Target Sector to Fund**: `{sector_demand.iloc[0]['Sector']}` (+{sector_demand.iloc[0]['Growth Rate (%)']}% Growth).
        2. **Partner Training Institute**: `{institute_data.iloc[0]['Institute']}` (Historical placement rate: **{institute_data.iloc[0]['Placement Rate (%)']}%**).
        3. **Corporate Hiring Anchors to Invite**: `{hiring_companies[hiring_companies['District'] == district]['Company'].tolist() if not hiring_companies[hiring_companies['District'] == district].empty else hiring_companies['Company'].iloc[:2].tolist()}`.
        4. **Targeted Unemployment Reduction**: **-28.5%** within 2 quarters.
        """)

    st.divider()
    st.subheader("Planned Analytics Features")
    st.markdown("""
    - Skill Gap Report
    - Skill Trend Report
    - AI-generated Skill Plans
    - Training Institute Ranking
    - Job Fair Company Selection
    - Hiring Company Recommendations
    """)

# ==========================================
# 15. PLANS
# ==========================================

elif st.session_state.page == "Plans":

    st.header("Skill Plans")
    st.write("Display and manage skill planning reports created by the District Admin.")

    active_plans = pd.DataFrame({
        "Plan ID": ["PLAN-BLR-01", "PLAN-KLB-02", "PLAN-BEL-03", "PLAN-MYS-04"],
        "District": ["Bengaluru Urban", "Kalaburagi", "Belagavi", "Mysuru"],
        "Focus Skill": ["Python & AI", "Solar PV Installation", "CNC Machining", "Healthcare Tech"],
        "Target Cohort": [300, 500, 420, 350],
        "Lead Institute": ["Govt Model ITI", "Tata-KSDC Centre", "GTTC Toolroom", "Karnataka Polytechnic"],
        "Scheduled Date": ["2026-03-15", "2026-04-20", "2026-05-10", "2026-06-01"]
    })
    st.dataframe(active_plans, use_container_width=True)

# ==========================================
# 16. EXECUTED
# ==========================================

elif st.session_state.page == "Executed":

    st.header("Executed Plans")
    st.write("Track which planned activities have actually been executed.")

    execution_data = pd.DataFrame({
        "Plan ID": ["PLAN-BLR-01", "PLAN-KLB-02", "PLAN-BEL-03"],
        "Activity": ["Python & AI Fast-Track Training", "Solar Rooftop Technician Camp", "CNC Apprenticeship Mela"],
        "Status": ["Executed", "In Progress", "Executed"],
        "Students Trained": [280, 410, 390],
        "Students Placed": [235, 290, 310],
        "Execution Date": ["2026-01-15", "2026-02-28", "2026-03-10"]
    })
    st.dataframe(execution_data, use_container_width=True)

# ==========================================
# 17. RESULTS
# ==========================================

elif st.session_state.page == "Results":

    st.header("Results & Impact Monitoring")
    st.write("Monitor changes in unemployment and skill gaps after skill plans are executed.")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📉 Unemployment Trend After Skill Plan Execution")
        trend_df = pd.DataFrame({
            "Quarter": ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1 (Post-Plan)"],
            "Unemployed Students": [520, 490, 470, 440, 310]
        })
        fig_trend = px.line(trend_df, x="Quarter", y="Unemployed Students", markers=True, title="Unemployment Reduction Curve")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("📊 Skill Gap Reduction Trend")
        gap_df = pd.DataFrame({
            "Skill": ["Python & AI", "Solar PV Tech", "CNC Machining", "Healthcare"],
            "Pre-Plan Gap": [78, 65, 58, 45],
            "Post-Plan Gap": [42, 28, 30, 22]
        })
        fig_gap = px.bar(gap_df, x="Skill", y=["Pre-Plan Gap", "Post-Plan Gap"], barmode="group", title="Skill Gap Shrinkage (%)")
        st.plotly_chart(fig_gap, use_container_width=True)

# ==========================================
# 18. FOOTER
# ==========================================

st.divider()
st.caption("Labour & Skill Planning System with AI Chart Bot | Government of Karnataka Decision Intelligence")
