import json

from graphing import clean_json
from main import extract
from resolve import resolve_entities
from main import extract, clean_roles
import wikipediaapi

def extract_with_retry(text, max_attempts=3):
    for attempt in range(max_attempts):
        raw = extract(text)
        try:
            data = clean_json(raw)
        except json.JSONDecodeError:
            continue  # bad JSON, try again
        if not isinstance(data.get("entities"), list) or not isinstance(data.get("relations"), list):
            continue
        # count how many relations have real quotes
        quoted = sum(1 for r in data["relations"] if isinstance(r, dict) and (r.get("evidence_quote") or "").strip())
        total = len(data["relations"])
        if total == 0 or quoted / total >= 0.6:  # 60%+ of relations have quotes = good enough
            return data
    return data  # give up after max_attempts, return last attempt anyway


def extract_all(paragraphs):
    all_data = []
    for p in paragraphs:
        data = extract_with_retry(p)
        role_map = clean_roles(data)

        data["entities"] = [e for e in data["entities"] if e["name"] not in role_map]
        for r in data["relations"]:
            r["source"] = role_map.get(r["source"], r["source"])
            r["target"] = role_map.get(r["target"], r["target"])

        print("=== RELATIONS AFTER EXTRACTION ===")
        for r in data["relations"]:
            quote = r.get("evidence_quote", "")
            print(f"  {r['source']} -> {r['target']} [{r['type']}] quote={'YES' if quote else 'NO'}")
        print(f"Total: {len(data['relations'])}, with quotes: {sum(1 for r in data['relations'] if r.get('evidence_quote'))}")
        print("===================================")

        all_data.append(data)
    return all_data

def merge_with_resolution(all_data):
    raw_nodes = {}
    raw_links = []
    mentions = {}  # canonical name -> list of {doc, quote}

    for doc_idx, data in enumerate(all_data):
        for e in data["entities"]:
            if e["name"].strip():
                raw_nodes[e["name"]] = e["type"]
        for r in data["relations"]:
            r["_doc"] = doc_idx
            raw_links.append(r)
            print("RAW NODES WITH TYPES:", raw_nodes)

    
    print("RAW NODE NAMES:", list(raw_nodes.keys()))
    alias_map = resolve_entities(raw_nodes)

    final_nodes = {}
    for name, typ in raw_nodes.items():
        canon = alias_map.get(name, name)
        final_nodes[canon] = typ

    final_links = []
    for r in raw_links:
        src = alias_map.get(r["source"], r["source"])
        tgt = alias_map.get(r["target"], r["target"])
        quote = r.get("evidence_quote", "")
        doc = r["_doc"]

        final_links.append(
            {"source": src, "target": tgt, "type": r["type"], "quote": quote}
        )

        for person in (src, tgt):
            mentions.setdefault(person, [])
            entry = {"doc": doc, "quote": quote, "relation": r["type"]}
            if entry not in mentions[person]:
                mentions[person].append(entry)

    nodes_out = []
    for name, typ in final_nodes.items():
        nodes_out.append({"id": name, "type": typ, "mentions": mentions.get(name, [])})
    final_links = [l for l in final_links if (l.get("quote") or "").strip()]
    node_ids = set(final_nodes.keys())
    final_links = [
        l for l in final_links if l["source"] in node_ids and l["target"] in node_ids
    ]
    return {"nodes": nodes_out, "links": final_links}


if __name__ == "__main__":
    wiki = wikipediaapi.Wikipedia(user_agent='epstein-docs-graph-test', language='en')
    page = wiki.page('Enron_scandal')
    text = page.text
    
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 200]
    paragraphs = paragraphs[:10]
    all_data = extract_all(paragraphs)
    merged = merge_with_resolution(all_data)
    with open("graph_data.json", "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Nodes: {len(merged['nodes'])}")
    for n in merged["nodes"]:
        print(" -", n["id"])


        