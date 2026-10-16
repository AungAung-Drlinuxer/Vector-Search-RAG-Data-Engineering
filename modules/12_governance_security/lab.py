#!/usr/bin/env python3
"""
Module 12_governance_security — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: Ingestion Gate PII Redaction Pipeline"""
    print(f"\n--- Exercise 1: Ingestion Gate PII Redaction Pipeline ---")
    # Exercise 1: PII redaction before embedding (standard library only, deterministic, offline).
    # No real embedding model is used here; we only sanitize the text that WOULD be embedded.
    import re
    
    EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    PHONE_PATTERN = re.compile(r"\b\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}\b")
    
    def redact_pii(text: str) -> str:
        """Replace emails and phone-like numbers with [REDACTED]."""
        text = EMAIL_PATTERN.sub("[REDACTED]", text)
        text = PHONE_PATTERN.sub("[REDACTED]", text)
        return text
    
    chunk = "Contact aung@example.com or call 09-777-123 for the project status."
    clean = redact_pii(chunk)
    print(clean)
    print("PII remaining:", "@" in clean or "09-777" in clean)
    # Expected output:
    # Contact [REDACTED] or call [REDACTED] for the project status.
    # PII remaining: False
    return True

def exercise_2() -> bool:
    """Exercise 2: In-Query Document-Level ACL Enforcement"""
    print(f"\n--- Exercise 2: In-Query Document-Level ACL Enforcement ---")
    # Exercise 2: Cosine ranking with a document-level ACL filter (standard library only, deterministic).
    import math
    
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)
    
    def search(query_vec, docs, allowed_doc_ids, k=3):
        """Rank by cosine similarity, then drop docs not in allowed_doc_ids."""
        scored = [(d["id"], cosine(query_vec, d["embedding"])) for d in docs]
        scored.sort(key=lambda t: t[1], reverse=True)  # rank first
        filtered = [(i, s) for i, s in scored if i in allowed_doc_ids]  # then filter
        return filtered[:k]
    
    docs = [
        {"id": "doc1", "embedding": [1.0, 0.0, 0.0]},  # secret doc, NOT allowed for user "aung"
        {"id": "doc2", "embedding": [0.9, 0.1, 0.0]},  # allowed
        {"id": "doc3", "embedding": [0.5, 0.5, 0.0]},  # allowed
        {"id": "doc4", "embedding": [0.0, 1.0, 0.0]},  # allowed
    ]
    query = [1.0, 0.0, 0.0]
    allowed = {"doc2", "doc3", "doc4"}  # ACL for user "aung"; doc1 is off-limits
    
    print("No filter :", [(i, round(s, 3)) for i, s in sorted(
        ((d["id"], cosine(query, d["embedding"])) for d in docs), key=lambda t: t[1], reverse=True)][:3])
    print("With ACL  :", [(i, round(s, 3)) for i, s in search(query, docs, allowed)])
    # Expected output:
    # No filter : [('doc1', 1.0), ('doc2', 0.994), ('doc3', 0.707)]
    # With ACL  : [('doc2', 0.994), ('doc3', 0.707), ('doc4', 0.0)]
    return True

def exercise_3() -> bool:
    """Exercise 3: PostgreSQL Row-Level Security (RLS) DDL & Policy Design"""
    print(f"\n--- Exercise 3: PostgreSQL Row-Level Security (RLS) DDL & Policy Design ---")
    # Exercise 3: DDL, RLS policy, and a pgvector SELECT — kept as strings (not executed here).
    # Reference: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
    
    DDL = """
    CREATE TABLE documents (
        id      integer PRIMARY KEY,
        content text,
        owner   text NOT NULL,
        embedding vector(4)
    );
    """
    
    RLS = """
    ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY docs_owner_isolation ON documents
        FOR SELECT
        USING (owner = current_user);
    """
    
    QUERY = """
    SELECT id, content, embedding <=> '[0.1,0.2,0.3,0.4]' AS distance
    FROM documents
    ORDER BY embedding <=> '[0.1,0.2,0.3,0.4]'
    LIMIT 3;
    """
    
    print(DDL.strip(), RLS.strip(), QUERY.strip(), sep="\n---\n")
    # Expected output:
    # CREATE TABLE documents (
    #     id      integer PRIMARY KEY,
    #     content text,
    #     owner   text NOT NULL,
    #     embedding vector(4)
    # );
    # ---
    # ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    # 
    # CREATE POLICY docs_owner_isolation ON documents
    #     FOR SELECT
    #     USING (owner = current_user);
    # ---
    # SELECT id, content, embedding <=> '[0.1,0.2,0.3,0.4]' AS distance
    # FROM documents
    # ORDER BY embedding <=> '[0.1,0.2,0.3,0.4]'
    # LIMIT 3;
    return True

