const API_URL = '';

// Toast Notification System
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 'alert-circle';
    
    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    if(window.lucide) lucide.createIcons({ root: toast });
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Auth Logic
function switchTab(tab) {
    if(tab === 'login') {
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('registerForm').classList.add('hidden');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.remove('active');
    } else {
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.remove('hidden');
        document.querySelectorAll('.tab-btn')[0].classList.remove('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }
}

const loginForm = document.getElementById('loginForm');
if(loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams();
        formData.append('username', document.getElementById('loginUsername').value);
        formData.append('password', document.getElementById('loginPassword').value);

        try {
            const res = await fetch(`${API_URL}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            const data = await res.json();
            if(res.ok) {
                localStorage.setItem('access_token', data.access_token);
                window.location.href = 'dashboard.html';
            } else {
                document.getElementById('loginError').innerText = data.detail;
            }
        } catch(err) {
            document.getElementById('loginError').innerText = 'Server error. Is the backend running?';
        }
    });
}

const registerForm = document.getElementById('registerForm');
if(registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('regName').value,
            username: document.getElementById('regUsername').value,
            email: document.getElementById('regEmail').value,
            age: parseInt(document.getElementById('regAge').value),
            contact: document.getElementById('regContact').value,
            password: document.getElementById('regPassword').value
        };

        try {
            const res = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(res.ok) {
                switchTab('login');
                document.getElementById('loginUsername').value = payload.username;
                showToast('Registration successful! Please login.', 'success');
            } else {
                document.getElementById('regError').innerText = data.detail;
            }
        } catch(err) {
            document.getElementById('regError').innerText = 'Server error.';
        }
    });
}

// Dashboard Logic
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = 'index.html';
}

let currentUserData = null;

async function fetchUserData() {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if(res.ok) {
        const user = await res.json();
        currentUserData = user;
        document.getElementById('userNameDisplay').innerText = `Welcome, ${user.name}`;
    }
}

// Profile Logic
function openProfileModal() {
    if (currentUserData) {
        document.getElementById('profName').value = currentUserData.name;
        document.getElementById('profUsername').value = currentUserData.username;
        document.getElementById('profEmail').value = currentUserData.email;
        document.getElementById('profAge').value = currentUserData.age;
        document.getElementById('profContact').value = currentUserData.contact;
    }
    document.getElementById('profError').innerText = '';
    document.getElementById('profSuccess').innerText = '';
    document.getElementById('profileModal').classList.remove('hidden');
}

function closeProfileModal() {
    document.getElementById('profileModal').classList.add('hidden');
}

const profileForm = document.getElementById('profileForm');
if(profileForm) {
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('profName').value,
            email: document.getElementById('profEmail').value,
            age: parseInt(document.getElementById('profAge').value),
            contact: document.getElementById('profContact').value
        };

        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_URL}/users/me`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(res.ok) {
                document.getElementById('profSuccess').innerText = 'Profile updated successfully!';
                document.getElementById('profError').innerText = '';
                fetchUserData(); // Refresh the displayed name
                setTimeout(closeProfileModal, 1500);
            } else {
                document.getElementById('profError').innerText = data.detail || 'Update failed';
                document.getElementById('profSuccess').innerText = '';
            }
        } catch(err) {
            document.getElementById('profError').innerText = 'Server error.';
            document.getElementById('profSuccess').innerText = '';
        }
    });
}

let allAvailableSymptoms = [];
let symptomsList = [];

function addSymptom(val) {
    if(val && !symptomsList.includes(val)) {
        symptomsList.push(val);
        renderSymptoms();
    }
    const input = document.getElementById('symptomSearchInput');
    if(input) input.value = '';
    const dropdown = document.getElementById('symptomDropdownList');
    if(dropdown) dropdown.classList.add('hidden');
}

function showDropdown() {
    const dropdown = document.getElementById('symptomDropdownList');
    if(dropdown) dropdown.classList.remove('hidden');
    filterSymptoms();
}

document.addEventListener('click', function(e) {
    const searchArea = document.querySelector('.custom-search');
    if(searchArea && !searchArea.contains(e.target)) {
        const dropdown = document.getElementById('symptomDropdownList');
        if(dropdown) dropdown.classList.add('hidden');
    }
});

function filterSymptoms() {
    const inputStr = document.getElementById('symptomSearchInput').value.toLowerCase();
    const dropdown = document.getElementById('symptomDropdownList');
    if(!dropdown) return;
    dropdown.innerHTML = '';
    
    const filtered = allAvailableSymptoms.filter(s => 
        s.toLowerCase().includes(inputStr) && !symptomsList.includes(s)
    );
    
    if(filtered.length === 0) {
        dropdown.innerHTML = '<div class="custom-dropdown-item" style="color:var(--text-muted); cursor:default;">No symptoms found</div>';
        return;
    }
    
    filtered.forEach(s => {
        const div = document.createElement('div');
        div.className = 'custom-dropdown-item';
        div.innerText = s;
        div.onclick = function() {
            addSymptom(s);
        };
        dropdown.appendChild(div);
    });
}

function removeSymptom(symp) {
    symptomsList = symptomsList.filter(s => s !== symp);
    renderSymptoms();
}

function renderSymptoms() {
    const container = document.getElementById('selectedSymptoms');
    if(!container) return;
    container.innerHTML = '';
    symptomsList.forEach(s => {
        const div = document.createElement('div');
        div.className = 'tag';
        div.innerHTML = `${s} <i data-lucide="x" onclick="removeSymptom('${s}')" style="width: 14px; height: 14px; cursor: pointer; color: var(--text-light); transition: color 0.2s;" onmouseover="this.style.color='var(--danger)'" onmouseout="this.style.color='var(--text-light)'"></i>`;
        container.appendChild(div);
    });
    if (window.lucide) {
        lucide.createIcons();
    }
}

let latestPrediction = null;

async function predictDisease() {
    if(symptomsList.length === 0) {
        showToast("Please add at least one symptom.", 'error');
        return;
    }
    
    const token = localStorage.getItem('access_token');
    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ symptoms: symptomsList })
        });
        
        const data = await res.json();
        if(res.ok) {
            latestPrediction = {
                symptoms: symptomsList,
                predicted_disease: data.predicted_disease,
                medicines: data.medicines,
                diet: data.diet,
                workout: data.workout
            };
            
            document.getElementById('resultsSection').classList.remove('hidden');
            document.getElementById('resDisease').innerText = data.predicted_disease;
            document.getElementById('resMedicine').innerText = data.medicines;
            document.getElementById('resDiet').innerText = data.diet;
            document.getElementById('resWorkout').innerText = data.workout;
        } else {
            showToast("Error: " + JSON.stringify(data.detail), 'error');
        }
    } catch(err) {
        showToast("Server error.", 'error');
    }
}

