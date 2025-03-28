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
    "id": "Site015",
    "name": "배송야드",
    "address": "1 Civic Center Plaza, Irvine, CA 92606, USA",
    "country": "USA",
    "city": "Irvine",
    "latitude": 33.6846,
    "longitude": -117.8265
}

# 토픽으로 메시지 전송
producer.send('qlinx-site-topic', sample_site)
producer.flush()

print("✅ 메시지 전송 완료!")
