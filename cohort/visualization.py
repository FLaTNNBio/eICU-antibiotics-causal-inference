"""
visualization.py
Generazione dei grafici comparativi.
"""

import numpy as np
import matplotlib.pyplot as plt
from config import OUT_PNG, WINDOWS 


def plot_comparison(results):
    """
    Crea un grafico a 3 pannelli per confrontare le finestre di trattamento.
    """
    print("\n" + "=" * 60)
    print("STEP 5 — Figura comparativa 24h vs 12h")
    print("=" * 60)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Confronto coorti — Finestra 24h (analisi primaria) vs 12h (sensibilità)\n"
        "Studio: Antibiotici terapeutici precoci → Mortalità ospedaliera (eICU)\n"
        f"BASELINE: Solo covariate STATICHE (n={results['24h']['n_features']}) — Zero leakage garantito",
        fontsize=10, fontweight="bold"
    )

    colors = {"24h": "#2ecc71", "12h": "#9b59b6"}

    # Panel 1 — Distribuzione A
    ax = axes[0]
    labels = list(WINDOWS.keys())
    n_A1 = [results[w]["n_A1"] for w in labels]
    n_A0 = [results[w]["n_A0"] for w in labels]

    x = np.arange(len(labels))
    width = 0.35
    b1 = ax.bar(x - width/2, n_A0, width, label="A=0 (controlli)", color="#3498db", alpha=0.8)
    b2 = ax.bar(x + width/2, n_A1, width, label="A=1 (trattati)", color="#e74c3c", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Finestra {w}" for w in labels])
    ax.set_ylabel("N pazienti")
    ax.set_title("Distribuzione A per finestra", fontweight="bold")
    ax.legend()
    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{int(bar.get_height())}", ha="center", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel 2 — % Trattati
    ax2 = axes[1]
    pct_A1 = [results[w]["pct_A1"] for w in labels]
    bars2 = ax2.bar(labels, pct_A1,
                    color=[colors[w] for w in labels],
                    alpha=0.85, edgecolor="white", width=0.4)
    ax2.set_ylabel("% trattati (A=1)")
    ax2.set_title("Prevalenza trattamento\nper finestra", fontweight="bold")
    ax2.set_ylim(0, max(pct_A1) * 1.4)
    for bar, v in zip(bars2, pct_A1):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.3,
                 f"{v:.1f}%", ha="center", fontsize=11, fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Panel 3 — Mortalità grezza
    ax3 = axes[2]
    x_pos = np.arange(2)
    w_ = 0.3
    for i, (win_label, res) in enumerate(results.items()):
        offset = (i - 0.5) * w_
        bars3 = ax3.bar(x_pos + offset, [res["m0"], res["m1"]],
                        w_, label=f"Finestra {win_label}",
                        color=colors[win_label], alpha=0.8, edgecolor="white")
        for bar, v in zip(bars3, [res["m0"], res["m1"]]):
            ax3.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.2,
                     f"{v:.1f}%", ha="center", fontsize=8)

    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(["A=0 (controlli)", "A=1 (trattati)"])
    ax3.set_ylabel("Mortalità ospedaliera (%)")
    ax3.set_title("Mortalità grezza per gruppo\n(non causale — prima IPTW)", fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    plt.tight_layout()
    out_fig = f"{OUT_PNG}sensitivity_24h_vs_12h_STATIC_ONLY.png"
    plt.savefig(out_fig, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Figura salvata: {out_fig}")