# Metabase

Metabase se koristi za vizualizaciju rezultata upita.

Pokreće se zajedno sa MongoDB bazom komandom:

```bash
docker compose up -d
```

Nakon pokretanja dostupan je na adresi:

```text
http://localhost:3000
```

Pri prvom pokretanju potrebno je napraviti admin nalog.

## Povezivanje baze

U Metabase-u se dodaje MongoDB baza `sbp-v2`.

Podešavanja za povezivanje su:

```text
Database type: MongoDB
Display name: sbp-v2
Host: mongodb
Port: 27017
Database name: sbp-v2
Authentication: bez autentifikacije
```

Host je `mongodb`, zato što se Metabase i MongoDB pokreću kao Docker kontejneri.

Nakon povezivanja baze potrebno je pokrenuti sinhronizaciju šeme.

## Priprema podataka za grafikone

Pre pravljenja grafikona pokreće se komanda:

```bash
docker exec -i sbp_mongodb mongosh sbp-v2 < metabase/write_results.js
```

Ova skripta izvršava upite nad bazom `sbp-v2` i rezultate upisuje u pomoćne kolekcije:

```text
results_psi_q1 ... results_psi_q5
results_sav_q1 ... results_sav_q5
```

Metabase zatim koristi ove kolekcije za prikaz grafikona.

## Dashboard

U Metabase-u je napravljen dashboard za prikaz rezultata upita.

Dashboard prikazuje rezultate upita za psihologa i akademskog savetnika, kao što su mentalno zdravlje po starosnim grupama, dominantan tip digitalnog sadržaja, wellbeing prema sajber nasilju i brain rot nivou, kao i akademski rizik po različitim grupama studenata.

Screenshot dashboard-a čuva se u folderu:

```text
metabase/screenshots/dashboard.png
```
