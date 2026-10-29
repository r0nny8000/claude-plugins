"""Measure whether a plugin skill triggers, one run per prompt.

Usage: python evals/measure_triggers.py <eval-set.json> <model> <out.json> [--skill NAME] [--plugin-dir DIR]

Without the options it measures the installed goal-crafter skill. --plugin-dir
loads an uninstalled plugin for the sessions, e.g. --skill scalable-cli
--plugin-dir plugins/finance.

Why not skill-creator's run_eval: it registers a temporary copy of the skill
and only counts calls to that copy. With the plugin installed, Claude calls the
real skill instead, so run_eval scores every hit as a miss.
"""
import argparse
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument("eval_set")
parser.add_argument("model")
parser.add_argument("out")
parser.add_argument("--skill", default="goal-crafter")
parser.add_argument("--plugin-dir")
args = parser.parse_args()
queries = json.load(open(args.eval_set))
env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
# A claude.ai connector (e.g. Scalable) could answer before any skill loads
# and turn a trigger into a miss, so the sessions run without MCP servers.
env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
command = ["claude", "--strict-mcp-config"]
if args.plugin_dir:
    # The sessions run in a temp dir, so a relative path would not resolve there.
    command += ["--plugin-dir", os.path.abspath(args.plugin_dir)]
workdir = tempfile.mkdtemp(prefix="trigger-real-")


def triggered(query):
    proc = subprocess.Popen(
        command + ["-p", query, "--output-format", "stream-json", "--verbose", "--model", args.model, "--max-turns", "1"],
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
                    # The first tool call decides: a Skill call to the skill is a trigger.
                    hit = item["name"] == "Skill" and args.skill in json.dumps(item.get("input"))
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
summary = {"model": args.model, "skill": args.skill, "total": len(results), "passed": sum(r["pass"] for r in results),
           "should_trigger_hits": sum(r["triggered"] for r in results if r["should_trigger"]),
           "should_trigger_total": sum(r["should_trigger"] for r in results),
           "false_triggers": sum(r["triggered"] for r in results if not r["should_trigger"])}
json.dump({"summary": summary, "results": results}, open(args.out, "w"), indent=2)
print(json.dumps(summary))
