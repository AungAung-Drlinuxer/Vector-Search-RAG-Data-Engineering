# M14 — Knowledge Graph RAG (GraphRAG) with Neo4j

Traditional RAG စနစ်များသည် text ကို fixed-size chunks များအဖြစ် အပိုင်းပိုင်းခွဲ၍ vector space အတွင်း သီးခြားစီ encode လုပ်သဖြင့် documents အချင်းချင်း ဆက်စပ်နေသော entity relationships နှင့် multi-hop dependencies များကို ခြေရာခံရာတွင် အားနည်းချက် ရှိသည်။ GraphRAG (Graph-based Retrieval-Augmented Generation) သည် Knowledge Graph ၏ explicit relational structures (Nodes and Edges) နှင့် Vector Search ၏ semantic flexibility ကို ပေါင်းစပ်ပြီး high-precision retrieval ကို ပေးစွမ်းသည်။

---

## ၁။ Property Graph Model နှင့် Cypher Language Fundamentals

### Overview

Property Graph Model သည် ဒေတာများကို အောက်ပါ အစိတ်အပိုင်း ၄ ခုဖြင့် ဖွဲ့စည်းသည်:
1. **Nodes (Vertices)**: Factual entities များကို ကိုယ်စားပြုသည် (ဥပမာ `Service`, `VPC`, `SecurityGroup`, `Person`)။
2. **Labels**: Node များ၏ categorization classification (ဥပမာ `:CloudService`, `:Team`)။
3. **Relationships (Edges)**: Node များကြားရှိ directed, typed connections များ (ဥပမာ `-[:CONNECTS_TO]->`, `-[:MANAGED_BY]->`)။
4. **Properties**: Nodes နှင့် Relationships များပေါ်တွင် key-value attributes များ (ဥပမာ `{name: 'GuardDuty', port: 443, created_at: 2026}`)။

### Engineering Rationale

Relational database တွင် foreign key joins အများအပြား (multi-table JOINs) ပြုလုပ်ရခြင်းသည် query scale ကြီးမားလာပါက compute overhead မြင့်မားသည်။ Graph database (Neo4j) သည် pointer-chasing index-free adjacency ကို အသုံးပြုသဖြင့် relationship traversal latency သည် total graph size ပေါ်တွင် မမှီခိုဘဲ local subgraph degree ပေါ်တွင်သာ မူတည်သည်။

### Python Emulation

```python
# Labeled Property Graph Model implementation in pure Python.

class PropertyGraph:
    def __init__(self):
        self.nodes = {}  # node_id -> {labels: set, properties: dict}
        self.edges = []  # list of (source, rel_type, target, properties)

    def add_node(self, node_id: str, label: str, **properties):
        if node_id not in self.nodes:
            self.nodes[node_id] = {"labels": set(), "properties": {}}
        self.nodes[node_id]["labels"].add(label)
        self.nodes[node_id]["properties"].update(properties)

    def add_edge(self, source: str, rel_type: str, target: str, **properties):
        assert source in self.nodes and target in self.nodes, "Both endpoints must exist"
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
for c in cypher[:3]:
    print(c)
# Expected output:
# MERGE (n:Provider {id: 'aws', name: 'Amazon Web Services'});
# MERGE (n:Service {id: 'guardduty', tier: 'Security'});
# MERGE (n:Network {id: 'vpc_1', cidr: '10.0.0.0/16'});
```

---

## ၂။ Unstructured Text မှ Triples Extraction နှင့် Entity Resolution

### Overview

Knowledge Graph တည်ဆောက်ခြင်း (Graph Ingestion) အဆင့်တွင် unstructured text chunk များမှ Factual Triples — `(Subject, Predicate, Object)` — များကို ထုတ်ယူရသည်။ ဥပမာ:
`"GuardDuty monitors VPC traffic in AWS."`
-> `(GuardDuty, MONITORS, VPC)`
-> `(VPC, DEPLOYED_IN, AWS)`

### Entity Resolution Gate

Text များတွင် identical real-world entity တစ်ခုတည်းကို အမည်အမျိုးမျိုးဖြင့် ရေးသားလေ့ရှိသည် (ဥပမာ `"AWS"`, `"Amazon Web Services"`, `"aws-cloud"`)။ Entity Resolution မပြုလုပ်ပါက graph တွင် duplicate nodes များ ဖြစ်ပေါ်ကာ reasoning paths များ ပြတ်တောက်သွားမည် ဖြစ်သည်။

