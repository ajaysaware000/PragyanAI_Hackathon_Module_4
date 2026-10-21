import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Phase 1: Explore | Labour & Skill",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f4f7fc;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(120deg, #12336b, #2563eb);
        padding: 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
    }

    .hero h1, .hero p {
        color: white;
    }

    .role-card {
        background: white;
        border: 1px solid #dbe3f0;
        border-radius: 14px;
        padding: 20px;
        min-height: 155px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
    }

    .role-icon {
        font-size: 30px;
    }

    .role-title {
        color: #12336b;
        font-size: 18px;
        font-weight: 700;
        margin-top: 8px;
    }

    .role-description {
        color: #475569;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# USER GROUPS
# --------------------------------------------------
users = {
    "District Admin — Labour & Skill": {
        "icon": "🏢",
        "description": (
            "Explore district-level labour and skill information. "
            "More district administration features can be added later."
        )
    },
    "State Admin — Labour & Skill": {
        "icon": "🏛️",
        "description": (
            "Explore state-level labour and skill information. "
            "State-wide monitoring features can be added later."
        )
    },
    "Training Institutes": {
        "icon": "🎓",
        "description": (
            "A section for training institutes. Institute profiles, "
            "courses, and training information can be added later."
        )
    },
    "Job Fair Companies": {
        "icon": "🤝",
        "description": (
            "A section for companies related to job fairs. Company "
            "profiles, vacancies, and recruitment information can be added later."
        )
    }
}

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.markdown("## 🏛️ Labour & Skill Portal")
st.sidebar.caption("Phase 1: Explore")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate to",
    [
        "Explore Dashboard",
        "Users",
        "District Admin",
        "State Admin",
        "Training Institutes",
        "Job Fair Companies"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Initial prototype — more features can be added later.")

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <p style="margin: 0; font-size: 14px; letter-spacing: 1px;">
        PHASE 1
    </p>
    <h1 style="margin: 8px 0;">Explore: Labour & Skill</h1>
    <p style="font-size: 16px; margin-bottom: 0;">
        Explore the user groups involved in the Labour & Skill ecosystem.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# EXPLORE DASHBOARD
# --------------------------------------------------
if page == "Explore Dashboard":

    st.subheader("Explore Dashboard")
    st.write(
        "Welcome to Phase 1. Select a user group to explore its section."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Phase", "01 — Explore")
    col2.metric("User Groups", len(users))
    col3.metric("Domain", "Labour & Skill")
    col4.metric("Version", "Starter")

    st.divider()
    st.subheader("Users")

    first_column, second_column = st.columns(2)

    for index, (user_name, details) in enumerate(users.items()):

        current_column = (
            first_column if index % 2 == 0 else second_column
        )

        with current_column:
            st.markdown(
                f"""
                <div class="role-card">
                    <div class="role-icon">{details["icon"]}</div>
                    <div class="role-title">{user_name}</div>
                    <p class="role-description">{details["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"Explore {user_name}",
                key=f"user_button_{index}",
                use_container_width=True
            ):
                st.session_state["selected_user"] = user_name
                st.rerun()

    if "selected_user" in st.session_state:
        st.divider()
        st.subheader("Selected User Group")
        st.write(st.session_state["selected_user"])
        st.info(
            "This section is ready for additional content and features."
        )

# --------------------------------------------------
# USERS PAGE
# --------------------------------------------------
elif page == "Users":

    st.subheader("Users")
    st.write("The following user groups are included in this version.")

    users_table = pd.DataFrame([
        {
            "No.": 1,
            "User Group": "District Admin — Labour & Skill"
        },
        {
            "No.": 2,
            "User Group": "State Admin — Labour & Skill"
        },
        {
            "No.": 3,
            "User Group": "Training Institutes"
        },
        {
            "No.": 4,
            "User Group": "Job Fair Companies"
        }
    ])

    st.dataframe(
        users_table,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# DISTRICT ADMIN PAGE
# --------------------------------------------------
elif page == "District Admin":

    st.subheader("🏢 District Admin — Labour & Skill")
    st.write("Welcome to the District Admin section.")

    st.info(
        "District-level information and administrative tools "
        "will be added here."
    )

# --------------------------------------------------
# STATE ADMIN PAGE
# --------------------------------------------------
elif page == "State Admin":

    st.subheader("🏛️ State Admin — Labour & Skill")
    st.write("Welcome to the State Admin section.")

    st.info(
        "State-level information and administrative tools "
        "will be added here."
    )

# --------------------------------------------------
# TRAINING INSTITUTES PAGE
# --------------------------------------------------
elif page == "Training Institutes":

    st.subheader("🎓 Training Institutes")
    st.write("Welcome to the Training Institutes section.")

    st.info(
        "Training institute details and related features "
        "will be added here."
    )

# --------------------------------------------------
# JOB FAIR COMPANIES PAGE
# --------------------------------------------------
elif page == "Job Fair Companies":

    st.subheader("🤝 Job Fair Companies")
    st.write("Welcome to the Job Fair Companies section.")

    st.info(
        "Company details and job fair features "
        "will be added here."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Phase 1: Explore | Labour & Skill | Initial prototype"
)
