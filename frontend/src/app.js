import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, query, orderBy, limit, onSnapshot } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// REPLACE WITH YOUR FIREBASE CONFIGURATION
const firebaseConfig = {
    apiKey: "AIzaSyDjYJPN_IcoziR3YfqDdmdRoajKZTD6FLU",
    authDomain: "lab-iot-493715.firebaseapp.com",
    projectId: "lab-iot-493715",
    storageBucket: "lab-iot-493715.firebasestorage.app",
    messagingSenderId: "998677631520",
    appId: "1:998677631520:web:e8f55be7c63e9fd27fe245"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Elements
const currentTempEl = document.getElementById('current-temp');
const avgTempEl = document.getElementById('avg-temp');
const currentHumEl = document.getElementById('current-humidity');
const avgHumEl = document.getElementById('avg-humidity');
const lastUpdateEl = document.getElementById('last-update');
const deviceStateEl = document.getElementById('device-state');

// Toggle Elements
const deviceToggleBtn = document.getElementById('device-toggle-btn');
const toggleDot = document.getElementById('toggle-dot');
const toggleTextOff = document.getElementById('toggle-state-text');
const toggleTextOn = document.getElementById('toggle-state-text-on');

let isDeviceOn = false;

// Chart Setup
const ctx = document.getElementById('sensorChart').getContext('2d');
const sensorChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Temperature (°C)',
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                data: [],
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6
            },
            {
                label: 'Humidity (%)',
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                data: [],
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: 'rgba(0,0,0,0.05)' }
            },
            x: {
                grid: { display: false }
            }
        }
    }
});

// Real-time listener
const sensorQuery = query(
    collection(db, "sensor_data"),
    orderBy("timestamp", "desc"),
    limit(50)
);

onSnapshot(sensorQuery, (snapshot) => {
    const data = [];
    snapshot.forEach((doc) => {
        data.push(doc.data());
    });

    if (data.length > 0) {
        const latest = data[0];
        updateRealtimeUI(latest);
        updateAverages(data);
        updateChart(data.reverse());
        
        // Sync toggle if not currently transitioning
        if (!deviceToggleBtn.disabled) {
            syncToggleWithState(latest.state);
        }
    }
});

function syncToggleWithState(state) {
    const newState = state === 'ON';
    if (newState !== isDeviceOn) {
        isDeviceOn = newState;
        updateToggleUI(isDeviceOn);
    }
}

function updateToggleUI(isOn) {
    if (isOn) {
        deviceToggleBtn.classList.remove('bg-slate-200');
        deviceToggleBtn.classList.add('bg-blue-600');
        toggleDot.classList.add('translate-x-8');
        toggleTextOff.classList.add('hidden');
        toggleTextOn.classList.remove('hidden');
    } else {
        deviceToggleBtn.classList.add('bg-slate-200');
        deviceToggleBtn.classList.remove('bg-blue-600');
        toggleDot.classList.remove('translate-x-8');
        toggleTextOff.classList.remove('hidden');
        toggleTextOn.classList.add('hidden');
    }
}

function updateRealtimeUI(latest) {
    currentTempEl.textContent = latest.temperature.toFixed(1);
    currentHumEl.textContent = latest.humidity.toFixed(1);
    deviceStateEl.textContent = `Status: ${latest.state}`;
    
    // Update color based on state
    if (latest.state === 'ON') {
        deviceStateEl.classList.add('bg-blue-100', 'text-blue-700');
        deviceStateEl.classList.remove('bg-slate-100', 'text-slate-600');
    } else {
        deviceStateEl.classList.remove('bg-blue-100', 'text-blue-700');
        deviceStateEl.classList.add('bg-slate-100', 'text-slate-600');
    }
    
    const date = latest.timestamp.toDate();
    lastUpdateEl.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function updateAverages(data) {
    const sumTemp = data.reduce((acc, curr) => acc + curr.temperature, 0);
    const sumHum = data.reduce((acc, curr) => acc + curr.humidity, 0);
    
    avgTempEl.textContent = `${(sumTemp / data.length).toFixed(1)} °C`;
    avgHumEl.textContent = `${(sumHum / data.length).toFixed(1)} %`;
}

function updateChart(historicalData) {
    const labels = historicalData.map(d => d.timestamp.toDate().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const temps = historicalData.map(d => d.temperature);
    const hums = historicalData.map(d => d.humidity);

    sensorChart.data.labels = labels;
    sensorChart.data.datasets[0].data = temps;
    sensorChart.data.datasets[1].data = hums;
    sensorChart.update('none'); // Update without animation for smoothness
}

// Download CSV Logic
const downloadBtn = document.getElementById('download-csv-btn');
downloadBtn.addEventListener('click', async () => {
    try {
        downloadBtn.innerHTML = `
            <svg class="animate-spin w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>Generating...</span>
        `;
        downloadBtn.disabled = true;

        const response = await fetch('/api/v1/sensors/export');
        if (!response.ok) throw new Error('Failed to generate export');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'sensor_data.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error("Export error:", error);
        alert("Failed to export CSV. Please try again.");
    } finally {
        downloadBtn.innerHTML = `
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            <span>Export CSV</span>
        `;
        downloadBtn.disabled = false;
    }
});

// Device Control Logic
async function toggleDevice() {
    const targetState = !isDeviceOn ? 'ON' : 'OFF';
    const originalIsOn = isDeviceOn;
    
    try {
        deviceToggleBtn.disabled = true;
        // Optimistic update
        updateToggleUI(!originalIsOn);
        
        const response = await fetch('/api/v1/device/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: targetState }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send command');
        }
        
        isDeviceOn = !originalIsOn;
        console.log(`Command ${targetState} sent successfully`);
    } catch (error) {
        console.error("Command error:", error);
        alert(`Error: ${error.message}`);
        // Revert on error
        updateToggleUI(originalIsOn);
    } finally {
        deviceToggleBtn.disabled = false;
    }
}

deviceToggleBtn.addEventListener('click', toggleDevice);
