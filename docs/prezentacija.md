# Prezentacija (skelet slajdova) — odbrana projekta

> Outline za izradu slajdova (PPTX/Google Slides). Po slajd = jedna ideja + vizual.

1. **Naslovna** — Analiza digitalnog ponašanja studenata · SBP · autori · MongoDB.
2. **Problem i cilj** — 500k studenata, pitanja psihologa i savetnika; cilj: brzi
   analitički upiti + demonstracija optimizacije šeme.
3. **Skup podataka** — 48 kolona, ~50 zemalja; ključne mere (zavisnost, wellbeing,
   brain rot, akademski rizik); čišćenje (bool, null, percentilni pragovi).
4. **v1 — normalizovana šema** — dijagram 6 kolekcija + veze preko `student_id`;
   poruka: realna normalizacija → upiti moraju `$lookup`.
5. **Unos podataka** — `load_v1.py`: streaming, tipizacija, batch; idempotentnost.
6. **10 upita** — kratak pregled (5 psiholog + 5 savetnik); istaći 2-3 najsloženija
   (AA-4 poređenje sesije/pažnje, AA-5 kombinovana grupa, PSY-5 višestruki filter).
7. **Uska grla** — `explain executionStats`: COLLSCAN + cena `$lookup` join-ova;
   primer plana izvršavanja za AA-5 (4 kolekcije).
8. **v2 — denormalizovana šema** — jedna kolekcija + `derived` polja + indeksi.
9. **Design paterni** — Computed, Extended Reference, Schema Versioning, Subset
   (primenjeni); kratko zašto Tree/Polymorphic/Document Versioning/Outlier nisu.
10. **Indeksiranje** — po jedan indeks po upitu; IXSCAN vs COLLSCAN (keys_examined).
11. **Prerada upita** — isti rezultat, bez `$lookup`-a (provera konzistentnosti: SVE ISPRAVNO).
12. **Rezultati performansi** — grafik `vrijeme_izvrsavanja.png` (AA-5 23×, AA-4 36×, PSY-1 20×).
13. **Pregledani dokumenti** — grafik `broj_dokumenata.png` (PSY-3 528k→14k, PSY-5 574k→11k).
14. **Iskrena analiza** — gde denormalizacija NE pomaže (PSY-2, PSY-4 neznatno sporiji;
    AA-3 isti) → ciljana, ne univerzalna optimizacija.
15. **Vizualizacija (Metabase)** — screenshot dashboard-a (rezultati upita).
16. **Zaključak** — kompromisi denormalizacije; kada se isplati; mogući dalji koraci
    (Attribute pattern za sadržaj, particionисање).
