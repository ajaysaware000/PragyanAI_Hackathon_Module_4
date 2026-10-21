
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import json
import os
import hashlib

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Karnataka District Skills Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Karnataka District Skills Dashboard")
st.caption("Employment, skills, job demand, job fairs and training analysis")

# --------------------------------------------------
# 2. FILE PATHS
# --------------------------------------------------


# Load the CSV file
uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    elif os.path.exists("karnataka_district_skills.csv"):
        df = pd.read_csv(
            "karnataka_district_skills.csv",
            encoding="utf-8-sig"
        )
    else:
        st.error("Please upload your CSV file.")
        st.stop()

except Exception as error:
    st.error(f"Unable to read CSV: {error}")
    st.stop()


# Clean column names
df.columns = (
    df.columns.astype(str)
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
)

# Display columns for troubleshooting
with st.expander("Debug: View CSV column names"):
    st.write(df.columns.tolist())
    st.dataframe(df.head(5), use_container_width=True)


# Find the District column even if its capitalization differs
district_column = next(
    (
        column for column in df.columns
        if column.strip().casefold() == "district"
    ),
    None
)

if district_column is None:
    st.error(
        "The CSV must contain a District column. "
        "Please check the column names displayed above."
    )
    st.stop()

# Standardize the name for the rest of the app
if district_column != "District":
    df = df.rename(columns={district_column: "District"})

# Remove rows where the district name is empty
df["District"] = df["District"].astype("string").str.strip()

df = df[
    df["District"].notna()
    & df["District"].ne("")
]

if df.empty:
    st.error("The CSV has no valid district records.")
    st.stop()



# --------------------------------------------------
# 3. USER AUTHENTICATION
# --------------------------------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def login_page():
    st.subheader("🔐 Login or Register")

    mode = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(mode, type="primary"):
        users = load_users()

        if not username.strip() or not password:
            st.error("Please enter both username and password.")
            return

        username = username.strip()

        if mode == "Register":
            if username in users:
                st.error("This username already exists.")
            else:
                users[username] = hash_password(password)
                save_users(users)
                st.success("Registration successful! Please log in.")

        else:
            if (
                username in users
                and users[username] == hash_password(password)
            ):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Incorrect username or password.")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_page()
    st.stop()


# --------------------------------------------------
# 4. LOGOUT
# --------------------------------------------------

with st.sidebar:
    st.success(
        f"Logged in as {st.session_state.get('username', 'User')}"
    )

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.rerun()


# --------------------------------------------------
# 5. LOAD DATASET
# --------------------------------------------------

st.sidebar.header("📂 Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        st.warning(
            f"Dataset '{DATA_FILE}' was not found. "
            "Upload your CSV file using the sidebar."
        )
        st.stop()

except Exception as error:
    st.error(f"Could not read the CSV file: {error}")
    st.stop()


# --------------------------------------------------
# 6. CLEAN COLUMN NAMES
# --------------------------------------------------

df.columns = [
    str(column).strip() for column in df.columns
]

# Standardize common column-name variations.
# This also handles duplicate "Students Placed" headers.

rename_map = {}

for column in df.columns:
    normalized = column.lower().strip().replace("_", " ")

    if normalized == "district":
        rename_map[column] = "District"

    elif normalized in ["skill", "skills", "skill name"]:
        rename_map[column] = "Skill"

    elif normalized in ["sector", "industry", "industry sector"]:
        rename_map[column] = "Sector"

    elif normalized in ["institute", "institution", "training institute"]:
        rename_map[column] = "Institute"

    elif normalized in [
        "employed students", "employed", "students employed"
    ]:
        rename_map[column] = "Employed Students"

    elif normalized in [
        "unemployed students", "unemployed", "students unemployed"
    ]:
        rename_map[column] = "Unemployed Students"

    elif normalized in ["job openings", "total job openings"]:
        rename_map[column] = "Job Openings"

    elif normalized in ["skill openings", "openings by skill"]:
        rename_map[column] = "Skill Openings"

    elif normalized in ["sector openings", "openings by sector"]:
        rename_map[column] = "Sector Openings"

    elif normalized in ["job fairs conducted", "job fairs"]:
        rename_map[column] = "Job Fairs Conducted"

    elif normalized in [
        "students participated", "participants"
    ]:
        rename_map[column] = "Students Participated"

    elif normalized in ["companies participated", "participating companies"]:
        rename_map[column] = "Companies Participated"

    elif normalized in ["companies hired", "hiring companies"]:
        rename_map[column] = "Companies Hired"

    elif normalized in ["students enrolled", "enrolled students"]:
        rename_map[column] = "Students Enrolled"

    elif normalized in ["students skilled", "skilled students"]:
        rename_map[column] = "Students Skilled"

