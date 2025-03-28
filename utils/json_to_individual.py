import os
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF

from dotenv import load_dotenv
load_dotenv()

FORWARDING = Namespace(os.getenv("ROOT_NAMESPACE"))
#FORWARDING = Namespace("http://www.qlinx.co.kr/ontology/forwarding#")

def parse_message_to_dict(message_str):
    parts = message_str.split()
    data = {}
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            data[key] = value
    return data

def json_to_rdf(message_str):
    g = Graph()
    g.bind("forwarding", FORWARDING)

    data = parse_message_to_dict(message_str)

    order_uri = URIRef(FORWARDING[f"Order_{data['order_id']}"])
    g.add((order_uri, RDF.type, FORWARDING.Order))
    g.add((order_uri, FORWARDING.orderId, Literal(data['order_id'])))
    g.add((order_uri, FORWARDING.departure, Literal(data['departure'])))
    g.add((order_uri, FORWARDING.destination, Literal(data['destination'])))
    g.add((order_uri, FORWARDING.customer, Literal(data['customer'])))
    g.add((order_uri, FORWARDING.status, Literal(data['status'])))

    return g
