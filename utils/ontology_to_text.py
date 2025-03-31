from urllib.parse import urlparse
from typing import Optional, Dict, List, Tuple

def extract_local_name(uri: Optional[object]) -> str:
    if not uri:
        return "(unknown)"
    if isinstance(uri, dict):
        uri = uri.get("value", "")
    if not isinstance(uri, str):
        return "(unknown)"
    parsed = urlparse(uri)
    return parsed.fragment if parsed.fragment else uri.split("/")[-1]

def class_to_text(cls_uri, label: Optional[Dict] = None, comment: Optional[Dict] = None) -> str:
    name = label.get("value") if label and "value" in label else extract_local_name(cls_uri)
    if comment and "value" in comment:
        return f"{name}: {comment['value']}"
    else:
        return f"{name} is a concept in the ontology."

def object_property_to_text(prop_uri, domain, range_) -> str:
    prop = extract_local_name(prop_uri)
    dom = extract_local_name(domain)
    rng = extract_local_name(range_)
    return f"'{prop}' is a relationship from {dom} to {rng}."

def data_property_to_text(prop_uri, domain, range_) -> str:
    prop = extract_local_name(prop_uri)
    dom = extract_local_name(domain)
    rng = extract_local_name(range_)
    return f"'{prop}' is a data property of {dom} and has value type {rng}."

def individual_to_text(ind_uri, type_uri, literals: Optional[List[Dict]] = None, relations: Optional[List[Dict]] = None) -> str:
    name = extract_local_name(ind_uri)
    type_name = extract_local_name(type_uri)
    text = f"{name} is an individual of type {type_name}."
    
    if literals:
        literal_text = "; ".join([f"{extract_local_name(l['prop'])} = {l['value']}" for l in literals])
        text += f" It has literal values: {literal_text}."

    if relations:
        relation_text = "; ".join([f"{extract_local_name(r['prop'])} → {extract_local_name(r['target'])}" for r in relations])
        text += f" It is connected to: {relation_text}."
    
    return text

def swrl_rule_to_text(rule: Dict) -> str:
    label = rule.get("label", {}).get("value")
    comment = rule.get("comment", {}).get("value")
    if label and comment:
        return f"Rule {label}: {comment}"
    elif comment:
        return f"A rule: {comment}"
    elif label:
        return f"Rule {label} with no description."
    else:
        return "Unnamed rule in the ontology."

def ontology_elements_to_sentences(classes, object_props, data_props, individuals, rules):
    sentences = []

    for cls in classes:
        sentences.append(class_to_text(cls.get("uri"), cls.get("label"), cls.get("comment")))

    for prop in object_props:
        sentences.append(object_property_to_text(prop.get("uri"), prop.get("domain"), prop.get("range")))

    for prop in data_props:
        sentences.append(data_property_to_text(prop.get("uri"), prop.get("domain"), prop.get("range")))

    for ind in individuals:
        sentences.append(individual_to_text(ind.get("uri"), ind.get("type"), ind.get("literals"), ind.get("relations")))

    for rule in rules:
        sentences.append(swrl_rule_to_text(rule))

    return sentences


def triples_to_sentences(individuals: list[dict]) -> list[str]:
    sentences = []

    for ind in individuals:
        subject = ind["uri"]
        subject_label = subject.split("#")[-1]

        # 🔹 타입 기반 서술
        type_label = ind.get("type", "").split("#")[-1]
        if type_label:
            sentences.append(f"{subject_label}는 {type_label} 타입입니다.")

        # 🔹 literals (데이터 속성)
        for lit in ind.get("literals", []):
            prop = lit["prop"].split("#")[-1]
            value = lit["value"]
            sentences.append(f"{subject_label}의 {prop}는 {value}입니다.")

        # 🔹 relations (object properties)
        for rel in ind.get("relations", []):
            prop = rel["prop"].split("#")[-1]
            target = rel["target"].split("#")[-1]
            sentences.append(f"{subject_label}는 {target}와(과) {prop} 관계를 가집니다.")

    return sentences

def extract_label(uri: str) -> str:
    """URI에서 마지막 localName 추출"""
    if "#" in uri:
        return uri.split("#")[-1]
    elif "/" in uri:
        return uri.split("/")[-1]
    return uri

def triples_to_natural_text(triples: List[Tuple[str, str, str]]) -> List[str]:
    sentences = []
    for s, p, o in triples:
        subj = extract_label(s)
        pred = extract_label(p)
        obj = extract_label(o)

        # 간단한 자연어 전환 규칙
        if pred.lower() in ["type", "rdf:type"]:
            sentences.append(f"{subj}는 {obj}의 유형입니다.")
        elif pred.lower() in ["hasname", "name", "label"]:
            sentences.append(f"{subj}의 이름은 {obj}입니다.")
        elif pred.lower() in ["status", "hasstatus"]:
            sentences.append(f"{subj}의 상태는 {obj}입니다.")
        elif pred.lower().startswith("has"):
            pred_natural = pred[3:].lower()
            sentences.append(f"{subj}는 {obj}라는 {pred_natural}를 가집니다.")
        else:
            sentences.append(f"{subj}는 {pred}가 {obj}입니다.")

    return sentences

def ontology_elements_to_sentences_parallel(classes, object_props, data_props, individuals, rules):
    """한글 + 영문 병렬 문장 리스트 반환"""
    def to_kor(text):
        # 간단한 병렬 번역 템플릿 예시
        if "is a concept" in text:
            return text.replace("is a concept in the ontology.", "는 온톨로지 개념입니다.")
        if "is an individual of type" in text:
            return text.replace("is an individual of type", "는 타입의 개체입니다.")
        if "It has literal values:" in text:
            text = text.replace("It has literal values:", "리터럴 속성:")
        if "It is connected to:" in text:
            text = text.replace("It is connected to:", "연결된 속성:")
        return text  # 그대로 반환해도 됨

    results = []
    for s in ontology_elements_to_sentences(classes, object_props, data_props, individuals, rules):
        kor = to_kor(s)
        results.append(f"{s} / {kor}")
    return results
