import pickle
import os
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

# 2. 메타데이터 로딩
with open(os.getenv("FAISS_META_FILE"), "rb") as f:
    data = pickle.load(f)

# 3. 최근 5개 출력 (방어적 출력)
for i, item in enumerate(data[-37:]):
    if isinstance(item, dict) and "text" in item:
        print(f"[{i}] {item['text']}")
    else:
        print(f"[{i}] (Invalid item): {item}")
