# Push Blocker: 256 MB BERT model in git history

**Status:** Will block `git push origin main` to GitHub (file size > 100 MB hard limit).
**Detected:** 2026-04-28 during pre-Phase-3.4 cleanup.

## What

`models/bert_classifier/model.safetensors` (256 MB) was committed in `4a7a199`
(`feat(03.1-04): run train_defense.py — produce all 3 model artifacts + 10/10 tests green`).

GitHub rejects any push that contains a single file ≥ 100 MB. The current local
branch has **151 commits ahead of `origin/main`** (last remote update was Waleed's
`bee151d` on 2026-04-12). When you next try to push the accumulated work, GitHub
will reject the entire push.

## Reproduce

```bash
$ du -sh models/bert_classifier/model.safetensors
256M
$ git log --oneline --all -- models/bert_classifier/model.safetensors
4a7a199 feat(03.1-04): run train_defense.py — produce all 3 model artifacts + 10/10 tests green
$ git log origin/main..main --oneline | wc -l
151
```

## Three options to fix

**Option A — Git LFS (preserves history; recommended for class deliverable).**
   Install Git LFS, retroactively migrate the large file, force-push.

   ```bash
   git lfs install
   echo "*.safetensors filter=lfs diff=lfs merge=lfs -text" > .gitattributes
   git add .gitattributes
   git commit -m "chore: add LFS pattern for *.safetensors"
   git lfs migrate import --include="*.safetensors" --everything
   git push --force-with-lease origin main
   ```

   Pros: keeps the trained model accessible to graders.
   Cons: requires Git LFS on grader's machine; force-push rewrites history.

**Option B — Untrack + retrain on demand (simplest; smaller repo).**
   Remove the model from git, document the training command in README, let
   graders regenerate it.

   ```bash
   git rm --cached models/bert_classifier/model.safetensors
   echo "models/bert_classifier/model.safetensors" >> .gitignore
   # Use git filter-repo to scrub it from history (or BFG):
   pip install git-filter-repo
   git filter-repo --invert-paths --path models/bert_classifier/model.safetensors
   git push --force-with-lease origin main
   ```

   Pros: tiny repo, no LFS dependency.
   Cons: graders must run `python scripts/train_defense.py` (~30 min) to reproduce;
   force-push rewrites history.

**Option C — Push a fresh branch from a clean point (no history rewrite).**
   Create a new branch from current state with the file untracked, push that
   branch instead of `main`.

   ```bash
   git checkout --orphan deliverable
   git rm -rf --cached models/bert_classifier/model.safetensors
   git add .
   git commit -m "Final deliverable snapshot for CS 763"
   git push -u origin deliverable
   ```

   Pros: no force-push, no LFS, original branch stays as-is locally.
   Cons: history is collapsed to one commit; reviewers can't see the per-phase
   atomic commits.

## Recommendation

**Option B with `git-filter-repo`** for this project. The training command is
short and documented (`python scripts/train_defense.py`), the BERT model is
deterministic given the seed, and a 256 MB file in a class repo is poor
practice anyway. Add a one-line replication note in README.

## Other large/regenerable artifacts

These are now `.gitignore`d (added 2026-04-28, commit `31a80a3`) so future
training won't recreate the same problem:

- `models/bert_classifier/checkpoint-*/`  (~768 MB each, 3 checkpoints)
- `models/bert_s{1,2,3}/`  (~2.5 GB each, EVAL-05 multi-seed final models)
- `models/bert_s*/checkpoint-*/`
- `.chroma/`  (local ChromaDB index)

The small `models/lr_meta_classifier_s{1,2,3}.json` (≈516 bytes each) ARE
committed — they're the small artifacts EVAL-05 actually depends on for
reproducibility checks.

## Action item for you

Decide between Option A / B / C, then execute before the Phase 3.4
deliverable push. This is the only blocker I found that needs your judgment
call rather than a documentation edit.
