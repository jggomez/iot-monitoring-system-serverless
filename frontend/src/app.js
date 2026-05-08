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
    }
});

function updateRealtimeUI(latest) {
    currentTempEl.textContent = latest.temperature.toFixed(1);
    currentHumEl.textContent = latest.humidity.toFixed(1);
    deviceStateEl.textContent = `Status: ${latest.state}`;
    
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
