import json
import networkx as nx
import matplotlib.pyplot as plt
from main import extract  # reuse your function from before

def clean_json(raw_text):
    # Ollama sometimes wraps JSON in markdown fences or extra text — strip that
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def build_graph(data):
    G = nx.MultiDiGraph()
    for entity in data["entities"]:
        G.add_node(entity["name"], type=entity["type"])
    for rel in data["relations"]:
        G.add_edge(rel["source"], rel["target"], type=rel["type"], quote=rel.get("evidence_quote", ""))
    return G

def draw_graph(G):
    pos = nx.spring_layout(G, seed=42, k=1.5)
    node_colors = ["skyblue" if G.nodes[n]["type"] == "person" else "lightgreen" for n in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=8, arrows=True, connectionstyle="arc3,rad=0.15")
    edge_labels = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        key = (u, v)
        edge_labels[key] = edge_labels.get(key, "") 
        edge_labels[key] = d["type"] if key not in edge_labels or edge_labels[key] == "" else edge_labels[key] + ", " + d["type"]
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    plt.savefig("graph.png", dpi=150, bbox_inches="tight")
    print("Saved graph.png")

def export_json(G):
    nodes = [{"id": n, "type": G.nodes[n]["type"]} for n in G.nodes]
    links = [{"source": u, "target": v, "type": d["type"], "quote": d.get("quote", "")} 
             for u, v, d in G.edges(data=True)]
    with open("graph_data.json", "w") as f:
        json.dump({"nodes": nodes, "links": links}, f, indent=2)
    print("Saved graph_data.json")

if __name__ == "__main__":
    sample = "Sarah Chen founded Bright Path Robotics in 2018. Her co-founder, Marcus Webb, had previously worked with her at TechCorp, where they met during a product launch in 2015."
    raw = extract(sample)
    data = clean_json(raw)
    G = build_graph(data)
    draw_graph(G)
    export_json(G)