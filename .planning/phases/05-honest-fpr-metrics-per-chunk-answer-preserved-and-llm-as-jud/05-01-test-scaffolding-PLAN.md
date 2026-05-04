---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: 01
type: execute
wave: 0
depends_on: []
files_modified:
  - tests/test_judge_fpr.py
  - tests/conftest.py
autonomous: true
requirements: []
tags: [testing, scaffolding, pytest]
must_haves:
  truths:
    - "tests/test_judge_fpr.py exists and pytest can collect it without errors"
    - "tests/conftest.py exposes ablation_snapshot and frozen_judge_cache fixtures"
    - "All V-01..V-09 sub-tasks have a corresponding test method"
    - "Tests SKIP cleanly when scripts/run_judge_fpr.py does not yet exist"
    - "Tests un-skip and validate as soon as scripts/run_judge_fpr.py lands in Plan 02"
  artifacts:
    - path: "tests/test_judge_fpr.py"
      provides: "9 stub tests V-01..V-09 with importlib spec_from_file_location skip-guard"
      contains: "spec_from_file_location, run_judge_fpr, pytestmark, skipif"
    - path: "tests/conftest.py"
      provides: "ablation_snapshot + frozen_judge_cache fixtures"
      contains: "@pytest.fixture, ablation_snapshot, frozen_judge_cache"
  key_links:
    - from: "tests/test_judge_fpr.py"
      to: "scripts/run_judge_fpr.py"
      via: "importlib.util.spec_from_file_location"
      pattern: "spec_from_file_location.*run_judge_fpr"
    - from: "tests/test_judge_fpr.py"
      to: "tests/conftest.py"
      via: "pytest fixture injection"
      pattern: "ablation_snapshot|frozen_judge_cache"
---

<objective>
Create Wave 0 test scaffolding for Phase 5: a `tests/test_judge_fpr.py` file containing 9 stub tests covering V-01..V-09 from VALIDATION.md, plus a new `tests/conftest.py` that exposes two pytest fixtures (`ablation_snapshot`, `frozen_judge_cache`) used by the idempotency / back-compat tests. The stub file MUST cleanly SKIP all tests until `scripts/run_judge_fpr.py` lands in Plan 02, then automatically un-skip once the production module exists.

Purpose: Lock the test contract before production code lands so that Plan 02 implementation is gated on green tests rather than asserted post-hoc. This mirrors the Wave 0 stub pattern established in Phase 3.2 / 3.4 (STATE.md Phase 03.4-01 entry).

Output: `tests/test_judge_fpr.py` (9 stub tests), `tests/conftest.py` (2 fixtures). All tests SKIP today; all 9 tests PASS after Plan 03 produces real artifacts.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-CONTEXT.md
@.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-RESEARCH.md
@.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md
@.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-VALIDATION.md
@tests/test_make_results.py
@tests/test_phase4_assets.py

<interfaces>
<!-- Production module contract that Plan 02 must implement (used by tests via importlib). -->
<!-- Tests reference these names; Plan 02's run_judge_fpr.py MUST export them at module level. -->

scripts/run_judge_fpr.py module-level names (per RESEARCH.md §3 skeleton):
- main(argv: list[str] | None = None) -> int — entry point
- DEFENSE_LOG_MAP: dict[str, str] — ablation_table.json key -> defense log filename
- TOP_K: int = 5
- N_CLEAN: int = 50
- JUDGE_SYSTEM_PROMPT: str (D-10 verbatim)
- JUDGE_USER_TEMPLATE: str (D-10 verbatim)
- parse_verdict(content: str) -> "DEGRADED" | "PRESERVED" | "TIE" | None

Schema contract for logs/ablation_table.json after Plan 03 runs (D-11):
- For each defense_key in DEFENSE_LOG_MAP (6 keys), the row dict gains 5 new keys:
  - per_chunk_fpr: float in [0.0, 1.0]
  - answer_preserved_fpr: float in [0.0, 1.0]
  - judge_fpr: float in [0.0, 1.0]
  - judge_model: str (e.g. "gpt-oss:20b-cloud")
  - judge_n_calls: int >= 50
- Existing "fpr" key MUST remain unchanged (back-compat, V-09).
- The "no_defense" row gets per_chunk_fpr=0.0, answer_preserved_fpr=0.0, judge_fpr=0.0, judge_n_calls=0 trivially (D-02).

