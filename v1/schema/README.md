# v1 — Normalizovana šema baze

U prvoj verziji baza je napravljena normalizovano. Podaci nisu čuvani u jednoj kolekciji, već su podeljeni u više kolekcija koje su povezane preko `student_id`.

Ova verzija služi da se vidi kako se upiti ponašaju kada podaci nisu denormalizovani i kada je za neke upite potrebno spajanje kolekcija pomoću `$lookup`.

U bazi postoji 6 kolekcija:

- `countries` — čuva podatke o državama, kao što su nivo razvijenosti, stopa siromaštva i internet infrastruktura.
- `students` — čuva osnovne podatke o studentima, na primer godine, pol, državu, obrazovanje, oblast studiranja i slično.
- `digital_behavior` — čuva podatke o digitalnom ponašanju studenata, kao što su sati korišćenja interneta, društvenih mreža, online učenja i kasno korišćenje uređaja.
- `academic` — čuva podatke vezane za učenje, motivaciju, pažnju, prisustvo nastavi i akademski rizik.
- `wellbeing` — čuva podatke o spavanju, stresu, anksioznosti, depresiji, digitalnoj zavisnosti i opštem blagostanju.
- `economic` — čuva ekonomske podatke, kao što su oglasi, klikovi, impulsivna kupovina i digitalna potrošnja.

Primer dokumenta iz kolekcije `students`:

```json
{
  "_id": 1,
  "country": "Qatar",
  "age": 21,
  "gender": "Male",
  "urban_rural": "Rural",
  "family_income_level": "High",
  "device_access": "Smartphone",
  "education_level": "Graduate",
  "field_of_study": "Business"
}
```

Primer dokumenta iz kolekcije `countries`:

```json
{
  "_id": "Qatar",
  "development_level": "Developing",
  "poverty_rate_percent": 16.3,
  "internet_infrastructure_index": 54.93,
  "average_internet_speed_mbps": 27.19
}
```

Sekundarni indeksi nisu dodavani u ovoj verziji. Korišćeni su samo podrazumevani indeksi nad `_id` poljem. Zbog toga se filtriranje po drugim poljima uglavnom izvršava skeniranjem cele kolekcije.

Kolekcija `economic` postoji u ovoj verziji zato što pripada originalnoj strukturi podataka, ali se ne koristi u analiziranim upitima. Zbog toga se u drugoj verziji baze ta polja ne prebacuju u glavnu kolekciju.

Skripte za unos podataka nalaze se u direktorijumu:

```text
../scripts/
```

Upiti se nalaze u direktorijumima:

```text
../milica
../ivan
```
