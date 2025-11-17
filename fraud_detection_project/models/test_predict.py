from predict import predict_transaction

sample = {
    "amount": 500,
    "timestamp": "2024-01-01 10:30:00",
    "location": "Delhi",
    "merchant": "Amazon",
    "category": "online",
    "transaction_type": "card",
    "device_id": "device123",
    "user_id": "user45"
}

print(predict_transaction(sample))
