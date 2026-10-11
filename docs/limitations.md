# Research Limitations & Ethical Governance

## 1. Methodological Limitations
1. **Augmented Feature Derivation**: While `attendance_rate`, `internal_test_score`, and `study_hours` were systematically mapped from the real Portuguese cohort's recorded variables (`absences`, `G1/G2`, `studytime`), the `assignment_submission_frequency` indicator was incorporated as an educational proxy variable to demonstrate the four-indicator methodology. Experimental metrics reflect this dataset composition.
2. **Attribution vs. Causality**: SHAP attributions characterize how input features shifted the mathematical model output. They do not prove causal relationships. Remediating a flagged risk indicator (e.g. compelling attendance) does not guarantee improved conceptual mastery.
3. **Threshold Calibration**: Operational risk-tier cut-offs ($P \ge 0.66$ for HIGH, $0.33 \le P < 0.66$ for MODERATE) and intervention trigger rules are design defaults. They require institutional calibration and domain validation prior to clinical educational deployment.
4. **Generalisability Across Academic Domains**: The models were trained and benchmarked on secondary school cohorts in Portugal. Transferability to higher education, engineering programs, or varied cultural contexts requires domain-specific re-training.

---

## 2. Technical & Architectural Boundaries
1. **Discrete Temporal Snapshots**: Longitudinal tracking logs temporal evaluation snapshots in SQLite. It does not employ deep spatio-temporal architectures (such as Graph Neural Networks or LSTMs), reflecting intentional design prioritization of lightweight CPU execution.
2. **Absence of Live LMS Synchronization**: The prototype ingests data via validated CSV imports and database tables. Direct live OAuth API connectivity to learning management systems (e.g. Canvas, Moodle) remains a designated future extension.
3. **Absence of Clinical Multi-Year Efficacy Studies**: Intervention tracking logs educator status updates (`Pending`, `In Progress`, `Completed`, `Dismissed`). The prototype does not claim empirical proof of pedagogical efficacy, as formal multi-semester controlled user studies have not yet been conducted.

---

## 3. Privacy, Security & Responsible AI
1. **Research Prototype Scope**: EduRisk XAI is a research demonstration prototype and is not certified for direct enterprise student data handling.
2. **Ethical Use Requirement**: Model outputs must be employed strictly for supportive, formative academic advising. They must **never** be used for punitive academic actions, automated disciplinary penalties, or admissions screening.
3. **Human-in-the-Loop Mandate**: Recommendations must be reviewed and validated by qualified faculty advisors exercising professional pedagogical judgment.
