/**
 * app.js — Maison Rouge Smart Expense Tracker
 * Core UI interactions & Live Reactivity:
 *   - Seamless period switching without page reload (Today / Week / Month)
 *   - Smooth number counter live-animations (odometer effect)
 *   - Chart live transition animations
 *   - Dynamic recent expenses and report tables updates
 *   - Category live prediction
 *   - Toast notifications
 *   - Responsive navigation helpers
 */

'use strict';

/* ════════════════════════════════════════════════════════════════════
   1. Live Number Animation (Odometer / Count-Up)
   ════════════════════════════════════════════════════════════════════ */

function animateNumber(element, targetVal, isCurrency = true, duration = 650) {
  if (!element) return;
  const currentVal = parseFloat(element.dataset.value) || 0;
  const target = parseFloat(targetVal) || 0;
  element.dataset.value = target;

  if (isNaN(currentVal) || isNaN(target)) {
    element.textContent = isCurrency ? '₹' + target.toFixed(2) : target.toString();
    return;
  }

  const startTime = performance.now();

  function updateCount(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // easeOutCubic
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = currentVal + (target - currentVal) * ease;

    if (isCurrency) {
      element.textContent = '₹' + val.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    } else {
      element.textContent = Math.round(val).toString();
    }

    if (progress < 1) {
      requestAnimationFrame(updateCount);
    } else {
      if (isCurrency) {
        element.textContent = '₹' + target.toLocaleString('en-IN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
      } else {
        element.textContent = Math.round(target).toString();
      }
    }
  }

  requestAnimationFrame(updateCount);
}

/* ════════════════════════════════════════════════════════════════════
   2. Segmented Control & Non-Refreshing Period Switching
   ════════════════════════════════════════════════════════════════════ */

function initSegmentedControl() {
  const container = document.querySelector('.segmented');
  if (!container) return;

  const buttons = container.querySelectorAll('.segmented-btn');
  const indicator = container.querySelector('.segmented-indicator');
  if (!buttons.length || !indicator) return;

  function moveIndicator(btn) {
    indicator.style.left = btn.offsetLeft + 'px';
    indicator.style.width = btn.offsetWidth + 'px';
  }

  // Set initial position from active button
  const activeBtn = container.querySelector('.segmented-btn.active') || buttons[0];
  requestAnimationFrame(() => moveIndicator(activeBtn));

  buttons.forEach(btn => {
    btn.addEventListener('click', async function () {
      if (this.classList.contains('active')) return;

      buttons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      this.classList.add('active');
      this.setAttribute('aria-pressed', 'true');
      moveIndicator(this);

      const period = this.dataset.period || 'month';
      document.body.dataset.period = period;

      // Update URL without page refresh
      const url = new URL(window.location.href);
      url.searchParams.set('period', period);
      url.searchParams.delete('page');
      window.history.pushState({ period }, '', url.toString());

      // Check if page supports live AJAX updates (Dashboard or Reports)
      const isDashboard = !!document.getElementById('hero-total');
      const isReports   = !!document.getElementById('reports-total-spent');

      if (isDashboard || isReports) {
        await handleLivePeriodChange(period, isDashboard, isReports);
      } else {
        // Fallback for regular paginated views like expense_list
        window.location.href = url.toString();
      }
    });
  });

  // Handle browser back/forward history without reload
  window.addEventListener('popstate', (e) => {
    const params = new URLSearchParams(window.location.search);
    const period = params.get('period') || 'month';
    const targetBtn = container.querySelector(`.segmented-btn[data-period="${period}"]`);
    if (targetBtn) {
      buttons.forEach(b => b.classList.remove('active'));
      targetBtn.classList.add('active');
      moveIndicator(targetBtn);
    }
    const isDashboard = !!document.getElementById('hero-total');
    const isReports   = !!document.getElementById('reports-total-spent');
    if (isDashboard || isReports) {
      handleLivePeriodChange(period, isDashboard, isReports);
    }
  });

  // Reposition indicator on window resize (mobile/tablet/laptop orientation change)
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const current = container.querySelector('.segmented-btn.active');
      if (current) moveIndicator(current);
    }, 80);
  });
}

/* ── Live AJAX Updater for Dashboard & Reports ── */
async function handleLivePeriodChange(period, isDashboard, isReports) {
  // Call the charting engine
  if (typeof window.loadChartsData === 'function') {
    const data = await window.loadChartsData(period);
    if (!data) return;

    if (isDashboard) {
      updateDashboardDOM(data);
    } else if (isReports) {
      updateReportsDOM(data);
    }
  }
}

