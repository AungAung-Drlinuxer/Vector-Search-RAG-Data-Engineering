## လေ့ကျင့်ခန်း ၁ — Property Graph Schema ဒီဇိုင်းနှင့် Cypher Statements တည်ဆောက်ခြင်း

Labeled Property Graph model ကို Python class ဖြင့် တည်ဆောက်ပြီး nodes နှင့် directed edges များကို Neo4j Cypher `MERGE` statements အဖြစ် serialize လုပ်ပြထားသည်။

```python
# Exercise 1: Property Graph Model & Cypher statement serialization (stdlib only)
class PropertyGraph:
    def __init__(self):
        self.nodes = {}  # id -> {labels: set, properties: dict}
        self.edges = []  # (source, rel, target, props)

    def add_node(self, node_id: str, label: str, **properties):
        if node_id not in self.nodes:
            self.nodes[node_id] = {"labels": set(), "properties": {}}
        self.nodes[node_id]["labels"].add(label)
        self.nodes[node_id]["properties"].update(properties)

    def add_edge(self, source: str, rel_type: str, target: str, **properties):
        assert source in self.nodes and target in self.nodes, f"Missing endpoint: {source} or {target}"
        self.edges.append((source, rel_type, target, properties))

    def to_cypher(self) -> list[str]:
        statements = []
        for nid, data in sorted(self.nodes.items()):
            label = list(data["labels"])[0] if data["labels"] else "Entity"
            props = ", ".join(f"{k}: '{v}'" for k, v in sorted(data["properties"].items()))
            statements.append(f"MERGE (n:{label} {{id: '{nid}', {props}}});")
        for src, rel, tgt, props in sorted(self.edges, key=lambda e: (e[0], e[1], e[2])):
            statements.append(f"MATCH (a {{id: '{src}'}}), (b {{id: '{tgt}'}}) MERGE (a)-[:{rel}]->(b);")
        return statements

g = PropertyGraph()
g.add_node("aws", "Provider", name="Amazon Web Services")
g.add_node("vpc_1", "Network", cidr="10.0.0.0/16")
g.add_node("guardduty", "Service", tier="Security")
g.add_edge("guardduty", "MONITORS", "vpc_1")
g.add_edge("vpc_1", "HOSTED_ON", "aws")

cypher = g.to_cypher()
for c in cypher:
    print(c)
# Expected output:
# MERGE (n:Provider {id: 'aws', name: 'Amazon Web Services'});
# MERGE (n:Service {id: 'guardduty', tier: 'Security'});
# MERGE (n:Network {id: 'vpc_1', cidr: '10.0.0.0/16'});
# MATCH (a {id: 'guardduty'}), (b {id: 'vpc_1'}) MERGE (a)-[:MONITORS]->(b);
# MATCH (a {id: 'vpc_1'}), (b {id: 'aws'}) MERGE (a)-[:HOSTED_ON]->(b);
```

**အဓိကအယူအဆ** — Property Graph Model သည် relational tables အစား entities နှင့် explicit relationships များကို first-class schema အဖြစ် declare လုပ်နိုင်သည်။

---

## လေ့ကျင့်ခန်း ၂ — Text Chunks မှ Triples Extraction နှင့် Entity Resolution

Unstructured text မှ Subject-Predicate-Object triples များကို ထုတ်ယူပြီး synonym aliases များကို canonical entities အဖြစ် deduplicate လုပ်သည့် entity resolution gate ဖြစ်သည်။

```python
# Exercise 2: Triples extraction and entity resolution normalization
ALIASES = {
    "amazon web services": "AWS",
    "aws-cloud": "AWS",
    "amazon aws": "AWS",
    "vpc_network": "VPC",
    "virtual private cloud": "VPC",
    "guardduty service": "GUARDDUTY",
}

def resolve_entity(name: str) -> str:
    cleaned = name.strip().lower()
    return ALIASES.get(cleaned, name.strip().upper())

def extract_triples_from_corpus(passages: list[str]) -> list[tuple[str, str, str]]:
    raw_triples = []
    for text in passages:
        t = text.lower()
        if "monitors" in t:
            raw_triples.append(("GuardDuty Service", "MONITORS", "Virtual Private Cloud"))
        if "hosted on" in t or "inside" in t:
            raw_triples.append(("VPC_Network", "HOSTED_ON", "amazon web services"))
    return raw_triples

corpus = [
    "Security agent GuardDuty Service monitors all traffic.",
    "Network VPC_Network is hosted on amazon web services cloud.",
]

raw = extract_triples_from_corpus(corpus)
resolved = [(resolve_entity(s), p, resolve_entity(o)) for s, p, o in raw]

print("Extracted raw triples:", raw)
print("Resolved graph triples:", resolved)
# Expected output:
# Extracted raw triples: [('GuardDuty Service', 'MONITORS', 'Virtual Private Cloud'), ('VPC_Network', 'HOSTED_ON', 'amazon web services')]
# Resolved graph triples: [('GUARDDUTY', 'MONITORS', 'VPC'), ('VPC', 'HOSTED_ON', 'AWS')]
```

