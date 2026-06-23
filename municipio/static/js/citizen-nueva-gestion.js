document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("citizenSearchInput");
    const results = document.getElementById("citizenSearchResults");

    if (!input || !results) return;

    async function searchCategories(value) {
        if (value.length < 3) {
            results.classList.remove("show");
            results.innerHTML = "";
            return;
        }

        const response = await fetch(`/ciudadano/api/categorias/buscar/?q=${encodeURIComponent(value)}`);
        const data = await response.json();

        results.innerHTML = "";

        if (!data.results.length) {
            results.classList.add("show");
            results.innerHTML = `
                <div class="citizen-search-empty">
                    No encontramos coincidencias. Probá con otra palabra.
                </div>
            `;
            return;
        }

        data.results.forEach(item => {
            const link = document.createElement("a");
            link.href = item.url;
            link.className = "citizen-search-result-link";
            link.innerHTML = `
                <strong>${item.nombre}</strong>
                <span>${item.tipo} / ${item.area}</span>
            `;
            results.appendChild(link);
        });

        results.classList.add("show");
    }

    input.addEventListener("input", function () {
        searchCategories(this.value.trim());
    });

    document.querySelectorAll(".citizen-tag-list button").forEach(btn => {
        btn.addEventListener("click", function () {
            input.value = this.innerText;
            searchCategories(input.value.trim());
            input.focus();
        });
    });
});