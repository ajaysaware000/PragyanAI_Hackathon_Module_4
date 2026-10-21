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

        st.write(f"*District:* {district}")
        st.write(f"*Planning Focus:* {focus}")
        st.write(
            f"*Unemployed Students:* "
            f"{int(row['Unemployed Students'])}"
        )
        st.write(
            f"*Available Job Openings:* "
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
