# Phase 2 Prototype Limitations

While the Phase-2 Research Demonstration Prototype successfully proves the technical feasibility of the methodology, it is intentionally constrained. The following limitations apply to this specific Phase-2 build and will be addressed in the final production system:

1. **Static Rules Engine**: The `InterventionEngine` uses hardcoded strings. The final system will feature a database-backed rules engine that administrators can modify.
2. **Simplified Features**: To ensure a clear demonstration of the 4 gaps, only 4 core features were mapped (Attendance, Study Hours, Internal Tests, Assignment Submissions). The final system will likely incorporate a broader feature space.
3. **Local Storage**: Data and models are stored locally (`.csv` and `.pkl`). The final system requires a secure cloud database (e.g. PostgreSQL) and artifact registry.
4. **No Authentication**: The Streamlit dashboard is open for demonstration purposes. The final system will implement Role-Based Access Control (RBAC) for Teachers vs Admins.
5. **Causal Fallacy Risk**: SHAP provides *explanations of the model's behavior*, not necessarily real-world causal relationships. The UI attempts to mitigate this by framing them as "Risk Factors", but user-testing is still required to measure educator trust and comprehension.
