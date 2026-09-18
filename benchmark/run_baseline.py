import sys, os, json, time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from benchmark.questions import BENCHMARK_QUESTIONS
from benchmark.run_benchmark import extract_number, grade_general_question
from app.services.baseline_text_to_sql import answer_question_for_benchmark

CATEGORIES_TO_TEST = ["simple", "aggregation", "joins", "time_comparison", "root_cause"]

def run():
    with open("benchmark/ground_truth.json") as f:
        ground_truth = json.load(f)

    questions = [q for q in BENCHMARK_QUESTIONS if q["category"] in CATEGORIES_TO_TEST]
    results = []

    for i, q in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {q['id']} ({q['category']}): {q['question']}")
        start = time.time()

        result = answer_question_for_benchmark(q["question"])
        elapsed = time.time() - start

        if q["ground_truth_type"] == "sql":
            grading = grade_general_question(q, ground_truth[q["id"]], result.get("answer"))
        else:
            # root_cause questions: baseline has no verification, so we can only
            # do a loose sanity check for whether key ground-truth facts appear
            # anywhere in its answer text.
            gt = ground_truth[q["id"]]["scenario_ground_truth"]["ground_truth"]["root_cause"]
            answer_text = str(result.get("answer") or "").lower()
            key_terms = [str(v).lower() for v in gt.values() if isinstance(v, str)]
            mentioned = sum(1 for term in key_terms if term in answer_text)
            grading = {"gradable": True, "correct": mentioned == len(key_terms),
                       "key_terms": key_terms, "terms_found": mentioned}

        results.append({
            "id": q["id"], "category": q["category"], "question": q["question"],
            "answer": result.get("answer"), "sql": result.get("sql"),
            "error": result.get("error"), "elapsed_seconds": round(elapsed, 2),
            "grading": grading,
        })
        print(f"  -> {grading}")
        if result.get("error"):
            print(f"     (error: {result['error']})")

    with open("benchmark/baseline_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    correct = sum(1 for r in results if r["grading"].get("correct"))
    print(f"\nDone. {correct}/{len(results)} correct. Results in benchmark/baseline_results.json")


if __name__ == "__main__":
    run()