# Push Blocker: 256 MB BERT model in git history — RESOLVED

**Status:** Resolved 2026-04-28 via `git filter-repo`.
**Detected:** 2026-04-28 during pre-Phase-3.4 cleanup.

## What was done

`models/bert_classifier/model.safetensors` (256 MB, originally committed in
`4a7a199`) was scrubbed from all 168 commits in local history using
`git-filter-repo`:

```bash
pip install git-filter-repo  # 2.47.0
git branch backup-pre-filter-repo  # safety net
git-filter-repo --invert-paths --path models/bert_classifier/model.safetensors --force
git remote add origin https://github.com/waleed79/CS763-indirect_prompt_injection.git
```

Repo size dropped from **506 MB → 19 MB**. The file remains on disk in
the working tree (untracked, gitignored) so local FusedDefense runs still
work without retraining.

`.gitignore` was updated to prevent the file from being re-tracked:

```
# Phase 3.1 BERT classifier final model (256 MB; regenerable from
# `python scripts/train_defense.py` per REPLICATION instructions in README).
models/bert_classifier/model.safetensors
```

README "Reproducing the trained defense models" section added with the
training commands graders need to regenerate the model from scratch.

## What you need to do

**Force-push to remote** (the local branch now has different commit hashes
than `origin/main`, since filter-repo rewrote 168 commits):

```bash
# Verify before pushing — local should be 168 commits ahead, remote unchanged
git log --oneline origin/main..main | wc -l   # expect ~168
git log -1 origin/main                          # expect bee151d (Waleed, 2026-04-12)

# Force-push the rewritten history
git push --force-with-lease origin main
```

`--force-with-lease` is safer than `--force`: it refuses the push if anyone
else has pushed to `origin/main` since you last fetched (would protect against
overwriting Waleed's hypothetical future work). Since `origin/main` hasn't
moved since 2026-04-12, this push will succeed.

**Tell Waleed before he pulls.** Anyone who has the old `origin/main` cloned
locally will see history divergence on next `git pull`. The fix on his end is:

```bash
git fetch origin
git reset --hard origin/main   # WARNING: discards any local changes
```

If Waleed has uncommitted work on the old history, he should stash/cherry-pick
it onto the new `main` rather than reset.

## Safety net

A backup branch `backup-pre-filter-repo` was created locally pointing at the
pre-rewrite tip. If anything goes wrong, recover with:

```bash
git reset --hard backup-pre-filter-repo
# (and the model.safetensors history will be back too)
```

You can delete this branch after the force-push lands cleanly:

```bash
git branch -D backup-pre-filter-repo
```

## Other large/regenerable artifacts (still gitignored, no action needed)

These were `.gitignore`d earlier in this cleanup pass (commit `31a80a3`) so
they don't recreate the same problem:

- `models/bert_classifier/checkpoint-*/`  (~768 MB each, 3 checkpoints)
- `models/bert_s{1,2,3}/`  (~2.5 GB each, EVAL-05 multi-seed final models)
- `models/bert_s*/checkpoint-*/`
- `.chroma/`  (local ChromaDB index)

The small `models/lr_meta_classifier_s{1,2,3}.json` (≈516 bytes each) ARE
committed — they're the small artifacts EVAL-05 actually depends on.
