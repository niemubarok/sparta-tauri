// Exit Gate System - Client-side JavaScript

class ExitGateApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentGateStatus = 'CLOSED';
        this.recentActivity = [];
        this.stats = { totalExits: 0, totalRevenue: 0 };
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing Exit Gate Application...');
        
        // Initialize Socket.IO connection
        this.initSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup barcode input auto-focus
        this.setupBarcodeInput();
        
        // Load initial data
        this.loadSystemStatus();
        this.loadStats();
        this.loadGPIOStatus();
        
        // Set up periodic GPIO status updates
        setInterval(() => {
            this.loadGPIOStatus();
        }, 2000); // Update every 2 seconds
        
        console.log('✅ Exit Gate Application initialized');
    }

    initSocket() {
        try {
            this.socket = io({
                reconnection: true,
                reconnectionAttempts: 5,
                reconnectionDelay: 1000,
                timeout: 20000
            });

            this.socket.on('connect', () => {
                console.log('🔌 Connected to server');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addActivity('System connected', 'success');
            });

            this.socket.on('disconnect', () => {
                console.log('🔌 Disconnected from server');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addActivity('System disconnected', 'error');
            });

            this.socket.on('reconnect', () => {
                console.log('🔌 Reconnected to server');
                this.addActivity('System reconnected', 'success');
                this.loadSystemStatus();
                this.loadStats();
            });

            this.socket.on('gate:status', (data) => {
                console.log('🚪 Gate status update:', data);
                this.updateGateStatus(data.status);
            });

            this.socket.on('transaction:result', (data) => {
                console.log('💳 Transaction result:', data);
                this.handleTransactionResult(data);
            });

            this.socket.on('stats:update', (data) => {
                console.log('📊 Stats update:', data);
                this.updateStats(data);
            });

            this.socket.on('error', (error) => {
                console.error('❌ Socket error:', error);
                this.showError(error.message || 'Connection error');
            });

        } catch (error) {
            console.error('❌ Failed to initialize socket:', error);
            this.showError('Failed to connect to server');
        }
    }

    setupEventListeners() {
        // Barcode input enter key
        const barcodeInput = document.getElementById('barcodeInput');
        if (barcodeInput) {
            barcodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.processTransaction();
                }
            });

            // Auto-focus on barcode input
            barcodeInput.addEventListener('blur', () => {
                setTimeout(() => {
                    if (document.activeElement !== barcodeInput) {
                        barcodeInput.focus();
                    }
                }, 100);
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // F1 - Open Gate
            if (e.key === 'F1') {
                e.preventDefault();
                this.openGate();
            }
            // F2 - Close Gate
            else if (e.key === 'F2') {
                e.preventDefault();
                this.closeGate();
            }
            // F3 - Test Gate
            else if (e.key === 'F3') {
                e.preventDefault();
                this.testGate();
            }
            // Escape - Clear input
            else if (e.key === 'Escape') {
                this.clearInput();
            }
        });

        // Visibility change (auto-focus when tab becomes visible)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && barcodeInput) {
                barcodeInput.focus();
            }
        });
    }

    setupBarcodeInput() {
        const barcodeInput = document.getElementById('barcodeInput');
        if (barcodeInput) {
            // Auto-focus
            barcodeInput.focus();
            
            // Simulate barcode scanner behavior
            let barcodeBuffer = '';
            let lastKeyTime = Date.now();
            
            barcodeInput.addEventListener('input', (e) => {
                const currentTime = Date.now();
                const timeDiff = currentTime - lastKeyTime;
                
                // If input is coming very fast (< 50ms between characters),
                // it's likely from a barcode scanner
                if (timeDiff < 50 && e.target.value.length > barcodeBuffer.length) {
                    barcodeBuffer = e.target.value;
                } else {
                    barcodeBuffer = '';
                }
                
                lastKeyTime = currentTime;
                
                // Auto-process if it looks like a complete barcode
                if (barcodeBuffer.length >= 8 && timeDiff > 100) {
                    setTimeout(() => {
                        this.processTransaction();
                    }, 200);
                }
            });
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (connected) {
                statusElement.className = 'badge bg-success me-2';
                statusElement.innerHTML = '<i class="bi bi-wifi"></i> Online';
            } else {
                statusElement.className = 'badge bg-danger me-2';
                statusElement.innerHTML = '<i class="bi bi-wifi-off"></i> Offline';
            }
        }
    }

    updateGateStatus(status) {
        this.currentGateStatus = status;
        
        const gateIcon = document.getElementById('gateIcon');
        const gateStatusText = document.getElementById('gateStatusText');
        const gateIndicator = document.getElementById('gateStatusIndicator');
        
        if (gateIcon && gateStatusText && gateIndicator) {
            // Remove all status classes
            gateIndicator.className = 'gate-status-indicator mb-3';
            
            switch (status) {
                case 'OPEN':
                    gateIcon.className = 'bi bi-door-open gate-icon gate-open';
                    gateStatusText.textContent = 'OPEN';
                    gateIndicator.classList.add('gate-open');
                    break;
                case 'OPENING':
                    gateIcon.className = 'bi bi-arrow-right gate-icon gate-opening';
                    gateStatusText.textContent = 'OPENING';
                    gateIndicator.classList.add('gate-opening');
                    break;
                case 'CLOSING':
                    gateIcon.className = 'bi bi-arrow-left gate-icon gate-closing';
                    gateStatusText.textContent = 'CLOSING';
                    gateIndicator.classList.add('gate-closing');
                    break;
                case 'ERROR':
                    gateIcon.className = 'bi bi-exclamation-triangle gate-icon gate-error';
                    gateStatusText.textContent = 'ERROR';
                    gateIndicator.classList.add('gate-error');
                    break;
                default: // CLOSED
                    gateIcon.className = 'bi bi-door-closed gate-icon gate-closed';
                    gateStatusText.textContent = 'CLOSED';
                    gateIndicator.classList.add('gate-closed');
            }
        }
        
        this.addActivity(`Gate ${status.toLowerCase()}`, status === 'ERROR' ? 'error' : 'info');
    }

    async openGate() {
        try {
            this.addActivity('Opening gate...', 'info');
            
            if (this.socket && this.isConnected) {
                this.socket.emit('gate:open', { autoCloseTime: 10 });
            } else {
                // Fallback to API call
                const response = await fetch('/api/gate/open', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ autoCloseTime: 10 })
                });
                
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.message);
                }
            }
        } catch (error) {
            console.error('❌ Error opening gate:', error);
            this.showError('Failed to open gate: ' + error.message);
        }
    }

    async closeGate() {
        try {
            this.addActivity('Closing gate...', 'info');
            
            if (this.socket && this.isConnected) {
                this.socket.emit('gate:close');
            } else {
                // Fallback to API call
                const response = await fetch('/api/gate/close', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.message);
                }
            }
        } catch (error) {
            console.error('❌ Error closing gate:', error);
            this.showError('Failed to close gate: ' + error.message);
        }
    }

    async testGate() {
        try {
            this.addActivity('Testing gate...', 'info');
            
            if (this.socket && this.isConnected) {
                this.socket.emit('gate:test');
            } else {
                // Fallback to API call
                const response = await fetch('/api/gate/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: 3 })
                });
                
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.message);
                }
            }
        } catch (error) {
            console.error('❌ Error testing gate:', error);
            this.showError('Failed to test gate: ' + error.message);
        }
    }

    async processTransaction() {
        const barcodeInput = document.getElementById('barcodeInput');
        const code = barcodeInput?.value.trim();
        
        if (!code) {
            this.showError('Please enter barcode or license plate');
            return;
        }
        
        try {
            this.showProcessingStatus(true);
            this.hideError();
            this.hideTransactionResult();
            
            this.addActivity(`Processing: ${code}`, 'info');
            
            if (this.socket && this.isConnected) {
                // Use WebSocket for real-time processing
                this.socket.emit('transaction:process', {
                    barcode: code.length >= 8 ? code : null,
                    licensePlate: code.length < 8 ? code : null
                });
            } else {
                // Fallback to API call
                const response = await fetch('/api/transaction/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        barcode: code.length >= 8 ? code : null,
                        licensePlate: code.length < 8 ? code : null
                    })
                });
                
                const result = await response.json();
                this.handleTransactionResult(result);
            }
            
        } catch (error) {
            console.error('❌ Error processing transaction:', error);
            this.showError('Failed to process transaction: ' + error.message);
            this.showProcessingStatus(false);
        }
    }

    handleTransactionResult(result) {
        this.showProcessingStatus(false);
        
        if (result.success && result.transaction) {
            this.showTransactionResult(result.transaction, result.fee);
            this.addActivity(`Exit processed: ${result.transaction.no_pol}`, 'success');
            
            // Auto-clear input after success
            setTimeout(() => {
                this.clearInput();
            }, 3000);
            
        } else {
            this.showError(result.message || 'Transaction processing failed');
            this.addActivity(`Failed: ${result.message}`, 'error');
        }
    }

    showTransactionResult(transaction, fee) {
        const resultDiv = document.getElementById('transactionResult');
        const vehicleNumber = document.getElementById('vehicleNumber');
        const entryTime = document.getElementById('entryTime');
        const vehicleType = document.getElementById('vehicleType');
        const exitFee = document.getElementById('exitFee');
        
        if (resultDiv && vehicleNumber && entryTime && vehicleType && exitFee) {
            vehicleNumber.textContent = transaction.no_pol || 'N/A';
            entryTime.textContent = transaction.waktu_masuk ? 
                new Date(transaction.waktu_masuk).toLocaleString() : 'N/A';
            vehicleType.textContent = transaction.id_kendaraan || 'N/A';
            exitFee.textContent = this.formatCurrency(fee || 0);
            
            resultDiv.classList.remove('d-none');
        }
    }

    hideTransactionResult() {
        const resultDiv = document.getElementById('transactionResult');
        if (resultDiv) {
            resultDiv.classList.add('d-none');
        }
    }

    showProcessingStatus(show) {
        const statusDiv = document.getElementById('processingStatus');
        if (statusDiv) {
            if (show) {
                statusDiv.classList.remove('d-none');
            } else {
                statusDiv.classList.add('d-none');
            }
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorDisplay');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorDiv && errorMessage) {
            errorMessage.textContent = message;
            errorDiv.classList.remove('d-none');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }
    }

    hideError() {
        const errorDiv = document.getElementById('errorDisplay');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    }

    clearInput() {
        const barcodeInput = document.getElementById('barcodeInput');
        if (barcodeInput) {
            barcodeInput.value = '';
            barcodeInput.focus();
        }
        
        this.hideError();
        this.hideTransactionResult();
        this.showProcessingStatus(false);
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateSystemStatus(data.status);
            }
        } catch (error) {
            console.error('❌ Error loading system status:', error);
        }
    }

    updateSystemStatus(status) {
        // Update GPIO status
        const gpioStatus = document.getElementById('gpioStatus');
        if (gpioStatus && status.gpio) {
            const icon = gpioStatus.querySelector('i');
            if (icon) {
                icon.className = status.gpio.initialized ? 
                    'bi bi-circle-fill text-success' : 
                    'bi bi-circle-fill text-danger';
            }
        }
        
        // Update database status
        const databaseStatus = document.getElementById('databaseStatus');
        if (databaseStatus && status.database) {
            const icon = databaseStatus.querySelector('i');
            if (icon) {
                icon.className = status.database.connected ? 
                    'bi bi-circle-fill text-success' : 
                    'bi bi-circle-fill text-warning';
            }
        }
        
        // Update audio status
        const audioStatus = document.getElementById('audioStatus');
        if (audioStatus && status.audio) {
            const icon = audioStatus.querySelector('i');
            if (icon) {
                icon.className = status.audio.isEnabled ? 
                    'bi bi-circle-fill text-success' : 
                    'bi bi-circle-fill text-secondary';
            }
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/transaction/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.stats);
            }
        } catch (error) {
            console.error('❌ Error loading stats:', error);
        }
    }

    updateStats(stats) {
        this.stats = stats;
        
        const totalExits = document.getElementById('totalExits');
        const totalRevenue = document.getElementById('totalRevenue');
        
        if (totalExits) {
            totalExits.textContent = stats.totalExits || 0;
        }
        
        if (totalRevenue) {
            totalRevenue.textContent = this.formatCurrency(stats.totalRevenue || 0);
        }
    }

    async playSound(soundType) {
        try {
            const response = await fetch(`/api/audio/play/${soundType}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            if (result.success) {
                this.addActivity(`Played ${soundType} sound`, 'info');
            }
        } catch (error) {
            console.error('❌ Error playing sound:', error);
        }
    }

    async testGPIO(pinName, pinNumber) {
        try {
            this.addActivity(`Testing ${pinName} (GPIO ${pinNumber})...`, 'info');
            
            const response = await fetch('/api/gpio/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    pin: pinNumber, 
                    name: pinName,
                    duration: 2000 // 2 seconds
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.addActivity(`${pinName} test successful`, 'success');
            } else {
                this.addActivity(`${pinName} test failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error(`❌ Error testing ${pinName}:`, error);
            this.addActivity(`${pinName} test error: ${error.message}`, 'error');
        }
    }

    async testAllGPIO() {
        try {
            this.addActivity('Testing all GPIO pins...', 'info');
            
            const response = await fetch('/api/gpio/test-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            if (result.success) {
                this.addActivity('All GPIO tests completed', 'success');
                if (result.results) {
                    result.results.forEach(test => {
                        const status = test.success ? 'success' : 'error';
                        this.addActivity(`${test.name}: ${test.message}`, status);
                    });
                }
            } else {
                this.addActivity(`GPIO test failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('❌ Error testing all GPIO:', error);
            this.addActivity(`GPIO test error: ${error.message}`, 'error');
        }
    }

    updateGPIOStatus(gpioData) {
        if (!gpioData) return;

        // Update input pin status
        const pins = {
            'loop1': { gpio: 18, status: gpioData.inputs?.loop1 },
            'loop2': { gpio: 27, status: gpioData.inputs?.loop2 },
            'struk': { gpio: 4, status: gpioData.inputs?.struk },
            'emergency': { gpio: 17, status: gpioData.inputs?.emergency }
        };

        Object.keys(pins).forEach(pinName => {
            const pin = pins[pinName];
            const badge = document.getElementById(`${pinName}Badge`);
            
            if (badge) {
                // Update badge based on pin status
                if (pin.status === true) {
                    badge.className = 'badge bg-success';
                    badge.textContent = `${pinName.toUpperCase()} ✓`;
                } else if (pin.status === false) {
                    badge.className = 'badge bg-warning';
                    badge.textContent = `${pinName.toUpperCase()} ○`;
                } else {
                    badge.className = 'badge bg-secondary';
                    badge.textContent = `${pinName.toUpperCase()} ?`;
                }
            }
        });
    }

    async loadGPIOStatus() {
        try {
            const response = await fetch('/api/gpio/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateGPIOStatus(data.gpio);
            }
        } catch (error) {
            console.error('❌ Error loading GPIO status:', error);
        }
    }

    addActivity(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const activity = { message, type, timestamp };
        
        this.recentActivity.unshift(activity);
        
        // Keep only last 10 activities
        if (this.recentActivity.length > 10) {
            this.recentActivity = this.recentActivity.slice(0, 10);
        }
        
        this.updateActivityDisplay();
    }

    updateActivityDisplay() {
        const activityDiv = document.getElementById('recentActivity');
        if (!activityDiv) return;
        
        if (this.recentActivity.length === 0) {
            activityDiv.innerHTML = '<div class="text-muted text-center">No recent activity</div>';
            return;
        }
        
        const html = this.recentActivity.map(activity => {
            const iconClass = this.getActivityIcon(activity.type);
            const textClass = this.getActivityTextClass(activity.type);
            
            return `
                <div class="activity-item">
                    <div class="activity-message ${textClass}">
                        <i class="${iconClass}"></i>
                        ${activity.message}
                    </div>
                    <div class="activity-time">${activity.timestamp}</div>
                </div>
            `;
        }).join('');
        
        activityDiv.innerHTML = html;
    }

    getActivityIcon(type) {
        switch (type) {
            case 'success': return 'bi bi-check-circle text-success';
            case 'error': return 'bi bi-x-circle text-danger';
            case 'warning': return 'bi bi-exclamation-triangle text-warning';
            default: return 'bi bi-info-circle text-info';
        }
    }

    getActivityTextClass(type) {
        switch (type) {
            case 'success': return 'text-success';
            case 'error': return 'text-danger';
            case 'warning': return 'text-warning';
            default: return 'text-info';
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    }
}

// Global functions for button clicks
function openGate() {
    window.exitGateApp.openGate();
}

function closeGate() {
    window.exitGateApp.closeGate();
}

function testGate() {
    window.exitGateApp.testGate();
}

function processTransaction() {
    window.exitGateApp.processTransaction();
}

function clearInput() {
    window.exitGateApp.clearInput();
}

function playSound(soundType) {
    window.exitGateApp.playSound(soundType);
}

function testGPIO(pinName, pinNumber) {
    window.exitGateApp.testGPIO(pinName, pinNumber);
}

function testAllGPIO() {
    window.exitGateApp.testAllGPIO();
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.exitGateApp = new ExitGateApp();
});
