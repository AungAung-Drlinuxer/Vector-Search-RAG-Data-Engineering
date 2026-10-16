#!/usr/bin/env python3
"""
Module 14: Knowledge Graph RAG (GraphRAG) with Neo4j — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

from collections import deque
import math
import sys

def exercise_1() -> bool:
    """Exercise 1: Property Graph Model & Cypher statement serialization"""
    print("\n--- Exercise 1: Property Graph Model & Cypher serialization ---")
    class PropertyGraph:
        def __init__(self):
            self.nodes = {}
            self.edges = []

        def add_node(self, node_id: str, label: str, **properties):
            if node_id not in self.nodes:
                self.nodes[node_id] = {"labels": set(), "properties": {}}
            self.nodes[node_id]["labels"].add(label)
            self.nodes[node_id]["properties"].update(properties)

        def add_edge(self, source: str, rel_type: str, target: str, **properties):
            assert source in self.nodes and target in self.nodes
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

    assert len(g.nodes) == 3
    assert len(g.edges) == 2
    assert any("Provider" in s for s in cypher)
    assert any("MONITORS" in s for s in cypher)
    return True

def exercise_2() -> bool:
    """Exercise 2: Triples extraction and entity resolution normalization"""
    print("\n--- Exercise 2: Triples extraction and entity resolution ---")
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

    assert resolved == [('GUARDDUTY', 'MONITORS', 'VPC'), ('VPC', 'HOSTED_ON', 'AWS')]
    return True

def exercise_3() -> bool:
    """Exercise 3: 1-hop and 2-hop BFS neighborhood traversal"""
    print("\n--- Exercise 3: Multi-hop BFS neighborhood traversal ---")
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

    assert any(h == 1 for h, _ in paths)
    assert any(h == 2 and "SecOps_Team" in p for h, p in paths)
    return True

def exercise_4() -> bool:
    """Exercise 4: Dual-lane hybrid retrieval fusion (dense vector + graph facts)"""
    print("\n--- Exercise 4: Dual-lane hybrid retrieval fusion ---")
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    def dual_lane_retrieve(query_text: str, query_vec: list[float], chunks: list[dict], kg_edges: list[tuple[str, str, str]], top_k: int = 2):
        ranked = sorted(chunks, key=lambda c: -cosine(query_vec, c["embedding"]))[:top_k]
        
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

    assert len(result["retrieved_passages"]) == 2
    assert "(GuardDuty) -[:MONITORS]-> (VPC)" in result["graph_relational_facts"]
    return True

def exercise_5() -> bool:
    """Exercise 5: Cypher syntax guardrails & read-only allowlist validation"""
    print("\n--- Exercise 5: Cypher syntax guardrails & allowlist ---")
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
        ("MATCH (s:Service)-[:MONITORS]->(v:Network) RETURN s.id, v.id", True),
        ("MATCH (n:Service) DELETE n", False),
        ("DROP TABLE documents", False),
    ]

    for q, expected_valid in test_queries:
        valid, reason = validate_cypher_query(q)
        print(f"Query: {q:<60} | Valid: {valid} ({reason})")
        assert valid == expected_valid

    return True

def exercise_6() -> bool:
    """Exercise 6: Graph Community Detection & Global Summarization Engine"""
    print("\n--- Exercise 6: Graph Community Detection ---")
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

    assert len(clusters) == 2
    assert "AWS" in clusters[0] and "GuardDuty" in clusters[0]
    assert "HR_Portal" in clusters[1] and "Payroll_DB" in clusters[1]
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 14 (GraphRAG with Neo4j) Lab Exercises")
    print("=" * 60)
    tests = [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5, exercise_6]
    passed = 0
    for t in tests:
        try:
            if t():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            return False
    print(f"\n[PASS] All {passed}/{len(tests)} exercises passed successfully.")
    return True

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
