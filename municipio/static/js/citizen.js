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

// ─── Selector de categorías (reclamos y solicitudes) ─────────────────────────
// Usado en: reclamos_categorias.html, solicitudes_categorias.html
// El input#categorySearch acepta data-empty-hint para personalizar el mensaje
// de "sin resultados" por tipo de gestión.

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("categorySearch");
    if (!searchInput) return;

    const searchResults = document.getElementById("searchResults");
    const areasStep = document.getElementById("areasStep");
    const categoriesStep = document.getElementById("categoriesStep");
    const backToAreas = document.getElementById("backToAreas");
    const areaCards = document.querySelectorAll(".platform-area-card");
    const areaPanels = document.querySelectorAll(".platform-category-area");
    const categoryCards = document.querySelectorAll(".platform-category-card");

    const emptyHint = searchInput.dataset.emptyHint ||
        "Probá con otra palabra, por ejemplo: poda, bache o alumbrado.";

    function showAreas() {
        areasStep.style.display = "block";
        categoriesStep.classList.remove("is-active");
        areaPanels.forEach(panel => panel.style.display = "none");
    }

    function showArea(areaId) {
        areasStep.style.display = "none";
        categoriesStep.classList.add("is-active");
        areaPanels.forEach(panel => {
            panel.style.display = panel.dataset.areaPanel === areaId ? "block" : "none";
        });
        searchResults.innerHTML = "";
        searchResults.classList.remove("is-active");
        searchInput.value = "";
    }

    areaCards.forEach(card => {
        card.addEventListener("click", function () {
            showArea(card.dataset.area);
        });
    });

    backToAreas.addEventListener("click", showAreas);

    searchInput.addEventListener("input", function () {
        const value = searchInput.value.toLowerCase().trim();
        searchResults.innerHTML = "";

        if (value.length < 2) {
            searchResults.classList.remove("is-active");
            areasStep.style.display = "block";
            categoriesStep.classList.remove("is-active");
            return;
        }

        areasStep.style.display = "none";
        categoriesStep.classList.remove("is-active");
        searchResults.classList.add("is-active");

        let matches = 0;
        categoryCards.forEach(card => {
            const name = card.dataset.categoryName || "";
            const area = card.dataset.categoryArea || "";
            if (name.includes(value) || area.includes(value)) {
                searchResults.appendChild(card.cloneNode(true));
                matches++;
            }
        });

        if (!matches) {
            searchResults.innerHTML = `
                <div class="platform-empty-state">
                    <i class="bi bi-search"></i>
                    <strong>No encontramos coincidencias</strong>
                    <span>${emptyHint}</span>
                </div>
            `;
        }
    });

    showAreas();
});