### Python Emulation

```python
# Deterministic triples extraction & entity normalization pipeline.

ALIASES = {
    "amazon web services": "AWS",
    "aws-cloud": "AWS",
    "amazon aws": "AWS",
    "vpc_network": "VPC",
    "virtual private cloud": "VPC",
}

def resolve_entity(name: str) -> str:
    cleaned = name.strip().lower()
    return ALIASES.get(cleaned, name.strip().upper())

def extract_triples(text: str) -> list[tuple[str, str, str]]:
    # Rule-based stand-in for an LLM extraction prompt
    triples = []
    if "monitors" in text.lower():
        triples.append(("GuardDuty", "MONITORS", "Virtual Private Cloud"))
    if "deployed in" in text.lower() or "inside" in text.lower():
        triples.append(("Virtual Private Cloud", "DEPLOYED_IN", "Amazon Web Services"))
    return triples

sample_text = "Security agent GuardDuty monitors network inside amazon web services."
raw_triples = extract_triples(sample_text)
resolved_triples = [(resolve_entity(s), p, resolve_entity(o)) for s, p, o in raw_triples]

print("Raw triples     :", raw_triples)
print("Resolved triples:", resolved_triples)
# Expected output:
# Raw triples     : [('GuardDuty', 'MONITORS', 'Virtual Private Cloud'), ('Virtual Private Cloud', 'DEPLOYED_IN', 'Amazon Web Services')]
# Resolved triples: [('GUARDDUTY', 'MONITORS', 'VPC'), ('VPC', 'DEPLOYED_IN', 'AWS')]
```

---

## ၃။ Multi-Hop Graph Traversal Engine (1-Hop & 2-Hop Reasoning)

### Overview

Multi-hop question answering သည် direct similarity ဖြင့် မဖြေဆိုနိုင်သော indirect relationship များကို ရှာဖွေခြင်း ဖြစ်သည်။
- *User Query*: "What team is responsible for the infrastructure monitoring our VPC?"
- *Hop 1*: `(VPC) <--[:MONITORS]-- (GuardDuty)`
- *Hop 2*: `(GuardDuty) --[:MANAGED_BY]--> (SecOps_Team)`
- *Deduction*: SecOps Team is responsible.

### Python BFS Implementation

```python
from collections import deque

def find_neighborhood(edges: list[tuple[str, str, str]], seed_node: str, max_hops: int = 2):
    # Directed & undirected graph representation
    adj = {}
    for s, r, t in edges:
        adj.setdefault(s, []).append((r, t, "outgoing"))
        adj.setdefault(t, []).append((r, s, "incoming"))

    visited = {seed_node}
    queue = deque([(seed_node, 0, [])])
    subgraph_paths = []

    while queue:
        curr, dist, path = queue.popleft()
        if dist >= max_hops:
            continue
        for rel, nxt, direction in adj.get(curr, []):
            step = f"{curr} -[{rel}]-> {nxt}" if direction == "outgoing" else f"{nxt} -[{rel}]-> {curr}"
            new_path = path + [step]
            subgraph_paths.append((dist + 1, " -> ".join(new_path)))
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, dist + 1, new_path))
    return subgraph_paths

kg_edges = [
    ("GuardDuty", "MONITORS", "VPC"),
    ("GuardDuty", "MANAGED_BY", "SecOps_Team"),
    ("VPC", "HOSTED_ON", "AWS"),
]
paths = find_neighborhood(kg_edges, seed_node="VPC", max_hops=2)
for hop, p in sorted(paths):
    print(f"Hop {hop}: {p}")
# Expected output:
# Hop 1: GuardDuty -[MONITORS]-> VPC
# Hop 1: VPC -[HOSTED_ON]-> AWS
# Hop 2: GuardDuty -[MONITORS]-> VPC -> GuardDuty -[MANAGED_BY]-> SecOps_Team
```

---

## ၄။ Dual-Lane Hybrid Retrieval (Dense Vector + Graph Triples Fusion)

### Architectural Flow

Hybrid GraphRAG retrieval pipeline သည် user query အား parallel lanes နှစ်ခုဖြင့် retrieve လုပ်သည်:
1. **Lane 1 (Dense Vector Store / pgvector)**: Query vector ဖြင့် unstructured top-K chunks များကို cosine distance ဖြင့် ဆွဲယူသည်။
2. **Lane 2 (Neo4j Graph Database)**: Query ထဲမှ entity mentions များကို extract လုပ်ပြီး 1-2 hops relational triples များကို ဆွဲယူသည်။
3. **Context Synthesis**: LLM prompt အတွင်းသို့ Vector Narrative Context နှင့် Graph Relational Triples နှစ်မျိုးလုံးကို structure ချထားပေးသည်။

