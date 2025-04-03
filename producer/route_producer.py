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

# 3. 여러 Route 샘플 데이터
sample_routes = [
    {
        "id": "Route001",
        "name": "아산공장-부산항",
        "transit_days": 1,
        "minimum_storage_waiting_days": 0,
        "daily_storage_cost": 50000,
        "transport_cost": 300000,
        "currency": "KRW",
        "transport_mode": "Truck",
        "transport_distance": 430.5,
        "distance_unit": "km",
        "departure": "Site001",
        "destination": "Site002"
    },
    {
        "id": "Route002",
        "name": "부산항-롱비치#1",
        "transit_days": 2,
        "minimum_storage_waiting_days": 1,
        "daily_storage_cost": 50,
        "transport_cost": 3000,
        "currency": "USD",
        "transport_mode": "Air",
        "transport_distance": 6025,
        "distance_unit": "mi",
        "departure": "Site002",
        "destination": "Site010"
    },
    {
        "id": "Route003",
        "name": "부산항-롱비치#2",
        "transit_days": 15,
        "minimum_storage_waiting_days": 2,
        "daily_storage_cost": 100,
        "transport_cost": 500,
        "currency": "USD",
        "transport_mode": "Sea",
        "transport_distance": 6025,
        "distance_unit": "mi",
        "departure": "Site002",
        "destination": "Site010"
    },
    {
        "id": "Route004",
        "name": "부산항-롱비치#3",
        "transit_days": 20,
        "minimum_storage_waiting_days": 1,
        "daily_storage_cost": 50,
        "transport_cost": 300,
        "currency": "USD",
        "transport_mode": "Sea",
        "transport_distance": 6025,
        "distance_unit": "mi",
        "departure": "Site002",
        "destination": "Site010"
    },
    {
        "id": "Route005",
        "name": "롱비치-LA야드",
        "transit_days": 1,
        "minimum_storage_waiting_days": 2,
        "daily_storage_cost": 100,
        "transport_cost": 300,
        "currency": "USD",
        "transport_mode": "Rail",
        "transport_distance": 30,
        "distance_unit": "mi",
        "departure": "Site010",
        "destination": "Site011"
    },
    {
        "id": "Route006",
        "name": "LA야드-배송야드",
        "transit_days": 1,
        "minimum_storage_waiting_days": 1,
        "daily_storage_cost": 50,
        "transport_cost": 200,
        "currency": "USD",
        "transport_mode": "Truck",
        "transport_distance": 20,
        "distance_unit": "mi",
        "departure": "Site011",
        "destination": "Site015"
    }
]

# 4. Kafka 토픽으로 반복 전송
for route in sample_routes:
    producer.send(os.getenv("ROUTE_TOPIC_NAME"), route)
    print(f"✅ Route 전송 완료: {route['id']}")

producer.flush()
