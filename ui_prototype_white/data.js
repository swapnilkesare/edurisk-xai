/**
 * EduRisk XAI — Fictional Demonstration Dataset
 * 
 * NOTICE: ALL RECORDS IN THIS FILE ARE EXPLICITLY FICTIONAL DEMONSTRATION SAMPLES.
 * This prototype does NOT read from or write to the project's SQLite database,
 * nor does it contain any real student data or credentials.
 */

window.EduRiskData = {
  isDemoData: true,
  metadata: {
    institution: "Horizon High School",
    academicTerm: "Term 2, Academic Year 2025–2026",
    generatedAt: "2026-10-14",
    leadEducator: "Dr. Elena Vance"
  },

  // Cohort summary statistics (Demo metrics)
  cohortStats: {
    totalStudents: 142,
    highRiskCount: 18,
    moderateRiskCount: 28,
    lowRiskCount: 96,
    assessmentsCompleted: 88,
    assessmentsPending: 54,
    followUpActionsPending: 7,
    activeInterventionsCount: 23,
    avgAttendance: 84.6,
    avgInternalTest: 71.2
  },

  // Longitudinal cohort trend data (Monthly tracking)
  monthlyTrends: [
    { month: "Oct", highRisk: 22, moderateRisk: 31, lowRisk: 89, assessed: 45 },
    { month: "Nov", highRisk: 20, moderateRisk: 29, lowRisk: 93, assessed: 64 },
    { month: "Dec", highRisk: 19, moderateRisk: 27, lowRisk: 96, assessed: 78 },
    { month: "Jan", highRisk: 21, moderateRisk: 30, lowRisk: 91, assessed: 82 },
    { month: "Feb", highRisk: 18, moderateRisk: 28, lowRisk: 96, assessed: 88 }
  ],

  // Risk distribution breakdown for charts
  riskDistribution: [
    { tier: "Low Risk", count: 96, percentage: 67.6, color: "#15803D", surface: "#DCFCE7", description: "Satisfactory academic & attendance metrics" },
    { tier: "Moderate Risk", count: 28, percentage: 19.7, color: "#D97706", surface: "#FEF3C7", description: "Borderline indicators; advisory monitoring recommended" },
    { tier: "High Risk", count: 18, percentage: 12.7, color: "#DC2626", surface: "#FEE2E2", description: "Critical threshold breach; immediate pedagogical intervention required" }
  ],

  // 15 Fictional student profiles for demo directory & table
  students: [
    {
      id: "STU-2026-081",
      name: "Marcus Brody",
      alias: "M.B.",
      grade: "Grade 11",
      section: "Class 11-B",
      attendance: 62.5,
      testScore: 41.0,
      assignmentRate: 50.0,
      studyHours: 4.5,
      riskTier: "High Risk",
      primaryRiskFactor: "Attendance Deficit (< 70%) & Low Test Scores",
      recommendedAction: "Mandatory Academic Mentorship & Attendance Contract",
      assessmentDate: "2026-10-11",
      status: "Action Required",
      interventions: [
        { id: "INT-101", title: "Schedule Bi-weekly Attendance Counseling", type: "Mentorship", status: "In Progress", dueDate: "2026-10-20" },
        { id: "INT-102", title: "Assign Peer Tutor for Mathematics", type: "Tutoring", status: "Pending", dueDate: "2026-10-25" }
      ],
      notes: "Student missed 6 consecutive Friday sessions. Family contacted on Oct 8."
    },
    {
      id: "STU-2026-042",
      name: "Sofia Rodriguez",
      alias: "S.R.",
      grade: "Grade 11",
      section: "Class 11-A",
      attendance: 94.0,
      testScore: 88.5,
      assignmentRate: 98.0,
      studyHours: 16.0,
      riskTier: "Low Risk",
      primaryRiskFactor: "None (Consistent High Engagement)",
      recommendedAction: "Maintain Current Enrichment Pathway",
      assessmentDate: "2026-10-12",
      status: "On Track",
      interventions: [],
      notes: "Excelling in STEM subjects. Recommended for advanced honors seminar."
    },
    {
      id: "STU-2026-095",
      name: "Tariq Al-Mansoor",
      alias: "T.A.",
      grade: "Grade 12",
      section: "Class 12-C",
      attendance: 76.0,
      testScore: 54.0,
      assignmentRate: 65.0,
      studyHours: 7.0,
      riskTier: "Moderate Risk",
      primaryRiskFactor: "Declining Assignment Submissions",
      recommendedAction: "Structured Homework Check-ins & Math Support",
      assessmentDate: "2026-10-09",
      status: "Review Pending",
      interventions: [
        { id: "INT-103", title: "Weekly Homework Submission Verification", type: "Academic Plan", status: "Pending", dueDate: "2026-10-22" }
      ],
      notes: "Shows high verbal understanding in class but struggles with homework completion."
    },
    {
      id: "STU-2026-014",
      name: "Elena Rostova",
      alias: "E.R.",
      grade: "Grade 10",
      section: "Class 10-A",
      attendance: 91.0,
      testScore: 79.0,
      assignmentRate: 92.0,
      studyHours: 12.5,
      riskTier: "Low Risk",
      primaryRiskFactor: "Mild Test Anxiety Noted",
      recommendedAction: "Standard Advisory Check-in",
      assessmentDate: "2026-10-13",
      status: "On Track",
      interventions: [],
      notes: "Active participant in school science exhibitions."
    },
    {
      id: "STU-2026-108",
      name: "David Kim",
      alias: "D.K.",
      grade: "Grade 11",
      section: "Class 11-B",
      attendance: 68.0,
      testScore: 48.0,
      assignmentRate: 42.0,
      studyHours: 5.0,
      riskTier: "High Risk",
      primaryRiskFactor: "Low Assignment Frequency & Irregular Attendance",
      recommendedAction: "Parent-Teacher Academic Conference",
      assessmentDate: "2026-10-07",
      status: "Action Required",
      interventions: [
        { id: "INT-104", title: "Parent-Teacher Conference Scheduled", type: "Parental Engagement", status: "In Progress", dueDate: "2026-10-18" },
        { id: "INT-105", title: "Study Skills Workshop Placement", type: "Tutoring", status: "Pending", dueDate: "2026-10-24" }
      ],
      notes: "Reported transportation difficulties. Counselor evaluating bus route adjustment."
    },
    {
      id: "STU-2026-033",
      name: "Amara Okafor",
      alias: "A.O.",
      grade: "Grade 12",
      section: "Class 12-A",
      attendance: 98.0,
      testScore: 92.0,
      assignmentRate: 100.0,
      studyHours: 20.0,
      riskTier: "Low Risk",
      primaryRiskFactor: "None (Exemplary Performance)",
      recommendedAction: "Nominate for Peer Leadership Tutoring Role",
      assessmentDate: "2026-10-14",
      status: "On Track",
      interventions: [],
      notes: "Top quartile across all foundational subjects."
    },
    {
      id: "STU-2026-067",
      name: "Lucas Meyer",
      alias: "L.M.",
      grade: "Grade 10",
      section: "Class 10-C",
      attendance: 73.0,
      testScore: 58.0,
      assignmentRate: 70.0,
      studyHours: 6.5,
      riskTier: "Moderate Risk",
      primaryRiskFactor: "Study Hours Below Recommended Threshold (< 8h)",
      recommendedAction: "Time Management & Study Scheduling Consultation",
      assessmentDate: "2026-10-10",
      status: "Review Pending",
      interventions: [
        { id: "INT-106", title: "Establish Daily Study Schedule Log", type: "Academic Plan", status: "Completed", dueDate: "2026-10-12" }
      ],
      notes: "Shows quick grasp of concepts once study routines are stabilized."
    },
    {
      id: "STU-2026-119",
      name: "Priya Patel",
      alias: "P.P.",
      grade: "Grade 11",
      section: "Class 11-A",
      attendance: 88.0,
      testScore: 74.0,
      assignmentRate: 85.0,
      studyHours: 11.0,
      riskTier: "Low Risk",
      primaryRiskFactor: "Occasional Late Submissions",
      recommendedAction: "Self-paced Checkpoint Review",
      assessmentDate: "2026-10-05",
      status: "On Track",
      interventions: [],
      notes: "Consistently recovers after interim teacher feedback."
    },
    {
      id: "STU-2026-052",
      name: "Jordan Taylor",
      alias: "J.T.",
      grade: "Grade 12",
      section: "Class 12-B",
      attendance: 64.0,
      testScore: 43.5,
      assignmentRate: 55.0,
      studyHours: 3.0,
      riskTier: "High Risk",
      primaryRiskFactor: "Low Internal Assessment & Minimal Study Time",
      recommendedAction: "Direct Pedagogical Remediation & Faculty Mentor",
      assessmentDate: "2026-10-06",
      status: "Action Required",
      interventions: [
        { id: "INT-107", title: "Assign Faculty Mentor for Weekly Sync", type: "Mentorship", status: "In Progress", dueDate: "2026-10-19" }
      ],
      notes: "Needs supplemental foundation in algebra and analytical reading."
    },
    {
      id: "STU-2026-027",
      name: "Chloe Dubois",
      alias: "C.D.",
      grade: "Grade 10",
      section: "Class 10-B",
      attendance: 82.0,
      testScore: 68.0,
      assignmentRate: 78.0,
      studyHours: 9.0,
      riskTier: "Moderate Risk",
      primaryRiskFactor: "Moderate Fluctuation in Test Performance",
      recommendedAction: "Bi-weekly Formative Check-ins",
      assessmentDate: "2026-10-11",
      status: "Review Pending",
      interventions: [],
      notes: "Performs strongly in group activities; test anxiety remains a factor."
    },
    {
      id: "STU-2026-140",
      name: "Aarav Sharma",
      alias: "A.S.",
      grade: "Grade 11",
      section: "Class 11-C",
      attendance: 95.0,
      testScore: 89.0,
      assignmentRate: 94.0,
      studyHours: 14.0,
      riskTier: "Low Risk",
      primaryRiskFactor: "None",
      recommendedAction: "Continued Enrichment",
      assessmentDate: "2026-10-13",
      status: "On Track",
      interventions: [],
      notes: "Consistent performance across all evaluation milestones."
    },
    {
      id: "STU-2026-075",
      name: "Hannah Schmidt",
      alias: "H.S.",
      grade: "Grade 12",
      section: "Class 12-C",
      attendance: 69.5,
      testScore: 52.0,
      assignmentRate: 60.0,
      studyHours: 5.5,
      riskTier: "High Risk",
      primaryRiskFactor: "Attendance Drop in Past 4 Weeks",
      recommendedAction: "Early Intervention Attendance Outreach",
      assessmentDate: "2026-10-08",
      status: "Action Required",
      interventions: [
        { id: "INT-108", title: "Attendance Support Officer Outreach", type: "Counseling", status: "Pending", dueDate: "2026-10-21" }
      ],
      notes: "Expressed concern regarding test backlog. Guidance counselor involved."
    }
  ],

  // Literature research benchmarks (Formal Multi-Model Evaluation on UCI Cohort)
  researchBenchmarks: [
    {
      model: "Random Forest (Selected)",
      cvMacroF1: 0.8787,
      cvStd: 0.0515,
      testMacroF1: 0.8077,
      testAccuracy: 87.69,
      highRiskRecall: 90.0,
      falseNegatives: 2,
      rocAuc: 0.9236,
      trainingDuration: 4.52,
      inferenceLatency: 10.05,
      serializedSize: 288.54,
      status: "Production Pipeline"
    },
    {
      model: "Decision Tree",
      cvMacroF1: 0.8522,
      cvStd: 0.0517,
      testMacroF1: 0.8077,
      testAccuracy: 87.69,
      highRiskRecall: 90.0,
      falseNegatives: 2,
      rocAuc: 0.9255,
      trainingDuration: 1.75,
      inferenceLatency: 4.96,
      serializedSize: 27.95,
      status: "Candidate Baseline"
    },
    {
      model: "Logistic Regression",
      cvMacroF1: 0.8376,
      cvStd: 0.0712,
      testMacroF1: 0.8467,
      testAccuracy: 90.77,
      highRiskRecall: 90.0,
      falseNegatives: 2,
      rocAuc: 0.9382,
      trainingDuration: 0.54,
      inferenceLatency: 5.01,
      serializedSize: 26.74,
      status: "Candidate Baseline"
    },
    {
      model: "Support Vector (SVC)",
      cvMacroF1: 0.8256,
      cvStd: 0.0442,
      testMacroF1: 0.8365,
      testAccuracy: 90.0,
      highRiskRecall: 90.0,
      falseNegatives: 2,
      rocAuc: 0.9459,
      trainingDuration: 2.25,
      inferenceLatency: 5.26,
      serializedSize: 62.67,
      status: "Candidate Baseline"
    }
  ],

  // Deterministic Intervention Rules for pedagogical demonstration
  interventionRules: [
    {
      id: "RULE-ATTN-01",
      name: "Critical Attendance Breach",
      condition: "attendance_rate < 70.0%",
      priority: "CRITICAL",
      action: "Mandatory Attendance Contract & Parent Contact",
      interventionType: "Attendance Counseling",
      leadRole: "Attendance Officer / Academic Dean"
    },
    {
      id: "RULE-TEST-02",
      name: "Formative Assessment Deficit",
      condition: "internal_test_score < 50.0%",
      priority: "HIGH",
      action: "Subject-Specific Peer Tutoring & Faculty Remediation",
      interventionType: "Subject Remediation",
      leadRole: "Subject Teacher"
    },
    {
      id: "RULE-SUBM-03",
      name: "Assignment Irregularity",
      condition: "assignment_submission_frequency < 60.0%",
      priority: "HIGH",
      action: "Weekly Academic Task Check-in & Homework Planner",
      interventionType: "Study Management",
      leadRole: "Homeroom Advisor"
    },
    {
      id: "RULE-STUDY-04",
      name: "Study Hours Under-allocation",
      condition: "study_hours < 8.0 hrs/week",
      priority: "MODERATE",
      action: "Study Habit Workshop & Time-Budgeting Consultation",
      interventionType: "Skills Coaching",
      leadRole: "Academic Counselor"
    }
  ]
};
