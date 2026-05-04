---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: 03
type: execute
wave: 2
depends_on: [02]
files_modified:
  - logs/judge_fpr_llama.json
  - logs/ablation_table.json
  - logs/judge_fpr_llama.json.cache
autonomous: false
requirements: []
tags: [execution, cloud-llm, judge-run]
user_setup:
  - service: ollama-cloud
    why: "gpt-oss:20b-cloud judge model requires Ollama cloud authentication"
    env_vars: []
    dashboard_config:
      - task: "Confirm `ollama login` is active before running"
        location: "Local terminal — run `ollama list` and verify gpt-oss:20b-cloud is accessible (matches Phase 02.4 / 03.3-07 convention)"
must_haves:
  truths:
    - "logs/judge_fpr_llama.json exists with 7 defense keys × 50 verdict records each (350 verdicts total per D-01)"
    - "logs/ablation_table.json has per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls on all 8 ablation rows (7 active defenses + no_defense trivial fill per D-02)"
    - "Existing fpr key on every row is unchanged (V-09 back-compat preserved)"
    - "All 9 Plan 01 tests pass when run against the new artifacts"
    - "M3 verdicts are NOT all-degraded (sanity: at least one PRESERVED in the corpus per RESEARCH §2.2 pre-flight)"
    - "Re-running scripts/run_judge_fpr.py with the cache produces byte-identical ablation_table.json (V-06 idempotence)"
  artifacts:
    - path: "logs/judge_fpr_llama.json"
      provides: "Per-cell judge verdicts for 7 defenses × 50 clean queries (350 total per D-01)"
      contains: '"phase": "05", "judge_model": "gpt-oss:20b-cloud", "verdicts"'
    - path: "logs/ablation_table.json"
      provides: "Extended ablation table with three honest FPR metrics per defense row (all 7 active rows + no_defense trivial fill)"
      contains: "per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls"
  key_links:
    - from: "logs/ablation_table.json"
      to: "logs/judge_fpr_llama.json"
      via: "judge_fpr value matches DEGRADED count / 50 per defense (V-07)"
      pattern: "judge_fpr"
    - from: "logs/ablation_table.json"
      to: "logs/defense_*_llama.json"
      via: "per_chunk_fpr numerator = sum(chunks_removed[clean]) per defense"
      pattern: "per_chunk_fpr"
---

<objective>
Execute `scripts/run_judge_fpr.py` against the live `gpt-oss:20b-cloud` judge to populate `logs/judge_fpr_llama.json` (350 per-cell verdicts: 7 active defenses × 50 clean queries per D-01) and extend `logs/ablation_table.json` with the three honest FPR metrics on all 8 ablation rows (7 active + no_defense trivial fill per D-02). Then run the full Plan 01 test suite to confirm V-01..V-09 all pass.

Purpose: Convert the locked code from Plan 02 into the actual deliverable artifacts that Plans 04 (writeup) and 05 (callout) consume. This is the only plan in Phase 5 that burns cloud-LLM compute.

Output: 3 artifacts populated/mutated; 9 V-tests passing.

**Why autonomous: false** — first invocation requires the operator to confirm `ollama login` is active and to monitor for auth errors during the 35-55 minute run. Once verified, execution itself is fully scripted.
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
@.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-VALIDATION.md
@scripts/run_judge_fpr.py

<runtime_expectations>
- 7 active defenses × 50 clean queries = 350 cloud calls minimum (per D-01: all 7 ablation rows). With D-12 retries, expect 360-380 actual calls.
- --delay 3 enforces ≥3s between calls; cloud-side latency adds another 3-5s per call (≈6-8s per call total).
- Total wall clock: 35-55 minutes (350 calls × ~6-8s/call ≈ 35-47 min, plus warmup, output writes, retry overhead).
- Auth errors from gpt-oss:20b-cloud trigger sys.exit(1) with "Run: ollama login" message.
- Mid-run failures resume from cache (RESEARCH §5.1) — re-running the same command picks up where it stopped.
</runtime_expectations>
</context>

