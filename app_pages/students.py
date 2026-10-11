"""
Page: Students Management & Scoped Roster View
Allows educators to browse student cohorts, inspect academic standing, and launch targeted risk assessments.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config.theme import (
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER
)
from database.database import SessionLocal
from database.models import Student, Prediction
from services.auth_service import get_scoped_students, log_audit_event

def render_students(current_user=None):
    st.markdown(f"""
    <div style="padding: 0.25rem 0 0.75rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            👥 Enrolled Student Roster
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem;">
            View and manage students enrolled in your academic cohort.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        students = get_scoped_students(db, current_user)
        org_name = current_user.organization.name if (current_user and current_user.organization) else "All Organizations (Global Admin)"

        st.caption(f"🏫 Organization Scope: **{org_name}** | Total Active Records: **{len(students)}**")

        # Quick Org Admin Action: Add New Student
        if current_user and current_user.role in ["ORG_ADMIN", "SYSTEM_ADMIN"]:
            with st.expander("➕ Register New Student to Roster", expanded=False):
                with st.form("add_student_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_id = st.text_input("Student Identifier (Roll No / ID)*", placeholder="e.g. STU-2026-089")
                        new_name = st.text_input("Student Full Name*", placeholder="e.g. Jordan Miller")
                    with c2:
                        new_course = st.selectbox("Course / Program", ["Computer Science & AI", "Data Science", "Software Engineering", "Information Systems"])
                        new_sem = st.number_input("Semester", min_value=1, max_value=8, value=3)

                    submitted = st.form_submit_button("Save Student to Roster", type="primary")
                    if submitted:
                        if not new_id.strip() or not new_name.strip():
                            st.error("Please provide both Student Identifier and Full Name.")
                        else:
                            existing = db.query(Student).filter(Student.student_identifier == new_id.strip()).first()
                            if existing:
                                st.error(f"Student with identifier '{new_id}' already exists.")
                            else:
                                new_stu = Student(
                                    student_identifier=new_id.strip(),
                                    name=new_name.strip(),
                                    course=new_course,
                                    semester=int(new_sem),
                                    organization_id=current_user.organization_id,
                                    created_by_user_id=current_user.id,
                                    created_at=datetime.utcnow()
                                )
                                db.add(new_stu)
                                db.commit()
                                log_audit_event(db, current_user.id, current_user.username, "STUDENT_CREATED", "STUDENT", f"Added {new_id}")
                                st.success(f"✅ Successfully registered {new_name} ({new_id})!")
                                st.rerun()

        if not students:
            st.info("No student records found in your organization yet. Use the form above to add students or conduct an assessment.")
            return

        # Prepare Student Table Data
        records = []
        for s in students:
            # Query latest prediction
            latest_pred = db.query(Prediction).filter(
                (Prediction.student_id == s.id) | (Prediction.student_identifier == s.student_identifier)
            ).order_by(Prediction.prediction_timestamp.desc()).first()

            tier_badge = latest_pred.risk_tier if latest_pred else "Not Assessed"
            prob_str = f"{latest_pred.probability:.1%}" if latest_pred else "—"
            last_date = latest_pred.prediction_timestamp.strftime("%Y-%m-%d") if latest_pred else "—"

            records.append({
                "ID": s.student_identifier,
                "Name": s.name,
                "Course": s.course,
                "Semester": f"Sem {s.semester}",
                "Academic Standing": tier_badge,
                "Predicted Risk": prob_str,
                "Last Assessed": last_date,
            })

        df_display = pd.DataFrame(records)

        # Filters
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            search_query = st.text_input("🔍 Search by student name or ID", placeholder="Type to filter...")
        with f_col2:
            tier_filter = st.selectbox("Filter by Standing", ["All Standings", "HIGH", "MODERATE", "LOW", "Not Assessed"])

        filtered_df = df_display.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["Name"].str.lower().str.contains(q) | 
                filtered_df["ID"].str.lower().str.contains(q)
            ]
        if tier_filter != "All Standings":
            filtered_df = filtered_df[filtered_df["Academic Standing"] == tier_filter]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-left: 5px solid {COLOR_ACCENT_TEAL}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-top: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <h3 style="color: {COLOR_TEXT_PRIMARY}; margin: 0 0 0.25rem 0; font-size: 1.2rem;">⚡ Quick Assessment Launcher</h3>
            <p style="color: {COLOR_TEXT_SECONDARY}; margin: 0 0 0.75rem 0; font-size: 0.95rem;">Select an enrolled student to automatically load their profile into the Risk Assessment engine.</p>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([2.5, 1.2])
        with col_act1:
            selected_stu_id = st.selectbox(
                "Choose a student from roster to evaluate:",
                [s.student_identifier for s in students],
                format_func=lambda x: f"{x} — {next((s.name for s in students if s.student_identifier == x), '')}",
                key="roster_student_quick_select"
            )
        with col_act2:
            st.markdown("<div style='padding-top: 1.7rem;'>", unsafe_allow_html=True)
            if st.button("🚀 Launch Assessment", type="primary", use_container_width=True, key="launch_roster_assessment_btn"):
                target_stu = next((s for s in students if s.student_identifier == selected_stu_id), None)
                if target_stu:
                    st.session_state.selected_student_for_assessment = {
                        "student_id": target_stu.student_identifier,
                        "student_name": target_stu.name
                    }
                st.session_state.current_page = "🎯 Student Risk Assessment"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    finally:
        db.close()
