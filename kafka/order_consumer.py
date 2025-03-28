from kafka import KafkaConsumer
import json
import os

from dotenv import load_dotenv
load_dotenv()

def create_order_individual(data):
    print("Creating Order Individual:", data)
    # TODO: Convert JSON to RDF Triple and send to Fuseki

consumer = KafkaConsumer(
    # 'qlinx-order-topic',
    os.getenv("ORDER_TOPIC_NAME"),
    # bootstrap_servers='localhost:9092',
    bootstrap_servers=os.getenv("KAFKA_IP"),
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening on topic: qlinx-order-topic")
for message in consumer:
    order_data = message.value
    create_order_individual(order_data)