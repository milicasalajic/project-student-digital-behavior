# Analiza digitalnog ponašanja studenata

Projekat iz predmeta **Sistemi baza podataka**.

**Autori:** Milica — uloga *studentski psiholog* (PSY-1..5) · Ivan — uloga *akademski savetnik* (AA-1..5)

Tema projekta je analiza digitalnog ponašanja studenata na osnovu skupa podataka koji sadrži informacije o korišćenju društvenih mreža, akademskim navikama, mentalnom zdravlju i digitalnim rizicima.

Za potrebe projekta kreirane su dve šeme baze podataka, pri čemu je glavni cilj pri kreiranju druge šeme bio poboljšanje performansi upita.

## Korišćene tehnologije

- MongoDB
- Python
- Docker
- Metabase
- MongoDB Compass

## Skup podataka

`global_student_digital_behavior_dataset.csv` — **500.000 studenata**, 48 kolona, ~50 zemalja.
CSV se ne dodaje na GitHub zbog veličine, već se čuva lokalno u folderu `data/`.
Prazne vrednosti (npr. 6.262 praznih `brain_rot_level`) se pri unosu upisuju kao `null`, a `cyberbullying_exposure`/`adult_content_exposure` se pretvaraju u bool.

## Struktura projekta

```
common/      deljeni kod za unos: config, schema (tipovi/podela), derived (izvedena polja)
v1/          normalizovana šema (sbp-v1): schema/, scripts/, queries/{milica,ivan}
v2/          denormalizovana šema (sbp-v2): schema/, scripts/, queries/{milica,ivan}
charts/      make_charts.py -> dijagrami poređenja (vreme, dokumenti, ubrzanje)
metabase/    write_results.js + SETUP.md (vizualizacija rezultata)
data/        lokalni CSV (van git-a)
```

Upiti se pišu i pokreću kao klasičan **mongosh** (u mongosh/Compass), a Python (pymongo) se koristi samo za unos i izgradnju šema. Svaki upit je zaseban `README.md` u `v{1,2}/queries/{milica,ivan}/Upit*/` sa kodom, screenshotom explain plana i rezultata.

## Pokretanje

```bash
pip install -r requirements.txt
docker compose up -d                 # MongoDB (27017) + Metabase (3000)

python -m v1.scripts.load_v1         # -> sbp-v1 (6 normalizovanih kolekcija)
python -m v2.scripts.build_v2        # -> sbp-v2 (denormalizovano + izvedena polja)
python -m v2.scripts.indexes         # indeksi na sbp-v2.students

python -m charts.make_charts         # -> charts/*.png
docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js   # -> results_* (za Metabase)
```

Upiti se zatim pokreću ručno u mongosh/Compass (vidi `v{1,2}/queries/`).

## Šeme

- **v1 (normalizovana, `sbp-v1`)** — 6 kolekcija: `countries` (dimenzija), `students`, `digital_behavior`, `academic`, `wellbeing`, `economic`, povezane preko `student_id`. Upiti koriste `$lookup` join-ove → namerno usko grlo. Detalji: [`v1/schema/`](v1/schema/README.md).
- **v2 (denormalizovana, `sbp-v2`)** — jedna kolekcija `students` sa svim poljima inline, poddokumentom `derived` (izvedena polja) i indeksima. Detalji: [`v2/schema/`](v2/schema/README.md).

## Upiti (10)

5 za ulogu **studentski psiholog** (Milica) + 5 za **akademski savetnik** (Ivan), pisani kao klasičan mongosh.

**Studentski psiholog (PSY):**
1. Starosne grupe (15-17, 18-20, 21-23, 24-25) → prosečna depresivnost, anksioznost, stres, akademski rizik.
2. Dominantan tip digitalnog sadržaja → broj studenata i prosečan brain rot indeks.
3. Studenti sa >6h dnevno na mrežama → prosečan san, raspon pažnje, produktivnost.
4. Izloženost sajber nasilju i nivo brain rot-a → broj, prosečan wellbeing, depresivnost, anksioznost, stres.
5. Visoka digitalna zavisnost + nizak wellbeing uz umereno korišćenje → broj, dominantan kratki video, kasno noću.

**Akademski savetnik (AA):**
1. Opsezi sati na mrežama (<2h, 2-4h, 4-6h, >6h) → broj, procenat, produktivnost, sati učenja, akademski rizik.
2. Procenat visokorizičnih (digital_addiction_score ≥ 25) po polu × području + prosečan stres.
3. Akademski rizik iznad proseka → broj, sati učenja, produktivnost, sati na mrežama.
4. Sesija duža od koncentracije, po nivou digitalnog sagorevanja → broj, rizik≠0, kasno noću, kratki video.
5. Razvijenost države × prihod porodice → broj, % sa akademskim rizikom, stres, akademski rizik, prisustvo, motivacija.

## Performanse (uporedna analiza)

![Vreme izvršavanja](charts/vreme_izvrsavanja.png)
![Broj dokumenata](charts/broj_dokumenata.png)

## Vizualizacija (Metabase)

Uputstvo za povezivanje i dashboard: [`metabase/SETUP.md`](metabase/SETUP.md).
