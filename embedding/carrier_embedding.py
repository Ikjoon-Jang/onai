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
df = pd.read_excel(EXCEL_PATH)

# 누락된 row 저장용 리스트
invalid_rows = []

# 1. 텍스트 데이터 구성 함수
def convert_to_text(row):
    try:
        return (
            f"{row['SHIPTO_NM']} is located at {row['TOT_ADDR']} "
            f"({row['CITY_NM']}, {row['STATE_NM']}, ZIP: {row['ZIP']}). "
            f"Coordinates are LAT: {row['LAT']}, LON: {row['LON']}."
        )
    except Exception as e:
        print(f"⚠️ 누락된 데이터로 인해 건너뜀: {row.get('SHIPTO_NM', 'N/A')} / 오류: {e}")
        invalid_rows.append(row)
        return None

# 2. 문장 생성 및 유효한 것만 추출
sentences_raw = df.apply(convert_to_text, axis=1).tolist()
sentences = [s for s in sentences_raw if s]

# 3. 누락된 데이터가 있다면 CSV로 저장
if invalid_rows:
    invalid_df = pd.DataFrame(invalid_rows)
    invalid_path = os.path.join("data", "invalid_carriers.csv")
    invalid_df.to_csv(invalid_path, index=False)
    print(f"⚠️ 누락된 {len(invalid_rows)}개의 행이 {invalid_path} 파일에 저장되었습니다.")

# 4. 유효한 데이터가 없으면 종료
if not sentences:
    raise ValueError("❌ 유효한 문장이 없습니다. 데이터를 확인하세요.")

# 5. 임베딩 요청
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=sentences
)

embeddings = [r.embedding for r in response.data]

# 6. FAISS에 저장
save_embeddings_to_faiss(sentences, embeddings)
print("✅ 운송사 정보 임베딩 및 저장 완료!")
