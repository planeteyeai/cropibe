// Global variables
let currentUser = null;
let token = null;
let otpEmail = null;

// API endpoints
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const API_ENDPOINTS = {
    login: '/token/',
    otp: '/users/otp/',
    verifyOtp: '/users/verify-otp/',
    users: '/users/',
    tasks: '/tasks/',
    equipment: '/equipment/',
    bookings: '/bookings/',
    maintenance: '/equipment/maintenance-records/',
    usage: '/equipment/usage-records/',
    comments: '/bookings/comments/',
    attachments: '/bookings/attachments/'
};

// Utility functions
const showToast = (message, type = 'success') => {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
};

const showLoading = () => {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loading-spinner';
    document.body.appendChild(spinner);
};

const hideLoading = () => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        document.body.removeChild(spinner);
    }
};

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
};

// API calls
const apiCall = async (endpoint, method = 'GET', data = null) => {
    try {
        showLoading();
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };

        const options = {
            method,
            headers
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'An error occurred');
        }

        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
};

// Authentication
const login = async (username, password) => {
    try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.login}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        token = data.access;
        currentUser = await apiCall('/users/me/');
        showToast('Login successful');
        showDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    }
};

// OTP Functions
const showOTPForm = () => {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('otp-form').style.display = 'block';
};

const showLoginForm = () => {
    document.getElementById('otp-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('otp-input-container').style.display = 'none';
    document.getElementById('verify-otp-btn').style.display = 'none';
    document.getElementById('email').value = '';
    document.getElementById('otp').value = '';
};

const sendOTP = async () => {
    try {
        const email = document.getElementById('email').value;
        if (!email) {
            showToast('Please enter your email', 'error');
            return;
        }

        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.otp}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to send OTP');
        }

        otpEmail = email;
        document.getElementById('otp-input-container').style.display = 'block';
        document.getElementById('verify-otp-btn').style.display = 'block';
        showToast('OTP sent successfully');
    } catch (error) {
        showToast(error.message, 'error');
    }
};

const verifyOTP = async () => {
    try {
        const otp = document.getElementById('otp').value;
        if (!otp) {
            showToast('Please enter the OTP', 'error');
            return;
        }

        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.verifyOtp}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: otpEmail, otp })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Invalid OTP');
        }

        token = data.access;
        currentUser = await apiCall('/users/me/');
        showToast('Login successful');
        showDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    }
};

// UI Functions
const showDashboard = () => {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    document.getElementById('user-info').textContent = `Welcome, ${currentUser.username}`;
    loadDashboardData();
};

