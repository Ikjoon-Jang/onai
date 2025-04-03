import pandas as pd
import os
from openai import OpenAI
from faiss_store import save_embeddings_to_faiss
from dotenv import load_dotenv

# .env에서 API 키 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 생성
client = OpenAI(api_key=api_key)

# 엑셀 파일 경로
EXCEL_PATH = os.getenv("CARRIER_FILE")

# 1. 엑셀 파일 로드
df = pd.read_excel(EXCEL_PATH)

# 2. 텍스트 데이터 구성: 주소 기반 문장
def convert_to_text(row):
    return (
        f"{row['SHIPTO_NM']} is located at {row['TOT_ADDR']} "
        f"({row['CITY_NM']}, {row['STATE_NM']}, ZIP: {row['ZIP']}). "
        f"Coordinates are LAT: {row['LAT']}, LON: {row['LON']}."
    )

sentences = df.apply(convert_to_text, axis=1).tolist()

# 3. OpenAI 임베딩 요청
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=sentences
)

embeddings = [r.embedding for r in response.data]

# 4. FAISS 저장
save_embeddings_to_faiss(sentences, embeddings)
print("✅ 운송사 정보 임베딩 및 저장 완료!")
