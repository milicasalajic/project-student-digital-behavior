# Metabase — povezivanje i dashboard

Metabase se pokreće zajedno sa MongoDB-om (`docker compose up -d`) i dostupan je na
**http://localhost:3000**.

## 1. Inicijalno podešavanje
1. Otvoriti `http://localhost:3000` i kreirati admin nalog (prvi put).

## 2. Povezivanje MongoDB baze
Admin settings → **Databases** → **Add database** → tip **MongoDB**:

| Polje | Vrednost |
|---|---|
| Display name | `sbp-v2` |
| Host | **`mongodb`** ⚠️ (ime servisa iz docker-compose, NE `localhost`) |
| Port | `27017` |
| Database name | `sbp-v2` |
| Authentication | bez (prazno) |

> Napomena: unutar Metabase kontejnera `localhost` je sam Metabase. Kontejneri se
> vide preko imena servisa na Docker mreži, pa je host `mongodb`.

Nakon dodavanja sačekati da Metabase odradi *sync* šeme.

## 3. Materijalizovani rezultati
Pre pravljenja grafikona pokrenuti:
```bash
python -m metabase.write_results
```
Time se rezultati svih 10 upita upisuju u sitne kolekcije:
`results_psi_q1..q5` i `results_sav_q1..q5` (u bazi `sbp-v2`).
Zatim u Metabase-u: Admin → Databases → `sbp-v2` → **Sync schema now**.

## 4. Predlog kartica za dashboard "Analiza digitalnog ponašanja studenata"
| Kartica | Kolekcija | Tip | Dimenzija → Mera |
|---|---|---|---|
| Mentalno zdravlje po uzrastu | `results_psi_q1` | bar | `_id` (uzrast) → prosek depresija/anksioznost/stres |
| Dominantan tip sadržaja | `results_psi_q2` | pie + bar | `_id` → broj_studenata, prosek_brain_rot |
| Wellbeing vs sajber-nasilje | `results_psi_q4` | bar | `_id` → prosek_wellbeing |
| Studenti po satima na mrežama | `results_sav_q1` | bar | `_id` (opseg) → broj_studenata, procenat |
| Visok rizik po polu/području | `results_sav_q2` | bar/heat | `_id.pol`,`_id.podrucje` → procenat_visokorizicnih |
| Rizik po razvoju × prihodu | `results_sav_q5` | bar | `_id` → procenat_sa_rizikom |

Sastaviti kartice u jedan dashboard i sačuvati screenshot u
`metabase/screenshots/dashboard.png` (za izveštaj).
