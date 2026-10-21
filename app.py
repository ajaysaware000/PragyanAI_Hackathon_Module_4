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
# 2. LOAD CSV
# ==========================================

CSV_FILE = "district_skills.csv"

try:
    df = pd.read_csv(
        CSV_FILE,
        encoding="utf-8-sig"
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_columns = [
        "district", "sector", "skill",
        "employed", "unemployed", "job_openings",
        "skill_demand", "available_candidates", "skill_gap"
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
    for column in ["district", "sector", "skill"]:
        df[column] = df[column].astype(str).str.strip()

    # Clean numeric columns
    numeric_columns = [
        "employed", "unemployed", "job_openings",
        "skill_demand", "available_candidates", "skill_gap"
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
        Employed_Students=("employed", "sum"),
        Unemployed_Students=("unemployed", "sum"),
        Job_Openings=("job_openings", "sum"),
        Training_Demand=("skill_demand", "sum")
    )
    .rename(columns={
        "district": "District",
        "Employed_Students": "Employed Students",
        "Unemployed_Students": "Unemployed Students",
        "Job_Openings": "Job Openings",
        "Training_Demand": "Skill Demand"
    })
)

skill_demand = (
    df
    .groupby("skill", as_index=False)
    .agg(
        Job_Openings=("job_openings", "sum"),
        Skill_Demand=("skill_demand", "sum"),
        Available_Candidates=("available_candidates", "sum"),
        Skill_Gap=("skill_gap", "sum")
    )
    .rename(columns={"skill": "Skill"})
    .sort_values("Skill Demand", ascending=False)
)

sector_demand = (
    df
    .groupby("sector", as_index=False)
    .agg(
        Job_Openings=("job_openings", "sum"),
        Skill_Demand=("skill_demand", "sum"),
        Skill_Gap=("skill_gap", "sum")
    )
    .rename(columns={"sector": "Sector"})
    .sort_values("Skill Demand", ascending=False)
)

# ==========================================
# 4. SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Explore Dashboard"

# ==========================================
# 5. LOGIN
# ==========================================

st.title("🎯 Labour & Skill Planning System")
st.caption(
    "District-level employment, skill demand and training planning "
    "powered by district_skills.csv"
)

if not st.session_state.logged_in:

    username = st.text_input("Username", key="login_username")
    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login", use_container_width=True):
        if username.strip() and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Enter a username and password.")

    st.info("Demo login: enter any username and password.")
    st.stop()

# ==========================================
# 6. SIDEBAR
# ==========================================

st.sidebar.title("Navigation")
st.sidebar.write(f"**User:** {st.session_state.username}")

page = st.sidebar.radio(
    "Select a Page",
    [
        "Explore Dashboard",
        "District Admin Dashboard",
        "State Admin",
        "Skill Analytics"
    ]
)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ==========================================
# 7. EXPLORE DASHBOARD
# ==========================================

if page == "Explore Dashboard":

    st.header("Explore Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Districts", df["district"].nunique())
    c2.metric("Sectors", df["sector"].nunique())
    c3.metric("Skills", df["skill"].nunique())
    c4.metric("CSV Records", len(df))

    st.divider()

    st.subheader("District Overview")
    st.dataframe(district_data, use_container_width=True)

    st.subheader("Employment by District")

    st.bar_chart(
        district_data.set_index("District")[
            ["Employed Students", "Unemployed Students"]
        ]
    )

    st.subheader("CSV Records")
    st.dataframe(df, use_container_width=True)

# ==========================================
# 8. DISTRICT ADMIN DASHBOARD
# ==========================================

elif page == "District Admin Dashboard":

    st.header("District Admin Dashboard")

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
        "Skill Demand",
        int(district_row["Skill Demand"])
    )

    st.divider()

    st.subheader("Skill-wise Demand")

    district_skill_demand = (
        district_records
        .groupby("skill", as_index=False)
        .agg(
            Job_Openings=("job_openings", "sum"),
            Skill_Demand=("skill_demand", "sum"),
            Skill_Gap=("skill_gap", "sum")
        )
        .set_index("skill")
    )

    st.bar_chart(district_skill_demand)

    st.subheader("Sector-wise Demand")

    district_sector_demand = (
        district_records
        .groupby("sector", as_index=False)
        .agg(
            Job_Openings=("job_openings", "sum"),
            Skill_Demand=("skill_demand", "sum"),
            Skill_Gap=("skill_gap", "sum")
        )
        .set_index("sector")
    )

    st.bar_chart(district_sector_demand)

    st.subheader("District Records")

    st.dataframe(district_records, use_container_width=True)

# ==========================================
# 9. STATE ADMIN
# ==========================================

elif page == "State Admin":

    st.header("State Admin")

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

    st.dataframe(district_data, use_container_width=True)

    st.subheader("Districts Requiring Attention")

    priority_districts = district_data.sort_values(
        "Unemployed Students",
        ascending=False
    ).head(3)

    st.dataframe(priority_districts, use_container_width=True)

# ==========================================
# 10. SKILL ANALYTICS
# ==========================================

elif page == "Skill Analytics":

    st.header("Skill Analytics")

    st.subheader("Skill Demand and Gap")

    st.bar_chart(
        skill_demand.set_index("Skill")[
            ["Skill Demand", "Available Candidates", "Skill Gap"]
        ]
    )

    st.dataframe(skill_demand, use_container_width=True)

    st.subheader("Sector Demand and Gap")

    st.bar_chart(
        sector_demand.set_index("Sector")[
            ["Skill Demand", "Skill Gap"]
        ]
    )

    st.dataframe(sector_demand, use_container_width=True)

# ==========================================
# 11. FOOTER
# ==========================================

st.divider()

st.caption(
    "Labour & Skill Planning System | "
    "Powered by district_skills.csv | Demonstration Version"
)
