"""Upiti — akademski savetnik (AA-1 .. AA-5).

Svaki builder vraća (collection, pipeline). v1 kreće iz normalizovane child
kolekcije i koristi $lookup; v2 čita jednu kolekciju `students` u sbp-v2.
"""
from queries._expr import (
    social_band_expr, burnout_expr, dominant_content_expr, is_late_night_expr,
    lookup_unwind,
)

# Procenat grupe u odnosu na ukupan broj (zajednički završni deo za AA-1).
_PCT_OF_TOTAL = [
    {"$setWindowFields": {"sortBy": {"_id": 1}, "output": {
        "ukupno": {"$sum": "$broj_studenata", "window": {"documents": ["unbounded", "unbounded"]}}}}},
    {"$addFields": {"procenat": {"$multiply": [{"$divide": ["$broj_studenata", "$ukupno"]}, 100]}}},
    {"$sort": {"_id": 1}},
]


def q1(version):
    """1. Po dnevnim satima na mrežama (<2h, 2-4h, 4-6h, >6h): broj, procenat,
    prosečan skor produktivnosti, prosečno sati učenja, prosečan akademski rizik."""
    if version == "v1":
        pipeline = [
            *lookup_unwind("academic", "a"),
            {"$addFields": {"band": social_band_expr()}},
            {"$group": {
                "_id": "$band",
                "broj_studenata": {"$sum": 1},
                "prosek_produktivnost": {"$avg": "$a.productivity_score"},
                "prosek_sati_ucenja": {"$avg": "$a.study_hours_per_week"},
                "prosek_akademski_rizik": {"$avg": "$a.academic_risk_score"},
            }},
            *_PCT_OF_TOTAL,
        ]
        return "digital_behavior", pipeline

    pipeline = [
        {"$group": {
            "_id": "$derived.social_media_band",
            "broj_studenata": {"$sum": 1},
            "prosek_produktivnost": {"$avg": "$productivity_score"},
            "prosek_sati_ucenja": {"$avg": "$study_hours_per_week"},
            "prosek_akademski_rizik": {"$avg": "$academic_risk_score"},
        }},
        *_PCT_OF_TOTAL,
    ]
    return "students", pipeline


def q2(version):
    """2. Procenat visokorizičnih (digital_addiction_score >= 25) po polu i tipu
    područja + njihov prosečan nivo stresa."""
    add_fields = {
        "procenat_visokorizicnih": {"$multiply": [{"$divide": ["$visokorizicni", "$ukupno"]}, 100]},
        "prosek_stres_visokorizicni": {"$cond": [
            {"$gt": ["$visokorizicni", 0]},
            {"$divide": ["$suma_stres_hr", "$visokorizicni"]},
            None,
        ]},
    }
    if version == "v1":
        pipeline = [
            *lookup_unwind("students", "s"),
            {"$addFields": {"high_risk": {"$gte": ["$digital_addiction_score", 25]}}},
            {"$group": {
                "_id": {"pol": "$s.gender", "podrucje": "$s.urban_rural"},
                "ukupno": {"$sum": 1},
                "visokorizicni": {"$sum": {"$cond": ["$high_risk", 1, 0]}},
                "suma_stres_hr": {"$sum": {"$cond": ["$high_risk", "$stress_level", 0]}},
            }},
            {"$addFields": add_fields},
            {"$project": {"suma_stres_hr": 0}},
            {"$sort": {"procenat_visokorizicnih": -1}},
        ]
        return "wellbeing", pipeline

    pipeline = [
        {"$group": {
            "_id": {"pol": "$gender", "podrucje": "$urban_rural"},
            "ukupno": {"$sum": 1},
            "visokorizicni": {"$sum": {"$cond": ["$derived.addiction_high_risk", 1, 0]}},
            "suma_stres_hr": {"$sum": {"$cond": ["$derived.addiction_high_risk", "$stress_level", 0]}},
        }},
        {"$addFields": add_fields},
        {"$project": {"suma_stres_hr": 0}},
        {"$sort": {"procenat_visokorizicnih": -1}},
    ]
    return "students", pipeline


def q3(version):
    """3. Studenti sa akademskim rizikom IZNAD proseka: broj + prosečno sati
    učenja, skor produktivnosti, sati na mrežama. Prosek se računa u pipeline-u
    preko $setWindowFields (prozor nad celim skupom) umesto $facet — $facet bi
    materijalizovao svih 500k dokumenata u jedan niz i prešao limit od 16/100 MB."""
    win = {"$setWindowFields": {"sortBy": {"_id": 1}, "output": {
        "m": {"$avg": "$academic_risk_score", "window": {"documents": ["unbounded", "unbounded"]}}}}}
    over_avg = {"$match": {"$expr": {"$gt": ["$academic_risk_score", "$m"]}}}

    if version == "v1":
        pipeline = [
            {"$project": {"academic_risk_score": 1, "study_hours_per_week": 1, "productivity_score": 1}},
            win,
            over_avg,
            {"$lookup": {"from": "digital_behavior", "localField": "_id",
                         "foreignField": "_id", "as": "d"}},
            {"$unwind": "$d"},
            {"$group": {
                "_id": None,
                "broj_studenata": {"$sum": 1},
                "prosek_sati_ucenja": {"$avg": "$study_hours_per_week"},
                "prosek_produktivnost": {"$avg": "$productivity_score"},
                "prosek_sati_mreze": {"$avg": "$d.social_media_hours"},
            }},
        ]
        return "academic", pipeline

    pipeline = [
        {"$project": {"academic_risk_score": 1, "study_hours_per_week": 1,
                      "productivity_score": 1, "social_media_hours": 1}},
        win,
        over_avg,
        {"$group": {
            "_id": None,
            "broj_studenata": {"$sum": 1},
            "prosek_sati_ucenja": {"$avg": "$study_hours_per_week"},
            "prosek_produktivnost": {"$avg": "$productivity_score"},
            "prosek_sati_mreze": {"$avg": "$social_media_hours"},
        }},
    ]
    return "students", pipeline


