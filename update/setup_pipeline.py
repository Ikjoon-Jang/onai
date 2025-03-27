import logging
from datetime import datetime
import os

from fuseki.fuseki_query import (
    get_classes,
    get_object_properties,
    get_data_properties,
    get_individuals_with_literals_and_relations,
    get_swrl_rules,
)
from utils.ontology_to_text import ontology_elements_to_sentences
from embedding.embedding import get_embedding
from embedding.faiss_store import save_faiss_index

os.makedirs("logs", exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/pipeline_{timestamp}.log"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

SENTENCE_LOG_FILE = f"logs/sentences_{timestamp}.log"

def save_sentences_to_file(sentences, filename=SENTENCE_LOG_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        for i, sentence in enumerate(sentences, 1):
            f.write(f"{i}. {sentence}\n")
    logging.info(f"📝 자연어 문장 {len(sentences)}개를 '{filename}'에 저장 완료")

def main():
    logging.info("🚀 Fuseki에서 온톨로지 요소 가져오는 중...")
    classes = get_classes()
    object_props = get_object_properties()
    data_props = get_data_properties()
    individuals = get_individuals_with_literals_and_relations()
    swrl_rules = get_swrl_rules()
    logging.info("✅ 온톨로지 요소 불러오기 완료")

    logging.info("🧠 자연어 문장으로 변환 중...")
    sentences = ontology_elements_to_sentences(
        classes, object_props, data_props, individuals, swrl_rules
    )
    logging.info(f"✅ 총 {len(sentences)}개의 문장 생성")
    save_sentences_to_file(sentences)

    logging.info("🔍 OpenAI 임베딩 생성 중...")
    embeddings = []
    valid_sentences = []
    for sentence in sentences:
        try:
            emb = get_embedding(sentence)
            embeddings.append(emb)
            valid_sentences.append(sentence)
        except Exception as e:
            logging.warning(f"❌ 임베딩 실패: '{sentence}' => {e}")

    logging.info(f"✅ 임베딩 생성 완료: {len(embeddings)}개")

    logging.info("💾 FAISS 인덱스 저장 중...")
    save_faiss_index(valid_sentences, embeddings)
    logging.info("✅ FAISS 인덱스 저장 완료")

if __name__ == "__main__":
    main()
