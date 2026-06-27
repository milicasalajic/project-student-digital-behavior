# v1 — Inicijalna NORMALIZOVANA šema (`sbp-v1`)

Šema verno prati strukturu izvora i deli podatke na **6 kolekcija** povezanih preko
`student_id`. Cilj je realna normalizacija u kojoj većina analitičkih upita mora da
spaja (`$lookup`) više kolekcija — to je namerno **usko grlo** koje merimo.

> **Bez sekundarnih indeksa** (samo implicitni `_id`). Time je svaki `$match` po
> ne-`_id` polju COLLSCAN, a join-ovi su isključivo na `_id` (najpovoljniji slučaj
> normalizacije), pa izmerena cena dolazi od spajanja i skeniranja — ne od loše veze.

## Kolekcije

| Kolekcija | `_id` | Broj | Polja |
|---|---|---|---|
| `countries` | country (string) | ~50 | development_level, poverty_rate_percent, internet_infrastructure_index, average_internet_speed_mbps |
| `students` | student_id | 500k | country (FK→countries), age, gender, urban_rural, family_income_level, device_access, education_level, field_of_study |
| `digital_behavior` | student_id | 500k | internet_access_hours, online_learning_hours, social_media_hours, sessions_per_day, average_session_length_minutes, late_night_usage, late_night_score, education/short_video/entertainment/news_content_hours, likes/comments/posts, brain_rot_index, brain_rot_level |
| `academic` | student_id | 500k | academic_motivation, attention_span_minutes, study_hours_per_week, class_attendance_rate, productivity_score, academic_risk_score |
| `wellbeing` | student_id | 500k | sleep_hours, stress_level, anxiety_score, depression_score, digital_addiction_score, wellbeing_index, cyberbullying_exposure, adult_content_exposure |
| `economic` | student_id | 500k | ads_viewed_per_day, ads_clicked_per_week, impulse_purchase_score, digital_spending_per_month, financial_risk_score |

## Primer dokumenta `students`
```json
{ "_id": 1, "country": "Qatar", "age": 21, "gender": "Male", "urban_rural": "Rural",
  "family_income_level": "High", "device_access": "Smartphone",
  "education_level": "Graduate", "field_of_study": "Business" }
```
## Primer dokumenta `countries`
```json
{ "_id": "Qatar", "development_level": "Developing", "poverty_rate_percent": 16.3,
  "internet_infrastructure_index": 54.93, "average_internet_speed_mbps": 27.19 }
```

## Koje kolekcije koji upit spaja
| Upit | Kolekcije (broj join-ova) |
|---|---|
| PSY-1 | students + wellbeing + academic (2) |
| PSY-2 | digital_behavior (0) |
| PSY-3 | digital_behavior + wellbeing + academic (2) |
| PSY-4 | wellbeing (0) |
| PSY-5 | wellbeing + digital_behavior (1) |
| AA-1 | digital_behavior + academic (1) |
| AA-2 | wellbeing + students (1) |
| AA-3 | academic + digital_behavior (1) + $facet |
| AA-4 | digital_behavior + academic (1) + poređenje polja |
| AA-5 | **countries + students + academic + wellbeing (3)** |

> `economic` se ne koristi ni u jednom od 10 upita (postoji radi potpunosti
> normalizacije); u v2 se izostavlja iz vruće kolekcije → **Subset pattern**.

Unos: [`../scripts/`](../scripts/README.md) · Upiti: [`../queries/`](../queries)
