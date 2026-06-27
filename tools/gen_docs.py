#!/usr/bin/env python3
"""Generiše README za upite (v1 i v2, psiholog i savetnik) iz builder-a.

Time su prikazani pipeline-ovi uvek usklađeni sa kodom u `queries/`. Ako postoji
`benchmarks/results.csv`, u naslove se dodaju izmereno vreme i broj dokumenata.

Pokretanje:  python -m tools.gen_docs
"""
import csv
import json

from common.config import ROOT
from queries import SUITES

AUTHOR_TITLE = {"psiholog": "Studentski psiholog", "savetnik": "Akademski savetnik"}


def load_times():
    p = ROOT / "benchmarks" / "results.csv"
    out = {}
    if p.exists():
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                out[(r["author"], r["query_id"], r["version"])] = r
    return out


def main():
    times = load_times()
    for version in ("v1", "v2"):
        for author, suite in SUITES.items():
            lines = [f"# Upiti — {AUTHOR_TITLE[author]} ({version})\n",
                     "_Generisano iz `queries/` (tools/gen_docs.py)._\n"]
            for qid, builder in suite.items():
                coll, pipe = builder(version)
                desc = (builder.__doc__ or "").strip()
                t = times.get((author, qid, version))
                head = f"## {qid.upper()}"
                if t and t["server_time_ms"] not in (None, "", "None"):
                    head += f" — {float(t['server_time_ms']):.0f} ms"
                lines.append(head + "\n")
                lines.append(desc + "\n")
                lines.append(f"Kolekcija: `{coll}`\n")
                lines.append("```javascript")
                lines.append(f"db.{coll}.aggregate(")
                lines.append(json.dumps(pipe, ensure_ascii=False, indent=2))
                lines.append(", { allowDiskUse: true })")
                lines.append("```")
                if t:
                    lines.append(
                        f"\n_Pregledani dokumenti: {int(t['docs_examined']):,} · "
                        f"vraćeno grupa: {t['n_returned']}_\n")
                lines.append("")
            path = ROOT / version / "queries" / author / "README.md"
            path.write_text("\n".join(lines), encoding="utf-8")
            print("napisano:", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
