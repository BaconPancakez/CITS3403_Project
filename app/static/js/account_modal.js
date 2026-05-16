(function () {

    const modal = document.getElementById("accountModal");
    if (!modal) return;

    const statsUrl = modal.dataset.accountStatsUrl;
    const updateUrl = modal.dataset.accountUpdateUrl;

    // ── Element refs ──────────────────────────────────────────────────────
    const avatar = document.getElementById("accountAvatar");
    const displayName = document.getElementById("accountDisplayName");
    const emailEl = document.getElementById("accountEmail");
    const memberSince = document.getElementById("accountMemberSince");
    const statsGrid = document.getElementById("accountStatsGrid");
    const nameInput = document.getElementById("accountNameInput");
    const nameForm = document.getElementById("accountNameForm");
    const nameFeedback = document.getElementById("accountNameFeedback");
    const nameSaveBtn = document.getElementById("accountNameSaveBtn");

    // Delete flow
    const step1 = document.getElementById("deleteStep1");
    const step2 = document.getElementById("deleteStep2");
    const showDeleteBtn = document.getElementById("showDeleteConfirm");
    const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
    const deleteInput = document.getElementById("deleteConfirmInput");
    const confirmBtn = document.getElementById("confirmDeleteBtn");

    // ── Stat definitions ──────────────────────────────────────────────────
    const STATS = [
        { key: "notes", icon: "📄", label: "Notes" },
        { key: "reviews", icon: "⭐", label: "Reviews" },
        { key: "quizzes", icon: "🧠", label: "Quizzes" },
        { key: "posts", icon: "💬", label: "Posts" },
        { key: "favourites", icon: "❤️", label: "Favourites" },
    ];

    // ── Load stats via fetch ──────────────────────────────────────────────
    function loadStats() {
        fetch(statsUrl)
            .then(r => r.json())
            .then(data => {
                // Avatar initials
                const initials = (data.name || data.email || "?")
                    .trim().charAt(0).toUpperCase();
                avatar.textContent = initials;

                // Identity
                displayName.textContent = data.name || "—";
                emailEl.textContent = data.email || "—";
                memberSince.textContent = data.member_since
                    ? "Member since " + data.member_since
                    : "";

                // Pre-fill name input
                nameInput.value = data.name || "";

                // Stats grid — build 5 cells (last row spans if odd)
                statsGrid.innerHTML = "";
                STATS.forEach(function (s, i) {
                    const col = document.createElement("div");
                    col.className = i === 4 ? "col-12" : "col-6";

                    const inner = document.createElement("div");
                    inner.className = "text-center p-2 rounded";
                    inner.style.background = "var(--bs-tertiary-bg, #f8f9fa)";

                    inner.innerHTML = `
                        <div style="font-size:1.25rem;">${s.icon}</div>
                        <div class="fw-bold" style="font-size:1.1rem; line-height:1.2;">
                            ${data[s.key] ?? 0}
                        </div>
                        <div class="text-muted" style="font-size:0.68rem; letter-spacing:0.04em;">
                            ${s.label.toUpperCase()}
                        </div>`;

                    col.appendChild(inner);
                    statsGrid.appendChild(col);
                });
            })
            .catch(function () {
                displayName.textContent = "Error loading data";
            });
    }

    // Reload on open
    modal.addEventListener("show.bs.modal", function () {
        // Reset delete flow
        step1.style.display = "";
        step2.style.display = "none";
        if (deleteInput) deleteInput.value = "";
        if (confirmBtn) confirmBtn.disabled = true;
        nameFeedback.textContent = "";
        loadStats();
    });

    // ── Name update (AJAX) ────────────────────────────────────────────────
    if (nameForm) {
        nameForm.addEventListener("submit", function (e) {
            e.preventDefault();
            nameFeedback.textContent = "";
            nameSaveBtn.disabled = true;
            nameSaveBtn.textContent = "Saving…";

            const body = new FormData();
            body.append("name", nameInput.value);

            fetch(updateUrl, {
                method: "POST",
                body: body,
            })
                .then(r => r.json())
                .then(function (data) {
                    if (data.ok) {
                        displayName.textContent = data.name;
                        avatar.textContent = data.name.charAt(0).toUpperCase();
                        nameFeedback.textContent = "✓ Name updated.";
                        nameFeedback.style.color = "var(--bs-success, #198754)";
                    } else {
                        nameFeedback.textContent = data.error || "Something went wrong.";
                        nameFeedback.style.color = "var(--bs-danger, #dc3545)";
                    }
                })
                .catch(function () {
                    nameFeedback.textContent = "Network error — try again.";
                    nameFeedback.style.color = "var(--bs-danger, #dc3545)";
                })
                .finally(function () {
                    nameSaveBtn.disabled = false;
                    nameSaveBtn.textContent = "Save";
                });
        });
    }

    // ── Delete flow ───────────────────────────────────────────────────────
    if (showDeleteBtn) {
        showDeleteBtn.addEventListener("click", function () {
            step1.style.display = "none";
            step2.style.display = "";
            deleteInput.focus();
        });
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", function () {
            step2.style.display = "none";
            step1.style.display = "";
            deleteInput.value = "";
            confirmBtn.disabled = true;
        });
    }

    if (deleteInput) {
        deleteInput.addEventListener("input", function () {
            confirmBtn.disabled = this.value.trim() !== "DELETE";
        });
    }

}());