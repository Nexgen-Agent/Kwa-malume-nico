/**
 * auth.js - Authentication management for Malume Nico
 * Connects to the FastAPI backend.
 */

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://api.malumenico.com'; // Placeholder for production URL

const AUTH_KEY = 'malume_nico_auth_token';
const USER_KEY = 'malume_nico_user_data';

const Auth = {
    /**
     * Get the currently logged in user from local storage
     */
    getUser: function() {
        const userData = localStorage.getItem(USER_KEY);
        return userData ? JSON.parse(userData) : null;
    },

    /**
     * Get the access token
     */
    getToken: function() {
        return localStorage.getItem(AUTH_KEY);
    },

    /**
     * Check if a user is logged in
     */
    isLoggedIn: function() {
        return this.getToken() !== null;
    },

    /**
     * Register a new user
     */
    register: async function(email, password, name = '') {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: name })
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { success: false, error: errorData.detail || 'Registration failed' };
            }

            // After registration, log in
            return await this.login(email, password);
        } catch (error) {
            return { success: false, error: 'Network error connecting to backend' };
        }
    },

    /**
     * Login a user
     */
    login: async function(email, password) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { success: false, error: errorData.detail || 'Login failure' };
            }

            const data = await response.json();
            localStorage.setItem(AUTH_KEY, data.access_token);

            // Get user profile
            const profileResponse = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${data.access_token}` }
            });

            if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                localStorage.setItem(USER_KEY, JSON.stringify(profileData));
            } else {
                // Fallback if profile fetch fails
                localStorage.setItem(USER_KEY, JSON.stringify({
                    email: email,
                    full_name: email.split('@')[0],
                    coupon_eligible: true
                }));
            }

            return { success: true };
        } catch (error) {
            return { success: false, error: 'Network error connecting to backend' };
        }
    },

    /**
     * Logout
     */
    logout: function() {
        localStorage.removeItem(AUTH_KEY);
        localStorage.removeItem(USER_KEY);
        window.location.reload();
    },

    /**
     * Simulated Google Login
     */
    loginWithGoogle: async function() {
        const response = await fetch(`${API_BASE_URL}/auth/google`, { method: 'POST' });
        const data = await response.json();
        alert(data.message);
        return { success: false, error: 'OAuth not fully implemented' };
    },

    /**
     * Simulated Facebook Login
     */
    loginWithFacebook: async function() {
        const response = await fetch(`${API_BASE_URL}/auth/facebook`, { method: 'POST' });
        const data = await response.json();
        alert(data.message);
        return { success: false, error: 'OAuth not fully implemented' };
    }
};

if (typeof window !== 'undefined') {
    window.Auth = Auth;
}
