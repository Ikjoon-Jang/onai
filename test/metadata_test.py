import pickle
import os
from dotenv import load_dotenv

load_dotenv()
meta_file = os.getenv("FAISS_META_FILE")

with open(meta_file, "rb") as f:
    data = pickle.load(f)

cleaned = []
for item in data:
    if isinstance(item, str):
        cleaned.append({"text": item, "source": "legacy"})
    elif isinstance(item, dict) and "text" in item:
        cleaned.append(item)

with open(meta_file, "wb") as f:
    pickle.dump(cleaned, f)

print(f"✅ 정제 완료: {len(cleaned)}개 항목 저장")
