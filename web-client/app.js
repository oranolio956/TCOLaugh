// Oranolio C2 Framework - Admin Dashboard JavaScript

class OranolioC2 {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.serverUrl = '';
        this.username = '';
        this.password = '';
        this.currentTab = 'sessions';
        this.agents = new Map();
        this.listeners = new Map();
        this.tasks = new Map();
        this.downloads = new Map();
        this.screenshots = new Map();
        this.credentials = new Map();
        this.targets = new Map();
        this.tunnels = new Map();
        this.chatMessages = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.loadSavedConnection();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });

        // Connection modal
        document.getElementById('connectBtn').addEventListener('click', () => {
            this.showConnectionModal();
        });

        document.getElementById('connectToServer').addEventListener('click', () => {
            this.connectToServer();
        });

        // Refresh buttons
        document.getElementById('refreshSessions').addEventListener('click', () => {
            this.refreshSessions();
        });

        document.getElementById('refreshDownloads').addEventListener('click', () => {
            this.refreshDownloads();
        });

        document.getElementById('refreshScreenshots').addEventListener('click', () => {
            this.refreshScreenshots();
        });

        // Action buttons
        document.getElementById('createListener').addEventListener('click', () => {
            this.showCreateListenerModal();
        });

        document.getElementById('executeCommand').addEventListener('click', () => {
            this.showExecuteCommandModal();
        });

        document.getElementById('addCredential').addEventListener('click', () => {
            this.showAddCredentialModal();
        });

        document.getElementById('addTarget').addEventListener('click', () => {
            this.showAddTargetModal();
        });

        document.getElementById('createTunnel').addEventListener('click', () => {
            this.showCreateTunnelModal();
        });

        // Chat
        document.getElementById('sendMessage').addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showSettingsModal();
        });
    }

    setupWebSocket() {
        // WebSocket will be established after authentication
    }

    connectWebSocket() {
        if (this.ws) {
            this.ws.close();
        }

        const wsUrl = this.serverUrl.replace('https://', 'wss://').replace('http://', 'ws://') + '/endpoint/channel';
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus('connected');
            this.authenticateWebSocket();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus('disconnected');
            this.isConnected = false;
            
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 5000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('disconnected');
        };
    }

    authenticateWebSocket() {
        // Send authentication message
        const authMessage = {
            type: 'auth',
            username: this.username,
            password: this.password
        };
        
        this.ws.send(JSON.stringify(authMessage));
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'auth_success':
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                this.syncData();
                break;
            case 'auth_failed':
                this.showNotification('Authentication failed', 'error');
                this.isConnected = false;
                break;
            case 'agent_new':
                this.addAgent(data.agent);
                break;
            case 'agent_update':
                this.updateAgent(data.agent);
                break;
            case 'agent_remove':
                this.removeAgent(data.agentId);
                break;
            case 'listener_new':
                this.addListener(data.listener);
                break;
            case 'listener_update':
                this.updateListener(data.listener);
                break;
            case 'listener_remove':
                this.removeListener(data.listenerName);
                break;
            case 'task_update':
                this.updateTask(data.task);
                break;
            case 'download_update':
                this.updateDownload(data.download);
                break;
            case 'screenshot_new':
                this.addScreenshot(data.screenshot);
                break;
            case 'credential_new':
                this.addCredential(data.credential);
                break;
            case 'target_new':
                this.addTarget(data.target);
                break;
            case 'tunnel_new':
                this.addTunnel(data.tunnel);
                break;
            case 'chat_message':
                this.addChatMessage(data.message);
                break;
            case 'sync_data':
                this.handleSyncData(data);
                break;
        }
    }

    connectToServer() {
        this.serverUrl = document.getElementById('serverUrl').value;
        this.username = document.getElementById('username').value;
        this.password = document.getElementById('password').value;

        if (!this.serverUrl || !this.username || !this.password) {
            this.showNotification('Please fill in all fields', 'error');
            return;
        }

        this.saveConnection();
        this.connectWebSocket();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('connectionModal'));
        modal.hide();
    }

    saveConnection() {
        localStorage.setItem('oranolio_connection', JSON.stringify({
            serverUrl: this.serverUrl,
            username: this.username,
            password: this.password
        }));
    }

    loadSavedConnection() {
        const saved = localStorage.getItem('oranolio_connection');
        if (saved) {
            const connection = JSON.parse(saved);
            this.serverUrl = connection.serverUrl;
            this.username = connection.username;
            this.password = connection.password;
            
            // Auto-connect if credentials are saved
            this.connectWebSocket();
        }
    }

    showConnectionModal() {
        const modal = new bootstrap.Modal(document.getElementById('connectionModal'));
        modal.show();
    }

    switchTab(tabName) {
        // Update active tab in sidebar
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show corresponding content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load data for the tab
        switch (tabName) {
            case 'sessions':
                this.refreshSessions();
                break;
            case 'listeners':
                this.refreshListeners();
                break;
            case 'tasks':
                this.refreshTasks();
                break;
            case 'downloads':
                this.refreshDownloads();
                break;
            case 'screenshots':
                this.refreshScreenshots();
                break;
            case 'credentials':
                this.refreshCredentials();
                break;
            case 'targets':
                this.refreshTargets();
                break;
            case 'tunnels':
                this.refreshTunnels();
                break;
            case 'chat':
                this.refreshChat();
                break;
        }
    }

    updateConnectionStatus(status) {
        let statusElement = document.querySelector('.connection-status');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.className = 'connection-status';
            document.body.appendChild(statusElement);
        }

        statusElement.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
                break;
            case 'disconnected':
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
                break;
            case 'connecting':
                statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
                break;
        }
    }

    syncData() {
        if (!this.isConnected) return;

        // Request sync data from server
        this.sendWebSocketMessage({
            type: 'sync_request',
            data: ['agents', 'listeners', 'tasks', 'downloads', 'screenshots', 'credentials', 'targets', 'tunnels', 'chat']
        });
    }

    sendWebSocketMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    // Agent management
    addAgent(agent) {
        this.agents.set(agent.id, agent);
        this.updateSessionsTable();
    }

    updateAgent(agent) {
        this.agents.set(agent.id, agent);
        this.updateSessionsTable();
    }

    removeAgent(agentId) {
        this.agents.delete(agentId);
        this.updateSessionsTable();
    }

    updateSessionsTable() {
        const tbody = document.getElementById('sessionsTableBody');
        tbody.innerHTML = '';

        this.agents.forEach(agent => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${agent.id}</td>
                <td>${agent.type || 'Unknown'}</td>
                <td>${agent.externalIP || 'N/A'}</td>
                <td>${agent.internalIP || 'N/A'}</td>
                <td>${agent.computer || 'N/A'}</td>
                <td>${agent.user || 'N/A'}</td>
                <td>${agent.os || 'Unknown'}</td>
                <td>${agent.process || 'N/A'}</td>
                <td>${new Date(agent.lastSeen).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.openAgentConsole('${agent.id}')">
                        <i class="fas fa-terminal"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="oranolioC2.executeAgentCommand('${agent.id}')">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.removeAgent('${agent.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    openAgentConsole(agentId) {
        // Open console for specific agent
        this.showNotification(`Opening console for agent ${agentId}`, 'info');
    }

    executeAgentCommand(agentId) {
        // Show command execution modal for specific agent
        this.showNotification(`Executing command on agent ${agentId}`, 'info');
    }

    removeAgent(agentId) {
        if (confirm(`Are you sure you want to remove agent ${agentId}?`)) {
            this.sendWebSocketMessage({
                type: 'agent_remove',
                agentId: agentId
            });
        }
    }

    // Listener management
    addListener(listener) {
        this.listeners.set(listener.name, listener);
        this.updateListenersTable();
    }

    updateListener(listener) {
        this.listeners.set(listener.name, listener);
        this.updateListenersTable();
    }

    removeListener(listenerName) {
        this.listeners.delete(listenerName);
        this.updateListenersTable();
    }

    updateListenersTable() {
        const tbody = document.getElementById('listenersTableBody');
        tbody.innerHTML = '';

        this.listeners.forEach(listener => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${listener.name}</td>
                <td>${listener.type || 'Unknown'}</td>
                <td>${listener.protocol || 'N/A'}</td>
                <td>${listener.host || 'N/A'}</td>
                <td>${listener.port || 'N/A'}</td>
                <td><span class="agent-status ${listener.status || 'inactive'}">${listener.status || 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.editListener('${listener.name}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.stopListener('${listener.name}')">
                        <i class="fas fa-stop"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Task management
    updateTask(task) {
        this.tasks.set(task.id, task);
        this.updateTasksDisplay();
    }

    updateTasksDisplay() {
        const container = document.getElementById('activeTasks');
        container.innerHTML = '';

        this.tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item mb-2 p-2 bg-dark rounded';
            taskElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${task.command || 'Unknown Command'}</span>
                    <span class="badge bg-${task.status === 'completed' ? 'success' : 'warning'}">${task.status || 'Running'}</span>
                </div>
            `;
            container.appendChild(taskElement);
        });
    }

    // Download management
    updateDownload(download) {
        this.downloads.set(download.id, download);
        this.updateDownloadsTable();
    }

    updateDownloadsTable() {
        const tbody = document.getElementById('downloadsTableBody');
        tbody.innerHTML = '';

        this.downloads.forEach(download => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${download.id}</td>
                <td>${download.filename || 'Unknown'}</td>
                <td>${this.formatFileSize(download.size || 0)}</td>
                <td>${download.agentId || 'N/A'}</td>
                <td><span class="agent-status ${download.status || 'pending'}">${download.status || 'Pending'}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.downloadFile('${download.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.deleteDownload('${download.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Screenshot management
    addScreenshot(screenshot) {
        this.screenshots.set(screenshot.id, screenshot);
        this.updateScreenshotsGrid();
    }

    updateScreenshotsGrid() {
        const container = document.getElementById('screenshotsGrid');
        container.innerHTML = '';

        this.screenshots.forEach(screenshot => {
            const screenshotElement = document.createElement('div');
            screenshotElement.className = 'col-md-4 col-lg-3';
            screenshotElement.innerHTML = `
                <div class="screenshot-item">
                    <img src="data:image/png;base64,${screenshot.content}" alt="Screenshot">
                    <div class="screenshot-overlay">
                        <div class="screenshot-info">
                            <h6>${screenshot.agentId || 'Unknown Agent'}</h6>
                            <small>${new Date(screenshot.timestamp).toLocaleString()}</small>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(screenshotElement);
        });
    }

    // Credential management
    addCredential(credential) {
        this.credentials.set(credential.id, credential);
        this.updateCredentialsTable();
    }

    updateCredentialsTable() {
        const tbody = document.getElementById('credentialsTableBody');
        tbody.innerHTML = '';

        this.credentials.forEach(credential => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${credential.username || 'N/A'}</td>
                <td>${'*'.repeat(credential.password?.length || 0)}</td>
                <td>${credential.domain || 'N/A'}</td>
                <td>${credential.type || 'Unknown'}</td>
                <td>${credential.host || 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.editCredential('${credential.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.deleteCredential('${credential.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Target management
    addTarget(target) {
        this.targets.set(target.id, target);
        this.updateTargetsTable();
    }

    updateTargetsTable() {
        const tbody = document.getElementById('targetsTableBody');
        tbody.innerHTML = '';

        this.targets.forEach(target => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${target.computer || 'N/A'}</td>
                <td>${target.domain || 'N/A'}</td>
                <td>${target.address || 'N/A'}</td>
                <td>${target.os || 'Unknown'}</td>
                <td><span class="agent-status ${target.alive ? 'active' : 'inactive'}">${target.alive ? 'Alive' : 'Dead'}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.editTarget('${target.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.deleteTarget('${target.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Tunnel management
    addTunnel(tunnel) {
        this.tunnels.set(tunnel.id, tunnel);
        this.updateTunnelsTable();
    }

    updateTunnelsTable() {
        const tbody = document.getElementById('tunnelsTableBody');
        tbody.innerHTML = '';

        this.tunnels.forEach(tunnel => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${tunnel.id}</td>
                <td>${tunnel.type || 'Unknown'}</td>
                <td>${tunnel.localHost || 'N/A'}</td>
                <td>${tunnel.localPort || 'N/A'}</td>
                <td>${tunnel.remoteHost || 'N/A'}</td>
                <td>${tunnel.remotePort || 'N/A'}</td>
                <td><span class="agent-status ${tunnel.status || 'inactive'}">${tunnel.status || 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="oranolioC2.editTunnel('${tunnel.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="oranolioC2.stopTunnel('${tunnel.id}')">
                        <i class="fas fa-stop"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Chat management
    addChatMessage(message) {
        this.chatMessages.push(message);
        this.updateChatDisplay();
    }

    updateChatDisplay() {
        const container = document.getElementById('chatMessages');
        container.innerHTML = '';

        this.chatMessages.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.className = `chat-message ${message.type || 'user'}`;
            messageElement.innerHTML = `
                <div class="message-header">
                    <strong>${message.username || 'System'}</strong>
                    <span class="text-muted">${new Date(message.timestamp).toLocaleString()}</span>
                </div>
                <div class="message-content">${message.content}</div>
            `;
            container.appendChild(messageElement);
        });

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        this.sendWebSocketMessage({
            type: 'chat_send',
            message: message
        });

        input.value = '';
    }

    // Utility functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    // Refresh functions
    refreshSessions() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['agents'] });
    }

    refreshListeners() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['listeners'] });
    }

    refreshTasks() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['tasks'] });
    }

    refreshDownloads() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['downloads'] });
    }

    refreshScreenshots() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['screenshots'] });
    }

    refreshCredentials() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['credentials'] });
    }

    refreshTargets() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['targets'] });
    }

    refreshTunnels() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['tunnels'] });
    }

    refreshChat() {
        this.sendWebSocketMessage({ type: 'sync_request', data: ['chat'] });
    }

    handleSyncData(data) {
        if (data.agents) {
            data.agents.forEach(agent => this.addAgent(agent));
        }
        if (data.listeners) {
            data.listeners.forEach(listener => this.addListener(listener));
        }
        if (data.tasks) {
            data.tasks.forEach(task => this.updateTask(task));
        }
        if (data.downloads) {
            data.downloads.forEach(download => this.updateDownload(download));
        }
        if (data.screenshots) {
            data.screenshots.forEach(screenshot => this.addScreenshot(screenshot));
        }
        if (data.credentials) {
            data.credentials.forEach(credential => this.addCredential(credential));
        }
        if (data.targets) {
            data.targets.forEach(target => this.addTarget(target));
        }
        if (data.tunnels) {
            data.tunnels.forEach(tunnel => this.addTunnel(tunnel));
        }
        if (data.chat) {
            data.chat.forEach(message => this.addChatMessage(message));
        }
    }

    // Modal functions (placeholder implementations)
    showCreateListenerModal() {
        this.showNotification('Create Listener functionality coming soon', 'info');
    }

    showExecuteCommandModal() {
        this.showNotification('Execute Command functionality coming soon', 'info');
    }

    showAddCredentialModal() {
        this.showNotification('Add Credential functionality coming soon', 'info');
    }

    showAddTargetModal() {
        this.showNotification('Add Target functionality coming soon', 'info');
    }

    showCreateTunnelModal() {
        this.showNotification('Create Tunnel functionality coming soon', 'info');
    }

    showSettingsModal() {
        this.showNotification('Settings functionality coming soon', 'info');
    }
}

// Initialize the application
const oranolioC2 = new OranolioC2();