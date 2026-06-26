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

## Napomena

CSV fajl sa podacima se ne dodaje na GitHub zbog veličine, već se čuva lokalno u folderu `data/`.