<tasks>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 1: Confirm ollama login + model availability before judge run</name>
  <what-built>Plan 02 produced scripts/run_judge_fpr.py. The script is ready to invoke. Before burning cloud-LLM budget on a 35-55 minute run (350 cloud calls across 7 active defenses per D-01), the operator confirms cloud auth is active.</what-built>
  <how-to-verify>
    1. Run `ollama list` and confirm `gpt-oss:20b-cloud` appears in the model list.
    2. Run a one-shot smoke test (note `conda run -n rag-security` prefix — required to match the project's conda env convention):
       ```
       conda run -n rag-security python -c "from ollama import Client; c = Client(host='http://localhost:11434'); r = c.chat(model='gpt-oss:20b-cloud', messages=[{'role':'user','content':'Reply with the single word PRESERVED'}], options={'temperature':0.0}); print((r.message.content if hasattr(r,'message') else r['message']['content'])[:50])"
       ```
       Expected: prints `PRESERVED` (or similar). If output contains "login required" or "auth error", run `ollama login` and re-test.
    3. Confirm working directory is the repo root (where `logs/` is a sibling of `scripts/`).
  </how-to-verify>
  <resume-signal>
    Type "approved" once `ollama list` shows the model AND the smoke test prints a verdict-shaped string. If auth fails, fix it (run `ollama login`) and re-verify before approving.
  </resume-signal>
</task>

<task type="auto">
  <name>Task 2: Execute scripts/run_judge_fpr.py end-to-end against cloud LLM</name>
  <files>logs/judge_fpr_llama.json, logs/ablation_table.json, logs/judge_fpr_llama.json.cache</files>
  <read_first>
    - scripts/run_judge_fpr.py (entire file — verify the script as Plan 02 produced it; especially the M1/M2/M3 formulas and the atomic-write blocks)
    - .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-RESEARCH.md (lines 561-640 — risk register; mid-run failure recovery via cache)
    - logs/ablation_table.json (current state — confirm 8 llama ablation rows present (no_defense + 7 active defenses) and existing keys intact BEFORE running)
  </read_first>
  <action>
    Pre-flight check (do these in sequence):
    1. Snapshot current ablation_table.json to a local backup so V-09 back-compat verification can compare pre/post:
       ```
       cp logs/ablation_table.json /tmp/ablation_table.pre_phase5.json
       ```
    2. Confirm fpr key value for fused_fixed_0.5 is 0.76 (sanity check the row schema):
       ```
       python -c "import json; d=json.load(open('logs/ablation_table.json')); assert abs(d['fused_fixed_0.5']['fpr']-0.76)<0.01, d['fused_fixed_0.5']['fpr']; print('OK')"
       ```

    Live execution (THE long-running step):
    3. Run the judge:
       ```
       conda run -n rag-security python scripts/run_judge_fpr.py --model gpt-oss:20b-cloud --delay 3 --cache logs/judge_fpr_llama.json.cache 2>&1 | tee logs/run_judge_fpr.stdout.log
       ```
       Expected wall clock: 35-55 minutes (350 cloud calls × ~6-8s/call + retries). If the run is interrupted (Ctrl-C, auth refresh, network blip), simply re-run the same command — the cache pattern (RESEARCH §5.1) resumes from the last completed verdict.

       Pass `timeout: 3600000` (60 minutes) to the Bash tool when invoking — judge runs can extend toward the upper bound under cloud rate limits.

    4. Confirm exit code is 0 and the per-cell file landed:
       ```
       ls -la logs/judge_fpr_llama.json
       python -c "import json; d=json.load(open('logs/judge_fpr_llama.json')); print('phase=', d.get('phase'), 'judge_model=', d.get('judge_model'), 'defenses=', list(d['verdicts'].keys()), 'n_verdicts_per_defense=', {k: len(v) for k,v in d['verdicts'].items()})"
       ```
       Expected: phase="05", judge_model="gpt-oss:20b-cloud", exactly 7 defense keys (per D-01), each with 50 verdict records.

    Post-flight verification:
    5. Confirm V-09 back-compat (existing fpr key unchanged):
       ```
       python -c "import json; pre=json.load(open('/tmp/ablation_table.pre_phase5.json')); post=json.load(open('logs/ablation_table.json')); [print('OK', k) if pre[k].get('fpr')==post[k].get('fpr') else (_ for _ in ()).throw(AssertionError(f'fpr changed on {k}: {pre[k].get(\"fpr\")} -> {post[k].get(\"fpr\")}')) for k in pre if 'fpr' in pre[k]]; print('all fpr keys unchanged')"
       ```
    6. Confirm new schema present on all 8 llama rows (7 active + no_defense):
       ```
       python -c "import json; d=json.load(open('logs/ablation_table.json')); needed={'per_chunk_fpr','answer_preserved_fpr','judge_fpr','judge_model','judge_n_calls'}; missing={k:list(needed-set(d[k])) for k in d if isinstance(d[k],dict) and 'asr_t1' in d[k]}; print({k:v for k,v in missing.items() if v})"
       ```
       Expected: empty dict `{}` (no row missing any of the 5 keys).
    7. Confirm no_defense trivial fill (D-02):
       ```
       python -c "import json; r=json.load(open('logs/ablation_table.json'))['no_defense']; assert r['per_chunk_fpr']==0.0 and r['answer_preserved_fpr']==0.0 and r['judge_fpr']==0.0 and r['judge_n_calls']==0; print('no_defense trivial fill OK — judge_n_calls=0 is the canonical no-calls signal per D-02; judge_model is set for schema-shape consistency only')"
       ```
    8. Confirm judge_n_calls range on active defenses (50 base + retries; expect 50-60 per active row):
       ```
       python -c "import json; d=json.load(open('logs/ablation_table.json')); active=['def02','bert_only','perplexity_only','imperative_only','fingerprint_only','fused_fixed_0.5','fused_tuned_threshold']; [print(f'{k}: judge_n_calls={d[k][\"judge_n_calls\"]}') or (_ for _ in ()).throw(AssertionError(f'{k}.judge_n_calls={d[k][\"judge_n_calls\"]} out of expected [50, 75]')) if not (50 <= d[k]['judge_n_calls'] <= 75) else None for k in active]; print('active-defense judge_n_calls in range')"
       ```
       Expected: each active defense has judge_n_calls in [50, 75] (50 base + reasonable retry budget).
    9. Run Plan 01 tests against the live artifacts:
       ```
       conda run -n rag-security pytest tests/test_judge_fpr.py -x -q
       ```
       Expected: 9 passed in <10s.
    10. Confirm idempotence (V-06): re-run with cache, ablation_table.json unchanged:
       ```
       md5sum logs/ablation_table.json > /tmp/ablation_md5_pre.txt
       conda run -n rag-security python scripts/run_judge_fpr.py --model gpt-oss:20b-cloud --delay 0 --cache logs/judge_fpr_llama.json.cache > /dev/null
       md5sum logs/ablation_table.json > /tmp/ablation_md5_post.txt
       diff /tmp/ablation_md5_pre.txt /tmp/ablation_md5_post.txt
       ```
       Expected: empty diff (md5 unchanged).

    On any failure:
    - Auth error (script exits with "Run: ollama login"): run `ollama login`, re-execute step 3 (cache resumes from last verdict).
    - Network timeout mid-run: simply re-execute step 3.
    - Test failure: read pytest output, identify which V-XX failed, inspect the relevant log file, file an issue if the failure points to a Plan 02 bug. Do NOT silently mutate logs to make tests pass.
  </action>
  <verify>
    <automated>conda run -n rag-security pytest tests/test_judge_fpr.py -x -q</automated>
  </verify>
  <acceptance_criteria>
    - `logs/judge_fpr_llama.json` exists and contains the keys `phase`, `judge_model`, `judge_prompt_template`, `verdicts`.
    - `python -c "import json; d=json.load(open('logs/judge_fpr_llama.json')); assert d['judge_model']=='gpt-oss:20b-cloud' and d['phase']=='05' and all(len(v)==50 for v in d['verdicts'].values()) and len(d['verdicts'])==7"` exits 0 (exactly 7 defense keys per D-01).
    - `python -c "import json; d=json.load(open('logs/ablation_table.json')); needed={'per_chunk_fpr','answer_preserved_fpr','judge_fpr','judge_model','judge_n_calls'}; assert all(needed.issubset(set(row)) for row in d.values() if isinstance(row, dict) and 'asr_t1' in row), 'rows missing new keys'"` exits 0 (every llama ablation row including no_defense has all 5 new keys).
    - `python -c "import json; d=json.load(open('logs/ablation_table.json'))['fused_fixed_0.5']; assert abs(d['fpr']-0.76)<0.01, f'fpr changed to {d[\"fpr\"]}'"` exits 0.
    - `python -c "import json; d=json.load(open('logs/ablation_table.json'))['no_defense']; assert d['per_chunk_fpr']==0.0 and d['judge_n_calls']==0"` exits 0 (canonical no-calls signal per D-02).
    - `python -c "import json; d=json.load(open('logs/ablation_table.json')); active=['def02','bert_only','perplexity_only','imperative_only','fingerprint_only','fused_fixed_0.5','fused_tuned_threshold']; total=sum(d[k]['judge_n_calls'] for k in active); assert 350<=total<=520, f'total active judge_n_calls={total} out of expected [350, 520]'"` exits 0 (350 base calls per D-01 + reasonable retry budget).
    - `conda run -n rag-security pytest tests/test_judge_fpr.py -x -q 2>&1 | grep -E "9 passed"` matches.
    - `grep -c "DEGRADED" logs/judge_fpr_llama.json` returns ≥ 1 (sanity: not all PRESERVED) AND ≤ 350 (sanity: not all DEGRADED).
    - md5 of `logs/ablation_table.json` is unchanged after a second invocation with the cache (V-06 idempotence verified live).
    - `logs/judge_fpr_llama.json.cache` exists (cache file persisted).
  </acceptance_criteria>
  <done>
    Three artifacts populated; 9/9 V-tests green; existing fpr key on all rows preserved; live idempotence verified; 350 base cloud calls completed across 7 active defenses (per D-01) with no_defense filled trivially per D-02. Plan 04 can now read the three new metric values across all 7 active rows.
  </done>
</task>

</tasks>

<verification>
- `conda run -n rag-security pytest tests/test_judge_fpr.py -x -v` — all 9 tests pass with verbose output (V-01..V-09 each named).
- `python -c "import json; d=json.load(open('logs/ablation_table.json')); [print(f'{k}: M1={v.get(\"per_chunk_fpr\"):.3f} M2={v.get(\"answer_preserved_fpr\"):.3f} M3={v.get(\"judge_fpr\"):.3f} fpr_orig={v.get(\"fpr\")}') for k, v in d.items() if isinstance(v, dict) and 'per_chunk_fpr' in v]"` — prints the 8-row results table (7 active + no_defense).
- Spot check one verdict record: `python -c "import json; d=json.load(open('logs/judge_fpr_llama.json'))['verdicts']['fused_fixed_0.5']; k=list(d.keys())[0]; print(k, d[k])"` — verdict, ab_assignment, raw_response, retry_count all present.
- Spot check fused_tuned_threshold has full 50 verdicts: `python -c "import json; d=json.load(open('logs/judge_fpr_llama.json'))['verdicts']['fused_tuned_threshold']; assert len(d)==50; print('fused_tuned_threshold has 50 verdicts')"`.
</verification>

<success_criteria>
- 350 base judge verdicts persisted (50 per active defense × 7 active defenses per D-01); judge_n_calls totals 350-520 across active rows after retries.
- ablation_table.json extended additively on all 8 llama rows (7 active + no_defense); existing keys unchanged.
- All 9 Plan 01 tests green against the live artifacts.
- Cache file persisted at logs/judge_fpr_llama.json.cache for re-runs.
- Re-run with cache produces byte-identical ablation_table.json (V-06 idempotence).
- M3 verdict distribution shows mixture of DEGRADED / PRESERVED / TIE (not collapsed to one value).
- no_defense row carries judge_n_calls=0 (canonical no-calls signal per D-02).
</success_criteria>

<output>
After completion, create `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-03-SUMMARY.md` documenting:
- Wall-clock duration of the judge run (expected 35-55 min for 350 cloud calls).
- Per-defense M1, M2, M3 results table for all 7 active defenses (the headline numbers Plan 04 will cite).
- Per-defense distribution: DEGRADED / PRESERVED / TIE / REFUSAL counts.
- Total retries observed (judge_n_calls - 50 per active defense; total budget consumed = sum across 7 actives).
- Any auth/network blips encountered + how the cache resumed.
- The 9-test pytest output (with timing).
- The "INFILTRATED leakage" sub-finding from RESEARCH §5.5 if observed (count of clean queries where defense-off answer contained any of the 5 anchor tokens — HACKED, COMPROMISED, INFILTRATED, SYSTEM_OVERRIDE, PAYLOAD_DELIVERED).
- md5 hash of logs/ablation_table.json post-Plan-03 (lock the bytes for downstream Plan 04 reproducibility).
- Confirmation that no_defense.judge_n_calls=0 (canonical no-calls signal per D-02) and no_defense.judge_model is set for schema-shape consistency only.
</output>
