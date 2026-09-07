"""Run the baseline over all scenarios in scenarios.json and report scores.

Usage:  python eval/evaluate_batch.py [--live]
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from tools import set_live                       # noqa: E402
from agent import build_agent                    # noqa: E402
from eval.evaluate import check_plan             # noqa: E402
from run_baseline import extract_plan            # noqa: E402


def user_message(s):
    c = s["constraints"]
    return (f"{s['request']}\n\nHard constraints: budget_pp=${c['budget_pp']}, "
            f"vegan_required={c['vegan_required']}, target_hour={c['target_hour']} (24h), "
            f"max_walk_m={c['max_walk_m']}, party_size={c['party_size']}, "
            f"search near lat={c['area']['lat']}, lon={c['area']['lon']}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    set_live(args.live)

    scenarios = json.loads((ROOT / "eval" / "scenarios.json").read_text())
    agent = build_agent()
    scores = []
    print(f"{'='*70}\nBASELINE EVALUATION ({len(scenarios)} scenarios, mode={'LIVE' if args.live else 'offline'})\n{'='*70}")
    for s in scenarios:
        res = agent.invoke({"messages": [("user", user_message(s))]})
        plan = extract_plan(res["messages"][-1].content)
        r = check_plan(plan, s["constraints"])
        scores.append(r["score"])
        print(f"{s['name']:26} score={r['score']}  valid={r['valid']}  {r['checks']}")
    print(f"\nMEAN constraint-satisfaction score: {sum(scores)/len(scores):.2f}")


if __name__ == "__main__":
    main()