```python
# Dual-lane hybrid retrieval fusion simulator

def hybrid_graph_vector_retrieve(query_text, query_vec, chunks, kg_edges, k=2):
    # Lane 1: Cosine dense retrieval
    def cosine(a, b):
        return sum(x * y for x, y in zip(a, b))
    ranked_chunks = sorted(chunks, key=lambda c: -cosine(query_vec, c["embedding"]))[:k]

    # Lane 2: Graph triples retrieval based on query keywords
    relevant_triples = []
    for s, r, o in kg_edges:
        if s.lower() in query_text.lower() or o.lower() in query_text.lower():
            relevant_triples.append(f"({s}) -[:{r}]-> ({o})")

    # Synthesis into prompt context
    context = {
        "text_passages": [c["text"] for c in ranked_chunks],
        "graph_facts": relevant_triples
    }
    return context

chunks = [
    {"text": "VPC provides isolated cloud network.", "embedding": [0.9, 0.1]},
    {"text": "Cooking pasta requires boiling water.", "embedding": [0.1, 0.9]},
]
kg = [("GuardDuty", "MONITORS", "VPC"), ("VPC", "PEERED_WITH", "VPC_Prod")]

ctx = hybrid_graph_vector_retrieve("What monitors VPC?", [0.85, 0.15], chunks, kg)
print("Passages:", ctx["text_passages"])
print("Graph Facts:", ctx["graph_facts"])
# Expected output:
# Passages: ['VPC provides isolated cloud network.', 'Cooking pasta requires boiling water.']
# Graph Facts: ['(GuardDuty) -[:MONITORS]-> (VPC)', '(VPC) -[:PEERED_WITH]-> (VPC_Prod)']
```

---

## ၅။ Text-to-Cypher vs Vector-to-Graph

### Comparison

- **Text-to-Cypher**: LLM က natural language query မှ Cypher query code (`MATCH ... WHERE ... RETURN`) ကို တိုက်ရိုက် generate လုပ်သည်။ တိကျသော aggregate queries (ဥပမာ "How many servers are in VPC-1?") များအတွက် အကောင်းဆုံးဖြစ်သော်လည်း syntax error သို့မဟုတ် hallucinated relationship types များ ဖြစ်ပေါ်နိုင်သည်။
- **Vector-to-Graph (Entity Linking)**: Query ထဲမှ entities များကို vector similarity ဖြင့် graph nodes များနှင့် map လုပ်ပြီး pre-written parameterized traversal query ဖြင့် deterministic fetch လုပ်သည်။ Production stability ပိုမိုမြင့်မားသည်။

---

## ၆။ Graph Community Detection & Global Summarization (Hierarchical GraphRAG)

### Overview

Microsoft GraphRAG architecture တွင် corpus တစ်ခုလုံးရှိ entities များကို graph clustering algorithms (ဥပမာ Leiden algorithm သို့မဟုတ် Connected Components) ဖြင့် modular communities အဖြစ် ခွဲခြားသည်။ Community တစ်ခုချင်းစီအတွက် thematic summary များကို offline pre-generate ပြုလုပ်ထားသဖြင့် macro-level global synthesis မေးခွန်းများကို လျင်မြန်စွာ ဖြေဆိုနိုင်သည်။

## Summary Checklist

- Entities (Nodes) နှင့် Explicit Connections (Edges) များကို Property Graph ဖြင့် တည်ဆောက်ပါ။
- Ingestion stage တွင် Entity Normalization / Resolution ပြုလုပ်၍ duplicate nodes များကို တားဆီးပါ။
- Multi-hop reasoning အတွက် 1-hop / 2-hop neighborhood traversal algorithms ကို အသုံးပြုပါ။
- Vector chunks နှင့် Graph triples များကို dual-lane retrieval ဖြင့် prompt context ထဲသို့ ပေါင်းစပ်ပါ။
- Natural language query မှ Cypher generate လုပ်ပါက schema whitelist validation guardrails ထည့်သွင်းပါ။
- Global thematic questions များအတွက် Graph Community Detection ဖြင့် hierarchical summarization ကို ဆောင်ရွက်ပါ။
