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
    "id": "Site001",
    "name": "부산항",
    "address": "부산광역시 영도구 해양로 301번길",
    "country": "대한민국",
    "city": "부산",
    "latitude": 35.0952,
    "longitude": 129.0403
}

# 토픽으로 메시지 전송
producer.send('qlinx-site-topic', sample_site)
producer.flush()

print("✅ 메시지 전송 완료!")
