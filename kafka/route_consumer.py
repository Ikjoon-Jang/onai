from kafka import KafkaConsumer
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging
import faiss
import numpy as np
import pickle

# 1. 환경 변수 로드
load_dotenv()

# 2. OpenAI 클라이언트 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. 로그 설정
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/qlinx_route_consumer.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


# 4. FAISS 인덱스 설정
faiss_index_file = os.getenv("FAISS_INDEX_FILE")
faiss_metadata_file = os.getenv("FAISS_META_FILE")
os.makedirs("faiss", exist_ok=True)

embedding_dim = 1536
if os.path.exists(faiss_index_file):
    index = faiss.read_index(faiss_index_file)
    with open(faiss_metadata_file, "rb") as f:
        metadata_list = pickle.load(f)
else:
    index = faiss.IndexFlatL2(embedding_dim)
    metadata_list = []

# 5. JSON → 병렬 자연어 문장 변환 함수
def route_json_to_text(data: dict) -> str:
    route_id = data.get("id", "(unknown)")
    name = data.get("name", "(no name)")
    duration = data.get("transit_days", "N/A")
    waiting = data.get("departure_waiting_days", "N/A")
    storage = data.get("storage_cost", "N/A")
    transport = data.get("transport_cost", "N/A")
    currency = data.get("currency", "N/A")
    mode = data.get("transport_mode", "N/A")
    distance = data.get("transport_distance", "N/A")
    unit = data.get("distance_unit", "N/A")
    departure = data.get("departure", "(unknown)")
    destination = data.get("destination", "(unknown)")

    # 영어 문장
    eng = (
        f"{route_id} is a Route named {name}. "
        f"It takes {duration} days of transport and {waiting} days of waiting at departure. "
        f"The storage cost is {storage}, transport cost is {transport}, using {currency}. "
        f"Transport mode: {mode}, distance: {distance} {unit}. "
        f"It starts from {departure} and ends at {destination}."
    )

    # 한글 문장
    kor = (
        f"{route_id}는 '{name}'이라는 이름의 경로입니다. "
        f"운송 소요일은 {duration}일이며, 출발 대기일은 {waiting}일입니다. "
        f"보관비용은 {storage}, 운송비용은 {transport}, 통화는 {currency}입니다. "
        f"운송 유형은 {mode}이고, 운송 거리는 {distance} {unit}입니다. "
        f"{departure}에서 출발하여 {destination}까지 운송됩니다."
    )

    return f"{kor} / {eng}"

# 6. 임베딩 함수
def embed_text(text: str):
    try:
        logging.info(f"🔍 Embedding 시작: {text[:100]}")
        model_name = os.getenv("EMBEDDING_MODEL")
        if not model_name:
            raise ValueError("❌ EMBEDDING_MODEL 환경변수가 설정되지 않았습니다.")

        response = client.embeddings.create(
            input=text,
            model=model_name
        )
        return response.data[0].embedding
    except Exception as e:
        logging.exception("❌ OpenAI embedding 중 오류 발생")
        return []

# 7. 전체 처리 함수
def create_route_individual(data):
    logging.info(f"✅ Received: {json.dumps(data, ensure_ascii=False)}")
    text = route_json_to_text(data)
    print(text)
    logging.info(f"📝 Converted to text: {text}")

    embedding = embed_text(text)
    if not embedding:
        return

    vector = np.array(embedding, dtype=np.float32).reshape(1, -1)

    # FAISS에 추가
    index.add(vector)
    metadata_list.append({
        "text": text,
        "source": "route",
        "raw": data
    })

    # 저장
    faiss.write_index(index, faiss_index_file)
    with open(faiss_metadata_file, "wb") as f:
        pickle.dump(metadata_list, f)

    logging.info(f"📌 Added to FAISS. Total vectors: {index.ntotal}")

# 8. Kafka Consumer 시작
consumer = KafkaConsumer(
    os.getenv("ROUTE_TOPIC_NAME"),
    bootstrap_servers=os.getenv("KAFKA_IP"),
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("📡 Listening on topic:", os.getenv("ROUTE_TOPIC_NAME"))

for message in consumer:
    route_data = message.value
    print(route_data)
    try:
        create_route_individual(route_data)
    except Exception as e:
        logging.error(f"❌ Error in create_route_individual: {e}")
        print("❌ 오류 발생:", e)
