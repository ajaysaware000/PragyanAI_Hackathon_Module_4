        PHASE 1
    </p>
    <h1 style="margin:8px 0;">Explore: Labour & Skill Ecosystem</h1>
    <p style="font-size:16px; margin-bottom:0;">
        A common starting point for district administrators, state administrators,
        training institutes, and job fair companies.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# USERS / ROLE DIRECTORY
# --------------------------------------------------
roles = {
    "District Admin — Labour & Skill": {
        "icon": "🏢",
        "description": "Explore district-level labour and skill information, local needs, and activities."
    },
    "State Admin — Labour & Skill": {
        "icon": "🏛️",
        "description": "Explore state-level labour and skill information and district-level overview."
    },
    "Training Institutes": {
        "icon": "🎓",
        "description": "A place for training institutes to be represented in the labour and skill ecosystem."
    },
    "Job Fair Companies": {
        "icon": "🤝",
        "description": "A place for companies participating in or organising job fair activities."
    }
}

if page == "Explore Dashboard":
    st.subheader("Explore Dashboard")
    st.write(
        "Choose a user group to begin exploring the Labour & Skill module. "
        "This version sets up the structure; detailed workflows will be added in later updates."
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Phase", "01 — Explore")
    m2.metric("User Groups", "4")
    m3.metric("Domain", "Labour & Skill")
    m4.metric("Version", "Starter")

    st.markdown("### Users")
    cols = st.columns(2)
    for i, (role_name, details) in enumerate(roles.items()):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="role-card">
                    <div class="role-icon">{details['icon']}</div>
                    <div class="role-title">{role_name}</div>
                    <p class="role-desc">{details['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")
            if st.button(f"Explore {role_name}", key=f"explore_{i}", use_container_width=True):
                st.session_state["selected_role"] = role_name
                st.rerun()

    selected_role = st.session_state.get("selected_role")
    if selected_role:
        st.divider()
        st.markdown(f"### Selected user group: {selected_role}")
        st.info("This section is ready for the next features you want to add.")

elif page == "Users":
    st.subheader("Users")
    st.write("The first version includes these four user groups:")
    users_df = pd.DataFrame([
        {"No.": 1, "User Group": "District Admin — Labour & Skill"},
        {"No.": 2, "User Group": "State Admin — Labour & Skill"},
        {"No.": 3, "User Group": "Training Institutes"},
        {"No.": 4, "User Group": "Job Fair Companies"}
    ])
    st.dataframe(users_df, use_container_width=True, hide_index=True)

elif page == "District Admin":
    st.subheader("🏢 District Admin — Labour & Skill")
    st.write("Explore district-level labour and skill information.")
    st.info("District-specific dashboards, filters, reports, and actions can be added in the next phase.")

elif page == "State Admin":
    st.subheader("🏛️ State Admin — Labour & Skill")
    st.write("Explore state-level labour and skill information across districts.")
    st.info("State-wide summaries, district comparisons, and monitoring tools can be added later.")

elif page == "Training Institutes":
    st.subheader("🎓 Training Institutes")
    st.write("Explore the training institute user group.")
    st.info("Institute profiles, courses, seats, enrolments, and outcomes can be added when you provide the requirements.")

elif page == "Job Fair Companies":
    st.subheader("🤝 Job Fair Companies")
    st.write("Explore companies associated with job fairs.")
    st.info("Company profiles, vacancies, job fairs, and recruitment outcomes can be added when you provide the requirements.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("Phase 1: Explore | Labour & Skill | Initial prototype — sample structure only")
