"""
Page: Students Management & Scoped Roster View
Provides persistent, one-time student registration using Permanent Roll Number (PRN)
as the unique identifier, deduplication, academic placement history, and targeted assessment dispatch.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config.theme import (
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_TEAL_SURFACE,
    COLOR_ACCENT_VIOLET,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE,
    COLOR_RISK_HIGH,
    COLOR_RISK_HIGH_SURFACE,
    COLOR_RISK_MODERATE,
    COLOR_RISK_MODERATE_SURFACE,
    COLOR_RISK_LOW,
    COLOR_RISK_LOW_SURFACE
)
from database.database import SessionLocal
from database.models import Student, Prediction
from database.crud import (
    normalize_prn,
    validate_prn,
    get_student_by_prn,
    register_student_prn,
    update_student_academic_placement
)
from services.auth_service import get_scoped_students, log_audit_event

def render_students(current_user=None):
    st.markdown(f"""
    <div style="padding: 0.25rem 0 0.75rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            👥 Enrolled Student Directory & PRN Registration
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem; margin: 0;">
            Register students once using their Permanent Roll Number (PRN) and track longitudinal academic assessments.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        org_id = current_user.organization_id if current_user else None
        org_name = current_user.organization.name if (current_user and current_user.organization) else "Global Academic System"
        user_id = current_user.id if current_user else None

        st.caption(f"🏫 Active Institution: **{org_name}** | Logged-in Educator: **{current_user.full_name if current_user else 'Guest'}**")

        # ====================================================================
        # 1. ONE-TIME PRN STUDENT REGISTRATION WORKFLOW
        # ====================================================================
        with st.expander("📝 Register New Student (One-Time PRN Onboarding)", expanded=False):
            st.markdown(f"""
            <div style="background-color: {COLOR_BG_SECONDARY}; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 0.85rem 1.15rem; margin-bottom: 1rem;">
                <strong style="color: {COLOR_ACCENT_TEAL}; font-size: 0.92rem;">📌 Permanent Roll Number (PRN) Policy:</strong>
                <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.86rem; margin-bottom: 0; line-height: 1.45;">
                    The PRN serves as the student's permanent, unique identifier throughout their academic tenure. 
                    Registering a student once allows all future longitudinal risk predictions and interventions to link automatically.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Step A: PRN Search & Live Verification
            col_search_prn, col_verify_btn = st.columns([3, 1])
            with col_search_prn:
                input_prn = st.text_input(
                    "Enter Permanent Roll Number (PRN)*",
                    placeholder="e.g. PRN-2024-0042",
                    help="Institutional roll number or registration code. Whitespace is trimmed and case normalized."
                )
            with col_verify_btn:
                st.markdown("<div style='padding-top: 1.8rem;'>", unsafe_allow_html=True)
                check_clicked = st.button("🔍 Verify PRN", use_container_width=True, key="btn_verify_prn_lookup")
                st.markdown("</div>", unsafe_allow_html=True)

            # Check if user entered a PRN or clicked verify
            norm_prn = normalize_prn(input_prn) if input_prn else ""

            if norm_prn:
                is_valid_format, format_err = validate_prn(norm_prn)
                if not is_valid_format:
                    st.warning(f"⚠️ {format_err}")
                else:
                    existing_student = get_student_by_prn(db, norm_prn, organization_id=org_id)
                    if existing_student:
                        st.markdown(f"""
                        <div style="background-color: {COLOR_ACCENT_TEAL_SURFACE}; border: 1px solid {COLOR_ACCENT_TEAL}; border-radius: 8px; padding: 1rem 1.25rem; margin-top: 0.75rem;">
                            <strong style="color: {COLOR_ACCENT_TEAL}; font-size: 1rem;">✅ Existing Student Record Found:</strong><br>
                            <span style="color: {COLOR_TEXT_PRIMARY}; font-size: 0.95rem;">
                                <strong>{existing_student.name}</strong> • PRN: <code>{existing_student.prn or existing_student.student_identifier}</code> • 
                                {existing_student.course} ({existing_student.department}) • Semester {existing_student.semester} (Division {existing_student.division or 'A'})
                            </span>
                            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.85rem; margin: 0.4rem 0 0 0;">
                                This student is already registered in your institution. You do not need to register them again.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        col_launch_exist, col_update_exist = st.columns([1.5, 1])
                        with col_launch_exist:
                            st.markdown("<div style='padding-top: 0.5rem;'>", unsafe_allow_html=True)
                            if st.button(f"🎯 Begin Risk Assessment for {existing_student.name}", type="primary", use_container_width=True, key="launch_from_lookup_btn"):
                                st.session_state.selected_student_for_assessment = {
                                    "student_id": existing_student.prn or existing_student.student_identifier,
                                    "student_name": existing_student.name,
                                    "course": existing_student.course,
                                    "semester": existing_student.semester
                                }
                                st.session_state.current_page = "🎯 Student Risk Assessment"
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

                        with col_update_exist:
                            with st.expander("✏️ Update Academic Placement (Semester / Division)", expanded=False):
                                with st.form("update_placement_form"):
                                    up_sem = st.number_input("New Semester", min_value=1, max_value=8, value=int(existing_student.semester or 3))
                                    up_div = st.text_input("New Division / Section", value=existing_student.division or "A")
                                    up_note = st.text_input("Reason / Note", placeholder="e.g. Promoted to Term 2")
                                    if st.form_submit_button("Update Placement", type="secondary"):
                                        update_student_academic_placement(
                                            db, 
                                            existing_student.id, 
                                            new_semester=up_sem, 
                                            new_division=up_div, 
                                            note=up_note
                                        )
                                        log_audit_event(db, user_id, current_user.username if current_user else "educator", "STUDENT_UPDATED", "STUDENT", f"Updated placement for {existing_student.prn}")
                                        st.success("✅ Academic placement updated!")
                                        st.rerun()
                    else:
                        # New PRN: Display One-Time Registration Form
                        st.info(f"✨ PRN `'{norm_prn}'` is available. Complete the form below to register this student:")
                        with st.form("prn_registration_form", clear_on_submit=False):
                            rc1, rc2 = st.columns(2)
                            with rc1:
                                reg_prn = st.text_input("Permanent Roll Number (Normalized)", value=norm_prn, disabled=True)
                                reg_name = st.text_input("Student Full Name*", placeholder="e.g. Sarah Jenkins")
                                reg_dept = st.selectbox("Academic Department", ["Engineering & Technology", "Computer Applications", "Applied Sciences", "Business & Economics"])
                                reg_course = st.selectbox("Program / Degree Track", ["Computer Science & AI", "Data Science & Analytics", "Information Technology", "Electronics Engineering", "Software Systems"])
                            with rc2:
                                reg_batch = st.text_input("Admission Batch / Academic Cycle", value="2024–2028")
                                reg_sem = st.number_input("Current Semester / Term", min_value=1, max_value=8, value=3)
                                reg_div = st.selectbox("Division / Section", ["A", "B", "C", "D"], index=0)
                                reg_email = st.text_input("Institutional Email (Optional)", placeholder="e.g. s.jenkins@horizon.edu")

                            reg_submit = st.form_submit_button("💾 Complete Student Registration", type="primary", use_container_width=True)

                            if reg_submit:
                                if not reg_name.strip():
                                    st.error("Student Full Name is required.")
                                else:
                                    stu, is_new, msg = register_student_prn(
                                        db=db,
                                        prn=norm_prn,
                                        name=reg_name.strip(),
                                        course=reg_course,
                                        department=reg_dept,
                                        semester=int(reg_sem),
                                        year=max(1, (int(reg_sem) + 1) // 2),
                                        batch_year=reg_batch,
                                        division=reg_div,
                                        email=reg_email,
                                        organization_id=org_id,
                                        created_by_user_id=user_id
                                    )
                                    if is_new and stu:
                                        log_audit_event(db, user_id, current_user.username if current_user else "educator", "STUDENT_REGISTERED", "STUDENT", f"Registered PRN {stu.prn}")
                                        st.success(f"🎉 {msg}")
                                        st.session_state.selected_student_for_assessment = {
                                            "student_id": stu.prn,
                                            "student_name": stu.name,
                                            "course": stu.course,
                                            "semester": stu.semester
                                        }
                                        st.rerun()
                                    else:
                                        st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)

        # ====================================================================
        # 2. ENROLLED STUDENT ROSTER TABLE & FILTERS
        # ====================================================================
        students = get_scoped_students(db, current_user)
        if not students:
            st.info("No enrolled students found in your organization. Use the registration form above to onboard your first student.")
            return

        records = []
        for s in students:
            # Query latest assessment
            latest_pred = db.query(Prediction).filter(
                (Prediction.student_id == s.id) | 
                (Prediction.student_identifier == s.student_identifier) |
                (Prediction.student_identifier == s.prn)
            ).order_by(Prediction.prediction_timestamp.desc()).first()

            tier_badge = latest_pred.risk_tier if latest_pred else "Not Assessed"
            prob_str = f"{latest_pred.probability:.1%}" if latest_pred else "—"
            last_date = latest_pred.prediction_timestamp.strftime("%Y-%m-%d") if latest_pred else "—"
            display_prn = s.prn or s.student_identifier

            records.append({
                "PRN": display_prn,
                "Student Name": s.name,
                "Course & Program": s.course or "General Studies",
                "Placement": f"Sem {s.semester} (Div {s.division or 'A'})",
                "Batch": s.batch_year or "2024–2028",
                "Academic Standing": tier_badge,
                "Predicted Risk": prob_str,
                "Last Assessed": last_date,
            })

        df_display = pd.DataFrame(records)

        # Table Filter Controls
        f_col1, f_col2, f_col3 = st.columns([2.5, 1.2, 1.2])
        with f_col1:
            search_query = st.text_input("🔍 Search by PRN, student name, or program...", placeholder="Type to filter...")
        with f_col2:
            tier_filter = st.selectbox("Academic Standing", ["All Standings", "HIGH", "MODERATE", "LOW", "Not Assessed"])
        with f_col3:
            sem_filter = st.selectbox("Semester Filter", ["All Semesters", "Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"])

        filtered_df = df_display.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["Student Name"].str.lower().str.contains(q) | 
                filtered_df["PRN"].str.lower().str.contains(q) |
                filtered_df["Course & Program"].str.lower().str.contains(q)
            ]
        if tier_filter != "All Standings":
            filtered_df = filtered_df[filtered_df["Academic Standing"] == tier_filter]
        if sem_filter != "All Semesters":
            filtered_df = filtered_df[filtered_df["Placement"].str.contains(sem_filter)]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ====================================================================
        # 3. QUICK ASSESSMENT LAUNCHER
        # ====================================================================
        st.markdown(f"""
        <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-left: 5px solid {COLOR_ACCENT_TEAL}; border-radius: 12px; padding: 1.25rem 1.5rem; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
            <h3 style="color: {COLOR_TEXT_PRIMARY}; margin: 0 0 0.25rem 0; font-size: 1.2rem;">⚡ Quick Assessment Dispatcher</h3>
            <p style="color: {COLOR_TEXT_SECONDARY}; margin: 0 0 0.75rem 0; font-size: 0.95rem;">
                Select an enrolled student to automatically load their registered PRN and academic profile into the Risk Assessment engine.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([2.5, 1.2])
        with col_act1:
            student_prn_list = [s.prn or s.student_identifier for s in students]
            selected_stu_prn = st.selectbox(
                "Choose a registered student by PRN:",
                student_prn_list,
                format_func=lambda x: f"{x} — {next((s.name for s in students if (s.prn == x or s.student_identifier == x)), '')}",
                key="roster_student_quick_select"
            )
        with col_act2:
            st.markdown("<div style='padding-top: 1.7rem;'>", unsafe_allow_html=True)
            if st.button("🚀 Launch Risk Assessment", type="primary", use_container_width=True, key="launch_roster_assessment_btn"):
                target_stu = next((s for s in students if (s.prn == selected_stu_prn or s.student_identifier == selected_stu_prn)), None)
                if target_stu:
                    st.session_state.selected_student_for_assessment = {
                        "student_id": target_stu.prn or target_stu.student_identifier,
                        "student_name": target_stu.name,
                        "course": target_stu.course,
                        "semester": target_stu.semester
                    }
                st.session_state.current_page = "🎯 Student Risk Assessment"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    finally:
        db.close()
