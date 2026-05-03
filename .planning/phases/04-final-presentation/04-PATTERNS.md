# Phase 4: Final Presentation - Pattern Map

**Mapped:** 2026-05-02
**Files analyzed:** 3 NEW Python files + 4 NEW asset outputs
**Analogs found:** 3 / 3 NEW Python files (100% — all map cleanly to Phase 3.4 patterns)

## File Classification

| New / Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------------|------|-----------|----------------|---------------|
| `scripts/make_diagrams.py` (NEW) | script / figure-generator | batch (deterministic file I/O) | `scripts/make_figures.py` | exact (same role + same data flow) |
| `scripts/make_qr.py` (NEW) | script / asset-generator | batch (one-shot file write) | `scripts/make_figures.py` (CLI scaffold) + qrcode lib README (encoding) | role-match (smaller scope; only 1 output file) |
| `tests/test_phase4_assets.py` (NEW) | test / asset-validator | request-response (file-on-disk assertions) | `tests/test_make_figures.py` | exact (same role + same data flow) |
| `figures/diagram_a_rag_pipeline.png` (NEW asset) | output artifact | n/a (PNG) | `figures/fig1_arms_race.png` | output convention only |
| `figures/diagram_b_defense_pipeline.png` (NEW asset) | output artifact | n/a (PNG) | `figures/fig5_cross_model_heatmap.png` | output convention only |
| `figures/qr_github_repo.png` (NEW asset) | output artifact | n/a (PNG) | (no analog — first QR in repo) | naming convention only |
| `figures/demo_tier2_mistral.gif` (NEW asset) | output artifact | n/a (GIF, manual capture) | (no analog) | naming convention only |
| `requirements.txt` (MODIFIED) | config | n/a (text append) | existing entries in same file | exact (file-edit) |

**Note on naming:** Research recommends file names `figures/diagA_rag_pipeline.png`, `figures/diagB_defense_pipeline.png`, `figures/qr_github.png` (snake-case + short prefix). Orchestrator-supplied names (`diagram_a_*`, `qr_github_repo.png`) are also acceptable. Planner should pick ONE convention and apply it consistently across script + tests + Slides embed; both forms occur in upstream docs. RECOMMENDED: follow research naming (`diagA_*`, `diagB_*`, `qr_github.png`) so it parallels existing `fig1..fig5` short-form names.

## Pattern Assignments

### `scripts/make_diagrams.py` (script, batch file I/O)

**Analog:** `scripts/make_figures.py` (read in full — 518 lines)

This is the most important pattern in the phase. `make_figures.py` is the canonical "deterministic figure generator" pattern; mirror it exactly for `make_diagrams.py`. The four reusable elements are:

**(1) Module-top deterministic setup** (`scripts/make_figures.py:21-36`):

```python
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
```

Caveat for Phase 4: poster prints at 36×48" so `savefig.dpi` should be raised to **300** (not 150) for `make_diagrams.py` per RESEARCH §"Pattern 1: matplotlib diagram script" (line 249 of `04-RESEARCH.md`). Keep `figure.dpi=150` for fast on-screen iteration. Keep Agg, constrained_layout, tableau-colorblind10 unchanged so Diagrams A/B match the visual style of `fig1..fig5`.

**(2) Atomic save helper** (`scripts/make_figures.py:81-92`):

```python
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
```

Copy this helper verbatim (bump `dpi=150` → `dpi=300` for poster-print quality).

**(3) Per-figure render functions registered in a dict + CLI dispatch** (`scripts/make_figures.py:467-513`):

```python
def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 3.4 -- emit 5 PNG figures for the writeup.")
    parser.add_argument("--logs-dir", default="logs")
    parser.add_argument("--output-dir", default="figures")
    parser.add_argument("--figures", nargs="*", default=None,
                        help="subset of figures to render (e.g. fig1 fig5); default renders all 5")
    return parser

ALL_RENDERERS = {
    "fig1": render_d03_arms_race,
    ...
}

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = []
    args = make_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ...
    selected = args.figures if args.figures else list(ALL_RENDERERS.keys())
    for key in selected:
        renderer = ALL_RENDERERS.get(key)
        ...
        try:
            renderer(logs_dir, output_dir)
            print(f"[OK] rendered {key}")
        except AssertionError as e:
            print(f"[ERROR] {key} (assertion): {e}", file=sys.stderr)
            return 2
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] {key}: {type(e).__name__}: {e}", file=sys.stderr)
            return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

For `make_diagrams.py`, replace the renderer dict with:

```python
ALL_RENDERERS = {
    "diagA": render_diagram_a_rag_pipeline,
    "diagB": render_diagram_b_defense_pipeline,
}
```

Diagrams take no `--logs-dir` input (they're hand-positioned schematics, not data plots) so the planner may simplify the CLI to `--output-dir` only. Keep the `--figures` subset arg though — enables `python scripts/make_diagrams.py --figures diagA` for fast iteration on one diagram.

**(4) Box + arrow primitives** (from RESEARCH §"Pattern 1" lines 253-283):

```python
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def box(ax, xy, w, h, text, color="#FFFFFF", edge="black"):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.05",
                                facecolor=color, edgecolor=edge, linewidth=1.5))
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha="center", va="center", fontsize=11)

