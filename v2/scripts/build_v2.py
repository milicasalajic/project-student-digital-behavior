import argparse
import csv

from pymongo import InsertOne, MongoClient
from tqdm import tqdm

from common.config import BATCH_SIZE, CSV_PATH, DB_V2, MONGO_URI, TOTAL_ROWS
from common.derived import derive
from common.schema import coerce

SUBSET_OMIT = {
    "poverty_rate_percent", "internet_infrastructure_index", "average_internet_speed_mbps",
    "ads_viewed_per_day", "ads_clicked_per_week", "impulse_purchase_score",
    "digital_spending_per_month", "financial_risk_score",
}


def build_doc(row):
    doc = {}
    for col, raw in row.items():
        if col == "student_id":
            doc["_id"] = coerce(col, raw)
        elif col in SUBSET_OMIT:
            continue
        else:
            doc[col] = coerce(col, raw)
    doc["derived"] = derive(doc)
    doc["schema_version"] = 2
    return doc


def main(drop=True):
    client = MongoClient(MONGO_URI)
    if drop:
        client.drop_database(DB_V2)
    coll = client[DB_V2]["students"]

    batch = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in tqdm(csv.DictReader(f), total=TOTAL_ROWS, unit="red", desc="v2 build"):
            batch.append(InsertOne(build_doc(row)))
            if len(batch) >= BATCH_SIZE:
                coll.bulk_write(batch, ordered=False)
                batch.clear()
    if batch:
        coll.bulk_write(batch, ordered=False)

    print(f"\n--- sbp-v2 gotovo ---\n  students: {coll.estimated_document_count():,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-drop", action="store_true")
    args = ap.parse_args()
    main(drop=not args.no_drop)
