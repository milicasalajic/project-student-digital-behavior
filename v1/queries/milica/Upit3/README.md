# Upit 3 - Prikazati broj studenata koji koriste društvene mreže više od 6 sati dnevno, i za tu grupu prosečan broj sati sna, prosečan raspon pažnje i prosečan skor produktivnosti.

Kod upita:

```
db.digital_behavior.aggregate([
  { $match: { social_media_hours: { $gt: 6 } } },
  { $lookup: { from: "wellbeing", localField: "_id", foreignField: "_id", as: "w" } },
  { $unwind: "$w" },
  { $lookup: { from: "academic", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_san: { $avg: "$w.sleep_hours" },
      prosek_paznja: { $avg: "$a.attention_span_minutes" },
      prosek_produktivnost: { $avg: "$a.productivity_score" } } },
  { $project: {
      _id: 0,
      broj_studenata: 1,
      prosek_san: { $round: ["$prosek_san", 2] },
      prosek_paznja: { $round: ["$prosek_paznja", 2] },
      prosek_produktivnost: { $round: ["$prosek_produktivnost", 2] } } }
], { allowDiskUse: true })
```

Brzina izvršavanja: 388 ms

Rezultat Explain opcije:

![explain](./explain.png)

Primer izlaznog dokumenta:

![rezultat](./output.png)