df = df.rename(columns=rename_map)

# Pandas may rename duplicate CSV headers to "Students Placed.1".
# Treat the first occurrence as job-fair placements and the next
# occurrence as institute placements when both exist.

placed_columns = [
    column for column in df.columns
    if column.lower().startswith("students placed")
]

if len(placed_columns) >= 2:
    df = df.rename(columns={
        placed_columns[0]: "JobFair Students Placed",
        placed_columns[1]: "Institute Students Placed"
    })
elif len(placed_columns) == 1:
    df = df.rename(columns={
        placed_columns[0]: "Students Placed"
    })


# --------------------------------------------------
# 7. VALIDATE DATA
# --------------------------------------------------

if df.empty:
    st.error("The CSV file has no data rows.")
    st.stop()

if "District" not in df.columns:
    st.error(
        "The CSV must contain a District column. "
        "Please check the column names."
    )
    st.write("Columns found:", df.columns.tolist())
    st.stop()

# Convert likely numeric columns to numbers.
numeric_candidates = [
    "Employed Students",
    "Unemployed Students",
    "Job Openings",
    "Skill Openings",
    "Sector Openings",
    "Job Fairs Conducted",
    "Students Participated",
    "JobFair Students Placed",
    "Institute Students Placed",
    "Students Placed",
    "Companies Participated",
    "Companies Hired",
    "Students Enrolled",
    "Students Skilled"
]

for column in numeric_candidates:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        ).fillna(0)

# Clean text columns.
for column in ["District", "Skill", "Sector", "Institute"]:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()

# Remove rows with missing district names.
df = df[df["District"].ne("") & df["District"].ne("nan")]

if df.empty:
    st.error("No valid district records were found.")
    st.stop()


# --------------------------------------------------
# 8. HELPER FUNCTIONS
# --------------------------------------------------

def number_column(data, column):
    if column in data.columns:
        return pd.to_numeric(
            data[column], errors="coerce"
        ).fillna(0)
    return pd.Series(0, index=data.index, dtype=float)


def chart_bar(data, x, y, title, color=None):
    if data.empty:
        st.info("No data available for this chart.")
        return

    if x not in data.columns or y not in data.columns:
        st.info(
            f"Cannot draw '{title}'. Required columns: {x} and {y}."
        )
        return

    plot_data = data[[x, y]].copy()
    plot_data[y] = pd.to_numeric(
        plot_data[y], errors="coerce"
    ).fillna(0)

    if plot_data.empty:
        st.info("No data available for this chart.")
        return

    fig = px.bar(
        plot_data,
        x=x,
        y=y,
        title=title,
        color=color if color in plot_data.columns else None,
        text_auto=True
    )

    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        xaxis_tickangle=-35,
        height=430
    )

    st.plotly_chart(fig, use_container_width=True)


def chart_pie(data, names, values, title):
    if data.empty:
        st.info("No data available for this chart.")
        return

    if names not in data.columns or values not in data.columns:
        st.info(
            f"Cannot draw '{title}'. Required columns: "
            f"{names} and {values}."
        )
        return

    plot_data = data[[names, values]].copy()
    plot_data[values] = pd.to_numeric(
        plot_data[values], errors="coerce"
    ).fillna(0)

    plot_data = plot_data[plot_data[values] > 0]

    if plot_data.empty:
        st.info("There are no positive values to display.")
        return

    fig = px.pie(
        plot_data,
        names=names,
        values=values,
        title=title,
        hole=0.35
    )

    st.plotly_chart(fig, use_container_width=True)


