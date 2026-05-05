const appSelect = document.getElementById('appSelect');
const fetchAppsBtn = document.getElementById('fetchAppsBtn');
const collectBtn = document.getElementById('collectBtn');
const toast = document.getElementById('toast');

let trendChart;

function apiBase() {
  return "http://127.0.0.1:8000";
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3800);
}

function request(path, options = {}) {
  const res = fetch(`${apiBase()}${path}`, options);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function checkBackend() {
  try {
    const data = request('/');
    document.getElementById('backendStatus').textContent = data.message ? 'Online' : 'Online';
  } catch (e) {
    document.getElementById('backendStatus').textContent = 'Offline / CORS issue';
  }
}

function loadApps() {
  appSelect.innerHTML = '<option value="">Loading apps...</option>';

  try {
    const apps = request('/apps/');

    if (!apps.length) {
      appSelect.innerHTML = '<option value="">No apps yet, click Fetch Top 100</option>';
      return;
    }

    appSelect.innerHTML = apps
      .map(app => `
        <option value="${app.app_id}">
          ${app.rank ? app.rank + '. ' : ''}${app.app_name}
          ${app.category ? ' — ' + app.category : ''}
        </option>
      `)
      .join('');

    loadDashboard(appSelect.value);
  } catch (e) {
    appSelect.innerHTML = '<option value="">Cannot load apps</option>';
    showToast('Cannot load app list. Please start backend first.');
  }
}

async function fetchTop100() {
  fetchAppsBtn.disabled = true;
  fetchAppsBtn.textContent = 'Fetching...';

  try {
    const data = await request('/apps/fetch-top100', { method: 'POST' });
    showToast(`Fetched ${data.saved_count || 0} apps. Total: ${data.total_apps || 0}`);
    await loadApps();
  } catch (e) {
    showToast('Fetch Top 100 failed. Check backend terminal.');
  } finally {
    fetchAppsBtn.disabled = false;
    fetchAppsBtn.textContent = 'Fetch Top 100';
  }
}

function collectReviews() {
  const appId = appSelect.value;

  if (!appId) {
    return showToast('Please select an app first.');
  }

  collectBtn.disabled = true;
  collectBtn.textContent = 'Collecting...';

  try {
    const months = document.getElementById('monthsBack').value;
    const perMonth = document.getElementById('reviewsPerMonth').value;

    const data = request(
      `/reviews/collect/${encodeURIComponent(appId)}?months_back=${months}&reviews_per_month=${perMonth}`,
      { method: 'POST' }
    );

    showToast(`Collected ${data.collected_count || 0} reviews for ${data.app_name || appId}`);

  } catch (e) {
    showToast('Review collection failed or took too long. Try fewer months/reviews.');
  } finally {
    collectBtn.disabled = false;
    collectBtn.textContent = 'Collect Reviews';
  }

  loadDashboard(appId);
}

function loadDashboard(appId) {
  if (!appId) return;

  try {
    const data = request(`/dashboard/${encodeURIComponent(appId)}`);

    if (data.error) {
      return showToast(data.error);
    }

    renderDashboard(data);
  } catch (e) {
    showToast('Dashboard data not ready. Collect reviews for this app first.');
  }
}

function renderDashboard(data) {
  const trend = data.trend_last_12_months || [];

  const totalPositive = trend.reduce((s, m) => s + Number(m.positive_count || 0), 0);
  const totalNegative = trend.reduce((s, m) => s + Number(m.negative_count || 0), 0);
  const total = totalPositive + totalNegative;

  document.getElementById('currentApp').textContent = data.app_name || '-';
  document.getElementById('totalReviews').textContent = total;
  document.getElementById('positiveReviews').textContent = totalPositive;
  document.getElementById('negativeReviews').textContent = totalNegative;
  document.getElementById('positiveRate').textContent =
    total ? `${Math.round((totalPositive / total) * 100)}%` : '-';

  renderTrendChart(trend);

  const rec = data.recommendation || {};
  document.getElementById('recommendationText').textContent =
    rec.recommendation || 'No recommendation generated yet.';

  document.getElementById('cacheBadge').textContent =
    rec.from_cache
      ? `Cached ${rec.generated_date || ''}`
      : `Generated ${rec.generated_date || ''}`;

  const reviews = data.sampled_reviews_last_28_days || [];

  document.getElementById('reviewsList').innerHTML = reviews.length
    ? reviews.map(r => `
      <article class="review-item">
        <div class="review-meta">
          <span class="pill ${r.sentiment_label}">${r.sentiment_label || 'unknown'}</span>
          <span class="pill">★ ${r.score || '-'}</span>
          <span class="pill">${r.review_date || '-'}</span>
          <span class="pill">confidence ${Number(r.sentiment_score || 0).toFixed(2)}</span>
        </div>
        <p>${escapeHtml(r.content || '')}</p>
      </article>
    `).join('')
    : '<p>No recent sampled reviews yet.</p>';
}

function renderTrendChart(trend) {
  const ctx = document.getElementById('trendChart');

  if (trendChart) {
    trendChart.destroy();
  }

  const positiveData = trend.map(m => Number(m.positive_count || 0));
  const negativeData = trend.map(m => Number(m.negative_count || 0));

  const maxValue = Math.max(...positiveData, ...negativeData, 10);
  const yMax = Math.ceil(maxValue * 1.2);

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: trend.map(m => m.month),
      datasets: [
        {
          label: 'Positive',
          data: positiveData,
          tension: 0.25,
          borderWidth: 3,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Negative',
          data: negativeData,
          tension: 0.25,
          borderWidth: 3,
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.dataset.label}: ${context.raw} reviews`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: yMax,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}

function escapeHtml(str) {
  return String(str).replace(/[&<>'"]/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[c]));
}

fetchAppsBtn.addEventListener('click', fetchTop100);
collectBtn.addEventListener('click', collectReviews);
appSelect.addEventListener('change', e => loadDashboard(e.target.value));

checkBackend();
loadApps();