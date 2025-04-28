// Handle notifications properly across pages
document.addEventListener('DOMContentLoaded', () => {
    const notificationElement = document.getElementById('notification');
    
    if (notificationElement) {
        // Only show if on intended page
        const allowedPages = ['/contact', '/dashboard']; // Add your pages
        if (!allowedPages.some(page => window.location.pathname.includes(page))) {
            notificationElement.remove();
            return;
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            notificationElement.style.transition = 'opacity 0.5s ease';
            notificationElement.style.opacity = '0';
            setTimeout(() => notificationElement.remove(), 500);
        }, 5000);

        // Manual close button
        notificationElement.querySelector('.close-notification')?.addEventListener('click', () => {
            notificationElement.remove();
        });
    }
});

// Usage in your login/logout handlers:
function showNotification(message, type = 'success') {
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '2000';
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">${message}</div>
        <button class="close-notification">&times;</button>
    `;
    
    document.getElementById('notification-container').appendChild(notification);
    
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s ease';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}