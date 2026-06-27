#!/usr/bin/env python3
"""Generiše slike rezultata (tabele) za svaki upit iz `results_*` kolekcija.

Tako se u query README-ovima (`v{1,2}/queries/{psiholog,savetnik}/qN.png`) prikazuju
stvarni rezultati. (Po želji se mogu zameniti screenshotovima iz Compass-a.)
v1 i v2 daju iste rezultate, pa se ista slika upisuje u oba foldera.

Preduslov: pokrenut `metabase/write_results.js` (popunjava results_* u sbp-v2).
Pokretanje:  python -m charts.make_result_images
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from pymongo import MongoClient  # noqa: E402

from common.config import DB_V2, MONGO_URI, ROOT  # noqa: E402

TITLES = {
    ("psiholog", "q1"): "PSY-1 · starosne grupe → mentalno zdravlje",
    ("psiholog", "q2"): "PSY-2 · dominantan sadržaj → brain rot",
    ("psiholog", "q3"): "PSY-3 · >6h na mrežama → san/pažnja/produktivnost",
    ("psiholog", "q4"): "PSY-4 · sajber nasilje → wellbeing",
    ("psiholog", "q5"): "PSY-5 · zavisnost+nizak wellbeing+umereno korišćenje",
    ("savetnik", "q1"): "AA-1 · opseg sati na mrežama",
    ("savetnik", "q2"): "AA-2 · visok rizik po polu × području",
    ("savetnik", "q3"): "AA-3 · akademski rizik iznad proseka",
    ("savetnik", "q4"): "AA-4 · sesija>pažnja → po sagorevanju",
    ("savetnik", "q5"): "AA-5 · razvoj države × prihod porodice",
}
PREFIX = {"psiholog": "psi", "savetnik": "sav"}


def fmt(v):
    if isinstance(v, bool):
        return "Da" if v else "Ne"
    if isinstance(v, float):
        return f"{v:.2f}"
    if v is None:
        return "—"
    if isinstance(v, dict):
        return ", ".join(f"{k}={fmt(x)}" for k, x in v.items())
    return str(v)


def render(rows, title, outpaths):
    cols = list(rows[0].keys())
    labels = ["grupa" if c == "_id" else c for c in cols]
    cell = [[fmt(r.get(c)) for c in cols] for r in rows]
    fig, ax = plt.subplots(figsize=(min(2.2 + 2.0 * len(cols), 18), 1.1 + 0.55 * len(rows)))
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=12)
    t = ax.table(cellText=cell, colLabels=labels, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.5)
    for j in range(len(cols)):
        h = t[0, j]
        h.set_facecolor("#4f81bd")
        h.set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):  # zebra
        if i % 2 == 0:
            for j in range(len(cols)):
                t[i, j].set_facecolor("#eef3fa")
    fig.tight_layout()
    for p in outpaths:
        fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    db = MongoClient(MONGO_URI)[DB_V2]
    for (role, qid), title in TITLES.items():
        coll = f"results_{PREFIX[role]}_{qid}"
        rows = list(db[coll].find())
        if not rows:
            print(f"  ! prazno: {coll} (pokreni metabase/write_results.js)")
            continue
        rows.sort(key=lambda r: (-(r.get("broj_studenata") or r.get("ukupno") or 0), str(r.get("_id"))))
        out = [ROOT / v / "queries" / role / f"{qid}.png" for v in ("v1", "v2")]
        render(rows, title, out)
        print(f"  {coll} -> {role}/{qid}.png ({len(rows)} redova)")


if __name__ == "__main__":
    main()
