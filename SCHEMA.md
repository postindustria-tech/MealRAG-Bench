# File formats

All JSON/JSONL uses UTF-8. JSONL contains one object per line. Recipe and query IDs are strings. Reference labels are strings (`"0"`, `"1"`, `"2"`, `"?"`).

## Dataset

- `data/dataset.json`: version, counts, label distribution, frozen 85-query retrieval scope and filenames relative to `data/`. `source_dataset_content_sha256` identifies the internal dataset before export; it is not a checksum of this reduced dataset file.
- `data/corpus-reference.json`: `recipes` lists `recipe_id`, original Markdown `file` and `sha256`. No title, ingredient list or instructions are included.
- `data/queries.jsonl`: `id`, exact `query`, type/difficulty/style/family, constraints, `known_full_recipe_ids`, annotation counts and coverage note. Known full IDs are not exhaustive corpus gold.
- `data/labels.jsonl`: unique (`query_id`, `recipe_id`), final `label`. The 12 explicit human decisions additionally have `human_adjudicated: true` and `rationale`. Missing flags mean the reconciled reference label, not a claim of human certification. Original source excerpts and provenance paths are omitted.

## Settings

`settings/experiments.json` contains `retrievers`, `rerankers`, `lexical_hybrid`, `agent_profiles` and `agent_studies`. IDs in `retrieval.source` and `reranker.source` refer to entries in this file, not local filesystem paths. A null reranker means no profile-level reranking; the query-formulation profile separately records its search pipeline, which uses `gpt-6-luna-reranker-001` settings with the specified retry/budget overrides.

`settings/prompts.json` maps agent prompt IDs to exact instructions and records the search-tool interface. Reranker `adapter` entries in `experiments.json` contain exact recorded prompts, response schemas, Jev criteria, Qwen wrappers and generation options. The Qwen pair template sits between its prefix and suffix. BGE consumes a query/document pair directly. These are descriptive settings; no experiment runner is included.

## Rankings

`results/rankings.jsonl` has one record per (`method`, `retriever`, `query_id`):

- `method`: `dense`, a reranker ID, `bm25`, or `hybrid`.
- `retriever`: the originating dense pool. For standalone BM25, the Gemini ID identifies the associated hybrid comparison, not an embedding used by BM25.
- `hits`: ordered recipe IDs with one-based `rank`, final `label`, and available original score fields. Dense retains top-20; rerankers top-10; BM25 top-20; hybrid top-10.
- `reranker_score` and `original_rank`: saved reranker score and rank in the original dense top-10.
- `cosine_similarity`, `bm25_score`, `rrf_score`, `source_ranks`: retain their original meaning and units. Dense similarity can remain attached to a reranked hit; it is not the reranker score.
- `timing`: available dense per-query measurements, in seconds.

All hit labels use the final label map. `unjudged` means an absent reference pair. Recipe text and titles are excluded from ranking records.

## Agent answers

`results/agent-answers.jsonl` has one record per (`profile_key`, `query_id`). Profile keys match `agent_profiles` in settings and summaries.

`status`, `recipe_id`, `label`, `outcome`, `selection_full` and `workflow_compliant_full` preserve final evaluation. `answer` is the retained parsed model answer when available; `raw_output` is the original final model output, including malformed responses. It is not a transcript, tool context or raw request log. Missing parsed answers are not reconstructed from prose.

`selection_full` can be true for a full selected recipe in a workflow-error record. `workflow_compliant_full` is true only for a successful full outcome. Compare the latter when protocol compliance matters.

Available `seen_recipe_ids`, `dense_candidate_ids`, `returned_recipe_ids`, search counts/query and `context_bytes` describe exposure without supplying recipe text. `seen_recipe_ids` is not guaranteed to retain exposure order. `sdk_reference_cost_usd` and `usage` are available SDK estimates and token accounting, not authoritative invoices. Null means unavailable. `answer_format` records the parser format when present.

## Summaries

`results/summary.json` retains the final numerical summaries: the ranking matrix, individual dense diagnostics, lexical comparisons, agent profiles, paired transitions, resource summaries and query timings. Eligible query IDs and denominators belong to each comparison. Source runtime paths/metadata are omitted; settings are in `settings/experiments.json`.

`SHA256SUMS` hashes the actual package files, excluding itself. It does not validate historical provenance, recipe recovery or upstream services.
