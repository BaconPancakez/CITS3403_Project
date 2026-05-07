window.addEventListener("scroll", function () {
    const arrow = document.querySelector(".scroll-indicator");
    if (!arrow) return;

    if (window.scrollY > 50) {
        arrow.style.opacity = "0";
    } else {
        arrow.style.opacity = "0.5";
    }
});