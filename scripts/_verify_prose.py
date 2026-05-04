"""Phase 7 Plan 06 — prose-unchanged audit script.

The addendum was appended in commit fe09ca3. The original Phase 5 content lives in
commit 7374f22 (the previous commit to docs/phase5_honest_fpr.md before the addendum).
We verify that the content of the current file above the addendum heading is
bit-for-bit identical to the original Phase 5 prose (7374f22).
"""
import subprocess

# The original Phase 5 content (before addendum was appended)
original_commit = '7374f22'
original = subprocess.check_output(
    ['git', 'show', f'{original_commit}:docs/phase5_honest_fpr.md']
).decode('utf-8')

cur = open('docs/phase5_honest_fpr.md', encoding='utf-8').read()
idx = cur.find('## Phase 7 addendum')
assert idx >= 0, 'addendum heading not found'
prefix = cur[:idx].rstrip()
original_stripped = original.rstrip()
assert prefix == original_stripped, (
    f'PROSE MUTATED: prefix bytes != original Phase 5 bytes (len_diff={len(prefix) - len(original_stripped)})'
)
print('OK: Phase 5 prose above addendum is bit-for-bit identical to original Phase 5 content (commit 7374f22)')
