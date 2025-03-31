import requests
import os
from typing import List, Dict, Tuple

from dotenv import load_dotenv
load_dotenv()

# FUSEKI_ENDPOINT = "http://3.36.178.68:3030/qlinx/query"
FUSEKI_ENDPOINT = os.getenv("FUSEKI_QUERY_URL")

def run_sparql_query(query: str) -> List[Dict]:
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.post(FUSEKI_ENDPOINT, data={"query": query}, headers=headers)
    response.raise_for_status()
    return response.json()["results"]["bindings"]

def get_classes() -> List[Dict]:
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?class ?label ?comment
    WHERE {
      ?class a owl:Class .
      OPTIONAL { ?class rdfs:label ?label }
      OPTIONAL { ?class rdfs:comment ?comment }
    }
    """
    results = run_sparql_query(query)
    return [
        {
            "uri": r.get("class", {}).get("value"),
            "label": r.get("label", {}).get("value"),
            "comment": r.get("comment", {}).get("value"),
        }
        for r in results
    ]

def get_object_properties() -> List[Dict]:
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?property ?domain ?range
    WHERE {
      ?property a owl:ObjectProperty .
      OPTIONAL { ?property rdfs:domain ?domain }
      OPTIONAL { ?property rdfs:range ?range }
    }
    """
    results = run_sparql_query(query)
    return [
        {
            "uri": r.get("property", {}).get("value"),
            "domain": r.get("domain", {}).get("value"),
            "range": r.get("range", {}).get("value"),
        }
        for r in results
    ]

def get_data_properties() -> List[Dict]:
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?property ?domain ?range
    WHERE {
      ?property a owl:DatatypeProperty .
      OPTIONAL { ?property rdfs:domain ?domain }
      OPTIONAL { ?property rdfs:range ?range }
    }
    """
    results = run_sparql_query(query)
    return [
        {
            "uri": r.get("property", {}).get("value"),
            "domain": r.get("domain", {}).get("value"),
            "range": r.get("range", {}).get("value"),
        }
        for r in results
    ]

def get_individuals_with_literals_and_relations() -> List[Dict]:
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?individual ?type ?prop ?value ?valueType
    WHERE {
      ?individual a ?type .
      FILTER(?type != owl:Class && ?type != owl:ObjectProperty && ?type != owl:DatatypeProperty)
      OPTIONAL {
        ?individual ?prop ?value .
        BIND(DATATYPE(?value) AS ?valueType)
      }
    }
    """
    results = run_sparql_query(query)
    individuals = {}
    for r in results:
        uri = r.get("individual", {}).get("value")
        if not uri:
            continue
        if uri not in individuals:
            individuals[uri] = {
                "uri": uri,
                "type": r.get("type", {}).get("value"),
                "literals": [],
                "relations": []
            }
        prop = r.get("prop", {}).get("value")
        value = r.get("value", {}).get("value")
        if not prop or not value:
            continue
        if "valueType" in r and r["valueType"].get("value"):  # literal
            individuals[uri]["literals"].append({
                "prop": prop,
                "value": value
            })
        else:  # object property (relation)
            individuals[uri]["relations"].append({
                "prop": prop,
                "target": value
            })
    return list(individuals.values())

def get_swrl_rules() -> List[Dict]:
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX swrl: <http://www.w3.org/2003/11/swrl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX swrla: <http://swrl.stanford.edu/ontologies/3.3/swrla.owl#>

    SELECT ?rule ?label ?comment ?body ?head ?isEnabled
    WHERE {
      ?rule rdf:type swrl:Imp .
      OPTIONAL { ?rule rdfs:label ?label }
      OPTIONAL { ?rule rdfs:comment ?comment }
      OPTIONAL { ?rule swrla:isRuleEnabled ?isEnabled }
      OPTIONAL { ?rule swrl:body ?body }
      OPTIONAL { ?rule swrl:head ?head }
    }
    """
    results = run_sparql_query(query)
    return [
        {
            "uri": r.get("rule", {}).get("value"),
            "label": r.get("label", {}),
            "comment": r.get("comment", {}),
            "body": r.get("body", {}).get("value"),
            "head": r.get("head", {}).get("value"),
            "isEnabled": r.get("isEnabled", {}).get("value"),
        }
        for r in results
    ]

def get_triples_for_individual(individual_uri: str) -> List[Tuple[str, str, str]]:
    query = f"""
    SELECT ?p ?o
    WHERE {{
      <{individual_uri}> ?p ?o .
    }}
    """
    results = run_sparql_query(query)
    
    triples = []
    for r in results:
        p = r.get("p", {}).get("value")
        o = r.get("o", {}).get("value")
        if p and o:
            triples.append((individual_uri, p, o))
    return triples


def get_all_ontology_elements():
    return {
        "classes": get_classes(),
        "object_props": get_object_properties(),
        "data_props": get_data_properties(),
        "individuals": get_individuals_with_literals_and_relations(),
        "rules": get_swrl_rules()
    }