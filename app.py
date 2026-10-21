import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


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
# ==========================================

if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Explore Dashboard"

if "district_data" not in st.session_state:
    st.session_state.district_data = district_data

if "skill_demand" not in st.session_state:
    st.session_state.skill_demand = skill_demand

if "sector_demand" not in st.session_state:
    st.session_state.sector_demand = sector_demand

if "job_fair_data" not in st.session_state:
    st.session_state.job_fair_data = job_fair_data

if "institute_data" not in st.session_state:
    st.session_state.institute_data = institute_data


# ==========================================
# 4. AI CHART BOT FUNCTIONS
# ==========================================

CHART_SPEC_SCHEMA = {
    "type": "object",
    "properties": {
        "dataset": {
            "type": "string",
            "enum": [
                "district_data",
                "skill_demand",
                "sector_demand",
                "job_fair_data",
                "institute_data"
            ]
        },
        "chart_type": {
            "type": "string",
            "enum": ["bar", "line", "pie", "scatter"]
        },
        "x_column": {"type": "string"},
        "y_columns": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "title": {"type": "string"},
        "explanation": {"type": "string"}
    },
    "required": [
        "dataset",
        "chart_type",
        "x_column",
        "y_columns",
        "title",
        "explanation"
    ],
    "additionalProperties": False
}


def get_available_datasets():
    return {
        "district_data": st.session_state.district_data,
        "skill_demand": st.session_state.skill_demand,
        "sector_demand": st.session_state.sector_demand,
        "job_fair_data": st.session_state.job_fair_data,
        "institute_data": st.session_state.institute_data,
    }


def build_data_context(datasets):
    context = []

    for name, df in datasets.items():
        columns = ", ".join(df.columns)
        context.append(f"{name}: columns = [{columns}]")

    return "\n".join(context)


