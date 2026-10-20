from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.analytics import (
    calculate_priorities,
    cluster_districts,
    compare_districts,
    extract_skills,
    forecast_demand,
    skill_gap_table,
    what_if_priorities,
)
from src.ai_assistant import (
    answer_with_llm,
    generate_policy_draft,
    retrieve_documents,
)
from src.agent_workflow import run_district_agent
from src.data_utils import normalize_district_data, validate_data
from src.reports import create_excel_report, create_pdf_report

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "documents"
OUTPUT_DIR = ROOT / "outputs"

DOCS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="K-SIWAP",
    page_icon="📊",
    layout="wide",
)

st.title("K-SIWAP")
st.subheader("Karnataka Skill Intelligence & Workforce Analytics Platform")

st.info(
    "Prototype notice: included datasets are SAMPLE DEMO DATA, "
    "not verified official government statistics."
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_project_data():
    district_data = pd.read_csv(
        DATA_DIR / "district_indicators_sample.csv"
    )
    job_data = pd.read_csv(
        DATA_DIR / "job_postings_sample.csv"
    )
    historical_data = pd.read_csv(
        DATA_DIR / "historical_demand_sample.csv"
    )
    return district_data, job_data, historical_data


try:
    data, jobs, history = load_project_data()
except FileNotFoundError as error:
    st.error(
        f"Required CSV file not found: {error.filename}. "
        "Check the files inside your data/ folder."
    )
    st.stop()

# --------------------------------------------------
# 2. SIDEBAR CONTROLS
# --------------------------------------------------

with st.sidebar:
    st.title("Project Controls")

    page = st.radio(
        "Choose a page",
        [
            "Overview",
            "District Comparison",
            "Skill Gaps & Priorities",
            "AI / ML Lab",
            "AI Planning Assistant",
            "RAG Policy Assistant",
            "Agentic Workflow",
            "Scenario Simulator",
            "Data Quality & Guide",
        ],
    )

    districts = sorted(data["district"].dropna().unique())

    selected_district = st.selectbox(
        "Select district",
        districts,
    )

    st.divider()
    st.subheader("Priority scoring weights")

    weights = {
        "demand": st.slider(
            "Employer demand",
            0, 100, 40
        ),
        "gap": st.slider(
            "Skill gap",
            0, 100, 30
        ),
        "training": st.slider(
            "Training capacity",
            0, 100, 20
        ),
        "momentum": st.slider(
            "Demand momentum",
            0, 100, 10
        ),
    }

    st.caption(
        "Weights are normalized automatically. "
        "These are illustrative values, not official policy weights."
    )

    district_upload = st.file_uploader(
        "Upload district data CSV",
        type=["csv"],
    )

    job_upload = st.file_uploader(
        "Upload job descriptions CSV",
        type=["csv"],
    )

    document_upload = st.file_uploader(
        "Upload policy document",
        type=["txt", "md"],
    )

# --------------------------------------------------
# 3. OPTIONAL FILE UPLOADS
# --------------------------------------------------

if district_upload is not None:
    try:
        uploaded_data = normalize_district_data(
            pd.read_csv(district_upload)
        )

        required_columns = {
            "district",
            "sector",
            "employer_demand",
            "skill_gap",
            "training_capacity",
            "demand_momentum",
        }

        missing = required_columns - set(uploaded_data.columns)

        if missing:
            st.error(
                "District CSV is missing these columns: "
                + ", ".join(sorted(missing))
            )
        else:
            data = pd.concat(
                [data, uploaded_data],
                ignore_index=True,
            ).drop_duplicates(
                subset=["district", "sector"],
                keep="last",
            )

            st.sidebar.success("District CSV loaded.")

    except Exception as error:
        st.sidebar.error(f"District upload error: {error}")

if job_upload is not None:
    try:
        uploaded_jobs = pd.read_csv(job_upload)

        if "description" not in uploaded_jobs.columns:
            st.sidebar.error(
                "Job CSV must contain a description column."
            )
        else:
            jobs = uploaded_jobs
            st.sidebar.success("Job descriptions loaded.")

    except Exception as error:
        st.sidebar.error(f"Job upload error: {error}")

if document_upload is not None:
    try:
        safe_name = Path(document_upload.name).name
        document_path = DOCS_DIR / safe_name

        document_path.write_text(
            document_upload.getvalue().decode(
                "utf-8", errors="ignore"
            ),
            encoding="utf-8",
        )

        st.sidebar.success(
            f"Document saved: {safe_name}"
        )

    except Exception as error:
        st.sidebar.error(f"Document upload error: {error}")

# --------------------------------------------------
# 4. CALCULATE PRIORITIES
# --------------------------------------------------

priorities = calculate_priorities(data, weights)

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":
    st.header(f"District Overview: {selected_district}")

    district_data = data[
        data["district"] == selected_district
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Sectors represented",
        int(district_data["sector"].nunique()),
    )

    col2.metric(
        "Average employer demand",
        f"{district_data['employer_demand'].mean():.1f}/100",
    )

    col3.metric(
        "Average skill gap",
        f"{district_data['skill_gap'].mean():.1f}/100",
    )

    col4.metric(
        "Training capacity",
        f"{district_data['training_capacity'].mean():.1f}/100",
    )

    chart1, chart2 = st.columns(2)

    with chart1:
        st.plotly_chart(
            px.bar(
                district_data,
                x="sector",
                y="employer_demand",
                title="Employer Demand by Sector",
            ),
            use_container_width=True,
        )

    with chart2:
        st.plotly_chart(
            px.bar(
                district_data,
                x="sector",
                y="skill_gap",
                title="Skill Gap by Sector",
            ),
            use_container_width=True,
        )

    st.subheader("District Priority Rankings")

    district_priorities = priorities[
        priorities["district"] == selected_district
    ].sort_values("priority_score", ascending=False)

    st.dataframe(
        district_priorities,
        use_container_width=True,
    )

# --------------------------------------------------
# PAGE 2: DISTRICT COMPARISON
# --------------------------------------------------

elif page == "District Comparison":
    st.header("District Comparison")

    selected_districts = st.multiselect(
        "Choose districts",
        districts,
        default=districts[:min(4, len(districts))],
    )

    comparison = compare_districts(
        data,
        selected_districts,
    )

    st.dataframe(
        comparison,
        use_container_width=True,
    )

    if not comparison.empty:
        metric = st.selectbox(
            "Choose comparison metric",
            [
                "employer_demand",
                "skill_gap",
                "training_capacity",
                "demand_momentum",
            ],
        )

        st.plotly_chart(
            px.bar(
                comparison,
                x="district",
                y=metric,
                color="district",
                title=f"District Comparison: {metric}",
            ),
            use_container_width=True,
        )

    st.subheader("Similar Districts: Clustering")

    clusters = cluster_districts(data)

    st.dataframe(
        clusters,
        use_container_width=True,
    )

# --------------------------------------------------
# PAGE 3: SKILL GAPS & PRIORITIES
# --------------------------------------------------

elif page == "Skill Gaps & Priorities":
    st.header("Skill Gap Analysis")

    gaps = skill_gap_table(data, jobs)

    st.dataframe(
        gaps,
        use_container_width=True,
    )

    st.subheader("Explainable Priority Scoring")

    st.write(
        "Review the individual contribution columns to see "
        "how each indicator affects the total score."
    )

    st.dataframe(
        priorities.sort_values(
            "priority_score",
            ascending=False,
        ),
        use_container_width=True,
    )

    comparison = compare_districts(data, districts)

    st.subheader("Download Reports")

    excel_path = create_excel_report(
        priorities,
        gaps,
        comparison,
        OUTPUT_DIR,
    )

    pdf_path = create_pdf_report(
        priorities,
        gaps,
        OUTPUT_DIR,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download Excel Report",
            data=excel_path.read_bytes(),
            file_name="ksiwap_planning_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    with col2:
        st.download_button(
            "Download PDF Report",
            data=pdf_path.read_bytes(),
            file_name="ksiwap_planning_report.pdf",
            mime="application/pdf",
        )

# --------------------------------------------------
# PAGE 4: AI / ML LAB
# --------------------------------------------------

elif page == "AI / ML Lab":
    st.header("AI and Machine Learning Lab")

    st.subheader("NLP: Skill Extraction from Job Descriptions")

    if "description" not in jobs.columns:
        st.warning(
            "Upload a job CSV containing a description column."
        )
    else:
        job_results = jobs.copy()

        job_results["extracted_skills"] = (
            job_results["description"]
            .fillna("")
            .apply(lambda text: ", ".join(extract_skills(text)))
        )

        st.dataframe(
            job_results,
            use_container_width=True,
        )

        all_skills = [
            skill
            for description in jobs["description"].fillna("")
            for skill in extract_skills(description)
        ]

        if all_skills:
            skill_counts = (
                pd.Series(all_skills)
                .value_counts()
                .rename_axis("skill")
                .reset_index(name="mentions")
            )

            st.plotly_chart(
                px.bar(
                    skill_counts,
                    x="skill",
                    y="mentions",
                    title="Skills Mentioned in Job Descriptions",
                ),
                use_container_width=True,
            )

    st.subheader("Machine Learning: Demand Trend")

    forecast_sector = st.selectbox(
        "Choose sector for trend analysis",
        sorted(data["sector"].unique()),
    )

    forecast = forecast_demand(
        history,
        selected_district,
        forecast_sector,
    )

    if forecast.empty:
        st.warning(
            "Insufficient historical observations for this district "
            "and sector. Add at least three distinct years of data."
        )
    else:
        st.dataframe(forecast, use_container_width=True)

        st.plotly_chart(
            px.line(
                forecast,
                x="year",
                y="demand_index",
                color="kind",
                markers=True,
                title="Historical Demand and Baseline Trend Estimate",
            ),
            use_container_width=True,
        )

    st.caption(
        "Skill extraction is a keyword-based NLP baseline. "
        "The trend estimate is not a validated economic forecast."
    )

# --------------------------------------------------
# PAGE 5: AI PLANNING ASSISTANT
# --------------------------------------------------

elif page == "AI Planning Assistant":
    st.header("AI District Planning Assistant")

    question = st.text_area(
        "Ask a question",
        placeholder=(
            "Why is a sector ranked highly in this district?"
        ),
    )

    if st.button("Generate Answer", type="primary"):
        context = priorities[
            priorities["district"] == selected_district
        ].to_string(index=False)

        answer, mode = answer_with_llm(
            question,
            context,
            data,
            selected_district,
        )

        st.markdown("### Answer")
        st.write(answer)
        st.caption(f"Response mode: {mode}")

# --------------------------------------------------
# PAGE 6: RAG POLICY ASSISTANT
# --------------------------------------------------

elif page == "RAG Policy Assistant":
    st.header("RAG Policy and Report Assistant")

    st.write(
        "Add policy or industry documents to the documents folder, "
        "or upload a TXT/MD document from the sidebar."
    )

    question = st.text_input(
        "Ask a question about your documents",
        placeholder=(
            "What should planners verify before launching training?"
        ),
    )

    if st.button("Retrieve Documents and Answer"):
        retrieved = retrieve_documents(
            question,
            DOCS_DIR,
        )

        if not retrieved:
            st.warning(
                "No documents found. Add TXT or MD files first."
            )
        else:
            st.subheader("Retrieved Evidence")

            for index, item in enumerate(retrieved, start=1):
                with st.expander(
                    f"Source {index}: {item['source']}"
                ):
                    st.write(item["text"])
                    st.caption(
                        f"Keyword overlap score: {item['score']}"
                    )

            answer, mode = answer_with_llm(
                question,
                "\n\n".join(
                    item["text"] for item in retrieved
                ),
                data,
                selected_district,
            )

            st.subheader("Answer")
            st.write(answer)
            st.caption(f"Response mode: {mode}")

    st.caption(
        "Current retrieval is a simple local baseline. "
        "Semantic embeddings and vector search can be added later."
    )

# --------------------------------------------------
# PAGE 7: AGENTIC WORKFLOW
# --------------------------------------------------

elif page == "Agentic Workflow":
    st.header("Agentic District Analysis")

    st.write(
        "The workflow coordinates data validation, priority scoring, "
        "document retrieval, and draft report generation."
    )

    if st.button("Run District Analysis", type="primary"):
        result = run_district_agent(
            selected_district,
            data,
            priorities,
            DOCS_DIR,
        )

        st.subheader("Workflow Steps")

        for step in result["steps"]:
            st.write(f"✓ {step}")

        st.subheader("Findings")
        st.write(result["summary"])

        st.subheader("District Priority Results")

        st.dataframe(
            result["priorities"],
            use_container_width=True,
        )

        st.subheader("Draft Policy Summary")

        st.write(
            generate_policy_draft(
                result["summary"],
                result["priorities"],
            )
        )

# --------------------------------------------------
# PAGE 8: WHAT-IF SCENARIO SIMULATOR
# --------------------------------------------------

elif page == "Scenario Simulator":
    st.header("What-If Scenario Simulator")

    st.write(
        "Change the sidebar weights to see how priority scores "
        "change relative to the baseline weights."
    )

    baseline = calculate_priorities(
        data,
        {
            "demand": 40,
            "gap": 30,
            "training": 20,
            "momentum": 10,
        },
    )

    scenario = calculate_priorities(
        data,
        weights,
    )

    comparison = what_if_priorities(
        baseline,
        scenario,
    )

    st.dataframe(
        comparison.sort_values(
            "scenario_score",
            ascending=False,
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        px.scatter(
            comparison,
            x="baseline_score",
            y="scenario_score",
            color="district",
            hover_data=["sector"],
            title="Baseline vs Scenario Scores",
        ),
        use_container_width=True,
    )

# --------------------------------------------------
# PAGE 9: DATA QUALITY & GUIDE
# --------------------------------------------------

elif page == "Data Quality & Guide":
    st.header("Data Quality and Project Guide")

    st.subheader("Data Quality Report")

    st.json(validate_data(data))

    st.subheader("Required District CSV Columns")

    st.code(
        "district, sector, employer_demand, skill_gap, "
        "training_capacity, demand_momentum"
    )

    st.subheader("Job Description CSV Columns")

    st.code(
        "district, sector, title, description, source, posted_on"
    )

    st.subheader("Historical Demand CSV Columns")

    st.code(
        "district, sector, year, demand_index"
    )

    st.warning(
        "Keep source, date, geography, definitions, and limitations "
        "with every dataset. Sample data must not be treated as "
        "verified official statistics."
    )

st.divider()
st.caption(
    "K-SIWAP prototype | Recommendations require evidence checks "
    "and human review before policy use."
)
