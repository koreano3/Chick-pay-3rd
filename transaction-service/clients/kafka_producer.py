from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka.infra.svc.cluster.local:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_transaction_event(event_type, data):
    message = {"event": event_type, **data}
    producer.send("transaction-events", message)
    producer.flush()
