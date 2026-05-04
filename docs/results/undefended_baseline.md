> Updated 2026-05-04: Phase 6 cross-LLM gap fill — gpt-oss-20b and gpt-oss-120b numbers added across all 5 tiers and {no_defense, fused, def02}. Phase 02.3 / Phase 3.4 numbers above this line are unchanged.

| model              | source                      |   asr_tier1 | asr_tier1b   |   asr_tier2 | asr_tier3   | asr_tier4   |   paired_asr_tier1 |   paired_asr_tier2 |   retrieval_rate |   n_queries |
|:-------------------|:----------------------------|------------:|:-------------|------------:|:------------|:------------|-------------------:|-------------------:|-----------------:|------------:|
| llama3.2:3b        | Phase 2.3 canonical (n=100) |        0.10 | —            |        0.12 | —           | —           |               0.10 |               0.16 |             0.86 |         100 |
| mistral:7b         | Phase 2.3 canonical (n=100) |        0.00 | —            |        0.26 | —           | —           |               0.00 |               0.32 |             0.86 |         100 |
| gpt-oss:20b-cloud  | Phase 6 v6 (n=100)          |        0.00 | 0.06         |        0.06 | 0.0         | 0.0         |               0.00 |               0.06 |             0.89 |         100 |
| gpt-oss:120b-cloud | Phase 6 v6 (n=100)          |        0.00 | 0.02         |        0.06 | 0.0         | 0.0         |               0.00 |               0.10 |             0.89 |         100 |
| llama3.2:3b        | Phase 2.2 frozen (n=10)     |        0.50 | —            |        0.00 | —           | —           |               0.50 |               0.00 |             1.00 |          10 |
