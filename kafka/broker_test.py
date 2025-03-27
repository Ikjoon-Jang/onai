from kafka import KafkaConsumer

try:
    consumer = KafkaConsumer(bootstrap_servers=['3.36.178.68:9092'])
    topics = consumer.topics()
    print("✅ Kafka 브로커 연결 성공! 사용 가능한 토픽 목록:", topics)
except Exception as e:
    print("❌ Kafka 브로커 연결 실패:", e)