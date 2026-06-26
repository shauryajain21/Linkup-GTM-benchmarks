# Company-research evals

Reproducible benchmarks of search/answer APIs (**Linkup · Exa · Perplexity ·
Parallel**) on company-research tasks. Each eval ships its data, the exact queries,
a scoring script, and a graph — so any result can be re-run and re-checked.

## Evals

| Eval | Question | Golden source | Best on this set |
|---|---|---|---|
| [funding-retrieval](funding-retrieval/) | Total funding raised, given only a company's name + HQ + founding year | Crunchbase total equity funding | Linkup (82% within ±25%, 2% median err) |

*More evals will be added as sibling folders.*

![Funding-retrieval accuracy by API](funding-retrieval/results/scorecard.png)

## How to run

Each eval is self-contained in its own folder with a README covering method,
results, and reproduction. Common setup:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then `cd <eval>/` and follow that eval's README. Querying the live APIs needs keys
(copy `.env.example` to `.env`); scoring and plotting the committed data needs only
Python 3.9+ and matplotlib.

## Layout

```
company-research-evals/
├── README.md            # this file
├── requirements.txt
└── <eval>/              # one folder per eval (data, scripts, results, README)
```

## Notes

- Search results are **non-deterministic** — re-runs shift a few values; the
  committed results are one representative run.
- Read each eval's caveats. Sets can be selection-biased; the per-eval README says
  so where it applies.
