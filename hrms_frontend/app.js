// // Wait for the DOM to be fully loaded before running scripts
// document.addEventListener('DOMContentLoaded', () => {

//     // --- CONFIGURATION ---
//     const API_BASE_URL = 'http://localhost:8000/api';
//     let loginModalInstance; // To control the modal programmatically

//     // --- DOM ELEMENTS ---
//     const loginButtonContainer = document.getElementById('login-button-container');
//     const userInfoContainer = document.getElementById('user-info-container');
//     const welcomeUsername = document.getElementById('welcome-username');
//     const logoutButton = document.getElementById('logout-button');
//     const loginForm = document.getElementById('login-form');
//     const loginError = document.getElementById('login-error');
//     const loginModalElement = document.getElementById('login-modal');
    
//     // Initialize Bootstrap Modal instance
//     if (loginModalElement) {
//         loginModalInstance = new bootstrap.Modal(loginModalElement);
//     }

//     /**
//      * Updates the navbar UI based on the user's login status.
//      */
//     function updateNavbar() {
//         const accessToken = localStorage.getItem('accessToken');
//         const username = localStorage.getItem('username');

//         if (accessToken && username) {
//             // User is logged in
//             loginButtonContainer.classList.add('hidden');
//             userInfoContainer.classList.remove('hidden');
//             welcomeUsername.textContent = username;
//         } else {
//             // User is logged out
//             loginButtonContainer.classList.remove('hidden');
//             userInfoContainer.classList.add('hidden');
//             welcomeUsername.textContent = '';
//         }
//     }

//     /**
//      * Redirects the user based on their role.
//      */
//     function redirectUser(role) {
//         if (role === 'ADMIN') {
//             window.location.href = '/admin/';
//         } else if (role === 'HR') {
//             window.location.href = '/portal/employee_form.html';
//         } else if (role === 'EMPLOYEE') {
//             window.location.href = '/portal/employee_detail.html';
//         } else {
//             // A sensible default if the role is unknown or logged out
//             console.warn(`Unknown role: ${role}. Redirecting to dashboard.`);
//             pageUrl = '/index.html';
//         }
//     }

//     /**
//      * Handles the login form submission.
//      * This now performs two requests:
//      * 1. POST to /login/ to get tokens.
//      * 2. GET to /user/me/ to get user role and details.
//      */
//     async function handleLogin(event) {
//         event.preventDefault();
//         loginError.classList.add('hidden'); // Hide old errors

//         const username = document.getElementById('login-username').value;
//         const password = document.getElementById('login-password').value;

//         try {
//             // --- Step 1: Get Tokens ---
//             const loginResponse = await fetch(`${API_BASE_URL}/login/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify({ username, password })
//             });

//             if (!loginResponse.ok) {
//                 loginError.textContent = 'Invalid username or password.';
//                 loginError.classList.remove('hidden');
//                 throw new Error('Login failed');
//             }

//             const tokenData = await loginResponse.json();

//             // Store tokens immediately to be used in the next request
//             localStorage.setItem('accessToken', tokenData.access);
//             localStorage.setItem('refreshToken', tokenData.refresh);

//             // --- Step 2: Get User Role ---
//             const userResponse = await fetch(`${API_BASE_URL}/user/me/`, {
//                 method: 'GET',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Authorization': `Bearer ${tokenData.access}` // Use the new token
//                 }
//             });

//             if (!userResponse.ok) {
//                 loginError.textContent = 'Login successful, but failed to fetch user details.';
//                 loginError.classList.remove('hidden');
//                 throw new Error('Failed to fetch user details');
//             }

//             const userDataResponse = await userResponse.json();

//             // Check for the response structure you specified
//             if (!userDataResponse.success || !userDataResponse.user) {
//                 loginError.textContent = 'Received invalid user data from server.';
//                 loginError.classList.remove('hidden');
//                 throw new Error('Invalid user data structure');
//             }
            
//             const user = userDataResponse.user;

//             // Store user details
//             localStorage.setItem('username', user.username);
//             localStorage.setItem('role', user.role);

//             // --- Success ---
//             loginModalInstance.hide(); // Hide the modal on success
//             loginForm.reset(); // Clear the form
            
//             // Redirect based on role
//             redirectUser(user.role);

//         } catch (error) {
//             console.error('Login process error:', error.message);
//             // If anything fails (login or user fetch), clear tokens to be safe
//             clearUserSession();
//         }
//     }

//     /**
//      * Handles the logout button click.
//      */
//     async function handleLogout() {
//         const refreshToken = localStorage.getItem('refreshToken');
        
