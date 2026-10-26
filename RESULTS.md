# Saved benchmark results

Final relevance version: **mealrag-final-v1**. These are recorded single-run results; see [METHOD.md](METHOD.md) for cohort definitions and limitations. Full metrics, paired transitions, resource summaries and exact eligible query IDs are in [results/summary.json](results/summary.json).

## Main comparison: 69 queries

| Configuration | Full | Partial | Irrelevant | Unknown | Abstain | Failure | Pipeline estimate, USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sonnet / dense top-3 | 59 | 5 | 0 | 0 | 5 | 0 | 0.517699 |
| Sonnet / reranked top-3 | 57 | 4 | 0 | 0 | 8 | 0 | 0.569799 |
| Haiku / dense top-3 | 53 | 10 | 1 | 0 | 4 | 1 | 0.025995 |
| Haiku / reranked top-3 | 51 | 10 | 1 | 0 | 7 | 0 | 0.063900 |
| Sonnet / reranked, clarified instruction | 58 | 6 | 0 | 0 | 5 | 0 | 0.582517 |
| Haiku / reranked, clarified instruction | 53 | 7 | 2 | 0 | 6 | 1 | 0.064835 |

Pipeline costs are saved reference estimates with historical stage overhead, not invoices. Failures remain in the denominator.

## Retrieval and reranking

Full Top-1 selections on the same 84 eligible queries from the frozen 85-query retrieval cohort. MRR@10 uses the same 82 eligible queries across all 42 configurations.

| Ranking | BGE-M3 | Gemma | Qwen3 | OpenAI | Gemini | Promptriever |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dense | 49 | 58 | 65 | 59 | 69 | 57 |
| BGE | 63 | 66 | 66 | 67 | 68 | 67 |
| Qwen | 69 | 74 | 75 | 76 | 75 | 74 |
| Luna none | 69 | 76 | 76 | 77 | 77 | 76 |
| Luna medium | 69 | 76 | 77 | 78 | 77 | 77 |
| Haiku | 67 | 68 | 71 | 72 | 70 | 69 |
| Jev | 66 | 71 | 72 | 73 | 73 | 72 |

In the separate dense/hybrid paired comparison, Gemini dense has 69/85 full Top-1 selections and hybrid 65/85; MRR@10 is 0.874799 versus 0.847103 on 83 queries. Standalone BM25 has incomplete annotation coverage. These denominators belong to this comparison.

## Diagnostic comparisons: 21 queries

| Question | Protocol-compliant full selections |
| --- | --- |
| Optional search | BGE 7 → 9; Gemini 15 → 18 |
| Context 3 → 10 | BGE 7 → 11; Gemini 15 → 18 |
| Dense top-10 → reranked top-3 | BGE 11 → 11; Gemini 18 → 20 |
| Sonnet → Haiku, same reranked top-3 | BGE 11 → 9; Gemini 20 → 16 |
| Agent-formulated search query | 20 → 18; full recipe selection alone is 20 → 21 |

## Context-size pilot: 18 queries

| Recipes supplied | Full | Abstain | Failure |
| ---: | ---: | ---: | ---: |
| 5 | 14 | 2 | 0 |
| 10 | 9 | 2 | 4 |
| 20 | 10 | 3 | 1 |
| 30 | 12 | 2 | 1 |

The pilot and diagnostic cohorts are deliberately selected and are distinct from the 69-query remainder. A full selection is not certification of a fully correct explanation.

## Online reranker request latency

Seconds per successful query–recipe pair request, including network time. This is not parallel top-10 serving latency.

| Reranker | Requests | Median | 5% trimmed mean | p95 |
| --- | ---: | ---: | ---: | ---: |
| Luna none | 2046 | 1.6021 | 1.8498 | 4.0895 |
| Luna medium | 2046 | 2.5438 | 2.6040 | 3.8739 |
| Haiku | 2046 | 1.1129 | 1.1670 | 1.9982 |
| Jev | 2046 | 0.2253 | 0.2363 | 0.3481 |

The trimmed mean removes floor(0.05 × n) values from each tail. Batch timings, accounting coverage and additional measurements remain in the machine-readable summary.