def q4(version):
    """4. Studenti kod kojih je prosečno trajanje sesije > trajanja koncentracije,
    grupisani po nivou digitalnog sagorevanja (iz brain_rot_index): broj, broj sa
    akademskim rizikom != 0, broj koji koriste mreže kasno noću, broj sa dominantnim
    kratkim video sadržajem."""
    if version == "v1":
        pipeline = [
            *lookup_unwind("academic", "a"),
            {"$match": {"$expr": {"$gt": ["$average_session_length_minutes",
                                          "$a.attention_span_minutes"]}}},
            {"$addFields": {
                "burnout": burnout_expr(),
                "dominant": dominant_content_expr(),
                "is_late": is_late_night_expr(),
            }},
            {"$group": {
                "_id": "$burnout",
                "broj_studenata": {"$sum": 1},
                "broj_sa_rizikom": {"$sum": {"$cond": [{"$ne": ["$a.academic_risk_score", 0]}, 1, 0]}},
                "broj_kasno_nocu": {"$sum": {"$cond": ["$is_late", 1, 0]}},
                "broj_kratki_video": {"$sum": {"$cond": [{"$eq": ["$dominant", "short_video"]}, 1, 0]}},
            }},
            {"$sort": {"_id": 1}},
        ]
        return "digital_behavior", pipeline

    pipeline = [
        {"$match": {"derived.session_exceeds_attention": True}},
        {"$group": {
            "_id": "$derived.digital_burnout_level",
            "broj_studenata": {"$sum": 1},
            "broj_sa_rizikom": {"$sum": {"$cond": ["$derived.has_academic_risk", 1, 0]}},
            "broj_kasno_nocu": {"$sum": {"$cond": ["$derived.is_late_night", 1, 0]}},
            "broj_kratki_video": {"$sum": {"$cond": ["$derived.is_short_video_dominant", 1, 0]}},
        }},
        {"$sort": {"_id": 1}},
    ]
    return "students", pipeline


def q5(version):
    """5. Po kombinaciji (nivo razvijenosti države x nivo prihoda porodice): broj,
    procenat sa akademskim rizikom (>0), prosečan stres, prosečan akademski rizik,
    prosečno prisustvo nastavi, prosečna akademska motivacija; sort opadajuće po % rizika."""
    add_pct = {"$addFields": {"procenat_sa_rizikom": {
        "$multiply": [{"$divide": ["$broj_sa_rizikom", "$broj_studenata"]}, 100]}}}
    sort = {"$sort": {"procenat_sa_rizikom": -1}}

    if version == "v1":
        pipeline = [
            {"$lookup": {"from": "countries", "localField": "country",
                         "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            *lookup_unwind("academic", "a"),
            *lookup_unwind("wellbeing", "w"),
            {"$group": {
                "_id": {"razvoj": "$c.development_level", "prihod": "$family_income_level"},
                "broj_studenata": {"$sum": 1},
                "broj_sa_rizikom": {"$sum": {"$cond": [{"$gt": ["$a.academic_risk_score", 0]}, 1, 0]}},
                "prosek_stres": {"$avg": "$w.stress_level"},
                "prosek_akademski_rizik": {"$avg": "$a.academic_risk_score"},
                "prosek_prisustvo": {"$avg": "$a.class_attendance_rate"},
                "prosek_motivacija": {"$avg": "$a.academic_motivation"},
            }},
            add_pct,
            sort,
        ]
        return "students", pipeline

    pipeline = [
        {"$group": {
            "_id": {"razvoj": "$development_level", "prihod": "$family_income_level"},
            "broj_studenata": {"$sum": 1},
            "broj_sa_rizikom": {"$sum": {"$cond": ["$derived.has_academic_risk", 1, 0]}},
            "prosek_stres": {"$avg": "$stress_level"},
            "prosek_akademski_rizik": {"$avg": "$academic_risk_score"},
            "prosek_prisustvo": {"$avg": "$class_attendance_rate"},
            "prosek_motivacija": {"$avg": "$academic_motivation"},
        }},
        add_pct,
        sort,
    ]
    return "students", pipeline


SAVETNIK = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}
