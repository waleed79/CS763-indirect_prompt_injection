---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: 05
type: execute
wave: 3
depends_on: [03]
files_modified:
  - docs/phase3_results.md
  - scripts/_build_ablation_table.py
autonomous: true
requirements: []
tags: [callout, documentation, light-touch-edit]
must_haves:
  truths:
    - "docs/phase3_results.md section 4 ends with a single-paragraph addendum pointing to docs/phase5_honest_fpr.md"
    - "scripts/_build_ablation_table.py docstring has a WARNING comment about Phase 5 schema preservation (RESEARCH section 5.6)"
    - "All other paragraphs in docs/phase3_results.md section 4 are unchanged (D-08: do NOT mutate the submitted artifact beyond the callout)"
    - "scripts/_build_ablation_table.py extract_row function and rebuild flow are unchanged (RESEARCH section 1.3)"
    - "docs/phase3_results.md still passes tests/test_writeup_structure.py (no regressions in numbered-heading contract)"
  artifacts:
    - path: "docs/phase3_results.md"
      provides: "Phase 3 results doc with addendum callout"
      contains: "phase5_honest_fpr.md, post-submission addendum"
    - path: "scripts/_build_ablation_table.py"
      provides: "Phase 3.1 ablation rebuild script with Phase 5 schema-preservation warning"
      contains: "WARNING and run_judge_fpr"
  key_links:
    - from: "docs/phase3_results.md"
      to: "docs/phase5_honest_fpr.md"
      via: "single-paragraph addendum at end of section 4"
      pattern: "phase5_honest_fpr\\.md"
    - from: "scripts/_build_ablation_table.py"
      to: "scripts/run_judge_fpr.py"
      via: "docstring warning recommending re-run after rebuild"
      pattern: "run_judge_fpr"
---

<objective>
Two light-touch edits to support Phase 5's deliverables:

1. Append one paragraph to docs/phase3_results.md section 4 pointing readers to the new addendum at docs/phase5_honest_fpr.md. Per D-08, this is the ONLY change to the already-submitted Phase 3.4 deliverable. Do NOT regenerate Figure 2, do NOT mutate the headline 76% number, do NOT alter any other paragraph.

2. Add a WARNING comment to the docstring of scripts/_build_ablation_table.py (RESEARCH section 5.6) explaining that re-running the rebuild script will wipe Phase 5's additive keys and listing the recovery path (re-run scripts/run_judge_fpr.py to restore them). Per RESEARCH section 1.3, the extract_row function and the rebuild flow itself are NOT modified.

Purpose: Thread Phase 5's three honest metrics back into the Phase 3.4 narrative without violating D-08 (no mutation of submitted artifact) and protect Phase 5's schema extension from accidental loss when a future contributor runs the rebuild script.

Output: 2 single-spot edits.

This plan runs in parallel with Plan 04 (writeup) — different files, no conflicts.
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
@docs/phase3_results.md
@scripts/_build_ablation_table.py
@tests/test_writeup_structure.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Append section 4 addendum paragraph to docs/phase3_results.md</name>
  <files>docs/phase3_results.md</files>
  <read_first>
    - docs/phase3_results.md (read lines 200-230: the tail of section 4 right before the separator; this is the insertion point per PATTERNS.md line 444)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md (lines 440-466: exact insertion point + suggested wording)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-CONTEXT.md (lines 191-194: D-08 constraint + suggested wording)
    - tests/test_writeup_structure.py (entire file: confirm what invariants this edit must NOT break; particularly the numbered-heading contract for `## N.` patterns)
  </read_first>
  <behavior>
    - Open docs/phase3_results.md.
    - Locate section 4 (Utility-Security Tradeoff). Find the LAST prose paragraph in section 4, immediately before the `---` separator that introduces section 5.
    - Append a NEW paragraph after the last existing paragraph but before the `---` separator. The paragraph is one sentence, ~3-4 lines.
    - Do NOT modify any prior paragraph in section 4. Do NOT regenerate Figure 2. Do NOT alter the headline 76% number anywhere. Do NOT touch any heading.
    - Post-edit, verify tests/test_writeup_structure.py still passes (numbered-heading contract intact, all original heading literals still present).
  </behavior>
  <action>
    1. Use Read to load docs/phase3_results.md, especially lines 200-230 (the section 4 tail). Identify the exact line number of the last paragraph of section 4 and the line number of the `---` separator.
    2. Use Edit tool. old_string = the last paragraph of section 4 (verbatim, including any trailing newline) AND the `---` separator. new_string = same last paragraph + blank line + new addendum paragraph + blank line + `---`.
    3. The exact addendum paragraph to insert (verbatim, three lines):