//         if (refreshToken) {
//             try {
//                 // Try to log out on the server
//                 await fetch(`${API_BASE_URL}/logout/`, {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json'
//                     },
//                     body: JSON.stringify({ refresh: refreshToken })
//                 });
//             } catch (error) {
//                 console.warn('Server logout failed, logging out locally:', error);
//             }
//         }

//         // Always clear the local session and redirect
//         clearUserSession();
//         window.location.href = '/'; // Redirect to home/login page
//     }

//     /**
//      * Clears all user data from localStorage and updates the UI.
//      */
//     function clearUserSession() {
//         localStorage.removeItem('accessToken');
//         localStorage.removeItem('refreshToken');
//         localStorage.removeItem('username');
//         localStorage.removeItem('role'); // <-- Added this
//         updateNavbar();
//     }

//     /**
//      * Updates the copyright year in the footer.
//      */
//     function updateFooterYear() {
//         const yearElement = document.getElementById('current-year');
//         if (yearElement) {
//             yearElement.textContent = new Date().getFullYear();
//         }
//     }

//     // --- INITIALIZATION ---

//     // Add event listeners
//     if (loginForm) {
//         loginForm.addEventListener('submit', handleLogin);
//     }
//     if (logoutButton) {
//         logoutButton.addEventListener('click', handleLogout);
//     }

//     // Run initial checks on page load
//     updateNavbar();
//     updateFooterYear();

// });


// document.addEventListener('DOMContentLoaded', () => {

//     // --- CONFIGURATION ---
//     const API_BASE_URL = 'http://localhost:8000/api';

//     // --- DOM ELEMENTS ---
//     const mainContent = document.getElementById('main-content');
//     const loginButtonContainer = document.getElementById('login-button-container');
//     const userInfoContainer = document.getElementById('user-info-container');
//     const welcomeUsername = document.getElementById('welcome-username');
//     const logoutButton = document.getElementById('logout-button');
//     const navLoginButton = document.getElementById('nav-login-button');

//     /**
//      * Updates the navbar UI based on login status.
//      */
//     function updateNavbar(username) {
//         if (username) {
//             // User is logged in
//             loginButtonContainer.classList.add('hidden');
//             userInfoContainer.classList.remove('hidden');
//             welcomeUsername.textContent = username;
//         } else {
//             // User is logged out
//             loginButtonContainer.classList.remove('hidden');
//             userInfoContainer.classList.add('hidden');
//             welcomeUsername.textContent = '';
//         }
//     }

//     /**
//      * Fetches and loads a partial HTML file into the main content area.
//      */
//     async function loadPageContent(pageName) {
//         // Map simple names to actual file paths
//         const pageMap = {
//             'login': 'partials/login.html',
//             'welcome': 'partials/welcome.html',
//             'employee_form': 'partials/employee_form.html',
//             'employee_detail': 'partials/employee_detail.html',
//         };

//         const pageUrl = pageMap[pageName] || pageMap['welcome'];

//         try {
//             const response = await fetch(pageUrl);
//             if (!response.ok) throw new Error(`Page not found: ${pageUrl}`);
//             const html = await response.text();
//             mainContent.innerHTML = html;
//         } catch (error) {
//             console.error('Failed to load page:', error);
//             mainContent.innerHTML = '<div class="alert alert-danger">Error: Could not load content.</div>';
//         }
//     }

//     /**
//      * Determines which page to load based on user role.
//      */
//     function loadDashboardByRole(role) {
//         if (role === 'ADMIN') {
//             // Admin is a special case: redirect to the Django admin
//             window.location.href = '/admin/';
//         } else if (role === 'HR') {
//             loadPageContent('employee_form');
//         } else if (role === 'EMPLOYEE') {
//             loadPageContent('employee_detail');
//         } else {
//             // Fallback for unknown roles
//             loadPageContent('welcome');
//         }
//     }

//     /**
//      * Handles the login form submission.
//      */
//     async function handleLogin(event) {
//         event.preventDefault();
//         const loginError = document.getElementById('login-error');
//         loginError.classList.add('hidden'); // Hide old errors

//         const username = document.getElementById('login-username').value;
//         const password = document.getElementById('login-password').value;

//         try {
//             // --- Step 1: Get Tokens ---
//             const loginResponse = await fetch(`${API_BASE_URL}/login/`, {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ username, password })
//             });

//             if (!loginResponse.ok) throw new Error('Invalid username or password.');
            