async function saveRecord() {
    if(!latestPrediction) return;
    
    const token = localStorage.getItem('access_token');
    try {
        const res = await fetch(`${API_URL}/save_record`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(latestPrediction)
        });
        
        const data = await res.json();
        if(res.ok) {
            showToast("Record saved successfully!", 'success');
            loadHistory();
        } else {
            showToast("Error saving record.", 'error');
        }
    } catch(err) {
        showToast("Server error.", 'error');
    }
}

let userHistoryData = [];

async function loadHistory() {
    const tableBody = document.getElementById('historyBody');
    if(!tableBody) return;
    
    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_URL}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if(res.ok) {
        userHistoryData = await res.json();
        tableBody.innerHTML = '';
        userHistoryData.forEach((item, index) => {
            const date = new Date(item.created_at).toLocaleDateString();
            tableBody.innerHTML += `
                <tr onclick="openHistoryModal(${index})" style="cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='rgba(15, 118, 110, 0.03)'" onmouseout="this.style.background='transparent'">
                    <td>${date}</td>
                    <td style="color: var(--text-light);">${item.symptoms}</td>
                    <td><span class="table-tag">${item.predicted_disease}</span></td>
                    <td style="text-align: right;">
                        <button onclick="event.stopPropagation(); deleteHistory(${item.id})" class="close-btn" style="color: #ef4444; background: rgba(239, 68, 68, 0.05); width: 32px; height: 32px; display: inline-flex;">
                            <i data-lucide="trash-2" style="width: 16px; height: 16px;"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        if(window.lucide) lucide.createIcons();
    }
}

async function deleteHistory(recordId, fromModal = false) {
    if(!confirm("Are you sure you want to delete this prediction record?")) return;
    
    const token = localStorage.getItem('access_token');
    try {
        const res = await fetch(`${API_URL}/history/${recordId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if(res.ok) {
            showToast("Record deleted successfully", "success");
            loadHistory(); // Refresh the table
            if (fromModal) {
                closeHistoryModal();
            }
        } else {
            showToast("Failed to delete record", "error");
        }
    } catch(err) {
        showToast("Server error during deletion", "error");
    }
}

function openHistoryModal(index) {
    const item = userHistoryData[index];
    if (!item) return;
    
    document.getElementById('histDate').innerText = new Date(item.created_at).toLocaleString();
    document.getElementById('histSymptoms').innerText = item.symptoms;
    document.getElementById('histDisease').innerText = item.predicted_disease;
    document.getElementById('histMedicines').innerText = item.medicines;
    document.getElementById('histDiet').innerText = item.diet;
    document.getElementById('histWorkout').innerText = item.workout;
    
    const modalDeleteBtn = document.getElementById('modalDeleteBtn');
    if (modalDeleteBtn) {
        modalDeleteBtn.onclick = () => deleteHistory(item.id, true);
    }
    
    document.getElementById('historyModal').classList.remove('hidden');
}

function closeHistoryModal() {
    document.getElementById('historyModal').classList.add('hidden');
}

async function loadSymptomsList() {
    try {
        const res = await fetch(`${API_URL}/symptoms`);
        if(res.ok) {
            allAvailableSymptoms = await res.json();
        }
    } catch(err) {
        console.error('Failed to load symptoms', err);
    }
}

// Initialize Page
document.addEventListener('DOMContentLoaded', () => {
    // If we are on dashboard page
    if (window.location.pathname.includes('dashboard.html')) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }
        fetchUserData();
        loadSymptomsList();
        loadHistory();
    }
    
    // Initialize icons if Lucide is present
    if (window.lucide) {
        lucide.createIcons();
    }
});
