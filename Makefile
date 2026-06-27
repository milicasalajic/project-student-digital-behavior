COMPOSE ?= docker compose
PY      ?= python

.PHONY: help up down load build indexes pipeline bench charts results all clean

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

bench:     ## merenje performansi -> benchmarks/results.csv
	$(PY) -m benchmarks.benchmark

charts:    ## dijagrami uporedne analize -> charts/*.png
	$(PY) -m charts.make_charts

results:   ## materijalizacija rezultata za Metabase -> results_* kolekcije
	$(PY) -m metabase.write_results

pipeline: load build indexes   ## ceo unos + optimizacija

all: up load build indexes bench charts results
	@echo "Gotovo. Metabase: http://localhost:3000 (vidi metabase/SETUP.md)"

clean:     ## obriši kontejnere I volumene (briše podatke u Mongo/Metabase)
	$(COMPOSE) down -v
