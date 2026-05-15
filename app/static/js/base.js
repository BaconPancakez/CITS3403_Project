(function () {
    const toggle = document.getElementById("themeSwitch");
    const html = document.documentElement;

    // Sync checkbox with whatever theme is already active (set in <head>)
    const current = html.getAttribute("data-bs-theme") || "light";
    if (toggle) toggle.checked = current === "dark";

    if (toggle) {
        toggle.addEventListener("change", function () {
            const next = this.checked ? "dark" : "light";
            html.setAttribute("data-bs-theme", next);
            localStorage.setItem("theme", next);
        });
    }
}());