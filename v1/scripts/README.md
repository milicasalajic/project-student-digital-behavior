# v1 — skripta za unos

`load_v1.py` — streaming unos CSV-a u normalizovanu bazu `sbp-v1` (6 kolekcija).

## Pokretanje
```bash
python -m v1.scripts.load_v1          # briše sbp-v1 i unosi iznova (idempotentno)
python -m v1.scripts.load_v1 --no-drop
```

## Kako radi
- `csv.DictReader` — red po red (konstantna memorija nad 319 MB; bez pandas-a).
- Tipizacija preko `common.schema.coerce` (int/float/bool/str; prazno → `null`).
- Svaki red se deli na 5 child kolekcija (`students`, `digital_behavior`, `academic`,
  `wellbeing`, `economic`) sa `_id = student_id`.
- Dimenzija `countries` (~50) se dedupe-uje u memoriji i upisuje na kraju.
- Batch unos: `bulk_write([InsertOne...], ordered=False)` po 5.000 (`BATCH_SIZE`).
- **Ne kreira sekundarne indekse** (v1 = baseline za merenje).

Očekivano: `students`=500.000, ostale child kolekcije=500.000, `countries`≈50.
