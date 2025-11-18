const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");
const mysql = require("mysql2");

const app = express();
app.use(cors());
app.use(bodyParser.json());

const db = mysql.createPool({
    host: "localhost",
    user: "root",
    password: "",
    database: "fraud_detection"
});

// Route: Get all transactions
app.get("/transactions", (req, res) => {
    db.query("SELECT * FROM transactions ORDER BY timestamp DESC", (err, rows) => {
        if (err) return res.status(500).json({ error: err });
        res.json(rows);
    });
});

// Route: Get all alerts
app.get("/fraud_alerts", (req, res) => {
    db.query("SELECT * FROM fraud_alerts ORDER BY timestamp DESC", (err, rows) => {
        if (err) return res.status(500).json({ error: err });
        res.json(rows);
    });
});

// Route: Create transaction and run Python model
app.post("/predict", (req, res) => {
    const inputData = req.body;

    // RUN PYTHON SCRIPT
    const python = spawn("python", ["./python/predict.py", JSON.stringify(inputData)]);

    let result = "";
    python.stdout.on("data", data => result += data.toString());

    python.on("close", () => {
        try {
            const prediction = JSON.parse(result);

            const {
                prediction: label,
                fraud_probability: prob
            } = prediction;

            const isFraud = prob > 0.6 ? 1 : 0;

            // Save transaction
            db.query(
                `INSERT INTO transactions (user_id, device_id, amount, transaction_type, location, timestamp, label, fraud_probability)
                 VALUES (?, ?, ?, ?, ?, NOW(), ?, ?)`,
                 [
                   inputData.user_id,
                   inputData.device_id,
                   inputData.amount,
                   inputData.transaction_type,
                   inputData.location,
                   isFraud ? 'fraud' : 'legit',
                   prob
                 ],
                 (err, resultTx) => {
                    if (err) return res.status(500).json({ error: err });

                    const transaction_id = resultTx.insertId;

                    // If fraud → save alert
                    if (isFraud) {
                        db.query(
                            `INSERT INTO fraud_alerts (transaction_id, predicted_label, confidence, timestamp)
                             VALUES (?, ?, ?, NOW())`,
                             [
                               transaction_id,
                               "fraud",
                               prob
                             ]
                        );
                    }

                    res.json({
                        success: true,
                        transaction_id,
                        fraud_probability: prob,
                        predicted_label: isFraud ? "fraud" : "legit"
                    });
                }
            );

        } catch (e) {
            res.status(500).json({ error: "Python output error", raw: result });
        }
    });
});

app.listen(5000, () => console.log("Backend running on port 5000"));