//             const tokenData = await loginResponse.json();
//             localStorage.setItem('accessToken', tokenData.access);
//             localStorage.setItem('refreshToken', tokenData.refresh);

//             // --- Step 2: Get User Details ---
//             const userResponse = await fetch(`${API_BASE_URL}/user/me/`, {
//                 headers: { 'Authorization': `Bearer ${tokenData.access}` }
//             });

//             if (!userResponse.ok) throw new Error('Could not fetch user details.');

//             const userData = await userResponse.json();
//             if (!userData.success || !userData.user) throw new Error('Invalid user data.');

//             const user = userData.user;

//             // --- Success: Store details and load dashboard ---
//             localStorage.setItem('username', user.username);
//             localStorage.setItem('role', user.role);
            
//             updateNavbar(user.username);
//             loadDashboardByRole(user.role);

//         } catch (error) {
//             console.error('Login process failed:', error);
//             loginError.textContent = error.message;
//             loginError.classList.remove('hidden');
//             clearUserSession(); // Clear any partial tokens
//         }
//     }

//     /**
//      * Handles the logout process.
//      */
//     async function handleLogout() {
//         const refreshToken = localStorage.getItem('refreshToken');
//         if (refreshToken) {
//             try {
//                 await fetch(`${API_BASE_URL}/logout/`, {
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({ refresh: refreshToken })
//                 });
//             } catch (error) {
//                 console.warn('Server logout failed, logging out locally.', error);
//             }
//         }
//         clearUserSession();
//         updateNavbar(null);
//         loadPageContent('welcome'); // Load the welcome page
//     }

//     /**
//      * Clears all user data from localStorage.
//      */
//     function clearUserSession() {
//         localStorage.removeItem('accessToken');
//         localStorage.removeItem('refreshToken');
//         localStorage.removeItem('username');
//         localStorage.removeItem('role');
//     }

//     /**
//      * Updates the copyright year in the footer.
//      */
//     function updateFooterYear() {
//         document.getElementById('current-year').textContent = new Date().getFullYear();
//     }
    
//     /**
//      * Checks login state on initial page load.
//      */
//     async function checkInitialLoginState() {
//         const token = localStorage.getItem('accessToken');
//         const username = localStorage.getItem('username');
//         const role = localStorage.getItem('role');

//         if (token && username && role) {
//             // We have data, assume user is logged in
//             // For a more robust app, you'd re-validate the token here
//             updateNavbar(username);
//             loadDashboardByRole(role);
//         } else {
//             // No data, user is logged out
//             updateNavbar(null);
//             loadPageContent('welcome');
//         }
//     }
    
//     // --- EVENT LISTENERS ---

//     // Listen for all clicks on the document
//     document.body.addEventListener('click', (event) => {
//         // Handle navbar login button
//         if (event.target.id === 'nav-login-button') {
//             loadPageContent('login');
//         }
        
//         // Handle welcome page login button
//         if (event.target.id === 'welcome-login-button') {
//             event.preventDefault(); // It's an <a> tag
//             loadPageContent('login');
//         }
        
//         // Handle logout button
//         if (event.target.id === 'logout-button') {
//             handleLogout();
//         }

//         // Handle show/hide password checkbox
//         if (event.target.id === 'show-password') {
//             const passwordField = document.getElementById('login-password');
//             if (passwordField) {
//                 passwordField.type = event.target.checked ? 'text' : 'password';
//             }
//         }
//     });

//     // Listen for all form submissions on the document
//     document.body.addEventListener('submit', (event) => {
//         // Handle login form submission
//         if (event.target.id === 'login-form') {
//             handleLogin(event);
//         }
//     });

//     // --- INITIALIZATION ---
//     updateFooterYear();
//     checkInitialLoginState();
// });

