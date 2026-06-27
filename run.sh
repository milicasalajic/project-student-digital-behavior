#!/usr/bin/env bash
# Reprodukcija celog projekta od nule (alternativa Makefile-u, npr. za Windows/Git-Bash).
set -euo pipefail
cd "$(dirname "$0")"

PY="${PY:-python}"

echo "==> 1/7 Pokretanje kontejnera (MongoDB + Metabase)"
docker compose up -d

echo "==> 2/7 Čekanje da MongoDB prihvati konekcije"
until docker exec sbp_mongodb mongosh --quiet --eval 'db.runCommand({ping:1}).ok' >/dev/null 2>&1; do
  sleep 2
done

echo "==> 3/7 Unos u sbp-v1 (normalizovano)"
$PY -m v1.scripts.load_v1

echo "==> 4/7 Izgradnja sbp-v2 (denormalizovano + Computed)"
$PY -m v2.scripts.build_v2

echo "==> 5/7 Kreiranje indeksa na sbp-v2"
$PY -m v2.scripts.indexes

echo "==> 6/7 Dijagrami uporedne analize (iz benchmarks/results.csv)"
$PY -m charts.make_charts

echo "==> 7/7 Materijalizacija rezultata za Metabase + slike rezultata"
docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js
$PY -m charts.make_query_docs

echo "Gotovo."
echo "Upiti: pokreni iz v{1,2}/{milica,ivan}/Upit* u mongosh/Compass."
echo "Metabase: http://localhost:3000 (vidi metabase/SETUP.md)"
