"""Phase 3.4 Plan 03: emit all 5 PNG figures for the Phase 3 writeup.

Figures emitted (per CONTEXT D-03/D-04/D-05/D-06/D-12):
  fig1_arms_race.png         -- D-03 grouped bar (6 tiers x 5 defenses = 30 bars)
  fig2_utility_security.png  -- D-04 two-panel ASR-vs-retrieval-rate
  fig3_loo_causal.png        -- D-05 two-panel ROC + scatter (AUC=0.372/0.410)
  fig4_ratio_sweep.png       -- D-06 line plot with log x-scale
  fig5_cross_model_heatmap.png -- D-12 5x3 heatmap (viridis_r)

All figures use Pattern 1 deterministic setup: np.random.seed(0), Agg backend,
dpi=150, constrained_layout, tableau-colorblind10 palette.

Atomic save: each PNG written to {path}.tmp then os.replace'd to final name.
Idempotent: re-running overwrites existing PNGs.

Defense column labels mirror DEFENSE_DISPLAY in scripts/make_results.py
(single source of truth per T-3.4-W1-05). The 5 canonical writeup-order
labels are:
    ["No Defense", "BERT alone", "Fused", "DEF-02", "Adaptive vs Fused"]
"""
from __future__ import annotations

# CRITICAL -- Pattern 1 setup MUST be at module top, BEFORE any pyplot import elsewhere
import os
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

np.random.seed(0)
plt.rcParams["savefig.dpi"] = 150
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["figure.constrained_layout.use"] = True
plt.style.use("tableau-colorblind10")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.metrics import roc_curve, roc_auc_score  # noqa: E402


# --------------------------------------------------------------------------- #
# DEFENSE_DISPLAY mirror (T-3.4-W1-05).                                       #
# Mirrors scripts/make_results.py DEFENSE_DISPLAY -- single source of truth   #
# for defense column / legend labels. If make_results.py is updated, update   #
# this dict in lockstep.                                                       #
# --------------------------------------------------------------------------- #
DEFENSE_DISPLAY: dict[str, str] = {
    # Top-level ablation_table.json keys
    "no_defense":                  "No Defense",
    "def02":                       "DEF-02",
    "bert_only":                   "BERT alone",
    "perplexity_only":             "Perplexity",
    "imperative_only":             "Imperative",
    "fingerprint_only":            "Fingerprint",
    "fused_fixed_0.5":             "Fused",
    "fused_tuned_threshold":       "Fused (tuned)",
    "atk08_vs_fused_llama":        "Adaptive vs Fused",
    # Inner defense_mode short-names + matrix _summary.json defense field
    "off":                         "No Defense",
    "fused":                       "Fused",
    "bert":                        "BERT alone",
    "perplexity":                  "Perplexity",
    "imperative":                  "Imperative",
    "fingerprint":                 "Fingerprint",
}

# Canonical writeup order for D-03 5-defense legend
D03_DEFENSE_ORDER = ["No Defense", "BERT alone", "Fused", "DEF-02", "Adaptive vs Fused"]


# --------------------------------------------------------------------------- #
# Atomic save helper (PATTERNS.md / RESEARCH "Atomic write idiom for PNGs")   #
# --------------------------------------------------------------------------- #
def save_atomic(fig, final_path: str) -> None:
    """Save figure to .tmp then atomically rename. Closes the figure after.

    os.replace is atomic on POSIX and Windows when src/dst are in the same
    directory; partial .tmp files are never visible to downstream consumers.
    """
    tmp_path = final_path + ".tmp"
    # Pass format="png" explicitly because matplotlib otherwise infers format
    # from the file extension and the .tmp suffix is unsupported.
    fig.savefig(tmp_path, bbox_inches="tight", dpi=150, format="png")
    plt.close(fig)
    os.replace(tmp_path, final_path)


