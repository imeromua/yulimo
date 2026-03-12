/* ===========================
   YULIMO Admin — Auth utilities
   =========================== */

const TOKEN_KEY = 'admin_token';

/**
 * Get the stored JWT access token.
 * @returns {string|null}
 */
export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Save the JWT access token.
 * @param {string} token
 */
export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the stored token (logout).
 */
export function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * Redirect to login page if no token is present.
 * @returns {boolean} true if authenticated, false if redirected
 */
export function requireAuth() {
    if (!getToken()) {
        window.location.replace('/admin/login.html');
        return false;
    }
    return true;
}

/**
 * Log out: clear token and redirect to login.
 */
export function logout() {
    clearToken();
    window.location.replace('/admin/login.html');
}
