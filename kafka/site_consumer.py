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

# 5. JSON → 자연어 문장 변환 함수 (Class 연관 포함)
def individual_json_to_text(data: dict) -> str:
    type_name = data.get("type", "Site")  # 기본값을 Site로 설정
    ind_id = data.get("id", "(unknown)")

    text = f"{ind_id} is an individual of type {type_name}."

    name_info = f" Its name is {data.get('name', '(no name)')}."
    location = (
        f" It is located in {data.get('city', 'a city')}, at {data.get('address', 'an address')}, "
        f"with latitude {data.get('latitude', 'N/A')}° and longitude {data.get('longitude', 'N/A')}° in {data.get('country', 'a country')}."
    )

    return f"{text}{name_info}{location}"

# 6. 임베딩 함수
def embed_text(text: str):
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
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
