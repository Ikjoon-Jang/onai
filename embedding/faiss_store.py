import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# 환경 변수로부터 인덱스 및 메타데이터 경로 가져오기
INDEX_FILE = os.getenv("FAISS_INDEX_FILE", "faiss_index.index")
META_FILE = os.getenv("FAISS_META_FILE", "faiss_metadata.pkl")
VECTOR_SIZE = 1536  # OpenAI embedding vector size

# 🔹 벡터 + 문장을 FAISS 인덱스 및 메타데이터에 저장
def save_embeddings_to_faiss(sentences: List[str], embeddings: List[List[float]]):
    vectors = np.array(embeddings, dtype="float32")

    # 기존 인덱스와 메타데이터 불러오기 (없으면 새로 생성)
    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(VECTOR_SIZE)
        metadata = []

    # 벡터 추가
    index.add(vectors)
    metadata.extend([{"text": s, "source": "ontology"} for s in sentences])
    # metadata.extend(sentences)

    # 저장
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ 저장 완료: {len(sentences)}개 문장을 FAISS에 저장했습니다.")

# 🔹 FAISS 인덱스와 메타데이터 불러오기
def load_index_and_metadata() -> Tuple[faiss.IndexFlatL2, List[str]]:
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

# 🔹 질의 벡터로 유사 문장 검색
import numpy as np

def search_faiss(query_vector, index, metadata, k=5):
    """
    FAISS 인덱스를 사용하여 유사한 문장을 검색합니다.
    거리 값을 유사도로 변환하여 함께 반환합니다.
    """
    query = np.array([query_vector], dtype="float32")
    D, I = index.search(query, k)

    results = []
    for idx, i in enumerate(I[0]):
        if i < len(metadata):
            item = metadata[i]
            # dict이면 "text" 키 우선, 아니면 str(item)
            if isinstance(item, dict):
                text = item.get("text", str(item))
            else:
                text = str(item)
            distance = float(D[0][idx])
            similarity = 1 / (1 + distance)  # 🎯 유사도 계산 (0~1 사이, 높을수록 유사)
            results.append((text, similarity))
        else:
            results.append((f"(Invalid index {i})", 0.0))
    return results


def save_faiss_index(sentences: List[str], embeddings: List[List[float]]):
    # 벡터 준비
    vectors = np.array(embeddings, dtype="float32")

    # FAISS 인덱스 초기화 및 추가
    index = faiss.IndexFlatL2(VECTOR_SIZE)
    index.add(vectors)

    # 인덱스 저장
    faiss.write_index(index, INDEX_FILE)

    # 메타데이터 저장
    with open(META_FILE, "wb") as f:
        pickle.dump(sentences, f)

    print(f"✅ 저장 완료: {len(sentences)}개 문장을 FAISS에 저장했습니다.")