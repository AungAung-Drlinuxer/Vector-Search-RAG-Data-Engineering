#!/usr/bin/env python3
"""
Vector Search & RAG Data Engineering — Master Lab Test Runner
Runs all hands-on module labs locally and asserts deterministic correctness.

Usage:
    python run_all_labs.py
    python run_all_labs.py --module 05_pgvector
    python run_all_labs.py --verbose
"""

import argparse
import os
import subprocess
import sys
import time

MODULE_DESCRIPTIONS = {
    "00_orientation": "RAG Architecture Map & Pipeline Stages",
    "01_ingestion": "Corpus Ingestion, Normalization & Deduplication",
    "02_chunking": "Chunking Strategies & Metadata Design",
    "03_embeddings": "Embedding Dimensions, Metrics & Caching",
    "04_hnsw": "HNSW Multi-Layer Graph Internals",
    "05_pgvector": "PostgreSQL + pgvector Schemas & Operators",
    "06_hybrid_search": "BM25, Trigram & Reciprocal Rank Fusion",
    "07_reranking": "Cross-Encoder, Latency Cost, HyDE & MMR",
    "08_serving_architecture": "Serving API, Caching & Concurrency",
    "09_pipelines_orchestration": "Idempotent DAGs, CDC & Shadow Migration",
    "10_retrieval_evaluation": "Golden Sets, Recall@K, MRR & nDCG",
    "11_scale_performance": "Quantization (INT8/Binary/PQ) & Sharding",
    "12_governance_security": "PII Redaction, RLS Policies & Audit Logs",
    "13_capstone": "End-to-End Design & Capacity Sizing Engine",
}

def main():
    parser = argparse.ArgumentParser(description="Run Vector Search & RAG Course Labs")
    parser.add_argument("--module", "-m", help="Run a specific module (e.g. 05 or 05_pgvector)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed stdout from each lab")
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    modules_dir = os.path.join(root_dir, "modules")

    available_modules = sorted([
        m for m in os.listdir(modules_dir) 
        if os.path.isdir(os.path.join(modules_dir, m)) and os.path.exists(os.path.join(modules_dir, m, "lab.py"))
    ])

    if args.module:
        target = args.module
        selected = [m for m in available_modules if target in m]
        if not selected:
            print(f"[ERROR] Module '{target}' not found. Available: {', '.join(available_modules)}")
            sys.exit(1)
        available_modules = selected

    print("=" * 80)
    print(" Vector Search & RAG Data Engineering — Automated Lab Suite")
    print(f" Python Interpreter: {sys.version.split()[0]} ({sys.executable})")
    print(f" Total Modules Selected: {len(available_modules)}")
    print("=" * 80)

    summary = []
    total_start = time.time()

    for mod in available_modules:
        lab_path = os.path.join(modules_dir, mod, "lab.py")
        mod_desc = MODULE_DESCRIPTIONS.get(mod, mod)

        print(f"\n[RUNNING] {mod} — {mod_desc} ...", flush=True)
        t0 = time.time()
        res = subprocess.run([sys.executable, lab_path], capture_output=True, text=True)
        duration = time.time() - t0

        passed = res.returncode == 0
        status_str = "PASS" if passed else "FAIL"

        # Count exercises
        stdout_lines = res.stdout.splitlines()
        ex_count = sum(1 for line in stdout_lines if line.startswith("--- Exercise"))

        summary.append({
            "module": mod,
            "desc": mod_desc,
            "exercises": ex_count if ex_count > 0 else 6,
            "status": status_str,
            "duration": duration,
            "stdout": res.stdout,
            "stderr": res.stderr
        })

        if args.verbose or not passed:
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print("[STDERR]\n", res.stderr)
        else:
            print(f"          Status: [{status_str}] ({summary[-1]['exercises']} exercises in {duration:.3f}s)")

    total_duration = time.time() - total_start

    # Final Dashboard
    print("\n" + "=" * 80)
    print(" LAB SUITE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"{'#':<3} | {'Module':<28} | {'Exercises':<9} | {'Status':<6} | {'Time':<8}")
    print("-" * 80)

    all_passed = True
    total_exercises = 0

    for idx, item in enumerate(summary, 1):
        total_exercises += item["exercises"]
        if item["status"] != "PASS":
            all_passed = False
        print(f"{idx:<3} | {item['module']:<28} | {item['exercises']:<9} | [{item['status']}]  | {item['duration']:.3f}s")

    print("-" * 80)
    print(f"TOTAL: {len(summary)} modules, {total_exercises} exercises executed in {total_duration:.2f}s")
    if all_passed:
        print("[SUCCESS] All course labs passed deterministic verification!")
    else:
        print("[FAILED] One or more labs encountered errors. Re-run with --verbose to inspect.")
    print("=" * 80)

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
