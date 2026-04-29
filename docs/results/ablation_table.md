| Defense              | defense_mode          | defense_mode_raw   | model       |   asr_t1 |   asr_t2 |   asr_t3 |   asr_t4 |   fpr |   retrieval_rate |   n_queries |   chunks_removed_total |
|:---------------------|:----------------------|:-------------------|:------------|---------:|---------:|---------:|---------:|------:|-----------------:|------------:|-----------------------:|
| No Defense           | no_defense            | off                | llama3.2:3b |     0.02 |     0.12 |     0.00 |     0.00 |  0.00 |             0.88 |         100 |                      0 |
| DEF-02               | def02                 | def02              | llama3.2:3b |     0.08 |     0.38 |     0.04 |     0.00 |  0.00 |             0.88 |         100 |                      0 |
| BERT alone           | bert_only             | bert               | llama3.2:3b |     0.00 |     0.00 |     0.00 |     0.00 |  0.76 |             0.44 |         100 |                    258 |
| Perplexity           | perplexity_only       | perplexity         | llama3.2:3b |     0.02 |     0.08 |     0.00 |     0.00 |  0.72 |             0.77 |         100 |                    133 |
| Imperative           | imperative_only       | imperative         | llama3.2:3b |     0.00 |     0.00 |     0.00 |     0.00 |  0.88 |             0.74 |         100 |                    232 |
| Fingerprint          | fingerprint_only      | fingerprint        | llama3.2:3b |     0.02 |     0.00 |     0.00 |     0.00 |  0.06 |             0.67 |         100 |                    179 |
| Fused                | fused_fixed_0.5       | fused              | llama3.2:3b |     0.00 |     0.00 |     0.00 |     0.00 |  0.76 |             0.50 |         100 |                    247 |
| Fused (tuned)        | fused_tuned_threshold | fused              | llama3.2:3b |     0.00 |     0.00 |     0.00 |     0.00 |  0.76 |             0.34 |         100 |                    270 |
| No Defense (mistral) | mistral_no_defense    | off                | mistral:7b  |     0.00 |     0.28 |     0.12 |     0.00 |  0.00 |             0.88 |         100 |                      0 |
| Fused (mistral)      | mistral_fused         | fused              | mistral:7b  |     0.00 |     0.00 |     0.00 |     0.00 |  0.76 |             0.50 |         100 |                    247 |
