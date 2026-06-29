# v2 — Denormalizovana šema baze

U drugoj verziji baza je napravljena denormalizovano. Za razliku od prve verzije, gde su podaci bili podeljeni u više kolekcija, ovde se podaci potrebni za upite čuvaju u jednoj kolekciji `students`.

Cilj ove verzije je da se smanji broj spajanja između kolekcija i da se upiti izvršavaju brže. U prvoj verziji su složeniji upiti morali da koriste `$lookup`, dok se u ovoj verziji većina potrebnih podataka već nalazi u istom dokumentu.

Kolekcija `students` sadrži oko 500.000 dokumenata. U okviru jednog dokumenta nalaze se osnovni podaci o studentu, podaci o digitalnom ponašanju, akademski podaci i podaci o wellbeing-u. Takođe je dodato i polje `development_level`, koje je u prvoj verziji bilo deo kolekcije `countries`.

Pored osnovnih polja, dokument sadrži i poddokument `derived`. U njemu se čuvaju vrednosti koje su izvedene iz postojećih podataka i koje se često koriste u upitima. Te vrednosti se računaju prilikom izgradnje baze, kako ne bi morale ponovo da se računaju svaki put kada se upit pokrene.

Primer dokumenta:

```json
{
  "_id": 1,
  "country": "Qatar",
  "development_level": "Developing",
  "age": 21,
  "gender": "Male",
  "urban_rural": "Rural",
  "family_income_level": "High",
  "social_media_hours": 1.1,
  "average_session_length_minutes": 16.06,
  "attention_span_minutes": 57.55,
  "late_night_usage": "Sometimes",
  "education_content_hours": 0.24,
  "short_video_hours": 0.46,
  "brain_rot_index": 5.87,
  "digital_addiction_score": 8.18,
  "wellbeing_index": 66.66,
  "stress_level": 4.26,
  "anxiety_score": 3.19,
  "depression_score": 1.41,
  "academic_risk_score": 0.0,
  "class_attendance_rate": 95.48,
  "academic_motivation": 7.18,
  "cyberbullying_exposure": false,
  "derived": {
    "age_group": "21-23",
    "dominant_content_type": "educational",
    "is_short_video_dominant": false,
    "social_media_band": "<2h",
    "social_gt6": false,
    "is_late_night": false,
    "session_exceeds_attention": false,
    "digital_burnout_level": "Nizak",
    "addiction_high_risk": false,
    "has_academic_risk": false
  },
  "schema_version": 2
}
```

U `derived` delu se nalaze polja kao što su starosna grupa, dominantan tip sadržaja, oznaka da li student koristi društvene mreže više od 6 sati, da li koristi uređaje kasno noću i da li postoji akademski rizik.

U ovoj verziji nisu prebačena sva polja iz prve verzije. Ekonomska polja i neka polja o internet infrastrukturi nisu korišćena u analiziranim upitima, pa nisu uključena u glavnu kolekciju. Na taj način dokument ostaje jednostavniji i sadrži samo podatke koji su potrebni za upite koji se mere.

Za ovu verziju dodati su i indeksi nad poljima koja se često koriste za filtriranje i grupisanje. Indeksi se kreiraju posebnom skriptom.

Izgradnja baze pokreće se komandom:

```bash
python -m v2.scripts.build_v2
```

Kreiranje indeksa pokreće se komandom:

```bash
python -m v2.scripts.indexes
```

Postoji i alternativni način izgradnje baze direktno kroz MongoDB, pomoću skripte `transform_v1_to_v2.js`. Taj pristup koristi `$lookup`, `$addFields` i `$merge`, ali je osnovni način za izgradnju ove verzije Python skripta `build_v2.py`.
