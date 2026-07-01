from pymongo import MongoClient

from common.config import DB_V2, MONGO_URI

INDEXES = [
    [("derived.age_group", 1)],
    [("derived.dominant_content_type", 1), ("brain_rot_index", -1)],
    [("derived.social_gt6", 1)],
    [("brain_rot_level", 1), ("cyberbullying_exposure", 1)],
    [("digital_addiction_score", 1), ("wellbeing_index", 1), ("social_media_hours", 1)],
    [("derived.social_media_band", 1)],
    [("derived.addiction_high_risk", 1), ("gender", 1), ("urban_rural", 1)],
    [("academic_risk_score", 1)],
    [("derived.session_exceeds_attention", 1), ("derived.digital_burnout_level", 1)],
    [("development_level", 1), ("family_income_level", 1)],
    [("derived.has_academic_risk", 1)],
]


def main():
    coll = MongoClient(MONGO_URI)[DB_V2]["students"]
    for keys in INDEXES:
        name = coll.create_index(keys)
        print(f"  + {name}")
    print(f"\nUkupno indeksa (sa _id): {len(coll.index_information())}")


if __name__ == "__main__":
    main()
