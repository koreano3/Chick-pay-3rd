from kafka import KafkaProducer
import os

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.kafka.svc.cluster.local:9092")
KAFKA_USER = os.getenv("KAFKA_USERNAME", "user1")
KAFKA_PASS = os.getenv("KAFKA_PASSWORD", "your-password")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=KAFKA_USER,
    sasl_plain_password=KAFKA_PASS
)
