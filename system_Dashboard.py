import csv
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import psutil
from datetime import datetime

app = FastAPI()

LOG_FILE = "system_metrics.csv"

# Create CSV header if not exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "CPU%", "MEMORY%", "DISK%"])


@app.get("/")
def dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>System Live Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background: #0f172a;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            h1 {
                color: #38bdf8;
                padding-top: 20px;
            }
            .chart-container {
                width: 80%;
                margin: 40px auto;
                background: #1e293b;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 0 25px rgba(0,0,0,0.5);
            }
        </style>
    </head>
    <body>
        <h1>⚙️ Real-Time System Health Dashboard</h1>
        <div class="chart-container">
            <canvas id="systemChart"></canvas>
        </div>

        <script>
            const ctx = document.getElementById('systemChart').getContext('2d');
            const systemChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'CPU %', borderColor: '#38bdf8', data: [] },
                        { label: 'RAM %', borderColor: '#4ade80', data: [] },
                        { label: 'Disk %', borderColor: '#facc15', data: [] }
                    ]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 100 },
                        x: { ticks: { color: '#94a3b8' } }
                    },
                    plugins: {
                        legend: { labels: { color: '#e2e8f0' } }
                    }
                }
            });

            async function fetchStats() {
                const res = await fetch('/stats');
                const data = await res.json();
                const timeLabel = data.time.split(" ")[1];
                
                systemChart.data.labels.push(timeLabel);
                systemChart.data.datasets[0].data.push(data.cpu);
                systemChart.data.datasets[1].data.push(data.memory);
                systemChart.data.datasets[2].data.push(data.disk);

                // keep only last 10 data points
                if (systemChart.data.labels.length > 10) {
                    systemChart.data.labels.shift();
                    systemChart.data.datasets.forEach(ds => ds.data.shift());
                }

                systemChart.update();
            }

            setInterval(fetchStats, 2000);
        </script>
    </body>
    </html>
    """)


@app.get("/stats")
def get_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, cpu, memory, disk])

    return JSONResponse({
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "time": timestamp
    })
