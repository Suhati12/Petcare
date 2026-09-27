/**
 * PetCare+ Notification Center & Unread Count Poller
 */

function fetchUnreadNotificationsCount() {
    fetch('/notifications/unread-count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('nav-unread-badge');
            if (badge) {
                if (data.unread_count > 0) {
                    badge.textContent = data.unread_count;
                    badge.classList.remove('d-none');
                } else {
                    badge.classList.add('d-none');
                }
            }
        })
        .catch(err => console.error("Notification polling error:", err));
}

// Request Browser Push Notification Permission if supported
function requestBrowserNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Browser notification permission granted.");
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchUnreadNotificationsCount();
    // Poll every 30 seconds
    setInterval(fetchUnreadNotificationsCount, 30000);
    requestBrowserNotificationPermission();
});
