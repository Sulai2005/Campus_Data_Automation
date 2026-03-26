/**
 * Authentication utilities and API helpers
 */

const API_BASE_URL = '/api';

/**
 * Get JWT token from localStorage
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Set JWT token in localStorage
 */
function setToken(token) {
    localStorage.setItem('token', token);
}

/**
 * Remove JWT token from localStorage
 */
function removeToken() {
    localStorage.removeItem('token');
}

/**
 * Get user role from localStorage
 */
function getUserRole() {
    return localStorage.getItem('role');
}

/**
 * Set user role in localStorage
 */
function setUserRole(role) {
    localStorage.setItem('role', role);
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return getToken() !== null;
}

/**
 * Logout user
 */
function logout() {
    removeToken();
    localStorage.removeItem('role');
    window.location.href = '/';
}

/**
 * Make authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    // Don't set Content-Type for FormData – browser sets it automatically with the boundary
    const isFormData = options.body instanceof FormData;

    const defaultHeaders = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token && { 'Authorization': `Bearer ${token}` })
    };

    const mergedOptions = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);

        // Handle 401 Unauthorized
        if (response.status === 401) {
            removeToken();
            window.location.href = '/';
            throw new Error('Unauthorized');
        }

        // Handle 403 Forbidden
        if (response.status === 403) {
            throw new Error('Access denied');
        }

        return response;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Make authenticated API request and return JSON
 */
async function apiRequestJSON(endpoint, options = {}) {
    const response = await apiRequest(endpoint, options);
    return await response.json();
}

/**
 * Require authentication - redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/';
    }
}

/**
 * Require specific role - redirect if role doesn't match
 */
function requireRole(requiredRole) {
    requireAuth();
    const userRole = getUserRole();
    if (userRole !== requiredRole) {
        alert('Access denied. You do not have permission to view this page.');
        logout();
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    // Insert at top of container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
