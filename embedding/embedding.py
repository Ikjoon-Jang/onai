# embedding.py (OpenAI v1.0 이상 호환)
import os
import logging
from typing import List, Union
from openai import OpenAI
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 사용할 임베딩 모델 지정
EMBEDDING_MODEL =  os.getenv("EMBEDDING_MODEL") 
# "text-embedding-3-small"

# ✅ 단일 텍스트를 임베딩 벡터로 변환
def get_embedding(text: str) -> List[float]:
    try:
        logging.info(f"📝 임베딩 요청 문장: {text[:100]}")  # 최대 100자까지 출력

        response = client.embeddings.create(
            input=[text],
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding

        # ✅ 방어적 체크
        if not isinstance(embedding, list) or not all(isinstance(x, float) for x in embedding):
            raise ValueError(f"임베딩 형식 오류: {embedding[:5]}...")

        return embedding

    except Exception as e:
        logging.error(f"❌ 임베딩 실패: {e}")
        raise

# ✅ 복수 문장을 벡터로 변환 (배치)
def embed_sentences(sentences: List[str]) -> List[List[float]]:
    embeddings = []
    for s in sentences:
        try:
            embeddings.append(get_embedding(s))
        except Exception as e:
            logging.warning(f"⚠️ 문장 임베딩 실패: '{s}' → {e}")
    return embeddings
