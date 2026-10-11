# EduRisk XAI — Full Project Audit and Architecture Repair Plan

**Project:** EduRisk (Student Academic Risk Assessment & Decision Support System)  
**Date:** October 11, 2026  
**Document:** `docs/project_audit_and_repair_plan.md`  
**Status:** Pre-implementation Audit & Specification

---

## 1. Executive Summary & Audit Overview

This audit comprehensively evaluates the existing **EduRisk XAI** application running locally at `http://localhost:8501/`. The platform's machine learning, SHAP explainability, and deterministic intervention rules are technically sound and empirically verified (all 26 automated unit and integration tests passing). However, significant usability, navigation, and user-experience limitations have emerged:

1. **Navigation Instability:** Transitioning between Home and Student Risk Assessment suffers from state desynchronization between widget keys, programmatically set session variables, and subpage action buttons.
2. **Left Sidebar Clutter:** Primary navigation is trapped in the left sidebar, which collapses on smaller screens and confuses teachers who expect a clean, standard horizontal top navigation bar.
3. **Dark-Mode Invisibility:** Brand titles, headings, and card containers use hardcoded dark colors (e.g. `#1e293b`, `#334155`) without explicit background/foreground themes, rendering text virtually invisible when a user's operating system or browser runs in Dark Mode.
4. **Absence of Role-Based Security:** The current application has no authentication, database user entities, organization tenancy, or role separation. All pages and administrator tools are accessible without access controls.

This document records the exact findings from the codebase audit and provides the architectural plan to fix these issues without altering or degrading the underlying machine-learning models, training pipelines, or research outputs.

---

## 2. Complete Project Structure & Baseline Verification

### 2.1 Workspace Inventory
```text
edurisk-xai/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py                      # Main Streamlit application & routing entry point
├── app_pages/                  # Modular view renderers
│   ├── dashboard.py            # Home / Overview view
│   ├── predict_student.py      # Student Risk Assessment view
│   ├── analytics.py            # Cohort Analytics
│   ├── data_import.py          # CSV Data Management
│   ├── model_training.py       # Candidate Model Training
│   ├── model_comparison.py     # Cross-Validation & Test Benchmarking
│   ├── explainability.py       # Local & Global SHAP Analysis
│   ├── interventions.py        # Intervention Rule Configuration
│   └── research_traceability.py# Academic Traceability Matrix
├── config/
│   └── settings.py             # Feature definitions, paths, thresholds
├── data/
│   ├── raw/student_data.csv    # UCI Student Performance baseline dataset
│   └── student_academic_risk_data.csv
├── database/
│   ├── database.py             # SQLAlchemy engine & SessionLocal
│   ├── models.py               # ORM Entities (Student, Prediction, Intervention, Rule)
│   ├── crud.py                 # Persistence helper functions
│   └── edurisk.db              # SQLite persistent database
├── docs/                       # Research documentation and methodology reports
├── models/
│   ├── artifacts/              # best_model.pkl & model_metadata.json
│   └── versions/               # Timestamped historical pipeline checkpoints
├── results/
│   ├── experiments/            # JSON records of benchmark runs
│   ├── figures/                # Publication-quality PNG visualizations
│   └── reports/                # Markdown experiment summaries
├── services/
│   ├── prediction_service.py   # Prediction & SHAP coordination
│   ├── training_service.py     # Model training & selection pipeline
│   ├── import_service.py       # Dataset upload & schema validation
│   └── report_service.py       # Report & figure generation
├── src/                        # Core algorithmic ML modules
└── tests/                      # Automated unit, integration & runtime tests
```

### 2.2 Version Control & Safety State
- **Git State:** A clean baseline commit has been initialized at commit `3722113` ("Baseline before navigation repair, UI redesign, and role-based access").
- **Backup Archive:** Pre-simplification archive is preserved in `_quarantine_legacy_backup/pre_simplification_backup/`.
- **Test Baseline:** 26/26 tests passing in `pytest tests -v` (runtime: ~29 seconds).

---

## 3. Navigation Failure Root-Cause Analysis

### 3.1 Failure Mode A: Returning to Home Fails or Locks User
* **Observed Symptom:** A teacher on the "Student Risk Assessment" page clicks "Home" or an on-screen "Return to Home" button, but the screen remains on the assessment view or re-renders the previous assessment results.
* **Root Cause 1 — Sidebar Widget Key Stale Restoration:** In Streamlit, when an `st.radio` or `st.selectbox` is given a widget `key` (e.g., `key="teacher_nav_radio"`), Streamlit caches its state in `st.session_state["teacher_nav_radio"]`. If a page button programmatically changes `st.session_state.teacher_nav = "🏠 Home"` and triggers `st.rerun()`, on the subsequent execution Streamlit restores the widget value from the cached widget key rather than the programmatic variable, restoring `"🎯 Predict Student Risk"` and overwriting `teacher_nav`.
* **Root Cause 2 — Competing Admin Dropdown Precedence:** In `app.py`, line 141 evaluates:
  ```python
  if admin_choice != "None (Teacher Mode)":
      # renders admin view
  else:
      # renders teacher view (Home, Predict, Results)
  ```
  If a user navigated to any Research/Admin tool, `admin_tool_selector` retains that value. Any subsequent click on "Home" in the primary navigation is ignored because the admin router evaluates first and overrides the teacher navigation state.
* **Root Cause 3 — Sidebar Collapse on Laptops/Tablets:** On common laptop screens and narrower browser windows, Streamlit automatically collapses the left sidebar into a hamburger menu. Teachers navigating the central content area lose visibility of the navigation entirely and have no obvious top bar to return Home.

