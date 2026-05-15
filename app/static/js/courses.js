
(() => {
    const BATCH = 80;

const input = document.getElementById('course-search');
const selects = document.querySelectorAll('.filter-select');
const form = document.getElementById('course-search-form');
if (!form) return;

const favoritesSection = document.getElementById('favorite-units-section');
const favoritesBody = document.getElementById('favorite-units-body');
const allBody = document.getElementById('all-units-body');

// ── Build show-more UI dynamically (JS-only feature) ─────────────
const showMoreContainer = document.createElement('div');
showMoreContainer.className = 'mt-3 text-center';

const showMoreStatus = document.createElement('p');
showMoreStatus.className = 'text-muted small mb-2';

const showMoreBtn = document.createElement('button');
showMoreBtn.className = 'btn btn-outline-primary px-5';
showMoreBtn.textContent = 'Show more units';

showMoreContainer.appendChild(showMoreStatus);
showMoreContainer.appendChild(showMoreBtn);
allBody.closest('.table-responsive').after(showMoreContainer);

// ── Row visibility ────────────────────────────────────────────────

function applyBatch() {
        const rows = allBody.querySelectorAll('tr');
        rows.forEach((row, i) => {
    row.style.display = i < BATCH ? '' : 'none';
        });
syncUI();
    }

const clearBtn = document.getElementById('clear-btn');

function syncClearBtn() {
        const hasText = (input ? input.value.trim() : '') !== '';
        const hasFilter = [...selects].some(sel => sel.value !== '');
if (clearBtn) clearBtn.style.display = (hasText || hasFilter) ? '' : 'none';
    }

function syncUI() {
        const rows = allBody.querySelectorAll('tr');
const total = rows.length;
        const visible = [...rows].filter(r => r.style.display !== 'none').length;
        showMoreStatus.textContent = total > 0 ? `Showing ${visible} of ${total} units` : '';
showMoreBtn.style.display = visible < total ? '' : 'none';
    }

    showMoreBtn.addEventListener('click', () => {
        const rows = allBody.querySelectorAll('tr');
let shown = 0;
        rows.forEach(row => {
            if (row.style.display === 'none' && shown < BATCH) {
    row.style.display = '';
shown++;
            }
        });
syncUI();
    });

// ── Live search ───────────────────────────────────────────────────

let t = null;
let controller = null;

    const renderFrom = (doc) => {
        const newFavSec = doc.getElementById('favorite-units-section');
const newFavBody = doc.getElementById('favorite-units-body');
const newAllBody = doc.getElementById('all-units-body');

if (newAllBody && allBody) allBody.innerHTML = newAllBody.innerHTML;
if (newFavBody && favoritesBody) favoritesBody.innerHTML = newFavBody.innerHTML;
if (newFavSec && favoritesSection) {
    favoritesSection.style.display =
    newFavSec.getAttribute('style')?.includes('display:none') ? 'none' : '';
        }
// Reset to first batch after every search/filter change
applyBatch();
    };

    const liveSearch = async () => {
        const url = new URL(form.action, window.location.origin);
const q = (input ? input.value : '').trim();
if (q) url.searchParams.set('q', q);
        selects.forEach(sel => {
            if (sel.value) url.searchParams.set(sel.name, sel.value);
        });

if (controller) controller.abort();
controller = new AbortController();

try {
            const res = await fetch(url.toString(), {
    signal: controller.signal,
headers: {'X-Requested-With': 'fetch' },
            });
if (!res.ok) return;
const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
renderFrom(doc);
window.history.replaceState({ }, '', url.pathname + url.search);
        } catch (_) {
    // ignore aborts / transient errors
}
    };

if (input) {
    input.addEventListener('input', () => {
        if (t) clearTimeout(t);
        syncClearBtn();
        t = setTimeout(liveSearch, 180);
    });
    }
    selects.forEach(sel => {
    sel.addEventListener('change', () => {
        if (t) clearTimeout(t);
        syncClearBtn();
        t = setTimeout(liveSearch, 180);
    });
    });

// ── Init ──────────────────────────────────────────────────────────
applyBatch();
syncClearBtn();
})();