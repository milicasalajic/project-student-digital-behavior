# Upit 3 (optimizovan) - Prikazati broj studenata koji koriste društvene mreže više od 6 sati dnevno, i za tu grupu prosečan broj sati sna, prosečan raspon pažnje i prosečan skor produktivnosti.

Kod upita:

```
db.students.aggregate([
  { $match: { "derived.social_gt6": true } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_san: { $avg: "$sleep_hours" },
      prosek_paznja: { $avg: "$attention_span_minutes" },
      prosek_produktivnost: { $avg: "$productivity_score" } } },
  { $project: {
      _id: 0,
      broj_studenata: 1,
      prosek_san: { $round: ["$prosek_san", 2] },
      prosek_paznja: { $round: ["$prosek_paznja", 2] },
      prosek_produktivnost: { $round: ["$prosek_produktivnost", 2] } } }
], { allowDiskUse: true })
```

Brzina izvršavanja: 17 ms

Rezultat Explain opcije:

![explain](./explain.png)

Primer izlaznog dokumenta:

![rezultat](./output.png)

Zaključak:
• Selektivan `$match` (`derived.social_gt6`) koristi indeks → `IXSCAN` umesto punog pregleda, uz uklonjena 2 join-a. Vreme padá ~23× (388→17 ms).
