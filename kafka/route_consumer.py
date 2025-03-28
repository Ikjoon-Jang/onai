from kafka import KafkaConsumer
import json
import os

from dotenv import load_dotenv
load_dotenv()

def create_route_individual(data):
    print("Creating Route Individual:", data)
    # TODO: Convert JSON to RDF Triple and send to Fuseki

consumer = KafkaConsumer(
    # 'qlinx-route-topic',
    os.getenv("ROUTE_TOPIC_NAME"),
    bootstrap_servers=os.getenv("KAFKA_IP"),
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening on topic: qlinx-route-topic")
for message in consumer:
    route_data = message.value
    create_route_individual(route_data)