/**
 * AuthService - Handles authentication and session management
 */
const AuthService = {
    /**
     * Simulate user registration
     */
    register: async (email, password, name) => {
        return new Promise((resolve, reject) => {
            console.log('Registering user:', email);
            setTimeout(() => {
                // Network error simulation (1 in 10 chance)
                if (Math.random() < 0.1) {
                    reject(new Error('Network error. Please try again later.'));
                    return;
                }

                if (!email || !email.includes('@')) {
                    reject(new Error('Invalid email address.'));
                    return;
                }

                const users = JSON.parse(localStorage.getItem('users') || '[]');
                if (users.find(u => u.email === email)) {
                    reject(new Error('Account already exists with this email.'));
                    return;
                }

                const newUser = {
                    id: 'user_' + Date.now(),
                    email,
                    password, // In a real app, never store plain text passwords
                    name,
                    coupons: 1500, // Welcome bonus
                    createdAt: new Date().toISOString()
                };

                users.push(newUser);
                localStorage.setItem('users', JSON.stringify(users));
                localStorage.setItem('currentUser', JSON.stringify(newUser));
                resolve(newUser);
            }, 1000);
        });
    },

    /**
     * Simulate user login
     */
    login: async (email, password) => {
        return new Promise((resolve, reject) => {
            console.log('Logging in user:', email);
            setTimeout(() => {
                // Network error simulation
                if (Math.random() < 0.1) {
                    reject(new Error('Network error. Please try again later.'));
                    return;
                }

                const users = JSON.parse(localStorage.getItem('users') || '[]');
                const user = users.find(u => u.email === email && u.password === password);

                if (user) {
                    localStorage.setItem('currentUser', JSON.stringify(user));
                    resolve(user);
                } else {
                    reject(new Error('Invalid email or password.'));
                }
            }, 1000);
        });
    },

    /**
     * Logout user
     */
    logout: () => {
        localStorage.removeItem('currentUser');
    },

    /**
     * Get currently logged in user
     */
    getCurrentUser: () => {
        return JSON.parse(localStorage.getItem('currentUser'));
    },

    /**
     * Check if user is logged in
     */
    isLoggedIn: () => {
        return AuthService.getCurrentUser() !== null;
    },

    /**
     * OAuth Login Placeholders
     */
    loginWithGoogle: async () => {
        return AuthService.simulateOAuth('Google');
    },

    loginWithFacebook: async () => {
        return AuthService.simulateOAuth('Facebook');
    },

    loginWithApple: async () => {
        return AuthService.simulateOAuth('Apple');
    },

    simulateOAuth: async (provider) => {
        return new Promise((resolve, reject) => {
            console.log(`Logging in with ${provider}...`);
            setTimeout(() => {
                if (Math.random() < 0.05) {
                    reject(new Error(`${provider} authentication failed.`));
                    return;
                }

                const user = {
                    id: provider.toLowerCase() + '_' + Date.now(),
                    email: `${provider.toLowerCase()}_user@example.com`,
                    name: `${provider} User`,
                    coupons: 1500,
                    provider: provider,
                    createdAt: new Date().toISOString()
                };

                localStorage.setItem('currentUser', JSON.stringify(user));
                resolve(user);
            }, 1000);
        });
    },

    /**
     * Update user coupons
     */
    updateCoupons: (amount) => {
        const user = AuthService.getCurrentUser();
        if (user) {
            user.coupons += amount;
            localStorage.setItem('currentUser', JSON.stringify(user));

            // Also update in users list
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            const index = users.findIndex(u => u.id === user.id);
            if (index !== -1) {
                users[index].coupons = user.coupons;
                localStorage.setItem('users', JSON.stringify(users));
            }
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthService;
}
