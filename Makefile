COMPOSE ?= docker compose
PY      ?= python

.PHONY: help up down load build indexes pipeline charts results images all clean

help:
	@echo "Ciljevi: up | load | build | indexes | bench | charts | results | all | down | clean"

up:        ## pokreni MongoDB + Metabase
	$(COMPOSE) up -d

down:      ## zaustavi kontejnere
	$(COMPOSE) down

load:      ## unos u sbp-v1 (normalizovano, 6 kolekcija)
	$(PY) -m v1.scripts.load_v1

build:     ## izgradnja sbp-v2 (denormalizovano + Computed)
	$(PY) -m v2.scripts.build_v2

indexes:   ## kreiranje indeksa na sbp-v2 (pymongo; mongosh nije obavezan)
	$(PY) -m v2.scripts.indexes

charts:    ## dijagrami uporedne analize -> charts/*.png (iz benchmarks/results.csv)
	$(PY) -m charts.make_charts

results:   ## materijalizacija rezultata za Metabase -> results_* kolekcije
	docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js

images:    ## per-upit dokumentacija -> v*/{milica,ivan}/Upit*/ (README + explain/index/output)
	$(PY) -m charts.make_query_docs

all: up load build indexes charts results images
	@echo "Gotovo. Upiti: pokreni iz v{1,2}/{milica,ivan}/Upit* u mongosh/Compass."
	@echo "Metabase: http://localhost:3000 (vidi metabase/SETUP.md)"

pipeline: load build indexes   ## ceo unos + optimizacija

clean:     ## obriši kontejnere I volumene (briše podatke u Mongo/Metabase)
	$(COMPOSE) down -v
