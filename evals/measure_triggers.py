"""Measure whether the installed goal-definer plugin skill triggers, one run per prompt.

Usage: python evals/measure_triggers.py <eval-set.json> <model> <out.json>

Why not skill-creator's run_eval: it registers a temporary copy of the skill
and only counts calls to that copy. With the plugin installed, Claude calls the
real skill instead, so run_eval scores every hit as a miss.
"""
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

eval_set, model, out = sys.argv[1], sys.argv[2], sys.argv[3]
queries = json.load(open(eval_set))
env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
workdir = tempfile.mkdtemp(prefix="trigger-real-")


def triggered(query):
    proc = subprocess.Popen(
        ["claude", "-p", query, "--output-format", "stream-json", "--verbose", "--model", model, "--max-turns", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True, cwd=workdir, env=env,
    )
    hit = None
    try:
        for line in proc.stdout:
            event = json.loads(line)
            message = event.get("message")
            if event.get("type") != "assistant" or not isinstance(message, dict):
                continue
            for item in message.get("content") or []:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    # The first tool call decides: a Skill call to goal-definer is a trigger.
                    hit = item["name"] == "Skill" and "goal-definer" in json.dumps(item.get("input"))
                    break
            if hit is not None:
                break
    finally:
        proc.kill()
        proc.wait()
    return bool(hit)


with ThreadPoolExecutor(max_workers=4) as pool:
    hits = list(pool.map(lambda q: triggered(q["query"]), queries))

results = [{"query": q["query"], "should_trigger": q["should_trigger"], "triggered": h,
            "pass": h == q["should_trigger"]} for q, h in zip(queries, hits)]
summary = {"model": model, "total": len(results), "passed": sum(r["pass"] for r in results),
           "should_trigger_hits": sum(r["triggered"] for r in results if r["should_trigger"]),
           "should_trigger_total": sum(r["should_trigger"] for r in results),
           "false_triggers": sum(r["triggered"] for r in results if not r["should_trigger"])}
json.dump({"summary": summary, "results": results}, open(out, "w"), indent=2)
print(json.dumps(summary))