document.addEventListener('DOMContentLoaded', () => {

    // --- CONFIGURATION ---
    const API_BASE_URL = 'http://localhost:8000/api';

    // --- DOM ELEMENTS ---
    const mainContent = document.getElementById('main-content');
    const loginButtonContainer = document.getElementById('login-button-container');
    const userInfoContainer = document.getElementById('user-info-container');
    const welcomeUsername = document.getElementById('welcome-username');

    // --- API HELPER ---

    /**
     * A wrapper for fetch that handles auth tokens and errors.
     * @param {string} endpoint API endpoint (e.g., '/employee/')
     * @param {object} options Fetch options (method, headers, body)
     * @returns {Promise<any>} JSON response
     */
    async function apiFetch(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { detail: `Request failed with status ${response.status}` };
            }
            throw new Error(errorData.detail || `Request failed with status ${response.status}`);
        }
        
        if (response.status === 204) { // Handle No Content
            return null;
        }
        return response.json();
    }

    // --- NAVIGATION / ROUTING ---

    /**
     * Fetches and loads a partial HTML file and initializes its scripts.
     * @param {string} pageName Key for the partial (e.g., 'login', 'employee_form')
     */
    async function loadPageContent(pageName) {
        const pageMap = {
            'login': 'partials/login.html',
            'welcome': 'partials/welcome.html',
            'employee_form': 'partials/employee_form.html',
            'employee_detail': 'partials/employee_detail.html',
            'attendance_update': 'partials/attendance_update.html',
            'personal_attendance': 'partials/personal_attendance.html'
        };

        const pageUrl = pageMap[pageName] || pageMap['welcome'];

        try {
            const response = await fetch(pageUrl);
            if (!response.ok) throw new Error(`Page not found: ${pageUrl}`);
            mainContent.innerHTML = await response.text();
            
            // Initialize scripts specific to this page
            initPageScripts(pageName);

        } catch (error) {
            console.error('Failed to load page:', error);
            mainContent.innerHTML = '<div class="alert alert-danger">Error: Could not load content.</div>';
        }
    }
    
    /**
     * A "router" that calls the correct init function for the loaded partial.
     * @param {string} pageName Key for the partial
     */
    function initPageScripts(pageName) {
        switch (pageName) {
            case 'login':
                initLoginPage();
                break;
            case 'employee_form':
                initEmployeeFormPage();
                break;
            case 'attendance_update':
                initAttendancePage();
                break;
            case 'employee_detail':
                initEmployeeDetailPage();
                break;
            case 'personal_attendance':
                initPersonalAttendancePage();
                break;
        }
    }

    // --- ADD THIS NEW HELPER FUNCTION for formatting dates ---
    /**
     * Formats a YYYY-MM-DD date string into "Month D, YYYY".
     * @param {string} dateString
     * @returns {string} Formatted date
     */
    function formatFullDate(dateString) {
        if (!dateString) return 'N/A';
        // Add time to avoid timezone issues
        const date = new Date(dateString + 'T00:00:00'); 
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    }

