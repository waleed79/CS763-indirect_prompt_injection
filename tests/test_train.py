"""Phase 3.2 EVAL-05 multi-seed aggregation tests.

TestSeedVariance — confirms that different seeds produce different negative sample
                   shuffling orders (stdlib proof-of-concept).

Plan 03.2-02 adds the --seed flag to train_defense.py; the stub guard test
(test_train_defense_has_no_seed_flag_yet) was deleted once the flag was implemented.

Run with:
    conda run -n rag-security python -m pytest tests/test_train.py -v
"""
from __future__ import annotations

from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
_TRAIN_DEFENSE_PATH = _SCRIPTS_DIR / "train_defense.py"


class TestSeedVariance:
    """EVAL-05: verify that different random seeds produce different shuffle orderings.

    Rationale: the --seed flag in train_defense.py (plan 03.2-02) re-samples the
    negative training examples using random.seed(args.seed). For EVAL-05 multi-seed
    aggregation to produce genuine variance in classifier behavior, different seeds
    must actually produce different negative sample pools. This class confirms that
    Python's stdlib random.seed + random.shuffle satisfy this requirement.
    """

    def test_seed_changes_shuffle_order(self):
        """Different seeds must produce different list orderings.

        Simulates what train_defense.py does: seed the RNG, then shuffle the
        negative sample pool. Seeds 1 and 2 must produce different orderings,
        confirming the --seed flag generates genuine variance in the trained
        meta-classifier.
        """
        import random

        data = list(range(100))

        random.seed(1)
        d1 = data.copy()
        random.shuffle(d1)

        random.seed(2)
        d2 = data.copy()
        random.shuffle(d2)

        assert d1 != d2, (
            "Seeds 1 and 2 produced identical orderings — this should never happen "
            "with Python's stdlib Mersenne Twister RNG"
        )

    def test_seed_flag_exists_in_train_defense(self):
        """Confirm --seed argparse flag is registered in train_defense.py (plan 03.2-02).

        Checks for 'add_argument.*--seed' pattern (the actual argparse registration)
        rather than the bare string '--seed', which may appear in docstrings/comments.
        This test replaced the stale stub that checked for the flag's absence.
        """
        import re
        src = _TRAIN_DEFENSE_PATH.read_text(encoding="utf-8")
        has_seed_arg = bool(re.search(r'add_argument\s*\([^)]*["\']--seed["\']', src))
        assert has_seed_arg, (
            "add_argument('--seed', ...) not found in train_defense.py — "
            "plan 03.2-02 must add the --seed argparse flag."
        )
