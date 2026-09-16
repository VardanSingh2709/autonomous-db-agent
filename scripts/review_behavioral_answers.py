import json

with open("benchmark/results.json") as f:
    results = json.load(f)

for r in results:
    if r["category"] in ("ambiguous", "edge_case", "adversarial"):
        print(f"\n=== {r['id']} ({r['category']}) ===")
        print("Q:", r["question"])
        print("A:", r.get("answer"))