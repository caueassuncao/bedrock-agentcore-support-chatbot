"""
Read and summarize the Bedrock evaluation results.
Run from the `starter` folder:  python read_results.py
"""
import json
import glob
import os

# --- locate the output file (no need to type the long path) ---
matches = glob.glob(os.path.join("eval-results", "**", "*_output.jsonl"), recursive=True)
if not matches:
    raise SystemExit("Could not find *_output.jsonl under eval-results/. "
                     "Run this from the 'starter' folder.")
path = matches[0]
print(f"Reading: {path}\n")

# --- load records ---
records = []
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))


def get_prompt(rec):
    """Best-effort extraction of the input prompt text."""
    turns = rec.get("conversationTurns")
    if isinstance(turns, list) and turns:
        turn = turns[0]
        # common shapes: turn['prompt']['content'][0]['text'] or turn['inputRecord']...
        try:
            return turn["prompt"]["content"][0]["text"]
        except Exception:
            pass
        try:
            return turn["inputRecord"]["prompt"]["content"][0]["text"]
        except Exception:
            pass
    if "prompt" in rec:
        return str(rec["prompt"])
    return "(prompt text not found)"


rows = []
for i, rec in enumerate(records, 1):
    score_obj = rec["automatedEvaluationResult"]["scores"][0]
    score = score_obj.get("result", score_obj.get("value"))
    explanation = ""
    details = score_obj.get("evaluatorDetails", [])
    if details:
        explanation = details[0].get("explanation", "")
    rows.append((i, score, get_prompt(rec), explanation))

# --- per-record detail ---
print("=" * 100)
for i, score, prompt, explanation in rows:
    flag = "PASS" if isinstance(score, (int, float)) and score >= 0.5 else "FAIL"
    print(f"\n[{i:2}] score={score}  {flag}")
    print(f"     prompt: {prompt[:140]}")
    if explanation:
        print(f"     judge : {explanation[:500]}")

# --- summary ---
nums = [s for _, s, _, _ in rows if isinstance(s, (int, float))]
passed = sum(1 for s in nums if s >= 0.5)
failed = sum(1 for s in nums if s == 0.0)
partial = sum(1 for s in nums if 0.0 < s < 1.0)

print("\n" + "=" * 100)
print("SUMMARY")
print(f"  Records scored : {len(nums)}")
print(f"  Average        : {sum(nums)/len(nums):.3f}" if nums else "  Average: n/a")
print(f"  Passed (>=0.5) : {passed}")
print(f"  Partial (0<x<1): {partial}")
print(f"  Failed (0.0)   : {failed}")
print("\n  Failing record numbers:",
      [i for i, s, _, _ in rows if isinstance(s, (int, float)) and s < 0.5])