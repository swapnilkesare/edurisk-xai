/**
 * EduRisk XAI — Anime.js Animation Controller
 * 
 * Purposeful, subtle micro-animations for page transitions, card staggering,
 * counter animations, step transitions, and accessible reduced-motion support.
 */

window.EduRiskAnimations = (function () {
  // Check user preference for reduced motion
  const prefersReducedMotion = () => {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  // Safe Anime.js invoker with fallback if library fails to load
  const runAnime = (params) => {
    if (prefersReducedMotion()) {
      // Execute complete callback immediately if provided
      if (typeof params.complete === 'function') {
        params.complete();
      }
      return null;
    }
    if (typeof window.anime === 'function') {
      return window.anime(params);
    }
    // Fallback if anime is unavailable
    if (typeof params.complete === 'function') {
      setTimeout(params.complete, params.duration || 200);
    }
    return null;
  };

  return {
    isReducedMotion: prefersReducedMotion,

    /**
     * Animate smooth page transition between views
     */
    animatePageTransition: function (targetViewElement) {
      if (!targetViewElement) return;
      if (prefersReducedMotion()) {
        targetViewElement.style.opacity = '1';
        targetViewElement.style.transform = 'none';
        return;
      }

      runAnime({
        targets: targetViewElement,
        opacity: [0, 1],
        translateY: [8, 0],
        easing: 'easeOutQuad',
        duration: 220
      });
    },

    /**
     * Staggered entrance for summary metric cards and list items
     */
    animateStaggerCards: function (cardSelectorOrElements) {
      if (prefersReducedMotion()) return;

      runAnime({
        targets: cardSelectorOrElements,
        opacity: [0, 1],
        translateY: [10, 0],
        delay: window.anime ? window.anime.stagger(50, { start: 60 }) : 50,
        easing: 'easeOutQuad',
        duration: 260
      });
    },

    /**
     * Eased count-up animation for numeric metric counters
     */
    animateCountUp: function (element, targetValue, duration = 650) {
      if (!element) return;
      if (prefersReducedMotion() || typeof window.anime !== 'function') {
        element.textContent = targetValue;
        return;
      }

      const isFloat = String(targetValue).includes('.');
      const counterObj = { val: 0 };

      runAnime({
        targets: counterObj,
        val: parseFloat(targetValue) || 0,
        round: isFloat ? 10 : 1,
        easing: 'easeOutCubic',
        duration: duration,
        update: function () {
          element.textContent = isFloat ? counterObj.val.toFixed(1) : Math.round(counterObj.val);
        }
      });
    },

    /**
     * Smooth stepper progress bar transition
     */
    animateProgressBar: function (fillElement, targetPercent) {
      if (!fillElement) return;
      if (prefersReducedMotion()) {
        fillElement.style.width = targetPercent + '%';
        return;
      }

      runAnime({
        targets: fillElement,
        width: targetPercent + '%',
        easing: 'easeOutQuad',
        duration: 320
      });
    },

    /**
     * Smooth transition between wizard form steps
     */
    animateStepSlide: function (currentStepEl, nextStepEl, direction = 'forward') {
      if (prefersReducedMotion()) {
        if (currentStepEl) {
          currentStepEl.classList.remove('active-step');
          currentStepEl.style.display = 'none';
        }
        if (nextStepEl) {
          nextStepEl.classList.add('active-step');
          nextStepEl.style.display = 'block';
        }
        return;
      }

      const offset = direction === 'forward' ? 14 : -14;

      if (currentStepEl) {
        runAnime({
          targets: currentStepEl,
          opacity: [1, 0],
          translateX: [0, -offset],
          easing: 'easeInQuad',
          duration: 160,
          complete: function () {
            currentStepEl.classList.remove('active-step');
            currentStepEl.style.display = 'none';

            if (nextStepEl) {
              nextStepEl.style.display = 'block';
              nextStepEl.classList.add('active-step');
              runAnime({
                targets: nextStepEl,
                opacity: [0, 1],
                translateX: [offset, 0],
                easing: 'easeOutQuad',
                duration: 200
              });
            }
          }
        });
      } else if (nextStepEl) {
        nextStepEl.style.display = 'block';
        nextStepEl.classList.add('active-step');
        runAnime({
          targets: nextStepEl,
          opacity: [0, 1],
          translateX: [offset, 0],
          easing: 'easeOutQuad',
          duration: 200
        });
      }
    },

    /**
     * Modal Pop-in & Backdrop Fade
     */
    animateModalOpen: function (overlayEl, dialogEl) {
      if (!overlayEl || !dialogEl) return;
      overlayEl.style.display = 'flex';

      if (prefersReducedMotion()) {
        overlayEl.style.opacity = '1';
        dialogEl.style.opacity = '1';
        dialogEl.style.transform = 'none';
        return;
      }

      runAnime({
        targets: overlayEl,
        opacity: [0, 1],
        easing: 'linear',
        duration: 160
      });

      runAnime({
        targets: dialogEl,
        opacity: [0, 1],
        scale: [0.94, 1],
        translateY: [10, 0],
        easing: 'easeOutQuad',
        duration: 220
      });
    },

    /**
     * Modal Close
     */
    animateModalClose: function (overlayEl, dialogEl, callback) {
      if (!overlayEl || !dialogEl) {
        if (callback) callback();
        return;
      }

      if (prefersReducedMotion()) {
        overlayEl.style.display = 'none';
        if (callback) callback();
        return;
      }

      runAnime({
        targets: dialogEl,
        opacity: [1, 0],
        scale: [1, 0.96],
        easing: 'easeInQuad',
        duration: 140
      });

      runAnime({
        targets: overlayEl,
        opacity: [1, 0],
        easing: 'linear',
        duration: 160,
        complete: function () {
          overlayEl.style.display = 'none';
          if (callback) callback();
        }
      });
    },

    /**
     * Notification Toast slide-in and dismiss
     */
    showToast: function (message, duration = 3000) {
      let container = document.getElementById('toastContainer');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.innerHTML = `<span>🔔</span> <div>${message}</div>`;
      container.appendChild(toast);

      if (prefersReducedMotion()) {
        setTimeout(() => {
          if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, duration);
        return;
      }

      runAnime({
        targets: toast,
        opacity: [0, 1],
        translateX: [40, 0],
        easing: 'easeOutQuad',
        duration: 240
      });

      setTimeout(() => {
        runAnime({
          targets: toast,
          opacity: [1, 0],
          translateX: [0, 30],
          easing: 'easeInQuad',
          duration: 200,
          complete: function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
          }
        });
      }, duration);
    },

    /**
     * Animate SVG or Chart Bar entrance
     */
    animateChartBars: function (barsSelector) {
      if (prefersReducedMotion()) return;

      runAnime({
        targets: barsSelector,
        scaleY: [0, 1],
        opacity: [0.3, 1],
        delay: window.anime ? window.anime.stagger(40) : 40,
        easing: 'easeOutQuad',
        duration: 380,
        transformOrigin: '50% 100%'
      });
    }
  };
})();
