# v2 — Optimizovana DENORMALIZOVANA šema (`sbp-v2`)

Jedna kolekcija **`students`** (500k) sa svim relevantnim poljima u jednom dokumentu,
poddokumentom `derived` (prekomputovane vrednosti) i indeksima. Nema više `$lookup`-a.

## Primer dokumenta
```json
{ "_id": 1, "country": "Qatar", "development_level": "Developing",
  "age": 21, "gender": "Male", "urban_rural": "Rural", "family_income_level": "High",
  "social_media_hours": 1.10, "average_session_length_minutes": 16.06,
  "attention_span_minutes": 57.55, "late_night_usage": "Sometimes",
  "education_content_hours": 0.24, "short_video_hours": 0.46,
  "brain_rot_index": 5.87, "digital_addiction_score": 8.18, "wellbeing_index": 66.66,
  "stress_level": 4.26, "anxiety_score": 3.19, "depression_score": 1.41,
  "academic_risk_score": 0.0, "class_attendance_rate": 95.48, "academic_motivation": 7.18,
  "cyberbullying_exposure": false,
  "derived": {
    "age_group": "21-23", "dominant_content_type": "educational",
    "is_short_video_dominant": false, "social_media_band": "<2h", "social_gt6": false,
    "is_late_night": false, "session_exceeds_attention": false,
    "digital_burnout_level": "Nizak", "addiction_high_risk": false, "has_academic_risk": false
  },
  "schema_version": 2 }
```

## Izvedena (Computed) polja
| Polje | Pravilo |
|---|---|
| `age_group` | 15-17 / 18-20 / 21-23 / 24-25 |
| `dominant_content_type` | argmax(education/short_video/entertainment/news _content_hours) → educational/short_video/entertainment/informative |
| `is_short_video_dominant` | bool |
| `social_media_band` | <2h / 2-4h / 4-6h / >6h |
| `social_gt6` | social_media_hours > 6 |
| `is_late_night` | late_night_usage ∈ {Often, Always} |
| `session_exceeds_attention` | average_session_length_minutes > attention_span_minutes |
| `digital_burnout_level` | iz `brain_rot_index` (percentili): Nizak <12.57 / Umeren <25.09 / Visok <34.77 / Težak ≥34.77 |
| `addiction_high_risk` | digital_addiction_score ≥ 25 |
| `has_academic_risk` | academic_risk_score > 0 |

## Indeksi
Vidi [`../scripts/indexes.py`](../scripts/indexes.py) / [`indexes.js`](../scripts/indexes.js)
— po jedan indeks za grupisanje/filtriranje svakog upita (npr. `{derived.age_group:1}`,
`{digital_addiction_score:1, wellbeing_index:1, social_media_hours:1}`,
`{development_level:1, family_income_level:1}`).

## Primenjeni MongoDB design paterni
| Pattern | Primena |
|---|---|
| **Computed** | poddokument `derived` (sve izvedene vrednosti računate jednom pri unosu) |
| **Extended Reference** | `development_level` denormalizovan iz `countries` → nema join-a za AA-5 |
| **Schema Versioning** | `sbp-v1` → `sbp-v2`, polje `schema_version` |
| **Subset** | ekonomska polja i nekorišćene infrastrukturne kolone izostavljene iz vruće kolekcije |
| **Attribute** *(opciono)* | 4 *_content_hours mogu se modelovati kao niz `content:[{type,hours}]` |
| **Approximation** *(lagano)* | percentilni pragovi i totali kao prekomputovane konstante |
| **Bucket** *(konceptualno)* | nema vremenske serije po studentu; baketiranje je analitičko (Computed) + `results_*` |
| Polymorphic / Tree / Document Versioning / Outlier | **N/A** — homogeni dokumenti, bez hijerarhije, statički snimak, ujednačena veličina (obrazloženo u izveštaju) |

Izgradnja: [`../scripts/`](../scripts/README.md) · Upiti: [`../queries/`](../queries)
