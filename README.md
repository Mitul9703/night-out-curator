# 🌃 Night-Out Curator — Agentic AI Baseline

A tool-using AI agent that plans a **two-stop night out** (dinner + one spot after) in the
**Tempe / greater Phoenix** area from a natural-language request, respecting real constraints:
**budget per person, dietary needs (vegan), open hours, and walkability**.

This repo is the **Phase-0 runnable baseline** for a CSE 598 (Agentic AI) capstone. It is
deliberately minimal — a single tool-using agent — so that the full multi-agent project can
measurably improve over it (see [Roadmap](#roadmap)).

> **Cost & keys:** every data source is **free and needs no credit card**. The only paid piece
> is the LLM, and even that has **free, no-card options** (Gemini Flash free tier, or local Ollama).

---

## What it does (the agent loop)

```
request ─▶ Agent
             ├─ search_venues   (Geoapify / bundled)      → candidate dinner + after-spots
             ├─ walk_route      (Geoapify / haversine)    → is the hop walkable?
             ├─ transit         (Valley Metro / Transitland) → or one short transit hop?
             └─ weather         (Open-Meteo)              → patio vs indoor, conditions
           ─▶ recommends a 2-stop plan  ─▶  objective constraint check (score)
```

## APIs used — all free, no credit card

| Capability | Source | Free? | Card? |
|---|---|---|---|
| Venue discovery + dietary filter + walking routes | [Geoapify](https://www.geoapify.com/) | ✅ 3,000/day | ❌ none |
| Public transit (bus/rail/streetcar) | [Valley Metro GTFS](https://www.phoenixopendata.com/) + [Transitland](https://www.transit.land/) | ✅ | ❌ none |
| Weather | [Open-Meteo](https://open-meteo.com/) | ✅ | ❌ none |
| LLM (default) | OpenAI | 💳 paid | yes |
| LLM (free option) | Google **Gemini Flash** free tier / **Ollama** (local) | ✅ | ❌ none |

**The baseline runs fully OFFLINE using bundled real Tempe data** (`data/`), so **no data-API keys
are required to reproduce it** — you only need one LLM provider configured. The `--live` flag
switches the tools to the real APIs.

### Scope: why Phoenix (for now)
The project is scoped to **greater Phoenix** because the free, no-card public-transit data
(**Valley Metro GTFS**) is regional. Venue/weather sources (Geoapify, Open-Meteo) are global, so the
approach generalizes to **any city** by swapping in that city's GTFS feed, or by using **Google
Directions/Routes** transit (which supports any city but **requires a billing account / credit card**).

---

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then edit .env to configure ONE LLM provider
```

Configure **one** LLM in `.env`:

| Provider | `.env` settings | Notes |
|---|---|---|
| **OpenAI** (default) | `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`, `OPENAI_API_KEY=...` | paid, best quality |
| **Anthropic** | `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-3-5-haiku-latest`, `ANTHROPIC_API_KEY=...` | paid |
| **Gemini Flash** | `LLM_PROVIDER=google_genai`, `LLM_MODEL=gemini-2.0-flash`, `GOOGLE_API_KEY=...` | **free tier, no card** ([get key](https://aistudio.google.com/apikey)) |
| **Ollama** (local) | `LLM_PROVIDER=ollama`, `LLM_MODEL=llama3.1` | **free, no card**; `ollama pull llama3.1` first |

Provider selection is handled generically in [`src/llm.py`](src/llm.py) via LangChain's `init_chat_model`, so adding another supported provider is just an env change.

(For `--live` only: also set `GEOAPIFY_KEY` and `TRANSITLAND_KEY` — both free, no card.)

## Run

```bash
# Offline (bundled data — recommended for reproducing; no data keys needed):
python run_baseline.py --scenario examples/test1.json

# Live (calls the real free APIs; needs GEOAPIFY_KEY + TRANSITLAND_KEY):
python run_baseline.py --scenario examples/test1.json --live
```

- **Input:** a scenario JSON in `examples/` (request text + hard constraints).
- **Output:** printed to the console **and** saved to `examples/output_<name>.txt`.

## Evaluation

```bash
python eval/evaluate_batch.py        # runs all scenarios in eval/scenarios.json, prints scores
```

The scorer (`eval/evaluate.py`) checks each plan against **ground-truth** venue data and reports a
0–1 **constraint-satisfaction score** over: budget, vegan, open-at-time, walkable. This is the
objective metric the full system is meant to improve.

## Test case & expected output

**Input** (`examples/test1.json`): *"Plan a night out for 4 near ASU Tempe Friday ~7pm, ~$40/person,
chill and walkable, one of us is vegan. Dinner + one spot after."*

**Expected behavior:** the agent searches for a vegan-friendly, walkable, in-budget plan (e.g.
**Pita Jungle → The Gelato Spot**) and prints a constraint check. A *valid* plan scores **1.0**.
Because the baseline has **no price/vibe data** (that's a Phase-2 web-enrichment feature), it can
also pick invalid plans — the score makes that visible. See `examples/output_test1.txt` and the
screenshot in `docs/`.

## Regenerate the bundled data (optional)

```bash
TRANSITLAND_KEY=... python scripts/cache_samples.py   # refresh weather + transit samples
```

---

## Roadmap (how the full project beats this baseline)

| | Baseline (this repo) | Full project (Phases 2–4) |
|---|---|---|
| Agents | one ReAct agent | **multi-agent** (Discovery, Enrichment, Transit, Weather, Critic) on **LangGraph** |
| Price / hours / vibe | ❌ not in free data → estimated | ✅ **web-fetch enrichment** reads each venue's site/menu |
| Verification | none | **Constraints-Critic** verifies & **re-plans** |
| Metric | low constraint-satisfaction | high constraint-satisfaction |

---

## Attribution
Venue data © OpenStreetMap contributors / Geoapify (ODbL). Transit data © Valley Metro (City of
Phoenix Open Data) via Transitland. Weather by Open-Meteo. Keys are read from environment variables
and are never committed.
