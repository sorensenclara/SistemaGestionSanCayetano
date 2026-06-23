document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("platformSidebar");
    const overlay = document.getElementById("platformSidebarOverlay");
    const viewToggle = document.getElementById("platformViewToggle");

    function closeMenu() {
        if (sidebar) sidebar.classList.remove("is-open");
        if (overlay) overlay.classList.remove("is-open");
    }

    function toggleMenu() {
        if (sidebar) sidebar.classList.toggle("is-open");
        if (overlay) overlay.classList.toggle("is-open");
    }

    if (sidebar) {
        document.querySelectorAll("#platformMenuBtn, .platform-sidebar-menu-btn").forEach(function (btn) {
            btn.addEventListener("click", toggleMenu);
        });

        if (overlay) {
            overlay.addEventListener("click", closeMenu);
        }

        document.querySelectorAll(".platform-sidebar-link:not(#platformViewToggle)").forEach(function (link) {
            link.addEventListener("click", closeMenu);
        });
    }

    if (viewToggle && !window.location.search.includes("preview_mobile=1")) {
        viewToggle.addEventListener("click", function () {
            closeMenu();

            const preview = document.createElement("div");
            preview.className = "platform-mobile-preview";

            preview.innerHTML = `
                <button class="platform-mobile-preview-close" type="button">
                    <i class="bi bi-x-lg"></i>
                    Vista desktop
                </button>

                <div class="platform-phone-frame">
                    <iframe src="${window.location.pathname}?preview_mobile=1" title="Vista celular"></iframe>
                </div>
            `;

            document.body.appendChild(preview);

            preview.querySelector(".platform-mobile-preview-close").addEventListener("click", function () {
                preview.remove();
            });
        });
    }

    /* =====================================================
       TABS GENÉRICOS
       Uso:
       data-platform-tabs="nombre"
       data-platform-tab="panel"
       data-platform-panel="panel"
    ===================================================== */

    document.querySelectorAll("[data-platform-tabs]").forEach(function (tabsGroup) {
        const groupName = tabsGroup.dataset.platformTabs;
        const tabs = tabsGroup.querySelectorAll("[data-platform-tab]");
        const panels = document.querySelectorAll('[data-platform-panel-group="' + groupName + '"]');

        tabs.forEach(function (tab) {
            tab.addEventListener("click", function () {
                const target = tab.dataset.platformTab;

                tabs.forEach(function (item) {
                    item.classList.remove("is-active");
                });

                panels.forEach(function (panel) {
                    panel.classList.remove("is-active");
                });

                tab.classList.add("is-active");

                const activePanel = document.querySelector(
                    '[data-platform-panel-group="' + groupName + '"][data-platform-panel="' + target + '"]'
                );

                if (activePanel) {
                    activePanel.classList.add("is-active");
                }
            });
        });
    });
});