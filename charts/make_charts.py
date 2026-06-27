#!/usr/bin/env python3
"""Generiše dijagrame uporedne analize performansi (v1 vs v2) iz benchmarks/results.csv.

Izlaz (charts/):
  - vrijeme_izvrsavanja.png : server vreme po upitu (log skala)
  - broj_dokumenata.png     : pregledani dokumenti po upitu (log skala)
  - ubrzanje.png            : faktor ubrzanja v1/v2 po upitu

Pokretanje:  python -m charts.make_charts
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.config import ROOT  # noqa: E402

AUTHOR_PREFIX = {"psiholog": "PSY", "savetnik": "AA"}


def _grouped_bar(pivot, ylabel, title, outfile, log=True):
    x = np.arange(len(pivot))
    w = 0.38
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(x - w / 2, pivot["v1"], w, label="v1 (normalizovana)", color="#c0504d")
    ax.bar(x + w / 2, pivot["v2"], w, label="v2 (denormalizovana + indeksi)", color="#4f81bd")
    if log:
        ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print("  ->", outfile)


def main():
    df = pd.read_csv(ROOT / "benchmarks" / "results.csv")
    df["q"] = df["author"].map(AUTHOR_PREFIX) + "-" + df["query_id"].str.replace("q", "", regex=False)

    pt = df.pivot(index="q", columns="version", values="server_time_ms").sort_index()
    pd_ = df.pivot(index="q", columns="version", values="docs_examined").sort_index()

    charts = ROOT / "charts"
    _grouped_bar(pt, "Server vreme (ms, log)", "Vreme izvršavanja upita: v1 vs v2",
                 charts / "vrijeme_izvrsavanja.png")
    _grouped_bar(pd_, "Pregledani dokumenti (log)", "Broj pregledanih dokumenata: v1 vs v2",
                 charts / "broj_dokumenata.png")

    # Faktor ubrzanja (zaštita od deljenja nulom)
    speed = (pt["v1"] / pt["v2"].replace(0, np.nan)).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(speed.index, speed.values, color="#9bbb59")
    ax.axhline(1.0, ls="--", c="gray")
    for i, v in enumerate(speed.values):
        if pd.notna(v):
            ax.text(i, v, f"{v:.0f}×", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Ubrzanje (v1 / v2)")
    ax.set_title("Faktor ubrzanja po upitu")
    plt.xticks(rotation=45, ha="right")
    ax.grid(axis="y", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(charts / "ubrzanje.png", dpi=150)
    plt.close(fig)
    print("  ->", charts / "ubrzanje.png")


if __name__ == "__main__":
    main()
