#!/usr/bin/env python3
"""Provera ispravnosti: rezultat svakog upita mora biti isti u v1 i v2.

Poredi (uz zaokruživanje float-ova) rezultate iste agregacije nad normalizovanom
i denormalizovanom šemom. Ovo je glavna verifikacija da prerada upita za v2 nije
promenila semantiku.

Pokretanje:  python -m tools.check_consistency
"""
import json

from pymongo import MongoClient

from common.config import DB_V1, DB_V2, MONGO_URI
from queries import SUITES

ROUND = 4


def norm(doc):
    """Stabilna, uporediva reprezentacija dokumenta (float-ovi zaokruženi)."""
    def r(v):
        if isinstance(v, float):
            return round(v, ROUND)
        if isinstance(v, dict):
            return {k: r(x) for k, x in sorted(v.items())}
        if isinstance(v, list):
            return [r(x) for x in v]
        return v
    return r(doc)


def key(doc):
    return json.dumps(norm(doc.get("_id")), sort_keys=True, ensure_ascii=False, default=str)


def run(db, builder, ver):
    coll, pipe = builder(ver)
    res = list(db[coll].aggregate(pipe, allowDiskUse=True))
    return sorted((norm(d) for d in res), key=lambda d: key(d))


def main():
    c = MongoClient(MONGO_URI)
    db1, db2 = c[DB_V1], c[DB_V2]
    ok = True
    for author, suite in SUITES.items():
        for qid, builder in suite.items():
            r1, r2 = run(db1, builder, "v1"), run(db2, builder, "v2")
            same = (r1 == r2)
            ok = ok and same
            mark = "OK " if same else "RAZLIKA"
            n = r1[0].get("broj_studenata") if (len(r1) == 1 and "broj_studenata" in r1[0]) else len(r1)
            print(f"  [{mark}] {author}/{qid}: v1={len(r1)} grupa, v2={len(r2)} grupa "
                  f"(rezultat: {n})")
            if not same:
                print("    v1:", json.dumps(r1, ensure_ascii=False, default=str)[:400])
                print("    v2:", json.dumps(r2, ensure_ascii=False, default=str)[:400])
    print("\nSVE ISPRAVNO" if ok else "\nIMA RAZLIKA — proveriti gore")


if __name__ == "__main__":
    main()
