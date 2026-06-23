// App Ciudadana - JS global

document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("citizenMenuBtn");
    const drawer = document.getElementById("citizenDrawer");
    const overlay = document.getElementById("citizenMenuOverlay");
    const close = document.getElementById("citizenDrawerClose");

    if (!btn || !drawer || !overlay || !close) return;

    function openDrawer() {
        drawer.classList.add("open");
        overlay.classList.add("open");
    }

    function closeDrawer() {
        drawer.classList.remove("open");
        overlay.classList.remove("open");
    }

    btn.addEventListener("click", openDrawer);
    close.addEventListener("click", closeDrawer);
    overlay.addEventListener("click", closeDrawer);
});