def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-|>", mutation_scale=18, linewidth=1.4))
```

Use `#D62728` (matplotlib default red, also in tableau-colorblind10) for the poisoned-chunk highlight in Diagram A — keeps palette consistent with `fig1..fig5`.

**Naming convention to follow:**
- File: `scripts/make_diagrams.py` (parallels `scripts/make_figures.py`).
- Render function names: `render_diagram_a_rag_pipeline`, `render_diagram_b_defense_pipeline` (mirrors existing `render_d03_arms_race`, `render_d04_utility_security`, etc. — verb-noun-context).
- Output PNG names: `diagA_rag_pipeline.png`, `diagB_defense_pipeline.png` (parallels `fig1_arms_race.png`).

**Import / dependency caveats:**
- matplotlib backend MUST be set to `Agg` BEFORE any pyplot import (existing comment in `make_figures.py:23` is explicit). Headless conda env / CI both require Agg.
- Use `# noqa: E402` after every import that follows the `matplotlib.use("Agg")` line (linter would otherwise complain about non-top-of-file imports).
- No new pip packages needed for `make_diagrams.py` (matplotlib + Pillow already in env per RESEARCH line 132).

---

### `scripts/make_qr.py` (script, batch file I/O — single output)

**Analog:** `scripts/make_figures.py` for CLI/atomic-save scaffolding; qrcode 8.2 README (cited in `04-RESEARCH.md:386-403`) for encoding logic.

**(1) CLI + main + atomic save scaffold** — copy the same structure from `scripts/make_figures.py:467-513` but trim to one output:

```python
def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 4 -- emit GitHub-repo QR PNG for the poster.")
    parser.add_argument("--output", default="figures/qr_github.png")
    parser.add_argument("--url", default="https://github.com/waleed79/CS763-indirect_prompt_injection",
                        help="Repo URL to encode (verified via `git remote get-url origin` 2026-05-02)")
    parser.add_argument("--box-size", type=int, default=12)
    parser.add_argument("--border", type=int, default=4)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv or [])
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    render_qr(args.url, args.output, args.box_size, args.border)
    print(f"[OK] wrote {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

**(2) qrcode encoding pattern** (RESEARCH §"QR code generation" lines 386-403):

```python
import qrcode

