# MealRAG benchmark materials

Saved results and evaluation data for a recipe RAG study: **790 recipes, 90 English queries**, six dense retrievers, six rerankers, BM25/RRF and nine agent studies. All relevance results use **mealrag-final-v1**.

Start with [the result tables](RESULTS.md) and [the evaluation method](METHOD.md).

## Contents

| Path | Contents |
| --- | --- |
| `fetch_recipes.py` | Standalone TheMealDB downloader and Markdown converter |
| `data/corpus-reference.json` | IDs, original filenames and SHA-256 hashes of the 790 benchmark documents |
| `data/queries.jsonl` | 90 queries, constraints, families and known full matches |
| `data/labels.jsonl` | 6,663 final query–recipe judgments, including 12 human-adjudicated pairs |
| `data/dataset.json` | Dataset version, counts and frozen retrieval cohort |
| `settings/experiments.json` | Recorded model aliases, revisions, input formats, generation settings and query cohorts |
| `settings/prompts.json` | Exact agent instructions and search-tool interface; reranker templates are in `experiments.json` |
| `results/summary.json` | Full final metrics, eligible query IDs, paired outcomes and recorded resource summaries |
| `results/rankings.jsonl` | Per-query candidate IDs, order, scores and final labels |
| `results/agent-answers.jsonl` | 717 saved agent outputs, final selection labels, statuses and available usage/costs |
| `SCHEMA.md` | Field descriptions and interpretation |
| `SHA256SUMS` | Checksums for the files in this package |

Recipe documents, model-input contexts, experiment runners, request/SDK logs, indexes, model weights and intermediate annotation history are excluded. Agent explanations and final outputs are retained as model-produced results; they can mention ingredients or quote brief source fragments. No full recipe contexts are included.

## Download recipe documents

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/). From this directory:

```sh
uv sync
uv run python fetch_recipes.py
```

The script calls the official TheMealDB API for letters a–z, deduplicates by source ID, filters incomplete records and writes `downloaded/recipes/*.md` plus `downloaded/recipes.json`. Only PyYAML is required. No models or paid inference are involved. The default output folder is ignored by Git.

```sh
uv run python fetch_recipes.py --output-dir /path/to/a/dedicated/output
```

Use a dedicated output directory: the importer replaces existing Markdown files in its `recipes/` subfolder. `--limit N` keeps the first N valid records in stable ID order; it does **not** recover the historical benchmark subset.

The live API can add, change or remove recipes. A fresh download is not guaranteed to reproduce the original 790 documents. Use `data/corpus-reference.json` to identify the original subset and compare hashes; ignore newly added IDs when comparing. A matching ID alone does not establish matching content. Hashes cover the complete generated Markdown bytes, including metadata and whitespace. Missing or changed documents cannot be reconstructed from a hash.

## Read and verify results

The saved results can be read without downloading recipes or installing Python dependencies. This package supports inspection of recorded outputs and metrics. Re-running model experiments requires an independent implementation using the published settings and prompts; experiment runners and a metric-recalculation script are not included.

Verify package integrity on macOS/Linux:

```sh
shasum -a 256 -c SHA256SUMS
```

These checksums verify exported bytes, not upstream billing or the historical recipe content. The method explains why cohorts, failures, unresolved judgments and costs must retain their original denominators and meaning.

## Recipe source

Recipes are obtained directly from [TheMealDB](https://www.themealdb.com/) using its official API. Recipe content is governed by [TheMealDB terms](https://www.themealdb.com/terms_of_use.php); this package does not grant a separate license to that content. The API guide documents [development access](https://www.themealdb.com/docs_api_guide.php). This package contains the downloader and corpus identifiers/hashes rather than the recipe corpus or images.
