"""Shared integer constants for poisoned-passage ID ranges.

Single source of truth for tier boundaries used by run_eval.py,
train_defense.py, and future Phase 3.x scripts.

Tier layout (passage_id ranges):
    T1 (Naive):            20000 – 20049
    T2 (Blended):          20050 – 20099
    T3 (LLM-generated):    20100 – 20149
    T1b (Homoglyph):       20150 – 20199  (Phase 3.3: ATK-01b Unicode homoglyph)
    T4 (Cross-chunk):      20200 – 20299
    Adaptive (ATK-08/09):  20500 – 20599  (Phase 3.2)

NOTE: T1b sits ABOVE T3 numerically (20150 > 20100).
  T3 upper bound in predicates must use TIER1B_ID_START (20150), NOT TIER4_ID_START (20200).
"""

# ── Poisoned passage_id range starts ─────────────────────────────────────────

TIER1_ID_START = 20000
TIER2_ID_START = 20050
TIER3_ID_START = 20100   # Phase 2.4: LLM-generated payloads
TIER1B_ID_START = 20150  # Phase 3.3: ATK-01b Unicode homoglyph obfuscation
TIER4_ID_START = 20200   # Phase 2.4: Cross-chunk fragmentation

ADAPTIVE_ID_START = 20500  # Phase 3.2: ATK-08/09 adaptive payloads

CLEAN_ID_MAX = 19999
