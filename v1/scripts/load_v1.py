#!/usr/bin/env python3
"""Unos CSV-a u INICIJALNU normalizovanu šemu `sbp-v1` (6 kolekcija).

Streaming preko csv.DictReader (konstantna memorija nad 319 MB), batch unos
preko bulk_write(InsertOne, ordered=False). Bez sekundarnih indeksa — v1 je
namerno "netjunovan" baseline za merenje uskih grla.

Pokretanje:  python -m v1.scripts.load_v1   [--no-drop]
"""
import argparse
import csv

from pymongo import InsertOne, MongoClient
from tqdm import tqdm

from common.config import BATCH_SIZE, CSV_PATH, DB_V1, MONGO_URI, TOTAL_ROWS
from common.schema import COUNTRY_DIM_COLS, V1_COLLECTIONS, coerce


def main(drop=True):
    client = MongoClient(MONGO_URI)
    if drop:
        client.drop_database(DB_V1)
    db = client[DB_V1]

    countries = {}  # country -> dim dokument (dedupe u memoriji, ~50)
    batches = {name: [] for name in V1_COLLECTIONS}

    def flush(name):
        if batches[name]:
            db[name].bulk_write(batches[name], ordered=False)
            batches[name].clear()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, total=TOTAL_ROWS, unit="red", desc="v1 unos"):
            sid = coerce("student_id", row["student_id"])
            country = (row.get("country") or "").strip() or None
            if country and country not in countries:
                countries[country] = {c: coerce(c, row.get(c)) for c in COUNTRY_DIM_COLS}
            for name, cols in V1_COLLECTIONS.items():
                doc = {"_id": sid}
                for c in cols:
                    doc[c] = coerce(c, row.get(c))
                batches[name].append(InsertOne(doc))
                if len(batches[name]) >= BATCH_SIZE:
                    flush(name)

    for name in V1_COLLECTIONS:
        flush(name)

    if countries:
        db["countries"].insert_many(
            [{"_id": n, **dim} for n, dim in countries.items()], ordered=False)

    print("\n--- sbp-v1 gotovo ---")
    for name in ["students", *(c for c in V1_COLLECTIONS if c != "students"), "countries"]:
        print(f"  {name:18s}: {db[name].estimated_document_count():,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-drop", action="store_true", help="ne briši bazu pre unosa")
    args = ap.parse_args()
    main(drop=not args.no_drop)
