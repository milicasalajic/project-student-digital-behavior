#!/usr/bin/env python3
"""Merenje performansi svih 10 upita nad v1 i v2.

Za svaki (upit x verzija) beleži:
  - wall-clock vreme (median i min od N ponavljanja, uz 1 warm-up)
  - server vreme (executionTimeMillis iz explain executionStats)
  - broj pregledanih dokumenata / ključeva (totalDocsExamined / totalKeysExamined,
    rekurzivno sabrano kroz sve faze jer $lookup ima ugnježdene pod-explain-e)
  - broj vraćenih grupa (n_returned)

Rezultat -> benchmarks/results.csv

Pokretanje:  python -m benchmarks.benchmark   [--repeats N]
"""
import argparse
import csv
import statistics
import time

from pymongo import MongoClient

from common.config import DB_V1, DB_V2, MONGO_URI, ROOT
from queries import SUITES

DEFAULT_REPEATS = 5


def walk_stats(obj, acc):
    """Rekurzivno kroz explain stablo: sabira docs/keys, skuplja sva vremena."""
    if isinstance(obj, dict):
        if "totalDocsExamined" in obj:
            acc["docs"] += obj.get("totalDocsExamined") or 0
        if "totalKeysExamined" in obj:
            acc["keys"] += obj.get("totalKeysExamined") or 0
        if "executionTimeMillis" in obj:
            acc["times"].append(obj["executionTimeMillis"])
        for v in obj.values():
            walk_stats(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            walk_stats(v, acc)
    return acc


def explain_stats(db, coll, pipeline):
    ex = db.command({
        "explain": {"aggregate": coll, "pipeline": pipeline, "cursor": {}, "allowDiskUse": True},
        "verbosity": "executionStats",
    })
    acc = walk_stats(ex, {"docs": 0, "keys": 0, "times": []})
    return {
        "server_time_ms": max(acc["times"]) if acc["times"] else None,
        "docs_examined": acc["docs"],
        "keys_examined": acc["keys"],
    }


def run_query(db, coll, pipeline, repeats):
    list(db[coll].aggregate(pipeline, allowDiskUse=True))  # warm-up (odbacuje se)
    walls, nret = [], 0
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = list(db[coll].aggregate(pipeline, allowDiskUse=True))
        walls.append((time.perf_counter() - t0) * 1000)
        nret = len(res)
    st = explain_stats(db, coll, pipeline)
    return {
        "wall_ms_median": round(statistics.median(walls), 2),
        "wall_ms_min": round(min(walls), 2),
        "server_time_ms": st["server_time_ms"],
        "docs_examined": st["docs_examined"],
        "keys_examined": st["keys_examined"],
        "n_returned": nret,
    }


def main(repeats=DEFAULT_REPEATS):
    client = MongoClient(MONGO_URI)
    dbs = {"v1": client[DB_V1], "v2": client[DB_V2]}
    rows = []
    for author, suite in SUITES.items():
        for qid, builder in suite.items():
            for ver, db in dbs.items():
                coll, pipeline = builder(ver)
                m = run_query(db, coll, pipeline, repeats)
                rows.append({"query_id": qid, "author": author, "version": ver, **m})
                print(f"{author:8s}/{qid} {ver}: wall={m['wall_ms_median']:>9.1f}ms  "
                      f"server={str(m['server_time_ms']):>6}ms  docs={m['docs_examined']:>10,}  "
                      f"keys={m['keys_examined']:>10,}  n={m['n_returned']}")

    out = ROOT / "benchmarks" / "results.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "query_id", "author", "version", "wall_ms_median", "wall_ms_min",
            "server_time_ms", "docs_examined", "keys_examined", "n_returned"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nSačuvano: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    args = ap.parse_args()
    main(repeats=args.repeats)
