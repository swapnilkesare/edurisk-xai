# EduRisk XAI — White UI Audit, Architecture Inspection & PRN Registration Repair Plan

**Project:** EduRisk (Explainable AI in Education)  
**Date:** October 14, 2026  
**Document:** `docs/white_ui_audit_and_prn_repair_plan.md`  
**Status:** Pre-Implementation Comprehensive Audit & Engineering Plan

---

## 1. Executive Summary & Audit Objectives

Following user feedback on the white-theme prototype and application state, this audit addresses five specific system challenges:
1. **Frontend Disconnection:** An isolated frontend prototype was running on `http://localhost:3000/`, while the authentic full-stack application (with SQLite ORM, 4 candidate ML models, SHAP explainability, and RBAC authentication) was running on `http://localhost:8501/`.
2. **Missing Login Gateway:** The prototype at `localhost:3000` omitted the authentication screen, launching directly into a mock dashboard with an unauthenticated client-side role dropdown.
3. **Assessment Layout Compression & Overflow:** The assessment outcome view squeezed multi-indicator explanations, SHAP attributions, and intervention cards into narrow, overflowing grid columns on standard viewports.
4. **Dark vs. White Design Disconnect:** While `ui_prototype_white` used the new white/teal palette, the production Streamlit app (`config/theme.py`) remained hardcoded to matte black (`#0B0D12`).
5. **Absence of Persistent One-Time PRN Registration:** Students were auto-created on the fly during inference with arbitrary string keys, without format validation, institutional uniqueness, or profile/assessment separation.

This plan establishes the engineering steps to repair both surfaces, unify the white theme, restore the authentic login gateway, eliminate layout compression, and implement permanent roll number (PRN) student registration.

---

## 2. Active Frontend & Architecture Inspection

### 2.1 Service Topology
| Endpoint | Technology | State | Scope & Data Connection |
|---|---|---|---|
| `http://localhost:8501/` | Python / Streamlit | Running (Task 64) | **Authentic Production Backend**: SQLite (`edurisk.db`), Scoped RBAC, 4 ML Classifiers, SHAP Explainers, Deterministic Rules. |
| `http://localhost:3000/` | HTML5 / CSS3 / Vanilla JS / Anime.js | Running (Task 102) | **Standalone UI Prototype**: Client-side mock dataset (`data.js`), isolated, offline Anime.js library. |

### 2.2 Root Cause Analysis

#### A. Missing Login Screen
- **In `ui_prototype_white` (`localhost:3000`)**: The initial routing in `main.js` was hardcoded to call `switchView('home')`. The DOM in `index.html` contained no `<section id="view-login">` or credential inputs. Instead, it provided an unauthenticated role `<select>`, violating security and the original user experience.
- **In `edurisk-xai` (`localhost:8501`)**: The login gateway exists in `app.py` lines 91–209, but because `config/theme.py` was styled in matte black, it did not reflect the approved white theme.

#### B. Compressed & Overflowing Assessment Outcome Layout
- In `ui_prototype_white`:
  - `.outcome-grid` was defined as `grid-template-columns: 1fr 1.2fr;` with no `minmax(0, 1fr)`.
  - Nested attribution tracks had fixed heights and non-wrapping flex child items.
  - Action buttons (`#btnExportDemoReport`, `#btnAssessAnother`) sat in a flex-end container that clipped on screens < 1100px.
- In `edurisk-xai` (`predict_student.py`):
  - Streamlit's `st.columns(3)` and `st.columns(2)` divide horizontal space strictly into fixed proportions. On screens < 1280px, factor cards collapsed into unreadable tall vertical strips.
  - Heavy border radiuses and fixed paddings caused text to overflow card boundaries.

#### C. Anime.js & Responsive CSS Dimensions
- `animations.js` used `translateX: [14, 0]` on step panels without `overflow: hidden` on parent containers, triggering horizontal scrollbar flashes during wizard transitions.
- Inline styles applied by Anime.js complete callbacks sometimes conflicted with responsive CSS media queries.

