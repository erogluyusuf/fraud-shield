from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
from datetime import datetime

app = FastAPI(title="Fraud Shield API")

class Transaction(BaseModel):
    user_id: str
    amount: float
    location: str
    timestamp: str | None = None

def get_rabbitmq_channel():
    parameters = pika.ConnectionParameters(host='rabbitmq', port=5672)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='transactions', durable=True)
    return connection, channel

@app.post("/transactions")
def add_transaction(transaction: Transaction):
    if not transaction.timestamp:
        transaction.timestamp = datetime.utcnow().isoformat()
    
    try:
        connection, channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange='',
            routing_key='transactions',
            body=json.dumps(transaction.dict()),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return {"message": "Transaction added to queue", "data": transaction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/status")
def get_user_status(user_id: str):
    return {"user_id": user_id, "risk_status": "unknown"}

@app.get("/frauds/recent")
def get_recent_frauds():
    return []
