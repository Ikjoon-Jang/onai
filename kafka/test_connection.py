from kafka import KafkaConsumer

try:
    consumer = KafkaConsumer(
        bootstrap_servers=['3.36.178.68:9092'],
        api_version=(2,5,0),
        request_timeout_ms=10000
    )
    print("✅ Kafka 브로커 연결 성공!")
except Exception as e:
    print(f"❌ Kafka 브로커 연결 실패: {e}")