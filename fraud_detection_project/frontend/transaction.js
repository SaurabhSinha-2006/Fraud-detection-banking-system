const API_BASE = "http://localhost:5000";

async function loadDashboard() {
  const txns = await fetch(API_BASE + "/transactions").then(r => r.json());
  const alerts = await fetch(API_BASE + "/fraud_alerts").then(r => r.json());
  // ... render as in previous dashboard.js ...
}

loadDashboard();
setInterval(loadDashboard, 5000);
