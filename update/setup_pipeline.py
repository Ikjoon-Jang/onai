import os
import pickle
from dotenv import load_dotenv
from embedding.faiss_store import save_embeddings_to_faiss
from utils.ontology_to_text import ontology_elements_to_sentences
from fuseki.fuseki_query import get_all_ontology_elements
import faiss

# 1. 환경 변수 로드
load_dotenv()

FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE")
FAISS_META_FILE = os.getenv("FAISS_META_FILE")

# ✅ 기존 FAISS 인덱스 및 메타데이터 초기화
if os.path.exists(FAISS_INDEX_FILE):
    os.remove(FAISS_INDEX_FILE)
    print(f"🧹 기존 인덱스 파일 삭제: {FAISS_INDEX_FILE}")

if os.path.exists(FAISS_META_FILE):
    with open(FAISS_META_FILE, "rb") as f:
        old_data = pickle.load(f)

    cleaned = []
    for item in old_data:
        if isinstance(item, str):
            cleaned.append({"text": item, "source": "legacy"})
        elif isinstance(item, dict) and "text" in item:
            cleaned.append(item)

    with open(FAISS_META_FILE, "wb") as f:
        pickle.dump(cleaned, f)

    print(f"🧹 기존 메타데이터 정리 완료: {len(cleaned)}개 항목 유지")

# 2. Fuseki에서 온톨로지 요소 가져오기
classes, object_props, data_props, individuals, rules = get_all_ontology_elements()

# 3. 요소들을 자연어 문장으로 변환 후 메타데이터 포맷 통일
sentences = ontology_elements_to_sentences(classes, object_props, data_props, individuals, rules)
metadata = [{"text": s, "source": "ontology"} for s in sentences]

# 4. FAISS 저장
save_embeddings_to_faiss(sentences, metadata)

print(f"✅ 총 {len(sentences)}개의 문장을 임베딩하고 인덱스를 새로 저장했습니다.")
