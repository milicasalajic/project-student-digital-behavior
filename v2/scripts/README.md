# v2 — izgradnja i indeksi

## 1. Izgradnja denormalizovane baze
```bash
python -m v2.scripts.build_v2          # -> sbp-v2.students (denormalizovano + Computed)
```
`build_v2.py` ponovo čita CSV i gradi jednu kolekciju `students`:
- sva polja inline + `development_level` (Extended Reference),
- poddokument `derived` (Computed, iz `common.derived.derive`),
- `schema_version: 2`,
- **Subset**: ekonomska polja i nekorišćene infrastrukturne kolone se izostavljaju.

> Computed polja se računaju u Python-u (čitljivije/pouzdanije nego u pipeline-u).
> Alternativa u Mongo-u: `transform_v1_to_v2.js` (`$lookup` + `$addFields` + `$merge`).

## 2. Indeksi (faza optimizacije)
```bash
python -m v2.scripts.indexes                                  # pymongo (preporučeno)
# ili, ako postoji mongosh u kontejneru:
docker exec -i sbp_mongodb mongosh sbp-v2 < v2/scripts/indexes.js
```
Po jedan indeks za grupisanje/filtriranje svakog od 10 upita (vidi `indexes.py`).

## 3. Alternativni put (in-Mongo transformacija)
```bash
docker exec -i sbp_mongodb mongosh sbp-v1 < v2/scripts/transform_v1_to_v2.js
```
Gradi `sbp-v2.students` iz `sbp-v1` spajanjem 6 kolekcija — ekvivalent `build_v2.py`,
ostavljen kao demonstracija `$lookup`/`$merge`/`allowDiskUse`.
