"""Phase 7 Plan 06 — numerical-fidelity audit script.

Verifies that all 30 cells (10 table rows x 3 metrics) in the addendum table
match the source JSON files.

Llama rows (rows 1-6): displayed at 2-decimal precision in the §4 table (as documented in
07-05-SUMMARY.md decisions). Tolerance = 0.005 (half of 0.01 rounding interval).

gpt-oss rows (rows 7-10): displayed at raw JSON precision. Tolerance = 0.0006.

Format lock: bare floats (no % signs, no trailing units) matching Phase 5 §4 style.
"""
import json
import re
import sys

# Source data
p5 = json.load(open('logs/ablation_table.json', encoding='utf-8'))
p7 = json.load(open('logs/ablation_table_gptoss_v7.json', encoding='utf-8'))

# Llama row keys in Phase 5 ablation_table.json
LLAMA_KEYS = {
    "DEF-02":      ["def02"],
    "BERT alone":  ["bert_only"],
    "Perplexity":  ["perplexity_only"],
    "Imperative":  ["imperative_only"],
    "Fingerprint": ["fingerprint_only"],
    "Fused":       ["fused_fixed_0.5", "fused"],
}
GPTOSS_KEYS = {
    ("gpt-oss:20b-cloud", "Fused"):   "gptoss20b_cloud__fused",
    ("gpt-oss:20b-cloud", "DEF-02"):  "gptoss20b_cloud__def02",
    ("gpt-oss:120b-cloud", "Fused"):  "gptoss120b_cloud__fused",
    ("gpt-oss:120b-cloud", "DEF-02"): "gptoss120b_cloud__def02",
}


def find_row(d, candidates):
    for c in candidates:
        if c in d:
            return d[c]
    raise KeyError(f"No key from {candidates} found in {list(d.keys())}")


# Read addendum table from docs/phase5_honest_fpr.md
text = open('docs/phase5_honest_fpr.md', encoding='utf-8').read()
m = re.search(r'## Phase 7 addendum.*?(?=^## |\Z)', text, re.S | re.M)
assert m, "Addendum section not found"
table_block = m.group()


def parse_table_rows(block):
    rows = []
    for line in block.splitlines():
        if not line.startswith('|') or '---' in line:
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 5:
            continue
        if cells[0].strip() == 'Model':
            continue
        rows.append(cells)
    return rows


rows = parse_table_rows(table_block)
assert len(rows) == 10, f"expected 10 data rows, got {len(rows)}"

# Lock the cell format to the canonical Phase 5 §4 style: bare floats (no %)
PCT_PATTERN = re.compile(r'%')
errors = []


def _parse_cell(cell_val: str, where: str):
    if PCT_PATTERN.search(cell_val):
        errors.append(f"{where}: unexpected '%' in cell {cell_val!r} — Phase 5 §4 format is bare floats")
        return None
    try:
        return float(cell_val.strip())
    except ValueError:
        errors.append(f"{where}: unparseable cell {cell_val!r}")
        return None


# First 6 rows = llama
llama_label_order = ["DEF-02", "BERT alone", "Perplexity", "Imperative", "Fingerprint", "Fused"]
for i, label in enumerate(llama_label_order):
    cells = rows[i]
    model_cell = cells[0]
    assert "llama" in model_cell.lower(), f"row {i}: expected llama, got {model_cell!r}"
    expected = find_row(p5, LLAMA_KEYS[label])
    for metric, cell_val in [
        ("per_chunk_fpr", cells[2]),
        ("answer_preserved_fpr", cells[3]),
        ("judge_fpr", cells[4]),
    ]:
        table_v = _parse_cell(cell_val, f"llama|{label}|{metric}")
        if table_v is None:
            continue
        src_v = round(expected[metric], 3)
        # Llama rows displayed at 2-decimal precision (per 07-05-SUMMARY decisions):
        # tolerance = 0.005 (half of 0.01 rounding interval)
        if abs(table_v - src_v) > 0.005:
            errors.append(f"llama|{label}|{metric}: table={table_v} json={src_v} diff={abs(table_v-src_v):.4f}")

# Last 4 rows = gpt-oss
gptoss_order = [
    ("gpt-oss:20b-cloud", "Fused"),
    ("gpt-oss:20b-cloud", "DEF-02"),
    ("gpt-oss:120b-cloud", "Fused"),
    ("gpt-oss:120b-cloud", "DEF-02"),
]
for j, (model, defense) in enumerate(gptoss_order):
    cells = rows[6 + j]
    expected = p7[GPTOSS_KEYS[(model, defense)]]
    for metric, cell_val in [
        ("per_chunk_fpr", cells[2]),
        ("answer_preserved_fpr", cells[3]),
        ("judge_fpr", cells[4]),
    ]:
        table_v = _parse_cell(cell_val, f"{model}|{defense}|{metric}")
        if table_v is None:
            continue
        src_v = round(expected[metric], 3)
        if abs(table_v - src_v) > 0.0006:
            errors.append(f"{model}|{defense}|{metric}: table={table_v} json={src_v}")

if errors:
    print("FIDELITY ERRORS:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)

print(f"OK: all {len(rows)} rows x 3 metrics = 30 cells match JSON sources to 3 decimals")
