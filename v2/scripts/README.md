# v2 — izgradnja i indeksi

## 1. Izgradnja denormalizovane baze

```bash
python -m v2.scripts.build_v2          # -> sbp-v2.students (denormalizovano + Computed)
```

`build_v2.py` ponovo čita CSV i gradi jednu kolekciju `students`:

- sva polja inline + `development_level`,
- poddokument `derived` (izvedena polja, iz `common.derived.derive`),
- `schema_version: 2`,
- ekonomska polja i nekorišćene infrastrukturne kolone se izostavljaju.

## 2. Indeksi

```bash
python -m v2.scripts.indexes                                  # pymongo (preporučeno)
# ili, ako postoji mongosh u kontejneru:
docker exec -i sbp_mongodb mongosh sbp-v2 < v2/scripts/indexes.js
```

Po jedan indeks za grupisanje/filtriranje svakog od 10 upita (vidi `indexes.py`).
