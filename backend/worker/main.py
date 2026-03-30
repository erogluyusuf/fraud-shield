import pika
import redis
import json
from datetime import datetime

r = redis.Redis(host='redis', port=6379, decode_responses=True)

def process_transaction(ch, method, properties, body):
    try:
        data = json.loads(body)
        user_id = data.get('user_id')
        amount = float(data.get('amount', 0))
        loc = data.get('location')
        now = datetime.fromisoformat(data.get('timestamp')).timestamp()
        
        violations = 0
        
        r.lpush(f"user:{user_id}:times", now)
        r.expire(f"user:{user_id}:times", 60)
        if r.llen(f"user:{user_id}:times") > 5:
            violations += 1
            
        history = r.lrange(f"user:{user_id}:amounts", 0, -1)
        if history:
            avg = sum(float(x) for x in history) / len(history)
            if amount > (avg * 3):
                violations += 1
        r.lpush(f"user:{user_id}:amounts", amount)
        r.ltrim(f"user:{user_id}:amounts", 0, 9)
        
        last_loc = r.get(f"user:{user_id}:last_loc")
        last_time = r.get(f"user:{user_id}:last_time")
        if last_loc and last_loc != loc and last_time:
            if now - float(last_time) < 300:
                violations += 1
                
        r.set(f"user:{user_id}:last_loc", loc)
        r.set(f"user:{user_id}:last_time", now)
        
        if violations >= 2:
            print(f"🚨 FRAUD DETECTED: {data}")
        else:
            print(f"✅ APPROVED: {data}")
            
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
    channel = connection.channel()
    channel.queue_declare(queue='transactions', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='transactions', on_message_callback=process_transaction)
    
    print("🚀 Worker is running and waiting for transactions...")
    channel.start_consuming()

if __name__ == '__main__':
    main()