Schema contract for logs/judge_fpr_llama.json (D-11):
- Top-level keys: "phase", "judge_model", "judge_prompt_template", "verdicts"
- verdicts: dict[defense_key, dict[query_index_str, verdict_record]]
- verdict_record keys: "verdict" ("DEGRADED|PRESERVED|TIE|REFUSAL"), "ab_assignment", "raw_response", "retry_count"
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create tests/conftest.py with ablation_snapshot + frozen_judge_cache fixtures</name>
  <files>tests/conftest.py</files>
  <read_first>
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md (lines 380-409 — conftest.py pattern; lines 552-556 — Wave-0 invariants)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-VALIDATION.md (lines 58-65 — Wave 0 requirements)
    - logs/ablation_table.json (to understand the snapshot shape — 6 defense rows + no_defense + extras)
  </read_first>
  <behavior>
    - ablation_snapshot fixture: copies real logs/ablation_table.json to tmp_path/ablation_table.json so tests can mutate it without polluting the real artifact. Returns a Path.
    - frozen_judge_cache fixture: writes a minimal pre-populated cache JSON (6 defense keys × 50 query indices, each with verdict="PRESERVED", ab_assignment="off=A,on=B", raw_response="", retry_count=0) to tmp_path/judge_fpr_llama.json.cache. Returns a Path. This pre-populates the cache so V-06 (idempotency) test can re-run main() and skip all 300 cloud calls.
    - No conftest.py exists yet (verified — first conftest.py in repo per PATTERNS.md line 381).
  </behavior>
  <action>
    Create `tests/conftest.py` (NEW file). Follow PATTERNS.md lines 384-407 verbatim, with these exact contents:

    ```python
    """Phase 5 fixtures: ablation snapshot + frozen judge cache.

    First conftest.py in this repo. Provides fixtures needed by
    tests/test_judge_fpr.py for V-06 (idempotency) and V-09 (back-compat) tests
    without mutating the real logs/ablation_table.json or burning cloud-LLM calls.
    """
    from __future__ import annotations

    import json
    import shutil
    from pathlib import Path

    import pytest

    # Mirror DEFENSE_LOG_MAP keys from scripts/run_judge_fpr.py (RESEARCH §3).
    # Kept in sync manually; if Plan 02 changes the keys, update this list.
    _DEFENSE_KEYS = [
        "def02",
        "bert_only",
        "perplexity_only",
        "imperative_only",
        "fingerprint_only",
        "fused_fixed_0.5",
        "fused_tuned_threshold",
    ]
    _N_CLEAN = 50  # indices 50-99 in defense logs (paired==False)


    @pytest.fixture
    def ablation_snapshot(tmp_path):
        """Copy of logs/ablation_table.json in tmp_path; tests can mutate freely."""
        src = Path("logs/ablation_table.json")
        if not src.exists():
            pytest.skip("logs/ablation_table.json not present in working tree")
        dst = tmp_path / "ablation_table.json"
        shutil.copy(src, dst)
        return dst


    @pytest.fixture
    def frozen_judge_cache(tmp_path):
        """Pre-populated judge cache so V-06 idempotency test makes zero cloud calls.

        Builds a minimal valid cache: each defense key maps to a dict of query
        indices (as strings) -> verdict_record. All verdicts are PRESERVED so
        downstream metrics are deterministic and the cache loader can short-circuit.
        """
        cache_path = tmp_path / "judge_fpr_llama.json.cache"
        cache = {}
        for defense_key in _DEFENSE_KEYS:
            cache[defense_key] = {
                str(50 + i): {
                    "verdict": "PRESERVED",
                    "ab_assignment": "off=A,on=B",
                    "raw_response": "PRESERVED",
                    "retry_count": 0,
                }
                for i in range(_N_CLEAN)
            }
        cache_path.write_text(json.dumps(cache, indent=2))
        return cache_path
    ```

    Use Write tool. No imports beyond stdlib + pytest.
  </action>
  <verify>
    <automated>conda run -n rag-security pytest tests/conftest.py --collect-only -q</automated>
  </verify>
  <acceptance_criteria>
    - File `tests/conftest.py` exists.
    - `grep -c "@pytest.fixture" tests/conftest.py` returns 2.
    - `grep "def ablation_snapshot" tests/conftest.py` returns 1 line.
    - `grep "def frozen_judge_cache" tests/conftest.py` returns 1 line.
    - `python -c "import json; from pathlib import Path; import importlib.util; spec=importlib.util.spec_from_file_location('cf', 'tests/conftest.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert hasattr(m, 'ablation_snapshot') and hasattr(m, 'frozen_judge_cache')"` exits 0.
    - `conda run -n rag-security pytest tests/ --collect-only -q 2>&1 | grep -i "error" | wc -l` returns 0 (no collection errors introduced).
  </acceptance_criteria>
  <done>
    tests/conftest.py exists with 2 pytest fixtures. Pytest collection succeeds with no new errors. Fixtures are importable via importlib.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create tests/test_judge_fpr.py with 9 stub tests V-01..V-09</name>
  <files>tests/test_judge_fpr.py</files>
  <read_first>
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-VALIDATION.md (lines 39-51 — V-01..V-09 test contract)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md (lines 309-376 — importlib spec_from_file_location pattern)
    - tests/test_make_results.py (lines 1-26 — verbatim copy template for the importlib skip-guard block)
    - tests/test_phase4_assets.py (lines 9-40 — secondary _try_load helper pattern reference)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-RESEARCH.md (lines 514-557 — full V-01..V-09 contract with bounds)
  </read_first>
  <behavior>
    - 9 tests covering V-01..V-09 (one method per validation sub-task).
    - Module-level pytestmark = pytest.mark.skipif(not _AVAILABLE, ...) so EVERY test SKIPS until Plan 02 lands scripts/run_judge_fpr.py.
    - Use importlib.util.spec_from_file_location (NOT `from scripts.run_judge_fpr import ...`) per PATTERNS.md line 552.
    - Each test method has a clear V-XX docstring tag and concrete assertion targets.
    - V-01 (no_defense zero): assert all three new metrics on no_defense row equal 0.0 and judge_n_calls == 0.
    - V-02 (M2 ≤ M1 numerator): for each defense, count(chunks_removed>0 AND verdict==DEGRADED) ≤ count(chunks_removed>0).
    - V-03 (judge_n_calls ≥ 50): for each of 6 defense rows, judge_n_calls >= 50.
    - V-04 (M1 in range): 0.0 ≤ per_chunk_fpr ≤ 1.0 for all 6 defense rows.
    - V-05 (M1 numerator ≤ 250): sum(chunks_removed) over clean queries ≤ TOP_K * N_CLEAN = 250.
    - V-06 (idempotent with cache): re-running main() with frozen_judge_cache produces byte-identical ablation_table.json on second run.
    - V-07 (M3 consistency): for each defense, judge_fpr * 50 == count(verdict == "DEGRADED") in logs/judge_fpr_llama.json.
    - V-08 (schema extension): each of 6 defense rows has the 5 new keys; "no_defense" row also has them (D-02 trivial fill).
    - V-09 (back-compat fpr unchanged): existing "fpr" key value on each row is unchanged after main() runs (compare to ablation_snapshot fixture pre-state).
  </behavior>
  <action>
    Create `tests/test_judge_fpr.py` (NEW file). Use Write tool.

    Header block — copy verbatim from tests/test_make_results.py:1-26 with these substitutions: `make_results` -> `run_judge_fpr`, reason string -> `"scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)"`:

    ```python
    """Wave 0 stubs for scripts/run_judge_fpr.py (Phase 5 Plan 02).

    Skips until run_judge_fpr.py is implemented. After Plan 02 lands, all 9 tests
    must pass. Covers V-01..V-09 from .planning/phases/05-*/05-VALIDATION.md.
    """
    from __future__ import annotations

    import importlib.util
    import json
    import shutil
    import sys
    from pathlib import Path

    import pytest

    _SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
    _MODULE_NAME = "run_judge_fpr"
    _MODULE_FILE = _SCRIPTS_DIR / "run_judge_fpr.py"

    try:
        _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_FILE)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        main = _mod.main
        DEFENSE_LOG_MAP = _mod.DEFENSE_LOG_MAP
        TOP_K = _mod.TOP_K
        N_CLEAN = _mod.N_CLEAN
        parse_verdict = _mod.parse_verdict
        _AVAILABLE = True
    except (AttributeError, FileNotFoundError, Exception):
        _AVAILABLE = False
        DEFENSE_LOG_MAP = {}  # placeholder so module loads cleanly during collect-only
        TOP_K = 5
        N_CLEAN = 50

    pytestmark = pytest.mark.skipif(
        not _AVAILABLE,
        reason="scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)",
    )


    NEW_KEYS = ("per_chunk_fpr", "answer_preserved_fpr", "judge_fpr", "judge_model", "judge_n_calls")


    def _load_ablation():
        return json.loads(Path("logs/ablation_table.json").read_text())


    def _load_verdicts():
        return json.loads(Path("logs/judge_fpr_llama.json").read_text())


    class TestSchemaExtension:
        def test_schema_extension(self):
            """V-08: each defense row has 5 new keys plus existing keys."""
            ablation = _load_ablation()
            for defense_key in DEFENSE_LOG_MAP:
                row = ablation[defense_key]
                for key in NEW_KEYS:
                    assert key in row, f"{defense_key} missing {key}"
            # no_defense gets trivial fill per D-02
            assert "no_defense" in ablation
            for key in NEW_KEYS:
                assert key in ablation["no_defense"], f"no_defense missing {key}"

        def test_back_compat_fpr_unchanged(self, ablation_snapshot):
            """V-09: existing fpr key on every row equals pre-Plan-03 snapshot value."""
            pre = json.loads(ablation_snapshot.read_text())
            post = _load_ablation()
            for defense_key, pre_row in pre.items():
                if "fpr" in pre_row:
                    assert post[defense_key]["fpr"] == pre_row["fpr"], (
                        f"fpr key on {defense_key} changed: {pre_row['fpr']} -> {post[defense_key]['fpr']}"
                    )


    class TestMetricBounds:
        def test_no_defense_zero(self):
            """V-01: no_defense row has all three new metrics == 0 (D-02 trivial fill)."""
            row = _load_ablation()["no_defense"]
            assert row["per_chunk_fpr"] == 0.0
            assert row["answer_preserved_fpr"] == 0.0
            assert row["judge_fpr"] == 0.0
            assert row["judge_n_calls"] == 0

        def test_m1_in_range(self):
            """V-04: 0.0 <= per_chunk_fpr <= 1.0 for all 6 defense rows."""
            ablation = _load_ablation()
            for defense_key in DEFENSE_LOG_MAP:
                m1 = ablation[defense_key]["per_chunk_fpr"]
                assert 0.0 <= m1 <= 1.0, f"{defense_key} M1={m1} out of [0,1]"

        def test_m1_numerator_bounded(self):
            """V-05: M1 numerator <= top_k * 50 = 250 (sanity bound)."""
            ablation = _load_ablation()
            denom = TOP_K * N_CLEAN
            for defense_key, log_fname in DEFENSE_LOG_MAP.items():
                log = json.loads(Path(f"logs/{log_fname}").read_text())
                clean = [r for r in log["results"] if not r.get("paired", False)]
                numerator = sum(r.get("chunks_removed", 0) for r in clean)
                assert numerator <= denom, (
                    f"{defense_key} M1 numerator {numerator} > {denom} = top_k * N_clean"
                )

        def test_m2_le_m1(self):
            """V-02: M2 numerator (chunks_removed>0 AND DEGRADED) <= M1 numerator (chunks_removed>0)."""
            verdicts_doc = _load_verdicts()
            for defense_key, log_fname in DEFENSE_LOG_MAP.items():
                log = json.loads(Path(f"logs/{log_fname}").read_text())
                clean = [r for r in log["results"] if not r.get("paired", False)]
                m1_count = sum(1 for r in clean if r.get("chunks_removed", 0) > 0)
                vds = verdicts_doc["verdicts"].get(defense_key, {})
                # Map query_index -> chunks_removed via record order (paired==False subset)
                # Use the verdicts dict's intersection with chunks_removed>0 records.
                chunk_removed_indices = {str(50 + i) for i, r in enumerate(clean) if r.get("chunks_removed", 0) > 0}
                m2_count = sum(
                    1 for q_idx, v in vds.items()
                    if v.get("verdict") == "DEGRADED" and q_idx in chunk_removed_indices
                )
                assert m2_count <= m1_count, (
                    f"{defense_key} M2 count {m2_count} > M1 count {m1_count}"
                )


    class TestJudgeConsistency:
        def test_judge_n_calls_min(self):
            """V-03: judge_n_calls >= 50 for each of the 6 defense rows."""
            ablation = _load_ablation()
            for defense_key in DEFENSE_LOG_MAP:
                n_calls = ablation[defense_key]["judge_n_calls"]
                assert n_calls >= 50, f"{defense_key} judge_n_calls={n_calls} < 50"

        def test_m3_consistency(self):
            """V-07: judge_fpr * 50 == count(verdict == DEGRADED) in per-cell file."""
            ablation = _load_ablation()
            verdicts_doc = _load_verdicts()
            for defense_key in DEFENSE_LOG_MAP:
                vds = verdicts_doc["verdicts"][defense_key]
                degraded_count = sum(1 for v in vds.values() if v.get("verdict") == "DEGRADED")
                m3 = ablation[defense_key]["judge_fpr"]
                expected = degraded_count / 50
                assert abs(m3 - expected) < 1e-9, (
                    f"{defense_key} judge_fpr={m3} disagrees with per-cell DEGRADED count {degraded_count}/50={expected}"
                )

        def test_idempotent_with_cache(self, frozen_judge_cache, tmp_path, monkeypatch):
            """V-06: re-running main() with cached verdicts produces byte-identical ablation_table.json."""
            # Snapshot pre-state, run main with frozen cache, snapshot post-state, run again, compare.
            ablation_path = Path("logs/ablation_table.json")
            pre = ablation_path.read_text()
            try:
                rc1 = main(["--cache", str(frozen_judge_cache), "--delay", "0"])
                assert rc1 == 0
                post1 = ablation_path.read_text()
                rc2 = main(["--cache", str(frozen_judge_cache), "--delay", "0"])
                assert rc2 == 0
                post2 = ablation_path.read_text()
                assert post1 == post2, "Re-run with cache produced different ablation_table.json"
            finally:
                # Restore pre-test state
                ablation_path.write_text(pre)
    ```

    Place exactly this code in `tests/test_judge_fpr.py`. Do NOT add additional helpers. Do NOT remove the broad `(AttributeError, FileNotFoundError, Exception)` except clause — collect-only must succeed before Plan 02 lands.
  </action>
  <verify>
    <automated>conda run -n rag-security pytest tests/test_judge_fpr.py --collect-only -q</automated>
  </verify>
  <acceptance_criteria>
    - File `tests/test_judge_fpr.py` exists.
    - `grep -c "def test_" tests/test_judge_fpr.py` returns 9.
    - `grep "spec_from_file_location" tests/test_judge_fpr.py` returns at least 1 line.
    - `grep "pytestmark = pytest.mark.skipif" tests/test_judge_fpr.py` returns 1 line.
    - `grep -E "V-0[1-9]" tests/test_judge_fpr.py | wc -l` returns >= 9 (every V-tag commented in a docstring).
    - `conda run -n rag-security pytest tests/test_judge_fpr.py --collect-only -q 2>&1 | grep -E "9 tests collected|9 selected"` matches.
    - `conda run -n rag-security pytest tests/test_judge_fpr.py -q 2>&1 | grep -E "9 skipped"` matches (every test SKIPS today because scripts/run_judge_fpr.py does not yet exist).
    - `conda run -n rag-security pytest tests/ -x --collect-only -q 2>&1 | grep -i "error" | wc -l` returns 0 (no new collection errors in the broader suite).
  </acceptance_criteria>
  <done>
    tests/test_judge_fpr.py exists with 9 stub tests covering V-01..V-09; all 9 SKIP cleanly today; pytest --collect-only succeeds with zero errors. After Plan 03 lands real artifacts, all 9 tests will run and pass.
  </done>