def show_metric(label, value):
    if isinstance(value, (int, float, np.integer, np.floating)):
        value = f"{value:,.0f}"
    st.metric(label, value)


def sum_if_exists(data, column):
    return int(number_column(data, column).sum())


# --------------------------------------------------
# 9. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("📌 Navigation")

page = st.sidebar.radio(
    "Choose Dashboard",
    [
        "Overview Dashboard",
        "Skill & Sector Demand",
        "Employment by District",
        "Job Fairs & Companies",
        "Training Institutes",
        "AI Skill Planning",
        "Plans & Execution",
        "Explore CSV Data"
    ]
)


# --------------------------------------------------
# 10. FILTERS
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("🔎 Filters")

districts = sorted(df["District"].dropna().unique().tolist())

selected_districts = st.sidebar.multiselect(
    "Select Districts",
    options=districts,
    default=districts
)

if "Sector" in df.columns:
    sectors = sorted(df["Sector"].dropna().unique().tolist())
else:
    sectors = []

selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=sectors,
    default=sectors
)

if "Skill" in df.columns:
    skills = sorted(df["Skill"].dropna().unique().tolist())
else:
    skills = []

selected_skills = st.sidebar.multiselect(
    "Select Skills",
    options=skills,
    default=skills
)

filtered = df[df["District"].isin(selected_districts)].copy()

if "Sector" in filtered.columns and selected_sectors:
    filtered = filtered[filtered["Sector"].isin(selected_sectors)]
elif "Sector" in filtered.columns and not selected_sectors:
    filtered = filtered.iloc[0:0]

if "Skill" in filtered.columns and selected_skills:
    filtered = filtered[filtered["Skill"].isin(selected_skills)]
elif "Skill" in filtered.columns and not selected_skills:
    filtered = filtered.iloc[0:0]

if not selected_districts:
    filtered = filtered.iloc[0:0]

st.sidebar.caption(
    f"Showing {len(filtered):,} of {len(df):,} rows"
)


# --------------------------------------------------
# 11. OVERVIEW DASHBOARD
# --------------------------------------------------

