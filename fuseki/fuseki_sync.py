# fuseki_sync.py
import rdflib
import requests
import logging

FUSEKI_QUERY_URL = "http://3.36.178.68:3030/qlinx/query"
FUSEKI_UPDATE_URL = "http://3.36.178.68:3030/qlinx/update"
RDF_FILE = "./data/rdf.xml"

def load_local_graph():
    g = rdflib.Graph()
    g.parse(RDF_FILE, format="xml")
    return g

def load_fuseki_graph():
    g = rdflib.Graph()
    query = """
    CONSTRUCT { ?s ?p ?o }
    WHERE { ?s ?p ?o }
    """
    headers = {"Accept": "application/rdf+xml"}
    res = requests.post(FUSEKI_QUERY_URL, data={"query": query}, headers=headers)
    res.raise_for_status()
    g.parse(data=res.text, format="xml")
    return g

def serialize_triples(graph):
    return "\n".join([
        f"<{s}> <{p}> <{o}> ." if isinstance(o, rdflib.URIRef) else f"<{s}> <{p}> \"{o}\" ."
        for s, p, o in graph
    ])

def sync_with_fuseki():
    local = load_local_graph()
    remote = load_fuseki_graph()

    to_add = local - remote
    to_remove = remote - local

    if not to_add and not to_remove:
        logging.info("✅ triple 변경 없음. 동기화 생략")
        return False

    if to_remove:
        delete_query = "DELETE DATA { " + serialize_triples(to_remove) + " }"
        res = requests.post(FUSEKI_UPDATE_URL, data=delete_query.encode("utf-8"), headers={"Content-Type": "application/sparql-update"})
        res.raise_for_status()
        logging.info(f"🗑️ 삭제된 triple 수: {len(to_remove)}")

    if to_add:
        insert_query = "INSERT DATA { " + serialize_triples(to_add) + " }"
        res = requests.post(FUSEKI_UPDATE_URL, data=insert_query.encode("utf-8"), headers={"Content-Type": "application/sparql-update"})
        res.raise_for_status()
        logging.info(f"✅ 추가된 triple 수: {len(to_add)}")

    return True