from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_user_created_event(user_id, email):
    message = {
        "event": "user_created",
        "user_id": user_id,
        "email": email
    }
    producer.send("user-signup", message)  # ✅ 통일된 토픽명
    producer.flush()
