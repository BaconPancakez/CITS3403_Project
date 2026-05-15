(function () {
    const fileInput = document.getElementById("notesFile");
    const txtSection = document.getElementById("txtEditorSection");
    const txtArea = document.getElementById("txtEditorArea");
    const txtContent = document.getElementById("notesTxtContent");
    const txtFname = document.getElementById("notesTxtFilename");
    const charCount = document.getElementById("txtCharCount");
    const step2 = document.getElementById("step2Indicator");
    const badge2 = document.getElementById("stepBadge2");
    const form = document.getElementById("uploadNotesForm");
    const modal = document.getElementById("uploadNotesModal");

    if (!fileInput) return;

    // ── Show / hide TXT editor based on selected file ─────────────────────────
    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (!file) {
            hideTxtEditor();
            return;
        }
        if (file.name.toLowerCase().endsWith(".txt")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                txtArea.value = e.target.result;
                updateCharCount();
                showTxtEditor();
                // Scroll editor into view smoothly
                txtSection.scrollIntoView({
                    behavior: "smooth", block: "nearest"
                });
            };
            reader.onerror = function () {
                txtArea.value = "";
                showTxtEditor();
            };
            reader.readAsText(file);
        } else {
            hideTxtEditor();
        }
    });

    function showTxtEditor() {
        txtSection.style.display = "block";
        step2.style.opacity = "1";
        badge2.className = "badge rounded-pill bg-primary";
    }

    function hideTxtEditor() {
        txtSection.style.display = "none";
        step2.style.opacity = "0.35";
        badge2.className = "badge rounded-pill bg-secondary";
        txtContent.value = "";
        txtFname.value = "";
    }

    // ── Live character count ──────────────────────────────────────────────────
    txtArea.addEventListener("input", updateCharCount);

    function updateCharCount() {
        const n = txtArea.value.length;
        charCount.textContent = n.toLocaleString() + " chars";
    }

    // ── On submit: copy edited text to hidden fields if in TXT mode ───────────
    form.addEventListener("submit", function () {
        const file = fileInput.files[0];
        if (file && file.name.toLowerCase().endsWith(".txt")
            && txtSection.style.display !== "none") {
            txtContent.value = txtArea.value;
            txtFname.value = file.name;
        }
    });

    // ── Reset everything when modal closes ────────────────────────────────────
    if (modal) {
        modal.addEventListener("hidden.bs.modal", function () {
            form.reset();
            hideTxtEditor();
            charCount.textContent = "";
        });
    }
}());