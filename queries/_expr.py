"""Deljeni aggregation izrazi za v1 upite (gde se izvedene vrednosti računaju u letu).

U v2 ove vrednosti su već prekomputovane u poddokumentu `derived`, pa se ovi izrazi
koriste samo u v1 varijantama — što i pokazuje cenu računanja po dokumentu.
Pragovi su identični onima u `common/derived.py`.
"""


def field(name, prefix=""):
    """'$x' ili '$prefix.x' za polja iz $lookup-ovanih (unwind) poddokumenata."""
    return f"${prefix}.{name}" if prefix else f"${name}"


def age_group_expr(prefix=""):
    a = field("age", prefix)
    return {"$switch": {"branches": [
        {"case": {"$lte": [a, 17]}, "then": "15-17"},
        {"case": {"$lte": [a, 20]}, "then": "18-20"},
        {"case": {"$lte": [a, 23]}, "then": "21-23"},
    ], "default": "24-25"}}


def social_band_expr(prefix=""):
    h = field("social_media_hours", prefix)
    return {"$switch": {"branches": [
        {"case": {"$lt": [h, 2]}, "then": "<2h"},
        {"case": {"$lt": [h, 4]}, "then": "2-4h"},
        {"case": {"$lte": [h, 6]}, "then": "4-6h"},
    ], "default": ">6h"}}


def burnout_expr(prefix=""):
    b = field("brain_rot_index", prefix)
    return {"$switch": {"branches": [
        {"case": {"$lt": [b, 12.57]}, "then": "Nizak"},
        {"case": {"$lt": [b, 25.09]}, "then": "Umeren"},
        {"case": {"$lt": [b, 34.77]}, "then": "Visok"},
    ], "default": "Težak"}}


def dominant_content_expr(prefix=""):
    edu = field("education_content_hours", prefix)
    sv = field("short_video_hours", prefix)
    ent = field("entertainment_content_hours", prefix)
    news = field("news_content_hours", prefix)
    return {"$let": {"vars": {"m": {"$max": [edu, sv, ent, news]}}, "in": {"$switch": {"branches": [
        {"case": {"$eq": [edu, "$$m"]}, "then": "educational"},
        {"case": {"$eq": [sv, "$$m"]}, "then": "short_video"},
        {"case": {"$eq": [ent, "$$m"]}, "then": "entertainment"},
    ], "default": "informative"}}}}


def is_late_night_expr(prefix=""):
    return {"$in": [field("late_night_usage", prefix), ["Often", "Always"]]}


def lookup_unwind(from_coll, as_name, local="_id", foreign="_id"):
    """Standardni left-join na _id + $unwind (1:1 veza ka child kolekciji)."""
    return [
        {"$lookup": {"from": from_coll, "localField": local,
                     "foreignField": foreign, "as": as_name}},
        {"$unwind": f"${as_name}"},
    ]
