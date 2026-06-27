"""Upiti — studentski psiholog (PSY-1 .. PSY-5).

Svaki builder vraća (collection, pipeline). v1 kreće iz normalizovane child
kolekcije i koristi $lookup; v2 čita jednu kolekciju `students` u sbp-v2.
"""
from queries._expr import (
    age_group_expr, dominant_content_expr, is_late_night_expr, lookup_unwind,
)


def q1(version):
    """1. Po starosnim grupama (15-17,18-20,21-23,24-25): broj + prosečna
    depresivnost, anksioznost, stres, akademski rizik."""
    if version == "v1":
        pipeline = [
            *lookup_unwind("wellbeing", "w"),
            *lookup_unwind("academic", "a"),
            {"$addFields": {"age_group": age_group_expr()}},
            {"$group": {
                "_id": "$age_group",
                "broj_studenata": {"$sum": 1},
                "prosek_depresija": {"$avg": "$w.depression_score"},
                "prosek_anksioznost": {"$avg": "$w.anxiety_score"},
                "prosek_stres": {"$avg": "$w.stress_level"},
                "prosek_akademski_rizik": {"$avg": "$a.academic_risk_score"},
            }},
            {"$sort": {"_id": 1}},
        ]
        return "students", pipeline

    pipeline = [
        {"$group": {
            "_id": "$derived.age_group",
            "broj_studenata": {"$sum": 1},
            "prosek_depresija": {"$avg": "$depression_score"},
            "prosek_anksioznost": {"$avg": "$anxiety_score"},
            "prosek_stres": {"$avg": "$stress_level"},
            "prosek_akademski_rizik": {"$avg": "$academic_risk_score"},
        }},
        {"$sort": {"_id": 1}},
    ]
    return "students", pipeline


def q2(version):
    """2. Po dominantnom tipu sadržaja: broj + prosečan brain rot indeks;
    sortirano opadajuće po brain rot indeksu."""
    if version == "v1":
        pipeline = [
            {"$addFields": {"dominant_content_type": dominant_content_expr()}},
            {"$group": {
                "_id": "$dominant_content_type",
                "broj_studenata": {"$sum": 1},
                "prosek_brain_rot": {"$avg": "$brain_rot_index"},
            }},
            {"$sort": {"prosek_brain_rot": -1}},
        ]
        return "digital_behavior", pipeline

    pipeline = [
        {"$group": {
            "_id": "$derived.dominant_content_type",
            "broj_studenata": {"$sum": 1},
            "prosek_brain_rot": {"$avg": "$brain_rot_index"},
        }},
        {"$sort": {"prosek_brain_rot": -1}},
    ]
    return "students", pipeline


def q3(version):
    """3. Studenti sa >6h društvenih mreža dnevno: broj + prosečan san,
    raspon pažnje, skor produktivnosti."""
    if version == "v1":
        pipeline = [
            {"$match": {"social_media_hours": {"$gt": 6}}},
            *lookup_unwind("wellbeing", "w"),
            *lookup_unwind("academic", "a"),
            {"$group": {
                "_id": None,
                "broj_studenata": {"$sum": 1},
                "prosek_san": {"$avg": "$w.sleep_hours"},
                "prosek_paznja": {"$avg": "$a.attention_span_minutes"},
                "prosek_produktivnost": {"$avg": "$a.productivity_score"},
            }},
        ]
        return "digital_behavior", pipeline

    pipeline = [
        {"$match": {"derived.social_gt6": True}},
        {"$group": {
            "_id": None,
            "broj_studenata": {"$sum": 1},
            "prosek_san": {"$avg": "$sleep_hours"},
            "prosek_paznja": {"$avg": "$attention_span_minutes"},
            "prosek_produktivnost": {"$avg": "$productivity_score"},
        }},
    ]
    return "students", pipeline


def q4(version):
    """4. Po izloženosti sajber nasilju (Da/Ne): broj + prosečan wellbeing,
    depresivnost, anksioznost, stres; sortirano rastuće po wellbeing-u."""
    group = {
        "_id": "$cyberbullying_exposure",
        "broj_studenata": {"$sum": 1},
        "prosek_wellbeing": {"$avg": "$wellbeing_index"},
        "prosek_depresija": {"$avg": "$depression_score"},
        "prosek_anksioznost": {"$avg": "$anxiety_score"},
        "prosek_stres": {"$avg": "$stress_level"},
    }
    pipeline = [
        {"$group": group},
        {"$sort": {"prosek_wellbeing": 1}},
    ]
    # cyberbullying_exposure i sve mere su u kolekciji wellbeing (v1) / students (v2)
    return ("wellbeing" if version == "v1" else "students"), pipeline


def q5(version):
    """5. Visok skor digitalne zavisnosti (>18.04) I nizak indeks blagostanja
    (<50.06) I umereno korišćenje mreža (<=4.20h): broj + koliko ima dominantan
    kratki video + koliko koristi mreže kasno noću."""
    if version == "v1":
        pipeline = [
            {"$match": {"digital_addiction_score": {"$gt": 18.04},
                        "wellbeing_index": {"$lt": 50.06}}},
            *lookup_unwind("digital_behavior", "d"),
            {"$match": {"d.social_media_hours": {"$lte": 4.20}}},
            {"$addFields": {
                "dominant": dominant_content_expr("d"),
                "is_late": is_late_night_expr("d"),
            }},
            {"$group": {
                "_id": None,
                "broj_studenata": {"$sum": 1},
                "broj_kratki_video": {"$sum": {"$cond": [{"$eq": ["$dominant", "short_video"]}, 1, 0]}},
                "broj_kasno_nocu": {"$sum": {"$cond": ["$is_late", 1, 0]}},
            }},
        ]
        return "wellbeing", pipeline

    pipeline = [
        {"$match": {"digital_addiction_score": {"$gt": 18.04},
                    "wellbeing_index": {"$lt": 50.06},
                    "social_media_hours": {"$lte": 4.20}}},
        {"$group": {
            "_id": None,
            "broj_studenata": {"$sum": 1},
            "broj_kratki_video": {"$sum": {"$cond": ["$derived.is_short_video_dominant", 1, 0]}},
            "broj_kasno_nocu": {"$sum": {"$cond": ["$derived.is_late_night", 1, 0]}},
        }},
    ]
    return "students", pipeline


PSIHOLOG = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}
