"""
Page: Teacher-Friendly Welcome & Overview
Title: EduRisk — Student Academic Risk Assessment
Subtitle: Identify students who may need additional academic support.
"""
import streamlit as st

def render_dashboard(prediction_service=None, training_service=None):
    st.markdown("""
    <div style="padding: 1.5rem 0 1rem 0;">
        <h1 style="color: #1e293b; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.25rem;">
            🎓 EduRisk — Student Academic Risk Assessment
        </h1>
        <p style="color: #475569; font-size: 1.15rem; margin-top: 0;">
            Identify students who may need additional academic support early in the term.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary Hero Container
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); 
                    border: 1px solid #bae6fd; border-radius: 12px; padding: 1.75rem; margin-bottom: 1.5rem;">
            <h3 style="color: #0369a1; margin-top: 0; font-size: 1.3rem;">
                👋 Welcome, Educator
            </h3>
            <p style="color: #334155; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1.25rem;">
                EduRisk is a simple, evidence-based tool designed to help you catch early warning signs of academic difficulty. 
                By reviewing current attendance, assignment patterns, and internal test performance, you can quickly see which 
                students could benefit from timely guidance and explore practical interventions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_btn, col_spacer = st.columns([1, 2])
        with col_btn:
            start_btn = st.button(
                "🚀 Start Student Assessment",
                type="primary",
                use_container_width=True,
                key="home_start_assessment_btn"
            )
            if start_btn:
                st.session_state.teacher_nav = "🎯 Predict Student Risk"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Simple 3-Step Process Cards
    st.markdown("### 📋 How It Works in 3 Simple Steps")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📝</div>
            <h4 style="color: #1e293b; margin-top: 0; margin-bottom: 0.5rem;">1. Enter Details</h4>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                Provide the student's current attendance, test marks, and study habits using an intuitive form.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚡</div>
            <h4 style="color: #1e293b; margin-top: 0; margin-bottom: 0.5rem;">2. Check Predicted Risk</h4>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                Click one button to receive an easy-to-read assessment showing whether additional support is advised.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🤝</div>
            <h4 style="color: #1e293b; margin-top: 0; margin-bottom: 0.5rem;">3. Support Your Student</h4>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                Review the key factors influencing the result and browse actionable, targeted pedagogical recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Reassuring Educator Notice
    st.info(
        "💡 **Supportive Guidance Philosophy**: EduRisk provides early decision support to supplement your professional judgment. "
        "Predictions are indicative estimates of current vulnerability, not permanent labels or limits on student ability."
    )
