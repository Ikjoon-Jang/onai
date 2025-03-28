# fuseki_insert.py

import rdflib
import requests
import logging
import os

# FUSEKI_UPDATE_URL = "http://3.36.178.68:3030/qlinx/update"
# FUSEKI_QUERY_URL = "http://3.36.178.68:3030/qlinx/query"
# RDF_FILE = "./data/rdf.xml"
FUSEKI_UPDATE_URL = os.getenv("FUSEKI_UPDATE_URL")
FUSEKI_QUERY_URL = os.getenv("FUSEKI_QUERY_URL")
RDF_FILE = os.getenv("RDF_FILE")

logging.basicConfig(level=logging.INFO)

def load_local_graph(path=RDF_FILE):
    g = rdflib.Graph()
    g.parse(path, format="xml")
    return g

def load_fuseki_graph():
    g = rdflib.Graph()
    query = """
    CONSTRUCT { ?s ?p ?o }
    WHERE { ?s ?p ?o }
    """
    headers = {"Accept": "application/rdf+xml"}
    response = requests.post(FUSEKI_QUERY_URL, data={"query": query}, headers=headers)
    response.raise_for_status()
    g.parse(data=response.text, format="xml")
    return g

def insert_new_triples(new_graph, old_graph):
    diff = new_graph - old_graph
    if len(diff) == 0:
        logging.info("✅ 변경된 트리플이 없습니다. 삽입 생략.")
        return

    insert_data = "\n".join([
        f"<{s}> <{p}> <{o}> ." if isinstance(o, rdflib.URIRef) else f"<{s}> <{p}> \"{o}\" ."
        for s, p, o in diff
    ])
    sparql = f"INSERT DATA {{ {insert_data} }}"

    headers = {"Content-Type": "application/sparql-update"}
    res = requests.post(FUSEKI_UPDATE_URL, data=sparql.encode("utf-8"), headers=headers)
    res.raise_for_status()
    logging.info(f"✅ 새로운 {len(diff)}개의 트리플을 Fuseki에 삽입했습니다.")

def update_fuseki_from_rdf():
    local_graph = load_local_graph()
    remote_graph = load_fuseki_graph()
    insert_new_triples(local_graph, remote_graph)

if __name__ == "__main__":
    update_fuseki_from_rdf()


def insert_triple_to_fuseki(graph):
    """
    rdflib.Graph 형태의 triple들을 Fuseki 서버로 업로드합니다.
    """
    try:
        triples = "\n".join([
            f"{s.n3()} {p.n3()} {o.n3()} ." for s, p, o in graph
        ])

        sparql_update = f"INSERT DATA {{ {triples} }}"

        headers = {'Content-Type': 'application/sparql-update'}
        response = requests.post(
            FUSEKI_UPDATE_URL,
            data=sparql_update.encode('utf-8'),
            headers=headers
        )

        if response.status_code in [200, 204]:
            logging.info("✅ Fuseki에 triple 업로드 성공")
            return True
        else:
            logging.error(f"❌ Fuseki 업로드 실패: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ Fuseki 업로드 중 예외 발생: {e}")
        return False