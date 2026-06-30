(function () {
  function applyTheme(theme) {
    localStorage.setItem("hermes-theme", theme);

    if (theme === "system") {
      delete document.documentElement.dataset.theme;
    } else {
      document.documentElement.dataset.theme = theme;
    }

    document.querySelectorAll("[data-theme-button]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.themeButton === theme);
    });

    window.dispatchEvent(new CustomEvent("hermes-theme-changed", { detail: { theme } }));
  }

  window.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("hermes-theme") || "system";

    document.querySelectorAll("[data-theme-button]").forEach((btn) => {
      btn.addEventListener("click", () => applyTheme(btn.dataset.themeButton));
    });

    applyTheme(saved);
  });
})();
