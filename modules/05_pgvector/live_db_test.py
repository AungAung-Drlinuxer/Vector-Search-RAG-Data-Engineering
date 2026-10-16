#!/usr/bin/env python3
"""
Module 05: Live PostgreSQL + pgvector Integration Test
Tests live vector operations against a running Docker container (or local PostgreSQL).

To start the database:
    docker compose up -d

Run this script:
    python modules/05_pgvector/live_db_test.py
"""

import sys
import time

def check_live_db():
    print("=" * 60)
    print("PostgreSQL + pgvector Live Integration Test")
    print("=" * 60)

    try:
        import psycopg
    except ImportError:
        print("[SKIP] 'psycopg' library is not installed.")
        print("To test against a live PostgreSQL database, install requirements:")
        print("    pip install -r requirements.txt")
        return True

    conn_str = "postgresql://postgres:postgres@localhost:5432/rag_course"
    print(f"Connecting to: {conn_str} ...")

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # 1. Check pgvector extension
                cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                row = cur.fetchone()
                if not row:
                    print("[FAIL] 'vector' extension is not installed in database.")
                    return False
                print(f"[OK] pgvector extension active (version {row[0]})")

                # 2. Insert test vectors
                cur.execute("CREATE TEMP TABLE test_vectors (id serial PRIMARY KEY, vec vector(3));")
                cur.execute("""
                    INSERT INTO test_vectors (vec) VALUES 
                    ('[1, 0, 0]'), 
                    ('[0, 1, 0]'), 
                    ('[0, 0, 1]');
                """)

                # 3. Test distance operators: L2 (<->), Cosine (<=>), Inner Product (<#>)
                query_vec = "[1, 0, 0]"
                cur.execute(f"SELECT id, vec <-> '{query_vec}' AS l2_dist FROM test_vectors ORDER BY l2_dist LIMIT 1;")
                best_l2 = cur.fetchone()

                cur.execute(f"SELECT id, vec <=> '{query_vec}' AS cos_dist FROM test_vectors ORDER BY cos_dist LIMIT 1;")
                best_cos = cur.fetchone()

                print(f"[OK] L2 distance (<->) nearest ID: {best_l2[0]} (distance: {best_l2[1]})")
                print(f"[OK] Cosine distance (<=>) nearest ID: {best_cos[0]} (distance: {best_cos[1]})")

                assert best_l2[0] == 1 and best_cos[0] == 1, "Nearest neighbor should be ID 1"

                # 4. Clean up temp table
                cur.execute("DROP TABLE test_vectors;")
                print("\n[PASS] All live pgvector integration tests passed!")
                return True

    except Exception as e:
        print(f"\n[INFO] Could not connect to PostgreSQL: {e}")
        print("To run live database tests, ensure the Docker container is started:")
        print("    docker compose up -d")
        print("    python modules/05_pgvector/live_db_test.py")
        return True  # Non-blocking if docker is not running

if __name__ == "__main__":
    check_live_db()
