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
faiss_index_file = "faiss/site_index.index"
faiss_metadata_file = "faiss/site_metadata.pkl"
os.makedirs("faiss", exist_ok=True)

# 인덱스 로드 또는 초기화
embedding_dim = 1536
if os.path.exists(faiss_index_file):
    index = faiss.read_index(faiss_index_file)
    with open(faiss_metadata_file, "rb") as f:
        metadata_list = pickle.load(f)
else:
    index = faiss.IndexFlatL2(embedding_dim)
    metadata_list = []

# 5. JSON → 자연어 문장 변환
def site_json_to_text(site: dict) -> str:
    return (
        # f"{site.get('city', '도시')} {site.get('address', '주소')}에 위치한 사이트는 "
        # f"아이디는 {site.get('id', '아이디')} 이며, 이름은 {site.get('name', '이름')} 이고, "
        # f"위도 {site.get('latitude', '위도')}°, 경도 {site.get('longitude', '경도')}°에 있으며, "
        # f"{site.get('country', '국가')}에 속합니다."
    )

# 6. OpenAI 임베딩
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
    text = site_json_to_text(data)
    print(text)
    logging.info(f"📝 Converted to text: {text}")
    embedding = embed_text(text)
    vector = np.array(embedding, dtype=np.float32).reshape(1, -1)
    print("FAISS에 추가")
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

# 8. Kafka Consumer
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