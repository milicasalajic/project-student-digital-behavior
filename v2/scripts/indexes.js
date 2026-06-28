// Kreiranje indeksa na sbp-v2.students (mongosh / MongoDB Compass varijanta).
// Pokretanje:  docker exec -i sbp_mongodb mongosh sbp-v2 < v2/scripts/indexes.js
// (Identično skripti v2/scripts/indexes.py — ova je za Compass/mongosh.)

const db = db.getSiblingDB("sbp-v2");
const c = db.students;

c.createIndex({ "derived.age_group": 1 });                                      // PSY-1
c.createIndex({ "derived.dominant_content_type": 1, "brain_rot_index": -1 });   // PSY-2
c.createIndex({ "derived.social_gt6": 1 });                                     // PSY-3
c.createIndex({  "brain_rot_level": 1, "cyberbullying_exposure": 1});                                 // PSY-4
c.createIndex({ "digital_addiction_score": 1, "wellbeing_index": 1, "social_media_hours": 1 }); // PSY-5
c.createIndex({ "derived.social_media_band": 1 });                              // AA-1
c.createIndex({ "derived.addiction_high_risk": 1, "gender": 1, "urban_rural": 1 }); // AA-2
c.createIndex({ "academic_risk_score": 1 });                                    // AA-3
c.createIndex({ "derived.session_exceeds_attention": 1, "derived.digital_burnout_level": 1 }); // AA-4
c.createIndex({ "development_level": 1, "family_income_level": 1 });            // AA-5
c.createIndex({ "derived.has_academic_risk": 1 });                              // AA-4/AA-5

print("Indeksi kreirani. Ukupno: " + c.getIndexes().length);
