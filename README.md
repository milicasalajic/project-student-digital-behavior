# Analiza digitalnog ponašanja studenata

Projekat iz predmeta **Sistemi baza podataka**.

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
v1/          INICIJALNA normalizovana šema (sbp-v1): scripts/load_v1.py, schema/, queries/ (mongosh upiti u .md)
v2/          OPTIMIZOVANA denormalizovana šema (sbp-v2): scripts/build_v2.py + indexes, schema/, queries/ (mongosh)
benchmarks/  results.csv (izmerena vremena preko explain executionStats)
charts/      make_charts.py -> dijagrami (vreme, dokumenti, ubrzanje)
metabase/    write_results.js + SETUP.md (vizualizacija rezultata)
docs/        izvestaj.md, prezentacija.md
```

> Upiti se pišu i pokreću kao **klasičan mongosh** (u `mongosh`/Compass), a ne kroz Python —
> Python (pymongo) se koristi samo za **unos i izgradnju šema**. Vidi `v1/queries/` i `v2/queries/`.

## Pokretanje (ceo tok)

```bash
# 0. CSV u data/ (već postoji simlink), kopirati .env.example -> .env po potrebi
pip install -r requirements.txt
docker compose up -d                 # MongoDB (27017) + Metabase (3000)

python -m v1.scripts.load_v1         # -> sbp-v1 (6 normalizovanih kolekcija)
python -m v2.scripts.build_v2        # -> sbp-v2 (denormalizovano + Computed polja)
python -m v2.scripts.indexes         # indeksi na sbp-v2.students

# Upiti se pokreću ručno u mongosh/Compass (v1/queries, v2/queries); vremena su u benchmarks/results.csv
python -m charts.make_charts         # -> charts/*.png (iz results.csv)
docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js   # -> results_* (za Metabase)
python -m charts.make_result_images  # -> v*/queries/*/qN.png (slike rezultata upita)
```
Skraćeno: `make all` ili `./run.sh`.

## Šeme

- **v1 (normalizovana, `sbp-v1`)** — 6 kolekcija: `countries` (dimenzija), `students`,
  `digital_behavior`, `academic`, `wellbeing`, `economic`, povezane preko `student_id`.
  Upiti koriste `$lookup` join-ove → namerno usko grlo. Detalji: [`v1/schema/`](v1/schema/README.md).
- **v2 (denormalizovana, `sbp-v2`)** — jedna kolekcija `students` sa svim poljima inline,
  poddokumentom `derived` (Computed) i indeksima. Detalji: [`v2/schema/`](v2/schema/README.md).

## Upiti (10)

5 za ulogu **studentski psiholog** + 5 za **akademski savetnik**, pisani kao klasičan mongosh.
Implementacije i izmerena vremena: [`v1/queries/`](v1/queries) i [`v2/queries/`](v2/queries).

## Performanse (uporedna analiza)

![Vreme izvršavanja](charts/vrijeme_izvrsavanja.png)
![Broj dokumenata](charts/broj_dokumenata.png)
![Ubrzanje](charts/ubrzanje.png)

## Vizualizacija (Metabase)

Uputstvo za povezivanje i dashboard: [`metabase/SETUP.md`](metabase/SETUP.md).

