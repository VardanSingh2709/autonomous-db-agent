import json, re

def extract_number(text):
    """Finds numbers in text, ignoring digits that are part of a Q1/Q2/Q3/Q4 label."""
    if text is None:
        return None
    cleaned = str(text).replace(",", "")
    match = re.search(r"(?<![Qq])-?\d+\.?\d*", cleaned)
    return float(match.group()) if match else None

def extract_all_numbers(text):
    if text is None:
        return []
    cleaned = str(text).replace(",", "")
    return [float(m) for m in re.findall(r"(?<![Qq])-?\d+\.?\d*", cleaned)]

def close(a, b, tol=0.02):
    if a is None or b is None:
        return False
    return abs(a - b) <= (abs(b) * tol + 0.01)

# Manual overrides for answers we can visually confirm are correct despite
# not being machine-parseable (e.g. spelled-out numbers like "four").
MANUAL_OVERRIDES = {
    "simple_03": True,  # answered "four" — correct, just not a digit
}

with open("benchmark/ground_truth.json") as f:
    ground_truth = json.load(f)
with open("benchmark/baseline_results.json") as f:
    results = json.load(f)

for r in results:
    if r["id"] in MANUAL_OVERRIDES:
        r["grading"] = {"gradable": True, "correct": MANUAL_OVERRIDES[r["id"]], "note": "manually verified (non-numeric answer format)"}

    elif r["category"] == "time_comparison":
        true_row = ground_truth[r["id"]]["result"][0]
        # time_03 uses "may_1"/"answer" keys instead of "q2"/"answer" — handle both
        true_first = true_row.get("q2", true_row.get("may_1"))
        true_second = true_row.get("answer")
        nums = extract_all_numbers(r["answer"])
        correct = any(close(n, true_first) for n in nums) and any(close(n, true_second) for n in nums)
        r["grading"] = {"gradable": True, "correct": correct, "true_first": true_first, "true_second": true_second}

    elif r["category"] == "root_cause":
        gt_root = ground_truth[r["id"]]["scenario_ground_truth"]["ground_truth"]["root_cause"]
        short_facts = [str(v).lower() for k, v in gt_root.items() if k != "explanation" and isinstance(v, str)]
        answer_text = str(r["answer"] or "").lower()
        if not short_facts:
            # No simple categorical fact exists for this scenario (e.g. product_mix_effect) —
            # can't grade by keyword matching. Mark as ungradable, don't default to True.
            r["grading"] = {"gradable": False, "reason": "no categorical fact to check for this scenario type"}
        else:
            mentioned = sum(1 for fact in short_facts if fact in answer_text)
            correct = mentioned == len(short_facts)
            r["grading"] = {"gradable": True, "correct": correct, "short_facts": short_facts, "facts_found": mentioned}

    else:  # simple, aggregation, joins
        true_row = ground_truth[r["id"]]["result"][0] if ground_truth[r["id"]]["result"] else {}
        true_value = true_row.get("answer")
        true_num = extract_number(true_value)
        submitted_num = extract_number(r["answer"])
        if true_num is not None and submitted_num is not None:
            correct = close(submitted_num, true_num)
        else:
            correct = str(true_value).strip().lower() in str(r["answer"] or "").strip().lower()
        r["grading"] = {"gradable": True, "correct": correct, "true_value": true_value}

    print(f"{r['id']} ({r['category']}): {r['grading']}")

with open("benchmark/baseline_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

gradable = [r for r in results if r["grading"].get("gradable")]
correct_count = sum(1 for r in gradable if r["grading"].get("correct"))
print(f"\nFinal: {correct_count}/{len(gradable)} correct ({len(results) - len(gradable)} ungradable, excluded from score).")