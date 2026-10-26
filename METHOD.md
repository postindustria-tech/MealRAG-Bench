# Dataset and evaluation method

## Dataset construction

The original corpus consists of 790 complete recipe documents downloaded from TheMealDB. Documents are not chunked. The importer requires an ID, title, instructions and at least two nonempty ingredients. Ingredient wording and amounts are preserved; instruction line endings and repeated blank lines are normalized. Each Markdown document records its source and source URL. Images are not downloaded.

The 90 English queries cover ingredient requests, natural phrasing, semantic matches, cuisine, ambiguity, exclusions and deliberately difficult cases. Query families can overlap across experiment cohorts. Known full matches are the annotated matches, not an exhaustive relevance set for the entire corpus.

The final version, `mealrag-final-v1`, reconciles 6,663 query–recipe judgments, including 12 explicit human pair decisions. Annotation was AI-assisted with scoped human review. Labels were partly refined after inspecting results. This is not exhaustive independent human certification or a pristine unseen test set. The original outputs and ranking order were retained and evaluated against the final labels without new generation.

The public export retains final labels and the rationale for the 12 human-adjudicated pairs. Original recipe excerpts, intermediate judgments and annotation audit history are omitted. Some human interpretations use ordinary culinary meaning or author-supplied clarification; they are local decisions, not general rules applied to unreviewed pairs.

## Relevance labels

| Label | Meaning |
| --- | --- |
| `2` | Full match: the documented recipe meets the request under the adopted interpretation |
| `1` | Partial match: some intent is met, but a requested property is missing or unsupported |
| `0` | Irrelevant: the central intent fails or an explicit exclusion is violated |
| `?` | Unresolved judgment |
| `unjudged` / absent pair | No reference judgment; never treated as zero |

An open ingredient list allows additional ingredients. A recipe is evaluated as written: substitutions or imagined missing ingredients do not establish a match. Scaling portions does not create a missing ingredient. Ingredient form, dish identity, cuisine and explicit exclusions matter. An ambiguous composite ingredient does not establish its full composition.

## Retrieval and reranking

Retrieval uses full documents, exact cosine search, L2-normalized float32 vectors and six recorded embedding configurations. The plain document representation is:

```text
Title: {title}
Cuisine: {area, when present}
Category: {category, when present}

Ingredients:
{ingredient lines without Markdown bullet prefixes}

Instructions:
{instructions}
```

Model-specific prefixes/templates are recorded in `settings/experiments.json`. Gemini's document wrapper is `title: {title} | text: {content}`, where `{content}` is the same labeled plain document representation above. The title therefore appears in both the wrapper and document text. No silent client truncation was used; upstream gateway behavior is not independently certified.

Dense snapshots retain top-20. Each reranker independently scores query–recipe pairs from each dense top-10 pool. The six pools share 2,046 unique pairs. Scores sort descending; ties retain original dense order. Qwen scores the yes/no logit difference, BGE a raw logit, chat rerankers a 0–100 score, and Jev an expected level on its 0–3 criteria. These scores are not interchangeable calibrated probabilities. Exact reranker instructions, wrappers, schemas and Jev criteria are in the settings.

BM25 uses the documented fixed tokenization, parameters and equal-weight RRF in `settings/experiments.json`. It is a single configuration, without a parameter sweep.

## Cohorts and metrics

The 21-query diagnostic set was deliberately chosen to expose retrieval problems; the 69-query remainder and 18-query pilot answer different experimental questions. Their overlapping families and prior development exposure prevent interpreting them as independent holdouts. Exact query IDs are retained for every agent profile.

Retrieval uses a frozen 85-query scope selected from originally positive queries. The 42-configuration ranking matrix reports Top-1 on 84 commonly resolved queries and MRR@10 on 82 commonly eligible queries. Other comparisons calculate their own common eligible subset: the Gemini dense/hybrid pair uses 85 for Top-1 and 83 for MRR@10. The five original empty-gold queries do not certify corpus-wide unanswerability.

Top-1 counts a full match at the first position. MRR@10 is the mean reciprocal rank of the first full match within ten results; unresolved positions that could change that rank exclude a query. A resolved list with no full match scores zero. Unknown positions are not removed to improve ranks. `summary.json` records the exact eligibility lists and denominators.

Success@k counts queries with at least one full match in the retrieved pool. Precision@k counts full-match positions divided by query count times k. Lower bounds treat unknown positions as non-full; upper bounds allow them to be full. These are retrieved-pool metrics, not corpus-wide recall.

## Agent outcomes

An agent receives the request and full recipe texts, without reference labels or diagnostic strata. It returns one recipe ID or null and an explanation. Modes supply initial context, permit search, or combine both; profile settings record the context size and limits. Search formulation starts with no documents and permits one search: Gemini retrieves ten candidates, Luna reranks against the original request, and three full recipes reach the agent.

A selected recipe's final label measures selection quality. It does not certify the explanation, consistency between ID and prose, or correctness of abstention. Multiple full matches permit choosing any one. An abstention does not prove that no full recipe exists in the corpus.

Outcomes retain full/partial/irrelevant/unknown selection, abstention and execution failure separately. Workflow violations and malformed output remain failures. The query-formulation study has 21 full selected recipes but only 18 protocol-compliant full selections; the three violations are preserved. Contradictory JSON outputs are not repaired by selecting a convenient interpretation. Pilot external-judge outputs are exploratory and are not a second final relevance standard.

## Cost, time and limitations

SDK cost estimates, available endpoint reports and historical retrieval/reranking overhead are distinct. Missing usage or cost is unknown, not zero. Agent token components retain ordinary input, cache creation/read and output separately. Pipeline estimates may include replayed historical stage costs; they are not provider invoices. Local compute is not assigned an API charge.

Per-request online latency includes network time for one query–recipe pair. It is not the latency of parallel reranking ten candidates. Batch throughput, warmup, query latency and full experiment wall time have different scopes. Historical model aliases, tariffs and deployment routing describe the saved runs; they are not promises about current availability or pricing. Single runs support descriptive comparisons, not universal model ordering or a proven causal prompt effect.
