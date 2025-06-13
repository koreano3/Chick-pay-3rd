from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'user-signup',  # user-service에서 발행한 토픽 이름
    bootstrap_servers='kafka.infra.svc.cluster.local:9092',  # 카프카 주소 (user-service와 동일하게)
    auto_offset_reset='earliest',    # 처음부터 메시지 읽기
    enable_auto_commit=True,
    group_id='test-group',           # 아무거나 지정(여러 번 테스트할 때 그룹명 바꿔도 됨)
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("카프카 메시지 대기중... (Ctrl+C로 종료)")
for message in consumer:
    print("받은 메시지:", message.value)