/* ── Update Dashboard Elements ── */
function updateDashboardDOM(data) {
  // 1. Total spent (animated)
  const heroTotal = document.getElementById('hero-total');
  if (heroTotal) animateNumber(heroTotal, data.total_amount, true);

  // 2. Period text
  const heroPeriod = document.getElementById('hero-period-text');
  if (heroPeriod && data.period_sub) {
    heroPeriod.style.opacity = '0';
    setTimeout(() => {
      heroPeriod.textContent = data.period_sub;
      heroPeriod.style.transition = 'opacity 0.25s ease';
      heroPeriod.style.opacity = '1';
    }, 150);
  }

  // 3. Transactions count (animated)
  const statTx = document.getElementById('stat-transactions');
  if (statTx) animateNumber(statTx, data.transaction_count, false);

  // 4. Top Category
  const statCat = document.getElementById('stat-top-category');
  if (statCat) {
    statCat.style.opacity = '0.3';
    setTimeout(() => {
      statCat.textContent = data.top_category || 'N/A';
      statCat.style.opacity = '1';
    }, 150);
  }

  // 5. Update "View all" link period query param
  const viewAllLink = document.getElementById('link-view-all');
  if (viewAllLink) {
    viewAllLink.href = `/expenses/?period=${data.period}`;
  }

  // 6. Recent expenses list
  const wrapper = document.getElementById('recent-expenses-wrapper');
  if (wrapper && Array.isArray(data.recent_expenses)) {
    if (data.recent_expenses.length === 0) {
      wrapper.innerHTML = `
        <div class="card">
          <div class="empty-state">
            <div class="empty-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>
              </svg>
            </div>
            <h2 class="empty-title">No expenses for ${data.period_display.toLowerCase()}</h2>
            <p class="empty-text">Add your spending to see recent entries here.</p>
            <a href="/expenses/add/" class="btn btn-primary mt-md">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
              Add Expense
            </a>
          </div>
        </div>`;
    } else {
      let rowsHtml = '<div class="expense-list" role="list" id="recent-expenses-list">';
      data.recent_expenses.forEach((e, idx) => {
        const catBadge = e.category_name
          ? `<span class="chip" style="background:${e.category_color}18;color:${e.category_color};">
               <span class="chip-dot" style="background:${e.category_color};"></span>
               ${e.category_name}
             </span>`
          : '';

        rowsHtml += `
          <div class="expense-row" role="listitem" style="animation-delay: ${idx * 40}ms">
            <div class="expense-icon-wrap" style="background:${e.category_color}18;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${e.category_color}" stroke-width="1.8" stroke-linecap="round">
                <rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>
              </svg>
            </div>
            <div class="expense-info">
              <div class="expense-desc">${escapeHtml(e.description)}</div>
              <div class="expense-meta">
                <span class="expense-date">${e.date}</span>
                ${catBadge}
              </div>
            </div>
            <div class="expense-amount">₹${Number(e.amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
            <div class="expense-actions">
              <a href="${e.edit_url}" class="btn-icon" title="Edit" aria-label="Edit ${escapeHtml(e.description)}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </a>
              <a href="${e.delete_url}" class="btn-icon" style="color:var(--error);border-color:rgba(220,38,38,0.2);" title="Delete" aria-label="Delete ${escapeHtml(e.description)}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
                </svg>
              </a>
            </div>
          </div>`;
      });
      rowsHtml += '</div>';
      wrapper.innerHTML = rowsHtml;
    }
  }
}

