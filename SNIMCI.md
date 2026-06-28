# Snimci (screenshotovi) upita — ček-lista

Svaki upit ima folder `v{1,2}/{milica,ivan}/Upit{n}/` sa dve slike koje treba da budu
**ručni screenshotovi iz GUI-a** (MongoDB Compass). Trenutno su tu prazni *placeholder*
okviri — zameni ih svojim snimcima **pod istim imenom** (`explain.png`, `output.png`).

- `output.png` — screenshot **rezultata upita** (primer izlaznog dokumenta).
- `explain.png` — screenshot **Explain plana** (tu se vidi i COLLSCAN/IXSCAN + korišćeni indeks).

> `output.png` je **isti za v1 i v2** (isti podaci, isti rezultat) — snimi jednom i iskopiraj
> u oba foldera. `explain.png` se **razlikuje** (v1 = COLLSCAN/`$lookup`, v2 = IXSCAN/bez join-a).

## Kako se snima u Compass-u

1. Konekcija: `mongodb://localhost:27017`.
2. Izaberi bazu — **`sbp-v1`** (za v1 snimke) ili **`sbp-v2`** (za v2 snimke) — pa kolekciju.
3. Tab **Aggregations** → zalepi `aggregate([...])` pipeline iz `README.md` tog upita.
   - U opcijama uključi **Allow Disk Use** (grupisanja nad 500k inače pucaju).
   - Klikni **Run** → snimi rezultat → `output.png`.
4. Za explain: u istom tabu **Explain** (dugme/▸ „Explain Plan") → snimi → `explain.png`.
5. macOS snimak regiona: `Cmd`+`Shift`+`4`, pa prevuci preko prozora.

Dvostepeni upiti (savetnik **AA-3**): pokreni oba reda (`const prosek = ...` pa glavni
`aggregate`); za `output.png` snimi finalni rezultat, za `explain.png` snimi explain glavnog
(drugog) `aggregate`-a.

## Podela posla

**Milica — studentski psiholog (`milica/`)**

| Upit | v1 explain | v2 explain | rezultat (v1=v2) |
|---|---|---|---|
| PSY-1 starosne grupe → mentalno zdravlje | ☐ | ☐ | ☐ |
| PSY-2 dominantan sadržaj → brain rot | ☐ | ☐ | ☐ |
| PSY-3 >6h na mrežama → san/pažnja/produktivnost | ☐ | ☐ | ☐ |
| PSY-4 sajber nasilje → wellbeing | ☐ | ☐ | ☐ |
| PSY-5 zavisnost + nizak wellbeing + umereno korišćenje | ☐ | ☐ | ☐ |

**Ivan — akademski savetnik (`ivan/`)**

| Upit | v1 explain | v2 explain | rezultat (v1=v2) |
|---|---|---|---|
| AA-1 opseg sati na mrežama | ☐ | ☐ | ☐ |
| AA-2 visok rizik po polu × području | ☐ | ☐ | ☐ |
| AA-3 akademski rizik iznad proseka | ☐ | ☐ | ☐ |
| AA-4 sesija > pažnja → po sagorevanju | ☐ | ☐ | ☐ |
| AA-5 razvoj države × prihod porodice | ☐ | ☐ | ☐ |

Ukupno: **20 explain** (10 v1 + 10 v2) + **10 rezultat** snimaka (svaki rezultat ide u v1 i v2 folder).
