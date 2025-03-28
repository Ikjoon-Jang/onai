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
    "id": "Site010",
    "name": "롱비치항",
    "address": "415 W. Ocean Blvd, Long Beach, CA 90802, USA",
    "country": "USA",
    "city": "Long Beach",
    "latitude": 33.7678,
    "longitude": -118.1893
}

# 토픽으로 메시지 전송
producer.send('qlinx-site-topic', sample_site)
producer.flush()

print("✅ 메시지 전송 완료!")