# --------------------------------------------------------------------------- #
# Figure 1 -- D-03 arms race grouped bar (6 tiers x 5 defenses = 30 bars)     #
# B-2 fix: explicit cell-by-cell population from real JSON; non-zero asserts. #
# --------------------------------------------------------------------------- #
def render_d03_arms_race(logs_dir: Path, output_dir: Path) -> None:
    """6 tier categories x 5 defense levels = 30 bars per CONTEXT D-03 amendment.

    EXPLICIT cell-by-cell population (B-2 fix). Reads ablation_table.json,
    eval_matrix/_summary.json, adaptive_fused_llama_s1.json,
    adaptive_nodefense_llama.json. Asserts non-zero invariants before save.
    """
    tiers = ["T1", "T1b", "T2", "T3", "T4", "Adaptive"]
    defenses = D03_DEFENSE_ORDER  # ["No Defense", "BERT alone", "Fused", "DEF-02", "Adaptive vs Fused"]

    # Load all sources defensively
    ablation = json.loads((logs_dir / "ablation_table.json").read_text(encoding="utf-8"))
    matrix = json.loads((logs_dir / "eval_matrix" / "_summary.json").read_text(encoding="utf-8"))
    matrix_df = pd.DataFrame(matrix)

    adaptive_fused: dict = {}
    p = logs_dir / "adaptive_fused_llama_s1.json"
    if p.exists():
        adaptive_fused = json.loads(p.read_text(encoding="utf-8")).get("aggregate", {})

    adaptive_nd: dict = {}
    p = logs_dir / "adaptive_nodefense_llama.json"
    if p.exists():
        adaptive_nd = json.loads(p.read_text(encoding="utf-8")).get("aggregate", {})

    # Helper: pull a single cell from the _summary.json matrix (model, defense, tier)
    def _matrix_cell(model: str, defense: str, tier: str) -> float:
        sub = matrix_df[
            (matrix_df["model"] == model)
            & (matrix_df["defense"] == defense)
            & (matrix_df["tier"] == tier)
        ]
        if sub.empty:
            return float("nan")
        return float(sub.iloc[0].get("asr_overall", float("nan")))

    # Defense -> ablation_table.json key mapping (raw keys verified 2026-04-28)
    nd = ablation.get("no_defense", {})
    bo = ablation.get("bert_only", {})
    fu = ablation.get("fused_fixed_0.5", {})
    d2 = ablation.get("def02", {})
    a8 = ablation.get("atk08_vs_fused_llama", {})

    NAN = float("nan")
    data = np.array(
        [
            # No Defense | BERT alone | Fused | DEF-02 | Adaptive vs Fused
            # row 0 -- T1 (from ablation.asr_t1)
            [nd.get("asr_t1", NAN), bo.get("asr_t1", NAN), fu.get("asr_t1", NAN), d2.get("asr_t1", NAN), NAN],
            # row 1 -- T1b (from _summary.json; BERT-alone + Adaptive-vs-Fused not measured)
            [
                _matrix_cell("llama3.2_3b", "no_defense", "tier1b"),
                NAN,
                _matrix_cell("llama3.2_3b", "fused", "tier1b"),
                _matrix_cell("llama3.2_3b", "def02", "tier1b"),
                NAN,
            ],
            # row 2 -- T2
            [nd.get("asr_t2", NAN), bo.get("asr_t2", NAN), fu.get("asr_t2", NAN), d2.get("asr_t2", NAN), NAN],
            # row 3 -- T3
            [nd.get("asr_t3", NAN), bo.get("asr_t3", NAN), fu.get("asr_t3", NAN), d2.get("asr_t3", NAN), NAN],
            # row 4 -- T4
            [nd.get("asr_t4", NAN), bo.get("asr_t4", NAN), fu.get("asr_t4", NAN), d2.get("asr_t4", NAN), NAN],
            # row 5 -- Adaptive
            [
                adaptive_nd.get("paired_asr_adaptive", adaptive_nd.get("asr_adaptive", 0.0)),
                NAN,
                adaptive_fused.get("paired_asr_adaptive", adaptive_fused.get("asr_adaptive", 0.0)),
                NAN,
                a8.get("asr_adaptive", NAN),
            ],
        ],
        dtype=float,
    )

    # B-2 invariant assertions -- fail loud if all-zero placeholder regression returns
    nonzero_count = int(np.sum((~np.isnan(data)) & (data > 1e-6)))
    assert np.nansum(data) > 0, (
        f"D-03 data matrix is all-zero or all-NaN -- refusing to render a meaningless "
        f"figure. Check ablation_table.json + _summary.json paths and key strings. "
        f"data=\n{data}"
    )
    assert np.nanmax(data) > 0.05, (
        f"D-03 data matrix has no measurable bar heights (max={np.nanmax(data):.4f}); "
        f"the figure would be visually empty. data=\n{data}"
    )
    assert nonzero_count >= 5, (
        f"D-03 data matrix has only {nonzero_count} non-zero cells; expected >= 5 "
        f"(catches accidentally setting only one cell). data=\n{data}"
    )

    # Render -- replace NaN with 0 (NaN bars draw as zero-height = "not measured").
    data_for_plot = np.where(np.isnan(data), 0.0, data)

    fig, ax = plt.subplots(figsize=(11, 5))
    width = 0.16
    x = np.arange(len(tiers))
    cmap_colors = plt.get_cmap("tab10").colors[:5]
    for i, (defense, color) in enumerate(zip(defenses, cmap_colors)):
        offset = (i - 2) * width
        ax.bar(x + offset, data_for_plot[:, i], width, label=defense, color=color)
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel("Paired / overall ASR")
    ax.set_xlabel("Attack tier")
    ax.set_title("D-03: Arms Race -- Attack Tier x Defense Level (llama3.2:3b)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    ax.set_ylim(0, max(0.5, float(np.nanmax(data)) * 1.2))
    ax.grid(True, axis="y", alpha=0.3)
    save_atomic(fig, str(output_dir / "fig1_arms_race.png"))


# --------------------------------------------------------------------------- #
# Figure 2 -- D-04 two-panel utility-security tradeoff                         #
# --------------------------------------------------------------------------- #
def render_d04_utility_security(logs_dir: Path, output_dir: Path) -> None:
    """Two-panel: (a) llama 7-defense ablation; (b) cross-LLM 3-defense.

    Panel (a) y-axis 0..0.45 (T2 ASR range); panel (b) y-axis 0..0.10 (mean ASR).
    Independent y-axes per RESEARCH discretion.
    """
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Panel (a): scatter for llama 7-defense ablation
    ablation = json.loads((logs_dir / "ablation_table.json").read_text(encoding="utf-8"))
    DEFENSE_KEYS_A = [
        "no_defense", "def02", "bert_only", "perplexity_only",
        "imperative_only", "fingerprint_only", "fused_fixed_0.5",
    ]
    palette_a = plt.get_cmap("tab10").colors
    for idx, key in enumerate(DEFENSE_KEYS_A):
        entry = ablation.get(key, {})
        if not entry:
            continue
        x = entry.get("retrieval_rate", 0.0)
        y = entry.get("asr_t2", 0.0)  # T2 most discriminating per Phase 3.1
        label = DEFENSE_DISPLAY.get(key, key)
        ax_a.scatter(x, y, s=120, color=palette_a[idx % len(palette_a)], label=label, edgecolor="black", linewidth=0.5)
        ax_a.annotate(label, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=8)
    ax_a.set_xlabel("Retrieval rate (poisoned chunks reaching LLM)")
    ax_a.set_ylabel("Paired ASR (T2)")
    ax_a.set_title("(a) llama3.2:3b -- 7 defense modes (D-04a)")
    ax_a.grid(True, alpha=0.3)
    ax_a.legend(loc="best", fontsize=7)

    # Panel (b): scatter from _summary.json (3 LLMs x 3 defenses)
    matrix_df = pd.DataFrame(
        json.loads((logs_dir / "eval_matrix" / "_summary.json").read_text(encoding="utf-8"))
    )
    # Aggregate per (model, defense) by averaging across tiers -- single point per cell
    agg = (
        matrix_df.groupby(["model", "defense"])
        .agg(asr=("asr_overall", "mean"), rr=("retrieval_rate", "mean"))
        .reset_index()
    )
    markers = {"no_defense": "o", "fused": "s", "def02": "^"}
    palette_b = {"llama3.2_3b": "#0072B2", "mistral_7b": "#D55E00", "gemma4_31b-cloud": "#009E73"}
    for model in agg["model"].unique():
        sub = agg[agg["model"] == model]
        for _, row in sub.iterrows():
            ax_b.scatter(
                row["rr"], row["asr"],
                s=140, marker=markers.get(row["defense"], "o"),
                color=palette_b.get(model, "gray"),
                edgecolor="black", linewidth=0.5,
                label=f"{model} / {row['defense']}",
            )
    ax_b.set_xlabel("Retrieval rate (mean across tiers)")
    ax_b.set_ylabel("Mean overall ASR (across 5 tiers)")
    ax_b.set_title("(b) 3 LLMs x 3 defenses (D-04b)")
    # De-dupe legend entries
    handles, labels = ax_b.get_legend_handles_labels()
    seen = {}
    for h, lab in zip(handles, labels):
        if lab not in seen:
            seen[lab] = h
    ax_b.legend(seen.values(), seen.keys(), loc="best", fontsize=6)
    ax_b.grid(True, alpha=0.3)
    save_atomic(fig, str(output_dir / "fig2_utility_security.png"))


# --------------------------------------------------------------------------- #
# Figure 3 -- D-05 two-panel LOO causal attribution (negative result)          #
# --------------------------------------------------------------------------- #
def render_d05_loo_causal(logs_dir: Path, output_dir: Path) -> None:
    """Two-panel: (a) ROC (inverted, AUC<0.5) + (b) influence-vs-cleanliness scatter.

    Per CONTEXT D-05: 'Inverted AUC = 0.372 (llama) / 0.410 (mistral)' annotation
    on panel (a). Panel (b) visualizes that injected chunks fall in LOW-influence
    region while clean chunks fall in HIGH-influence region.
    """
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel (a): ROC for both models (both below diagonal)
    auc_values: dict[str, float] = {}
    for model_key, label, color in [
        ("llama", "llama3.2:3b", "#D55E00"),
        ("mistral", "mistral:7b", "#0072B2"),
    ]:
        loo = json.loads(
            (logs_dir / f"loo_results_{model_key}.json").read_text(encoding="utf-8")
        )
        y_true: list[int] = []
        y_score: list[int] = []
        for q in loo.get("results", []):
            for ch in q.get("chunk_results", []):
                y_true.append(int(bool(ch.get("is_injected", 0))))
                y_score.append(int(bool(ch.get("diverged", 0))))
        if not y_true or len(set(y_true)) < 2:
            continue
        fpr_v, tpr_v, _ = roc_curve(y_true, y_score)
        auc = float(roc_auc_score(y_true, y_score))
        auc_values[model_key] = auc
        ax_a.plot(fpr_v, tpr_v, color=color, linewidth=2,
                  marker="o", markersize=6,
                  label=f"{label} (AUC={auc:.3f})")
    ax_a.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random (AUC=0.500)")
    ax_a.set_xlabel("False positive rate")
    ax_a.set_ylabel("True positive rate")
    auc_llama = auc_values.get("llama", 0.372)
    auc_mistral = auc_values.get("mistral", 0.410)
    ax_a.set_title(
        f"(a) LOO influence ROC -- Inverted AUC = {auc_llama:.3f} / {auc_mistral:.3f}"
    )
    ax_a.legend(loc="lower right", fontsize=8)
    ax_a.text(
        0.50, 0.18,
        "Below random => systematic\nclean-bias, not noise",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
        fontsize=9,
    )
    ax_a.set_xlim(0, 1)
    ax_a.set_ylim(0, 1)
    ax_a.grid(True, alpha=0.3)

    # Panel (b): scatter -- x=is_injected (0/1), y=diverged (jittered), color by tier
    loo_llama = json.loads(
        (logs_dir / "loo_results_llama.json").read_text(encoding="utf-8")
    )
    points: list[dict] = []
    for q in loo_llama.get("results", []):
        for ch in q.get("chunk_results", []):
            points.append(
                {
                    "is_injected": int(bool(ch.get("is_injected", 0))),
                    "diverged": int(bool(ch.get("diverged", 0))),
                    "tier": ch.get("tier", "unknown"),
                }
            )
    df_chunks = pd.DataFrame(points)
    if not df_chunks.empty:
        sns.stripplot(
            data=df_chunks, x="is_injected", y="diverged", hue="tier",
            jitter=0.30, alpha=0.55, ax=ax_b, dodge=True,
        )
    ax_b.set_xticks([0, 1])
    ax_b.set_xticklabels(["Clean", "Injected"])
    ax_b.set_ylabel("LOO divergence (1 if removing chunk changes answer)")
    ax_b.set_xlabel("Chunk class")
    ax_b.set_title("(b) Influence vs cleanliness -- INVERSION VISIBLE (D-05b)")
    ax_b.legend(loc="best", fontsize=7, title="Tier")
    ax_b.grid(True, alpha=0.3)
    save_atomic(fig, str(output_dir / "fig3_loo_causal.png"))


# --------------------------------------------------------------------------- #
# Figure 4 -- D-06 ratio sweep (log x-scale per RESEARCH discretion)           #
# --------------------------------------------------------------------------- #
def render_d06_ratio_sweep(logs_dir: Path, output_dir: Path) -> None:
    """ASR-vs-poisoning-ratio line plot.

    Log x-scale per RESEARCH discretion (matches PoisonedRAG Figure 3 + BadRAG
    Figure 4 conventions). 5 markers at 0.5%, 1%, 2%, 5%, 10%.
    """
    ratios = [0.005, 0.01, 0.02, 0.05, 0.10]
    ratio_keys = ["0005", "0010", "0020", "0050", "0100"]
    asrs: list[float] = []
    for r_key in ratio_keys:
        path = logs_dir / f"eval_ratio_{r_key}.json"
        if not path.exists():
            asrs.append(0.0)
            continue
        agg = json.loads(path.read_text(encoding="utf-8")).get("aggregate", {})
        asr = agg.get(
            "paired_asr_tier1",
            agg.get("asr_tier1", agg.get("asr_overall", 0.0)),
        )
        asrs.append(float(asr))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ratios, asrs, marker="o", linewidth=2, markersize=10, color="#D55E00")
    ax.set_xscale("log")
    ax.set_xlabel("Poisoning ratio (fraction of corpus, log scale)")
    ax.set_ylabel("Tier-1 ASR")
    ax.set_title("D-06: ATK-02 -- Attack success vs corpus contamination (llama3.2:3b, undefended)")
    ax.grid(True, alpha=0.3, which="both")
    # Annotate each marker with the value
    for r, a in zip(ratios, asrs):
        ax.annotate(
            f"{a:.2f}", (r, a),
            xytext=(8, 8), textcoords="offset points", fontsize=9,
        )
    ax.set_ylim(0, max(0.25, max(asrs) * 1.4))
    save_atomic(fig, str(output_dir / "fig4_ratio_sweep.png"))


