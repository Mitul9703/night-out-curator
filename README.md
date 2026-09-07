# Night-Out Curator (Agentic AI Baseline)

A tool-using AI agent that plans a two-stop night out (dinner, then one spot after) in the
Tempe / greater Phoenix area from a request in plain English. It respects real rules: budget per
person, dietary needs (vegan), open hours, and walkability.

This repo is the Phase-0 runnable baseline for a CSE 598 (Agentic AI) capstone. It is kept minimal
on purpose (one tool-using agent), so the full multi-agent project can measurably improve over it
(see [Roadmap](#roadmap)).

> Cost and keys: every data source is free and needs no credit card. The only paid part is the LLM,
> and even that has free, no-card options (Gemini Flash free tier, or local Ollama).

## What it does (the agent loop)

```
request -> Agent
             |- search_venues  (Geoapify / bundled)         candidate dinner + after-spots
             |- walk_route      (Geoapify / haversine)       is the hop walkable?
             |- transit         (Valley Metro / Transitland) or one short transit hop?
             |- weather         (Open-Meteo)                 patio vs indoor, conditions
           -> recommends a 2-stop plan -> objective constraint check (score)
```

## APIs used (all free, no credit card)

| Capability | Source | Free? | Card? |
|---|---|---|---|
| Venue discovery + dietary filter + walking routes | [Geoapify](https://www.geoapify.com/) | yes, 3,000/day | none |
| Public transit (bus/rail/streetcar) | [Valley Metro GTFS](https://www.phoenixopendata.com/) + [Transitland](https://www.transit.land/) | yes | none |
| Weather | [Open-Meteo](https://open-meteo.com/) | yes | none |
| LLM (default) | OpenAI | paid | yes |
| LLM (free option) | Google Gemini Flash free tier, or Ollama (local) | yes | none |

The baseline runs fully offline using bundled real Tempe data in `data/`, so no data-API keys are
needed to reproduce it. You only need one LLM provider. The `--live` flag switches the tools to the
real APIs.

### Scope: why Phoenix (for now)
The project is scoped to greater Phoenix because the free, no-card transit data (Valley Metro GTFS)
is regional. The venue and weather sources (Geoapify, Open-Meteo) are global, so the approach can
extend to any city by dropping in that city's GTFS feed, or by using Google Directions/Routes
transit (which covers any city but needs a billing account / credit card).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then edit .env to set ONE LLM provider
```

Set exactly one LLM provider in `.env`:

| Provider | `.env` settings | Notes |
|---|---|---|
| OpenAI (default) | `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`, `OPENAI_API_KEY=...` | paid, best quality |
| Anthropic | `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-3-5-haiku-latest`, `ANTHROPIC_API_KEY=...` | paid |
| Gemini Flash | `LLM_PROVIDER=google_genai`, `LLM_MODEL=gemini-2.0-flash`, `GOOGLE_API_KEY=...` | free tier, no card ([get key](https://aistudio.google.com/apikey)) |
| Ollama (local) | `LLM_PROVIDER=ollama`, `LLM_MODEL=llama3.1` | free, no card; run `ollama pull llama3.1` first |

Provider selection lives in [`src/llm.py`](src/llm.py) via LangChain's `init_chat_model`, so adding
another supported provider is just an env change.

Data-source keys are only needed for `--live`: set `GEOAPIFY_KEY` and `TRANSITLAND_KEY` (both free,
no card).

## Run

```bash
# Offline (bundled data, recommended for reproducing, no data keys needed):
python run_baseline.py --scenario examples/test1.json

# Live (calls the real free APIs, needs GEOAPIFY_KEY + TRANSITLAND_KEY):
python run_baseline.py --scenario examples/test1.json --live
```

- Input: a scenario JSON in `examples/` (request text + the hard rules). Two are provided:
  `examples/test1.json` and `examples/test2.json`.
- Output: printed to the console and saved to `examples/output_<name>.txt`.

## Evaluation

```bash
python eval/evaluate_batch.py     # runs all scenarios in eval/scenarios.json and prints scores
```

The scorer (`eval/evaluate.py`) checks each plan against ground-truth venue data and reports a 0 to 1
constraint-satisfaction score over budget, vegan, open-at-time, and walkable. This is the objective
metric the full system is meant to improve.

## Test case and expected output

Input (`examples/test1.json`): "Plan a night out for 4 near ASU Tempe Friday ~7pm, ~$40/person,
chill and walkable, one of us is vegan. Dinner + one spot after."

Expected: the agent finds a vegan-friendly, walkable, in-budget plan (for example
Pita Jungle then The Gelato Spot) and prints a constraint check. A valid plan scores 1.0. The exact
saved output is in `examples/output_test1.txt` (and `examples/output_test2.txt` for the second test).

## Regenerate the bundled data (optional)

```bash
TRANSITLAND_KEY=... python scripts/cache_samples.py   # refresh the weather + transit samples
```

## Known limitations

- The offline data in `data/` is a small curated snapshot of Tempe venues, not the whole city.
- `--live` needs the free `GEOAPIFY_KEY` and `TRANSITLAND_KEY` to be set.
- LLM output is not deterministic, so the exact plan can vary between runs.
- The free structured data has no price and lists opening hours only about 20% of the time, so the
  baseline estimates budget and mood rather than verifying them. Recovering these is a Phase-2
  feature (reading venue websites).
- Tested with Python 3.13 and the pinned versions in `requirements.txt`.

## Roadmap (how the full project beats this baseline)

| | Baseline (this repo) | Full project (Phases 2-4) |
|---|---|---|
| Agents | one ReAct agent | multi-agent (Discovery, Enrichment, Transit, Weather, Critic) on LangGraph |
| Price / hours / mood | not in free data, estimated | web-fetch enrichment reads each venue's own page |
| Verification | none | a Critic verifies the plan and asks for a re-plan |
| Metric | lower constraint-satisfaction | higher constraint-satisfaction |

## Attribution
Venue data (c) OpenStreetMap contributors / Geoapify (ODbL). Transit data (c) Valley Metro
(City of Phoenix Open Data) via Transitland. Weather by Open-Meteo. Keys are read from environment
variables and are never committed.