</task>

</tasks>

<verification>
- `conda run -n rag-security pytest tests/test_judge_fpr.py -q` — expects "9 skipped" exactly.
- `conda run -n rag-security pytest tests/ -x` — full suite still green (no new failures, no new collection errors).
- `python -c "import json; spec=__import__('importlib').util.spec_from_file_location('cf', 'tests/conftest.py'); m=__import__('importlib').util.module_from_spec(spec); spec.loader.exec_module(m); assert hasattr(m, 'ablation_snapshot')"` — fixtures importable.
</verification>

<success_criteria>
- 9 stub tests in tests/test_judge_fpr.py all SKIP today (red state expected pre-Plan-02).
- 2 fixtures in tests/conftest.py importable via importlib.
- pytest collection emits 0 errors before AND after this plan.
- File-naming, docstring tags, and importlib idiom match Phase 3.4 Wave-0 conventions (PATTERNS.md lines 309-376).
- Plan 02 can land scripts/run_judge_fpr.py and tests will auto-unmark via _AVAILABLE flip.
</success_criteria>

<output>
After completion, create `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-01-SUMMARY.md` documenting:
- The 9 stub tests created (one bullet per V-XX with method name).
- The 2 fixtures created (with their tmp_path usage).
- The exact "9 skipped" pytest output before Plan 02.
- Confirmation that the importlib skip-guard pattern matches tests/test_make_results.py:1-26 verbatim.
</output>
