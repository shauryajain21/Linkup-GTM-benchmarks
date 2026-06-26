# Linkup Company-Research Bench (150 companies)

A reproducible benchmark comparing four web-retrieval APIs — **Linkup, Exa, Perplexity, Parallel** — on **B2B company research** across **150 real companies**. For each company, every engine retrieves five sections of GTM-relevant info; a shared synthesizer structures the results; an LLM judge scores relevance against a verified company identity.

## Result (n = 150)

| Engine | Actionable signals / company | Information repeated | On-target sources | Answers what was asked | Right company found | Worst-case consistency (P10) |
|---|---|---|---|---|---|---|
| **Linkup** | **71.8** | 11% | **82.7%** | **79.5%** | **85%** | **★ 59.1** |
| Exa | 71.2 | 17% | 77.7% | 73.0% | 80% | 56.1 |
| Parallel | 46.4 | 13% | 75.9% | 70.6% | 78% | 55.8 |
| Perplexity | 49.6 | 3% | 75.2% | 69.6% | 78% | 51.9 |

On this set Linkup is #1 on every dimension: more distinct signals with less repetition, more on-target sources, more often the right company, and the steadiest worst-case.

**Column meanings**
- **Actionable signals / company** — distinct, **deduplicated** items returned across the 5 sections.
- **Information repeated** — % of returned items that were duplicates (lower = less padding).
- **On-target sources** — share of retrieved signals actually **pointing at the target company** (purity).
- **Answers what was asked** — share of signals that **address the section's question**.
- **Right company found** — % of sections where the engine identified the **correct entity** (not a namesake).
- **Worst-case consistency (P10)** — relevance at the engine's **worst 10%** of companies (higher = degrades less).

## How it works

**Pipeline (per company × 5 sections × 4 engines):**
1. **Agentic retrieval** — each engine scrapes the company page (where supported) + runs the section's searches, returning raw sources. Per-provider QPS limits: Linkup 25, others 10.
2. **Synth** (`claude-sonnet-4-6`) — formats each engine's raw results into a structured JSON list, **grounded only in that engine's results** (identical synth for all → differences reflect retrieval, not the writer).
3. **Judge** (`claude-opus-4-8`) — per (company, section), scores each engine on `right_company` (identification), `entity_relevance` (on-target sources), `topical_relevance` (answers the ask), anchored on the company's verified identity (domain, HQ, founded, funding, investors).

Quantity, dedup/duplicate-rate, completeness, source-mix, unique-recall, URL-backed%, authority, and consistency (P10/bomb) are computed **deterministically** at aggregate time — only relevance/identification uses the LLM judge.

### The 5 sections (search queries + output schema)
| Section | Searches run | Output |
|---|---|---|
| `1_offering` | `"{name}" {domain} what does company do product` (+ scrape) | `{offering_points:[...]}` |
| `2_features` | features/benefits + pain-point/solution (+ scrape) | `{pairings:[{pain_point,solution,feature}]}` |
| `3_case_studies` | case study / success story / ROI (+ scrape) | `{exists,case_studies:[{url,customer,key_result}]}` |
| `4_customers` | customer / "trusted by" / partnership (+ scrape) | `{customers:[{name,url}]}` |
| `5_ctas` | pricing / demo / signup CTAs (+ scrape) | `{ctas:[{text,url,location}]}` |

Exact query templates, synth instructions, schemas, the **disambiguation block**, and the **judge prompt** are all in `run_bench.py` (`SECTIONS`, `SYNTH_SYS`, `JUDGE_SYS`).

## Reproduce

The captured retrieval/synth/judge data ships in `results/*.jsonl`, so you can rebuild the scorecard with **zero API calls**:

```bash
pip install -r requirements.txt
python3 run_bench.py --aggregate    # rebuilds results/scorecard.json from captured data
python3 report.py                   # prints the table above
```

### Re-run live (fresh data)
```bash
cp .env.example .env                # add your 5 API keys
rm results/raw.jsonl.gz results/synth.jsonl results/judge.jsonl  # clear captured data to re-fetch
python3 run_bench.py --concurrency 24   # all 150 companies (resumable; ~per-provider QPS throttled)
python3 run_bench.py --aggregate && python3 report.py
```
`run_bench.py` is resumable (skips keys already in the stores) and persists after every unit. `--dry-run` prints the plan + rendered prompts without any API calls. `--limit N` / `--offset N` for subsets.

## Files
```
data/companies_150.csv     # the 150 companies + disambiguation fields (name, domain, url, HQ, founded, funding, investors, crunchbase)
run_bench.py               # harness: agentic retrieval -> synth -> judge -> aggregate (prompts + judge infra live here)
report.py                  # prints the display-named result table from results/scorecard.json
results/
  raw.jsonl.gz             # captured retrieval (3,000 units = 150 × 5 × 4), gzipped (55M); harness reads it transparently
  synth.jsonl              # captured structured answers
  judge.jsonl              # captured judge verdicts (750 = 150 × 5)
  scorecard.json           # aggregated metrics (regenerated by --aggregate)
  table.md                 # the result table
requirements.txt           # httpx
.env.example               # API key placeholders
```

## Notes
- **Deduped quantity.** "Signals/company" counts *distinct* items; raw counts and duplicate-rate are both in `scorecard.json`.
- **Judge is the only LLM scoring step**; everything else is deterministic and recomputable from the captured stores.
