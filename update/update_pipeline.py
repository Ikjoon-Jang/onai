# update_pipeline.py
import logging
from datetime import datetime
from fuseki.fuseki_query import (
    get_classes,
    get_object_properties,
    get_data_properties,
    get_individuals_with_literals_and_relations,
    get_swrl_rules,
)
from utils.ontology_to_text import ontology_elements_to_sentences
from utils.ontology_to_text import triples_to_sentences
from embedding.embedding import get_embedding
from embedding.embedding import embed_sentences
from embedding.faiss_store import save_faiss_index

from utils.ontology_to_text import triples_to_natural_text
from fuseki.fuseki_query import get_triples_for_individual
from embedding.faiss_store import append_to_faiss_index

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = f"logs/update_pipeline_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

def save_sentences_to_file(sentences, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for i, s in enumerate(sentences, 1):
            f.write(f"{i}. {s}\n")

def update_single_individual_index(individual_uri: str):
    try:
        logging.info(f"🔍 Fuseki에서 triple 조회: {individual_uri}")
        triples = get_triples_for_individual(individual_uri)

        if not triples:
            logging.warning(f"⚠️ triple이 없습니다: {individual_uri}")
            return False

        logging.info(f"📄 triple → 자연어 문장 변환 중...")
        sentences = triples_to_natural_text(triples)
        logging.info(f"📄 변환된 문장 수: {len(sentences)}")

        logging.info(f"🔢 문장 → OpenAI 임베딩 중...")
        embeddings = embed_sentences(sentences)

        logging.info(f"🧾 문장 샘플: {sentences[0]}")
        logging.info(f"📐 임베딩 길이: {len(embeddings[0])}, 타입: {type(embeddings[0][0])}")

        logging.info(f"💾 FAISS에 임베딩 추가 중...")
        append_to_faiss_index(sentences, embeddings)

        logging.info(f"✅ 단일 Individual 인덱스 업데이트 완료: {individual_uri}")
        return True

    except Exception as e:
        logging.error(f"❌ 단일 인덱스 업데이트 실패: {e}")
        return False



def main():
    logging.info("📡 Fuseki로부터 온톨로지 요소 수집 중...")
    classes = get_classes()
    obj_props = get_object_properties()
    data_props = get_data_properties()
    individuals = get_individuals_with_literals_and_relations()
    rules = get_swrl_rules()

    logging.info("🧠 자연어 문장 변환 중...")
    sentences = ontology_elements_to_sentences(classes, obj_props, data_props, individuals, rules)
    logging.info(f"✅ 총 {len(sentences)}개 문장 생성됨")
    
    sentence_file = f"logs/sentences_{timestamp}.log"
    save_sentences_to_file(sentences, sentence_file)

    embeddings = []
    valid_sentences = []
    logging.info("🧬 임베딩 생성 시작")
    for s in sentences:
        try:
            emb = get_embedding(s)
            embeddings.append(emb)
            valid_sentences.append(s)
        except Exception as e:
            logging.warning(f"임베딩 실패: {s} => {e}")

    save_faiss_index(valid_sentences, embeddings)
    logging.info("✅ FAISS 인덱스 저장 완료")

if __name__ == "__main__":
    main()
