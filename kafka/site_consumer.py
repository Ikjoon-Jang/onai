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
    filename="logs/qlinx_site_consumer.log",
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

# 5. JSON → 자연어 병렬 문장 변환 함수
def individual_json_to_text(data: dict) -> str:
    type_name = data.get("type", "Site")
    ind_id = data.get("id", "(unknown)")
    name = data.get("name", "(no name)")
    address = data.get("address", "주소 정보 없음")
    city = data.get("city", "도시 정보 없음")
    country = data.get("country", "국가 정보 없음")
    lat = data.get("latitude", "위도 없음")
    lon = data.get("longitude", "경도 없음")

    # 영어 문장
    eng = (
        f"{ind_id} is an individual of type {type_name}. "
        f"Its name is {name}. "
        f"It is located in {city}, at {address}, with latitude {lat}° and longitude {lon}° in {country}."
    )

    # 한글 문장
    kor = (
        f"{ind_id}는 {type_name} 타입의 개체입니다. 이름은 {name}이며, "
        f"{country} {city}의 {address}에 위치해 있고, "
        f"위도는 {lat}°, 경도는 {lon}°입니다."
    )

    return f"{kor} / {eng}"


# 6. 임베딩 함수
def embed_text(text: str):
    try:
        response = client.embeddings.create(
            input=text,
            model=os.getenv("EMBEDDING_MODEL")
            # "text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"❌ OpenAI embedding error: {e}")
        return []

# 7. 전체 처리 함수
def create_site_individual(data):
    logging.info(f"✅ Received: {json.dumps(data, ensure_ascii=False)}")
    text = individual_json_to_text(data)
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
        "source": "site",
        "raw": data
    })

    # 저장
    faiss.write_index(index, faiss_index_file)
    with open(faiss_metadata_file, "wb") as f:
        pickle.dump(metadata_list, f)

    logging.info(f"📌 Added to FAISS. Total vectors: {index.ntotal}")

# 8. Kafka Consumer 시작
consumer = KafkaConsumer(
    os.getenv("SITE_TOPIC_NAME"),
    bootstrap_servers=os.getenv("KAFKA_IP"),
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("📡 Listening on topic:", os.getenv("SITE_TOPIC_NAME"))

for message in consumer:
    site_data = message.value
    print(site_data)
    try:
        create_site_individual(site_data)
    except Exception as e:
        logging.error(f"❌ Error in create_site_individual: {e}")
        print("❌ 오류 발생:", e)