def render_qr(url: str, out_path: str, box_size: int = 12, border: int = 4) -> None:
    qr = qrcode.QRCode(
        version=None,                                       # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% recovery
        box_size=box_size,                                  # ~12 px/module → ~600 px image
        border=border,                                      # quiet zone modules
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Atomic write — same idiom as make_figures.save_atomic
    tmp = out_path + ".tmp"
    img.save(tmp)
    os.replace(tmp, out_path)
```

**Naming convention to follow:**
- File: `scripts/make_qr.py` (matches `make_figures.py` / `make_results.py` `make_*` convention).
- Single render function `render_qr` (no dict needed — only one artifact).
- Output PNG: `figures/qr_github.png` (RESEARCH-recommended name; short, matches `figX_*` brevity).

**Import / dependency caveats:**
- `qrcode[pil]==8.2` is NOT yet installed. Planner MUST add a setup task: `conda run -n rag-security pip install "qrcode[pil]==8.2"` AND append `qrcode[pil]==8.2` to `requirements.txt` (RESEARCH §"Runtime State Inventory" line 318 calls this out for RAG-05 reproducibility).
- `qrcode` import depends on Pillow (already installed at 12.2.0). The `[pil]` extra is the standard way to ensure PIL backend.
- VERIFIED URL: `git remote get-url origin` → `https://github.com/waleed79/CS763-indirect_prompt_injection.git` (2026-05-02). Strip the `.git` suffix when encoding (the URL a phone visits).
- Repo MUST be PUBLIC before printing (RESEARCH §"Pitfall 5" + ASVS V4 line 625). Add a verification task to the plan.

---

### `tests/test_phase4_assets.py` (test, request-response file assertions)

**Analog:** `tests/test_make_figures.py` (read in full — 57 lines). Same role (asset-existence smoke test), same data flow (assertions on files-on-disk).

**(1) Wave-0 importlib stub pattern** (`tests/test_make_figures.py:1-26`):

```python
"""Wave 0 stub for scripts/make_diagrams.py + scripts/make_qr.py (Phase 4).

Skips until the scripts are implemented. After Plan lands, all tests must pass.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

def _try_load(modname: str):
    try:
        spec = importlib.util.spec_from_file_location(modname, _SCRIPTS_DIR / f"{modname}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (AttributeError, FileNotFoundError, Exception):
        return None

_diag = _try_load("make_diagrams")
_qr = _try_load("make_qr")
_DIAG_OK = _diag is not None
_QR_OK = _qr is not None
```

**(2) Smoke-test class structure** (`tests/test_make_figures.py:29-56`):

```python
class TestMakeDiagramsSmoke:
    EXPECTED_PNGS = [
        "diagA_rag_pipeline.png",
        "diagB_defense_pipeline.png",
    ]

    @pytest.mark.skipif(not _DIAG_OK, reason="scripts/make_diagrams.py not yet implemented")
    def test_main_runs_with_no_args(self, tmp_path):
        rc = _diag.main(["--output-dir", str(tmp_path)])
        assert rc == 0

    @pytest.mark.skipif(not _DIAG_OK, reason="scripts/make_diagrams.py not yet implemented")
    def test_both_diagrams_emitted(self, tmp_path):
        _diag.main(["--output-dir", str(tmp_path)])
        for name in self.EXPECTED_PNGS:
            path = tmp_path / name
            assert path.exists(), f"expected {name} to be written"
            assert path.stat().st_size > 1024, f"{name} suspiciously small (<1KB)"

    def test_agg_backend_used(self):
        import matplotlib
        assert matplotlib.get_backend().lower() == "agg"
```

**(3) Asset-on-disk assertions** (from RESEARCH §"Validation Architecture" lines 557-599 — already drafted):

```python
from pathlib import Path
from PIL import Image

FIG = Path("figures")

def test_minimum_two_figures_present():
    pngs = list(FIG.glob("*.png"))
    assert len(pngs) >= 2, f"PRES-02 requires >=2 visualizations, found {len(pngs)}"

def test_diagram_a_present():
    assert (FIG / "diagA_rag_pipeline.png").exists(), "Diagram A (RAG pipeline) missing"

def test_diagram_b_present():
    assert (FIG / "diagB_defense_pipeline.png").exists(), "Diagram B (defense) missing"

def test_qr_present():
    p = FIG / "qr_github.png"
    assert p.exists() and p.stat().st_size > 0, "QR PNG missing or empty"

def test_qr_decodes_to_repo_url():
    pytest = __import__("pytest")
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except ImportError:
        pytest.skip("pyzbar not installed; manual QR scan-test required instead")
    img = Image.open(FIG / "qr_github.png")
    decoded = decode(img)
    assert decoded, "QR did not decode"
    url = decoded[0].data.decode()
    assert "github.com/waleed79/CS763-indirect_prompt_injection" in url, f"QR URL wrong: {url}"

def test_demo_gif_present_and_animated():
    p = FIG / "demo_tier2_mistral.gif"
    assert p.exists(), "Demo GIF missing"
    assert p.stat().st_size > 50_000, "Demo GIF too small (likely a single frame)"
    assert p.stat().st_size < 2_000_000, "Demo GIF too large for slide embedding (>2 MB)"
    img = Image.open(p)
    assert getattr(img, "n_frames", 1) > 1, "GIF has only 1 frame (not animated)"
```

**Naming convention to follow:**
- File: `tests/test_phase4_assets.py` (matches existing `tests/test_make_figures.py`, `tests/test_make_results.py` — `test_*.py` per `pytest.ini`).
- Class: `Test*` (per `pytest.ini` `python_classes = Test*`). Either group into `TestPhase4Assets` or split into `TestMakeDiagramsSmoke` / `TestMakeQrSmoke` / `TestPhase4AssetsOnDisk`. Splitting matches `test_make_figures.py`'s single-class style and reads more cleanly per concern.
- Function names: `test_*` (per `pytest.ini`).

**Import / dependency caveats:**
- The on-disk tests (`test_demo_gif_*`, `test_qr_present`) read from the real `figures/` directory, not `tmp_path`. This is intentional — they validate the FINAL artifacts that will be embedded in the deck/poster. Make sure they ONLY run after the `make_*` scripts have produced the artifacts; otherwise mark `xfail` until Wave-1 lands.
- `pyzbar` is OPTIONAL — gracefully skip if not installed (RESEARCH §line 583). Don't add it to `requirements.txt`; manual phone-scan is an acceptable substitute (RESEARCH §"Pitfall 5").
- `Pillow` (already installed) provides `Image.n_frames` for animated-GIF detection. No new dep.
- The `pytest.ini` global `--timeout=60` applies — none of these tests exceed a few seconds, so default is fine.

---

### `requirements.txt` (config, single-line append)

**Analog:** existing entries in the same file. Just append `qrcode[pil]==8.2`. RESEARCH §line 318 explicitly directs this for RAG-05 reproducibility.

---

## Shared Patterns

### Atomic file write (PNG / GIF / any binary)
**Source:** `scripts/make_figures.py:81-92` (`save_atomic`)
**Apply to:** `make_diagrams.py`, `make_qr.py`, any future Phase 4 script that emits a binary asset.

```python
def save_atomic(fig, final_path: str) -> None:
    tmp_path = final_path + ".tmp"
    fig.savefig(tmp_path, bbox_inches="tight", dpi=300, format="png")  # 300 for poster
    plt.close(fig)
    os.replace(tmp_path, final_path)
```

For non-matplotlib outputs (the QR PIL image), the equivalent is:

```python
tmp = out_path + ".tmp"
img.save(tmp)
os.replace(tmp, out_path)
```

Rationale (from `make_figures.py:84-86` docstring): "os.replace is atomic on POSIX and Windows when src/dst are in the same directory; partial .tmp files are never visible to downstream consumers." Critical because `tests/test_phase4_assets.py` checks `path.exists()` and a partial write would falsely pass.

### Deterministic matplotlib setup (Pattern 1)
**Source:** `scripts/make_figures.py:21-36`
**Apply to:** `make_diagrams.py` (only matplotlib-using new script).

The 14-line block must appear before any other pyplot import in the process. Existing project convention; do not vary.

### CLI scaffold + error-coded exit
**Source:** `scripts/make_figures.py:467-513`
**Apply to:** `make_diagrams.py` and `make_qr.py`.

- `argparse`-based parser with `--output-dir` (or `--output` for single-file scripts).
- `main(argv: list[str] | None)` returning int (0 = OK, 2 = error).
- Wrap renderer call in `try/except` and print `[OK]` / `[ERROR]` to stdout/stderr.
- `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))` at module bottom.

### Wave-0 importlib stub for tests against not-yet-existing scripts
**Source:** `tests/test_make_figures.py:1-26` (and same pattern in `tests/test_make_results.py:1-26`)
**Apply to:** `tests/test_phase4_assets.py` only if Wave-0 ordering matters (i.e., the test file is committed before the scripts). If both ship together in one wave, the importlib dance can be simplified to a plain `from scripts.make_diagrams import main` with a `try/except ImportError` guard.

### Conda env invocation
**Source:** CLAUDE.md + RESEARCH §"Project Constraints" line 64
**Apply to:** Every Phase 4 script run AND the test command.

```bash
conda run -n rag-security python scripts/make_diagrams.py
conda run -n rag-security python scripts/make_qr.py
conda run -n rag-security python -m pytest tests/test_phase4_assets.py -x --quiet
```

### Visual style consistency across all figures (Pitfall 7)
**Source:** RESEARCH §"Pitfall 7" line 376 + `scripts/make_figures.py:36` (`tableau-colorblind10`)
**Apply to:** Both new diagrams.

- Same DPI family (300 for poster, 150 for screen).
- Same palette: `tableau-colorblind10` style + `#D62728` for the "poisoned chunk" highlight in Diagram A.
- Same `constrained_layout=True`, same `Agg` backend.
- Same `savefig.bbox = "tight"`.

This is what makes Diagrams A/B feel like siblings of `fig1..fig5` on the poster.

## No Analog Found

| File | Role | Reason | Planner guidance |
|------|------|--------|------------------|
| `figures/qr_github.png` | output PNG | First QR code in repo. | No analog needed; output of `make_qr.py`. RESEARCH lines 386-403 has the encoding recipe. |
| `figures/demo_tier2_mistral.gif` | manual capture artifact | First GIF in repo. | No script analog — capture via Win+G then ffmpeg per RESEARCH lines 407-422. Add a `scripts/make_demo_gif.md` recipe doc (recommended in RESEARCH line 213) instead of a Python script. |
| `figures/diagram_a_rag_pipeline.png` / `figures/diagB_defense_pipeline.png` | output PNGs | First architecture diagrams in repo. | No analog needed; they are outputs of `make_diagrams.py`. The `fig1..fig5` PNGs in `figures/` are *data* visualizations (bar charts, ROC, heatmaps) — not architecture schematics — so they are convention-only references for naming + DPI + palette. |

## Reusable Assets the Planner Should Cite Verbatim

These are existing files — do NOT copy or modify. The planner references them by path in the PLAN's action steps so plans can pull narrative/numbers/figures into Slides:

| Path | Purpose |
|------|---------|
| `docs/phase3_results.md` | Single source of truth for every cited number (RESEARCH "Pitfall 3") |
| `docs/results/arms_race_table.md` | Pre-formatted MD arms race table for slide content |
| `docs/results/cross_model_matrix.md` | Cross-model 5×3 defense matrix |
| `docs/results/ablation_table.md` | 7-defense ablation table |
| `docs/xss_ssrf_taxonomy.md` | Threat-model / taxonomy text source |
| `figures/fig1_arms_race.png` | Hero figure — embed in talk (D-04) and poster panel (D-15) |
| `figures/fig2_utility_security.png` | 76% FPR caveat slide (D-09) |
| `figures/fig3_loo_causal.png` | LOO negative result reference (D-10, limitations only) |
| `figures/fig4_ratio_sweep.png` | One-bullet generalizability mention (D-08) |
| `figures/fig5_cross_model_heatmap.png` | gemma4 0% finding slide + poster panel (D-15) |
| `scripts/make_figures.py` | Pattern source for `make_diagrams.py` (do NOT modify; copy patterns into the new file) |
| `tests/test_make_figures.py` | Pattern source for `tests/test_phase4_assets.py` |
| `tests/test_make_results.py` | Secondary pattern source for `tests/test_phase4_assets.py` (importlib stub variant) |
| `pytest.ini` | Test config — `Test*` classes, `test_*` funcs, 60s timeout, verbose default |
| `requirements.txt` | Append `qrcode[pil]==8.2` for RAG-05 reproducibility |
| `.planning/phases/04-final-presentation/04-CONTEXT.md` | D-01..D-16 — every planning decision |
| `.planning/phases/04-final-presentation/04-RESEARCH.md` | Stack, skeletons, verified versions, pitfalls |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `figures/`, `docs/`, `pytest.ini`, `requirements.txt`, project-root config files.
**Files scanned:** 41 scripts (Glob), 21 tests (Glob), 5 existing figures (Glob), 2 reference Python files (Read full), 2 reference test files (Read full), 1 pytest config (Read), 1 git-remote check (Bash).
**Pattern extraction date:** 2026-05-02

---

## PATTERN MAPPING COMPLETE

**Phase:** 04 — Final Presentation
**Files classified:** 8 (3 NEW Python files + 4 NEW asset outputs + 1 MODIFIED config)
**Analogs found:** 3 / 3 NEW Python files (100%)

### Coverage
- Files with exact analog: 3 (`make_diagrams.py`, `tests/test_phase4_assets.py`, `requirements.txt`)
- Files with role-match analog: 1 (`make_qr.py` — CLI scaffold from `make_figures.py` + encoding from qrcode README)
- Files with no analog: 4 (output assets — PNGs / GIF; first of their kind in repo)

### Key Patterns Identified
- All matplotlib-emitting scripts MUST set `MPLBACKEND=Agg` at module top (existing project convention; non-negotiable per `make_figures.py:23` comment).
- All binary-asset writes MUST use the `.tmp` + `os.replace` atomic idiom (so `tests/test_phase4_assets.py::*present*` cannot pass on a partial write).
- All scripts follow `make_*` naming + `argparse` CLI + `main(argv) -> int` returning 0/2 + `if __name__ == "__main__": sys.exit(...)`.
- All tests follow `tests/test_*.py` + `Test*` class + `test_*` function (per `pytest.ini`); use the `importlib.util.spec_from_file_location` Wave-0 stub if scripts may not exist yet.
- Visual style for new diagrams must mirror `fig1..fig5` (tableau-colorblind10 palette, `#D62728` for the poisoned-chunk highlight, constrained_layout, 300 DPI for poster vs 150 for screen) per Pitfall 7.
- Single source of truth for ALL cited numbers is `docs/phase3_results.md` (Pitfall 3) — every poster/slide statistic must trace to that file.
- New pip dep `qrcode[pil]==8.2` requires `requirements.txt` update for RAG-05 reproducibility.

### File Created
`.planning/phases/04-final-presentation/04-PATTERNS.md`

### Ready for Planning
Pattern mapping complete. Planner can now reference these analog patterns and concrete code excerpts directly in the per-plan action steps for Phase 4.
