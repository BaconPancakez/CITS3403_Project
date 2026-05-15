(function () {

    // ── Restore active tab from ?tab= query param ─────────────────────────
    const tabParam = new URLSearchParams(window.location.search).get("tab");
    if (tabParam) {
        const trigger = document.querySelector(`#${CSS.escape(tabParam)}-tab`);
        if (trigger) bootstrap.Tab.getOrCreateInstance(trigger).show();
    }

    // ── Generic bulk-select setup ─────────────────────────────────────────
    function initBulkSelect(opts) {
        const selectAll = document.getElementById(opts.selectAllId);
        const bar = document.getElementById(opts.bulkBarId);
        const countEl = document.getElementById(opts.bulkCountId);
        const form = document.getElementById(opts.bulkFormId);
        const clearBtn = document.getElementById(opts.clearBtnId);

        if (!selectAll || !bar || !form) return;

        function getBoxes() {
            return [...document.querySelectorAll(`.${opts.checkboxClass}`)];
        }

        function sync() {
            const boxes = getBoxes();
            const checked = boxes.filter(b => b.checked);
            const count = checked.length;

            bar.classList.toggle("visible", count > 0);
            countEl.textContent = `${count} report${count === 1 ? "" : "s"} selected`;

            selectAll.indeterminate = count > 0 && count < boxes.length;
            selectAll.checked = count > 0 && count === boxes.length;

            boxes.forEach(b => {
                b.closest("tr").classList.toggle("row-selected", b.checked);
            });

            form.querySelectorAll('input[name="report_ids"]').forEach(n => n.remove());
            checked.forEach(b => {
                const h = document.createElement("input");
                h.type = "hidden";
                h.name = "report_ids";
                h.value = b.value;
                form.appendChild(h);
            });
        }

        selectAll.addEventListener("change", function () {
            getBoxes().forEach(b => { b.checked = this.checked; });
            sync();
        });

        document.addEventListener("change", function (e) {
            if (e.target.classList.contains(opts.checkboxClass)) sync();
        });

        if (clearBtn) {
            clearBtn.addEventListener("click", function () {
                getBoxes().forEach(b => { b.checked = false; });
                selectAll.checked = false;
                sync();
            });
        }
    }

    initBulkSelect({
        selectAllId: "noteSelectAll",
        checkboxClass: "note-report-cb",
        bulkBarId: "noteBulkBar",
        bulkCountId: "noteBulkCount",
        bulkFormId: "noteBulkForm",
        clearBtnId: "noteBulkClear",
    });

    initBulkSelect({
        selectAllId: "quizSelectAll",
        checkboxClass: "quiz-report-cb",
        bulkBarId: "quizBulkBar",
        bulkCountId: "quizBulkCount",
        bulkFormId: "quizBulkForm",
        clearBtnId: "quizBulkClear",
    });

}());