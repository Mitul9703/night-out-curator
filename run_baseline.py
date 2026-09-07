"""Run the BASELINE Night-Out Curator on one scenario and score it.

Usage:
    python run_baseline.py --scenario examples/test1.json           # offline (bundled data)
    python run_baseline.py --scenario examples/test1.json --live     # call live free APIs

Requires ONE LLM provider configured in .env (see .env.example):
    OpenAI (default) | Gemini Flash free tier | local Ollama
Output is printed and saved to examples/output_<name>.txt
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from tools import set_live                    # noqa: E402
from agent import build_agent                 # noqa: E402
from eval.evaluate import check_plan, GT      # noqa: E402


def extract_plan(text: str) -> dict:
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    blob = m[-1] if m else None
    if not blob:
        m = re.findall(r"(\{[^{}]*\"stops\"[\s\S]*?\})", text)
        blob = m[-1] if m else None
    try:
        return json.loads(blob) if blob else {"stops": []}
    except Exception:
        return {"stops": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="examples/test1.json")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    scenario = json.loads((ROOT / args.scenario).read_text())
    set_live(args.live)

    c = scenario["constraints"]
    user_msg = (f"{scenario['request']}\n\n"
                f"Hard constraints: budget_pp=${c['budget_pp']}, vegan_required={c['vegan_required']}, "
                f"target_hour={c['target_hour']} (24h), max_walk_m={c['max_walk_m']}, "
                f"party_size={c['party_size']}, search near lat={c['area']['lat']}, lon={c['area']['lon']}.")

    print(f"\n{'='*70}\nSCENARIO: {scenario['name']}  (mode={'LIVE' if args.live else 'offline'})\n{'='*70}")
    print(scenario["request"])

    agent = build_agent()
    result = agent.invoke({"messages": [("user", user_msg)]})
    final = result["messages"][-1].content

    print(f"\n--- agent recommendation ---\n{final}\n")

    plan = extract_plan(final)
    # attach venue names for readability
    for s in plan.get("stops", []):
        v = GT.get(s.get("venue_id"))
        s["name"] = v["name"] if v else "(unknown)"

    report = check_plan(plan, c)
    print(f"{'='*70}\nCONSTRAINT CHECK (objective, vs ground truth)\n{'='*70}")
    for k, ok in report["checks"].items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {k:9}: {report['details'][k]}")
    print(f"\n  score={report['score']}  valid={report['valid']}")
    print("  plan:", " -> ".join(f"{s.get('name')} ({s.get('type')})" for s in plan.get("stops", [])))

    out = ROOT / "examples" / f"output_{scenario['name']}.txt"
    out.write_text(f"SCENARIO: {scenario['name']} (mode={'LIVE' if args.live else 'offline'})\n"
                   f"{scenario['request']}\n\n--- agent recommendation ---\n{final}\n\n"
                   f"--- constraint check ---\n" +
                   "\n".join(f"[{'PASS' if ok else 'FAIL'}] {k}: {report['details'][k]}"
                             for k, ok in report["checks"].items()) +
                   f"\n\nscore={report['score']} valid={report['valid']}\n")
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