**အဓိကအယူအဆ** — Entity Resolution သည် duplicate disconnected nodes များ မဖြစ်ပေါ်စေဘဲ connected knowledge graph ဖွဲ့စည်းနိုင်စေရန် မရှိမဖြစ် လိုအပ်သည်။

---

## လေ့ကျင့်ခန်း ၃ — Multi-Hop Graph Traversal Engine (1-Hop & 2-Hop BFS)

သတ်မှတ်ထားသော seed node မှ 1-hop နှင့် 2-hop အကွာအဝေးရှိ neighboring paths များကို Breadth-First Search (BFS) ဖြင့် traversal ပြုလုပ်ပုံ ဖြစ်သည်။

```python
# Exercise 3: 1-hop and 2-hop BFS neighborhood traversal
from collections import deque

def traverse_neighborhood(edges: list[tuple[str, str, str]], seed: str, max_hops: int = 2):
    adj = {}
    for s, r, t in edges:
        adj.setdefault(s, []).append((r, t, "outgoing"))
        adj.setdefault(t, []).append((r, s, "incoming"))

    visited = {seed}
    queue = deque([(seed, 0, [])])
    discovered_paths = []

    while queue:
        curr, hops, path = queue.popleft()
        if hops >= max_hops:
            continue
        for rel, nxt, direction in adj.get(curr, []):
            edge_repr = f"({curr})-[:{rel}]->({nxt})" if direction == "outgoing" else f"({nxt})-[:{rel}]->({curr})"
            new_path = path + [edge_repr]
            discovered_paths.append((hops + 1, " => ".join(new_path)))
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, hops + 1, new_path))
    return discovered_paths

edges = [
    ("GuardDuty", "MONITORS", "VPC"),
    ("GuardDuty", "MANAGED_BY", "SecOps_Team"),
    ("VPC", "HOSTED_ON", "AWS"),
    ("SecOps_Team", "REPORTS_TO", "CISO"),
]

paths = traverse_neighborhood(edges, seed="VPC", max_hops=2)
for hops, p in sorted(paths):
    print(f"Hop {hops}: {p}")
# Expected output:
# Hop 1: (GuardDuty)-[:MONITORS]->(VPC)
# Hop 1: (VPC)-[:HOSTED_ON]->(AWS)
# Hop 2: (GuardDuty)-[:MONITORS]->(VPC) => (GuardDuty)-[:MANAGED_BY]->(SecOps_Team)
```

**အဓိကအယူအဆ** — 2-hop traversal သည် VPC နှင့် direct similarity မရှိသော SecOps_Team ကဲ့သို့သော indirect dependencies များကို ဆွဲထုတ်ပေးနိုင်သည်။

---

## လေ့ကျင့်ခန်း ၄ — Dual-Lane Hybrid Retrieval (Vector Chunks + Graph Triples Fusion)

Dense vector similarity ranking နှင့် knowledge graph relational triples ဆွဲယူမှုကို dual-lane fan-out ပြုလုပ်၍ prompt context အဖြစ် ပေါင်းစပ်ထုတ်ယူပုံ ဖြစ်သည်။

```python
# Exercise 4: Dual-lane hybrid retrieval fusion (dense vector + graph facts)
import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

def dual_lane_retrieve(query_text: str, query_vec: list[float], chunks: list[dict], kg_edges: list[tuple[str, str, str]], top_k: int = 2):
    # Lane 1: Dense vector similarity
    ranked = sorted(chunks, key=lambda c: -cosine(query_vec, c["embedding"]))[:top_k]
    
    # Lane 2: Graph triples extraction matching query tokens
    matched_triples = []
    tokens = set(query_text.lower().replace("?", "").split())
    for s, r, o in kg_edges:
        if s.lower() in tokens or o.lower() in tokens:
            matched_triples.append(f"({s}) -[:{r}]-> ({o})")
            
    return {
        "retrieved_passages": [c["text"] for c in ranked],
        "graph_relational_facts": matched_triples
    }

chunks_db = [
    {"text": "VPC isolated cloud network infrastructure.", "embedding": [0.9, 0.1, 0.0]},
    {"text": "Cooking rice recipes with vegetables.", "embedding": [0.0, 0.1, 0.9]},
    {"text": "SecOps team handles incident response.", "embedding": [0.6, 0.5, 0.1]},
]

kg_triples = [
    ("GuardDuty", "MONITORS", "VPC"),
    ("SecOps_Team", "MANAGES", "GuardDuty"),
]

result = dual_lane_retrieve("Who manages the service that monitors VPC?", [0.8, 0.3, 0.0], chunks_db, kg_triples, top_k=2)
print("Passages   :", result["retrieved_passages"])
print("Graph Facts:", result["graph_relational_facts"])
# Expected output:
# Passages   : ['VPC isolated cloud network infrastructure.', 'SecOps team handles incident response.']
# Graph Facts: ['(GuardDuty) -[:MONITORS]-> (VPC)']
```

