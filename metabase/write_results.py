#!/usr/bin/env python3
"""Materijalizuje rezultate svih 10 upita u rezultat-kolekcije u `sbp-v2`.

Metabase tada grafikuje sitne `results_*` kolekcije trivijalno (umesto da pokreće
složene agregacije pri svakom učitavanju dashboard-a).

Kolekcije: results_psi_q1..q5, results_sav_q1..q5  (svaka prepisana preko $out)

Pokretanje:  python -m metabase.write_results
"""
from pymongo import MongoClient

from common.config import DB_V2, MONGO_URI
from queries import SUITES

PREFIX = {"psiholog": "psi", "savetnik": "sav"}


def main():
    db = MongoClient(MONGO_URI)[DB_V2]
    for author, suite in SUITES.items():
        for qid, builder in suite.items():
            coll, pipeline = builder("v2")
            out = f"results_{PREFIX[author]}_{qid}"
            db[coll].aggregate(pipeline + [{"$out": out}], allowDiskUse=True)
            print(f"  {out:20s}: {db[out].count_documents({})} redova")
    print("\nGotovo. U Metabase-u: Admin -> Databases -> sbp-v2 -> Sync schema now.")


if __name__ == "__main__":
    main()