# --------------------------------------------------------------------------- #
# Figure 5 -- D-12 cross-model heatmap (W-5 FAIL-LOUD on missing cells)        #
# --------------------------------------------------------------------------- #
def render_d12_cross_model_heatmap(logs_dir: Path, output_dir: Path) -> None:
    """5x3 heatmap: rows = 5 tiers, cols = 3 LLMs, cells = ASR under fused defense.

    Per CONTEXT D-12: viridis_r colormap, per-cell numeric annotation.
    W-5 fix: assert matrix.shape == (5, 3) AND no NaN cells before sns.heatmap.
    """
    rows = json.loads(
        (logs_dir / "eval_matrix" / "_summary.json").read_text(encoding="utf-8")
    )
    df = pd.DataFrame(rows)
    fused = df[df["defense"] == "fused"]
    matrix = fused.pivot(index="tier", columns="model", values="asr_overall")
    # Reorder rows per CONTEXT D-12 spec
    matrix = matrix.reindex(["tier1", "tier1b", "tier2", "tier3", "tier4"])

    # Detect underscore vs colon model-name schema
    col_order_underscore = ["llama3.2_3b", "mistral_7b", "gemma4_31b-cloud"]
    col_order_colon = ["llama3.2:3b", "mistral:7b", "gemma4:31b-cloud"]
    if set(col_order_underscore).issubset(set(matrix.columns)):
        matrix = matrix[col_order_underscore]
        xticklabels = ["llama3.2:3b", "mistral:7b", "gemma4:31b-cloud"]
    elif set(col_order_colon).issubset(set(matrix.columns)):
        matrix = matrix[col_order_colon]
        xticklabels = col_order_colon
    else:
        raise AssertionError(
            f"D-12 model column schema drift: _summary.json columns are "
            f"{list(matrix.columns)}; expected one of {col_order_underscore} or "
            f"{col_order_colon}. Inspect logs/eval_matrix/_summary.json and update "
            f"col_order_* lists in render_d12_cross_model_heatmap accordingly."
        )

    # W-5 invariant assertions -- fail loud if any cell is missing
    assert matrix.shape == (5, 3), (
        f"D-12 wrong shape: {matrix.shape} (expected (5, 3)). Likely cause: a tier "
        f"missing from _summary.json or a duplicate (tier, model) pair. df=\n{matrix}"
    )
    assert not matrix.isna().any().any(), (
        f"D-12 has NaN cells (schema drift between _summary.json model/tier strings "
        f"and the expected reindex labels). matrix=\n{matrix}"
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        matrix, annot=True, fmt=".2f", cmap="viridis_r",
        xticklabels=xticklabels,
        yticklabels=["T1", "T1b", "T2", "T3", "T4"],
        cbar_kws={"label": "Overall ASR (n=100, unpaired)"},
        linewidths=0.5, ax=ax,
    )
    ax.set_title("D-12: EVAL-V2-01 -- Cross-model ASR under fused defense")
    ax.set_xlabel("LLM target")
    ax.set_ylabel("Attack tier")
    save_atomic(fig, str(output_dir / "fig5_cross_model_heatmap.png"))


