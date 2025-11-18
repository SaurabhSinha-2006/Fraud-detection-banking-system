const API_BASE = "http://localhost:5000";

async function loadDashboard() {
  try {
    const txns = await fetch(API_BASE + "/transactions").then(r => r.json());
    const alerts = await fetch(API_BASE + "/fraud_alerts").then(r => r.json());

    document.getElementById("total-transactions").innerText = txns.length;
    document.getElementById("total-frauds").innerText = alerts.length;
    document.getElementById("fraud-rate").innerText =
      txns.length ? ((alerts.length / txns.length) * 100).toFixed(2) + "%" : "0%";

    let txnHtml = "";
    txns.forEach(t => {
      const prob = t.fraud_probability ? (t.fraud_probability*100).toFixed(1) + "%" : "N/A";
      txnHtml += `<tr>
        <td>${t.transaction_id||""}</td>
        <td>${t.amount||""}</td>
        <td>${t.location||""}</td>
        <td>${t.merchant||""}</td>
        <td>${t.transaction_type||""}</td>
        <td>${prob}</td>
        <td>${t.label||""}</td>
      </tr>`;
    });
    document.getElementById("transaction-table").innerHTML = txnHtml;

    let alertHtml = "";
    alerts.forEach(a => {
      alertHtml += `<tr>
        <td>${a.alert_id}</td>
        <td>${a.transaction_id}</td>
        <td>${a.predicted_label}</td>
        <td>${(a.confidence*100).toFixed(1)}%</td>
        <td>${a.timestamp}</td>
      </tr>`;
    });
    document.getElementById("alert-table").innerHTML = alertHtml;

  } catch (e) {
    console.error("Dashboard load error:", e);
  }
}

loadDashboard();
setInterval(loadDashboard, 5000);
