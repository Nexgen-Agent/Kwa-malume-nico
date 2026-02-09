/**
 * Simulated Authentication Module for Malume Nico
 * Handles user registration, login, and session management using localStorage.
 */

const Auth = {
    // Current session key
    SESSION_KEY: 'mn_user_session',
    // Registered users key
    USERS_KEY: 'mn_registered_users',

    /**
     * Initialize authentication state
     */
    init() {
        console.log('Auth module initialized');
        // Check for existing session
        this.getCurrentUser();
    },

    /**
     * Register a new user with email and password
     */
    signUpWithEmail(email, password, name = '') {
        return new Promise((resolve, reject) => {
            // Basic validation
            if (!email || !email.includes('@')) {
                return reject({ message: 'Invalid email address' });
            }
            if (!password || password.length < 6) {
                return reject({ message: 'Password must be at least 6 characters' });
            }

            const users = this._getUsers();
            if (users[email]) {
                return reject({ message: 'Account already exists' });
            }

            // Create new user
            const newUser = {
                email,
                password, // In a real app, this would be hashed on the server
                name: name || email.split('@')[0],
                createdAt: new Date().toISOString()
            };

            users[email] = newUser;
            this._saveUsers(users);

            // Auto-login after signup
            this._createSession(newUser);
            resolve(newUser);
        });
    },

    /**
     * Login with email and password
     */
    loginWithEmail(email, password) {
        return new Promise((resolve, reject) => {
            const users = this._getUsers();
            const user = users[email];

            if (!user || user.password !== password) {
                return reject({ message: 'Invalid email or password' });
            }

            this._createSession(user);
            resolve(user);
        });
    },

    /**
     * Simulated OAuth login (Google/Facebook)
     */
    loginWithOAuth(provider) {
        return new Promise((resolve) => {
            console.log(`Connecting to ${provider}...`);

            // Mocking a delay for OAuth popup/redirect
            setTimeout(() => {
                const mockUser = {
                    email: `user_${provider}@example.com`,
                    name: `${provider} User`,
                    provider: provider,
                    createdAt: new Date().toISOString()
                };

                // Save or update user in our simulated DB
                const users = this._getUsers();
                users[mockUser.email] = mockUser;
                this._saveUsers(users);

                this._createSession(mockUser);
                resolve(mockUser);
            }, 1000);
        });
    },

    /**
     * Get the currently logged in user
     */
    getCurrentUser() {
        const session = localStorage.getItem(this.SESSION_KEY);
        if (!session) return null;

        try {
            return JSON.parse(session);
        } catch (e) {
            console.error('Failed to parse session', e);
            return null;
        }
    },

    /**
     * Logout current user
     */
    logout() {
        localStorage.removeItem(this.SESSION_KEY);
        console.log('User logged out');
    },

    /**
     * Helper to get all users from localStorage
     */
    _getUsers() {
        const users = localStorage.getItem(this.USERS_KEY);
        return users ? JSON.parse(users) : {};
    },

    /**
     * Helper to save users to localStorage
     */
    _saveUsers(users) {
        localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
    },

    /**
     * Helper to create a session
     */
    _createSession(user) {
        // Don't store password in session
        const sessionUser = { ...user };
        delete sessionUser.password;
        localStorage.setItem(this.SESSION_KEY, JSON.stringify(sessionUser));
    }
};

// Initialize auth
Auth.init();

// Export to window for global access
window.Auth = Auth;
