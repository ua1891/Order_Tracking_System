document.addEventListener('DOMContentLoaded', () => {
    // Poll the backend for new notifications every 10 seconds
    const POLLING_INTERVAL = 10000;

    function checkNotifications() {
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    data.forEach(notif => {
                        // The prompt requested to show 'Pop Ok'. We show a SweetAlert2 popup.
                        Swal.fire({
                            title: 'Status Update!',
                            text: notif.message,
                            icon: 'info',
                            confirmButtonText: 'Pop Ok', // Specifically requested by user
                            confirmButtonColor: '#0d6efd'
                        }).then(() => {
                            // Optionally reload to update dashboard status if we are on dashboard
                            if (window.location.pathname === '/') {
                                window.location.reload();
                            }
                        });
                    });
                }
            })
            .catch(error => console.error("Error fetching notifications:", error));
    }

    setInterval(checkNotifications, POLLING_INTERVAL);
    
    // Initial check just in case
    setTimeout(checkNotifications, 2000);
});