```
**Post-submission addendum (Phase 5).** After Phase 3.4 submission, three more honest FPR metrics were computed to refine the 76% upper bound into per-chunk, answer-preserved, and judge-scored variants. See `docs/phase5_honest_fpr.md` for the methodology and per-defense breakdown.
```

    4. Save and verify with the test command. If tests/test_writeup_structure.py was passing before, it must still be passing after.

    Critical invariants (D-08 mitigation):
    - Do NOT mutate any other paragraph in section 4.
    - Do NOT regenerate any figure file (docs/figures/d04_fpr_*.png etc.).
    - Do NOT alter the headline "76%" or "0.76" number anywhere in the doc.
    - Do NOT change any `##` heading text or numbering.
    - The diff for this task should be a small additive change: ~3-5 new lines, 0 deletions (apart from the necessary single newline split before/after the inserted paragraph).
  </action>
  <verify>
    <automated>grep -c "phase5_honest_fpr.md" docs/phase3_results.md && grep -c "Post-submission addendum" docs/phase3_results.md && conda run -n rag-security pytest tests/test_writeup_structure.py -x -q</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "phase5_honest_fpr.md" docs/phase3_results.md` returns 1 (exactly one reference).
    - `grep -c "Post-submission addendum" docs/phase3_results.md` returns 1.
    - `grep -c "76%" docs/phase3_results.md` returns the same count as before. Capture pre-count via `git show HEAD:docs/phase3_results.md | grep -c "76%"` before editing; the post-edit count MUST equal it.
    - `grep -cE "^## [0-9]+\." docs/phase3_results.md` returns exactly 13 (matches Phase 3.4 contract enforced by tests/test_writeup_structure.py per STATE.md Phase 03.4-05).
    - `conda run -n rag-security pytest tests/test_writeup_structure.py -x -q` shows passing tests, NO failures.
    - `git diff --numstat docs/phase3_results.md` shows ≤8 added lines, 0 deleted lines (light-touch).
    - The new paragraph appears within section 4 (not in section 5 or later). Verify with `grep -B 5 "Post-submission addendum" docs/phase3_results.md` showing section 4 context (CSP analog or section 4 heading) and `grep -A 3 "Post-submission addendum" docs/phase3_results.md` showing the `---` separator next.
  </acceptance_criteria>
  <done>
    docs/phase3_results.md has one new paragraph at the end of section 4 pointing to docs/phase5_honest_fpr.md. All other content is byte-identical to pre-edit. tests/test_writeup_structure.py still green.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add WARNING comment to scripts/_build_ablation_table.py docstring</name>
  <files>scripts/_build_ablation_table.py</files>
  <read_first>
    - scripts/_build_ablation_table.py (read lines 1-15: the existing module docstring; insertion point is between the last line of the docstring and `import json`)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md (lines 469-498: exact warning wording + insertion-point guidance)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-RESEARCH.md (lines 629-640: RESEARCH section 5.6 mitigation rationale)
  </read_first>
  <behavior>
    - Open scripts/_build_ablation_table.py.
    - Locate the existing module docstring (lines 1-5 per PATTERNS.md line 472-475).
    - Append (within the same docstring) a WARNING block referencing both Phase 3.2 (scripts/_assemble_ablation.py) and Phase 5 (scripts/run_judge_fpr.py) extension scripts.
    - Do NOT modify any code below the docstring (no changes to imports, extract_row, the rebuild loop, or anything else per RESEARCH section 1.3 invariant).
  </behavior>
  <action>
    1. Use Read to load scripts/_build_ablation_table.py lines 1-15.
    2. Use the Edit tool. The replacement appends a WARNING block to the existing docstring. If the existing docstring differs from PATTERNS.md line 472-475, preserve all existing lines and append the WARNING block at the end of the docstring (before the closing triple-quote).

       Pattern of the new docstring tail (verbatim, 6 lines of WARNING content):

```
WARNING: this script rebuilds ablation_table.json from per-defense logs and
wipes any keys not produced by extract_row(). If you have run
scripts/_assemble_ablation.py (Phase 3.2 causal-attribution keys) or
scripts/run_judge_fpr.py (Phase 5 honest-FPR keys: per_chunk_fpr,
answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls) to extend the
schema, re-run those scripts after this one to restore the extended schema.
```

    3. Do NOT modify any other line in scripts/_build_ablation_table.py.
  </action>
  <verify>
    <automated>conda run -n rag-security python -c "import importlib.util; spec=importlib.util.spec_from_file_location('bat', 'scripts/_build_ablation_table.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert 'WARNING' in m.__doc__ and 'run_judge_fpr.py' in m.__doc__ and '_assemble_ablation.py' in m.__doc__; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "WARNING" scripts/_build_ablation_table.py` returns 1 (exactly one new WARNING block).
    - `grep -c "run_judge_fpr.py" scripts/_build_ablation_table.py` returns 1.
    - `grep -c "_assemble_ablation.py" scripts/_build_ablation_table.py` returns 1.
    - `grep -c "per_chunk_fpr" scripts/_build_ablation_table.py` returns 1 (the warning lists the new keys).
    - The python -c importlib check passes (docstring contains the three required substrings).
    - `git diff --numstat scripts/_build_ablation_table.py` shows ≤7 added lines, 0 deleted lines.
    - `grep -E "^def extract_row" scripts/_build_ablation_table.py` still matches (function signature unchanged).
    - The script still runs without errors as a smoke test: `conda run -n rag-security python -c "import importlib.util; spec=importlib.util.spec_from_file_location('bat', 'scripts/_build_ablation_table.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(hasattr(m, 'extract_row'))"` returns `True`.
    - No code changes outside the docstring: `git diff scripts/_build_ablation_table.py` shows changes ONLY in lines 1-15 (the docstring region).
  </acceptance_criteria>
  <done>
    scripts/_build_ablation_table.py docstring contains the WARNING block. extract_row and the rebuild flow are byte-identical to pre-edit. Future contributors running the rebuild script will see the warning and know to re-run scripts/run_judge_fpr.py to restore Phase 5 schema.
  </done>