def generate_chart_spec(question, datasets):
    """Convert a natural-language question into a safe chart specification."""

    if OpenAI is None:
        raise RuntimeError("The openai package is not installed.")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    system_prompt = f"""
You are a data visualization assistant for a Labour and Skill Planning System.

Choose the most suitable dataset and columns for the user's question.

Available datasets and columns:
{build_data_context(datasets)}

Rules:
- Use only columns that exist in the selected dataset.
- For comparing multiple numeric measures, use a bar chart.
- For trends over time, use a line chart.
- For proportion of one categorical column, use a pie chart.
- For relationship between two numeric columns, use a scatter chart.
- Return only the chart specification.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "chart_specification",
                "strict": True,
                "schema": CHART_SPEC_SCHEMA,
            },
        },
        temperature=0,
    )

    return json.loads(response.choices[0].message.content)


def validate_chart_spec(spec, datasets):
    dataset_name = spec["dataset"]
    df = datasets.get(dataset_name)

    if df is None:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    x_column = spec["x_column"]
    y_columns = spec["y_columns"]

    if x_column not in df.columns:
        raise ValueError(f"Column '{x_column}' does not exist in {dataset_name}.")

    for column in y_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in {dataset_name}.")

    return df


def render_chart(df, spec):
    chart_type = spec["chart_type"]
    x_column = spec["x_column"]
    y_columns = spec["y_columns"]
    title = spec["title"]

    if chart_type == "bar":
        if len(y_columns) == 1:
            fig = px.bar(df, x=x_column, y=y_columns[0], title=title)
        else:
            fig = px.bar(
                df,
                x=x_column,
                y=y_columns,
                barmode="group",
                title=title,
            )

    elif chart_type == "line":
        fig = px.line(df, x=x_column, y=y_columns, title=title)

    elif chart_type == "pie":
        fig = px.pie(df, names=x_column, values=y_columns[0], title=title)

    elif chart_type == "scatter":
        fig = px.scatter(df, x=x_column, y=y_columns[0], title=title)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


def simple_fallback_chart(question, datasets):
    """Offline chart selection when AI is unavailable."""

    question_lower = question.lower()

    if "unemploy" in question_lower:
        df = datasets["district_data"]
        spec = {
            "dataset": "district_data",
            "chart_type": "bar",
            "x_column": "District",
            "y_columns": ["Unemployed Students"],
            "title": "Unemployed Students by District",
            "explanation": "Showing unemployed students for each district."
        }

    elif "employ" in question_lower:
        df = datasets["district_data"]
        spec = {
            "dataset": "district_data",
            "chart_type": "bar",
            "x_column": "District",
            "y_columns": ["Employed Students", "Unemployed Students"],
            "title": "Employed and Unemployed Students by District",
            "explanation": "Comparing employment and unemployment across districts."
        }

    elif "skill" in question_lower:
        df = datasets["skill_demand"]
        spec = {
            "dataset": "skill_demand",
            "chart_type": "bar",
            "x_column": "Skill",
            "y_columns": ["Openings"],
            "title": "Job Openings by Skill",
            "explanation": "Showing demand for each skill."
        }

    elif "sector" in question_lower:
        df = datasets["sector_demand"]
        spec = {
            "dataset": "sector_demand",
            "chart_type": "bar",
            "x_column": "Sector",
            "y_columns": ["Openings"],
            "title": "Job Openings by Sector",
            "explanation": "Showing demand across sectors."
        }

    elif "job fair" in question_lower or "fair" in question_lower:
        df = datasets["job_fair_data"]
        spec = {
            "dataset": "job_fair_data",
            "chart_type": "bar",
            "x_column": "District",
            "y_columns": ["Companies Participated", "Companies Hired"],
            "title": "Job Fair Company Participation and Hiring",
            "explanation": "Comparing participating and hiring companies by district."
        }

    elif "institute" in question_lower or "training" in question_lower:
        df = datasets["institute_data"]
        spec = {
            "dataset": "institute_data",
            "chart_type": "bar",
            "x_column": "Institute",
            "y_columns": [
                "Students Enrolled",
                "Students Skilled",
                "Students Placed"
            ],
            "title": "Training Institute Outcomes",
            "explanation": "Comparing enrolment, training and placement outcomes."
        }

    else:
        df = datasets["district_data"]
        spec = {
            "dataset": "district_data",
            "chart_type": "bar",
            "x_column": "District",
            "y_columns": [
                "Employed Students",
                "Unemployed Students",
                "Job Openings"
            ],
            "title": "District Employment Overview",
            "explanation": "Showing employment, unemployment and openings by district."
        }

    return df, spec


def show_ai_chart_bot():
    st.header("🤖 AI Chart Bot")
    st.write(
        "Ask a question about districts, skills, sectors, training institutes "
        "or job fairs, and get an instant chart."
    )

    datasets = get_available_datasets()

    with st.expander("Available data"):
        for name, df in datasets.items():
            st.markdown(f"**{name}**")
            st.dataframe(df, use_container_width=True)

    example_questions = [
        "Show unemployed students by district",
        "Compare employed and unemployed students across districts",
        "Show job openings by skill",
        "Show job openings by sector",
        "Compare companies participated and companies hired in job fairs",
        "Show training institute outcomes"
    ]

    st.caption("Examples: " + " | ".join(example_questions))

    question = st.text_input(
        "Ask your question",
        placeholder="e.g. Show unemployed students by district"
    )

    use_ai = st.toggle(
        "Use AI model",
        value=bool(os.getenv("OPENAI_API_KEY")),
        help="Turn off to use the built-in offline chart suggestions."
    )

    if st.button("Generate Chart", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        try:
            if use_ai:
                spec = generate_chart_spec(question, datasets)
                df = validate_chart_spec(spec, datasets)
            else:
                df, spec = simple_fallback_chart(question, datasets)

            st.success(spec["explanation"])
            render_chart(df, spec)

            with st.expander("Chart details"):
                st.json(spec)

        except Exception as e:
            st.error(f"Could not generate the chart: {e}")


# ==========================================
# 5. APPLICATION HEADER
# ==========================================

st.title("🎯 Labour & Skill Planning System")
st.caption("District-level employment, skill demand and training planning")


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
    "AI Chart Bot",
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
        "job openings, hiring companies and training outcomes."
    )

    selected_district = st.selectbox(
        "Select District",
        district_data["District"].tolist()
    )

    selected_row = district_data[
        district_data["District"] == selected_district
    ].iloc[0]

    st.subheader("Employment and Job Openings")

    c1, c2, c3 = st.columns(3)

    c1.metric("Employed Students", int(selected_row["Employed Students"]))
    c2.metric("Unemployed Students", int(selected_row["Unemployed Students"]))
    c3.metric("Job Openings", int(selected_row["Job Openings"]))

    st.divider()

    st.subheader("1. Which Sectors and Skills Are Growing?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill-wise Demand")
        st.bar_chart(skill_demand.set_index("Skill")["Openings"])

    with col2:
        st.markdown("#### Sector-wise Demand")
        st.bar_chart(sector_demand.set_index("Sector")["Openings"])

    st.divider()

    st.subheader("2. Employed and Unemployed Students")

    st.dataframe(
        district_data[["District", "Employed Students", "Unemployed Students"]],
        use_container_width=True
    )

    st.bar_chart(
        district_data.set_index("District")[
            ["Employed Students", "Unemployed Students"]
        ]
    )

    st.divider()

    st.subheader("3. Job Openings — District-wise")

    st.bar_chart(district_data.set_index("District")["Job Openings"])

    st.divider()

    st.subheader("4. Hiring Companies")

    hiring_companies = pd.DataFrame({
        "Company": [
            "ABC Technologies",
            "Karnataka Manufacturing Ltd.",
            "Healthcare Services Ltd."
        ],
        "Sector": ["IT", "Manufacturing", "Healthcare"],
        "Skill Required": [
            "Python and Data Analytics",
            "Welding and Electrical",
            "Healthcare Support"
        ],
        "Openings": [50, 35, 25]
    })

    st.dataframe(hiring_companies, use_container_width=True)

    st.divider()

    st.subheader("5. Job Fair Performance")

    st.dataframe(job_fair_data, use_container_width=True)

    fair_row = job_fair_data[
        job_fair_data["District"] == selected_district
    ].iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric("Job Fairs Conducted", int(fair_row["Job Fairs Conducted"]))
    c2.metric("Students Participated", int(fair_row["Students Participated"]))
    c3.metric("Students Placed", int(fair_row["Students Placed"]))

    c4, c5 = st.columns(2)

    c4.metric("Companies Participated", int(fair_row["Companies Participated"]))
    c5.metric("Companies That Hired", int(fair_row["Companies Hired"]))

    st.divider()

    st.subheader("6. Training Institute Performance")

    st.dataframe(institute_data, use_container_width=True)

    st.bar_chart(
        institute_data.set_index("Institute")[
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


# ==========================================
# 12. TRAINING INSTITUTES
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


# ==========================================
# 14. ANALYTICS - AI SKILL PLANNING
# ==========================================

elif st.session_state.page == "Analytics - AI Skill Planning":

    st.header("Analytics - AI Skill Planning")

    st.write(
        "This module helps district administrators create skill plans "
        "based on unemployment, skill gaps and demand."
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
        st.write(f"**Unemployed Students:** {int(row['Unemployed Students'])}")
        st.write(f"**Available Job Openings:** {int(row['Job Openings'])}")

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
# 15. AI CHART BOT
# ==========================================

elif st.session_state.page == "AI Chart Bot":
    show_ai_chart_bot()


# ==========================================
# 16. PLANS
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
# 17. EXECUTED
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
# 18. RESULTS
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
        st.write("Historical unemployment data will be displayed here.")

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
# 19. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | Initial Development Version"
)
