// ALTERNATIVA build_v2.py: izgradnja sbp-v2.students iz sbp-v1 unutar Mongo-a
// ($lookup spajanje 6 kolekcija + $addFields za Computed polja + $merge).
// Kanonski put je build_v2.py (Computed polja su čitljivija u Python-u); ovo je
// ovde da pokaže ekvivalentnu transformaciju agregacijom ($lookup/$merge/allowDiskUse).
//
// Pokretanje: docker exec -i sbp_mongodb mongosh sbp-v1 < v2/scripts/transform_v1_to_v2.js

const src = db.getSiblingDB("sbp-v1");

src.students.aggregate([
  // --- Spajanje normalizovanih kolekcija (1:1 na _id) i dimenzije countries ---
  { $lookup: { from: "digital_behavior", localField: "_id", foreignField: "_id", as: "d" } }, { $unwind: "$d" },
  { $lookup: { from: "academic",        localField: "_id", foreignField: "_id", as: "a" } }, { $unwind: "$a" },
  { $lookup: { from: "wellbeing",       localField: "_id", foreignField: "_id", as: "w" } }, { $unwind: "$w" },
  { $lookup: { from: "countries",       localField: "country", foreignField: "_id", as: "c" } }, { $unwind: "$c" },

  // --- Sastavljanje denormalizovanog dokumenta (Subset: bez economic kolekcije) ---
  { $project: {
      country: 1, age: 1, gender: 1, urban_rural: 1, family_income_level: 1,
      device_access: 1, education_level: 1, field_of_study: 1,
      development_level: "$c.development_level",            // Extended Reference
      // digital_behavior
      internet_access_hours: "$d.internet_access_hours", online_learning_hours: "$d.online_learning_hours",
      social_media_hours: "$d.social_media_hours", sessions_per_day: "$d.sessions_per_day",
      average_session_length_minutes: "$d.average_session_length_minutes",
      late_night_usage: "$d.late_night_usage", late_night_score: "$d.late_night_score",
      education_content_hours: "$d.education_content_hours", short_video_hours: "$d.short_video_hours",
      entertainment_content_hours: "$d.entertainment_content_hours", news_content_hours: "$d.news_content_hours",
      likes_given_per_day: "$d.likes_given_per_day", comments_written_per_day: "$d.comments_written_per_day",
      posts_created_per_week: "$d.posts_created_per_week", brain_rot_index: "$d.brain_rot_index",
      brain_rot_level: "$d.brain_rot_level",
      // academic
      academic_motivation: "$a.academic_motivation", attention_span_minutes: "$a.attention_span_minutes",
      study_hours_per_week: "$a.study_hours_per_week", class_attendance_rate: "$a.class_attendance_rate",
      productivity_score: "$a.productivity_score", academic_risk_score: "$a.academic_risk_score",
      // wellbeing
      sleep_hours: "$w.sleep_hours", stress_level: "$w.stress_level", anxiety_score: "$w.anxiety_score",
      depression_score: "$w.depression_score", digital_addiction_score: "$w.digital_addiction_score",
      wellbeing_index: "$w.wellbeing_index", cyberbullying_exposure: "$w.cyberbullying_exposure",
      adult_content_exposure: "$w.adult_content_exposure",
  } },

  // --- Computed: izvedena polja ---
  { $addFields: { derived: {
      age_group: { $switch: { branches: [
        { case: { $lte: ["$age", 17] }, then: "15-17" },
        { case: { $lte: ["$age", 20] }, then: "18-20" },
        { case: { $lte: ["$age", 23] }, then: "21-23" } ], default: "24-25" } },
      social_media_band: { $switch: { branches: [
        { case: { $lt: ["$social_media_hours", 2] }, then: "<2h" },
        { case: { $lt: ["$social_media_hours", 4] }, then: "2-4h" },
        { case: { $lte: ["$social_media_hours", 6] }, then: "4-6h" } ], default: ">6h" } },
      social_gt6: { $gt: ["$social_media_hours", 6] },
      dominant_content_type: { $let: {
        vars: { m: { $max: ["$education_content_hours", "$short_video_hours", "$entertainment_content_hours", "$news_content_hours"] } },
        in: { $switch: { branches: [
          { case: { $eq: ["$education_content_hours", "$$m"] }, then: "educational" },
          { case: { $eq: ["$short_video_hours", "$$m"] }, then: "short_video" },
          { case: { $eq: ["$entertainment_content_hours", "$$m"] }, then: "entertainment" } ], default: "informative" } } } },
      is_short_video_dominant: { $let: {
        vars: { m: { $max: ["$education_content_hours", "$short_video_hours", "$entertainment_content_hours", "$news_content_hours"] } },
        in: { $and: [ { $eq: ["$short_video_hours", "$$m"] }, { $ne: ["$education_content_hours", "$$m"] } ] } } },
      is_late_night: { $in: ["$late_night_usage", ["Often", "Always"]] },
      session_exceeds_attention: { $gt: ["$average_session_length_minutes", "$attention_span_minutes"] },
      digital_burnout_level: { $switch: { branches: [
        { case: { $lt: ["$brain_rot_index", 12.57] }, then: "Nizak" },
        { case: { $lt: ["$brain_rot_index", 25.09] }, then: "Umeren" },
        { case: { $lt: ["$brain_rot_index", 34.77] }, then: "Visok" } ], default: "Težak" } },
      addiction_high_risk: { $gte: ["$digital_addiction_score", 25] },
      has_academic_risk: { $gt: ["$academic_risk_score", 0] },
  }, schema_version: 2 } },

  { $merge: { into: { db: "sbp-v2", coll: "students" }, whenMatched: "replace", whenNotMatched: "insert" } }
], { allowDiskUse: true });

print("transform_v1_to_v2: sbp-v2.students popunjen iz sbp-v1.");
