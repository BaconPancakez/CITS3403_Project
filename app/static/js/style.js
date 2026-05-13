window.addEventListener("scroll", function () {
    const arrow = document.querySelector(".scroll-indicator");
    if (!arrow) return;

    if (window.scrollY > 50) {
        arrow.style.opacity = "0";
    } else {
        arrow.style.opacity = "0.5";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("notesPreviewModal");
    if (!modal) return;

    const titleEl = modal.querySelector("#notesPreviewModalLabel");
    const detailsEl = modal.querySelector("#notesPreviewDetails");
    const frameEl = modal.querySelector("#notesPreviewFrame");

    modal.addEventListener("show.bs.modal", function (event) {
        const trigger = event.relatedTarget;
        if (!trigger) return;

        const title = trigger.getAttribute("data-note-title") || "Notes";
        const details = trigger.getAttribute("data-note-details") || "";
        const src = trigger.getAttribute("data-note-src") || "";

        if (titleEl) titleEl.textContent = title;
        if (detailsEl) {
            detailsEl.textContent = details;
            detailsEl.classList.toggle("d-none", !details);
        }
        if (frameEl) frameEl.src = src;
    });

    modal.addEventListener("hidden.bs.modal", function () {
        if (frameEl) frameEl.src = "";
    });
});