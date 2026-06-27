# Upiti — Akademski savetnik (v2)

_Generisano iz `queries/` (tools/gen_docs.py)._

## Q1 — 500 ms

1. Po dnevnim satima na mrežama (<2h, 2-4h, 4-6h, >6h): broj, procenat,
prosečan skor produktivnosti, prosečno sati učenja, prosečan akademski rizik.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": "$derived.social_media_band",
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_produktivnost": {
        "$avg": "$productivity_score"
      },
      "prosek_sati_ucenja": {
        "$avg": "$study_hours_per_week"
      },
      "prosek_akademski_rizik": {
        "$avg": "$academic_risk_score"
      }
    }
  },
  {
    "$setWindowFields": {
      "sortBy": {
        "_id": 1
      },
      "output": {
        "ukupno": {
          "$sum": "$broj_studenata",
          "window": {
            "documents": [
              "unbounded",
              "unbounded"
            ]
          }
        }
      }
    }
  },
  {
    "$addFields": {
      "procenat": {
        "$multiply": [
          {
            "$divide": [
              "$broj_studenata",
              "$ukupno"
            ]
          },
          100
        ]
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


## Q2 — 529 ms

2. Procenat visokorizičnih (digital_addiction_score >= 25) po polu i tipu
područja + njihov prosečan nivo stresa.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": {
        "pol": "$gender",
        "podrucje": "$urban_rural"
      },
      "ukupno": {
        "$sum": 1
      },
      "visokorizicni": {
        "$sum": {
          "$cond": [
            "$derived.addiction_high_risk",
            1,
            0
          ]
        }
      },
      "suma_stres_hr": {
        "$sum": {
          "$cond": [
            "$derived.addiction_high_risk",
            "$stress_level",
            0
          ]
        }
      }
    }
  },
  {
    "$addFields": {
      "procenat_visokorizicnih": {
        "$multiply": [
          {
            "$divide": [
              "$visokorizicni",
              "$ukupno"
            ]
          },
          100
        ]
      },
      "prosek_stres_visokorizicni": {
        "$cond": [
          {
            "$gt": [
              "$visokorizicni",
              0
            ]
          },
          {
            "$divide": [
              "$suma_stres_hr",
              "$visokorizicni"
            ]
          },
          null
        ]
      }
    }
  },
  {
    "$project": {
      "suma_stres_hr": 0
    }
  },
  {
    "$sort": {
      "procenat_visokorizicnih": -1
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 6_


## Q3 — 1227 ms

3. Studenti sa akademskim rizikom IZNAD proseka: broj + prosečno sati
učenja, skor produktivnosti, sati na mrežama. Prosek se računa u pipeline-u
preko $setWindowFields (prozor nad celim skupom) umesto $facet — $facet bi
materijalizovao svih 500k dokumenata u jedan niz i prešao limit od 16/100 MB.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$project": {
      "academic_risk_score": 1,
      "study_hours_per_week": 1,
      "productivity_score": 1,
      "social_media_hours": 1
    }
  },
  {
    "$setWindowFields": {
      "sortBy": {
        "_id": 1
      },
      "output": {
        "m": {
          "$avg": "$academic_risk_score",
          "window": {
            "documents": [
              "unbounded",
              "unbounded"
            ]
          }
        }
      }
    }
  },
  {
    "$match": {
      "$expr": {
        "$gt": [
          "$academic_risk_score",
          "$m"
        ]
      }
    }
  },
  {
    "$group": {
      "_id": null,
      "broj_studenata": {
        "$sum": 1
      },
      "prosek_sati_ucenja": {
        "$avg": "$study_hours_per_week"
      },
      "prosek_produktivnost": {
        "$avg": "$productivity_score"
      },
      "prosek_sati_mreze": {
        "$avg": "$social_media_hours"
      }
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 1_


## Q4 — 153 ms

4. Studenti kod kojih je prosečno trajanje sesije > trajanja koncentracije,
grupisani po nivou digitalnog sagorevanja (iz brain_rot_index): broj, broj sa
akademskim rizikom != 0, broj koji koriste mreže kasno noću, broj sa dominantnim
kratkim video sadržajem.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$match": {
      "derived.session_exceeds_attention": true
    }
  },
  {
    "$group": {
      "_id": "$derived.digital_burnout_level",
      "broj_studenata": {
        "$sum": 1
      },
      "broj_sa_rizikom": {
        "$sum": {
          "$cond": [
            "$derived.has_academic_risk",
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
      },
      "broj_kratki_video": {
        "$sum": {
          "$cond": [
            "$derived.is_short_video_dominant",
            1,
            0
          ]
        }
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

_Pregledani dokumenti: 90,432 · vraćeno grupa: 4_


## Q5 — 669 ms

5. Po kombinaciji (nivo razvijenosti države x nivo prihoda porodice): broj,
procenat sa akademskim rizikom (>0), prosečan stres, prosečan akademski rizik,
prosečno prisustvo nastavi, prosečna akademska motivacija; sort opadajuće po % rizika.

Kolekcija: `students`

```javascript
db.students.aggregate(
[
  {
    "$group": {
      "_id": {
        "razvoj": "$development_level",
        "prihod": "$family_income_level"
      },
      "broj_studenata": {
        "$sum": 1
      },
      "broj_sa_rizikom": {
        "$sum": {
          "$cond": [
            "$derived.has_academic_risk",
            1,
            0
          ]
        }
      },
      "prosek_stres": {
        "$avg": "$stress_level"
      },
      "prosek_akademski_rizik": {
        "$avg": "$academic_risk_score"
      },
      "prosek_prisustvo": {
        "$avg": "$class_attendance_rate"
      },
      "prosek_motivacija": {
        "$avg": "$academic_motivation"
      }
    }
  },
  {
    "$addFields": {
      "procenat_sa_rizikom": {
        "$multiply": [
          {
            "$divide": [
              "$broj_sa_rizikom",
              "$broj_studenata"
            ]
          },
          100
        ]
      }
    }
  },
  {
    "$sort": {
      "procenat_sa_rizikom": -1
    }
  }
]
, { allowDiskUse: true })
```

_Pregledani dokumenti: 500,000 · vraćeno grupa: 9_

