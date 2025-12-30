class AuthSystem {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('auth_user') || 'null');
        this.init();
    }

    init() {
        this.checkAuthState();
        this.setupEventListeners();
    }

    checkAuthState() {
        if (this.token) {
            this.verifyToken();
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateTo(link.dataset.page);
            });
        });

        // Forms
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Admin actions and other delegated button handlers
        document.addEventListener('click', (e) => {
            const updateBtn = e.target.closest('.update-role-btn');
            if (updateBtn) {
                this.handleUpdateRole({ ...e, target: updateBtn });
                return;
            }

            const refreshBtn = e.target.closest('#refreshUsers');
            if (refreshBtn) {
                if (typeof window.loadUsers === 'function') window.loadUsers();
                return;
            }

            const addUserBtn = e.target.closest('#addUserBtn');
            if (addUserBtn) {
                if (typeof window.showAddUserForm === 'function') window.showAddUserForm();
                else this.showAlert("Fonction d'ajout d'utilisateur à venir", 'alert-info');
                return;
            }
        });
    }

    navigateTo(page) {
        window.location.href = `${page}.html`;
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const formData = {
            username: form.querySelector('#username').value,
            email: form.querySelector('#email').value,
            password: form.querySelector('#password').value,
            role: form.querySelector('#role').value
        };

        this.showAlert('', 'alert-success');

        try {
            const response = await this.makeRequest('/register', 'POST', formData);
            if (response.success) {
                this.showAlert('Registration successful! Please login.', 'alert-success');
                form.reset();
                setTimeout(() => this.navigateTo('login'), 2000);
            } else {
                this.showAlert(response.message, 'alert-error');
            }
        } catch (error) {
            this.showAlert('Registration failed. Please try again.', 'alert-error');
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const formData = {
            username: form.querySelector('#username').value,
            password: form.querySelector('#password').value
        };

        this.showAlert('', 'alert-success');

        try {
            const response = await this.makeRequest('/login', 'POST', formData);
            if (response.success) {
                this.token = response.data.token;
                this.user = response.data.user;
                
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('auth_user', JSON.stringify(this.user));
                
                this.showAlert('Login successful! Redirecting...', 'alert-success');
                setTimeout(() => this.navigateTo('dashboard'), 1500);
            } else {
                this.showAlert(response.message, 'alert-error');
            }
        } catch (error) {
            this.showAlert('Login failed. Please check your credentials.', 'alert-error');
        }
    }

    async handleLogout() {
        if (!this.token) return;

        try {
            await this.makeRequest('/logout', 'POST', { token: this.token });
        } catch (error) {
            // Ignore logout errors
        }

        this.clearAuth();
        this.navigateTo('index');
    }

    async verifyToken() {
        if (!this.token) return false;

        try {
            const response = await this.makeRequest('/verify', 'GET', null, true);
            if (response.success) {
                return true;
            }
        } catch (error) {
            // Token invalid or expired
        }

        this.clearAuth();
        return false;
    }

    async loadUsers() {
        if (!await this.verifyToken() || this.user.role !== 'admin') {
            return;
        }

        try {
            const response = await this.makeRequest('/users', 'GET', null, true);
            if (response.success) {
                this.displayUsers(response.data);
            }
        } catch (error) {
            console.error('Failed to load users:', error);
        }
    }

    async handleUpdateRole(e) {
        if (e && typeof e.preventDefault === 'function') e.preventDefault();
        const btn = e.target.closest ? e.target.closest('.update-role-btn') : e.target;
        if (!btn) return;
        const userId = btn.dataset.userId;
        const newRole = btn.dataset.newRole || btn.dataset.currentRole;

        if (!newRole) return;

        if (!confirm(`Voulez-vous vraiment changer le rôle de cet utilisateur en ${newRole} ?`)) {
            return;
        }

        try {
            const response = await this.makeRequest('/users/update-role', 'POST', {
                user_id: userId,
                new_role: newRole
            }, true);

            if (response.success) {
                this.showAlert('User role updated successfully!', 'alert-success');
                this.loadUsers();
            } else {
                this.showAlert(response.message, 'alert-error');
            }
        } catch (error) {
            this.showAlert('Failed to update user role', 'alert-error');
        }
    }

    displayUsers(users) {
        const tbody = document.querySelector('#usersTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            
            const actions = this.user.role === 'admin' && user.id !== this.user.id
                ? `<button class="btn update-role-btn" data-user-id="${user.id}" data-new-role="${user.role === 'admin' ? 'user' : 'admin'}">
                    Make ${user.role === 'admin' ? 'User' : 'Admin'}
                   </button>`
                : '';

            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td><span class="role-badge role-${user.role}">${user.role}</span></td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>${actions}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updateUI() {
        // Update user info in dashboard
        const userInfoElement = document.getElementById('userInfo');
        if (userInfoElement && this.user) {
            userInfoElement.innerHTML = `
                <strong>${this.user.username}</strong>
                <span class="role-badge role-${this.user.role}">${this.user.role}</span>
                <span>${this.user.email}</span>
            `;
        }

        // Show/hide admin section
        const adminSection = document.getElementById('adminSection');
        if (adminSection) {
            adminSection.classList.toggle('hidden', this.user?.role !== 'admin');
        }

        // Update navigation based on auth state
        document.querySelectorAll('.auth-only').forEach(el => {
            el.classList.toggle('hidden', !this.token);
        });
        
        document.querySelectorAll('.guest-only').forEach(el => {
            el.classList.toggle('hidden', !!this.token);
        });
    }

    async makeRequest(endpoint, method, data = null, auth = false) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (auth && this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return await response.json();
    }

    showAlert(message, className) {
        const alertDiv = document.getElementById('alert');
        if (alertDiv) {
            alertDiv.className = `alert ${className}`;
            alertDiv.textContent = message;
            alertDiv.classList.toggle('hidden', !message);
        }
    }

    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        this.updateUI();
    }

    // Public methods for page initialization
    initDashboard() {
        if (!this.token) {
            this.navigateTo('login');
            return;
        }

        this.updateUI();
        if (this.user?.role === 'admin') {
            this.loadUsers();
        }
    }

    initLoginPage() {
        if (this.token) {
            this.navigateTo('dashboard');
        }
        this.updateUI();
    }

    initRegisterPage() {
        if (this.token) {
            this.navigateTo('dashboard');
        }
        this.updateUI();
    }
}

// Initialize auth system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.auth = new AuthSystem();
    
    // Initialize specific page
    const currentPage = window.location.pathname.split('/').pop().split('.')[0];
    
    switch(currentPage) {
        case 'dashboard':
        case 'admin':
            window.auth.initDashboard();
            break;
        case 'login':
            window.auth.initLoginPage();
            break;
        case 'register':
            window.auth.initRegisterPage();
            break;
        default:
            window.auth.updateUI();
    }
});