if page == "Overview Dashboard":

    st.header("📊 Overview Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        show_metric("Districts", filtered["District"].nunique())

    with col2:
        show_metric(
            "Employed Students",
            sum_if_exists(filtered, "Employed Students")
        )

    with col3:
        show_metric(
            "Unemployed Students",
            sum_if_exists(filtered, "Unemployed Students")
        )

    with col4:
        show_metric(
            "Job Openings",
            sum_if_exists(filtered, "Job Openings")
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        if "Employed Students" in filtered.columns:
            employment = (
                filtered.groupby("District", as_index=False)
                ["Employed Students"].sum()
                .sort_values("Employed Students", ascending=False)
            )

            chart_bar(
                employment,
                "District",
                "Employed Students",
                "Employed Students by District"
            )
        else:
            st.info("Employed Students column is missing.")

    with right:
        if "Unemployed Students" in filtered.columns:
            unemployment = (
                filtered.groupby("District", as_index=False)
                ["Unemployed Students"].sum()
                .sort_values("Unemployed Students", ascending=False)
            )

            chart_bar(
                unemployment,
                "District",
                "Unemployed Students",
                "Unemployed Students by District"
            )
        else:
            st.info("Unemployed Students column is missing.")

    st.subheader("Job Openings by District")

    if "Job Openings" in filtered.columns:
        openings = (
            filtered.groupby("District", as_index=False)
            ["Job Openings"].sum()
            .sort_values("Job Openings", ascending=False)
        )

        chart_bar(
            openings,
            "District",
            "Job Openings",
            "Total Job Openings by District"
        )

    st.subheader("Sector Distribution")

    if "Sector" in filtered.columns:
        sector_counts = (
            filtered.groupby("Sector", as_index=False)
            .size()
            .rename(columns={"size": "Records"})
        )

        chart_pie(
            sector_counts,
            "Sector",
            "Records",
            "Records by Sector"
        )


# --------------------------------------------------
# 12. SKILL AND SECTOR DEMAND
# --------------------------------------------------

elif page == "Skill & Sector Demand":

    st.header("💼 Skill & Sector Demand")

    left, right = st.columns(2)

    with left:
        if "Skill" in filtered.columns:
            if "Skill Openings" in filtered.columns:
                skill_data = (
                    filtered.groupby("Skill", as_index=False)
                    ["Skill Openings"].sum()
                    .sort_values("Skill Openings", ascending=False)
                    .head(15)
                )
                chart_bar(
                    skill_data,
                    "Skill",
                    "Skill Openings",
                    "Top 15 Skills by Openings"
                )
            elif "Job Openings" in filtered.columns:
                skill_data = (
                    filtered.groupby("Skill", as_index=False)
                    ["Job Openings"].sum()
                    .sort_values("Job Openings", ascending=False)
                    .head(15)
                )
                chart_bar(
                    skill_data,
                    "Skill",
                    "Job Openings",
                    "Top 15 Skills by Job Openings"
                )
            else:
                st.info("No skill-opening or job-opening column exists.")
        else:
            st.info("Skill column is missing.")

    with right:
        if "Sector" in filtered.columns:
            if "Sector Openings" in filtered.columns:
                sector_data = (
                    filtered.groupby("Sector", as_index=False)
                    ["Sector Openings"].sum()
                    .sort_values("Sector Openings", ascending=False)
                )
                chart_bar(
                    sector_data,
                    "Sector",
                    "Sector Openings",
                    "Job Openings by Sector"
                )
            elif "Job Openings" in filtered.columns:
                sector_data = (
                    filtered.groupby("Sector", as_index=False)
                    ["Job Openings"].sum()
                    .sort_values("Job Openings", ascending=False)
                )
                chart_bar(
                    sector_data,
                    "Sector",
                    "Job Openings",
                    "Job Openings by Sector"
                )
            else:
                st.info("No sector-opening or job-opening column exists.")
        else:
            st.info("Sector column is missing.")

    st.subheader("Filtered Dataset")
    st.dataframe(filtered, use_container_width=True)


# --------------------------------------------------
# 13. EMPLOYMENT BY DISTRICT
# --------------------------------------------------

elif page == "Employment by District":

    st.header("📍 Employment by District")

    if "Employed Students" in filtered.columns:
        employment = (
            filtered.groupby("District", as_index=False)
            ["Employed Students"].sum()
            .sort_values("Employed Students", ascending=False)
        )

        chart_bar(
            employment,
            "District",
            "Employed Students",
            "Employment Comparison by District"
        )

    if "Unemployed Students" in filtered.columns:
        unemployment = (
            filtered.groupby("District", as_index=False)
            ["Unemployed Students"].sum()
            .sort_values("Unemployed Students", ascending=False)
        )

        chart_bar(
            unemployment,
            "District",
            "Unemployed Students",
            "Unemployment Comparison by District"
        )

    if (
        "Employed Students" in filtered.columns
        and "Unemployed Students" in filtered.columns
    ):
        employment_comparison = (
            filtered.groupby("District", as_index=False)[
                ["Employed Students", "Unemployed Students"]
            ].sum()
        )

        fig = px.bar(
            employment_comparison,
            x="District",
            y=["Employed Students", "Unemployed Students"],
            barmode="group",
            title="Employed vs Unemployed Students"
        )

        fig.update_layout(
            xaxis_tickangle=-35,
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 14. JOB FAIRS AND COMPANIES
# --------------------------------------------------

elif page == "Job Fairs & Companies":

    st.header("🎯 Job Fairs & Companies")

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric(
            "Job Fairs Conducted",
            sum_if_exists(filtered, "Job Fairs Conducted")
        )

    with col2:
        show_metric(
            "Students Participated",
            sum_if_exists(filtered, "Students Participated")
        )

    with col3:
        show_metric(
            "Companies Hired",
            sum_if_exists(filtered, "Companies Hired")
        )

    left, right = st.columns(2)

    with left:
        if "Job Fairs Conducted" in filtered.columns:
            fair_data = (
                filtered.groupby("District", as_index=False)
                ["Job Fairs Conducted"].sum()
            )
            chart_bar(
                fair_data,
                "District",
                "Job Fairs Conducted",
                "Job Fairs by District"
            )

    with right:
        if "Companies Participated" in filtered.columns:
            company_data = (
                filtered.groupby("District", as_index=False)
                ["Companies Participated"].sum()
            )
            chart_bar(
                company_data,
                "District",
                "Companies Participated",
                "Participating Companies by District"
            )

    placement_column = (
        "JobFair Students Placed"
        if "JobFair Students Placed" in filtered.columns
        else "Students Placed"
    )

    if placement_column in filtered.columns:
        placement_data = (
            filtered.groupby("District", as_index=False)
            [placement_column].sum()
        )

        chart_bar(
            placement_data,
            "District",
            placement_column,
            "Students Placed through Job Fairs"
        )


# --------------------------------------------------
# 15. TRAINING INSTITUTES
# --------------------------------------------------

elif page == "Training Institutes":

    st.header("🏫 Training Institutes")

    if "Institute" in filtered.columns:
        institute_column = st.selectbox(
            "Select Institute",
            ["All Institutes"] +
            sorted(filtered["Institute"].dropna().unique().tolist())
        )

        institute_data = filtered.copy()

        if institute_column != "All Institutes":
            institute_data = institute_data[
                institute_data["Institute"] == institute_column
            ]

        col1, col2, col3 = st.columns(3)

        with col1:
            show_metric(
                "Students Enrolled",
                sum_if_exists(institute_data, "Students Enrolled")
            )

        with col2:
            show_metric(
                "Students Skilled",
                sum_if_exists(institute_data, "Students Skilled")
            )

        with col3:
            placed_column = (
                "Institute Students Placed"
                if "Institute Students Placed" in institute_data.columns
                else "Students Placed"
            )
            show_metric(
                "Students Placed",
                sum_if_exists(institute_data, placed_column)
            )

        if "Students Enrolled" in institute_data.columns:
            enrolled = (
                institute_data.groupby("Institute", as_index=False)
                ["Students Enrolled"].sum()
            )
            chart_bar(
                enrolled,
                "Institute",
                "Students Enrolled",
                "Students Enrolled by Institute"
            )

        if "Students Skilled" in institute_data.columns:
            skilled = (
                institute_data.groupby("Institute", as_index=False)
                ["Students Skilled"].sum()
            )
            chart_bar(
                skilled,
                "Institute",
                "Students Skilled",
                "Students Skilled by Institute"
            )

        if (
            "Students Enrolled" in institute_data.columns
            and "Students Skilled" in institute_data.columns
        ):
            training_comparison = (
                institute_data.groupby("Institute", as_index=False)[
                    ["Students Enrolled", "Students Skilled"]
                ].sum()
            )

            fig = px.bar(
                training_comparison,
                x="Institute",
                y=["Students Enrolled", "Students Skilled"],
                barmode="group",
                title="Enrolled vs Skilled Students"
            )

            fig.update_layout(xaxis_tickangle=-35, height=450)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(
            "The CSV does not contain an Institute column."
        )


# --------------------------------------------------
# 16. AI SKILL PLANNING
# --------------------------------------------------

elif page == "AI Skill Planning":

    st.header("🤖 AI Skill Planning")
    st.write(
        "This section uses simple data-based rules to identify "
        "skills and districts that may need more training."
    )

    if "Skill" in filtered.columns:
        opening_column = (
            "Skill Openings"
            if "Skill Openings" in filtered.columns
            else "Job Openings"
        )

        if opening_column in filtered.columns:
            skill_demand = (
                filtered.groupby("Skill", as_index=False)
                [opening_column].sum()
                .sort_values(opening_column, ascending=False)
            )

            if not skill_demand.empty:
                st.subheader("Skills with the Highest Demand")
                st.dataframe(
                    skill_demand.head(10),
                    use_container_width=True
                )

                chart_bar(
                    skill_demand.head(10),
                    "Skill",
                    opening_column,
                    "Top Skills Recommended for Training"
                )

                highest_demand = skill_demand.iloc[0]

                st.info(
                    f"Suggested focus: {highest_demand['Skill']}. "
                    f"It has {highest_demand[opening_column]:,.0f} "
                    "recorded openings in the selected data."
                )
        else:
            st.info("Job opening data is unavailable.")

    if (
        "District" in filtered.columns
        and "Unemployed Students" in filtered.columns
    ):
        district_needs = (
            filtered.groupby("District", as_index=False)
            ["Unemployed Students"].sum()
            .sort_values("Unemployed Students", ascending=False)
        )

        st.subheader("Districts with More Unemployed Students")
        st.dataframe(
            district_needs.head(10),
            use_container_width=True
        )

        chart_bar(
            district_needs.head(10),
            "District",
            "Unemployed Students",
            "Districts to Prioritize for Training"
        )

    st.caption(
        "These are basic data-driven suggestions, not predictions from "
        "a trained machine-learning model. Recommendations depend on "
        "the quality and completeness of the uploaded dataset."
    )


# --------------------------------------------------
# 17. PLANS AND EXECUTION
# --------------------------------------------------

elif page == "Plans & Execution":

    st.header("📝 Plans & Execution")

    st.write(
        "Use this section to create a simple training plan "
        "based on the current dashboard filters."
    )

    plan_districts = sorted(
        filtered["District"].dropna().unique().tolist()
    )

    plan_district = st.selectbox(
        "Target District",
        plan_districts if plan_districts else ["No district available"]
    )

    plan_skill_options = (
        sorted(filtered["Skill"].dropna().unique().tolist())
        if "Skill" in filtered.columns else []
    )

    plan_skill = st.selectbox(
        "Training Skill",
        plan_skill_options if plan_skill_options else ["Not available"]
    )

    target_students = st.number_input(
        "Target Number of Students",
        min_value=1,
        max_value=100000,
        value=100,
        step=10
    )

    training_budget = st.number_input(
        "Estimated Training Budget (₹)",
        min_value=0,
        max_value=100000000,
        value=100000,
        step=5000
    )

    if st.button("Generate Training Plan", type="primary"):
        st.subheader("Generated Training Plan")

        st.write(f"**District:** {plan_district}")
        st.write(f"**Skill:** {plan_skill}")
        st.write(f"**Target Students:** {target_students:,}")
        st.write(f"**Estimated Budget:** ₹{training_budget:,.2f}")

        st.write(
            f"**Estimated Cost per Student:** "
            f"₹{training_budget / target_students:,.2f}"
        )

        st.success(
            "Plan generated. Review local job demand, training capacity "
            "and available funds before implementation."
        )


# --------------------------------------------------
# 18. EXPLORE CSV DATA
# --------------------------------------------------

elif page == "Explore CSV Data":

    st.header("📁 Explore CSV Data")

    st.write("### Dataset Preview")
    st.dataframe(filtered, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric("Rows", len(filtered))

    with col2:
        show_metric("Columns", len(filtered.columns))

    with col3:
        show_metric(
            "Missing Values",
            int(filtered.isna().sum().sum())
        )

    st.subheader("Column Information")

    column_info = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": [str(dtype) for dtype in filtered.dtypes],
        "Missing Values": filtered.isna().sum().values,
        "Unique Values": [
            filtered[column].nunique()
            for column in filtered.columns
        ]
    })

    st.dataframe(column_info, use_container_width=True)

    csv_output = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered CSV",
        data=csv_output,
        file_name="karnataka_skills_filtered.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 19. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Karnataka District Skills Dashboard | "
    "Streamlit + Pandas + Plotly"
)
