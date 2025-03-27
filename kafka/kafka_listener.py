# kafka_listener.py
from kafka import KafkaConsumer
import json
import logging
import time
from utils.json_to_individual import json_to_rdf
from fuseki.fuseki_insert import insert_triple_to_fuseki
from update.update_pipeline import update_single_individual_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/kafka_listener.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

def parse_kv_string_to_dict(message_str: str) -> dict:
    result = {}
    for item in message_str.strip().split():
        if ':' in item:
            key, value = item.split(':', 1)
            result[key.strip()] = value.strip()
    return result

KAFKA_BROKER = '3.36.178.68:9092'  # 필요 시 수정
KAFKA_TOPIC = 'qlinx-orders'       # 실제 사용하는 토픽명으로 변경

def start_kafka_listener():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=f'onai-test-group-{int(time.time())}',  # ← 유일한 그룹 ID
        value_deserializer=lambda m: m.decode('utf-8'),  # ← JSON 아님
    )

    logging.info(f"📡 Kafka Topic '{KAFKA_TOPIC}' 수신 대기 중...")

    for message in consumer:
        try:
            logging.info("🔥 Kafka 메시지 루프 진입 성공!")
            data = message.value

            if not data.strip():
                logging.warning("⚠️ 빈 메시지 수신됨. 건너뜀.")
                continue
            
            if not data:
                logging.warning("⚠️ 수신된 메시지 값이 비어있습니다.")
                continue

            logging.info(f"📥 메시지 수신: #####{data}#####")

            rdf_graph = json_to_rdf(data)
            logging.info(f"🧾 변환된 RDF triple 수: {len(rdf_graph)}")
            for s, p, o in rdf_graph:
                logging.info(f"▶️ {s} {p} {o}")

            inserted = insert_triple_to_fuseki(rdf_graph)

            if inserted:
                individual_uri = str([s for s, p, o in rdf_graph if str(p).endswith("#type")][0])
                update_single_individual_index(individual_uri)

        except Exception as e:
            logging.error(f"❌ 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    start_kafka_listener()
