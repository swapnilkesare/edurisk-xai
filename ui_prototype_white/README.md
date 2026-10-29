# EduRisk XAI — White UI Prototype with Anime.js

An interactive, modern, and accessible **White Theme UI Prototype** designed for the **EduRisk XAI** student academic risk assessment and decision support platform.

Built using **HTML5, CSS3, Vanilla JavaScript, and Anime.js (v3.2.2)**.

---

## 🔒 Project Preservation Guarantee (Zero Changes to Existing Files)

**This prototype was constructed strictly inside this isolated directory (`ui_prototype_white/`).**

- **0 pre-existing files modified, renamed, or deleted.**
- Existing Streamlit application (`app.py`, `app_pages/`, `config/`) remains 100% untouched.
- Existing Python environments, dependencies, and `requirements.txt` remain untouched.
- Existing SQLite databases (`database/edurisk.db`), models (`models/artifacts/`), and figures remain completely unaltered.
- This prototype does **not** write to or read from the production database.

---

## 🎨 Color Palette & Design System

The white theme interface adheres to the following design tokens:

| Token Name | Hex Code | UI Usage |
|---|---|---|
| **Main Background** | `#F8FAFC` | App body background |
| **Card Background** | `#FFFFFF` | Primary cards, modals, table surfaces |
| **Primary Teal** | `#0F9F95` | Primary buttons, active nav indicators, brand accent |
| **Primary Button Text** | `#FFFFFF` | Text inside primary action buttons |
| **Main Heading** | `#172033` | Primary page headers and card titles |
| **Body Text** | `#475569` | High-contrast standard body copy |
| **Secondary Text** | `#64748B` | Subtitles, labels, and secondary metadata |
| **Borders** | `#E2E8F0` | Card borders, dividers, and table cell lines |
| **Light Teal Surface** | `#E8F8F6` | Active tab highlights, badge surfaces, alert boxes |
| **Accent Violet** | `#7966D8` | Secondary badges and analytical accents |
| **Warning (Moderate Risk)** | `#D97706` | Borderline risk badge and alerts (`#FEF3C7` surface) |
| **High Risk Indicator** | `#DC2626` | High-risk alerts and error boundaries (`#FEE2E2` surface) |
| **Low Risk Indicator** | `#15803D` | Safe status badges and protective attributions (`#DCFCE7` surface) |

---

## 📂 Prototype Directory Structure

```text
ui_prototype_white/
├── index.html           # Semantic HTML5 single-page application structure
├── styles.css           # Complete light design system, accessible tokens, responsive & print media
├── main.js              # SPA router, form validation, filter/sort engine, modal controller
├── animations.js        # Dedicated Anime.js animation manager (with reduced-motion safeguards)
├── data.js              # Explicitly fictional demonstration datasets (students, benchmarks, rules)
├── vendor/
│   └── anime.min.js     # Vendored Anime.js v3.2.2 library (100% offline standalone capability)
├── package.json         # Standalone package manifest with npm start scripts
└── README.md            # Architecture, validation report, and run instructions
```

---

## ✨ Anime.js Animation Implementation

All animations are purposeful, lightweight (150–350ms), and mathematically restrained to maintain professionalism:

1. **Page Transitions**: Smooth fade-in (`opacity: [0, 1]`) with subtle upward motion (`translateY: [8, 0]`, 220ms, `easeOutQuad`).
2. **Dashboard Stagger**: Summary metric cards and list rows cascade gently into view (`anime.stagger(50ms)`).
3. **Animated Metric Counters**: Eased numeric count-up from `0` to target values on dashboard initialization (`easeOutCubic`, 650ms).
4. **Interactive Stepper Progress**: Form progress bar width eases smoothly between steps (`320ms, easeOutQuad`).
5. **Form Step Slide**: Horizontal slide-and-fade transition between assessment sections (`160ms -> 200ms`).
6. **Modal Overlays**: Backdrop fade (`160ms`) paired with a spring scale pop-in (`scale: [0.94, 1.0]`, 220ms).
7. **Notification Toasts**: Slide-in from top right with auto-dismiss exit animation.
8. **Reduced Motion Accessibility**: Full `@media (prefers-reduced-motion: reduce)` support instantly bypasses transitions and animations when requested by the operating system or user agent.

