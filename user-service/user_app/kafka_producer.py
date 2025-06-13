from kafka import KafkaProducer
import json

import logging
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='kafka.infra.svc.cluster.local:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


def send_user_signup_event(user_data):
    try:
        logger.info(f"Sending message to Kafka: {user_data}")
        future = producer.send('user-signup', user_data)
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
        producer.flush()
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {str(e)}")
        raise