// Application JavaScript - Theme Toggle, HTMX Setup, and UI Helpers

document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const htmlEl = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill text-warning';
        } else {
            themeIcon.className = 'bi bi-moon-stars-fill text-secondary';
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', async () => {
            const currentTheme = htmlEl.getAttribute('data-bs-theme') || 'light';
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Instantly apply theme to DOM
            htmlEl.setAttribute('data-bs-theme', nextTheme);
            updateThemeIcon(nextTheme);

            // Persist theme via POST to server and cookie
            const csrftoken = getCookie('csrftoken');
            try {
                await fetch('/accounts/toggle-theme/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken,
                    },
                    body: `theme=${nextTheme}`
                });
            } catch (err) {
                console.warn('Could not persist theme to server:', err);
            }
        });
    }

    // Set initial icon on page load
    const currentTheme = htmlEl.getAttribute('data-bs-theme') || 'light';
    updateThemeIcon(currentTheme);

    // 2. Mobile Sidebar Drawer
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const appSidebar = document.querySelector('.app-sidebar');
    if (sidebarToggleBtn && appSidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            appSidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 992 && 
                appSidebar.classList.contains('show') && 
                !appSidebar.contains(e.target) && 
                !sidebarToggleBtn.contains(e.target)) {
                appSidebar.classList.remove('show');
            }
        });
    }

    // 3. Auto-dismiss flash alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach((alert) => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 4000);
    });

    // 4. Password Visibility Toggle (Eye Icon)
    document.addEventListener('click', (e) => {
        const toggleBtn = e.target.closest('.toggle-password-btn');
        if (!toggleBtn) return;

        e.preventDefault();
        const targetId = toggleBtn.getAttribute('data-target');
        const input = targetId ? document.getElementById(targetId) : toggleBtn.closest('.input-group')?.querySelector('input');
        if (!input) return;

        const icon = toggleBtn.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            if (icon) {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            }
            toggleBtn.setAttribute('title', 'Hide Password');
        } else {
            input.type = 'password';
            if (icon) {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
            toggleBtn.setAttribute('title', 'Show Password');
        }
    });
});

// 4. HTMX CSRF Token Configuration
document.addEventListener('htmx:configRequest', (event) => {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        event.detail.headers['X-CSRFToken'] = csrftoken;
    }
});
