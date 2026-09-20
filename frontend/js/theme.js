// ============ 主题切换 ============

// 初始化：页面 DOM 加载完后，读取保存的主题
function initTheme() {
    const theme = localStorage.getItem("theme");
    if (theme === "dark") {
        document.body.classList.add("dark");
    }
    updateThemeButton();
}

// 切换主题
function toggleTheme() {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    updateThemeButton();
    if (window.updateStarfield) {
        window.updateStarfield();
    }
}

// 更新按钮图标
function updateThemeButton() {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    const isDark = document.body.classList.contains("dark");
    btn.textContent = isDark ? "☀️" : "🌙";
}

// 页面 DOM 加载完后初始化
window.addEventListener("DOMContentLoaded", () => {
    initTheme();
    if (window.updateStarfield) {
        window.updateStarfield();
    }
});