# --------------------------------------------------------------------------- #
# Figure 5 v6 -- D-10: 5×5 cross-model heatmap (fused only, Phase 6)          #
# --------------------------------------------------------------------------- #
def render_d12_cross_model_heatmap_v6(logs_dir: Path, output_dir: Path) -> None:
    """D-10: 4×4 cross-model heatmap (FUSED defense only) — Phase 6 v6.

    Reads logs/eval_matrix/_summary_v6.json (75 cells), filters to defense == "fused",
    pivots to (4 tiers × 4 LLMs). T4 and gemma4 excluded (all zeros).
    Preserves W-5 fail-loud invariants but at shape (4, 4).
    """
    summary_path = logs_dir / "eval_matrix" / "_summary_v6.json"
    rows = json.loads(summary_path.read_text(encoding="utf-8"))
    df = pd.DataFrame(rows)
    fused = df[df["defense"] == "fused"]
    matrix = fused.pivot(index="tier", columns="model", values="asr_overall")
    matrix = matrix.reindex(["tier1", "tier1b", "tier2", "tier3"])

    col_order = ["llama3.2_3b", "mistral_7b",
                 "gpt-oss_20b-cloud", "gpt-oss_120b-cloud"]
    if not set(col_order).issubset(set(matrix.columns)):
        raise AssertionError(
            f"D-12 v6 model column schema drift: _summary_v6.json columns are "
            f"{list(matrix.columns)}; expected superset of {col_order}."
        )
    matrix = matrix[col_order]

    # W-5 fail-loud — shape (4, 4): T4 and gemma4 dropped
    assert matrix.shape == (4, 4), (
        f"D-12 v6 wrong shape: {matrix.shape} (expected (4, 4)). df=\n{matrix}"
    )
    assert not matrix.isna().any().any(), (
        f"D-12 v6 has NaN cells. matrix=\n{matrix}"
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(
        matrix, annot=True, fmt=".2f", cmap="viridis_r",
        xticklabels=["llama3.2:3b", "mistral:7b",
                     "gpt-oss:20b-cloud", "gpt-oss:120b-cloud"],
        yticklabels=["T1", "T1b", "T2", "T3"],
        cbar_kws={"label": "Overall ASR (n=100, unpaired)"},
        linewidths=0.5, ax=ax,
    )
    ax.set_title("D-12 v6: Cross-model ASR under fused defense (4 LLMs, 4 tiers)")
    ax.set_xlabel("LLM target")
    ax.set_ylabel("Attack tier")
    save_atomic(fig, str(output_dir / "d12_cross_model_heatmap_v6.png"))


# --------------------------------------------------------------------------- #
# Figure 5 undefended v6 -- D-10 + D-08: 5×4 undefended heatmap               #
# --------------------------------------------------------------------------- #
def render_d12_undefended_v6(logs_dir: Path, output_dir: Path) -> None:
    """D-10: 4×4 cross-model UNDEFENDED heatmap. T4 and gemma4 excluded (all zeros).

    Reads T1b for llama/mistral from _summary_v6.json (no_defense cells).
    Reads all tiers for gpt-oss from eval_harness_undefended_gptoss*_v6.json.
    """
    summary_path = logs_dir / "eval_matrix" / "_summary_v6.json"
    summary = {
        (c["model"], c["tier"]): c["asr_overall"]
        for c in json.loads(summary_path.read_text(encoding="utf-8"))
        if c["defense"] == "no_defense"
    }

    tier_keys = ["tier1", "tier1b", "tier2", "tier3"]
    display_tiers = ["T1", "T1b", "T2", "T3"]
    sources = [
        ("llama3.2:3b",        "llama3.2_3b",       None),
        ("mistral:7b",         "mistral_7b",         None),
        ("gpt-oss:20b-cloud",  "gpt-oss_20b-cloud",  logs_dir / "eval_harness_undefended_gptoss20b_v6.json"),
        ("gpt-oss:120b-cloud", "gpt-oss_120b-cloud", logs_dir / "eval_harness_undefended_gptoss120b_v6.json"),
    ]

    data = []
    xticklabels = []
    for label, model_key, harness_path in sources:
        if harness_path is not None:
            agg = json.loads(harness_path.read_text(encoding="utf-8"))["aggregate"]
            row = [agg.get(f"asr_{t}", 0.0) for t in tier_keys]
        else:
            row = [summary.get((model_key, t), 0.0) for t in tier_keys]
        data.append(row)
        xticklabels.append(label)

    matrix = pd.DataFrame(
        data, index=xticklabels, columns=display_tiers
    ).T  # rows=tiers, cols=LLMs

    assert matrix.shape == (4, 4), (
        f"D-12 v6 undefended wrong shape: {matrix.shape} (expected (4, 4)). df=\n{matrix}"
    )
    assert not matrix.isna().any().any(), (
        f"D-12 v6 undefended has NaN cells. matrix=\n{matrix}"
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(
        matrix, annot=True, fmt=".2f", cmap="viridis_r",
        xticklabels=xticklabels,
        yticklabels=display_tiers,
        cbar_kws={"label": "Overall ASR (undefended, n=100)"},
        linewidths=0.5, ax=ax,
    )
    ax.set_title("D-12 v6: Cross-model ASR — undefended baseline (4 tiers × 4 LLMs)")
    ax.set_xlabel("LLM target")
    ax.set_ylabel("Attack tier")
    save_atomic(fig, str(output_dir / "d12_undefended_v6.png"))


# --------------------------------------------------------------------------- #
# Figure 1 v6 -- D-11: arms-race bars extended to 5 LLMs (Phase 6)            #
# --------------------------------------------------------------------------- #
def render_d03_arms_race_v6(logs_dir: Path, output_dir: Path) -> None:
    """D-11: arms-race bars extended to include gpt-oss-20b and gpt-oss-120b.

    Reads logs/eval_matrix/_summary_v6.json (75 cells). Plots grouped bars:
    each tier on x-axis, bar groups colored by (model, defense). Preserves
    B-2 fail-loud invariants from render_d03_arms_race.
    """
    summary_path = logs_dir / "eval_matrix" / "_summary_v6.json"
    rows = json.loads(summary_path.read_text(encoding="utf-8"))
    df = pd.DataFrame(rows)

    tiers = ["tier1", "tier1b", "tier2", "tier3"]
    models = ["llama3.2_3b", "mistral_7b",
              "gpt-oss_20b-cloud", "gpt-oss_120b-cloud"]
    defenses = ["no_defense", "fused", "def02"]

    # Build (tier × model_defense) data matrix
    n_tiers = len(tiers)
    bar_groups: list[tuple[str, str]] = [(m, d) for m in models for d in defenses]
    n_groups = len(bar_groups)
    data = np.full((n_tiers, n_groups), np.nan, dtype=float)
    for ti, tier in enumerate(tiers):
        for gi, (model, defense) in enumerate(bar_groups):
            sel = df[(df["tier"] == tier) & (df["model"] == model)
                     & (df["defense"] == defense)]
            if len(sel) > 0:
                data[ti, gi] = float(sel.iloc[0]["asr_overall"])

    # B-2 fail-loud invariants (matches render_d03_arms_race)
    assert np.nansum(data) > 0, "D-03 v6 all-zero/NaN matrix — refusing to render"
    assert np.nanmax(data) > 0.05, "D-03 v6 no measurable bar heights"
    nonzero_count = int(np.sum(~np.isnan(data) & (data > 0)))
    assert nonzero_count >= 5, f"D-03 v6 only {nonzero_count} non-zero cells"

    # Muted, high-contrast palette: 4 model families (ColorBrewer-inspired),
    # 3 shades per family (dark=no_defense, mid=fused, light=def02).
    # Hatching adds a second visual cue for defense tier.
    _bar_colors = {
        "llama3.2_3b":        {"no_defense": "#2166ac", "fused": "#6aafd4", "def02": "#b0d4ea"},
        "mistral_7b":         {"no_defense": "#b2182b", "fused": "#d6604d", "def02": "#f4a582"},
        "gpt-oss_20b-cloud":  {"no_defense": "#1b7837", "fused": "#5aae61", "def02": "#a6dba0"},
        "gpt-oss_120b-cloud": {"no_defense": "#762a83", "fused": "#9970ab", "def02": "#c2a5cf"},
    }
    _bar_hatches = {"no_defense": "", "fused": "//", "def02": ".."}
    _defense_labels = {"no_defense": "undefended", "fused": "fused", "def02": "def02"}
    _model_labels = {
        "llama3.2_3b": "llama3.2:3b", "mistral_7b": "mistral:7b",
        "gpt-oss_20b-cloud": "gpt-oss:20b", "gpt-oss_120b-cloud": "gpt-oss:120b",
    }

    # Plot grouped bars
    fig, ax = plt.subplots(figsize=(14, 6))
    bar_width = 0.8 / max(n_groups, 1)
    x = np.arange(n_tiers)
    for gi, (model, defense) in enumerate(bar_groups):
        col = data[:, gi]
        col_safe = np.where(np.isnan(col), 0.0, col)
        ax.bar(
            x + gi * bar_width - 0.4 + bar_width / 2,
            col_safe,
            width=bar_width,
            color=_bar_colors[model][defense],
            hatch=_bar_hatches[defense],
            edgecolor="white",
            linewidth=0.4,
            label=f"{_model_labels[model]} / {_defense_labels[defense]}",
        )
    ax.set_xticks(x)
    ax.set_xticklabels(["T1", "T1b", "T2", "T3"])
    ax.set_xlabel("Attack tier")
    ax.set_ylabel("Overall ASR (n=100, unpaired)")
    ax.set_title("D-03 v6: Arms race bars — 4 tiers × 4 LLMs × 3 defenses (Phase 6)")
    ax.legend(loc="upper right", fontsize=7, ncol=2, framealpha=0.85)
    ax.set_ylim(0, max(0.3, float(np.nanmax(data)) * 1.15))
    save_atomic(fig, str(output_dir / "d03_arms_race_v6.png"))


# --------------------------------------------------------------------------- #
# CLI plumbing                                                                 #
# --------------------------------------------------------------------------- #
def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 3.4 -- emit 5 PNG figures for the writeup."
    )
    parser.add_argument("--logs-dir", default="logs")
    parser.add_argument("--output-dir", default="figures")
    parser.add_argument(
        "--figures", nargs="*", default=None,
        help="subset of figures to render (e.g. fig1 fig5); default renders all 5",
    )
    return parser


ALL_RENDERERS = {
    "fig1":     render_d03_arms_race,
    "fig2":     render_d04_utility_security,
    "fig3":     render_d05_loo_causal,
    "fig4":     render_d06_ratio_sweep,
    "fig5":     render_d12_cross_model_heatmap,
    "fig5_v6":  render_d12_cross_model_heatmap_v6,
    "fig5_und": render_d12_undefended_v6,
    "fig1_v6":  render_d03_arms_race_v6,
}


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = []
    args = make_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(args.logs_dir)

    selected = args.figures if args.figures else list(ALL_RENDERERS.keys())
    for key in selected:
        renderer = ALL_RENDERERS.get(key)
        if renderer is None:
            print(f"[WARN] unknown figure key: {key}", file=sys.stderr)
            continue
        try:
            renderer(logs_dir, output_dir)
            print(f"[OK] rendered {key}")
        except AssertionError as e:
            # Surfaces from B-2 D-03 invariants and W-5 D-12 invariants.
            print(f"[ERROR] {key} (assertion): {e}", file=sys.stderr)
            return 2
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] {key}: {type(e).__name__}: {e}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
