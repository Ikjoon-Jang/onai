from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='3.36.178.68:9092',
    value_serializer=lambda x: x.encode('utf-8')
)

producer.send('qlinx-orders', value='order_id:TEST-001 departure:l0001 destination:l0002 customer:c999 status:new')
producer.flush()