</task>

</tasks>

<verification>
- `git diff --stat docs/phase3_results.md scripts/_build_ablation_table.py` shows tiny diffs in both files (≤10 lines total each).
- `conda run -n rag-security pytest tests/test_writeup_structure.py -x -q` — green.
- `conda run -n rag-security pytest tests/test_judge_fpr.py -x -q` — still green (Plan 03 artifacts unaffected by these edits).
- Manual: open docs/phase3_results.md and verify the addendum paragraph reads naturally as the closing thought of section 4 before transitioning to section 5.
</verification>

<success_criteria>
- docs/phase3_results.md gains exactly one paragraph at the end of section 4 (no other changes).
- scripts/_build_ablation_table.py gains a WARNING block in its docstring (no other changes).
- All existing tests still pass (test_writeup_structure.py + test_judge_fpr.py both green).
- D-08 invariant preserved: the headline 76% number, all section 4 figures, all other section 4 paragraphs are byte-identical to the pre-edit state.
- RESEARCH section 1.3 invariant preserved: extract_row and the rebuild loop in _build_ablation_table.py are byte-identical to the pre-edit state.
</success_criteria>

<output>
After completion, create `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-05-SUMMARY.md` documenting:
- The exact paragraph appended to docs/phase3_results.md (quote it).
- The exact WARNING block appended to scripts/_build_ablation_table.py docstring (quote it).
- git diff --stat output for both files (line counts confirming light-touch).
- Confirmation that pre/post 76% counts in docs/phase3_results.md are equal.
- Confirmation that tests/test_writeup_structure.py is still green.
- Phase 5 wrap-up summary: list of the 5 SUMMARY files (01..05) produced across all plans + final state of logs/ablation_table.json (bytes / md5 / row count).
</output>
