from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_IP"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 여러 개의 Site 데이터 리스트
sample_sites = [
    {
        "id": "Site001",
        "name": "아산공장",
        "address": "충청남도 아산시 시민로 456",
        "country": "대한민국",
        "city": "아산시",
        "latitude": 36.7890,
        "longitude": 127.0010,
        "type": "Site"
    },
    {
        "id": "Site002",
        "name": "부산항",
        "address": "부산광역시 강서구 성북동 1",
        "country": "대한민국",
        "city": "부산광역시",
        "latitude": 35.0525,
        "longitude": 128.8336,
        "type": "Site"
    },
    {
        "id": "Site010",
        "name": "롱비치항",
        "address": "415 W. Ocean Blvd, Long Beach, CA 90802, USA",
        "country": "USA",
        "city": "Long Beach",
        "latitude": 33.7678,
        "longitude": -118.1893,
        "type": "Site"
    },
    {
        "id": "Site011",
        "name": "LA야드",
        "address": "200 N Spring St, Los Angeles, CA 90012, USA",
        "country": "USA",
        "city": "Los Angeles",
        "latitude": 34.0537,
        "longitude": -118.2428,
        "type": "Site"
    },
    {
        "id": "Site015",
        "name": "배송야드",
        "address": "1 Civic Center Plaza, Irvine, CA 92606, USA",
        "country": "USA",
        "city": "Irvine",
        "latitude": 33.6846,
        "longitude": -117.8265,
        "type": "Site"
    }
]

# 토픽으로 메시지 반복 전송
for site in sample_sites:
    producer.send('qlinx-site-topic', site)
    print(f"✅ 메시지 전송 완료: {site['id']}")

producer.flush()
