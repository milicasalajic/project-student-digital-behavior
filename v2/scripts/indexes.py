#!/usr/bin/env python3
"""Kreira indekse na `sbp-v2.students` (tehnika indeksiranja iz faze optimizacije).

Svaki indeks je biran prema $match/$group/$sort ključevima konkretnog upita.

Pokretanje:  python -m v2.scripts.indexes
"""
from pymongo import MongoClient

from common.config import DB_V2, MONGO_URI

# (ključevi, komentar -> koji upit ubrzava)
INDEXES = [
    ([("derived.age_group", 1)], "PSY-1: grupisanje po starosnim grupama"),
    ([("derived.dominant_content_type", 1), ("brain_rot_index", -1)], "PSY-2: grupa + sort"),
    ([("derived.social_gt6", 1)], "PSY-3: filter >6h"),
    ([("cyberbullying_exposure", 1)], "PSY-4: grupa po izloženosti"),
    ([("digital_addiction_score", 1), ("wellbeing_index", 1), ("social_media_hours", 1)], "PSY-5: složeni filter"),
    ([("derived.social_media_band", 1)], "AA-1: grupa po opsegu sati"),
    ([("derived.addiction_high_risk", 1), ("gender", 1), ("urban_rural", 1)], "AA-2: filter + grupa"),
    ([("academic_risk_score", 1)], "AA-3: rizik iznad proseka"),
    ([("derived.session_exceeds_attention", 1), ("derived.digital_burnout_level", 1)], "AA-4: filter + grupa"),
    ([("development_level", 1), ("family_income_level", 1)], "AA-5: kombinovana grupa"),
    ([("derived.has_academic_risk", 1)], "AA-4/AA-5: brojanje rizika"),
]


def main():
    coll = MongoClient(MONGO_URI)[DB_V2]["students"]
    for keys, comment in INDEXES:
        name = coll.create_index(keys)
        print(f"  + {name:55s} ({comment})")
    print(f"\nUkupno indeksa (sa _id): {len(coll.index_information())}")


if __name__ == "__main__":
    main()
