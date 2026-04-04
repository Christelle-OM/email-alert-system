// API Configuration
const API_BASE_URL = '/api';

// Utility Functions
function showAlert(elementId, message, type = 'success') {
    const alertElement = document.getElementById(elementId);
    alertElement.textContent = message;
    alertElement.className = `alert ${type}`;
}

function clearAlert(elementId) {
    const alertElement = document.getElementById(elementId);
    alertElement.className = 'alert hidden';
}

async function checkApiHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        document.getElementById('api-status').textContent = 'Online ✓';
        document.getElementById('api-status').style.color = '#28a745';
    } catch (error) {
        document.getElementById('api-status').textContent = 'Offline ✗';
        document.getElementById('api-status').style.color = '#dc3545';
    }
}

// Tab Navigation
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        const tabName = this.dataset.tab;
        
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        this.classList.add('active');
        
        // Load data for specific tabs
        if (tabName === 'subscribers') {
            loadSubscribers();
        } else if (tabName === 'history') {
            loadAlertHistory();
        } else if (tabName === 'stats') {
            loadStatistics();
        }
    });
});

// ============= Send Single Alert =============
document.getElementById('send-alert-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('recipient').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    const scheduledTime = document.getElementById('schedule-time').value;
    
    try {
        const payload = {
            recipient_email: email,
            subject: subject,
            message: message
        };
        
        if (scheduledTime) {
            payload.scheduled_for = new Date(scheduledTime).toISOString();
        }
        
        const response = await fetch(`/api/alerts/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showAlert('alert-status', 'Alert sent successfully! ✓', 'success');
            document.getElementById('send-alert-form').reset();
            setTimeout(() => clearAlert('alert-status'), 5000);
        } else {
            const error = await response.json();
            showAlert('alert-status', `Error: ${error.detail || 'Failed to send alert'}`, 'error');
        }
    } catch (error) {
        showAlert('alert-status', `Error: ${error.message}`, 'error');
    }
});

// ============= Send Bulk Alerts =============
document.getElementById('bulk-alert-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const emailsText = document.getElementById('bulk-recipients').value;
    const subject = document.getElementById('bulk-subject').value;
    const message = document.getElementById('bulk-message').value;
    const scheduledTime = document.getElementById('bulk-schedule-time').value;
    
    const recipient_emails = emailsText
        .split('\n')
        .map(email => email.trim())
        .filter(email => email.length > 0);
    
    if (recipient_emails.length === 0) {
        showAlert('bulk-status', 'Please enter at least one email address', 'error');
        return;
    }
    
    try {
        const payload = {
            recipient_emails: recipient_emails,
            subject: subject,
            message: message
        };
        
        if (scheduledTime) {
            payload.scheduled_for = new Date(scheduledTime).toISOString();
        }
        
        const response = await fetch(`${API_BASE_URL}/alerts/send-bulk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const result = await response.json();
            const message = `Bulk alerts processed! Sent: ${result.sent}, Failed: ${result.failed}, Scheduled: ${result.scheduled}`;
            showAlert('bulk-status', message, 'success');
            document.getElementById('bulk-alert-form').reset();
            setTimeout(() => clearAlert('bulk-status'), 5000);
        } else {
            const error = await response.json();
            showAlert('bulk-status', `Error: ${error.detail || 'Failed to send alerts'}`, 'error');
        }
    } catch (error) {
        showAlert('bulk-status', `Error: ${error.message}`, 'error');
    }
});

// ============= Subscribers Management =============
document.getElementById('subscriber-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('subscriber-email').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/subscribers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        });
        
        if (response.ok) {
            showAlert('subscriber-status', 'Subscriber added successfully! ✓', 'success');
            document.getElementById('subscriber-form').reset();
            setTimeout(() => {
                clearAlert('subscriber-status');
                loadSubscribers();
            }, 1500);
        } else {
            const error = await response.json();
            showAlert('subscriber-status', `Error: ${error.detail || 'Failed to add subscriber'}`, 'error');
        }
    } catch (error) {
        showAlert('subscriber-status', `Error: ${error.message}`, 'error');
    }
});

async function loadSubscribers() {
    try {
        const response = await fetch(`${API_BASE_URL}/subscribers?limit=100`);
        const subscribers = await response.json();
        
        const container = document.getElementById('subscribers-list');
        
        if (subscribers.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 20px;">No subscribers yet</p>';
            return;
        }
        
        container.innerHTML = subscribers.map(sub => `
            <div class="list-item">
                <div class="item-content">
                    <div class="item-title">${sub.email}</div>
                    <div class="item-meta">
                        Added: ${new Date(sub.created_at).toLocaleString()}
                        <span class="item-status ${sub.is_active ? 'status-active' : 'status-inactive'}">
                            ${sub.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="deleteSubscriber(${sub.id})">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        document.getElementById('subscribers-list').innerHTML = `<p style="color: red;">Error loading subscribers: ${error.message}</p>`;
    }
}

async function deleteSubscriber(id) {
    if (!confirm('Are you sure you want to delete this subscriber?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/subscribers/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadSubscribers();
        } else {
            alert('Failed to delete subscriber');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ============= Alert History =============
async function loadAlertHistory() {
    try {
        const status = document.getElementById('status-filter').value;
        const url = status 
            ? `${API_BASE_URL}/alerts?status=${status}&limit=100`
            : `${API_BASE_URL}/alerts?limit=100`;
        
        const response = await fetch(url);
        const alerts = await response.json();
        
        const container = document.getElementById('alerts-list');
        
        if (alerts.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 20px;">No alerts found</p>';
            return;
        }
        
        container.innerHTML = alerts.reverse().map(alert => `
            <div class="list-item">
                <div class="item-content">
                    <div class="item-title">${alert.subject}</div>
                    <div class="item-meta">
                        To: ${alert.recipient_email} | 
                        Created: ${new Date(alert.created_at).toLocaleString()}
                        ${alert.sent_at ? `| Sent: ${new Date(alert.sent_at).toLocaleString()}` : ''}
                    </div>
                    ${alert.error_message ? `<div style="color: #dc3545; margin-top: 5px;">Error: ${alert.error_message}</div>` : ''}
                </div>
                <span class="item-status ${`status-${alert.status}`}">
                    ${alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                </span>
            </div>
        `).join('');
    } catch (error) {
        document.getElementById('alerts-list').innerHTML = `<p style="color: red;">Error loading alerts: ${error.message}</p>`;
    }
}

// ============= Statistics =============
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        
        const container = document.getElementById('stats-container');
        
        container.innerHTML = `
            <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="stat-value">${stats.alerts.total}</div>
                <div class="stat-label">Total Alerts</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                <div class="stat-value">${stats.alerts.sent}</div>
                <div class="stat-label">Alerts Sent</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);">
                <div class="stat-value">${stats.alerts.pending}</div>
                <div class="stat-label">Pending Alerts</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
                <div class="stat-value">${stats.alerts.failed}</div>
                <div class="stat-label">Failed Alerts</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);">
                <div class="stat-value">${stats.subscribers.total}</div>
                <div class="stat-label">Total Subscribers</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);">
                <div class="stat-value">${stats.subscribers.active}</div>
                <div class="stat-label">Active Subscribers</div>
            </div>
        `;
    } catch (error) {
        document.getElementById('stats-container').innerHTML = `<p style="color: red;">Error loading statistics: ${error.message}</p>`;
    }
}

// Filter for alert history
document.getElementById('status-filter')?.addEventListener('change', loadAlertHistory);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
    setInterval(checkApiHealth, 30000); // Check API health every 30 seconds
});
