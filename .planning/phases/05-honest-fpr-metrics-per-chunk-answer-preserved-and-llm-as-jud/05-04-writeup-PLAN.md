---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: 04
type: execute
wave: 3
depends_on: [03]
files_modified:
  - docs/phase5_honest_fpr.md
autonomous: true
requirements: []
tags: [writeup, documentation, results]
must_haves:
  truths:
    - "docs/phase5_honest_fpr.md exists with all 6 numbered sections per CONTEXT D-09"
    - "Headline frames 76% as 'loose upper bound' refined into three honest metrics (D-09)"
    - "Section 4 contains a 4-column results table with 7 active-defense rows per D-01 (FPR (orig 76%-style) | per_chunk_fpr | answer_preserved_fpr | judge_fpr)"
    - "Section 3 cites MT-Bench (Zheng et al., 2023) for pairwise-judge position bias mitigation (RESEARCH §2.5)"
    - "Section 3 includes the no_defense provenance sentence: judge_n_calls = 0 is the canonical no-calls signal; judge_model is set for schema consistency only (D-02)"
    - "Section 6 enumerates limitations: single-seed, single-judge, single-LLM-target, 50-query eval set"
    - "Section 5 (Discussion) calls out the 'INFILTRATED leakage' interpretation that M3 captures both removed-utility AND removed-attack-leakage (RESEARCH §5.5)"
    - "All numbers in tables read from logs/ablation_table.json verbatim (no manual transcription drift)"
  artifacts:
    - path: "docs/phase5_honest_fpr.md"
      provides: "Standalone Phase 5 writeup deliverable"
      min_lines: 80
      contains: "## 1. Motivation, ## 2. The three metrics, ## 3. Methodology, ## 4. Results, ## 5. Discussion, ## 6. Limitations"
  key_links:
    - from: "docs/phase5_honest_fpr.md"
      to: "logs/ablation_table.json"
      via: "Section 4 results table reads canonical values"
      pattern: "per_chunk_fpr|answer_preserved_fpr|judge_fpr"
    - from: "docs/phase5_honest_fpr.md"
      to: "scripts/run_judge_fpr.py"
      via: "Section 3 methodology cites the entry point + judge prompt verbatim"
      pattern: "scripts/run_judge_fpr\\.py"
---

<objective>
Author the standalone Phase 5 writeup `docs/phase5_honest_fpr.md` per the 6-section contract locked in CONTEXT D-09. The doc explains why the headline 76% query-level FPR is a loose upper bound, defines the three honest metrics, documents the judge methodology (with MT-Bench position-bias citation and the no_defense provenance note per D-02), presents the per-defense results table for all 7 active defenses (D-01), discusses the surprising "removed-attack-leakage" interpretation (RESEARCH §5.5), and lists single-seed/single-judge/single-LLM/50-query limitations.

This is a code-light, prose-heavy plan — no Python changes, just a single Markdown file. All numerical values are read directly from the artifacts Plan 03 produced.

Purpose: Pin down the user-visible cost of the fused defense in narrative form so Phase 4 (final presentation) and the Phase 3.4 callout (Plan 05) have a canonical reference.

