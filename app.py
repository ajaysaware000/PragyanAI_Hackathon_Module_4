import json
import hashlib
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------
# App configuration
# ----------------------------
st.set_page_config(
    page_title="District Admin | Labour & Skill",
    page_icon="📊",
    layout="wide",
)

DATA_FILE = Path("karnataka_district_skills.csv")
PLANS_FILE = Path("skill_plans.json")
USERS_FILE = Path("users.json")

st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    [data-testid="stMetric"] {
        background: white; padding: 16px; border-radius: 12px;
        border: 1px solid #e8edf5;
    }
    .block-container {padding-top: 1.5rem;}
    h1, h2, h3 {color: #17365d;}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# Helpers
# ----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_dataset():
    if not DATA_FILE.exists():
        return None, (
            f"Could not find **{DATA_FILE.name}**. Put this CSV file in the same folder "
            "as `app.py`, then restart Streamlit."
        )

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as exc:
        return None, f"Could not read the CSV file: {exc}"

    # Normalize column names and handle duplicate headings such as "Students Placed".
    df.columns = [str(c).strip() for c in df.columns]
    if list(df.columns).count("Students Placed") > 1:
        placed_positions = [i for i, c in enumerate(df.columns) if c == "Students Placed"]
        df.columns.values[placed_positions[0]] = "JobFair Students Placed"
        df.columns.values[placed_positions[1]] = "Institute Students Placed"

    required = [
        "District", "Employed Students", "Unemployed Students", "Job Openings",
        "Skill", "Skill Openings", "Sector", "Sector Openings",
        "Job Fairs Conducted", "Students Participated", "Companies Participated",
        "Companies Hired", "Institute", "Students Enrolled", "Students Skilled",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, (
            "Your CSV is missing these required columns: "
            + ", ".join(f"`{c}`" for c in missing)
            + ". Please check the column headings."
        )

    numeric_cols = [
        "Employed Students", "Unemployed Students", "Job Openings",
        "Skill Openings", "Sector Openings", "Job Fairs Conducted",
        "Students Participated", "Companies Participated", "Companies Hired",
        "Students Enrolled", "Students Skilled",
        "JobFair Students Placed", "Institute Students Placed",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["District", "Skill", "Sector", "Institute"]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    return df, None


def total(df, col):
    return int(df[col].sum()) if col in df.columns else 0


def safe_rate(numerator, denominator):
    return (100 * numerator / denominator) if denominator else 0.0


def skill_recommendations(df):
    """Rule-based recommendations using available CSV fields, not an external AI model."""
    skill_demand = (
        df.groupby("Skill", as_index=False)["Skill Openings"]
        .sum()
        .sort_values("Skill Openings", ascending=False)
    )
    district_unemployment = (
        df.groupby("District", as_index=False)["Unemployed Students"]
        .sum()
        .sort_values("Unemployed Students", ascending=False)
    )
    institute_stats = df.groupby("Institute", as_index=False).agg(
        Enrolled=("Students Enrolled", "sum"),
        Skilled=("Students Skilled", "sum"),
        Placed=("Institute Students Placed", "sum") if "Institute Students Placed" in df.columns
        else ("Students Skilled", "sum"),
    )
    institute_stats["Skill Rate (%)"] = (
        institute_stats["Skilled"] / institute_stats["Enrolled"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    institute_stats["Placement Rate (%)"] = (
        institute_stats["Placed"] / institute_stats["Skilled"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    institute_stats = institute_stats.sort_values(
        ["Placement Rate (%)", "Skill Rate (%)"], ascending=False
    )
    sector_demand = (
        df.groupby("Sector", as_index=False)["Sector Openings"]
        .sum()
        .sort_values("Sector Openings", ascending=False)
    )
    return skill_demand, district_unemployment, institute_stats, sector_demand


# ----------------------------
# Authentication (demo/local only)
# ----------------------------
def auth_screen():
    st.title("🔐 Labour & Skill Portal")
    st.caption("District Admin • Karnataka")
    st.info(
        "Demo authentication stores users locally in `users.json`. "
        "For production use, replace this with secure identity management."
    )
    login_tab, register_tab = st.tabs(["Login", "Register"])

    users = read_json(USERS_FILE, {})

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            record = users.get(username.strip())
            if record and record.get("password_hash") == hash_password(password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username.strip()
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Create username", key="register_username")
            new_password = st.text_input("Create password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted_register = st.form_submit_button("Create account", use_container_width=True)
        if submitted_register:
            clean_name = new_username.strip()
            if len(clean_name) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(new_password) < 6:
                st.error("Use a password with at least 6 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif clean_name in users:
                st.error("That username already exists.")
            else:
                users[clean_name] = {"password_hash": hash_password(new_password)}
                write_json(USERS_FILE, users)
                st.success("Account created. Open the Login tab to sign in.")


# ----------------------------
# Main application
# ----------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    auth_screen()
    st.stop()

df, load_error = load_dataset()

with st.sidebar:
    st.title("🏛️ Labour & Skill")
    st.caption(f"Signed in as **{st.session_state.get('username', 'Admin')}**")
    if st.button("Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("username", None)
        st.rerun()
    st.divider()
    page = st.radio(
        "Navigation",
        [
            "Overview Dashboard",
            "Skill & Sector Demand",
            "Employment by District",
            "Job Fairs & Companies",
            "Training Institutes",
            "AI Skill Planning",
            "Plans & Execution",
            "Explore CSV Data",
        ],
    )
    st.divider()
    st.caption("Data source")
    st.code(DATA_FILE.name)

st.title("District Admin — Labour & Skill Management")
st.caption("Explore district employment, skill demand, job fairs, training outcomes, and skill plans.")

if load_error:
    st.error(load_error)
    st.markdown("""
    **Folder layout**
    ```text
    your-project/
    ├── app.py
    ├── requirements.txt
    └── karnataka_district_skills.csv
    ```
    """)
    st.stop()

# Global filters
with st.expander("🔎 Filter dashboard data", expanded=True):
    c1, c2, c3 = st.columns(3)
    all_districts = sorted(df["District"].dropna().unique().tolist())
    selected_districts = c1.multiselect(
        "Districts", all_districts, default=all_districts
    )
    all_sectors = sorted(df["Sector"].dropna().unique().tolist())
    selected_sectors = c2.multiselect("Sectors", all_sectors, default=all_sectors)
    all_skills = sorted(df["Skill"].dropna().unique().tolist())
    selected_skills = c3.multiselect("Skills", all_skills, default=all_skills)

filtered = df[
    df["District"].isin(selected_districts)
    & df["Sector"].isin(selected_sectors)
    & df["Skill"].isin(selected_skills)
].copy()

if filtered.empty:
    st.warning("No rows match these filters. Please select at least one district, sector, and skill.")
    st.stop()

skill_demand, district_unemployment, institute_stats, sector_demand = skill_recommendations(filtered)

if page == "Overview Dashboard":
    st.subheader("📌 Key Indicators")
    metrics = [
        ("Employed Students", total(filtered, "Employed Students")),
        ("Unemployed Students", total(filtered, "Unemployed Students")),
        ("Job Openings", total(filtered, "Job Openings")),
        ("Job Fairs Conducted", total(filtered, "Job Fairs Conducted")),
        ("Students Participated", total(filtered, "Students Participated")),
        ("Job Fair Placements", total(filtered, "JobFair Students Placed")),
    ]
    cols = st.columns(3)
    for i, (label, value) in enumerate(metrics):
        cols[i % 3].metric(label, f"{value:,}")

    left, right = st.columns(2)
    with left:
        emp = filtered.groupby("District", as_index=False)[
            ["Employed Students", "Unemployed Students"]
        ].sum().sort_values("Unemployed Students", ascending=False)
        fig = px.bar(emp, x="District", y=["Employed Students", "Unemployed Students"],
                     barmode="group", title="Employment status by district")
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(skill_demand.head(10), x="Skill Openings", y="Skill",
                     orientation="h", title="Top skills by openings")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("District snapshot")
    district_summary = filtered.groupby("District", as_index=False).agg(
        Employed=("Employed Students", "sum"),
        Unemployed=("Unemployed Students", "sum"),
        Job_Openings=("Job Openings", "sum"),
        Job_Fairs=("Job Fairs Conducted", "sum"),
    )
    st.dataframe(district_summary, use_container_width=True, hide_index=True)

elif page == "Skill & Sector Demand":
    st.subheader("📈 Skill-wise and Sector-wise Growth / Demand")
    st.caption("The CSV contains opening counts, not historical dates. These charts show current demand in the supplied sample, not time-based growth.")
    left, right = st.columns(2)
    with left:
        fig = px.bar(skill_demand, x="Skill Openings", y="Skill", orientation="h",
                     title="Skill openings")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(sector_demand, x="Sector Openings", y="Sector", orientation="h",
                     title="Sector openings")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Skill and sector data")
    a, b = st.columns(2)
    with a:
        st.dataframe(skill_demand.sort_values("Skill Openings", ascending=False),
                     use_container_width=True, hide_index=True)
    with b:
        st.dataframe(sector_demand.sort_values("Sector Openings", ascending=False),
                     use_container_width=True, hide_index=True)

    st.markdown("#### District-wise skill openings")
    skill_district = filtered.groupby(["District", "Skill"], as_index=False)["Skill Openings"].sum()
    st.dataframe(skill_district.sort_values("Skill Openings", ascending=False),
                 use_container_width=True, hide_index=True)

elif page == "Employment by District":
    st.subheader("👥 Student Employment & Unemployment")
    district_employment = filtered.groupby("District", as_index=False).agg(
        Employed=("Employed Students", "sum"),
        Unemployed=("Unemployed Students", "sum"),
        Job_Openings=("Job Openings", "sum"),
    )
    district_employment["Unemployment share (%)"] = (
        district_employment["Unemployed"] /
        (district_employment["Employed"] + district_employment["Unemployed"]).replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    fig = px.bar(district_employment, x="District", y=["Employed", "Unemployed"],
                 barmode="group", title="Employed vs unemployed students")
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(district_employment.sort_values("Unemployed", ascending=False),
                 use_container_width=True, hide_index=True)

    st.markdown("#### District-wise openings by skill")
    openings = filtered.groupby(["District", "Skill"], as_index=False)["Skill Openings"].sum()
    st.dataframe(openings.sort_values("Skill Openings", ascending=False),
                 use_container_width=True, hide_index=True)

elif page == "Job Fairs & Companies":
    st.subheader("🤝 Job Fairs and Hiring Companies")
    metrics = [
        ("Job fairs", total(filtered, "Job Fairs Conducted")),
        ("Students participated", total(filtered, "Students Participated")),
        ("Students placed", total(filtered, "JobFair Students Placed")),
        ("Companies participated", total(filtered, "Companies Participated")),
        ("Companies hired", total(filtered, "Companies Hired")),
    ]
    cols = st.columns(3)
    for i, (label, value) in enumerate(metrics):
        cols[i % 3].metric(label, f"{value:,}")

    fair_summary = filtered.groupby("District", as_index=False).agg(
        Job_Fairs=("Job Fairs Conducted", "sum"),
        Students_Participated=("Students Participated", "sum"),
        Students_Placed=("JobFair Students Placed", "sum"),
        Companies_Participated=("Companies Participated", "sum"),
        Companies_Hired=("Companies Hired", "sum"),
    )
    fair_summary["Placement rate (%)"] = (
        fair_summary["Students_Placed"] /
        fair_summary["Students_Participated"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    fig = px.bar(fair_summary, x="District",
                 y=["Companies_Participated", "Companies_Hired"],
                 barmode="group", title="Companies participating vs hiring")
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(fair_summary.sort_values("Students_Placed", ascending=False),
                 use_container_width=True, hide_index=True)
    st.info("Company names are not present in this CSV. The app can compare company counts, but cannot list individual hiring companies without another company-level dataset.")

elif page == "Training Institutes":
    st.subheader("🎓 Training Institute Performance")
    st.caption("Ranking is based on placement rate, then skill rate. The ranking is indicative because the source contains aggregated sample records.")
    st.dataframe(institute_stats, use_container_width=True, hide_index=True)
    fig = px.bar(institute_stats, x="Institute", y=["Enrolled", "Skilled", "Placed"],
                 barmode="group", title="Enrolled, skilled, and placed students by institute")
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Institute selection")
    chosen = st.selectbox("View an institute", sorted(filtered["Institute"].unique()))
    institute_rows = filtered[filtered["Institute"] == chosen]
    st.dataframe(institute_rows, use_container_width=True, hide_index=True)

elif page == "AI Skill Planning":
    st.subheader("🧠 AI-Assisted Skill Planning")
    st.caption("This starter version uses transparent, rule-based recommendations from your CSV. It does not call an external AI model.")
    top_skills = skill_demand.head(5)["Skill"].tolist()
    top_sectors = sector_demand.head(5)["Sector"].tolist()
    top_districts = district_unemployment.head(5)["District"].tolist()

    st.markdown("#### Generated Skill Gap & Demand Report")
    st.write(f"**Districts with the highest recorded unemployment:** {', '.join(top_districts) if top_districts else 'No data'}")
    st.write(f"**Skills with the most recorded openings:** {', '.join(top_skills) if top_skills else 'No data'}")
    st.write(f"**Sectors with the most recorded openings:** {', '.join(top_sectors) if top_sectors else 'No data'}")

    recommendations = []
    for _, row in district_unemployment.head(5).iterrows():
        district = row["District"]
        district_rows = filtered[filtered["District"] == district]
        local_skills = district_rows.groupby("Skill")["Skill Openings"].sum().sort_values(ascending=False)
        local_sectors = district_rows.groupby("Sector")["Sector Openings"].sum().sort_values(ascending=False)
        recommendations.append({
            "District": district,
            "Unemployed Students": int(row["Unemployed Students"]),
            "Suggested Skill": local_skills.index[0] if len(local_skills) else "Review local demand",
            "Suggested Sector": local_sectors.index[0] if len(local_sectors) else "Review local demand",
            "Reason": "Prioritize training and employer outreach; validate with local labour-market data.",
        })
    st.markdown("#### Recommended district actions")
    st.dataframe(pd.DataFrame(recommendations), use_container_width=True, hide_index=True)

    st.markdown("#### Create a Skill Plan")
    with st.form("skill_plan_form"):
        plan_title = st.text_input("Plan title", value="District Skill Gap Action Plan")
        plan_district = st.selectbox("Target district", sorted(filtered["District"].unique()))
        plan_skill = st.selectbox("Skill to focus on", sorted(filtered["Skill"].unique()))
        plan_institute = st.selectbox("Training institute", sorted(filtered["Institute"].unique()))
        plan_sector = st.selectbox("Target sector", sorted(filtered["Sector"].unique()))
        plan_company = st.text_input("Company to invite (optional; enter manually)")
        target_students = st.number_input("Target students to train", min_value=1, max_value=100000, value=100)
        plan_notes = st.text_area("Action / notes", value="Train students in the selected skill and coordinate employer interviews.")
        create_plan = st.form_submit_button("Save Skill Plan", use_container_width=True)

    if create_plan:
        plans = read_json(PLANS_FILE, [])
        plans.append({
            "id": f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": plan_title,
            "district": plan_district,
            "skill": plan_skill,
            "institute": plan_institute,
            "sector": plan_sector,
            "company": plan_company.strip(),
            "target_students": int(target_students),
            "notes": plan_notes,
            "status": "Planned",
            "created_date": str(date.today()),
            "executed_date": "",
            "actual_students_trained": 0,
            "result_notes": "",
        })
        write_json(PLANS_FILE, plans)
        st.success("Skill plan saved to skill_plans.json.")
        st.rerun()

elif page == "Plans & Execution":
    st.subheader("🗂️ Plans, Execution, and Results")
    plans = read_json(PLANS_FILE, [])
    if not plans:
        st.info("No plans saved yet. Create one from the AI Skill Planning page.")
    else:
        plan_df = pd.DataFrame(plans)
        st.markdown("#### Saved plans")
        st.dataframe(plan_df, use_container_width=True, hide_index=True)

        plan_ids = [p["id"] for p in plans]
        selected_id = st.selectbox("Choose a plan to update", plan_ids)
        selected_plan = next(p for p in plans if p["id"] == selected_id)
        with st.form("update_plan_form"):
            status = st.selectbox(
                "Status",
                ["Planned", "In Progress", "Executed", "On Hold"],
                index=["Planned", "In Progress", "Executed", "On Hold"].index(
                    selected_plan.get("status", "Planned")
                ),
            )
            executed_date = st.date_input(
                "Execution date",
                value=date.fromisoformat(selected_plan["executed_date"])
                if selected_plan.get("executed_date") else date.today(),
            )
            actual_students = st.number_input(
                "Students actually trained",
                min_value=0, max_value=100000,
                value=int(selected_plan.get("actual_students_trained", 0)),
            )
            result_notes = st.text_area(
                "Result / outcome notes", value=selected_plan.get("result_notes", "")
            )
            save_update = st.form_submit_button("Update plan status", use_container_width=True)
        if save_update:
            for p in plans:
                if p["id"] == selected_id:
                    p["status"] = status
                    p["executed_date"] = str(executed_date) if status == "Executed" else ""
                    p["actual_students_trained"] = int(actual_students)
                    p["result_notes"] = result_notes
            write_json(PLANS_FILE, plans)
            st.success("Plan updated.")
            st.rerun()

        st.markdown("#### Plan status summary")
        status_counts = pd.DataFrame(plans)["status"].value_counts().rename_axis("Status").reset_index(name="Plans")
        st.plotly_chart(px.pie(status_counts, names="Status", values="Plans", title="Plans by status"),
                        use_container_width=True)

        executed = [p for p in plans if p.get("status") == "Executed"]
        st.metric("Executed plans", len(executed))
        st.metric("Students trained across executed plans",
                  sum(int(p.get("actual_students_trained", 0)) for p in executed))
        st.info("Trend unemployment and skill gaps over time require dated historical CSV snapshots. This starter app displays current indicators and stores plan execution dates for future tracking.")

elif page == "Explore CSV Data":
    st.subheader("📄 Explore Source Dataset")
    st.write(f"Rows: **{len(filtered):,}** · Columns: **{len(filtered.columns)}**")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_karnataka_district_skills.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Prototype note: use verified official data before making policy decisions. "
    "This app's rankings and recommendations are based only on the fields present in the uploaded CSV."
)
