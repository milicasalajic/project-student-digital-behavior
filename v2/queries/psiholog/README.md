# Upiti — Studentski psiholog (v2)

_Generisano iz `queries/` (tools/gen_docs.py)._

## Q1 — 502 ms

1. Po starosnim grupama (15-17,18-20,21-23,24-25): broj + prosečna
depresivnost, anksioznost, stres, akademski rizik.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": "$derived.age_group",
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_depresija": {
        "$avg": "$depression_score"
      },
      "prosek_anksioznost": {
        "$avg": "$anxiety_score"
      },
      "prosek_stres": {
        "$avg": "$stress_level"
      },
      "prosek_akademski_rizik": {
        "$avg": "$academic_risk_score"
      }
    }
  },
  {
    "$sort": {
      "_id": 1
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 4_


## Q2 — 442 ms

2. Po dominantnom tipu sadržaja: broj + prosečan brain rot indeks;
sortirano opadajuće po brain rot indeksu.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": "$derived.dominant_content_type",
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_brain_rot": {
        "$avg": "$brain_rot_index"
      }
    }
  },
  {
    "$sort": {
      "prosek_brain_rot": -1
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 4_


## Q3 — 17 ms

3. Studenti sa >6h društvenih mreža dnevno: broj + prosečan san,
raspon pažnje, skor produktivnosti.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$match": {
      "derived.social_gt6": true
    }
  },
  {
    "$group": {
      "_id": null,
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_san": {
        "$avg": "$sleep_hours"
      },
      "prosek_paznja": {
        "$avg": "$attention_span_minutes"
      },
      "prosek_produktivnost": {
        "$avg": "$productivity_score"
      }
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 14,103 · vraćeno grupa: 1_


## Q4 — 410 ms

4. Po izloženosti sajber nasilju (Da/Ne): broj + prosečan wellbeing,
depresivnost, anksioznost, stres; sortirano rastuće po wellbeing-u.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": "$cyberbullying_exposure",
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_wellbeing": {
        "$avg": "$wellbeing_index"
      },
      "prosek_depresija": {
        "$avg": "$depression_score"
      },
      "prosek_anksioznost": {
        "$avg": "$anxiety_score"
      },
      "prosek_stres": {
        "$avg": "$stress_level"
      }
    }
  },
  {
    "$sort": {
      "prosek_wellbeing": 1
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 2_


## Q5 — 81 ms

5. Visok skor digitalne zavisnosti (>18.04) I nizak indeks blagostanja
(<50.06) I umereno korišćenje mreža (<=4.20h): broj + koliko ima dominantan
kratki video + koliko koristi mreže kasno noću.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$match": {
      "digital_addiction_score": {
        "$gt": 18.04
      },
      "wellbeing_index": {
        "$lt": 50.06
      },
      "social_media_hours": {
        "$lte": 4.2
      }
    }
  },
  {
    "$group": {
      "_id": null,
      "broj_studenata": {
        "$sum": 1
      },
      "broj_kratki_video": {
        "$sum": {
          "$cond": [
            "$derived.is_short_video_dominant",
            1,
            0
          ]
        }
      },
      "broj_kasno_nocu": {
        "$sum": {
          "$cond": [
            "$derived.is_late_night",
            1,
            0
          ]
        }
      }
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 10,690 · vraćeno grupa: 1_