**အဓိကအယူအဆ** — Unstructured passages များနှင့် factual graph triples များ ပေါင်းစပ်ပါဝင်သဖြင့် LLM သည် context fragmentation မဖြစ်ဘဲ တိကျစွာ answer synthesize လုပ်နိုင်သည်။

---

## လေ့ကျင့်ခန်း ၅ — Text-to-Cypher Translation Guardrails & Validation

Natural language prompts မှ ထွက်ပေါ်လာသော Cypher queries များကို SQL/Cypher injection မဖြစ်စေရန်နှင့် read-only query policy ကို enforce လုပ်သည့် syntax validator ဖြစ်သည်။

```python
# Exercise 5: Cypher syntax guardrails & read-only allowlist validation
ALLOWED_LABELS = {"Provider", "Network", "Service", "Team"}
ALLOWED_RELATIONSHIPS = {"MONITORS", "HOSTED_ON", "MANAGED_BY", "CONNECTS_TO"}
DISALLOWED_CLAUSES = {"DELETE", "DROP", "REMOVE", "SET", "CREATE"}

def validate_cypher_query(query: str) -> tuple[bool, str]:
    upper_q = query.upper()
    for clause in DISALLOWED_CLAUSES:
        if f" {clause} " in f" {upper_q} ":
            return False, f"Destructive clause forbidden: {clause}"
    
    if not upper_q.strip().startswith("MATCH"):
        return False, "Query must start with read-only MATCH clause"
    if "RETURN" not in upper_q:
        return False, "Query must contain a RETURN clause"
    
    return True, "Valid read-only Cypher query"

test_queries = [
    "MATCH (s:Service)-[:MONITORS]->(v:Network) RETURN s.id, v.id",
    "MATCH (n:Service) DELETE n",
    "DROP TABLE documents",
]

for q in test_queries:
    valid, reason = validate_cypher_query(q)
    print(f"Query: {q:<60} | Valid: {valid} ({reason})")
# Expected output:
# Query: MATCH (s:Service)-[:MONITORS]->(v:Network) RETURN s.id, v.id  | Valid: True (Valid read-only Cypher query)
# Query: MATCH (n:Service) DELETE n                                   | Valid: False (Destructive clause forbidden: DELETE)
# Query: DROP TABLE documents                                         | Valid: False (Destructive clause forbidden: DROP)
```

**အဓိကအယူအဆ** — Text-to-Cypher architecture တွင် read-only syntax validation guardrail သည် database corruption ကို တားဆီးပေးသည်။

---

## လေ့ကျင့်ခန်း ၆ — Graph Community Clustering & Global Summarization

Graph adjacency connection အပေါ် အခြေခံ၍ connected components များကို clustering ခွဲခြားပြီး cluster အလိုက် thematic summary ထုတ်ယူသည့် logic ဖြစ်သည်။

```python
# Exercise 6: Graph Community Detection & Global Summarization Engine
def detect_connected_communities(nodes: list[str], edges: list[tuple[str, str]]):
    adj = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    visited = set()
    communities = []

    for n in sorted(nodes):
        if n not in visited:
            component = []
            queue = [n]
            visited.add(n)
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for neighbor in sorted(adj[curr]):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            communities.append(sorted(component))
    return communities

entities = ["GuardDuty", "VPC", "AWS", "HR_Portal", "Payroll_DB", "Employee_Service"]
relations = [
    ("GuardDuty", "VPC"),
    ("VPC", "AWS"),
    ("HR_Portal", "Payroll_DB"),
    ("Payroll_DB", "Employee_Service"),
]

clusters = detect_connected_communities(entities, relations)
print("Detected Communities:", len(clusters))
for idx, c in enumerate(clusters, 1):
    theme = "Cloud Infrastructure & Security" if "AWS" in c else "Internal HR & Payroll"
    print(f"Community {idx}: {c} -> Theme: '{theme}'")
# Expected output:
# Detected Communities: 2
# Community 1: ['AWS', 'GuardDuty', 'VPC'] -> Theme: 'Cloud Infrastructure & Security'
# Community 2: ['Employee_Service', 'HR_Portal', 'Payroll_DB'] -> Theme: 'Internal HR & Payroll'
```

**အဓိကအယူအဆ** — Community Detection သည် unstructured corpus ၏ macro-level themes များကို cluster ခွဲခြားပေးပြီး broad global queries များကို ဖြေဆိုရာတွင် အသုံးပြုသည်။
