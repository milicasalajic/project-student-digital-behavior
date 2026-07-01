const db = db.getSiblingDB("sbp-v2");
const c = db.students;

c.createIndex({ "derived.age_group": 1 });
c.createIndex({ "derived.dominant_content_type": 1, "brain_rot_index": -1 });
c.createIndex({ "derived.social_gt6": 1 });
c.createIndex({ "brain_rot_level": 1, "cyberbullying_exposure": 1 });
c.createIndex({ "digital_addiction_score": 1, "wellbeing_index": 1, "social_media_hours": 1 });
c.createIndex({ "derived.social_media_band": 1 });
c.createIndex({ "derived.addiction_high_risk": 1, "gender": 1, "urban_rural": 1 });
c.createIndex({ "academic_risk_score": 1 });
c.createIndex({ "derived.session_exceeds_attention": 1, "derived.digital_burnout_level": 1 });
c.createIndex({ "development_level": 1, "family_income_level": 1 });
c.createIndex({ "derived.has_academic_risk": 1 });

print("Indeksi kreirani. Ukupno: " + c.getIndexes().length);