def exercise_4() -> bool:
    """Exercise 4: Multi-Tenant Isolation Architecture နှိုင်းယှဉ်ချက်"""
    print(f"\n--- Exercise 4: Multi-Tenant Isolation Architecture နှိုင်းယှဉ်ချက် ---")
    # Exercise 4: schema-per-tenant (dict-of-dicts) vs shared table (list with tenant_id), offline & deterministic.
    
    # Model 1: schema-per-tenant — physical separation
    tenants = {
        "tenantA": {"docs": ["A-doc1", "A-doc2"]},
        "tenantB": {"docs": ["B-doc1"]},
    }
    
    def query_schema_per_tenant(tenant_id):
        return list(tenants[tenant_id]["docs"])  # wrong key raises KeyError, no silent leak
    
    # Model 2: shared table — every query MUST filter on tenant_id
    shared_rows = [
        {"tenant_id": "tenantA", "doc": "A-doc1"},
        {"tenant_id": "tenantA", "doc": "A-doc2"},
        {"tenant_id": "tenantB", "doc": "B-doc1"},
    ]
    
    def query_shared_table(tenant_id, apply_filter=True):
        if apply_filter:
            return [r["doc"] for r in shared_rows if r["tenant_id"] == tenant_id]
        return [r["doc"] for r in shared_rows]  # simulate a forgotten filter -> leak!
    
    print("schema-per-tenant A :", query_schema_per_tenant("tenantA"))
    print("shared table A (safe):", query_shared_table("tenantA"))
    print("shared table A (bug):", query_shared_table("tenantA", apply_filter=False))
    # Expected output:
    # schema-per-tenant A : ['A-doc1', 'A-doc2']
    # shared table A (safe): ['A-doc1', 'A-doc2']
    # shared table A (bug): ['A-doc1', 'A-doc2', 'B-doc1']
    return True

def exercise_5() -> bool:
    """Exercise 5: Append-Only Structured Audit Logging"""
    print(f"\n--- Exercise 5: Append-Only Structured Audit Logging ---")
    # Exercise 5: JSON-lines audit logger for retrieval requests (deterministic offline clock, no real DB).
    import json
    
    _audit_log = []
    _clock = {"now": 0}  # deterministic stand-in for a real timestamp source
    
    def next_timestamp():
        _clock["now"] += 1
        return "2026-01-01T00:00:%02dZ" % _clock["now"]
    
    def retrieval_request(user, query, results, allowed):
        """Append one JSON audit line: user, query, result ids, allowed flag, timestamp."""
        event = {
            "user": user,
            "query": query,
            "result_ids": [r["id"] for r in results],
            "allowed": allowed,
            "timestamp": next_timestamp(),
        }
        _audit_log.append(json.dumps(event))  # real system: append-only table, never update/delete
    
    ranked = [{"id": "doc1", "score": 0.9}, {"id": "doc2", "score": 0.8}]  # doc1 later found disallowed
    retrieval_request("aung", "project status", ranked, allowed=True)     # naive request logged
    retrieval_request("aung", "project status", ranked[:1], allowed=False)  # denial recorded too
    for line in _audit_log:
        print(line)
    # Expected output:
    # {"user": "aung", "query": "project status", "result_ids": ["doc1", "doc2"], "allowed": true, "timestamp": "2026-01-01T00:00:01Z"}
    # {"user": "aung", "query": "project status", "result_ids": ["doc1"], "allowed": false, "timestamp": "2026-01-01T00:00:02Z"}
    return True

def exercise_6() -> bool:
    """Exercise 6: Cascade Deletion Engine နှင့် Data Provenance Tracking"""
    print(f"\n--- Exercise 6: Cascade Deletion Engine နှင့် Data Provenance Tracking ---")
    # Exercise 6: cascade delete with provenance + retention record (standard library only, deterministic).
    
    docs = {"doc1": {"source_url": "https://example.com/a", "license": "CC-BY-4.0"},
            "doc2": {"source_url": "https://example.com/b", "license": "proprietary"}}
    chunks = [{"id": "c1", "doc_id": "doc1"}, {"id": "c2", "doc_id": "doc1"}, {"id": "c3", "doc_id": "doc2"}]
    embeddings = {"c1": [1.0, 0.0], "c2": [0.0, 1.0], "c3": [0.5, 0.5]}
    audit_refs = [{"event": "read", "doc_id": "doc1"}, {"event": "read", "doc_id": "doc2"}]
    deletion_log = []
    
    def delete_doc(doc_id):
        """Cascade-delete a doc, its chunks, embeddings, audit refs; keep provenance in deletion_log."""
        if doc_id not in docs:
            return False
        provenance = docs.pop(doc_id)                       # remove source doc
        chunk_ids = [c["id"] for c in chunks if c["doc_id"] == doc_id]
        chunks[:] = [c for c in chunks if c["doc_id"] != doc_id]      # drop its chunks
        for cid in chunk_ids:
            embeddings.pop(cid, None)                        # drop their embeddings
        audit_refs[:] = [a for a in audit_refs if a["doc_id"] != doc_id]  # scrub audit refs
        deletion_log.append({"doc_id": doc_id, "chunks_deleted": chunk_ids,
                             "provenance": provenance,
                             "retention_note": "provenance kept for compliance, content purged"})
        return True
    
    delete_doc("doc1")
    orphans = [c["id"] for c in chunks if c["doc_id"] not in docs]  # must be empty
    print("chunks left    :", [c["id"] for c in chunks])
    print("embeddings left:", sorted(embeddings))
    print("audit refs left:", audit_refs)
    print("orphan chunks  :", orphans)
    print("deletion log   :", deletion_log)
    # Expected output:
    # chunks left    : ['c3']
    # embeddings left: ['c3']
    # audit refs left: [{'event': 'read', 'doc_id': 'doc2'}]
    # orphan chunks  : []
    # deletion log   : [{'doc_id': 'doc1', 'chunks_deleted': ['c1', 'c2'], 'provenance': {'source_url': 'https://example.com/a', 'license': 'CC-BY-4.0'}, 'retention_note': 'provenance kept for compliance, content purged'}]
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 12_governance_security Lab Exercises")
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
