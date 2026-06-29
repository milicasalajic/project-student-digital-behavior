// Materijalizacija rezultata 10 upita u rezultat-kolekcije (za Metabase).
// Pokretanje:  docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js

const db = db.getSiblingDB("sbp-v2");
const O = { allowDiskUse: true };

// --- Psiholog ---
db.students.aggregate([
  { $group: { _id: "$derived.age_group", broj_studenata: { $sum: 1 },
      prosek_depresija: { $avg: "$depression_score" }, prosek_anksioznost: { $avg: "$anxiety_score" },
      prosek_stres: { $avg: "$stress_level" }, prosek_akademski_rizik: { $avg: "$academic_risk_score" } } },
  { $sort: { _id: 1 } }, { $out: "results_psi_q1" }], O);

db.students.aggregate([
  { $group: { _id: "$derived.dominant_content_type", broj_studenata: { $sum: 1 },
      prosek_brain_rot: { $avg: "$brain_rot_index" } } },
  { $sort: { prosek_brain_rot: -1 } }, { $out: "results_psi_q2" }], O);

db.students.aggregate([
  { $match: { "derived.social_gt6": true } },
  { $group: { _id: null, broj_studenata: { $sum: 1 }, prosek_san: { $avg: "$sleep_hours" },
      prosek_paznja: { $avg: "$attention_span_minutes" }, prosek_produktivnost: { $avg: "$productivity_score" } } },
  { $out: "results_psi_q3" }], O);

db.students.aggregate([
  { $match: { brain_rot_level: { $ne: null } } },
  { $group: {
      _id: {
        cyberbullying_exposure: "$cyberbullying_exposure", brain_rot_level: "$brain_rot_level"},
      broj_studenata: { $sum: 1 }, prosek_wellbeing: { $avg: "$wellbeing_index" }, prosek_depresija: { $avg: "$depression_score" },
      prosek_anksioznost: { $avg: "$anxiety_score" },prosek_stres: { $avg: "$stress_level" } } },
  { $project: {_id: 0, cyberbullying_exposure: "$_id.cyberbullying_exposure", brain_rot_level: "$_id.brain_rot_level",
      broj_studenata: 1, prosek_wellbeing: { $round: ["$prosek_wellbeing", 2] },  prosek_depresija: { $round: ["$prosek_depresija", 2] },
      prosek_anksioznost: { $round: ["$prosek_anksioznost", 2] }, prosek_stres: { $round: ["$prosek_stres", 2] } } },
  { $sort: { prosek_wellbeing: 1 } },
  { $out: "results_psi_q4" }
], O);

db.students.aggregate([
  { $match: { digital_addiction_score: { $gt: 18.04 }, wellbeing_index: { $lt: 50.06 }, social_media_hours: { $lte: 4.20 } } },
  { $group: { _id: null, broj_studenata: { $sum: 1 },
      broj_kratki_video: { $sum: { $cond: ["$derived.is_short_video_dominant", 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$derived.is_late_night", 1, 0] } } } },
  { $out: "results_psi_q5" }], O);

// --- Savetnik ---
const uk_sav_q1 = db.students.countDocuments();
db.students.aggregate([
  { $group: { _id: "$derived.social_media_band", broj_studenata: { $sum: 1 },
      prosek_produktivnost: { $avg: "$productivity_score" }, prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_akademski_rizik: { $avg: "$academic_risk_score" } } },
  { $addFields: { procenat: { $multiply: [{ $divide: ["$broj_studenata", uk_sav_q1] }, 100] } } },
  { $sort: { _id: 1 } }, { $out: "results_sav_q1" }], O);

db.students.aggregate([
  { $group: { _id: { pol: "$gender", podrucje: "$urban_rural" }, ukupno: { $sum: 1 },
      visokorizicni: { $sum: { $cond: ["$derived.addiction_high_risk", 1, 0] } },
      suma_stres_hr: { $sum: { $cond: ["$derived.addiction_high_risk", "$stress_level", 0] } } } },
  { $addFields: { pol: "$_id.pol", podrucje: "$_id.podrucje",
      procenat_visokorizicnih: { $multiply: [{ $divide: ["$visokorizicni", "$ukupno"] }, 100] },
      prosek_stres_visokorizicni: { $cond: [{ $gt: ["$visokorizicni", 0] }, { $divide: ["$suma_stres_hr", "$visokorizicni"] }, null] } } },
  { $project: { suma_stres_hr: 0 } }, { $sort: { procenat_visokorizicnih: -1 } }, { $out: "results_sav_q2" }], O);

const prosek_sav_q3 = db.students.aggregate([{ $group: { _id: null, m: { $avg: "$academic_risk_score" } } }]).toArray()[0].m;
db.students.aggregate([
  { $match: { academic_risk_score: { $gt: prosek_sav_q3 } } },
  { $group: { _id: null, broj_studenata: { $sum: 1 }, prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_produktivnost: { $avg: "$productivity_score" }, prosek_sati_mreze: { $avg: "$social_media_hours" } } },
  { $out: "results_sav_q3" }], O);

db.students.aggregate([
  { $match: { "derived.session_exceeds_attention": true } },
  { $group: { _id: "$derived.digital_burnout_level", broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: ["$derived.has_academic_risk", 1, 0] } },
      broj_kasno_nocu: { $sum: { $cond: ["$derived.is_late_night", 1, 0] } },
      broj_kratki_video: { $sum: { $cond: ["$derived.is_short_video_dominant", 1, 0] } } } },
  { $sort: { _id: 1 } }, { $out: "results_sav_q4" }], O);

db.students.aggregate([
  { $group: { _id: { razvoj: "$development_level", prihod: "$family_income_level" }, broj_studenata: { $sum: 1 },
      broj_sa_rizikom: { $sum: { $cond: ["$derived.has_academic_risk", 1, 0] } },
      prosek_stres: { $avg: "$stress_level" }, prosek_akademski_rizik: { $avg: "$academic_risk_score" },
      prosek_prisustvo: { $avg: "$class_attendance_rate" }, prosek_motivacija: { $avg: "$academic_motivation" } } },
  { $addFields: { razvoj: "$_id.razvoj", prihod: "$_id.prihod",
      procenat_sa_rizikom: { $multiply: [{ $divide: ["$broj_sa_rizikom", "$broj_studenata"] }, 100] } } },
  { $sort: { procenat_sa_rizikom: -1 } }, { $out: "results_sav_q5" }], O);

print("Materijalizovano 10 results_* kolekcija u sbp-v2.");
