document.getElementById("txnForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const body = {
        amount: Number(amount.value),
        location: location.value,
        merchant: merchant.value,
        category: category.value,
        transaction_type: transaction_type.value,
        user_id: Number(user_id.value),
        device_id: Number(device_id.value)
    };

    const res = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body)
    });

    const data = await res.json();
    document.getElementById("response").innerText =
        "Prediction: " + data.predicted_label + 
        " | Probability: " + data.fraud_probability;
});