Output: docs/phase5_honest_fpr.md (~80-150 lines).
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
@docs/xss_ssrf_taxonomy.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write docs/phase5_honest_fpr.md following the 6-section contract from CONTEXT D-09</name>
  <files>docs/phase5_honest_fpr.md</files>
  <read_first>
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-CONTEXT.md (lines 65-83 — D-09 6-section structure verbatim)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-RESEARCH.md (lines 280-310 — RESEARCH §2.2 on the INFILTRATED leakage finding for §5; lines 369-382 — MT-Bench citation for §3)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-PATTERNS.md (lines 268-305 — header + sub-table style from docs/phase3_results.md)
    - docs/phase3_results.md (lines 1-30 — header metadata block; lines 184-210 — sub-table column alignment style; lines 199-209 — the §4 paragraph that gets the addendum callout in Plan 05, for cross-reference consistency)
    - logs/ablation_table.json (read entire file — extract verbatim values for the §4 table; planner-verified to contain all 7 active-defense rows per D-01)
    - logs/judge_fpr_llama.json (read top-level keys + spot-check verdict counts for §3 methodology section)
    - scripts/run_judge_fpr.py (read JUDGE_SYSTEM_PROMPT and JUDGE_USER_TEMPLATE constants — these go verbatim into §2 + §3 of the writeup)
  </read_first>
  <action>
    Create `docs/phase5_honest_fpr.md` (NEW file). Use Write tool. The doc has the following exact structure:

    **Header block** (verbatim PATTERNS.md line 274-285 style — adapt strings to Phase 5):
    ```markdown
    # Phase 5: Honest FPR Metrics — Per-Chunk, Answer-Preserved, and LLM-as-Judge

    **Course:** CS 763 (Computer Security) — UW-Madison Spring 2026
    **Team:** Musa & Waleed
    **Phase:** 5 (post-submission addendum to Phase 3.4)
    **Document status:** Final.
    **Source artifacts:** scripts/run_judge_fpr.py + logs/judge_fpr_llama.json + logs/ablation_table.json + logs/defense_*_llama.json
    **Eval set:** 50 clean queries (indices 50–99 in data/test_queries.json), llama3.2:3b target, 7 active defense configurations (per D-01).

    ---
    ```

    **§ 1. Motivation** (~150-200 words):
    - Open with the headline framing from D-09: "76% is the upper bound under the strictest interpretation (≥1 chunk removed = false positive). The three honest metrics — per-chunk X%, answer-preserved Y%, judge Z% — refine this upper bound into the user-visible cost." Substitute X, Y, Z with actual percentages read from logs/ablation_table.json for the fused_fixed_0.5 row.
    - Explain why query-level "≥1 removed" overstates user cost (per CONTEXT D-09): per-chunk normalizes for retrieval depth; answer-preserved conditions on user-visible effect; judge captures semantic equivalence under paraphrase.
    - Important: NO retraction language. The 76% number remains correct under its stated definition; the new metrics refine the cost interpretation, they do not invalidate Phase 3.4.

    **§ 2. The three metrics** (~200-300 words):
    - Formal definition + denominator for each metric (CONTEXT lines 152-171 verbatim formulas):
      - **Per-chunk FPR (M1)** = sum(chunks_removed) over 50 clean queries / (top_k × 50) = numerator / 250.
      - **Answer-preserved FPR (M2)** = |{q ∈ clean : chunks_removed[q] > 0 AND judge[q] == DEGRADED}| / 50.
      - **Judge FPR (M3)** = |{q ∈ clean : judge[q] == DEGRADED}| / 50.
    - Present the judge prompt verbatim (the JUDGE_USER_TEMPLATE from scripts/run_judge_fpr.py, in a fenced ``` code block so reviewers can audit wording).
    - Note explicitly that M2 ⊆ flagged set ∩ degraded set, while M3 is the unconditional degraded rate. M2 isolates "user actually suffered" cases.

    **§ 3. Methodology** (~250-350 words):
    - Judge model: gpt-oss:20b-cloud (D-03), accessed via Ollama at temperature=0.0, --delay 3 between calls.
    - Eval set: 50 clean queries (paired==False, indices 50-99). No re-inference — defense-off and defense-on answer strings come from the existing logs/defense_*_llama.json artifacts (D-04).
    - **no_defense row provenance (D-02):** "The `no_defense` row reports `judge_n_calls = 0` (no judge calls were issued — chunks_removed is 0 by construction); the `judge_model` field is populated for schema consistency only and does not imply judge invocation." Include this sentence verbatim in the methodology subsection so reviewers can verify the audit trail without ambiguity.
    - Single-seed call convention: one judge call per (defense, query) pair across the 7 active defenses (D-01); no_defense is excluded from judge calls per D-02. **Standing caveat (D-05):** "All judge numbers in this addendum are single-seed, mirroring the Phase 3.3-07 EVAL-V2-01 single-seed convention. CIs at n=50 are wide (~±7pp at 95%); we accept the imprecision in exchange for consistency with prior phases."
    - Position-bias mitigation: A/B order randomization with logged assignment per record (D-10). Cite **MT-Bench (Zheng et al., 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS 2023 Datasets & Benchmarks Track, arXiv:2306.05685)** § 4.3 for the canonical pairwise-judge-position-bias result; AlpacaEval 2.0 (Dubois et al., 2024) uses the same convention. Our protocol logs `ab_assignment` per record (`off=A,on=B` or `off=B,on=A`) so reviewers can audit.
    - Edge handling (D-12): TIE → counted as PRESERVED; refusals/parse failures retried once, then PRESERVED. This is conservative for the defense (does not inflate FPR by counting ambiguity as degradation).
    - Reproducibility: a grader running `python scripts/run_judge_fpr.py --model gpt-oss:20b-cloud --delay 3` from a clean checkout reproduces the per-cell verdicts via the cache file. Wall clock ~35-55 minutes for 350 cloud calls (7 active defenses × 50 queries per D-01).

    **§ 4. Results** (the headline section — table + brief narrative):
    - Open with one sentence: "The three honest metrics for each of the 7 active defense configurations on llama3.2:3b are:" then a 4-column pipe table.
    - Table format (per PATTERNS.md lines 290-300 alignment style — exactly 7 active-defense rows per D-01):
      ```
      | Defense                      | FPR (≥1 removed) | Per-chunk FPR | Answer-preserved FPR | Judge FPR |
      |:-----------------------------|-----------------:|--------------:|---------------------:|----------:|
      | DEF-02 (system prompt)       |              ... |           ... |                  ... |       ... |
      | BERT only                    |              ... |           ... |                  ... |       ... |
      | Perplexity only              |              ... |           ... |                  ... |       ... |
      | Imperative only              |              ... |           ... |                  ... |       ... |
      | Fingerprint only             |              ... |           ... |                  ... |       ... |
      | **Fused (fixed θ=0.5)**      |              ... |           ... |                  ... |       ... |
      | Fused (tuned θ=0.10)         |              ... |           ... |                  ... |       ... |
      ```
      Read each numeric cell verbatim from `logs/ablation_table.json` (rows: `def02`, `bert_only`, `perplexity_only`, `imperative_only`, `fingerprint_only`, `fused_fixed_0.5`, `fused_tuned_threshold` — all 7 verified present per D-01) — for `fpr` use existing key, for the three new metrics use `per_chunk_fpr`, `answer_preserved_fpr`, `judge_fpr`. Format to 2 decimal places. Bold the fused_fixed_0.5 row (the headline defense from Phase 3.1). All 7 rows MUST appear; do NOT omit fused_tuned_threshold.
    - One paragraph after the table summarizing the gap: "On the fused defense, per-chunk FPR is X%, answer-preserved FPR is Y%, and judge FPR is Z% — all materially below the 76% upper bound. The gap reveals that even on clean queries where some chunk gets filtered, the user usually still gets the right answer." Substitute actual numbers.

    **§ 5. Discussion** (~250-300 words):
    - Lead with the "what the gap reveals" paragraph (CONTEXT D-09 §5): why M1 ≪ original FPR (most clean queries have multiple chunks but only one or two get removed, normalizing for retrieval depth shrinks the number); why M3 may be lower than expected (RESEARCH §5.5 — defense sometimes filters anchor-token-leaked retrievals, improving the answer; the judge correctly calls these PRESERVED or TIE). Quote the surprising INFILTRATED finding from RESEARCH §2.2 verbatim — defense-off baseline produced "INFILTRATED." on a *clean* query where unfiltered retrieval pulled a Tier-1 poisoned passage into top-5; fused defense filtered it and produced a clean refusal.
    - Bullet for the audit-trail value of M3 over M1: M3 captures both **removed legitimate content** (true utility cost) and **removed poisoned content that leaked into clean-query top-k retrievals** (utility *gain*). Both effects are folded into the headline; the per-cell verdict file at `logs/judge_fpr_llama.json` lets auditors disaggregate by examining DEGRADED verdicts query-by-query.
    - Optional: if the leakage subset is non-trivial (count of clean queries where defense-off answer contains any of HACKED/COMPROMISED/INFILTRATED/SYSTEM_OVERRIDE/PAYLOAD_DELIVERED), report it as a sentence — "On N of 50 clean queries the defense-off baseline returned an anchor-token-contaminated answer; on those queries the defense's removal arguably *improved* utility, and the judge correctly classified them as PRESERVED or TIE." If unable to compute quickly, omit this sentence (it is RESEARCH §5.5 "Optional Claude's-discretion sub-analysis").
    - One paragraph reconciling Phase 3.4: the original 76% upper bound remains correct for its stated definition (≥1 chunk removed); the three honest metrics are not corrections but refinements that disaggregate the cost signal.

    **§ 6. Limitations** (~150 words, bullet list):
    - Single-seed judge calls (D-05) — wider CIs than 3-seed majority would yield; ~±7pp at n=50.
    - Single judge model (gpt-oss:20b-cloud) — cross-judge sanity check (e.g. gemma4:31b-cloud on a 20-query subset) is deferred to Future Work (CONTEXT §deferred).
    - Single LLM target (llama3.2:3b) — does not establish whether utility cost generalizes to mistral or gemma4 (CONTEXT §deferred).
    - 50-query eval set — small; CIs accordingly wide.
    - No bootstrap CIs reported (CONTEXT §deferred — recommended but not blocking).
    - Position bias only mitigated by single-shot randomization with logged assignment, not by swap-stability filtering as in MT-Bench § 4.3.

    **References** (footer — plain numbered list per STATE.md Phase 03.4-05 entry):
    ```
    ## References

    1. Zheng et al., 2023. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."
       NeurIPS 2023 Datasets & Benchmarks Track. arXiv:2306.05685.
    2. Dubois et al., 2024. "Length-Controlled AlpacaEval: A Simple Way to Debias
       Automatic Evaluators." arXiv:2404.04475.
    ```

    **Implementation notes:**
    - Read all percentages from logs/ablation_table.json — do NOT hardcode hypothetical numbers. All 7 active-defense rows MUST appear in the §4 table per D-01 (planner-verified that fused_tuned_threshold is present in the JSON; do NOT silently omit it).
    - Use plain Markdown pipe tables, NOT raw `|` text patterns. Per STATE.md Phase 03.4-05, Google Docs paste preserves them.
    - Use plain numbered list for references (NOT `[^N]` footnote syntax) per STATE.md Phase 03.4-05.
    - Doc is ASCII-safe — no em dashes (`—`) where ASCII works, but the docs/phase3_results.md analog uses em dashes throughout, so they are acceptable.
    - Total length target: 80-150 lines including the table and code blocks. Stay focused — this is a 1-2 day phase, not a full report.

    Use Write tool to create the file in one pass.
  </action>
  <verify>
    <automated>python -c "import re; t=open('docs/phase5_honest_fpr.md').read(); [exec('assert f\"## {n}.\" in t, n', {'t': t, 'n': n}) for n in range(1, 7)]; assert 'gpt-oss:20b-cloud' in t; assert 'MT-Bench' in t or 'Zheng' in t; assert '2306.05685' in t; assert 'Limitations' in t; assert 'judge_n_calls' in t and 'schema consistency' in t.lower(), 'no_defense provenance sentence missing'; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - File `docs/phase5_honest_fpr.md` exists.
    - File ≥80 lines: `wc -l docs/phase5_honest_fpr.md` returns ≥80.
    - All 6 numbered headings present: `grep -cE "^## [1-6]\." docs/phase5_honest_fpr.md` returns exactly 6.
    - Specific section names present: `grep -E "^## 1\. Motivation" docs/phase5_honest_fpr.md` matches; same for "Three", "Methodology", "Results", "Discussion", "Limitations".
    - Judge model cited: `grep -c "gpt-oss:20b-cloud" docs/phase5_honest_fpr.md` returns ≥1.
    - MT-Bench citation present: `grep -E "MT-Bench|Zheng" docs/phase5_honest_fpr.md` matches AND `grep "2306.05685" docs/phase5_honest_fpr.md` matches.
    - Results table present: `grep -c "Per-chunk FPR" docs/phase5_honest_fpr.md` returns ≥1 AND the table has a header row + exactly 7 active-defense data rows (`grep -cE "^\| (DEF-02|BERT only|Perplexity only|Imperative only|Fingerprint only|\*\*Fused \(fixed|Fused \(tuned)" docs/phase5_honest_fpr.md` returns 7) per D-01.
    - fused_tuned_threshold row present: `grep -E "Fused \(tuned" docs/phase5_honest_fpr.md` matches (D-01: row MUST NOT be omitted).
    - Standing caveat about single-seed: `grep -E "single-seed|single seed" docs/phase5_honest_fpr.md` matches.
    - "76%" or "0.76" upper-bound framing present: `grep -E "76%|0\.76" docs/phase5_honest_fpr.md` matches.
    - **no_defense provenance sentence present (D-02):** `grep -E "judge_n_calls.*0" docs/phase5_honest_fpr.md` matches AND `grep -iE "schema consistency|schema-shape" docs/phase5_honest_fpr.md` matches (the §3 methodology sentence about no_defense audit-trail provenance).
    - Numbers in §4 table actually read from ablation_table.json (manual spot-check: pick the fused_fixed_0.5 row's per_chunk_fpr in the JSON, multiply by 100, format to 2 decimals — value must appear in the doc's table).
    - Header metadata block present: `grep -E "^\\*\\*Course:\\*\\*" docs/phase5_honest_fpr.md` matches AND `grep -E "^\\*\\*Source artifacts:\\*\\*" docs/phase5_honest_fpr.md` matches.
    - References section present at end: `grep -E "^## References$" docs/phase5_honest_fpr.md` matches.
    - No `[^N]` footnote syntax: `grep -cE "\[\^[0-9]" docs/phase5_honest_fpr.md` returns 0 (per STATE.md Phase 03.4-05 Google Docs paste compatibility).
  </acceptance_criteria>
  <done>
    docs/phase5_honest_fpr.md exists with all 6 sections, headline framing, methodology with MT-Bench citation AND no_defense provenance sentence (D-02), results table with verbatim numbers from logs/ablation_table.json for all 7 active defenses (D-01 — fused_tuned_threshold included), discussion calling out the leakage interpretation, and explicit limitations. ~80-150 lines. Plan 05 callout in docs/phase3_results.md §4 can now reference this file.
  </done>
</task>

</tasks>

<verification>
- Render the markdown (open in any preview tool); confirm pipe table renders cleanly with all 7 active-defense rows.
- Cross-check §4 table values against `logs/ablation_table.json` — every cell traceable to a JSON key for all 7 active rows.
- Confirm reference 1 cites MT-Bench arXiv ID 2306.05685.
- Confirm §3 contains the no_defense provenance sentence (D-02).
</verification>

<success_criteria>
- File length 80-150 lines.
- All 6 numbered headings present.
- §4 results table has header + exactly 7 active-defense rows (per D-01) with verbatim values from ablation_table.json.
- §3 methodology cites MT-Bench (Zheng et al., 2023) for position-bias mitigation.
- §3 methodology includes the no_defense provenance sentence (D-02): judge_n_calls=0 is the canonical no-calls signal; judge_model is set for schema consistency only.
- §5 discussion includes the INFILTRATED leakage interpretation.
- §6 limitations enumerates single-seed, single-judge, single-LLM, 50-query.
- Plain numbered references (not [^N] footnotes).
- Headline frames 76% as loose upper bound, NOT as retraction.
</success_criteria>

<output>
After completion, create `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-04-SUMMARY.md` documenting:
- Final line count of docs/phase5_honest_fpr.md.
- The §4 results table reproduced verbatim with all 7 active-defense rows (so the SUMMARY itself is auditable).
- Confirmation that the §3 no_defense provenance sentence is present (D-02).
- One sentence on the §5 discussion narrative (did the leakage finding apply, or was the optional sub-analysis omitted?).
- Confirmation that the headline framing is "loose upper bound" (not retraction).
- Any divergence from the D-09 6-section structure with rationale, or "no divergence" if exact.
</output>
