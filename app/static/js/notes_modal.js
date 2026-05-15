(function () {
    const modal = document.getElementById("notesPreviewModal");
    if (!modal) return;

    const frame = document.getElementById("notesPreviewFrame");
    const label = document.getElementById("notesPreviewModalLabel");
    const detail = document.getElementById("notesPreviewDetails");
    const badge = document.getElementById("notesPreviewBadge");
    const dlBtn = document.getElementById("notesDownloadBtn");

    modal.addEventListener("show.bs.modal", function (e) {
        const btn = e.relatedTarget;
        if (!btn) return;

        const title = btn.getAttribute("data-note-title") || "Notes";
        const detailTxt = btn.getAttribute("data-note-details") || "";

        // data-note-src should already point to /preview, but normalise just in case
        let previewBase = (btn.getAttribute("data-note-src") || "")
            .split("?")[0]                                   // strip any existing params
            .replace(/\/(file|download)$/, "/preview");      // fallback conversion

        if (!previewBase) return;

        // Derive the download URL from the preview URL
        const downloadUrl = previewBase.replace(/\/preview$/, "/download");

        // Pass the current theme so the iframe stylesheet matches the app
        const theme = document.documentElement.getAttribute("data-bs-theme") || "light";
        const src = previewBase + "?theme=" + encodeURIComponent(theme);

        // Populate header
        label.textContent = title;

        if (detailTxt) {
            detail.textContent = detailTxt;
            detail.style.display = "block";
        } else {
            detail.style.display = "none";
        }

        // File extension badge
        const ext = previewBase.split(".").pop().toUpperCase();
        if (ext && ext.length <= 4 && ext !== "PREVIEW") {
            badge.textContent = ext;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }

        if (dlBtn) dlBtn.href = downloadUrl;
        frame.src = src;
    });

    // Clear iframe on close so it stops loading in the background
    modal.addEventListener("hide.bs.modal", function () {
        frame.src = "";
    });

    // Reload iframe with updated theme if user toggles while modal is open
    const observer = new MutationObserver(function () {
        if (!modal.classList.contains("show") || !frame.src) return;
        const updated = frame.src.replace(
            /([?&]theme=)[^&]*/,
            "$1" + (document.documentElement.getAttribute("data-bs-theme") || "light")
        );
        if (updated !== frame.src) frame.src = updated;
    });
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-bs-theme"],
    });
}());