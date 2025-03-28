from kafka import KafkaProducer
import json

import os

from dotenv import load_dotenv
load_dotenv()

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_IP"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 샘플 Site 데이터 (Ontology에 맞게 수정 가능)
sample_site = {
    "id": "Site002",
    "name": "아산공장",
    "address": "충청남도 아산시 시민로 456",
    "country": "대한민국",
    "city": "아산",
    "latitude": 36.7890,
    "longitude": 127.0010
}

# 토픽으로 메시지 전송
producer.send('qlinx-site-topic', sample_site)
producer.flush()

print("✅ 메시지 전송 완료!")
