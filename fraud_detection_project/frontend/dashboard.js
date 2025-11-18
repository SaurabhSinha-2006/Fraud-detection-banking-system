const API = "http://localhost:5000";

async function loadDashboard() {
    try {
        const txns = await fetch(`${API}/transactions`).then(r => r.json());
        const alerts = await fetch(`${API}/fraud_alerts`).then(r => r.json());

        document.getElementById("total-transactions").innerText = txns.length;
        document.getElementById("total-frauds").innerText = alerts.length;
        document.getElementById("fraud-rate").innerText =
            ((alerts.length / txns.length) * 100).toFixed(2) + "%";

        /// ==== Fill Transaction Table ====
        let txnRows = "";
        txns.forEach(t => {
            txnRows += `
                <tr>
                    <td>${t.transaction_id}</td>
                    <td>${t.amount}</td>
                    <td>${t.location}</td>
                    <td>${t.merchant}</td>
                    <td>${t.category}</td>
                    <td>${t.transaction_type}</td>
                    <td>${(t.fraud_probability * 100).toFixed(1)}%</td>
                    <td>${t.label}</td>
                </tr>
            `;
        });
        document.getElementById("transaction-table").innerHTML = txnRows;

        /// ==== Fill Alert Table ====
        let alertRows = "";
        alerts.forEach(a => {
            alertRows += `
                <tr>
                    <td>${a.alert_id}</td>
                    <td>${a.transaction_id}</td>
                    <td>${a.predicted_label}</td>
                    <td>${(a.confidence * 100).toFixed(1)}%</td>
                    <td>${a.timestamp}</td>
                </tr>
            `;
        });
        document.getElementById("alert-table").innerHTML = alertRows;

    } catch (err) {
        console.error("Error:", err);
    }
}

// auto refresh every 5 sec
setInterval(loadDashboard, 5000);
loadDashboard();
