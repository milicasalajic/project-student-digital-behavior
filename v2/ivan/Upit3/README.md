# Upit 3 (optimizovan) - Izdvojiti studente sa akademskim rizikom iznad proseka; prikazati ukupan broj studenata, prosečan broj sati učenja, prosečan skor produktivnosti i prosečan broj sati na društvenim mrežama.

Kod upita:

~~~
// 1) prosečan akademski rizik
const prosek = db.students.aggregate([
  { $group: { _id: null, m: { $avg: "$academic_risk_score" } } }
]).toArray()[0].m;

// 2) studenti iznad proseka
db.students.aggregate([
  { $match: { academic_risk_score: { $gt: prosek } } },
  { $group: {
      _id: null,
      broj_studenata: { $sum: 1 },
      prosek_sati_ucenja: { $avg: "$study_hours_per_week" },
      prosek_produktivnost: { $avg: "$productivity_score" },
      prosek_sati_mreze: { $avg: "$social_media_hours" } } }
], { allowDiskUse: true })
~~~

Brzina izvršavanja: 376 ms

Rezultat Explain opcije:

![explain](./explain.png)

Primer izlaznog dokumenta:

![rezultat](./output.png)

Zaključak:
  • Filter `academic_risk_score > prosek` koristi indeks (`IXSCAN`), uz uklonjen join. Ubrzanje je umereno (~1.4×) jer je i v1 bio relativno brz — usko grlo ovde nije izraženo.
