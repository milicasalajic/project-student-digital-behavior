# Analiza digitalnog ponašanja studenata

Projekat iz predmeta **Sistemi baza podataka**.

**Autori:** Milica — uloga *studentski psiholog* (PSY-1..5) · Ivan — uloga *akademski savetnik* (AA-1..5)

Tema projekta je analiza digitalnog ponašanja studenata na osnovu skupa podataka koji sadrži informacije o korišćenju društvenih mreža, akademskim navikama, mentalnom zdravlju i digitalnim rizicima.

## Korišćene tehnologije

- MongoDB
- Python
- Docker
- Metabase
- MongoDB Compass

## Pokretanje

MongoDB i Metabase se pokreću pomoću Docker-a:

```bash
docker compose up -d
```

MongoDB konekcija:

```txt
mongodb://localhost:27017
```

Metabase je dostupan na:

```txt
http://localhost:3000
```

## Skup podataka

`global_student_digital_behavior_dataset.csv` — **500.000 studenata**, 48 kolona, ~50 zemalja.
CSV se ne dodaje na GitHub zbog veličine, već se čuva lokalno u folderu `data/`.
Čišćenje pri unosu: `cyberbullying_exposure`/`adult_content_exposure` → bool; prazne
vrednosti (npr. 6.262 praznih `brain_rot_level`) → `null` (ne forsira se kategorija).

## Struktura projekta

```
common/      deljeni kod za unos: config, schema (tipovi/podela), derived (Computed polja)
v1/          INICIJALNA normalizovana šema (sbp-v1): scripts/load_v1.py, schema/, milica/ + ivan/ (per-upit folderi: kod + explain/rezultat screenshot)
v2/          OPTIMIZOVANA denormalizovana šema (sbp-v2): scripts/build_v2.py + indexes, schema/, milica/ + ivan/ (per-upit: kod + explain/rezultat screenshot + zaključak)
benchmarks/  results.csv (izmerena vremena preko explain executionStats)
charts/      make_charts.py -> dijagrami (vreme, dokumenti, ubrzanje)
metabase/    write_results.js + SETUP.md (vizualizacija rezultata)
docs/        izvestaj.md, prezentacija.md
```

> Upiti se pišu i pokreću kao **klasičan mongosh** (u `mongosh`/Compass), a ne kroz Python —
> Python (pymongo) se koristi samo za **unos i izgradnju šema**. Vidi per-upit foldere u `v1/{milica,ivan}/` i `v2/{milica,ivan}/`.

## Pokretanje (ceo tok)

```bash
# 0. CSV u data/ (već postoji simlink), kopirati .env.example -> .env po potrebi
pip install -r requirements.txt
docker compose up -d                 # MongoDB (27017) + Metabase (3000)

python -m v1.scripts.load_v1         # -> sbp-v1 (6 normalizovanih kolekcija)
python -m v2.scripts.build_v2        # -> sbp-v2 (denormalizovano + Computed polja)
python -m v2.scripts.indexes         # indeksi na sbp-v2.students

# Upiti se pokreću ručno u mongosh/Compass (v{1,2}/{milica,ivan}/Upit*); vremena su u benchmarks/results.csv
python -m charts.make_charts         # -> charts/*.png (iz results.csv)
docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js   # -> results_* (za Metabase)
python -m charts.make_query_docs     # -> v*/{milica,ivan}/Upit*/ (README + placeholderi za screenshotove)
```
Skraćeno: `make all` ili `./run.sh`.

## Šeme

- **v1 (normalizovana, `sbp-v1`)** — 6 kolekcija: `countries` (dimenzija), `students`,
  `digital_behavior`, `academic`, `wellbeing`, `economic`, povezane preko `student_id`.
  Upiti koriste `$lookup` join-ove → namerno usko grlo. Detalji: [`v1/schema/`](v1/schema/README.md).
- **v2 (denormalizovana, `sbp-v2`)** — jedna kolekcija `students` sa svim poljima inline,
  poddokumentom `derived` (Computed) i indeksima. Detalji: [`v2/schema/`](v2/schema/README.md).

## Upiti (10)

5 za ulogu **studentski psiholog** (Milica) + 5 za **akademski savetnik** (Ivan), pisani kao klasičan mongosh.

**Studentski psiholog (PSY):**
1. Starosne grupe (15-17, 18-20, 21-23, 24-25) → prosečna depresivnost, anksioznost, stres, akademski rizik.
2. Dominantan tip digitalnog sadržaja → broj studenata i prosečan brain rot indeks.
3. Studenti sa >6h dnevno na mrežama → prosečan san, raspon pažnje, produktivnost.
4. Izloženost sajber nasilju → broj, prosečan wellbeing, depresivnost, anksioznost, stres.
5. Visoka digitalna zavisnost (>18.04) + nizak wellbeing (<50.06) uz umereno korišćenje (≤4.20h) → broj, dominantan kratki video, kasno noću.

**Akademski savetnik (AA):**
1. Opsezi sati na mrežama (<2h, 2-4h, 4-6h, >6h) → broj, procenat, produktivnost, sati učenja, akademski rizik.
2. Procenat visokorizičnih (digital_addiction_score ≥ 25) po polu × području + prosečan stres.
3. Akademski rizik iznad proseka → broj, sati učenja, produktivnost, sati na mrežama.
4. Sesija duža od koncentracije, po nivou digitalnog sagorevanja → broj, rizik≠0, kasno noću, kratki video.
5. Razvijenost države × prihod porodice → broj, % sa akademskim rizikom, stres, akademski rizik, prisustvo, motivacija.

Implementacije i izmerena vremena, **po jedan folder na upit** (kao u primeru Andrija/Vuk):
[`v1/milica`](v1/milica) · [`v1/ivan`](v1/ivan) · [`v2/milica`](v2/milica) · [`v2/ivan`](v2/ivan).

## Performanse (uporedna analiza)

![Vreme izvršavanja](charts/vrijeme_izvrsavanja.png)
![Broj dokumenata](charts/broj_dokumenata.png)
![Ubrzanje](charts/ubrzanje.png)

## Vizualizacija (Metabase)

Uputstvo za povezivanje i dashboard: [`metabase/SETUP.md`](metabase/SETUP.md).

