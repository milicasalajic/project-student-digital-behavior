# Upit 2 - Procenat „visokorizičnih“ studenata (digital_addiction_score ≥ 25) po polu i tipu područja, i njihov prosečan nivo stresa.

Kod upita:

~~~
db.wellbeing.aggregate([
  { $lookup: { from: "students", localField: "_id", foreignField: "_id", as: "s" } },
  { $unwind: "$s" },
  { $addFields: { high_risk: { $gte: ["$digital_addiction_score", 25] } } },
  { $group: {
      _id: { pol: "$s.gender", podrucje: "$s.urban_rural" },
      ukupno: { $sum: 1 },
      visokorizicni: { $sum: { $cond: ["$high_risk", 1, 0] } },
      suma_stres_hr: { $sum: { $cond: ["$high_risk", "$stress_level", 0] } } } },
  { $addFields: {
      procenat_visokorizicnih: { $multiply: [{ $divide: ["$visokorizicni", "$ukupno"] }, 100] },
      prosek_stres_visokorizicni: { $cond: [
        { $gt: ["$visokorizicni", 0] },
        { $divide: ["$suma_stres_hr", "$visokorizicni"] },
        null ] } } },
  { $project: { suma_stres_hr: 0 } },
  { $sort: { procenat_visokorizicnih: -1 } }
], { allowDiskUse: true })
~~~

Brzina izvršavanja: 5365 ms

Rezultat Explain opcije:

![explain](./explain.png)

Primer izlaznog dokumenta:

![rezultat](./output.png)
