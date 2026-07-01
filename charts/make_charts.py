import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common.config import ROOT

RESULTS = [
    ("PSY-1", "v1", 10256, 1500002),
    ("PSY-1", "v2", 502, 500000),
    ("PSY-2", "v1", 379, 500000),
    ("PSY-2", "v2", 442, 500000),
    ("PSY-3", "v1", 388, 528208),
    ("PSY-3", "v2", 17, 14103),
    ("PSY-4", "v1", 278, 500000),
    ("PSY-4", "v2", 410, 500000),
    ("PSY-5", "v1", 1013, 573650),
    ("PSY-5", "v2", 81, 10690),
    ("AA-1", "v1", 5015, 1000001),
    ("AA-1", "v2", 565, 500000),
    ("AA-2", "v1", 5365, 1000001),
    ("AA-2", "v2", 529, 500000),
    ("AA-3", "v1", 522, 1016392),
    ("AA-3", "v2", 376, 516391),
    ("AA-4", "v1", 5534, 1000001),
    ("AA-4", "v2", 153, 90432),
    ("AA-5", "v1", 15394, 2000003),
    ("AA-5", "v2", 669, 500000),
]


def _series(field_index):
    labels = sorted({r[0] for r in RESULTS})
    v1 = {r[0]: r[field_index] for r in RESULTS if r[1] == "v1"}
    v2 = {r[0]: r[field_index] for r in RESULTS if r[1] == "v2"}
    return labels, [v1[l] for l in labels], [v2[l] for l in labels]


def _grouped_bar(labels, v1, v2, ylabel, title, outfile):
    x = np.arange(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(x - w / 2, v1, w, label="v1 (normalizovana)", color="#c0504d")
    ax.bar(x + w / 2, v2, w, label="v2 (denormalizovana + indeksi)", color="#4f81bd")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print("  ->", outfile)


def main():
    charts = ROOT / "charts"

    labels, t1, t2 = _series(2)
    _grouped_bar(labels, t1, t2, "Server vreme (ms, log)",
                 "Vreme izvršavanja upita: v1 vs v2", charts / "vreme_izvrsavanja.png")

    labels, d1, d2 = _series(3)
    _grouped_bar(labels, d1, d2, "Pregledani dokumenti (log)",
                 "Broj pregledanih dokumenata: v1 vs v2", charts / "broj_dokumenata.png")

    labels, t1, t2 = _series(2)
    speed = [(l, a / b) for l, a, b in zip(labels, t1, t2) if b]
    speed.sort(key=lambda p: p[1], reverse=True)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar([p[0] for p in speed], [p[1] for p in speed], color="#9bbb59")
    ax.axhline(1.0, ls="--", c="gray")
    for i, (_, v) in enumerate(speed):
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
