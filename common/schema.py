"""Definicija kolona iz CSV-a, tipizacija i podela na normalizovane (v1) kolekcije.

48 kolona skupa `global_student_digital_behavior_dataset.csv`. Tip svake kolone je
eksplicitan (bez oslanjanja na inferenciju), a prazne vrednosti (npr. 6.262 praznih
`brain_rot_level`) postaju None umesto da budu prinudno svrstane u neku kategoriju.
"""

#Tipovi kolona 

INT_COLS = {"student_id", "age", "late_night_score"}

BOOL_COLS = {"cyberbullying_exposure": "Yes", "adult_content_exposure": "Yes"}

STR_COLS = {
    "country", "development_level", "gender", "urban_rural", "family_income_level",
    "device_access", "education_level", "field_of_study", "late_night_usage",
    "brain_rot_level",
}

FLOAT_COLS = {
    "poverty_rate_percent", "internet_infrastructure_index", "average_internet_speed_mbps",
    "internet_access_hours", "academic_motivation", "online_learning_hours",
    "social_media_hours", "sessions_per_day", "average_session_length_minutes",
    "education_content_hours", "short_video_hours", "entertainment_content_hours",
    "news_content_hours", "likes_given_per_day", "comments_written_per_day",
    "posts_created_per_week", "brain_rot_index", "attention_span_minutes",
    "study_hours_per_week", "class_attendance_rate", "productivity_score", "sleep_hours",
    "stress_level", "anxiety_score", "depression_score", "ads_viewed_per_day",
    "ads_clicked_per_week", "impulse_purchase_score", "digital_spending_per_month",
    "digital_addiction_score", "wellbeing_index", "academic_risk_score", "financial_risk_score",
}


def coerce(col, raw):
    """Pretvara sirovu CSV vrednost (str) u odgovarajući tip.

    Prazan string -> None (BSON null), čime se korektno tretiraju prazne vrednosti
    (npr. brain_rot_level). NaN se nikada ne upisuje (poison za $avg/$group).
    """
    raw = (raw or "").strip()
    if col in INT_COLS:
        return int(raw) if raw != "" else None
    if col in FLOAT_COLS:
        return float(raw) if raw != "" else None
    if col in BOOL_COLS:
        return raw == BOOL_COLS[col]
    # string
    return raw if raw != "" else None


# Dimenziona tabela: ključ je `country`, vrednosti zavise funkcionalno od zemlje.
COUNTRY_DIM_COLS = [
    "development_level", "poverty_rate_percent",
    "internet_infrastructure_index", "average_internet_speed_mbps",
]

# Polja po kolekciji (bez _id=student_id; `country` je FK ka countries._id).
V1_COLLECTIONS = {
    "students": [
        "country", "age", "gender", "urban_rural", "family_income_level",
        "device_access", "education_level", "field_of_study",
    ],
    "digital_behavior": [
        "internet_access_hours", "online_learning_hours", "social_media_hours",
        "sessions_per_day", "average_session_length_minutes", "late_night_usage",
        "late_night_score", "education_content_hours", "short_video_hours",
        "entertainment_content_hours", "news_content_hours", "likes_given_per_day",
        "comments_written_per_day", "posts_created_per_week", "brain_rot_index",
        "brain_rot_level",
    ],
    "academic": [
        "academic_motivation", "attention_span_minutes", "study_hours_per_week",
        "class_attendance_rate", "productivity_score", "academic_risk_score",
    ],
    "wellbeing": [
        "sleep_hours", "stress_level", "anxiety_score", "depression_score",
        "digital_addiction_score", "wellbeing_index", "cyberbullying_exposure",
        "adult_content_exposure",
    ],
    "economic": [
        "ads_viewed_per_day", "ads_clicked_per_week", "impulse_purchase_score",
        "digital_spending_per_month", "financial_risk_score",
    ],
}

# Sve kolone (za sanity-proveru pri unosu).
ALL_COLUMNS = (
    ["student_id"] + COUNTRY_DIM_COLS
    + [c for cols in V1_COLLECTIONS.values() for c in cols]
)
