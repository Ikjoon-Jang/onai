from kafka import KafkaConsumer
import json
import os

from dotenv import load_dotenv
load_dotenv()

# Fuseki에 RDF 데이터 전송 함수 (예시)
def create_site_individual(data):
    print("Creating Site Individual:", data)
    # TODO: Convert JSON to RDF Triple and send to Fuseki

consumer = KafkaConsumer(
    # 'qlinx-site-topic',
    os.getenv("SITE_TOPIC_NAME"),
    bootstrap_servers=os.getenv("KAFKA_IP"),
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening on topic: qlinx-site-topic")
for message in consumer:
    site_data = message.value
    create_site_individual(site_data)