// --- ADD THIS NEW HELPER FUNCTION for uploading files ---
    /**
     * A wrapper for fetch that handles FormData (for file uploads).
     * @param {string} endpoint API endpoint
     * @param {object} options Fetch options (MUST include method and body)
     * @returns {Promise<any>} JSON response
     */
    async function apiFetchFormData(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        const headers = {
            // -- DO NOT set 'Content-Type' --
            // The browser sets it automatically for FormData
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Request failed with status ${response.status}`);
        }
        
        if (response.status === 204) return null;
        return response.json();
    }

    /**
     * Initializes the Employee Detail (Profile) page.
     */
    function initEmployeeDetailPage() {
        // Load the user's data
        loadEmployeeProfile();

        // Listen for the file input to change
        const photoInput = document.getElementById('photo-upload-input');
        if (photoInput) {
            photoInput.addEventListener('change', handlePhotoUpload);
        }
    }

    /**
     * Fetches the /api/user/me/ endpoint and populates the profile.
     */
    async function loadEmployeeProfile() {
        try {
            // We fetch "user/me/" since this is the employee's OWN profile
            const data = await apiFetch('/user/me/');
            if (!data.success || !data.user) {
                throw new Error('Invalid user data received.');
            }
            const user = data.user;

            // Populate all the fields
            document.getElementById('profile-id').textContent = String(user.id).padStart(5, '0');
            document.getElementById('profile-name').textContent = `${user.first_name} ${user.last_name}`;
            
            // Use the API response data you showed me before
            document.getElementById('profile-position').textContent = user.position_title || 'N/A';
            document.getElementById('profile-email').textContent = user.email;
            document.getElementById('profile-department').textContent = user.department_name || 'N/A';
            document.getElementById('profile-hire-date').textContent = formatFullDate(user.hire_date);

            // Update the photo
            // We assume the user object has a 'photo' field with the full URL
            updateProfilePhoto(user.photo_url); 

        } catch (error) {
            showMessage('danger', `Could not load profile: ${error.message}`);
        }
    }

    /**
     * Updates the profile photo display.
     * @param {string | null} photoUrl The URL of the new photo
     */
    function updateProfilePhoto(photoUrl) {
        console.log(photoUrl)
        const img = document.getElementById('profile-photo-img');
        const placeholder = document.getElementById('profile-photo-placeholder');

        if (photoUrl) {
            // Set the source and a unique timestamp to break browser cache
            img.src = `${photoUrl}?t=${new Date().getTime()}`;
            img.classList.remove('hidden');
            placeholder.classList.add('hidden');
        } else {
            // Show placeholder if no photo
            img.classList.add('hidden');
            placeholder.classList.remove('hidden');
        }
    }

    /**
     * Handles the file selection and upload.
     * @param {Event} event The 'change' event from the file input
     */
    async function handlePhotoUpload(event) {
        const file = event.target.files[0];
        if (!file) return; // No file selected

        const formData = new FormData();
        formData.append('photo', file);

        try {
            // Send the file to a new endpoint
            // This endpoint should handle the file and update the user's photo
            const data = await apiFetchFormData('/user/me/upload_photo/', {
                method: 'PATCH', // or 'POST' or 'PUT'
                body: formData
            });

            // Assuming the API returns the updated user data or just the new photo URL
            if (data.photo) {
                updateProfilePhoto(data.photo);
                showMessage('success', 'Profile photo updated!');
            } else {
                throw new Error('API did not return a new photo URL.');
            }

        } catch (error) {
            showMessage('danger', `Upload failed: ${error.message}`);
        }

        // Clear the file input's value so you can upload the same file again
        event.target.value = null;
    }

    // --- PAGE INITIALIZATION FUNCTIONS ---

    /**
     * Attaches listeners for the Login page.
     */
    function initLoginPage() {
        const showPassword = document.getElementById('show-password');
        if (showPassword) {
            showPassword.addEventListener('change', (e) => {
                const passField = document.getElementById('login-password');
                if (passField) {
                    passField.type = e.target.checked ? 'text' : 'password';
                }
            });
        }
    }

    /**
     * Initializes the "Manage Employees" page (HR Dashboard).
     */
    function initEmployeeFormPage() {
        // Load the initial employee list
        loadEmployeeList();

        // --- NEW ---
        // Fetch data for both dropdowns at the same time
        Promise.all([
            apiFetch('/department/'), // Assumes GET /api/department/
            apiFetch('/position/')  // Assumes GET /api/position/
        ])
        .then(([departments, positions]) => {
            populateDropdown('emp-department', departments, 'name');
            populateDropdown('emp-position', positions, 'title');
        })
        .catch(error => {
            showMessage('danger', `Failed to load form options: ${error.message}`);
        });
    }


    // --- NEW HELPER FUNCTION ---
    /**
     * Populates a <select> dropdown with options from an array.
     * @param {string} selectId The ID of the <select> element.
     * @param {Array<object>} items The array of data objects.
     * @param {string} textField The key in the object to use for the option text.
     */
    function populateDropdown(selectId, items, textField) {
        const select = document.getElementById(selectId);
        if (!select) return;

        select.innerHTML = `<option value="" disabled selected>Select a ${selectId.split('-')[1]}...</option>`; // Clear 'Loading...'
        
        items.forEach(item => {
            const option = document.createElement('option');
            // Assuming your API returns an object like { id: 1, name: 'Sales' }
            // or { id: 1, title: 'Manager' }
            // We use item.id as the value and the specified textField as the text.
            option.value = item.id; 
            option.textContent = item[textField];
            select.appendChild(option);
        });
    }

    /**
     * Initializes the "Update Attendance" page.
     */
    function initAttendancePage() {
        // Attach helper button listener
        const markAll = document.getElementById('mark-all-present');
        if (markAll) {
            markAll.addEventListener('click', () => {
                document.querySelectorAll('select[name="status"]').forEach(select => {
                    select.value = 'present';
                    select.dispatchEvent(new Event('change')); // Trigger color change
                });
            });
        }
        
        // Load the attendance data
        loadAttendanceData();
    }

    // --- AUTHENTICATION ---

    /**
     * Updates the navbar UI based on login status.
     */
    function updateNavbar(username) {
        if (username) {
            loginButtonContainer.classList.add('hidden');
            userInfoContainer.classList.remove('hidden');
            welcomeUsername.textContent = username;
        } else {
            loginButtonContainer.classList.remove('hidden');
            userInfoContainer.classList.add('hidden');
            welcomeUsername.textContent = '';
        }
    }
    
    /**
     * Determines which page to load based on user role.
     */
    function loadDashboardByRole(role) {
        if (role === 'ADMIN') {
            window.location.href = '/admin/'; // Redirect to Django admin
        } else if (role === 'HR') {
            loadPageContent('employee_form');
        } else if (role === 'EMPLOYEE') {
            loadPageContent('employee_detail');
        } else {
            loadPageContent('welcome'); // Fallback
        }
    }

    /**
     * Handles the login form submission.
     */
    async function handleLogin(event) {
        event.preventDefault();
        const loginError = document.getElementById('login-error');
        loginError.classList.add('hidden'); 

        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            // Step 1: Get Tokens
            const tokenData = await apiFetch('/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            localStorage.setItem('accessToken', tokenData.access);
            localStorage.setItem('refreshToken', tokenData.refresh);

            // Step 2: Get User Details
            const userData = await apiFetch('/user/me/'); // Uses new token
            if (!userData.success || !userData.user) throw new Error('Invalid user data.');
            
            const user = userData.user;
            localStorage.setItem('username', user.username);
            localStorage.setItem('role', user.role);
            
            updateNavbar(user.username);
            loadDashboardByRole(user.role);

        } catch (error) {
            loginError.textContent = error.message;
            loginError.classList.remove('hidden');
            clearUserSession(); // Clear any partial tokens
        }
    }

    /**
     * Handles the logout process.
     */
    async function handleLogout() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
            try {
                await apiFetch('/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh: refreshToken })
                });
            } catch (error) {
                console.warn('Server logout failed, logging out locally.', error);
            }
        }
        clearUserSession();
        updateNavbar(null);
        loadPageContent('welcome'); // Load the welcome page
    }

    /**
     * Clears all user data from localStorage.
     */
    function clearUserSession() {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('username');
        localStorage.removeItem('role');
    }

    // --- EMPLOYEE MANAGEMENT (for employee_form.html) ---

    /**
     * Fetches employee list and renders it.
     */
    async function loadEmployeeList() {
        const listElement = document.getElementById('employee-list');
        if (!listElement) return;

        try {
            const employees = await apiFetch('/employee/'); // Assumes GET /api/employee/
            listElement.innerHTML = ''; // Clear list
            if (!employees || employees.length === 0) {
                listElement.innerHTML = '<p class="text-center text-muted p-4">No employees have been added yet.</p>';
                return;
            }

            employees.forEach(emp => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    <div>
                        <strong>${emp.first_name || ''} ${emp.last_name || ''}</strong><br />
                        <small class="text-muted">
                            ${emp.department || 'N/A'} — ${emp.position || 'N/A'}
                        </small>
                    </div>
                    <button class="btn btn-outline-danger btn-sm delete-employee" data-id="${emp.id}" title="Delete Employee">
                        <i class="bi bi-trash"></i>
                    </button>
                `;
                listElement.appendChild(li);
            });
        } catch (error) {
            showMessage('danger', `Error loading employees: ${error.message}`);
        }
    }

    /**
     * Handles the "Add Employee" form submission.
     */
    async function handleAddEmployee(event) {
        event.preventDefault();
        
        // --- UPDATED: Get all values from the new form ---
        const newEmployee = {
            username: document.getElementById('emp-username').value,
            email: document.getElementById('emp-email').value,
            password: document.getElementById('emp-password').value,
            first_name: document.getElementById('emp-first_name').value,
            last_name: document.getElementById('emp-last_name').value,
            department: document.getElementById('emp-department').value, // This is now the department ID
            position: document.getElementById('emp-position').value,   // This is now the position ID
        };
        
        // --- Validate dropdowns ---
        if (!newEmployee.department || !newEmployee.position) {
            showMessage('danger', 'Please select a department and position.');
            return;
        }

        try {
            await apiFetch('/employee/', { // Assumes POST /api/employee/
                method: 'POST',
                body: JSON.stringify(newEmployee)
            });
            showMessage('success', 'Employee added successfully!');
            event.target.reset(); // Clear form
            loadEmployeeList(); // Refresh list
        } catch (error) {
            // Your API will likely return detailed errors (e.g., "username already exists")
            showMessage('danger', `Error adding employee: ${error.message}`);
        }
    }

    /**
     * Handles a click on a "Delete Employee" button.
     * @param {string} employeeId
     */
    async function handleDeleteEmployee(employeeId) {
        if (!confirm('Are you sure you want to delete this employee?')) {
            return;
        }
        try {
            await apiFetch(`/employee/${employeeId}/`, { // Assumes DELETE /api/employee/<id>/
                method: 'DELETE'
            });
            showMessage('success', 'Employee deleted.');
            loadEmployeeList(); // Refresh list
        } catch (error) {
            showMessage('danger', `Error deleting employee: ${error.message}`);
        }
    }

    // --- ATTENDANCE MANAGEMENT (for attendance_update.html) ---

    /**
     * Fetches the full employee list and today's attendance, then merges them.
     */
    async function loadAttendanceData() {
        const tbody = document.getElementById('attendance-tbody');
        const dateEl = document.getElementById('attendance-date');
        if (!tbody) return;

        try {
            // Step 1 & 2: Fetch both data sources at the same time
            const [employees, attendanceData] = await Promise.all([
                apiFetch('/employee/'),           // Assumes this is the FULL employee list
                apiFetch('/attendance/by_date/')  // Assumes this is just today's MARKED records
            ]);

            // Set the date (using the local date as a fallback)
            const today = new Date().toLocaleDateString('en-US', { 
                year: 'numeric', month: 'long', day: 'numeric' 
            });
            dateEl.textContent = attendanceData.date || today;
            
            // Step 3: Create a "lookup map" for quick access to attendance status
            // This is much faster than a nested loop.
            const attendanceMap = new Map();
            if (attendanceData && attendanceData.attendance) {
                attendanceData.attendance.forEach(item => {
                    attendanceMap.set(item.employee_id, item.status);
                });
            }

            tbody.innerHTML = ''; // Clear table

            // Step 4: Iterate over the FULL employee list
            if (!employees || employees.length === 0) {
                showMessage('warning', 'No employees found to mark attendance for.');
                return;
            }

            employees.forEach(employee => {
                // Step 5: "Merge" - Get the status from the map, or an empty string if not found
                
                const status = attendanceMap.get(employee.id) || ''; 

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>
                        ${employee.id}
                        <!-- This hidden input is the most important part for saving -->
                        <input type="hidden" name="employee_id" value="${employee.id}">
                    </td>
                    <td>
                        <!-- Get the name from the full employee list -->
                        ${employee.first_name} ${employee.last_name}
                    </td>
                    <td>
                        <select class="form-select form-select-sm" name="status">
                            <!-- This is the "empty field" if status is not set -->
                            <option value="" ${status === '' ? 'selected' : ''} disabled>Select...</option>
                            
                            <option value="present" ${status === 'present' ? 'selected' : ''}>Present</option>
                            <option value="absent" ${status === 'absent' ? 'selected' : ''}>Absent</option>
                            <option value="leave" ${status === 'leave' ? 'selected' : ''}>On Leave</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(tr);
                
                // Add color-coding logic
                const select = tr.querySelector('select');
                updateRowColor(select); // Color on load
                select.addEventListener('change', () => updateRowColor(select));
            });

        } catch (error) {
            showMessage('danger', `Error loading attendance: ${error.message}`);
        }
    }

    /**
     * Handles the "Save Attendance" form submission.
     */
    async function handleSaveAttendance(event) {
        event.preventDefault();
        const payload = [];
        const today = new Date().toLocaleDateString('sv-SE');
        document.querySelectorAll('#attendance-tbody tr').forEach(row => {
            payload.push({
                employee_id: row.querySelector('input[name="employee_id"]').value,
                status: row.querySelector('select[name="status"]').value,
                date: today,
            });
        });

        try {
            // Assumes POST /api/attendance/bulk_create_or_update/
            await apiFetch('/attendance/bulk_create_or_update/', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            showMessage('success', 'Attendance saved successfully!');
        } catch (error) {
            showMessage('danger', `Error saving attendance: ${error.message}`);
        }
    }
    
    /**
     * Updates a table row's color based on attendance status.
     */
    function updateRowColor(selectElement) {
        const selectedValue = selectElement.value.toLowerCase();
        const row = selectElement.closest('tr');
        
        // Always remove old colors
        row.classList.remove('table-success', 'table-danger', 'table-warning');

        // Add new color based on value
        if (selectedValue === 'present') {
        row.classList.add('table-success');
        } else if (selectedValue === 'absent') {
        row.classList.add('table-danger');
        } else if (selectedValue === 'leave') {
        row.classList.add('table-warning');
        }
        // If value is "" (empty), no color is added
    }

    // --- UTILITY FUNCTIONS ---

    /**
     * Displays a dismissible Bootstrap alert in the '#message-container'.
     * @param {'success' | 'danger' | 'warning' | 'info'} type
     * @param {string} message
     */
    function showMessage(type, message) {
        const container = document.getElementById('message-container');
        if (!container) {
            console.warn('No #message-container found on this partial.');
            return;
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show m-3`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.prepend(alert);
        
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    }
    
    /**
     * Updates the copyright year in the footer.
     */
    function updateFooterYear() {
        const yearEl = document.getElementById('current-year');
        if(yearEl) {
            yearEl.textContent = new Date().getFullYear();
        }
    }
    
    /**
     * Checks login state on initial page load.
     */
    async function checkInitialLoginState() {
        const username = localStorage.getItem('username');
        const role = localStorage.getItem('role');

        if (username && role) {
            // We have data, assume user is logged in
            // For a more robust app, you'd re-validate the token here
            updateNavbar(username);
            loadDashboardByRole(role);
        } else {
            // No data, user is logged out
            updateNavbar(null);
            loadPageContent('welcome');
        }
    }

    async function initPersonalAttendancePage() {
        try {
            // Call the new API endpoint
            const data = await apiFetch('/attendance/me/');
            if (!data.success) {
                throw new Error('API returned an error.');
            }

            // Populate header
            document.getElementById('att-full-name').textContent = `${data.employee.first_name} ${data.employee.last_name}`;
            document.getElementById('att-emp-id').textContent = String(data.employee.id).padStart(5, '0');

            // Populate summary boxes
            document.getElementById('att-total-days').textContent = data.summary.total_days;
            document.getElementById('att-present').textContent = data.summary.present_count;
            document.getElementById('att-absent').textContent = data.summary.absent_count;
            document.getElementById('att-leave').textContent = data.summary.leave_count;

            // Populate progress bar
            const percent = data.summary.attendance_percentage.toFixed(1);
            document.getElementById('att-percentage-label').textContent = percent;
            const progressBar = document.getElementById('att-progress-bar');
            progressBar.style.width = `${percent}%`;
            progressBar.setAttribute('aria-valuenow', percent);
            document.getElementById('att-percentage-bar').textContent = `${percent}%`;

            // Populate history table
            const historyBody = document.getElementById('att-history-body');
            historyBody.innerHTML = ''; // Clear any old data
            
            if (data.history.length === 0) {
                historyBody.innerHTML = `
                    <tr>
                      <td colspan="2" class="text-center text-muted">No attendance records found.</td>
                    </tr>
                `;
                return;
            }

            // Use the formatFullDate function you already have
            data.history.forEach(record => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${formatFullDate(record.date)}</td>
                    <td>${formatHistoryStatusBadge(record.status)}</td>
                `;
                historyBody.appendChild(tr);
            });

        } catch (error) {
            showMessage('danger', `Could not load attendance report: ${error.message}`);
        }
    }
    
    // --- GLOBAL EVENT LISTENERS (Using Event Delegation) ---

    // Listen for all clicks on the document
    document.body.addEventListener('click', (event) => {
        const target = event.target;
        
        // --- Navigation clicks ---
        const navLogin = target.closest('#nav-login-button') || target.closest('#welcome-login-button');
        if (navLogin) {
            event.preventDefault();
            loadPageContent('login');
        }
        
        if (target.closest('#logout-button')) {
            handleLogout();
        }
        
        if (target.closest('#nav-attendance-button')) {
            loadPageContent('attendance_update');
        }

        if (target.closest('#nav-back-to-hr')) {
            loadPageContent('employee_form');
        }

        // --- Action clicks ---
        const deleteBtn = target.closest('.delete-employee');
        if (deleteBtn) {
            event.preventDefault();
            handleDeleteEmployee(deleteBtn.dataset.id);
        }

        // --- Handle Edit Photo buttons ---
        const editPhotoBtn = event.target.closest('.edit-photo-btn');
        if (editPhotoBtn) {
            event.preventDefault();
            // Trigger the hidden file input
            document.getElementById('photo-upload-input').click();
        }

        const navMyAttendance = event.target.closest('#nav-my-attendance');
        if (navMyAttendance) {
            event.preventDefault();
            loadPageContent('personal_attendance');
        }
        
        // For the "Back" button on the attendance page
        const navBackToProfile = event.target.closest('#nav-back-to-profile');
        if (navBackToProfile) {
            event.preventDefault();
            loadPageContent('employee_detail');
        }
    });

    // Listen for all form submissions on the document
    document.body.addEventListener('submit', (event) => {
        if (event.target.id === 'login-form') {
            handleLogin(event);
        }
        
        if (event.target.id === 'add-employee-form') {
            handleAddEmployee(event);
        }
        
        if (event.target.id === 'attendance-form') {
            handleSaveAttendance(event);
        }
    });

    // --- INITIALIZATION ---
    updateFooterYear();
    checkInitialLoginState();
});