---

## 🚀 How to Run the Prototype Locally

This prototype requires no external package installations or cloud dependencies. You can serve it using any standard local web server.

### Option A: Using Python Built-in HTTP Server (Recommended)
From the project workspace root:
```bash
python -m http.server 3000 --directory ui_prototype_white
```
Then open your web browser at:
```
http://localhost:3000
```

### Option B: Using Node / npx
```bash
cd ui_prototype_white
npm start
```
or:
```bash
npx -y serve ui_prototype_white -p 3000
```

### Option C: Direct Browser Opening
Simply double-click or open `ui_prototype_white/index.html` directly in any modern browser (Chrome, Edge, Firefox, Safari). The vendored Anime.js file in `vendor/anime.min.js` ensures that all scripts and styles work completely offline without internet connectivity.

---

## 🧭 Implemented Interactive Features

- **Horizontal Top Navigation**:
  - Logo with school affiliation pill badge.
  - Active tab highlighting with light teal surface, dark teal font, and animated indicator bar.
  - Role switcher dropdown: Toggle between **Educator**, **Org Admin**, and **Researcher** (demonstration).
  - Mobile hamburger toggle menu for responsive viewing.
- **Teacher Dashboard**:
  - Greeting and context hero banner with immediate "Assess Student Risk" and "Review Priority Cohort" quick buttons.
  - 4 key summary cards with animated numeric counters (Total Monitored, Requiring Attention, Completed, Follow-ups Pending).
  - Cohort Risk Distribution SVG Donut Chart with accessible text center and legend.
  - Longitudinal Monthly Progress Chart (Oct–Feb) tracking risk progression.
  - Recent activity table with live search, risk-tier filtering pills, and column sorting.
- **Interactive Multi-Step Assessment Wizard**:
  - **Step 1**: Student reference, alias, cohort level, and academic track.
  - **Step 2**: Formative test score (interactive slider), assignment frequency slider, and prior grade.
  - **Step 3**: Cumulative attendance slider, weekly study hours slider, and support options.
  - **Step 4**: Structured summary review table before submission.
  - Client-side validation with visible inline error messages and `aria-invalid` tags.
  - Accessible tooltips `(?)` explaining research rationale for each indicator.
  - Simulated outcome card displaying transparent risk tier badge, risk-increasing vs protective factor attribution decomposition, and recommended pedagogical actions.
- **Student Cohort Directory**:
  - Full searchable student table with live filtering by risk tier.
  - "Details" button opens an interactive modal with full academic breakdown, case notes, and editable intervention status toggles (`Pending`, `In Progress`, `Completed`).
- **Institutional Reports & Exports**:
  - Executive synthesis banner.
  - Pedagogical action resolution statistics.
  - "Download Demo CSV" button generating and saving client-side CSV on the fly.
  - "Print / Save PDF" triggering print-optimized stylesheet.
- **Research & Admin Tools**:
  - Literature benchmark comparison table displaying empirical UCI cohort results across all 4 classifiers (Random Forest, Decision Tree, SVC, Logistic Regression).
  - Deterministic intervention rules table displaying trigger conditions, priority, and assigned stakeholders.

---

## 🛡️ Demonstration Data & Ethical Boundaries

- **Fictional Data Only**: All student names (e.g. Marcus Brody, Sofia Rodriguez), IDs (`STU-2026-xxx`), scores, and notes are fictitious demonstration samples.
- **No Fabricated Machine Learning**: The assessment form explicitly labels simulated outcomes as a prototype demonstration. It does not fabricate live model predictions or pretend to execute backend pipelines.
- **Human Oversight**: In alignment with EduRisk’s research principles, risk tiers provide advisory screening for educational mentors and must never be used for punitive measures.
