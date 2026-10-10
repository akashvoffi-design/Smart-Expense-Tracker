/**
 * charts.js — Maison Rouge Smart Expense Tracker
 *
 * Professional Chart.js integration with:
 *   - Category Breakdown (Doughnut Chart with percentage tooltips & custom legend)
 *   - Spending Over Time (Daily Bar / Gradient Area Line Chart)
 *   - Live dataset updates & smooth animation transitions without page refresh
 *   - Non-destructive empty-state overlay
 *   - Responsive sizing for Laptop, Tablet, and Mobile viewports
 */

'use strict';

/* ── Global Chart.js Instances ── */
let doughnutChart = null;
let timeChart = null;

/* ── Chart.js Defaults ── */
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = '#6B6B6B';
  Chart.defaults.plugins.legend.labels.boxWidth = 10;
  Chart.defaults.plugins.legend.labels.borderRadius = 999;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26,26,26,0.92)';
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 12;
  Chart.defaults.plugins.tooltip.titleFont = { weight: '700', size: 13, family: "'Inter', sans-serif" };
  Chart.defaults.plugins.tooltip.bodyFont  = { size: 12, family: "'Inter', sans-serif" };
  Chart.defaults.animation.duration = 750;
  Chart.defaults.animation.easing = 'easeOutQuart';
}

/* ── Currency Formatter Helper ── */
function formatCurrency(n) {
  return '₹' + Number(n || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/* ── Empty Overlay Helper ── */
function setChartEmptyState(wrapElement, isEmpty, message = 'No data for this period') {
  if (!wrapElement) return;
  let overlay = wrapElement.querySelector('.chart-empty-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'chart-empty-overlay';
    overlay.innerHTML = `
      <div class="empty-icon" style="width:40px;height:40px;border-radius:50%;background:rgba(179,0,27,0.06);display:flex;align-items:center;justify-content:center;color:#B3001B;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4l2 2"/>
        </svg>
      </div>
      <p style="font-size:12px;font-weight:600;color:var(--text-secondary);margin:0;">${message}</p>
    `;
    wrapElement.appendChild(overlay);
  }

  const canvas = wrapElement.querySelector('canvas');
  if (isEmpty) {
    overlay.classList.add('active');
    overlay.style.display = 'flex';
    if (canvas) canvas.style.opacity = '0.15';
  } else {
    overlay.classList.remove('active');
    overlay.style.display = 'none';
    if (canvas) canvas.style.opacity = '1';
  }
}

/* ── 1. Doughnut Chart: Category Breakdown ── */
function renderOrUpdateDoughnut(canvas, labels, data, colors) {
  if (!canvas) return;
  const wrap = canvas.closest('.chart-wrap');
  const hasData = Array.isArray(data) && data.length > 0 && data.some(v => v > 0);

  if (!hasData) {
    setChartEmptyState(wrap, true, 'No spending in this period');
    if (doughnutChart) {
      doughnutChart.data.labels = ['No Data'];
      doughnutChart.data.datasets[0].data = [1];
      doughnutChart.data.datasets[0].backgroundColor = ['#EAE5E5'];
      doughnutChart.update();
    }
    return;
  }

  setChartEmptyState(wrap, false);

  if (doughnutChart) {
    doughnutChart.data.labels = labels;
    doughnutChart.data.datasets[0].data = data;
    doughnutChart.data.datasets[0].backgroundColor = colors;
    doughnutChart.update();
    return;
  }

  doughnutChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverOffset: 10,
        hoverBorderColor: '#ffffff',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 9,
            font: { size: 11, weight: '600' },
          },
        },
        tooltip: {
          callbacks: {
            label: function (ctx) {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : '0';
              return `  ${ctx.label}: ${formatCurrency(ctx.parsed)} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

/* ── 2. Time-Series Chart: Daily Spending ── */
function renderOrUpdateTimeSeries(canvas, labels, data) {
  if (!canvas) return;
  const wrap = canvas.closest('.chart-wrap');
  const hasData = Array.isArray(data) && data.length > 0 && data.some(v => v > 0);

  if (!hasData) {
    setChartEmptyState(wrap, true, 'No spending recorded');
    if (timeChart) {
      timeChart.data.labels = ['No Data'];
      timeChart.data.datasets[0].data = [0];
      timeChart.update();
    }
    return;
  }

  setChartEmptyState(wrap, false);

  // Gradient background fill for area chart
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, 'rgba(179, 0, 27, 0.28)');
  gradient.addColorStop(0.7, 'rgba(179, 0, 27, 0.05)');
  gradient.addColorStop(1, 'rgba(179, 0, 27, 0.00)');

  const chartType = labels.length <= 7 ? 'bar' : 'line';

  if (timeChart) {
    timeChart.data.labels = labels;
    timeChart.data.datasets[0].data = data;
    timeChart.data.datasets[0].type = chartType;
    timeChart.data.datasets[0].fill = chartType === 'line';
    timeChart.update();
    return;
  }

  timeChart = new Chart(canvas, {
    type: chartType,
    data: {
      labels,
      datasets: [{
        label: 'Daily Spending',
        data,
        backgroundColor: chartType === 'bar' ? 'rgba(179, 0, 27, 0.85)' : gradient,
        borderColor: '#B3001B',
        borderWidth: chartType === 'bar' ? 0 : 2.5,
        borderRadius: 8,
        pointBackgroundColor: '#B3001B',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: labels.length > 15 ? 3 : 5,
        pointHoverRadius: 7,
        fill: chartType === 'line',
        tension: 0.35,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: {
            font: { size: 11, weight: '500' },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 10,
          },
        },
        y: {
          grid: {
            color: 'rgba(26, 26, 26, 0.06)',
            drawTicks: false,
          },
          border: { display: false, dash: [4, 4] },
          ticks: {
            font: { size: 11 },
            callback: (v) => '₹' + v.toLocaleString('en-IN'),
            maxTicksLimit: 6,
          },
          beginAtZero: true,
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `  ${formatCurrency(ctx.parsed.y)}`,
          },
        },
      },
    },
  });
}

/* ── Live Chart Loader ── */
async function loadChartsData(period) {
  applyChartDefaults();

  const doughnutCanvas = document.getElementById('chart-doughnut');
  const timeCanvas     = document.getElementById('chart-timeseries');

  if (!doughnutCanvas && !timeCanvas) return null;

  const currentPeriod = period
    || document.body.dataset.period
    || new URLSearchParams(window.location.search).get('period')
    || 'month';

  try {
    const resp = await fetch(`/api/chart-data/?period=${currentPeriod}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const json = await resp.json();

    if (doughnutCanvas && json.doughnut) {
      renderOrUpdateDoughnut(
        doughnutCanvas,
        json.doughnut.labels,
        json.doughnut.data,
        json.doughnut.colors
      );
    }

    if (timeCanvas && json.timeseries) {
      renderOrUpdateTimeSeries(
        timeCanvas,
        json.timeseries.labels,
        json.timeseries.data
      );
    }

    return json;
  } catch (err) {
    console.error('Failed to load chart data:', err);
    return null;
  }
}

// Expose globally for app.js live updates
window.loadChartsData = loadChartsData;

document.addEventListener('DOMContentLoaded', () => {
  loadChartsData();
});
