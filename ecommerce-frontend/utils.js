const API_BASE = 'http://127.0.0.1:8000/';

// Helper to parse JWT tokens (to get role/user_id)
function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
}

function logout() {
    localStorage.clear(); // Clear all data
    window.location.href = 'login.html';
}

/**
 * Shows a beautiful toast notification
 * @param {string} message - The text to display
 * @param {string} type - 'success', 'error', 'warning', or 'info'
 * @param {number} duration - Time in ms before auto-close (default 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    let container = document.querySelector('.toast-container');
    
    // Create container if it doesn't exist
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create Toast Element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon"></span>
        <span style="flex-grow:1">${message}</span>
        <div class="toast-progress" style="animation-duration: ${duration}ms"></div>
    `;

    // Append to DOM
    container.appendChild(toast);

    // Remove logic
    const removeToast = () => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        toast.addEventListener('animationend', () => toast.remove());
    };

    // Auto remove
    setTimeout(removeToast, duration);

    // Click to remove immediately
    toast.onclick = removeToast;
}

// A wrapper around fetch to handle Auth headers and Token Refresh
async function authFetch(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    
    // Set default headers
    options.headers = options.headers || {};
    options.headers['ngrok-skip-browser-warning'] = 'true';

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, options);

    // If 401 (Unauthorized), try to refresh the token
    if (response.status === 401) {
        const refresh = localStorage.getItem('refreshToken');
        if (refresh) {
            try {
                const refreshRes = await fetch(`${API_BASE}/api/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh })
                });

                if (refreshRes.ok) {
                    const data = await refreshRes.json();
                    localStorage.setItem('accessToken', data.access);
                    // Retry the original request with the new token
                    options.headers['Authorization'] = `Bearer ${data.access}`;
                    response = await fetch(url, options);
                } else {
                    // Refresh failed, force logout
                    logout();
                }
            } catch (error) {
                logout();
            }
        } else {
            logout();
        }
    }

    // Rate Limit Handling (Global)
    if (response.status === 403) {
        try {
            // Clone response so we don't consume the body for the caller
            const clone = response.clone();
            const text = await clone.text();
            if (text.includes("Rate Limit")) {
                showToast("⚠️ " + text, 'warning', 5000);
            }
        } catch (e) {
            console.error("Error checking rate limit", e);
        }
    }

    return response;
}

// Wrapper for Fetch to handle Rate Limits manually (e.g. for Login/Register)
async function checkRateLimit(response) {
    if (response.status === 403) {
        try {
            // Clone response so subsequent .json() calls don't fail
            const clone = response.clone();
            const text = await clone.text();
            if (text.includes("Rate Limit")) {
                showToast("⚠️ " + text, 'warning', 5000);
                return true;
            }
        } catch (e) {
            return false;
        }
    }
    return false;
}

function showConfirm(message) {
    return new Promise((resolve) => {
        // 1. Create Modal HTML
        const modal = document.createElement('div');
        modal.className = 'modal'; 
        modal.style.display = 'flex'; 
        modal.style.zIndex = '10000'; 
        
        modal.innerHTML = `
            <div class="confirm-modal-content">
                <h3 style="margin-top:0">Are you sure?</h3>
                <p>${message}</p>
                <div class="confirm-actions">
                    <button id="confirmYes" class="confirm-btn-yes">Yes</button>
                    <button id="confirmNo" class="confirm-btn-no">Cancel</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 2. Handle Clicks
        const btnYes = modal.querySelector('#confirmYes');
        const btnNo = modal.querySelector('#confirmNo');

        function cleanup() {
            document.body.removeChild(modal);
        }

        btnYes.onclick = () => {
            cleanup();
            resolve(true); // User clicked Yes
        };

        btnNo.onclick = () => {
            cleanup();
            resolve(false); // User clicked No
        };

        // Click outside to cancel
        modal.onclick = (e) => {
            if (e.target === modal) {
                cleanup();
                resolve(false);
            }
        };
    });
}
