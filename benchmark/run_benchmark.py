import sys, os, json, time, re, argparse
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from benchmark.questions import BENCHMARK_QUESTIONS
from app.agents.investigator import investigate, investigate_general


def extract_number(text):
    """Pulls the first number out of a string, for loose comparison. Returns None if none found."""
    if text is None:
        return None
    match = re.search(r"-?\d+\.?\d*", str(text).replace(",", ""))
    return float(match.group()) if match else None


def grade_general_question(question_def, ground_truth_entry, submitted_answer):
    """Compares a submitted answer to a precomputed ground truth value, with tolerance."""
    if ground_truth_entry["status"] != "ok":
        return {"gradable": False, "reason": "ground truth itself failed to compute"}

    true_row = ground_truth_entry["result"][0] if ground_truth_entry["result"] else {}
    true_value = true_row.get("answer")

    submitted_num = extract_number(submitted_answer)
    true_num = extract_number(true_value)

    if true_num is not None and submitted_num is not None:
        correct = abs(submitted_num - true_num) <= (abs(true_num) * 0.02 + 0.01)
        return {"gradable": True, "correct": correct, "true_value": true_value, "submitted": submitted_answer}

    # Fall back to a loose string comparison for non-numeric answers (e.g. region/category names)
    correct = str(true_value).strip().lower() in str(submitted_answer).strip().lower()
    return {"gradable": True, "correct": correct, "true_value": true_value, "submitted": submitted_answer}


def run(category_filter=None, limit=None):
    with open("benchmark/ground_truth.json") as f:
        ground_truth = json.load(f)

    existing_results = []
    completed_ids = set()
    if os.path.exists("benchmark/results.json"):
        with open("benchmark/results.json") as f:
            existing_results = json.load(f)
            completed_ids = {r["id"] for r in existing_results if "error" not in r}

    questions = BENCHMARK_QUESTIONS
    if category_filter:
        questions = [q for q in questions if q["category"] == category_filter]
    if limit:
        questions = questions[:limit]

    results = list(existing_results)

    for i, q in enumerate(questions):
        if q["id"] in completed_ids:
            print(f"[skip] {q['id']} already completed successfully")
            continue

        print(f"\n[{i+1}/{len(questions)}] {q['id']} ({q['category']}): {q['question']}")
        start = time.time()

        try:
            if q["ground_truth_type"] == "scenario":
                answer, trace = investigate(q["question"], q["scenario_key"])
                verification = next((e["verification"] for e in reversed(trace) if "verification" in e), None)
                grading = {"gradable": True, "correct": bool(verification and verification.get("verified"))}
            else:
                answer, trace = investigate_general(q["question"])
                if q["ground_truth_type"] == "sql":
                    grading = grade_general_question(q, ground_truth[q["id"]], answer.get("answer"))
                else:
                    grading = {"gradable": False, "reason": "behavioral — requires manual review"}

            elapsed = time.time() - start
            results = [r for r in results if r["id"] != q["id"]]
            results.append({
                "id": q["id"], "category": q["category"], "question": q["question"],
                "answer": answer, "num_steps": len(trace),
                "num_queries": sum(1 for e in trace if e.get("tool") == "execute_readonly_sql"),
                "elapsed_seconds": round(elapsed, 2), "grading": grading,
            })
            print(f"  -> {grading}")

        except Exception as e:
            print(f"  -> STOPPING: {e}")
            results = [r for r in results if r["id"] != q["id"]]
            results.append({
                "id": q["id"], "category": q["category"], "question": q["question"],
                "error": str(e), "grading": {"gradable": False, "reason": "crashed"}
            })
            with open("benchmark/results.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Partial results saved. Resume later by re-running this command — completed questions will be skipped.")
            return

    with open("benchmark/results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nDone. {len(results)} total results in benchmark/results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default=None, help="Run only this category (e.g. simple)")
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N questions")
    args = parser.parse_args()
    run(category_filter=args.category, limit=args.limit)