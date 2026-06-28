"""Computed pattern: izvedena polja koja se računaju JEDNOM pri unosu u v2.
"""


CONTENT_FIELDS = [
    ("education_content_hours", "educational"),
    ("short_video_hours", "short_video"),
    ("entertainment_content_hours", "entertainment"),
    ("news_content_hours", "informative"),
]


def age_group(age):
    if age is None:
        return None
    if age <= 17:
        return "15-17"
    if age <= 20:
        return "18-20"
    if age <= 23:
        return "21-23"
    return "24-25"


def social_media_band(h):
    if h is None:
        return None
    if h < 2:
        return "<2h"
    if h < 4:
        return "2-4h"
    if h <= 6:
        return "4-6h"
    return ">6h"


def dominant_content_type(doc):
    """Argmax od 4 *_content_hours; tie-break po prioritetu (edu > short_video > ...)."""
    best_label, best_val = None, None
    for field, label in CONTENT_FIELDS:
        v = doc.get(field) or 0.0
        if best_val is None or v > best_val:  # strict > čuva raniji (prioritetniji) na izjednačenju
            best_val, best_label = v, label
    return best_label


def digital_burnout_level(brain_rot_index):
    """Nivo digitalnog sagorevanja iz brain_rot_index, percentili p25/p75/p95."""
    if brain_rot_index is None:
        return None
    if brain_rot_index < 12.57:
        return "Nizak"
    if brain_rot_index < 25.09:
        return "Umeren"
    if brain_rot_index < 34.77:
        return "Visok"
    return "Težak"


def derive(doc):
    """Vraća poddokument `derived` sa svim Computed poljima za jedan (tipizovan) red."""
    dom = dominant_content_type(doc)
    session = doc.get("average_session_length_minutes")
    attention = doc.get("attention_span_minutes")
    addiction = doc.get("digital_addiction_score")
    risk = doc.get("academic_risk_score")
    sm = doc.get("social_media_hours")
    return {
        "age_group": age_group(doc.get("age")),
        "dominant_content_type": dom,
        "is_short_video_dominant": dom == "short_video",
        "social_media_band": social_media_band(sm),
        "social_gt6": (sm is not None and sm > 6),
        "is_late_night": doc.get("late_night_usage") in ("Often", "Always"),
        "session_exceeds_attention": (
            session is not None and attention is not None and session > attention
        ),
        "digital_burnout_level": digital_burnout_level(doc.get("brain_rot_index")),
        "addiction_high_risk": (addiction is not None and addiction >= 25),
        "has_academic_risk": (risk is not None and risk > 0),
    }
