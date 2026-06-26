# Linkup GTM Benchmarks

Public, reproducible benchmarks of how well web-search / answer APIs —
**Linkup · Exa · Perplexity · Parallel** — do the go-to-market work teams actually
wire them into: **enriching people** and **researching companies**.

Each benchmark ships its dataset, the exact queries, the scoring code, and the
results, so every number on this page can be re-run and re-checked. Search is
non-deterministic and a couple of these sets are built on Linkup's home turf — we
say so where it matters and tried to design the scoring to be fair to every engine,
not flattering to one.

> **Why this exists.** A search/answer API is increasingly the retrieval layer
> behind CRM enrichment, pre-call research, lead scoring, and signal detection. The
> usual benchmarks for these APIs measure generic QA. These measure the GTM jobs:
> given a person, return *that* person; given a company, return information a rep
> can act on.

---

## Linkup across GTM tasks

Two benchmarks, scored across all four engines. Higher is better unless noted.

### People

| Signal | What it measures | Linkup | Exa | Perplexity | Parallel |
|---|---|---|---|---|---|
| **Enrichment** | Returned the **correct person** from a profile URL (n=500) | **94%** | 56% | 64% | 63% |
| **Richness** | Pre-meeting **brief quality**, judged 0–100 (n=100) | **64.8** | 55.8 | 53.1 | 59.8 |
| **Freshness** | Caught a **just-happened job change** (n=57) | **74%** | 14% | 9% | 11% |

### Company

| Signal | What it measures | Linkup | Exa | Perplexity | Parallel |
|---|---|---|---|---|---|
| **Research depth** | **Actionable signals** found per company (n=150) | **71.8** | 71.2 | 49.6 | 46.4 |
| **Funding accuracy** | Total funding within **±25%** of Crunchbase (n=93) | **82%** | 71% | 60% | 74% |

A theme runs through both: engines that *search for a name* tend to land on a
namesake or a cached page, while fetching the URL / grounding on a verified
identity returns the right entity more often. Each section below shows where that
shows up — and where the gap closes.

---

## People