### 3.2 Failure Mode B: Navigation After Assessment Form Submission
* **Observed Symptom:** After entering student indicators and clicking "Predict Student Risk", the assessment result is displayed. If the teacher subsequently clicks another navigation item, the form state re-executes or the assessment view persists.
* **Root Cause:** In `app_pages/predict_student.py`, lines 210–213 store `st.session_state.current_prediction = result` and call `st.rerun()`. Because the assessment view renders both the input form and the results in the same view conditionally based on `has_active_prediction`, navigation state was entangled with result persistence.

---

## 4. Visual Theme, Branding & Dark-Mode Audit

### 4.1 Contrast & Readability Breakdown
* **Brand Header:** In `app.py`, the sidebar branding was rendered as:
  ```html
  <h2 style="margin: 0; color: #1e293b; font-size: 1.5rem;">🎓 EduRisk</h2>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Student Risk Assessment</p>
  ```
  `#1e293b` is dark charcoal. In OS/browser Dark Mode, Streamlit's default dark canvas is `#0e1117`. A dark charcoal header on a dark charcoal canvas has a contrast ratio under **1.4:1**, violating WCAG 2.1 AA accessibility guidelines (minimum 4.5:1 required).
* **Card Containers:** Hero banners and step cards in `app_pages/dashboard.py` hardcode light pastel backgrounds:
  ```html
  <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border: 1px solid #bae6fd; ...">
  ```
  In Dark Mode, Streamlit sets default body text to near-white. If an element inherits or mixes light text onto a light container, contrast drops to illegible levels.
* **Absence of `.streamlit/config.toml`:** The application lacked an explicit theme configuration file, leaving color rendering subject to arbitrary browser user-agent defaults.

### 4.2 Solution Strategy
- Create `.streamlit/config.toml` defining explicit, high-contrast, theme-agnostic design tokens.
- Implement CSS variables and clean theme classes supporting both light and dark environments with guaranteed minimum 4.5:1 contrast ratios.
- Replace fragile inline color styles with semantic design tokens (`--text-primary`, `--bg-card`, `--border-subtle`, `--brand-primary`).

---

## 5. Security, Tenancy & Authentication Audit

### 5.1 Existing State
* **User Accounts:** 0 (None exist in `database/models.py`).
* **Organization Multi-Tenancy:** 0 (No `organization_id` on any database table).
* **Access Control:** All administrative, model training, and database features are open to anyone accessing `http://localhost:8501/`.
* **Password Hashing:** No authentication libraries currently integrated.

### 5.2 Environment Capability Verification
* Verified installed Python security modules:
  - `hashlib` (Available): Provides `hashlib.pbkdf2_hmac` with SHA-256 (NIST recommended, 200,000+ iterations).
  - `secrets` (Available): Cryptographically secure random tokens and salts.
  - `cryptography` (Available): AES/Fernet encryption if needed for secrets.
* Conclusion: We can implement **production-grade, zero-dependency PBKDF2-SHA256 password hashing** directly through Python's standard library without requiring unpinned external packages like `passlib` or `bcrypt`.

---

## 6. Target Architecture & Implementation Plan

### 6.1 Phase 2 — Horizontal Top Navigation Bar
Replace the left sidebar navigation with a responsive, modern horizontal navigation bar at the top of the viewport:
- **Brand / Logo:** `🎓 EduRisk` with clear badge.
- **Top Navigation Items:**
  1. `🏠 Home`
  2. `🎯 Student Risk Assessment`
  3. `👥 Students`
  4. `📊 Reports`
  5. `🛠️ Research & Admin Tools` *(Visible and accessible ONLY to authorized administrators/researchers)*
- **User / Account Menu:** Right-aligned status indicator showing logged-in user, role badge, organization name, and a secure Logout button.
- **Routing Engine:** A single, centralized `st.session_state.current_page` dispatcher with no competing sidebar radios.

### 6.2 Phase 3 — Theme & Visual Branding
- Create `.streamlit/config.toml` with explicit palette.
- Implement responsive, accessible typography and high-contrast styling for Dark and Light modes.

### 6.3 Phase 4 — Simplified Teacher Experience
- Streamlined 4-step workflow: Select/Enter Student $\rightarrow$ Assess $\rightarrow$ Plain-language Risk Overview $\rightarrow$ Practical Pedagogical Interventions.
- Avoid technical AI terminology on teacher pages; maintain detailed SHAP plots and model metrics strictly in the Research & Admin area.

### 6.4 Phase 5 — Secure Role-Based Access Control (RBAC)
- Add database models:
  - `User`: `id`, `username`, `email`, `password_hash`, `salt`, `role` (`TEACHER`, `ORG_ADMIN`, `SYSTEM_ADMIN`), `organization_id`, `is_active`, `created_at`.
  - `Organization`: `id`, `name`, `code`, `created_at`.
  - `AuditLog`: `id`, `user_id`, `action`, `resource`, `details`, `timestamp`, `ip_address`.
- Implement PBKDF2-SHA256 password hashing with unique per-user 32-byte salts and 200,000 iterations.
- Implement server-side role enforcement on every view. If a Teacher attempts to view `Research & Admin Tools`, the router halts execution with a 403 Forbidden message.
- Scope student queries: Teachers and Org Admins see only students belonging to their own organization.

### 6.5 Phase 6 — Additional Student Information Roadmap
- Document proposed schema extensions (subject-wise marks, assignment completion rates, attendance trends, LMS participation, student interests).
- Evaluate leakage risks and model training readiness before adding fields to the active pipeline.

### 6.6 Phase 7 — Research Preservation
- Ensure `models/artifacts/best_model.pkl`, `data/student_academic_risk_data.csv`, `results/`, and `tests/` remain 100% functional without data loss or model degradation.

---

## 7. Approval & Next Steps

This document serves as the formal blueprint for the upcoming implementation phases. All subsequent changes will be applied sequentially and verified against the automated test suite.
