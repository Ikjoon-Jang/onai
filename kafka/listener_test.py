from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'qlinx-orders',
    bootstrap_servers=['3.36.178.68:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-basic-group',
    value_deserializer=lambda x: x.decode('utf-8')
)

print("🌀 Kafka consumer 진입")

for message in consumer:
    print("📩 메시지 수신:", message.value)