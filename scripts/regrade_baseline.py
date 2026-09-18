import json, re

def extract_numbers_excluding_quarter_labels(text):
    """Finds numbers in text, ignoring digits that are part of a Q1/Q2/Q3/Q4 label."""
    if text is None:
        return []
    cleaned = str(text).replace(",", "")
    # Negative lookbehind: don't match a digit immediately preceded by Q or q
    matches = re.findall(r"(?<![Qq])-?\d+\.?\d*", cleaned)
    return [float(m) for m in matches]


def close(a, b, tol=0.02):
    if a is None or b is None:
        return False
    return abs(a - b) <= (abs(b) * tol + 0.01)


with open("benchmark/ground_truth.json") as f:
    ground_truth = json.load(f)
with open("benchmark/baseline_results.json") as f:
    results = json.load(f)

for r in results:
    if r["category"] == "time_comparison":
        true_row = ground_truth[r["id"]]["result"][0]
        true_q2, true_q3 = true_row.get("q2"), true_row.get("answer")
        nums = extract_numbers_excluding_quarter_labels(r["answer"])
        # crude but effective: correct if BOTH true values appear somewhere in the extracted numbers
        correct = any(close(n, true_q2) for n in nums) and any(close(n, true_q3) for n in nums)
        r["grading"] = {"gradable": True, "correct": correct, "true_q2": true_q2, "true_q3": true_q3, "extracted_numbers": nums}

    elif r["category"] == "root_cause":
        # Only check the SHORT categorical fact (region/product/tier/channel/customer_type),
        # never the full prose explanation.
        gt_root = ground_truth[r["id"]]["scenario_ground_truth"]["ground_truth"]["root_cause"]
        short_facts = [str(v).lower() for k, v in gt_root.items() if k != "explanation" and isinstance(v, str)]
        answer_text = str(r["answer"] or "").lower()
        mentioned = sum(1 for fact in short_facts if fact in answer_text)
        correct = mentioned == len(short_facts)
        r["grading"] = {"gradable": True, "correct": correct, "short_facts": short_facts, "facts_found": mentioned}

    print(f"{r['id']}: {r['grading']}")

with open("benchmark/baseline_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

correct_count = sum(1 for r in results if r["grading"].get("correct"))
print(f"\nRe-graded. {correct_count}/{len(results)} correct.")