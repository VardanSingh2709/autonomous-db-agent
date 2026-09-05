import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.database.connection import run_query
from benchmark.questions import BENCHMARK_QUESTIONS

ground_truth = {}

for q in BENCHMARK_QUESTIONS:
    if q["ground_truth_type"] == "sql":
        try:
            result = run_query(q["ground_truth_query"])
            ground_truth[q["id"]] = {"status": "ok", "result": result}
            print(f"[OK] {q['id']}: {result}")
        except Exception as e:
            ground_truth[q["id"]] = {"status": "error", "error": str(e)}
            print(f"[ERROR] {q['id']}: {e}")

    elif q["ground_truth_type"] == "scenario":
        # Reuse an already-verified scenario ground truth file rather than recomputing.
        path = f"demo_database/scenarios/{q['scenario_key']}.json"
        with open(path) as f:
            ground_truth[q["id"]] = {"status": "ok", "scenario_ground_truth": json.load(f)}
        print(f"[OK] {q['id']}: (loaded from {path})")

    elif q["ground_truth_type"] == "behavioral":
        ground_truth[q["id"]] = {"status": "behavioral", "expected_behavior": q["expected_behavior"]}
        print(f"[BEHAVIORAL] {q['id']}: {q['expected_behavior']}")

with open("benchmark/ground_truth.json", "w") as f:
    json.dump(ground_truth, f, indent=2, default=str)

print(f"\nDone. {len(BENCHMARK_QUESTIONS)} questions processed, ground truth written to benchmark/ground_truth.json")