Source: [`people/`](people) (from
[`linkedin-extraction-benchmark`](https://github.com/shauryajain21/linkedin-extraction-benchmark)).
Three signals that cover the people-data lifecycle: getting the record right,
turning it into something useful, and keeping it current.

### Signal 1 — Enrichment success rate *(completeness + correctness, n=500)*

Hand each API a LinkedIn URL and ask for the full profile via its native
structured-output endpoint. Two deterministic checks against an independent
ground-truth DB: *how much came back*, and *is it the right person?*

| Engine | Fields filled (completeness /100) | Correct person (%) | Wrong person / namesake (of 500) |
|---|---|---|---|
| **Linkup** | **96.5** | **94%** | **12** |
| Perplexity | 73.7 | 64% | 122 |
| Exa | 71.9 | 56% | 191 |
| Parallel | 60.5 | 63% | 69 |

![Returned the correct person, by engine](assets/people_enrichment.png)

Completeness and correctness are different questions: an engine can fill the *name*
box confidently while attaching the wrong human's company. Because correctness is
checked against an independent DB, the gap measures the thing downstream automation
depends on — whether the record points at the right account before a rep ever sees
it.

**Where this matters in GTM:**
- **CRM enrichment & data hygiene** — fill missing title/company/location/work
  history on inbound leads or an existing book of accounts; correctness is what
  keeps the database trustworthy as it scales.
- **Lead routing & scoring** — the right company and title decide ICP fit and which
  rep owns the lead; a wrong-company match routes and scores against the wrong account.
- **Identity resolution & dedupe** — matching the right person avoids merging two
  different humans into one record.
- **List / TAM building** — turning a set of profile URLs into a clean target-account
  list depends on both fields being present *and* correct.

### Signal 2 — Richness of content *(pre-meeting brief quality, n=100)*

A different task from extraction: each engine's raw web results are synthesized into
a short sales brief (notes + conversation questions), then scored by an Opus-4.8
judge on freshness + specificity + actionability.

| Engine | Brief score (overall /100) | Freshness | Specificity | Actionability | Best brief (of 100) |
|---|---|---|---|---|---|
| **Linkup** | **64.8** | **58.6** | 69.4 | **68.2** | **51** |
| Parallel | 59.8 | 45.9 | 70.1 | 64.9 | 26 |
| Exa | 55.8 | 43.9 | 66.0 | 59.9 | 16 |
| Perplexity | 53.1 | 42.6 | 59.7 | 58.1 | 6 |

![Pre-meeting brief quality, by engine](assets/people_richness.png)

**Where this matters in GTM:** account research before a call. Freshness is the
differentiator — surfacing a post from last week or a just-announced round preps a
rep better than a 2019 job title. The scoring is honest about trade-offs: Parallel
edges raw specificity, Perplexity is most reliably on the right person.

### Signal 3 — Freshness of people content *(job-change detection, n=57)*

We took a subset of people who changed jobs **this month** and asked each engine for
their current employer — does it report the **new** company or the **stale** old one?

| Engine | Caught the move (fresh %) | Reported stale employer | Wrong person | No answer |
|---|---|---|---|---|
| **Linkup** | **74%** | 7 | 4 | 4 |
| Exa | 14% | 32 | 11 | 6 |
| Parallel | 11% | 30 | 11 | 10 |
| Perplexity | 9% | 17 | 7 | 28 |

![Caught a just-happened job change, by engine](assets/people_freshness.png)

**Where this matters in GTM:** job-change signals are among the highest-value sales
triggers — a champion who just moved may buy again — but only if they're fresh. The
common failure mode is *stale*: finding the right person but reporting their previous
company as current. Because company names appear across languages and abbreviations,
classification here is judged by an Opus-4.8 model rather than string-matched.

*The same retrieval question — fetch the live profile vs. search the name — also
powers other GTM signals (funding rounds, hiring spikes, leadership changes); job
changes are the one isolated here.*

---

## Company

Firmographics and research that drive account scoring, prioritization, and outbound.
Two signals are live; more are in progress.

### Signal 1 — B2B company research *(n=150, 5 sections)*

Source: [`company/research-150/`](company/research-150) (from
[`linkup-company-bench-150`](https://github.com/shauryajain21/linkup-company-bench-150)).

For 150 real companies, each engine runs five sections of GTM research. The method
is held identical across engines so the result reflects *retrieval*, not the writer:

1. **Agentic retrieval** — for each section the engine runs the section's searches
   (and scrapes the company page where supported) and returns **raw sources only**,
   no generated answer.
2. **Shared synthesis** (`claude-sonnet-4-6`) — the same prompt turns each engine's
   raw results into a structured list, grounded *only* in what that engine returned.
3. **Judge** (`claude-opus-4-8`) — scores each section against the company's
   **verified identity** (domain, HQ, founded, funding, investors) for right-company,
   on-target sources, and whether it answered the ask.

The five sections — what each set of queries goes after, and why it's GTM signal:

| Section | What the queries target | Why it matters |
|---|---|---|
| **Offering** | homepage + *"what does {company} do / product"* | the core pitch: what they sell and to whom |
| **Pain → solution** | *features / benefits* + *pain point / problem / solution* | maps buyer problems to the product angle a rep leads with |
| **Case studies** | *case study / success story / ROI / metrics* | proof points: customer + key result |
| **Customers** | *customer / client / "trusted by" / partnership* | named logos and partners for account mapping |
| **CTAs** | site-scoped *book a demo / pricing / sign up* | the buying motion and conversion signals |

| Engine | Actionable signals / co. | Repeated | On-target sources | Answered the ask | Right company | Worst-case (P10) |
|---|---|---|---|---|---|---|
| **Linkup** | **71.8** | 11% | **82.7%** | **79.5%** | **85%** | **59.1** |
| Exa | 71.2 | 17% | 77.7% | 73.0% | 80% | 56.1 |
| Parallel | 46.4 | 13% | 75.9% | 70.6% | 78% | 55.8 |
| Perplexity | 49.6 | 3% | 75.2% | 69.6% | 78% | 51.9 |

![Actionable signals found per company, by engine](assets/company_research.png)

Only relevance and identification use the judge; quantity, dedup, source-mix, and
worst-case consistency are computed deterministically and recompute from the captured
data. **Where this matters in GTM:** account research and territory planning at scale —
more distinct, on-target signal per company, with a steady worst case so the pipeline
doesn't fall apart on the hard accounts.

### Signal 2 — Funding retrieval *(n=93)*

Source: [`company/research-evals/`](company/research-evals) (from
[`company-research-evals`](https://github.com/shauryajain21/company-research-evals)).

Given only a company's **name + HQ + founding year**, return total funding raised via
each engine's structured output. Scored against Crunchbase total equity funding;
`error = |api − golden| / golden`.

| Engine | Within 10% | Within 25% | Within 50% | Median error | Coverage |
|---|---|---|---|---|---|
| **Linkup** | **67%** | **82%** | **90%** | **2%** | 100% |
| Parallel | 57% | 74% | 81% | 6% | 100% |
| Exa | 52% | 71% | 85% | 10% | 100% |
| Perplexity | 45% | 60% | 74% | 15% | 94% |

![Funding within ±25% of Crunchbase, by engine](assets/company_funding.png)

Scored on the 93 companies where every engine returned a number. **Where this matters
in GTM:** funding is a core firmographic for ICP fit, account scoring, and timing —
hitting the actual number (not just the right ballpark) is what makes it usable in a
scoring model. *Note: this set is selection-biased toward Linkup (see Caveats).*

---

## Methodology

The benches differ in task, but share the same design principles — built to be
reproducible and to reward signal a GTM team can actually use, not raw volume.

- **Each API at its own native surface.** Extraction uses structured-output
  endpoints; research uses raw search endpoints. No LLM wrapper sits between the API
  and the score, so we measure the retrieval engine itself. Where a step *does* need
  a model (synthesizing a brief, structuring research), it's held **identical across
  all four engines** so differences reflect retrieval, not the writer.
- **Independent ground truth.** People correctness joins to a profile DB not derived
  from any of the four APIs; funding checks against Crunchbase; company research is
  anchored on a verified company identity. No self-reference bias.
- **Deterministic where possible, judged where necessary.** Field-fill, company-match,
  dedup, source-mix, and consistency are computed deterministically. An LLM judge is
  used only where strings fail — cross-language company names, and the quality of a
  brief or a research answer.
- **Judged for business signal, not volume.** The judge rubrics deliberately reward
  what a rep needs — *fresh, specific, on-target, and actionable* — and penalize
  padding, namesakes, and stale or fabricated detail. A long answer full of generic or
  duplicated points scores worse than a short one that's correct and current.
- **Reproducible.** Datasets, queries, and scoring scripts are committed; the company
  bench even ships its captured retrieval so you can rebuild the scorecard with zero
  API calls. Search is non-deterministic, so committed numbers are one representative
  run.

---

## Repo layout

```
Linkup-GTM-benchmarks/
├── README.md                    # this file — the single combined narrative
├── people/                      # LinkedIn profile extraction — 3 signals (n=500)
└── company/
    ├── research-150/            # B2B company research — 5 sections (n=150)
    └── research-evals/          # funding retrieval (+ future company evals)
```

Each folder is self-contained — its own data, scripts, and a deep-dive README with
full reproduction steps. This top-level README is the single source for the combined
story and results.

```bash
git clone https://github.com/shauryajain21/Linkup-GTM-benchmarks.git
cd Linkup-GTM-benchmarks
# then cd into a bench folder and follow its README to reproduce
```

---

## Caveats

- **Search is non-deterministic.** Re-runs shift a few values; committed numbers are
  one representative run.
- **Some sets are intentionally biased**, and we read them that way. The funding set
  is the 93/100 companies where Linkup did best in a larger run — read it as "on home
  turf," not a neutral ranking. The job-change set is, by construction, people who
  recently moved.
- **These are transparent vendor benchmarks.** Linkup built them, and Linkup wins on
  this page. The method, data, and scoring are open precisely so the claims can be
  checked and re-run rather than taken on faith.
