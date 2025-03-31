from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

# 2. Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_IP"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 3. 샘플 Route 데이터 (Ontology 기준에 맞게 구성)
sample_route = {
    "id": "Route001",
    "name": "아산공장-부산항",
    "transit_days": 1,
    "departure_waiting_days": 0,
    "storage_cost": 0,
    "transport_cost": 300000,
    "currency": "KRW",
    "transport_mode": "Truck",
    "transport_distance": 430.5,
    "distance_unit": "km",
    "departure": "Site001",        
    "destination": "Site002"       
}

# 4. Kafka 토픽으로 전송
producer.send(os.getenv("ROUTE_TOPIC_NAME"), sample_route)
producer.flush()

print("✅ Route 메시지 전송 완료!")