#### D. Database Schema & Student Registration
- `Student` model (`database/models.py` lines 62–80) currently uses `student_identifier = Column(String(64), unique=True)`.
- In `database/crud.py` (`get_or_create_student`), students were created implicitly during predictions if the ID didn't exist.
- No PRN format validation, normalization, or dedicated one-time registration workflow was enforced.

---

## 3. Systematic Repair Plan

### Phase A: Database Schema & PRN Registration Engine
1. **Database Backup**: Create an immediate copy `database/edurisk_backup_pre_prn.db`.
2. **Schema Migration**:
   - Enhance `Student` entity to explicitly support `prn` as the primary institutional roll number.
   - Enforce institutional tenancy: unique constraint on `(organization_id, prn)`.
   - Add institutional fields: `department`, `course`, `semester`, `division`, `admission_year`, `enrollment_status`.
3. **PRN Normalization & Validation**:
   - Whitespace stripping, uppercase conversion, preservation of leading zeros (e.g. `PRN-2024-0012`).
   - Format regex validation: configurable pattern with safe fallback.
4. **CRUD Workflow**:
   - `lookup_student_by_prn(db, prn, organization_id)`
   - `register_student_prn(db, student_data, user_id, organization_id)`
   - Prevent duplicate registration while allowing profile updates through auditable workflows.
   - Link multiple longitudinal assessments to the same student ID.

### Phase B: White Theme Transformation for Authentic Streamlit Application (`edurisk-xai`)
1. **Update `config/theme.py`**:
   - Replace matte black tokens (`#0B0D12`, `#151922`) with authoritative white theme tokens:
     * Background: `#F8FAFC`
     * Card: `#FFFFFF`
     * Primary Teal: `#0F9F95`
     * Text Heading: `#172033`
     * Text Body: `#475569`
     * Secondary Text: `#64748B`
     * Borders: `#E2E8F0`
     * Teal Surface: `#E8F8F6`
     * Violet Accent: `#7966D8`
   - Rewrite `inject_custom_theme()` to enforce crisp white cards, proper text contrast, clean top navigation bar, and visible focus rings.

### Phase C: Uncompressed Assessment Layout (`app_pages/predict_student.py`)
1. **PRN Selection & Verification**:
   - Assessment page starts with PRN lookup. If student exists, load profile and show past history. If not, prompt one-click PRN registration.
2. **Layout Uncompression**:
   - Replace squeezed narrow columns with full-width responsive containers (`min-width: 0`).
   - Prominent Risk Tier Banner across the top with accessible color badges.
   - Eased metric cards with responsive wrapping.
   - Full-width Factor Attribution decomposition with side-by-side or stacked responsive cards.
   - Full-width Pedagogical Support Action cards with clear priority badges.
   - Wrapping action bar for "Assess Another Student", "Print/Export Summary", and "Return to Home".

### Phase D: Roster & PRN Student Registration Management (`app_pages/students.py`)
1. Add dedicated "One-Time PRN Student Registration" interface.
2. Provide live PRN lookup before submission to prevent duplicates.
3. Display enrolled roster with search, filter, PRN, course, semester, and action buttons to launch assessments.

### Phase E: UI Prototype (`ui_prototype_white/` at `localhost:3000`) Alignment
1. Add a genuine Login Gateway screen (`#view-login`) with credentials check, demo account quick logins, and session storage.
2. Refactor `.outcome-grid` in `styles.css` and `main.js` with `min-width: 0`, auto-wrapping, and responsive layout.
3. Implement PRN-based student registration tab in the prototype to match backend behavior.
4. Fix Anime.js container overflow rules to eliminate horizontal scroll flashes.

---

## 4. Verification & Validation Protocol
- Run 37+ automated pytest tests in `edurisk-xai`.
- Verify database migration against backup.
- Test authentication (valid, invalid, logout, RBAC).
- Test PRN registration (valid, duplicate rejection, case normalization, multi-tenancy).
- Test assessment execution and layout at desktop, tablet, and mobile breakpoints.
