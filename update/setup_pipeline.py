# setup_pipeline.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from fuseki.fuseki_query import get_all_ontology_elements
from utils.ontology_to_text import ontology_elements_to_sentences
from embedding.embedding import get_embedding
from embedding.faiss_store import save_faiss_index

# 📌 환경 변수 로드
load_dotenv()

# 📁 로그 폴더 준비
os.makedirs("logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

log_filename = f"logs/pipeline_{timestamp}.log"
sentence_log_filename = f"logs/sentences_{timestamp}.log"

# 🪵 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

# 🧹 기존 FAISS 파일 초기화
index_file = os.getenv("FAISS_INDEX_FILE")
meta_file = os.getenv("FAISS_META_FILE")

if index_file and os.path.exists(index_file):
    os.remove(index_file)
    logging.info(f"🗑️ 기존 인덱스 파일 삭제: {index_file}")

if meta_file and os.path.exists(meta_file):
    os.remove(meta_file)
    logging.info(f"🗑️ 기존 메타데이터 파일 삭제: {meta_file}")

logging.info("🧹 기존 메타데이터 정리 완료 → 새로운 벡터로 재구축 시작")

def save_sentences_to_file(sentences, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for i, s in enumerate(sentences, 1):
            f.write(f"{i}. {s}\n")
    logging.info(f"📄 자연어 문장 {len(sentences)}개를 '{filename}'에 저장 완료")

def main():
    logging.info("🚀 Fuseki에서 온톨로지 요소 불러오는 중...")
    classes, object_props, data_props, individuals, rules = get_all_ontology_elements()
    logging.info("✅ Fuseki 요소 로딩 완료")

    logging.info("🧠 자연어 문장 변환 시작...")
    sentences = ontology_elements_to_sentences(classes, object_props, data_props, individuals, rules)
    save_sentences_to_file(sentences, sentence_log_filename)
    logging.info(f"✅ 총 {len(sentences)}개 문장 생성 완료")

    logging.info("🔍 OpenAI 임베딩 수행 중...")
    embeddings = []
    valid_sentences = []

    for sentence in sentences:
        try:
            emb = get_embedding(sentence)
            embeddings.append(emb)
            valid_sentences.append(sentence)
        except Exception as e:
            logging.warning(f"❌ 임베딩 실패: '{sentence[:30]}...' → {e}")

    # ✅ dict 형태 오염 방지
    embeddings = [e["embedding"] if isinstance(e, dict) else e for e in embeddings]

    logging.info(f"✅ 임베딩 완료: {len(embeddings)}개")

    logging.info("💾 FAISS 인덱스 저장 중...")
    save_faiss_index(valid_sentences, embeddings)
    logging.info("✅ FAISS 저장 완료")

if __name__ == "__main__":
    main()