/* ── Update Reports Elements ── */
function updateReportsDOM(data) {
  // 1. Total spent (animated)
  const repTotal = document.getElementById('reports-total-spent');
  if (repTotal) animateNumber(repTotal, data.total_amount, true);

  // 2. Transactions count (animated)
  const repTx = document.getElementById('reports-transactions');
  if (repTx) animateNumber(repTx, data.transaction_count, false);

  // 3. Header badge & date range
  const repBadge = document.getElementById('reports-badge');
  if (repBadge) repBadge.textContent = data.period_display;

  const repRange = document.getElementById('reports-date-range');
  if (repRange) repRange.textContent = `${data.start_date_str} – ${data.end_date_str}`;

  // 4. Update CSV & PDF buttons with current period
  const csvBtn = document.getElementById('btn-export-csv');
  const pdfBtn = document.getElementById('btn-export-pdf');
  if (csvBtn) csvBtn.href = `/reports/export/csv/?period=${data.period}`;
  if (pdfBtn) pdfBtn.href = `/reports/export/pdf/?period=${data.period}`;

  // 5. Toggle empty state vs data cards
  const hasExpenses = data.transaction_count > 0;
  const chartsRow = document.getElementById('reports-charts-row');
  const catCard   = document.getElementById('reports-category-card');
  const expCard   = document.getElementById('reports-expenses-card');
  const emptyCard = document.getElementById('reports-empty-state');

  if (chartsRow) chartsRow.style.display = hasExpenses ? 'grid' : 'none';
  if (catCard)   catCard.style.display   = hasExpenses ? 'block' : 'none';
  if (expCard)   expCard.style.display   = hasExpenses ? 'block' : 'none';
  if (emptyCard) emptyCard.style.display = hasExpenses ? 'none' : 'block';

  if (!hasExpenses) return;

  // 6. Category breakdown table body
  const catTbody = document.getElementById('reports-category-tbody');
  if (catTbody && Array.isArray(data.category_breakdown)) {
    let catRows = '';
    data.category_breakdown.forEach(row => {
      catRows += `
        <tr>
          <td>
            <div class="flex-row" style="gap:8px;">
              <span class="chip-dot" style="width:8px;height:8px;border-radius:50%;background:${row.color};flex-shrink:0;"></span>
              <span style="font-weight:600;">${escapeHtml(row.name)}</span>
            </div>
            <div class="cat-bar" style="background:${row.color};width:${row.percentage}%"></div>
          </td>
          <td style="color:var(--text-secondary);">${row.count}</td>
          <td class="amount-cell">₹${Number(row.total).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
          <td style="text-align:right;color:var(--text-secondary);">${row.percentage}%</td>
        </tr>`;
    });
    catTbody.innerHTML = catRows;

    const footCount = document.getElementById('reports-category-foot-count');
    const footTotal = document.getElementById('reports-category-foot-total');
    if (footCount) footCount.textContent = data.transaction_count;
    if (footTotal) footTotal.textContent = '₹' + Number(data.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  // 7. All expenses table body
  const expTbody = document.getElementById('reports-expenses-tbody');
  if (expTbody && Array.isArray(data.all_expenses)) {
    let expRows = '';
    data.all_expenses.forEach(e => {
      const catBadge = e.category_name
        ? `<span class="chip" style="background:${e.category_color}18;color:${e.category_color};">
             <span class="chip-dot" style="background:${e.category_color};"></span>
             ${escapeHtml(e.category_name)}
           </span>`
        : '<span style="color:var(--text-secondary);">—</span>';

      expRows += `
        <tr>
          <td style="color:var(--text-secondary);white-space:nowrap;">${e.date}</td>
          <td style="font-weight:500;">${escapeHtml(e.description)}</td>
          <td>${catBadge}</td>
          <td class="amount-cell">₹${Number(e.amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
        </tr>`;
    });
    expTbody.innerHTML = expRows;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* ════════════════════════════════════════════════════════════════════
   3. Toast Notifications (Dynamic-Island style)
   ════════════════════════════════════════════════════════════════════ */

function initToasts() {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    const totalMs = 3850;
    setTimeout(() => {
      toast.addEventListener('animationend', () => {
        toast.remove();
      }, { once: true });
      setTimeout(() => toast.remove(), 500);
    }, totalMs - 500);
  });
}

/* ════════════════════════════════════════════════════════════════════
   4. Live Category Prediction
   ════════════════════════════════════════════════════════════════════ */

function initCategoryPredictor() {
  const descInput = document.getElementById('id_description');
  const categorySelect = document.getElementById('id_category');
  const badgeContainer = document.getElementById('prediction-badge');

  if (!descInput || !categorySelect) return;

  let debounceTimer = null;

  descInput.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const query = this.value.trim();

    if (query.length < 3) {
      hideBadge();
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const response = await fetch(
          `/api/predict-category/?q=${encodeURIComponent(query)}`
        );
        const data = await response.json();

        if (data.category) {
          const option = Array.from(categorySelect.options).find(
            opt => opt.text.toLowerCase() === data.category.toLowerCase()
          );
          if (option) {
            const currentVal = categorySelect.value;
            const isBlank = !currentVal || currentVal === '';
            if (isBlank) {
              categorySelect.value = option.value;
            }
            showBadge(data.category);
          }
        }
      } catch (err) {
        console.warn('Category prediction failed:', err);
      }
    }, 320);
  });

  function showBadge(categoryName) {
    if (!badgeContainer) return;
    badgeContainer.innerHTML = `
      <span class="badge-suggested">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        Suggested: ${categoryName}
      </span>
    `;
    badgeContainer.style.display = 'block';
  }

  function hideBadge() {
    if (badgeContainer) {
      badgeContainer.style.display = 'none';
      badgeContainer.innerHTML = '';
    }
  }

  categorySelect.addEventListener('change', hideBadge);
}

/* ════════════════════════════════════════════════════════════════════
   5. General Form Enhancements
   ════════════════════════════════════════════════════════════════════ */

function initForms() {
  const inputs = document.querySelectorAll('.form-input');
  inputs.forEach(input => {
    function checkValue() {
      if (input.value !== '') {
        input.classList.add('has-value');
      } else {
        input.classList.remove('has-value');
      }
    }
    checkValue();
    input.addEventListener('input', checkValue);
    input.addEventListener('change', checkValue);
  });

  const forms = document.querySelectorAll('form[data-loading]');
  forms.forEach(form => {
    form.addEventListener('submit', function () {
      const btn = this.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loader"></span> Saving…';
      }
    });
  });
}

/* ════════════════════════════════════════════════════════════════════
   6. Active Tab Highlighting
   ════════════════════════════════════════════════════════════════════ */

function initTabBar() {
  const currentPath = window.location.pathname;
  const tabItems = document.querySelectorAll('.tab-item[data-path]');
  tabItems.forEach(tab => {
    const path = tab.dataset.path;
    if (path && (currentPath === path || currentPath.startsWith(path + '/'))) {
      tab.classList.add('active');
    }
  });
}

/* ════════════════════════════════════════════════════════════════════
   Boot Application
   ════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initSegmentedControl();
  initToasts();
  initCategoryPredictor();
  initForms();
  initTabBar();
});
