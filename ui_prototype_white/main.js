/**
 * EduRisk XAI — White Theme UI Prototype Main Script
 * 
 * Features:
 * - Single Page Navigation router
 * - Role-aware UI switcher (Demonstration mode)
 * - Multi-step interactive risk assessment form with validation
 * - Dynamic data filtering, search, and sorting
 * - Student detail modals with editable intervention checklist
 * - Anime.js micro-animations and accessibility integrations
 */

document.addEventListener('DOMContentLoaded', function () {
  // --- Global Application State ---
  const state = {
    currentView: 'home',
    currentRole: 'teacher', // 'teacher', 'admin', 'researcher'
    studentFilter: 'all',
    searchQuery: '',
    sortColumn: 'assessmentDate',
    sortAscending: false,
    studentsList: [...window.EduRiskData.students],
    activeAssessmentStep: 1,
    assessmentData: {
      studentRef: '',
      studentAlias: '',
      gradeLevel: 'Grade 11',
      academicStream: 'Science & Mathematics',
      internalTestScore: 65,
      assignmentRate: 75,
      priorGrade: 'B',
      subjectDifficulties: 'Mathematics',
      studyHours: 8,
      attendanceRate: 82,
      tutoringSupport: 'none',
      familySupport: 'moderate'
    },
    selectedStudentForModal: null
  };

  // --- Element Selectors ---
  const views = {
    login: document.getElementById('view-login'),
    home: document.getElementById('view-home'),
    assessment: document.getElementById('view-assessment'),
    students: document.getElementById('view-students'),
    reports: document.getElementById('view-reports'),
    admin: document.getElementById('view-admin')
  };

  const navButtons = document.querySelectorAll('.nav-button');
  const mobileToggleBtn = document.getElementById('mobileMenuToggle');
  const navMenu = document.getElementById('navMenu');
  const studentDetailModal = document.getElementById('studentDetailModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalDoneBtn = document.getElementById('modalDoneBtn');

  // Pre-configured authentic demo accounts
  const DEMO_USERS = {
    teacher1: { username: 'teacher1', name: 'Dr. Elena Vance', role: 'teacher', roleTitle: 'Educator', initials: 'EV', org: 'Horizon High School' },
    teacher2: { username: 'teacher2', name: 'Marcus Brody', role: 'teacher', roleTitle: 'Educator', initials: 'MB', org: 'Metro District High' },
    orgadmin: { username: 'orgadmin', name: 'Administrator Sterling', role: 'admin', roleTitle: 'Org Admin', initials: 'AS', org: 'Horizon High School' },
    researcher: { username: 'researcher', name: 'Lead Researcher Kesare', role: 'researcher', roleTitle: 'Researcher', initials: 'RK', org: 'System-Wide' }
  };

  // ==========================================================================
  // 1. ROUTER & AUTHENTICATION STATE MANAGEMENT
  // ==========================================================================

  function checkAuthState() {
    const raw = sessionStorage.getItem('edurisk_active_user');
    const mainNavBar = document.getElementById('mainNavBar');
    const authenticatedNavControls = document.getElementById('authenticatedNavControls');
    const unauthNavIndicator = document.getElementById('unauthNavIndicator');
    const navItemAdmin = document.getElementById('navItemAdmin');

    if (!raw) {
      state.currentUser = null;
      if (mainNavBar) mainNavBar.style.display = 'none';
      if (authenticatedNavControls) authenticatedNavControls.style.display = 'none';
      if (unauthNavIndicator) unauthNavIndicator.style.display = 'flex';
      switchView('login');
      return false;
    }

    try {
      state.currentUser = JSON.parse(raw);
      state.currentRole = state.currentUser.role;

      if (mainNavBar) mainNavBar.style.display = 'flex';
      if (authenticatedNavControls) authenticatedNavControls.style.display = 'flex';
      if (unauthNavIndicator) unauthNavIndicator.style.display = 'none';

      const userProfileName = document.getElementById('userProfileName');
      const userAvatar = document.getElementById('userAvatar');
      const currentRoleBadge = document.getElementById('currentRoleBadge');

      if (userProfileName) userProfileName.textContent = state.currentUser.name;
      if (userAvatar) userAvatar.textContent = state.currentUser.initials;
      if (currentRoleBadge) currentRoleBadge.textContent = state.currentUser.roleTitle;

      // Role boundary: educators cannot access administrative research tools
      if (navItemAdmin) {
        navItemAdmin.style.display = (state.currentRole === 'admin' || state.currentRole === 'researcher') ? 'block' : 'none';
      }

      const greetingHeading = document.getElementById('userGreetingHeading');
      if (greetingHeading) {
        greetingHeading.textContent = `Welcome back, ${state.currentUser.name}`;
      }

      return true;
    } catch (e) {
      sessionStorage.removeItem('edurisk_active_user');
      switchView('login');
      return false;
    }
  }

  function switchView(targetViewId) {
    if (!views[targetViewId]) return;

    // Route Guard: Unauthenticated users are strictly confined to login
    const isAuth = !!sessionStorage.getItem('edurisk_active_user');
    if (!isAuth && targetViewId !== 'login') {
      targetViewId = 'login';
    }

    // Role Guard: Teacher role cannot navigate to research & admin
    if (targetViewId === 'admin' && state.currentRole === 'teacher') {
      window.EduRiskAnimations.showToast('Access Denied: Research & Admin tools are restricted to authorized administrators.');
      return;
    }

    // Hide all views
    Object.keys(views).forEach(key => {
      if (views[key]) {
        views[key].classList.remove('active-view');
        views[key].style.display = 'none';
      }
    });

    // Update active nav button
    navButtons.forEach(btn => {
      const isTarget = btn.getAttribute('data-target-view') === targetViewId;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });

    // Show target view
    const targetEl = views[targetViewId];
    targetEl.style.display = 'block';
    targetEl.classList.add('active-view');

    // Run Anime.js transition
    window.EduRiskAnimations.animatePageTransition(targetEl);

    state.currentView = targetViewId;

    // Close mobile menu if open
    if (navMenu && navMenu.classList.contains('mobile-open')) {
      navMenu.classList.remove('mobile-open');
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Trigger view-specific initializations
    if (targetViewId === 'home') {
      renderDashboardMetrics();
      renderRecentActivityTable();
    } else if (targetViewId === 'students') {
      renderStudentsDirectory();
    } else if (targetViewId === 'reports') {
      renderReportsView();
    } else if (targetViewId === 'admin') {
      renderAdminView();
    }
  }

  // Bind top navigation buttons
  navButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const target = this.getAttribute('data-target-view');
      switchView(target);
    });
  });

  // Mobile menu toggle
  if (mobileToggleBtn) {
    mobileToggleBtn.addEventListener('click', function () {
      const isOpen = navMenu.classList.toggle('mobile-open');
      mobileToggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // ==========================================================================
  // 2. AUTHENTICATION & LOGIN FORM HANDLERS
  // ==========================================================================

  const loginForm = document.getElementById('loginForm');
  const loginErrorAlert = document.getElementById('loginErrorAlert');
  const loginErrorText = document.getElementById('loginErrorText');
  const btnLogout = document.getElementById('btnLogout');

  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const u = (document.getElementById('loginUsername').value || '').trim();
      const p = (document.getElementById('loginPassword').value || '').trim();

      if (!u || !p) {
        showLoginError('Please enter both username and password.');
        return;
      }

      const user = DEMO_USERS[u];
      if (user && (p === 'teacher123' || p === 'admin123' || p === 'researcher123')) {
        hideLoginError();
        sessionStorage.setItem('edurisk_active_user', JSON.stringify(user));
        checkAuthState();
        switchView('home');
        window.EduRiskAnimations.showToast(`Logged in successfully as ${user.name} (${user.roleTitle})`);
      } else {
        showLoginError('Invalid username or password. Please verify credentials.');
      }
    });
  }

  // Demo account quick login buttons
  document.querySelectorAll('.btn-demo-pill').forEach(btn => {
    btn.addEventListener('click', function () {
      const u = this.getAttribute('data-user');
      const p = this.getAttribute('data-pass');
      document.getElementById('loginUsername').value = u;
      document.getElementById('loginPassword').value = p;
      loginForm.dispatchEvent(new Event('submit'));
    });
  });

  if (btnLogout) {
    btnLogout.addEventListener('click', function () {
      sessionStorage.removeItem('edurisk_active_user');
      window.EduRiskAnimations.showToast('You have been signed out successfully.');
      checkAuthState();
    });
  }

  function showLoginError(msg) {
    if (loginErrorAlert && loginErrorText) {
      loginErrorText.textContent = msg;
      loginErrorAlert.style.display = 'flex';
    }
  }

  function hideLoginError() {
    if (loginErrorAlert) {
      loginErrorAlert.style.display = 'none';
    }
  }


  // ==========================================================================
  // 3. DASHBOARD RENDERING & VISUALIZATIONS
  // ==========================================================================

  function renderDashboardMetrics() {
    const stats = window.EduRiskData.cohortStats;
    const totalEl = document.getElementById('metricTotalStudents');
    const attentionEl = document.getElementById('metricAttentionStudents');
    const completedEl = document.getElementById('metricCompletedAssessments');
    const pendingEl = document.getElementById('metricPendingActions');

    if (totalEl) window.EduRiskAnimations.animateCountUp(totalEl, stats.totalStudents, 600);
    if (attentionEl) window.EduRiskAnimations.animateCountUp(attentionEl, stats.highRiskCount, 600);
    if (completedEl) window.EduRiskAnimations.animateCountUp(completedEl, stats.assessmentsCompleted, 600);
    if (pendingEl) window.EduRiskAnimations.animateCountUp(pendingEl, stats.followUpActionsPending, 600);

    // Stagger metric cards entrance
    window.EduRiskAnimations.animateStaggerCards('.metric-card');
  }

  function renderRecentActivityTable() {
    const tbody = document.getElementById('recentActivityTbody');
    if (!tbody) return;

    // Filter students
    let filtered = state.studentsList.filter(s => {
      const matchesSearch = s.name.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
                            s.id.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
                            s.grade.toLowerCase().includes(state.searchQuery.toLowerCase());
      if (state.studentFilter === 'all') return matchesSearch;
      if (state.studentFilter === 'high') return matchesSearch && s.riskTier === 'High Risk';
      if (state.studentFilter === 'moderate') return matchesSearch && s.riskTier === 'Moderate Risk';
      if (state.studentFilter === 'low') return matchesSearch && s.riskTier === 'Low Risk';
      return matchesSearch;
    });

    // Sort students
    filtered.sort((a, b) => {
      let valA = a[state.sortColumn];
      let valB = b[state.sortColumn];
      if (typeof valA === 'string') {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }
      if (valA < valB) return state.sortAscending ? -1 : 1;
      if (valA > valB) return state.sortAscending ? 1 : -1;
      return 0;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
            🔍 No student records match the active filter or search criteria.
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = filtered.slice(0, 7).map(student => {
      const badgeClass = student.riskTier === 'High Risk' ? 'high-risk' :
                         student.riskTier === 'Moderate Risk' ? 'moderate-risk' : 'low-risk';
      
      return `
        <tr>
          <td>
            <strong>${student.id}</strong><br>
            <span style="font-size: 0.78rem; color: var(--text-secondary);">${student.alias}</span>
          </td>
          <td>
            <strong>${student.name}</strong><br>
            <span style="font-size: 0.78rem; color: var(--text-secondary);">${student.grade} (${student.section})</span>
          </td>
          <td>${student.assessmentDate}</td>
          <td>
            <span class="risk-badge ${badgeClass}">
              <span class="risk-dot"></span>
              ${student.riskTier}
            </span>
          </td>
          <td style="max-width: 240px; font-size: 0.84rem;">
            ${student.recommendedAction}
          </td>
          <td>
            <button class="btn btn-secondary btn-sm view-student-btn" data-student-id="${student.id}" aria-label="View profile for ${student.name}">
              View Profile
            </button>
          </td>
        </tr>
      `;
    }).join('');

    // Attach click listeners to view buttons
    document.querySelectorAll('.view-student-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        const studentId = this.getAttribute('data-student-id');
        openStudentModal(studentId);
      });
    });
  }

  // Dashboard Table Search & Filter Listeners
  const dashSearchInput = document.getElementById('dashSearchInput');
  if (dashSearchInput) {
    dashSearchInput.addEventListener('input', function () {
      state.searchQuery = this.value.trim();
      renderRecentActivityTable();
    });
  }

  document.querySelectorAll('.table-toolbar .filter-pill').forEach(pill => {
    pill.addEventListener('click', function () {
      document.querySelectorAll('.table-toolbar .filter-pill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      state.studentFilter = this.getAttribute('data-filter') || 'all';
      renderRecentActivityTable();
    });
  });

  // Table Sort Header Listeners
  document.querySelectorAll('.data-table th.sortable').forEach(th => {
    th.addEventListener('click', function () {
      const col = this.getAttribute('data-sort-col');
      if (state.sortColumn === col) {
        state.sortAscending = !state.sortAscending;
      } else {
        state.sortColumn = col;
        state.sortAscending = true;
      }
      renderRecentActivityTable();
    });
  });

  // Fast Navigation Quick Buttons
  const btnAssessQuick = document.getElementById('btnQuickAssess');
  if (btnAssessQuick) {
    btnAssessQuick.addEventListener('click', () => switchView('assessment'));
  }

  const btnReviewAttention = document.getElementById('btnReviewAttention');
  if (btnReviewAttention) {
    btnReviewAttention.addEventListener('click', () => {
      switchView('students');
      const highRiskPill = document.querySelector('#studentsFilterGroup [data-filter="high"]');
      if (highRiskPill) highRiskPill.click();
    });
  }

  // ==========================================================================
  // 4. MULTI-STEP ASSESSMENT WIZARD
  // ==========================================================================

  const stepNodes = document.querySelectorAll('.step-node');
  const stepPanels = document.querySelectorAll('.wizard-form-step');
  const stepperFill = document.getElementById('stepperFill');
  const btnWizardBack = document.getElementById('btnWizardBack');
  const btnWizardNext = document.getElementById('btnWizardNext');
  const btnWizardReset = document.getElementById('btnWizardReset');
  const btnRunAssessment = document.getElementById('btnRunAssessment');
  const assessmentOutcomeCard = document.getElementById('assessmentOutcomeCard');

  // Sliders dynamic value display sync
  function setupSliderSync(sliderId, badgeId, unit = '%') {
    const slider = document.getElementById(sliderId);
    const badge = document.getElementById(badgeId);
    if (!slider || !badge) return;

    slider.addEventListener('input', function () {
      badge.textContent = this.value + unit;
      state.assessmentData[sliderId] = parseFloat(this.value);
    });
  }

  setupSliderSync('internalTestScore', 'internalTestBadge', '%');
  setupSliderSync('assignmentRate', 'assignmentRateBadge', '%');
  setupSliderSync('attendanceRate', 'attendanceRateBadge', '%');
  setupSliderSync('studyHours', 'studyHoursBadge', ' hrs');

  function updateWizardStep(newStep) {
    if (newStep < 1 || newStep > 4) return;

    const currentStepEl = document.getElementById(`wizardStep${state.activeAssessmentStep}`);
    const nextStepEl = document.getElementById(`wizardStep${newStep}`);
    const direction = newStep > state.activeAssessmentStep ? 'forward' : 'backward';

    // Update stepper nodes
    stepNodes.forEach((node, idx) => {
      const stepIdx = idx + 1;
      node.classList.toggle('active', stepIdx === newStep);
      node.classList.toggle('completed', stepIdx < newStep);
    });

    // Update progress bar width
    const percentMap = { 1: 25, 2: 50, 3: 75, 4: 100 };
    window.EduRiskAnimations.animateProgressBar(stepperFill, percentMap[newStep]);

    // Slide transition
    window.EduRiskAnimations.animateStepSlide(currentStepEl, nextStepEl, direction);

    state.activeAssessmentStep = newStep;

    // Update button states
    if (btnWizardBack) {
      btnWizardBack.style.visibility = newStep === 1 ? 'hidden' : 'visible';
    }

    if (btnWizardNext) {
      btnWizardNext.style.display = newStep === 4 ? 'none' : 'inline-flex';
    }

    if (btnRunAssessment) {
      btnRunAssessment.style.display = newStep === 4 ? 'inline-flex' : 'none';
    }

    // If step 4 (Review), populate review table
    if (newStep === 4) {
      populateReviewSummary();
    }
  }

  // Stepper Header Node Click
  stepNodes.forEach(node => {
    node.addEventListener('click', function () {
      const targetStep = parseInt(this.getAttribute('data-step-target'), 10);
      if (targetStep < state.activeAssessmentStep || validateCurrentStep(state.activeAssessmentStep)) {
        updateWizardStep(targetStep);
      }
    });
  });

  // Client-side Validation per Step
  function validateCurrentStep(stepNum) {
    let isValid = true;

    if (stepNum === 1) {
      const refInput = document.getElementById('studentRefInput');
      const refErr = document.getElementById('studentRefError');
      if (!refInput.value.trim()) {
        refInput.setAttribute('aria-invalid', 'true');
        refErr.classList.add('visible');
        isValid = false;
      } else {
        refInput.setAttribute('aria-invalid', 'false');
        refErr.classList.remove('visible');
        state.assessmentData.studentRef = refInput.value.trim();
      }

      const aliasInput = document.getElementById('studentAliasInput');
      state.assessmentData.studentAlias = aliasInput.value.trim() || 'N/A';
      state.assessmentData.gradeLevel = document.getElementById('gradeLevelSelect').value;
      state.assessmentData.academicStream = document.getElementById('academicStreamSelect').value;
    } else if (stepNum === 2) {
      state.assessmentData.internalTestScore = parseFloat(document.getElementById('internalTestScore').value);
      state.assessmentData.assignmentRate = parseFloat(document.getElementById('assignmentRate').value);
      state.assessmentData.priorGrade = document.getElementById('priorGradeSelect').value;
      state.assessmentData.subjectDifficulties = document.getElementById('subjectDifficultiesSelect').value;
    } else if (stepNum === 3) {
      state.assessmentData.attendanceRate = parseFloat(document.getElementById('attendanceRate').value);
      state.assessmentData.studyHours = parseFloat(document.getElementById('studyHours').value);
      state.assessmentData.tutoringSupport = document.getElementById('tutoringSelect').value;
      state.assessmentData.familySupport = document.getElementById('familySupportSelect').value;
    }

    return isValid;
  }

  if (btnWizardNext) {
    btnWizardNext.addEventListener('click', function () {
      if (validateCurrentStep(state.activeAssessmentStep)) {
        updateWizardStep(state.activeAssessmentStep + 1);
      }
    });
  }

  if (btnWizardBack) {
    btnWizardBack.addEventListener('click', function () {
      updateWizardStep(state.activeAssessmentStep - 1);
    });
  }

  if (btnWizardReset) {
    btnWizardReset.addEventListener('click', function () {
      if (confirm('Reset assessment form? All current entries will be cleared.')) {
        document.getElementById('studentAssessmentForm').reset();
        document.getElementById('studentRefInput').value = '';
        document.getElementById('studentAliasInput').value = '';
        setupSliderSync('internalTestScore', 'internalTestBadge', '%');
        setupSliderSync('assignmentRate', 'assignmentRateBadge', '%');
        setupSliderSync('attendanceRate', 'attendanceRateBadge', '%');
        setupSliderSync('studyHours', 'studyHoursBadge', ' hrs');
        if (assessmentOutcomeCard) assessmentOutcomeCard.style.display = 'none';
        updateWizardStep(1);
        window.EduRiskAnimations.showToast('Assessment form has been reset.');
      }
    });
  }

  function populateReviewSummary() {
    const summaryContainer = document.getElementById('reviewSummaryTable');
    if (!summaryContainer) return;

    summaryContainer.innerHTML = `
      <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.25rem;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
          <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 6px 0; color: var(--text-secondary);">Student Reference:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right;">${state.assessmentData.studentRef || 'STU-DEMO-01'} (${state.assessmentData.studentAlias || 'None'})</td>
          </tr>
          <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 6px 0; color: var(--text-secondary);">Cohort & Stream:</td>
            <td style="padding: 6px 0; font-weight: 600; text-align: right;">${state.assessmentData.gradeLevel} • ${state.assessmentData.academicStream}</td>
          </tr>
          <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 6px 0; color: var(--text-secondary);">Internal Test Score:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right; color: ${state.assessmentData.internalTestScore < 50 ? 'var(--risk-high)' : 'var(--text-heading)'};">${state.assessmentData.internalTestScore}%</td>
          </tr>
          <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 6px 0; color: var(--text-secondary);">Assignment Submission:</td>
            <td style="padding: 6px 0; font-weight: 600; text-align: right;">${state.assessmentData.assignmentRate}%</td>
          </tr>
          <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 6px 0; color: var(--text-secondary);">Attendance Rate:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right; color: ${state.assessmentData.attendanceRate < 70 ? 'var(--risk-high)' : 'var(--text-heading)'};">${state.assessmentData.attendanceRate}%</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary);">Weekly Study Hours:</td>
            <td style="padding: 6px 0; font-weight: 600; text-align: right;">${state.assessmentData.studyHours} hours/week</td>
          </tr>
        </table>
      </div>
    `;
  }

  // Handle Demonstration Assessment Submission
  if (btnRunAssessment) {
    btnRunAssessment.addEventListener('click', function () {
      btnRunAssessment.disabled = true;
      btnRunAssessment.innerHTML = '⏳ Simulating Assessment...';

      setTimeout(() => {
        btnRunAssessment.disabled = false;
        btnRunAssessment.innerHTML = '🚀 Run Demonstration Assessment';

        renderAssessmentOutcome();
      }, 700);
    });
  }

  function renderAssessmentOutcome() {
    if (!assessmentOutcomeCard) return;

    // Transparent heuristic for demonstration risk tier
    const attn = state.assessmentData.attendanceRate;
    const test = state.assessmentData.internalTestScore;
    const study = state.assessmentData.studyHours;
    const subm = state.assessmentData.assignmentRate;

    let tier = 'Low Risk';
    let badgeClass = 'low-risk';
    let actionDesc = 'Continue positive reinforcement and standard academic check-ins.';

    if (attn < 70 || test < 50 || study < 4) {
      tier = 'High Risk';
      badgeClass = 'high-risk';
      actionDesc = 'Immediate faculty advisor meeting, attendance contract, and foundational tutoring required.';
    } else if (attn < 80 || test < 65 || subm < 70) {
      tier = 'Moderate Risk';
      badgeClass = 'moderate-risk';
      actionDesc = 'Bi-weekly advisory check-in and structured study habit schedule recommended.';
    }

    const bannerBg = tier === 'High Risk' ? '#DC2626' : (tier === 'Moderate Risk' ? '#D97706' : '#15803D');

    const outcomeHtml = `
      <div style="background-color: ${bannerBg}; color: #FFFFFF; border-radius: var(--radius-md); padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9; font-weight: 700;">Simulated Formative Risk Assessment</div>
          <div style="font-size: 1.85rem; font-weight: 800; letter-spacing: -0.01em;">${tier}</div>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: var(--radius-md); font-size: 0.88rem; font-weight: 600;">
          Student PRN: ${state.assessmentData.studentRef || 'STU-2026-081'}
        </div>
      </div>

      <div class="outcome-alert-box">
        <strong>⚠️ Non-Production Simulation Notice:</strong> This interactive prototype demonstrates UI layouts, explainability visualizations, and deterministic rules. Production predictions are served by the calibrated Random Forest model on the backend.
      </div>

      <div class="outcome-grid">
        <!-- Feature Attribution Decomposition -->
        <div>
          <h4 style="margin-bottom: 0.85rem; font-size: 1rem; color: var(--text-heading);">Simulated Risk Factor Attribution:</h4>
          
          <div class="attribution-bar-row">
            <div class="attribution-label-row">
              <span>Attendance Rate (${attn}%)</span>
              <strong style="color: ${attn < 75 ? 'var(--risk-high)' : 'var(--risk-low)'};">${attn < 75 ? '+ Risk (Deficit)' : '- Protective'}</strong>
            </div>
            <div class="attribution-track">
              <div class="attribution-fill ${attn < 75 ? 'risk-increasing' : 'protective'}" style="width: ${Math.min(100, Math.abs(attn - 75) * 1.5 + 20)}%;"></div>
            </div>
          </div>

          <div class="attribution-bar-row">
            <div class="attribution-label-row">
              <span>Internal Test Score (${test}%)</span>
              <strong style="color: ${test < 60 ? 'var(--risk-high)' : 'var(--risk-low)'};">${test < 60 ? '+ Risk (Deficit)' : '- Protective'}</strong>
            </div>
            <div class="attribution-track">
              <div class="attribution-fill ${test < 60 ? 'risk-increasing' : 'protective'}" style="width: ${Math.min(100, Math.abs(test - 60) * 1.2 + 15)}%;"></div>
            </div>
          </div>

          <div class="attribution-bar-row">
            <div class="attribution-label-row">
              <span>Study Hours (${study} hrs/wk)</span>
              <strong style="color: ${study < 8 ? 'var(--risk-high)' : 'var(--risk-low)'};">${study < 8 ? '+ Risk (Deficit)' : '- Protective'}</strong>
            </div>
            <div class="attribution-track">
              <div class="attribution-fill ${study < 8 ? 'risk-increasing' : 'protective'}" style="width: ${Math.min(100, Math.abs(study - 8) * 4 + 20)}%;"></div>
            </div>
          </div>
        </div>

        <!-- Deterministic Pedagogical Interventions -->
        <div>
          <h4 style="margin-bottom: 0.85rem; font-size: 1rem; color: var(--text-heading);">Recommended Pedagogical Actions:</h4>
          <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.15rem;">
            <p style="font-weight: 700; color: var(--text-heading); margin-bottom: 0.5rem; font-size: 0.95rem;">
              ${actionDesc}
            </p>
            <ul style="padding-left: 1.2rem; font-size: 0.86rem; color: var(--text-body); line-height: 1.65; margin: 0;">
              ${attn < 75 ? '<li><strong>Attendance Outreach:</strong> Initiate mandatory counselor conference (Rule RULE-ATTN-01).</li>' : ''}
              ${test < 60 ? '<li><strong>Academic Remediation:</strong> Enroll in mathematics remedial peer-cohort (Rule RULE-ACAD-02).</li>' : ''}
              ${study < 8 ? '<li><strong>Study Contract:</strong> Formulate weekly study-hour tracking schedule (Rule RULE-HABIT-01).</li>' : ''}
              <li><strong>Advisor Milestone:</strong> Schedule 14-day progress re-assessment.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="outcome-actions-row">
        <button class="btn btn-secondary" id="btnExportDemoReport">
          📄 Download Summary
        </button>
        <button class="btn btn-primary" id="btnAssessAnother">
          ➕ Assess Another Student
        </button>
      </div>
    `;

    assessmentOutcomeCard.innerHTML = outcomeHtml;
    assessmentOutcomeCard.style.display = 'block';

    window.EduRiskAnimations.animateModalOpen(assessmentOutcomeCard, assessmentOutcomeCard);

    document.getElementById('btnAssessAnother').addEventListener('click', function () {
      assessmentOutcomeCard.style.display = 'none';
      updateWizardStep(1);
    });

    document.getElementById('btnExportDemoReport').addEventListener('click', function () {
      window.print();
    });

    assessmentOutcomeCard.scrollIntoView({ behavior: 'smooth' });
  }


  // ==========================================================================
  // 5. STUDENTS DIRECTORY VIEW
  // ==========================================================================

  function renderStudentsDirectory() {
    const tbody = document.getElementById('studentsDirectoryTbody');
    if (!tbody) return;

    let students = [...state.studentsList];

    // Filter by risk tier
    const filterGroup = document.getElementById('studentsFilterGroup');
    const activePill = filterGroup ? filterGroup.querySelector('.filter-pill.active') : null;
    const filterTier = activePill ? activePill.getAttribute('data-filter') : 'all';

    const searchInput = document.getElementById('studentsSearchInput');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    students = students.filter(s => {
      const matchesSearch = s.name.toLowerCase().includes(query) ||
                            s.id.toLowerCase().includes(query) ||
                            s.grade.toLowerCase().includes(query);
      if (filterTier === 'high') return matchesSearch && s.riskTier === 'High Risk';
      if (filterTier === 'moderate') return matchesSearch && s.riskTier === 'Moderate Risk';
      if (filterTier === 'low') return matchesSearch && s.riskTier === 'Low Risk';
      return matchesSearch;
    });

    tbody.innerHTML = students.map(s => {
      const badgeClass = s.riskTier === 'High Risk' ? 'high-risk' :
                         s.riskTier === 'Moderate Risk' ? 'moderate-risk' : 'low-risk';
      return `
        <tr>
          <td><strong>${s.id}</strong></td>
          <td>
            <strong>${s.name}</strong><br>
            <span style="font-size: 0.78rem; color: var(--text-secondary);">${s.alias}</span>
          </td>
          <td>${s.grade}</td>
          <td><strong>${s.attendance}%</strong></td>
          <td><strong>${s.testScore}%</strong></td>
          <td>${s.studyHours}h/wk</td>
          <td><span class="risk-badge ${badgeClass}"><span class="risk-dot"></span>${s.riskTier}</span></td>
          <td>
            <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
              <button class="btn btn-secondary btn-sm view-directory-student" data-student-id="${s.id}">
                Details
              </button>
              <button class="btn btn-primary btn-sm assess-directory-student" data-student-id="${s.id}">
                🎯 Assess
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    document.querySelectorAll('.view-directory-student').forEach(btn => {
      btn.addEventListener('click', function () {
        openStudentModal(this.getAttribute('data-student-id'));
      });
    });

    document.querySelectorAll('.assess-directory-student').forEach(btn => {
      btn.addEventListener('click', function () {
        const studentId = this.getAttribute('data-student-id');
        const student = state.studentsList.find(s => s.id === studentId);
        if (student) {
          switchView('assessment');
          document.getElementById('studentRefInput').value = student.id;
          document.getElementById('studentAliasInput').value = student.alias || '';
          updateWizardStep(1);
          window.EduRiskAnimations.showToast(`Pre-filled assessment for ${student.name} (${student.id}).`);
        }
      });
    });
  }

  // Bind directory search & filters
  const dirSearchInput = document.getElementById('studentsSearchInput');
  if (dirSearchInput) {
    dirSearchInput.addEventListener('input', renderStudentsDirectory);
  }

  document.querySelectorAll('#studentsFilterGroup .filter-pill').forEach(pill => {
    pill.addEventListener('click', function () {
      document.querySelectorAll('#studentsFilterGroup .filter-pill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      renderStudentsDirectory();
    });
  });

  // ==========================================================================
  // PRN-BASED ONE-TIME STUDENT REGISTRATION
  // ==========================================================================
  const btnOpenPrnModal = document.getElementById('btnOpenPrnModal');
  const prnRegistrationModal = document.getElementById('prnRegistrationModal');
  const prnModalCloseBtn = document.getElementById('prnModalCloseBtn');
  const btnCancelPrnModal = document.getElementById('btnCancelPrnModal');
  const btnVerifyPrn = document.getElementById('btnVerifyPrn');
  const regPrnInput = document.getElementById('regPrnInput');
  const regPrnError = document.getElementById('regPrnError');
  const prnExistingStudentAlert = document.getElementById('prnExistingStudentAlert');
  const prnExistingDetails = document.getElementById('prnExistingDetails');
  const newStudentRegForm = document.getElementById('newStudentRegForm');
  const btnSubmitPrnReg = document.getElementById('btnSubmitPrnReg');
  const btnAssessExistingStudent = document.getElementById('btnAssessExistingStudent');

  let activeVerifiedPrn = null;

  if (btnOpenPrnModal) {
    btnOpenPrnModal.addEventListener('click', openPrnModal);
  }

  function openPrnModal() {
    if (!prnRegistrationModal) return;
    regPrnInput.value = '';
    regPrnError.classList.remove('visible');
    prnExistingStudentAlert.style.display = 'none';
    newStudentRegForm.style.display = 'none';
    btnSubmitPrnReg.style.display = 'none';
    prnRegistrationModal.style.display = 'flex';
    window.EduRiskAnimations.animateModalOpen(prnRegistrationModal, prnRegistrationModal.querySelector('.modal-dialog'));
  }

  function closePrnModal() {
    if (!prnRegistrationModal) return;
    prnRegistrationModal.style.display = 'none';
  }

  if (prnModalCloseBtn) prnModalCloseBtn.addEventListener('click', closePrnModal);
  if (btnCancelPrnModal) btnCancelPrnModal.addEventListener('click', closePrnModal);

  function normalizePrn(val) {
    return (val || '').trim().toUpperCase();
  }

  if (btnVerifyPrn) {
    btnVerifyPrn.addEventListener('click', function () {
      const prn = normalizePrn(regPrnInput.value);
      if (!prn || prn.length < 2) {
        regPrnError.textContent = 'Please enter a valid PRN (e.g., PRN-2026-009).';
        regPrnError.classList.add('visible');
        return;
      }
      regPrnError.classList.remove('visible');
      activeVerifiedPrn = prn;

      // Check if PRN already exists in student list
      const existing = state.studentsList.find(s => normalizePrn(s.id) === prn || normalizePrn(s.prn) === prn);
      if (existing) {
        prnExistingDetails.innerHTML = `
          <strong>${existing.name}</strong> • ${existing.grade} (${existing.section}) • Track: ${existing.stream || 'Science & Mathematics'}<br>
          Risk Tier: <strong>${existing.riskTier}</strong> | Attendance: ${existing.attendance}%
        `;
        prnExistingStudentAlert.style.display = 'block';
        newStudentRegForm.style.display = 'none';
        btnSubmitPrnReg.style.display = 'none';

        if (btnAssessExistingStudent) {
          btnAssessExistingStudent.onclick = function () {
            closePrnModal();
            switchView('assessment');
            document.getElementById('studentRefInput').value = existing.id || existing.prn;
            document.getElementById('studentAliasInput').value = existing.alias || '';
            window.EduRiskAnimations.showToast(`Loaded registered student ${existing.name} (${existing.id}) for assessment.`);
          };
        }
      } else {
        // Not found: display registration form
        prnExistingStudentAlert.style.display = 'none';
        newStudentRegForm.style.display = 'block';
        btnSubmitPrnReg.style.display = 'inline-flex';
        document.getElementById('regStudentName').focus();
      }
    });
  }

  if (btnSubmitPrnReg) {
    btnSubmitPrnReg.addEventListener('click', function () {
      const name = (document.getElementById('regStudentName').value || '').trim();
      if (!name) {
        alert('Student full name is required for registration.');
        return;
      }

      const email = (document.getElementById('regEmail').value || '').trim();
      const grade = document.getElementById('regGrade').value;
      const section = (document.getElementById('regSection').value || '').trim() || 'Class 11-A';
      const stream = document.getElementById('regStream').value;
      const batch = (document.getElementById('regBatch').value || '').trim() || '2024–2026';

      const newStudent = {
        id: activeVerifiedPrn,
        prn: activeVerifiedPrn,
        name: name,
        alias: name.split(' ').map(n => n[0]).join('.') + '.',
        email: email,
        grade: grade,
        section: section,
        stream: stream,
        batch: batch,
        attendance: 88.0,
        testScore: 72.0,
        assignmentRate: 85.0,
        studyHours: 9.0,
        riskTier: 'Low Risk',
        assessmentDate: new Date().toISOString().split('T')[0],
        interventionsAssigned: 0,
        interventions: []
      };

      state.studentsList.unshift(newStudent);
      window.EduRiskData.cohortStats.totalStudents += 1;
      closePrnModal();
      renderStudentsDirectory();
      renderDashboardMetrics();
      window.EduRiskAnimations.showToast(`Student ${name} (${activeVerifiedPrn}) registered successfully!`);
    });
  }


  // ==========================================================================
  // 6. STUDENT DETAIL MODAL
  // ==========================================================================

  function openStudentModal(studentId) {
    const student = state.studentsList.find(s => s.id === studentId);
    if (!student) return;

    state.selectedStudentForModal = student;
    const bodyEl = document.getElementById('studentModalBody');
    const titleEl = document.getElementById('studentModalTitle');

    if (titleEl) {
      titleEl.innerHTML = `🎓 ${student.name} <span style="font-size: 0.82rem; color: var(--text-secondary); font-weight: normal;">(${student.id})</span>`;
    }

    const badgeClass = student.riskTier === 'High Risk' ? 'high-risk' :
                       student.riskTier === 'Moderate Risk' ? 'moderate-risk' : 'low-risk';

    bodyEl.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">Cohort: ${student.grade} • ${student.section}</span><br>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Assessed: ${student.assessmentDate}</span>
        </div>
        <span class="risk-badge ${badgeClass}"><span class="risk-dot"></span>${student.riskTier}</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1.5rem; text-align: center;">
        <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); padding: 0.65rem; border-radius: var(--radius-sm);">
          <span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 600;">Attendance</span><br>
          <strong style="font-size: 1.15rem; color: ${student.attendance < 70 ? 'var(--risk-high)' : 'var(--text-heading)'};">${student.attendance}%</strong>
        </div>
        <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); padding: 0.65rem; border-radius: var(--radius-sm);">
          <span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 600;">Test Score</span><br>
          <strong style="font-size: 1.15rem; color: ${student.testScore < 50 ? 'var(--risk-high)' : 'var(--text-heading)'};">${student.testScore}%</strong>
        </div>
        <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); padding: 0.65rem; border-radius: var(--radius-sm);">
          <span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 600;">Assignments</span><br>
          <strong style="font-size: 1.15rem;">${student.assignmentRate}%</strong>
        </div>
        <div style="background-color: var(--bg-main); border: 1px solid var(--border-color); padding: 0.65rem; border-radius: var(--radius-sm);">
          <span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 600;">Study Hours</span><br>
          <strong style="font-size: 1.15rem;">${student.studyHours}h/wk</strong>
        </div>
      </div>

      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.95rem; margin-bottom: 0.4rem;">Assigned Pedagogical Interventions:</h4>
        ${student.interventions.length === 0 ? `
          <p style="font-size: 0.85rem; color: var(--text-secondary);">No active intervention contracts. Student is currently on track.</p>
        ` : `
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${student.interventions.map((intv, idx) => `
              <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-main); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); font-size: 0.85rem;">
                <div>
                  <strong>${intv.title}</strong><br>
                  <span style="font-size: 0.75rem; color: var(--text-secondary);">${intv.type} • Due ${intv.dueDate}</span>
                </div>
                <select class="form-control" style="font-size: 0.75rem; padding: 0.25rem 0.5rem; width: auto;" onchange="EduRiskApp.updateInterventionStatus('${student.id}', ${idx}, this.value)">
                  <option value="Pending" ${intv.status === 'Pending' ? 'selected' : ''}>Pending</option>
                  <option value="In Progress" ${intv.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                  <option value="Completed" ${intv.status === 'Completed' ? 'selected' : ''}>Completed</option>
                </select>
              </div>
            `).join('')}
          </div>
        `}
      </div>

      <div>
        <h4 style="font-size: 0.95rem; margin-bottom: 0.4rem;">Educator Observations & Case Notes:</h4>
        <div style="background: var(--bg-main); border: 1px solid var(--border-color); padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.84rem; color: var(--text-body); font-style: italic;">
          "${student.notes}"
        </div>
      </div>
    `;

    const dialogEl = studentDetailModal.querySelector('.modal-dialog');
    window.EduRiskAnimations.animateModalOpen(studentDetailModal, dialogEl);
  }

  function closeModal() {
    const dialogEl = studentDetailModal.querySelector('.modal-dialog');
    window.EduRiskAnimations.animateModalClose(studentDetailModal, dialogEl);
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (modalDoneBtn) modalDoneBtn.addEventListener('click', closeModal);

  // Close modal on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && studentDetailModal.style.display === 'flex') {
      closeModal();
    }
  });

  // ==========================================================================
  // 7. REPORTS & EXPORTS
  // ==========================================================================

  function renderReportsView() {
    const btnDownloadCsv = document.getElementById('btnDownloadCsv');
    if (btnDownloadCsv) {
      btnDownloadCsv.onclick = function () {
        exportDemoCsv();
      };
    }

    const btnPrintReport = document.getElementById('btnPrintReport');
    if (btnPrintReport) {
      btnPrintReport.onclick = function () {
        window.print();
      };
    }
  }

  function exportDemoCsv() {
    const headers = ['StudentID', 'Name', 'Grade', 'AttendanceRate', 'TestScore', 'AssignmentRate', 'StudyHours', 'RiskTier', 'RecommendedAction'];
    const rows = state.studentsList.map(s => [
      `"${s.id}"`,
      `"${s.name}"`,
      `"${s.grade}"`,
      s.attendance,
      s.testScore,
      s.assignmentRate,
      s.studyHours,
      `"${s.riskTier}"`,
      `"${s.recommendedAction}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `EduRisk_Cohort_Demo_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.EduRiskAnimations.showToast('Downloaded Demonstration CSV report.');
  }

  // ==========================================================================
  // 8. RESEARCH & ADMIN TOOLS (ROLE DEMO)
  // ==========================================================================

  function renderAdminView() {
    const benchmarksTbody = document.getElementById('benchmarkTableTbody');
    if (benchmarksTbody) {
      const data = window.EduRiskData.researchBenchmarks;
      benchmarksTbody.innerHTML = data.map(m => `
        <tr ${m.status.includes('Production') ? 'style="background-color: var(--teal-surface);"' : ''}>
          <td>
            <strong>${m.model}</strong>
            ${m.status.includes('Production') ? '<span class="benchmark-badge-active" style="margin-left: 6px;">Production Active</span>' : ''}
          </td>
          <td><strong>${m.cvMacroF1.toFixed(4)}</strong> <span style="font-size: 0.75rem; color: var(--text-secondary);">(±${m.cvStd.toFixed(4)})</span></td>
          <td><strong>${m.testMacroF1.toFixed(4)}</strong></td>
          <td>${m.testAccuracy.toFixed(2)}%</td>
          <td><strong style="color: var(--teal-primary);">${m.highRiskRecall.toFixed(1)}%</strong></td>
          <td>${m.falseNegatives}</td>
          <td>${m.trainingDuration.toFixed(2)}s</td>
          <td>${m.inferenceLatency.toFixed(2)}ms</td>
        </tr>
      `).join('');
    }

    const rulesTbody = document.getElementById('rulesTableTbody');
    if (rulesTbody) {
      const rules = window.EduRiskData.interventionRules;
      rulesTbody.innerHTML = rules.map(r => `
        <tr>
          <td><code>${r.id}</code></td>
          <td><strong>${r.name}</strong></td>
          <td><code>${r.condition}</code></td>
          <td><span class="risk-badge ${r.priority === 'CRITICAL' ? 'high-risk' : r.priority === 'HIGH' ? 'moderate-risk' : 'low-risk'}">${r.priority}</span></td>
          <td>${r.action}</td>
          <td><span style="font-size: 0.8rem; color: var(--text-secondary);">${r.leadRole}</span></td>
        </tr>
      `).join('');
    }
  }

  // Expose global helper for inline HTML event callbacks
  window.EduRiskApp = {
    updateInterventionStatus: function (studentId, intvIndex, newStatus) {
      const student = state.studentsList.find(s => s.id === studentId);
      if (student && student.interventions[intvIndex]) {
        student.interventions[intvIndex].status = newStatus;
        window.EduRiskAnimations.showToast(`Updated intervention status to: "${newStatus}"`);
      }
    }
  };

  // --- Initial Boot ---
  checkAuthState();
});

