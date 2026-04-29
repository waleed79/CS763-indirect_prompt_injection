| model              | source                      |   asr_tier1 |   asr_tier2 |   paired_asr_tier1 |   paired_asr_tier2 |   retrieval_rate |   n_queries |
|:-------------------|:----------------------------|------------:|------------:|-------------------:|-------------------:|-----------------:|------------:|
| llama3.2:3b        | Phase 2.3 canonical (n=100) |        0.10 |        0.12 |               0.10 |               0.16 |             0.86 |         100 |
| mistral:7b         | Phase 2.3 canonical (n=100) |        0.00 |        0.26 |               0.00 |               0.32 |             0.86 |         100 |
| gpt-oss:20b-cloud  | Phase 2.3 canonical (n=100) |        0.00 |        0.23 |               0.00 |               0.28 |             0.86 |         100 |
| gpt-oss:120b-cloud | Phase 2.3 canonical (n=100) |        0.00 |        0.09 |               0.00 |               0.14 |             0.86 |         100 |
| llama3.2:3b        | Phase 2.2 frozen (n=10)     |        0.50 |        0.00 |               0.50 |               0.00 |             1.00 |          10 |
