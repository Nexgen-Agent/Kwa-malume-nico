/**
 * auth.js - Authentication management for Malume Nico
 * Handles registration, login, and session management using localStorage.
 */

const AUTH_KEY = 'malume_nico_auth_session';
const USERS_KEY = 'malume_nico_users';

const Auth = {
    /**
     * Get the currently logged in user
     */
    getUser: function() {
        const session = localStorage.getItem(AUTH_KEY);
        return session ? JSON.parse(session) : null;
    },

    /**
     * Check if a user is logged in
     */
    isLoggedIn: function() {
        return this.getUser() !== null;
    },

    /**
     * Register a new user
     */
    register: function(email, password, name = '') {
        // Basic validation
        if (!this.validateEmail(email)) {
            return { success: false, error: 'Invalid email' };
        }
        if (password.length < 6) {
            return { success: false, error: 'Password must be at least 6 characters' };
        }

        const users = this.getAllUsers();
        if (users.find(u => u.email === email)) {
            return { success: false, error: 'Account already exists' };
        }

        const newUser = {
            email: email,
            password: this.mockHash(password), // Mock hash for security demonstration
            name: name,
            coupon_eligible: true, // Mark as eligible for rewards/coupons
            created_at: new Date().toISOString()
        };

        users.push(newUser);
        localStorage.setItem(USERS_KEY, JSON.stringify(users));

        // Automatically log in after registration
        return this.login(email, password);
    },

    /**
     * Login a user
     */
    login: function(email, password) {
        const users = this.getAllUsers();
        const hashedPassword = this.mockHash(password);
        const user = users.find(u => u.email === email && u.password === hashedPassword);

        if (!user) {
            return { success: false, error: 'Login failure' };
        }

        // Create session (excluding password)
        const sessionUser = { ...user };
        delete sessionUser.password;

        localStorage.setItem(AUTH_KEY, JSON.stringify(sessionUser));
        return { success: true, user: sessionUser };
    },

    /**
     * Logout
     */
    logout: function() {
        localStorage.removeItem(AUTH_KEY);
        window.location.reload();
    },

    /**
     * Simulated Google Login
     */
    loginWithGoogle: function() {
        console.log('Google login placeholder');
        // Simulate successful redirect/login for demo
        return this.register('google_user@example.com', 'google_oauth_placeholder', 'Google User');
    },

    /**
     * Simulated Facebook Login
     */
    loginWithFacebook: function() {
        console.log('Facebook login placeholder');
        // Simulate successful redirect/login for demo
        return this.register('fb_user@example.com', 'fb_oauth_placeholder', 'Facebook User');
    },

    /**
     * Helper: Get all registered users from localStorage
     */
    getAllUsers: function() {
        const users = localStorage.getItem(USERS_KEY);
        return users ? JSON.parse(users) : [];
    },

    /**
     * Helper: Validate email format
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Mock hashing for security demonstration
     */
    mockHash: function(str) {
        // Simple base64 "hash" for demonstration in a static mockup
        // In a real app, use SHA-256 or bcrypt on the server
        return btoa('salt_' + str).split('').reverse().join('');
    }
};

// Export for use in other scripts if needed, though we'll use it globally for this static site
if (typeof window !== 'undefined') {
    window.Auth = Auth;
}