const loadDashboardData = async () => {
    try {
        const [users, tasks, equipment, bookings] = await Promise.all([
            apiCall(API_ENDPOINTS.users),
            apiCall(API_ENDPOINTS.tasks),
            apiCall(API_ENDPOINTS.equipment),
            apiCall(API_ENDPOINTS.bookings)
        ]);

        updateDashboardStats(users, tasks, equipment, bookings);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
};

const updateDashboardStats = (users, tasks, equipment, bookings) => {
    document.getElementById('total-users').textContent = users.count;
    document.getElementById('total-tasks').textContent = tasks.count;
    document.getElementById('total-equipment').textContent = equipment.count;
    document.getElementById('total-bookings').textContent = bookings.count;
};

// Users Management
const loadUsers = async () => {
    try {
        const users = await apiCall(API_ENDPOINTS.users);
        const tbody = document.querySelector('#users-table tbody');
        tbody.innerHTML = '';

        users.results.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Populate user select dropdowns
        const userSelects = document.querySelectorAll('select[name="assigned_to"]');
        userSelects.forEach(select => {
            select.innerHTML = '<option value="">Select User</option>';
            users.results.forEach(user => {
                select.innerHTML += `<option value="${user.id}">${user.username}</option>`;
            });
        });
    } catch (error) {
        console.error('Error loading users:', error);
    }
};

const createUser = async (formData) => {
    try {
        await apiCall(API_ENDPOINTS.users, 'POST', formData);
        showToast('User created successfully');
        $('#createUserModal').modal('hide');
        loadUsers();
    } catch (error) {
        console.error('Error creating user:', error);
    }
};

// Tasks Management
const loadTasks = async () => {
    try {
        const tasks = await apiCall(API_ENDPOINTS.tasks);
        const tbody = document.querySelector('#tasks-table tbody');
        tbody.innerHTML = '';

        tasks.results.forEach(task => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${task.title}</td>
                <td>${task.description}</td>
                <td><span class="status-badge status-${task.status.toLowerCase()}">${task.status}</span></td>
                <td>${formatDate(task.due_date)}</td>
                <td>${task.assigned_to?.username || 'Unassigned'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="editTask(${task.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
};

const createTask = async (formData) => {
    try {
        await apiCall(API_ENDPOINTS.tasks, 'POST', formData);
        showToast('Task created successfully');
        $('#createTaskModal').modal('hide');
        loadTasks();
    } catch (error) {
        console.error('Error creating task:', error);
    }
};

// Equipment Management
const loadEquipment = async () => {
    try {
        const equipment = await apiCall(API_ENDPOINTS.equipment);
        const tbody = document.querySelector('#equipment-table tbody');
        tbody.innerHTML = '';

        equipment.results.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.name}</td>
                <td>${item.type}</td>
                <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                <td>${item.assigned_to?.username || 'Unassigned'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="editEquipment(${item.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEquipment(${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading equipment:', error);
    }
};

const createEquipment = async (formData) => {
    try {
        await apiCall(API_ENDPOINTS.equipment, 'POST', formData);
        showToast('Equipment created successfully');
        $('#createEquipmentModal').modal('hide');
        loadEquipment();
    } catch (error) {
        console.error('Error creating equipment:', error);
    }
};

// Bookings Management
const loadBookings = async () => {
    try {
        const bookings = await apiCall(API_ENDPOINTS.bookings);
        const tbody = document.querySelector('#bookings-table tbody');
        tbody.innerHTML = '';

        bookings.results.forEach(booking => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${booking.title}</td>
                <td>${booking.description}</td>
                <td><span class="status-badge status-${booking.status.toLowerCase()}">${booking.status}</span></td>
                <td>${formatDate(booking.start_date)}</td>
                <td>${formatDate(booking.end_date)}</td>
                <td>${booking.created_by?.username || 'Unknown'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="editBooking(${booking.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteBooking(${booking.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
};

const createBooking = async (formData) => {
    try {
        await apiCall(API_ENDPOINTS.bookings, 'POST', formData);
        showToast('Booking created successfully');
        $('#createBookingModal').modal('hide');
        loadBookings();
    } catch (error) {
        console.error('Error creating booking:', error);
    }
};

// Logout
const logout = () => {
    token = null;
    currentUser = null;
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    showLoginForm();
    showToast('Logged out successfully');
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        login(username, password);
    });

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = e.target.getAttribute('data-section');
            showSection(section);
        });
    });

    // Create forms
    document.getElementById('create-user-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        createUser(Object.fromEntries(formData));
    });

    document.getElementById('create-task-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        createTask(Object.fromEntries(formData));
    });

    document.getElementById('create-equipment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        createEquipment(Object.fromEntries(formData));
    });

    document.getElementById('create-booking-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        createBooking(Object.fromEntries(formData));
    });
});

// Section Navigation
const showSection = (section) => {
    document.querySelectorAll('.content-section').forEach(s => {
        s.style.display = 'none';
    });
    document.getElementById(`${section}-section`).style.display = 'block';

    switch (section) {
        case 'users':
            loadUsers();
            break;
        case 'tasks':
            loadTasks();
            break;
        case 'equipment':
            loadEquipment();
            break;
        case 'bookings':
            loadBookings();
            break;
    }
}; 