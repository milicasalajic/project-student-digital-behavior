#!/usr/bin/env python3
"""Generiše per-upit dokumentaciju u stilu Primera (Andrija/Vuk).

Za svaku ulogu (milica = psiholog, ivan = savetnik) i svaku verziju (v1, v2)
pravi folder `v{ver}/{autor}/Upit{n}/` sa:
  - README.md    (naslov + kod upita + "Brzina izvršavanja" + slike + zaključak za v2)
  - explain.png  <-- SCREENSHOT iz Compass/GUI: rezultat Explain opcije
  - output.png   <-- SCREENSHOT iz Compass/GUI: primer izlaznog dokumenta (rezultat)

Slike se NE generišu — to su ručni screenshotovi iz GUI-a. Skripta upisuje samo
prazne placeholder slike (iscrtkan okvir) i to SAMO ako fajl još ne postoji, pa
ponovno pokretanje nikad ne pregazi već dodate snimke. "Brzina izvršavanja" se
čita iz benchmarks/results.csv (executionTimeMillis, medijana 3 izvršavanja).

Pokretanje:  python -m charts.make_query_docs
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from common.config import ROOT  # noqa: E402

# ── mapiranje uloga ──────────────────────────────────────────────────────────
ROLES = {
    # autor      (uloga,       results_ prefiks, oznaka)
    "milica": ("psiholog", "psi", "PSY"),
    "ivan":   ("savetnik", "sav", "AA"),
}

# ── kod upita (klasičan mongosh, identičan onome u v{1,2}/queries) ────────────
PSI = {
1: ("""db.students.aggregate([
  { $lookup: { from: "wellbeing", localField: "_id", foreignField: "_id", as: "w" } },
  { $unwind: "$w" },
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $addFields: { age_group: { $switch: { branches: [
        { case: { $lte: ["$age", 17] }, then: "15-17" },
        { case: { $lte: ["$age", 20] }, then: "18-20" },
        { case: { $lte: ["$age", 23] }, then: "21-23" }
      ], default: "24-25" } } } },
  { $group: {
      _id: "$age_group",
      broj_studenata: { $sum: 1 },
      prosek_depresija: { $avg: "$w.depression_score" },
      prosek_anksioznost: { $avg: "$w.anxiety_score" },
      prosek_stres: { $avg: "$w.stress_level" },
      prosek_akademski_rizik: { $avg: "$a.academic_risk_score" } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $group: {
      _id: "$derived.age_group",
      broj_studenata: { $sum: 1 },
      prosek_depresija: { $avg: "$depression_score" },
      prosek_anksioznost: { $avg: "$anxiety_score" },
      prosek_stres: { $avg: "$stress_level" },
      prosek_akademski_rizik: { $avg: "$academic_risk_score" } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })"""),
2: ("""db.digital_behavior.aggregate([
  { $addFields: { dominant_content_type: { $let: {
      vars: { m: { $max: ["$education_content_hours", "$short_video_hours",
                          "$entertainment_content_hours", "$news_content_hours"] } },
      in: { $switch: { branches: [
        { case: { $eq: ["$education_content_hours", "$$m"] }, then: "educational" },
        { case: { $eq: ["$short_video_hours", "$$m"] }, then: "short_video" },
        { case: { $eq: ["$entertainment_content_hours", "$$m"] }, then: "entertainment" }
      ], default: "informative" } } } } } },
  { $group: {
      _id: "$dominant_content_type",
      broj_studenata: { $sum: 1 },
      prosek_brain_rot: { $avg: "$brain_rot_index" } } },
  { $sort: { prosek_brain_rot: -1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $group: {
      _id: "$derived.dominant_content_type",
      broj_studenata: { $sum: 1 },
      prosek_brain_rot: { $avg: "$brain_rot_index" } } },
  { $sort: { prosek_brain_rot: -1 } }
], { allowDiskUse: true })"""),
3: ("""db.digital_behavior.aggregate([
  { $match: { social_media_hours: { $gt: 6 } } },
  { $lookup: { from: "wellbeing", localField: "_id", foreignField: "_id", as: "w" } },
  { $unwind: "$w" },
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_san: { $avg: "$w.sleep_hours" },
      prosek_paznja: { $avg: "$a.attention_span_minutes" },
      prosek_produktivnost: { $avg: "$a.productivity_score" } } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $match: { "derived.social_gt6": true } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_san: { $avg: "$sleep_hours" },
      prosek_paznja: { $avg: "$attention_span_minutes" },
      prosek_produktivnost: { $avg: "$productivity_score" } } }
], { allowDiskUse: true })"""),
4: ("""db.wellbeing.aggregate([
  { $group: {
      _id: "$cyberbullying_exposure",
      broj_studenata: { $sum: 1 },
      prosek_wellbeing: { $avg: "$wellbeing_index" },
      prosek_depresija: { $avg: "$depression_score" },
      prosek_anksioznost: { $avg: "$anxiety_score" },
      prosek_stres: { $avg: "$stress_level" } } },
  { $sort: { prosek_wellbeing: 1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $group: {
      _id: "$cyberbullying_exposure",
      broj_studenata: { $sum: 1 },
      prosek_wellbeing: { $avg: "$wellbeing_index" },
      prosek_depresija: { $avg: "$depression_score" },
      prosek_anksioznost: { $avg: "$anxiety_score" },
      prosek_stres: { $avg: "$stress_level" } } },
  { $sort: { prosek_wellbeing: 1 } }
], { allowDiskUse: true })"""),
5: ("""db.wellbeing.aggregate([
  { $match: { digital_addiction_score: { $gt: 18.04 }, wellbeing_index: { $lt: 50.06 } } },
  { $lookup: { from: "digital_behavior", localField: "_id", foreignField: "_id", as: "d" } },
  { $unwind: "$d" },
  { $match: { "d.social_media_hours": { $lte: 4.20 } } },
  { $addFields: {
      dominant: { $let: {
        vars: { m: { $max: ["$d.education_content_hours", "$d.short_video_hours",
                            "$d.entertainment_content_hours", "$d.news_content_hours"] } },
        in: { $switch: { branches: [
          { case: { $eq: ["$d.education_content_hours", "$$m"] }, then: "educational" },
          { case: { $eq: ["$d.short_video_hours", "$$m"] }, then: "short_video" },
          { case: { $eq: ["$d.entertainment_content_hours", "$$m"] }, then: "entertainment" }
        ], default: "informative" } } } },
      is_late: { $in: ["$d.late_night_usage", ["Often", "Always"]] } } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      broj_kratki_video: { $sum: { $cond: [{ $eq: ["$dominant", "short_video"] }, 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$is_late", 1, 0] } } } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $match: { digital_addiction_score: { $gt: 18.04 },
              wellbeing_index: { $lt: 50.06 },
              social_media_hours: { $lte: 4.20 } } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      broj_kratki_video: { $sum: { $cond: ["$derived.is_short_video_dominant", 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$derived.is_late_night", 1, 0] } } } }
], { allowDiskUse: true })"""),
}

SAV = {
1: ("""// ukupan broj studenata
const ukupno = db.digital_behavior.countDocuments();

db.digital_behavior.aggregate([
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $addFields: { band: { $switch: { branches: [
        { case: { $lt: ["$social_media_hours", 2] }, then: "<2h" },
        { case: { $lt: ["$social_media_hours", 4] }, then: "2-4h" },
        { case: { $lte: ["$social_media_hours", 6] }, then: "4-6h" }
      ], default: ">6h" } } } },
  { $group: {
      _id: "$band",
      broj_studenata: { $sum: 1 },
      prosek_produktivnost: { $avg: "$a.productivity_score" },
      prosek_sati_ucenja: { $avg: "$a.study_hours_per_week" },
      prosek_akademski_rizik: { $avg: "$a.academic_risk_score" } } },
  { $addFields: { procenat: { $multiply: [{ $divide: ["$broj_studenata", ukupno] }, 100] } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })""",
"""// ukupan broj studenata
const ukupno = db.students.countDocuments();

db.students.aggregate([
  { $group: {
      _id: "$derived.social_media_band",
      broj_studenata: { $sum: 1 },
      prosek_produktivnost: { $avg: "$productivity_score" },
      prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_akademski_rizik: { $avg: "$academic_risk_score" } } },
  { $addFields: { procenat: { $multiply: [{ $divide: ["$broj_studenata", ukupno] }, 100] } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })"""),
2: ("""db.wellbeing.aggregate([
  { $lookup: { from: "students", localField: "_id", foreignField: "_id", as: "s" } },
  { $unwind: "$s" },
  { $addFields: { high_risk: { $gte: ["$digital_addiction_score", 25] } } },
  { $group: {
      _id: { pol: "$s.gender", podrucje: "$s.urban_rural" },
      ukupno: { $sum: 1 },
      visokorizicni: { $sum: { $cond: ["$high_risk", 1, 0] } },
      suma_stres_hr: { $sum: { $cond: ["$high_risk", "$stress_level", 0] } } } },
  { $addFields: {
      procenat_visokorizicnih: { $multiply: [{ $divide: ["$visokorizicni", "$ukupno"] }, 100] },
      prosek_stres_visokorizicni: { $cond: [
        { $gt: ["$visokorizicni", 0] },
        { $divide: ["$suma_stres_hr", "$visokorizicni"] },
        null ] } } },
  { $project: { suma_stres_hr: 0 } },
  { $sort: { procenat_visokorizicnih: -1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $group: {
      _id: { pol: "$gender", podrucje: "$urban_rural" },
      ukupno: { $sum: 1 },
      visokorizicni: { $sum: { $cond: ["$derived.addiction_high_risk", 1, 0] } },
      suma_stres_hr: { $sum: { $cond: ["$derived.addiction_high_risk", "$stress_level", 0] } } } },
  { $addFields: {
      procenat_visokorizicnih: { $multiply: [{ $divide: ["$visokorizicni", "$ukupno"] }, 100] },
      prosek_stres_visokorizicni: { $cond: [
        { $gt: ["$visokorizicni", 0] },
        { $divide: ["$suma_stres_hr", "$visokorizicni"] },
        null ] } } },
  { $project: { suma_stres_hr: 0 } },
  { $sort: { procenat_visokorizicnih: -1 } }
], { allowDiskUse: true })"""),
3: ("""// 1) prosečan akademski rizik
const prosek = db.academic.aggregate([
  { $group: { _id: null, m: { $avg: "$academic_risk_score" } } }
]).toArray()[0].m;

// 2) studenti iznad proseka
db.academic.aggregate([
  { $match: { academic_risk_score: { $gt: prosek } } },
  { $lookup: { from: "digital_behavior", localField: "_id", foreignField: "_id", as: "d" } },
  { $unwind: "$d" },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_produktivnost: { $avg: "$productivity_score" },
      prosek_sati_mreze: { $avg: "$d.social_media_hours" } } }
], { allowDiskUse: true })""",
"""// 1) prosečan akademski rizik
const prosek = db.students.aggregate([
  { $group: { _id: null, m: { $avg: "$academic_risk_score" } } }
]).toArray()[0].m;

// 2) studenti iznad proseka
db.students.aggregate([
  { $match: { academic_risk_score: { $gt: prosek } } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_produktivnost: { $avg: "$productivity_score" },
      prosek_sati_mreze: { $avg: "$social_media_hours" } } }
], { allowDiskUse: true })"""),
4: ("""db.digital_behavior.aggregate([
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $match: { $expr: { $gt: ["$average_session_length_minutes", "$a.attention_span_minutes"] } } },
  { $addFields: {
      burnout: { $switch: { branches: [
        { case: { $lt: ["$brain_rot_index", 12.57] }, then: "Nizak" },
        { case: { $lt: ["$brain_rot_index", 25.09] }, then: "Umeren" },
        { case: { $lt: ["$brain_rot_index", 34.77] }, then: "Visok" }
      ], default: "Težak" } },
      dominant: { $let: {
        vars: { m: { $max: ["$education_content_hours", "$short_video_hours",
                            "$entertainment_content_hours", "$news_content_hours"] } },
        in: { $switch: { branches: [
          { case: { $eq: ["$education_content_hours", "$$m"] }, then: "educational" },
          { case: { $eq: ["$short_video_hours", "$$m"] }, then: "short_video" },
          { case: { $eq: ["$entertainment_content_hours", "$$m"] }, then: "entertainment" }
        ], default: "informative" } } } },
      is_late: { $in: ["$late_night_usage", ["Often", "Always"]] } } },
  { $group: {
      _id: "$burnout",
      broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: [{ $ne: ["$a.academic_risk_score", 0] }, 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$is_late", 1, 0] } },
      broj_kratki_video: { $sum: { $cond: [{ $eq: ["$dominant", "short_video"] }, 1, 0] } } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $match: { "derived.session_exceeds_attention": true } },
  { $group: {
      _id: "$derived.digital_burnout_level",
      broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: ["$derived.has_academic_risk", 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$derived.is_late_night", 1, 0] } },
      broj_kratki_video: { $sum: { $cond: ["$derived.is_short_video_dominant", 1, 0] } } } },
  { $sort: { _id: 1 } }
], { allowDiskUse: true })"""),
5: ("""db.students.aggregate([
  { $lookup: { from: "countries", localField: "country", foreignField: "_id", as: "c" } },
  { $unwind: "$c" },
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $lookup: { from: "wellbeing", localField: "_id", foreignField: "_id", as: "w" } },
  { $unwind: "$w" },
  { $group: {
      _id: { razvoj: "$c.development_level", prihod: "$family_income_level" },
      broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: [{ $gt: ["$a.academic_risk_score", 0] }, 1, 0] } },
      prosek_stres: { $avg: "$w.stress_level" },
      prosek_akademski_rizik: { $avg: "$a.academic_risk_score" },
      prosek_prisustvo: { $avg: "$a.class_attendance_rate" },
      prosek_motivacija: { $avg: "$a.academic_motivation" } } },
  { $addFields: { procenat_sa_rizikom: {
      $multiply: [{ $divide: ["$broj_sa_rizikom", "$broj_studenata"] }, 100] } } },
  { $sort: { procenat_sa_rizikom: -1 } }
], { allowDiskUse: true })""",
"""db.students.aggregate([
  { $group: {
      _id: { razvoj: "$development_level", prihod: "$family_income_level" },
      broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: ["$derived.has_academic_risk", 1, 0] } },
      prosek_stres: { $avg: "$stress_level" },
      prosek_akademski_rizik: { $avg: "$academic_risk_score" },
      prosek_prisustvo: { $avg: "$class_attendance_rate" },
      prosek_motivacija: { $avg: "$academic_motivation" } } },
  { $addFields: { procenat_sa_rizikom: {
      $multiply: [{ $divide: ["$broj_sa_rizikom", "$broj_studenata"] }, 100] } } },
  { $sort: { procenat_sa_rizikom: -1 } }
], { allowDiskUse: true })"""),
}

CODE = {"psiholog": PSI, "savetnik": SAV}

# ── naslovi upita ─────────────────────────────────────────────────────────────
TITLES = {
("psiholog", 1): "Grupisati studente po starosnim grupama (15-17, 18-20, 21-23, 24-25) i prikazati prosečnu depresivnost, anksioznost, stres i akademski rizik.",
("psiholog", 2): "Grupisati studente prema dominantnom tipu digitalnog sadržaja; prikazati broj studenata i prosečan brain rot indeks, sortirano opadajuće po brain rot indeksu.",
("psiholog", 3): "Prikazati broj studenata koji koriste društvene mreže više od 6 sati dnevno, i za tu grupu prosečan broj sati sna, prosečan raspon pažnje i prosečan skor produktivnosti.",
("psiholog", 4): "Grupisati studente prema izloženosti sajber nasilju; prikazati broj studenata, prosečan wellbeing indeks, depresivnost, anksioznost i stres, sortirano rastuće po wellbeing indeksu.",
("psiholog", 5): "Broj studenata sa visokim skorom digitalne zavisnosti (>18.04) i niskim indeksom blagostanja (<50.06) koji NE koriste mreže intenzivno (≤4.20h); za tu grupu broj studenata, broj sa dominantnim kratkim videom i broj koji koriste mreže kasno noću.",
("savetnik", 1): "Grupisati studente po dnevnim satima korišćenja društvenih mreža (<2h, 2-4h, 4-6h, >6h); prikazati broj studenata, procenat, prosečan skor produktivnosti, prosečan broj sati učenja i prosečan akademski rizik.",
("savetnik", 2): "Procenat „visokorizičnih“ studenata (digital_addiction_score ≥ 25) po polu i tipu područja, i njihov prosečan nivo stresa.",
("savetnik", 3): "Izdvojiti studente sa akademskim rizikom iznad proseka; prikazati ukupan broj studenata, prosečan broj sati učenja, prosečan skor produktivnosti i prosečan broj sati na društvenim mrežama.",
("savetnik", 4): "Studenti kod kojih je prosečno trajanje sesije duže od trajanja koncentracije, grupisani po nivou digitalnog sagorevanja (iz brain_rot_index); za svaku grupu broj studenata, broj sa akademskim rizikom ≠ 0, broj koji koriste mreže kasno noću i broj sa dominantnim kratkim videom.",
("savetnik", 5): "Grupisati studente prema kombinaciji nivoa razvijenosti države i nivoa prihoda porodice; za svaku grupu broj studenata, procenat sa akademskim rizikom (>0), prosečan stres, prosečan akademski rizik, prosečno prisustvo nastavi i prosečnu akademsku motivaciju, sortirano opadajuće po procentu sa rizikom.",
}

# ── plan pristupa po upitu (verifikovano živim explain-om na MongoDB 7.0) ─────
# v1_base, v1_lookups; v2_scan, v2_index (keyPattern za IXSCAN ili postojeći indeks za COLLSCAN),
# v2_uses_index, two_step, zakljucak_v2
PLAN = {
("psiholog", 1): dict(v1_base="students", v1_lookups=["wellbeing", "academic"],
    v2_scan="COLLSCAN", v2_index="{ derived.age_group: 1 }", v2_uses_index=False, two_step=False,
    zak="Uklonjena su dva `$lookup` join-a (wellbeing, academic), a grupiše se po prekomputovanom `derived.age_group`. Vreme padá ~20× (10256→502 ms). Grupisanje ide po celoj kolekciji (COLLSCAN), ali bez skupih spajanja."),
("psiholog", 2): dict(v1_base="digital_behavior", v1_lookups=[],
    v2_scan="COLLSCAN", v2_index="{ derived.dominant_content_type: 1, brain_rot_index: -1 }", v2_uses_index=False, two_step=False,
    zak="Upit i u v1 radi nad jednom kolekcijom (bez join-a), pa denormalizacija ne donosi ubrzanje — v2 je čak neznatno sporiji zbog većih dokumenata. Pošten nalaz: optimizacija ne pomaže kada nema uskog grla."),
("psiholog", 3): dict(v1_base="digital_behavior", v1_lookups=["wellbeing", "academic"],
    v2_scan="IXSCAN", v2_index="{ derived.social_gt6: 1 }", v2_uses_index=True, two_step=False,
    zak="Selektivan `$match` (`derived.social_gt6`) koristi indeks → `IXSCAN` umesto punog pregleda, uz uklonjena 2 join-a. Vreme padá ~23× (388→17 ms)."),
("psiholog", 4): dict(v1_base="wellbeing", v1_lookups=[],
    v2_scan="COLLSCAN", v2_index="{ cyberbullying_exposure: 1 }", v2_uses_index=False, two_step=False,
    zak="Jedna kolekcija i u v1; nema join-a ni selektivnog filtera, pa je COLLSCAN neizbežan u obe verzije — slično vreme (pošten nalaz)."),
("psiholog", 5): dict(v1_base="wellbeing", v1_lookups=["digital_behavior"],
    v2_scan="IXSCAN", v2_index="{ digital_addiction_score: 1, wellbeing_index: 1, social_media_hours: 1 }", v2_uses_index=True, two_step=False,
    zak="Složeni indeks `{digital_addiction_score, wellbeing_index, social_media_hours}` + uklonjen join → `IXSCAN`, ~12× brže (1013→81 ms)."),
("savetnik", 1): dict(v1_base="digital_behavior", v1_lookups=["academic"],
    v2_scan="COLLSCAN", v2_index="{ derived.social_media_band: 1 }", v2_uses_index=False, two_step=False,
    zak="Uklonjen `$lookup` (academic) i grupisanje po `derived.social_media_band` → ~9× brže (5015→565 ms). Grupisanje po celoj kolekciji (COLLSCAN), bez spajanja."),
("savetnik", 2): dict(v1_base="wellbeing", v1_lookups=["students"],
    v2_scan="COLLSCAN", v2_index="{ derived.addiction_high_risk: 1, gender: 1, urban_rural: 1 }", v2_uses_index=False, two_step=False,
    zak="Uklonjen `$lookup` (students) i korišćen prekomputovani `derived.addiction_high_risk` → ~10× brže (5365→529 ms). Grupisanje po celoj kolekciji (COLLSCAN)."),
("savetnik", 3): dict(v1_base="academic", v1_lookups=["digital_behavior"],
    v2_scan="IXSCAN", v2_index="{ academic_risk_score: 1 }", v2_uses_index=True, two_step=True,
    zak="Filter `academic_risk_score > prosek` koristi indeks (`IXSCAN`), uz uklonjen join. Ubrzanje je umereno (~1.4×) jer je i v1 bio relativno brz — usko grlo ovde nije izraženo."),
("savetnik", 4): dict(v1_base="digital_behavior", v1_lookups=["academic"],
    v2_scan="IXSCAN", v2_index="{ derived.session_exceeds_attention: 1, derived.digital_burnout_level: 1 }", v2_uses_index=True, two_step=False,
    zak="Najveće ubrzanje (~36×): u v1 je `$expr` poređenje polja (sesija vs pažnja) posle join-a forsiralo pun pregled; u v2 je to prekomputovano (`derived.session_exceeds_attention`) i indeksirano → `IXSCAN` (5534→153 ms)."),
("savetnik", 5): dict(v1_base="students", v1_lookups=["countries", "academic", "wellbeing"],
    v2_scan="COLLSCAN", v2_index="{ development_level: 1, family_income_level: 1 }", v2_uses_index=False, two_step=False,
    zak="Uklonjena tri `$lookup` join-a (countries, academic, wellbeing) i `development_level` denormalizovan (Extended Reference) → ~23× brže (15394→669 ms). Grupisanje po celoj kolekciji (COLLSCAN), bez spajanja."),
}

# ── placeholder slike (zameniti ručnim Compass/GUI screenshotovima) ──────────
def placeholder(path, label):
    """Napravi prazan placeholder okvir SAMO ako fajl ne postoji (čuva ručne snimke)."""
    if path.exists():
        return
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0.02, 0.05), 0.96, 0.9, fill=True,
                 facecolor="#f4f6f8", edgecolor="#9aa7b4", lw=1.6, ls="--"))
    ax.text(0.5, 0.64, "[ Compass / GUI screenshot ]", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#5a6b7b")
    ax.text(0.5, 0.42, label, ha="center", va="center", fontsize=11, color="#5a6b7b")
    ax.text(0.5, 0.20, "zameni ovu sliku snimkom iz GUI-a (isto ime fajla)",
            ha="center", va="center", fontsize=9, color="#9aa7b4")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


# ── main ─────────────────────────────────────────────────────────────────────
def readme(role, n, version, ms):
    title = TITLES[(role, n)]
    code = CODE[role][n][0 if version == "v1" else 1]
    head = f"# Upit {n}{' (optimizovan)' if version == 'v2' else ''} - {title}\n"
    body = [head, "\nKod upita:\n", "\n~~~\n", code, "\n~~~\n",
            f"\nBrzina izvršavanja: {ms} ms\n",
            "\nRezultat Explain opcije:\n", "\n![explain](./explain.png)\n",
            "\nPrimer izlaznog dokumenta:\n", "\n![rezultat](./output.png)\n"]
    if version == "v2":
        body += [f"\nZaključak:\n  • {PLAN[(role, n)]['zak']}\n"]
    return "".join(body)


def main():
    df = pd.read_csv(ROOT / "benchmarks" / "results.csv")

    def server_ms(role, version, n):
        r = df[(df.author == role) & (df.version == version) & (df.query_id == f"q{n}")]
        return int(r.iloc[0]["server_time_ms"])

    for author, (role, prefix, mark) in ROLES.items():
        for version in ("v1", "v2"):
            for n in range(1, 6):
                folder = ROOT / version / author / f"Upit{n}"
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "README.md").write_text(
                    readme(role, n, version, server_ms(role, version, n)), encoding="utf-8")
                placeholder(folder / "explain.png", f"EXPLAIN — {mark}-{n} ({version})")
                placeholder(folder / "output.png", f"REZULTAT (primer dokumenta) — {mark}-{n}")
                print(f"  {version}/{author}/Upit{n}/  (README + placeholder ako fali)")


if __name__ == "__main__":
    main()
