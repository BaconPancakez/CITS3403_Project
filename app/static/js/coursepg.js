(function () {
    const input = document.getElementById("noteSearchInput");
    const clearBtn = document.getElementById("noteSearchClear");
    const empty = document.getElementById("noteSearchEmpty");

    if (!input) return;

    function filter() {
        const q = input.value.trim().toLowerCase();
        const cards = document.querySelectorAll(".note-card");
        let shown = 0;

        cards.forEach(function (card) {
            const title = card.getAttribute("data-note-title") || "";
            const uploader = card.getAttribute("data-note-uploader") || "";
            const details = card.getAttribute("data-note-details") || "";
            const match = !q || title.includes(q) || uploader.includes(q) || details.includes(q);

            card.style.display = match ? "" : "none";
            if (match) shown++;
        });

        clearBtn.style.display = q ? "inline-flex" : "none";
        empty.style.display = (q && shown === 0) ? "block" : "none";
    }

    input.addEventListener("input", filter);

    clearBtn.addEventListener("click", function () {
        input.value = "";
        filter();
        input.focus();
    });
}());

(function () {
    const VISIBLE_DEFAULT = 4;

    const list = document.getElementById("reviewList");
    const toggleBtn = document.getElementById("reviewToggleBtn");
    const sortBtns = document.querySelectorAll(".review-sort-btn");
    const barRows = document.querySelectorAll(".review-bar-row");
    const reviewForm = document.querySelector('form:has(textarea[name="review_text"])');
    const reviewTextarea = reviewForm ? reviewForm.querySelector('textarea[name="review_text"]') : null;
    const reviewDraftPreview = document.getElementById("reviewDraftPreview");
    const reviewDraftText = document.getElementById("reviewDraftText");

    if (!list) return;

    let currentSort = "newest";
    let currentStar = 0;      // 0 = all
    let expanded = false;

    // ── Collect review items ──────────────────────────────────────────────
    function items() {
        return [...list.querySelectorAll(".review-item")];
    }

    // ── Sort ──────────────────────────────────────────────────────────────
    function sorted(arr) {
        return [...arr].sort(function (a, b) {
            const ra = parseInt(a.dataset.rating, 10);
            const rb = parseInt(b.dataset.rating, 10);
            const ca = parseInt(a.dataset.created, 10);
            const cb = parseInt(b.dataset.created, 10);
            if (currentSort === "highest") return rb - ra || cb - ca;
            if (currentSort === "lowest") return ra - rb || cb - ca;
            return cb - ca;
        });
    }

    // ── Re-render ─────────────────────────────────────────────────────────
    function render() {
        const all = items();
        const filtered = currentStar
            ? all.filter(el => parseInt(el.dataset.rating, 10) === currentStar)
            : all;
        const ordered = sorted(filtered);

        all.forEach(el => { el.style.display = "none"; });
        ordered.forEach(function (el, i) {
            list.appendChild(el);
            el.style.display = (!expanded && i >= VISIBLE_DEFAULT) ? "none" : "";
        });

        // Toggle button
        if (toggleBtn) {
            if (ordered.length <= VISIBLE_DEFAULT) {
                toggleBtn.style.display = "none";
            } else if (expanded) {
                toggleBtn.textContent = "Show fewer";
                toggleBtn.style.display = "";
            } else {
                toggleBtn.textContent = `Show all ${ordered.length} reviews`;
                toggleBtn.style.display = "";
            }
        }

        // Highlight active bar
        barRows.forEach(function (row) {
            const star = parseInt(row.dataset.star, 10);
            const active = currentStar === star;
            const fill = row.querySelector(".review-bar-fill");

            row.style.background = active
                ? "rgba(245, 158, 11, 0.12)"
                : "";
            if (fill) fill.style.background = active ? "#d97706" : "#f59e0b";
        });
    }

    // ── Sort buttons ──────────────────────────────────────────────────────
    sortBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            currentSort = this.dataset.sort;
            sortBtns.forEach(b => {
                b.classList.toggle("btn-primary", b === this);
                b.classList.toggle("btn-outline-secondary", b !== this);
            });
            render();
        }.bind(btn));
    });

    // ── Bar row clicks ────────────────────────────────────────────────────
    barRows.forEach(function (row) {
        row.addEventListener("click", function () {
            const star = parseInt(this.dataset.star, 10);
            // Clicking the active filter again clears it
            currentStar = (currentStar === star) ? 0 : star;
            expanded = false;
            render();
        });
    });

    // ── Show more / fewer ─────────────────────────────────────────────────
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            expanded = !expanded;
            render();
        });
    }

    // ── Initial render ────────────────────────────────────────────────────
    render();

    if (reviewTextarea && reviewDraftPreview && reviewDraftText) {
        const syncReviewDraft = function () {
            const text = reviewTextarea.value.trim();
            reviewDraftText.textContent = text;
            reviewDraftPreview.classList.toggle("d-none", text.length === 0);
        };

        reviewTextarea.addEventListener("input", syncReviewDraft);
        syncReviewDraft();
    }

}());
