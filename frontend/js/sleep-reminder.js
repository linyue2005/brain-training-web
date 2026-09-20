// ============ 早睡提醒 ============
(function () {
    // 每 30 分钟检查一次
    const CHECK_INTERVAL = 30 * 60 * 1000;

    function getMessage() {
        const now = new Date();
        const hour = now.getHours();
        const minute = now.getMinutes();

        // 只在 22:00 ~ 05:59 之间
        const isNightTime = (hour >= 22 && hour <= 23) || (hour >= 0 && hour < 6);
        if (!isNightTime) return null;

        // 只在整点或半点提醒（00 或 30 分）
        const isOnTime = (minute >= 0 && minute <= 5) || (minute >= 30 && minute <= 35);
        if (!isOnTime) return null;

        const timeStr = String(hour).padStart(2, "0") + ":" + String(minute).padStart(2, "0");

        if (hour >= 22) {
            return "🌙 已经 " + timeStr + " 了，该准备睡觉了~";
        } else {
            return "😴 太晚了，快去睡觉吧！";
        }
    }

    function showOrUpdateReminder() {
        const msg = getMessage();
        const existing = document.getElementById("sleep-reminder");

        if (!msg) {
            // 不满足条件，移除已有提醒
            if (existing) existing.remove();
            return;
        }

        if (existing) {
            // 已有提醒，更新内容
            existing.innerHTML = msg;
            return;
        }

        // 找插入位置
        const card = document.querySelector(".card");
        if (!card) return;

        const userBar = document.getElementById("user-bar");
        const div = document.createElement("div");
        div.id = "sleep-reminder";
        div.className = "sleep-reminder";
        div.innerHTML = msg;

        if (userBar && userBar.parentNode === card) {
            userBar.parentNode.insertBefore(div, userBar.nextSibling);
        } else {
            card.insertBefore(div, card.firstChild);
        }
    }

    // 页面加载时检查一次
    window.addEventListener("DOMContentLoaded", showOrUpdateReminder);

    // 每 30 分钟自动检查
    setInterval(showOrUpdateReminder, CHECK_INTERVAL);
})();