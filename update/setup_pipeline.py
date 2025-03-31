import logging
from datetime import datetime
import os

from fuseki.fuseki_query import get_all_ontology_elements
from utils.ontology_to_text import ontology_elements_to_sentences_parallel
from embedding.embedding import embed_sentences
from embedding.faiss_store import save_embeddings_to_faiss

# 🔧 로그 설정
os.makedirs("logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = f"logs/pipeline_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
)

SENTENCE_LOG_FILE = f"logs/sentences_{timestamp}.log"

def save_sentences_to_file(sentences, filename=SENTENCE_LOG_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        for i, s in enumerate(sentences, 1):
            f.write(f"{i}. {s}\n")
    logging.info(f"✅ 자연어 문장 {len(sentences)}개를 '{filename}'에 저장 완료")

def main():
    logging.info("🚀 Fuseki로부터 온톨로지 요소 불러오는 중...")
    data = get_all_ontology_elements()
    logging.info("✅ 불러오기 완료")

    logging.info("📝 자연어 문장 변환 (한글+영문 병렬) 중...")
    sentences = ontology_elements_to_sentences_parallel(
        data["classes"],
        data["object_props"],
        data["data_props"],
        data["individuals"],
        data["rules"]
    )
    logging.info(f"✅ 문장 수: {len(sentences)}")
    save_sentences_to_file(sentences)

    logging.info("🔍 OpenAI 임베딩 중...")
    embeddings = embed_sentences(sentences)
    logging.info(f"✅ 유효 임베딩 수: {len(embeddings)}")

    logging.info("💾 FAISS 인덱스 저장 중...")
    save_embeddings_to_faiss(sentences, embeddings)
    logging.info("🎉 완료! FAISS 인덱스 재구축 완료")

if __name__ == "__main__":
    main()
