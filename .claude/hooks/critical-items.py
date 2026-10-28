#!/usr/bin/env python3
"""SessionStart hook: show the top critical items to resolve or close.

Reads the seed tasks in index.html (the board only lives in browser memory),
scores them with the same business-impact rules as the board and the PMO Agent,
and prints the top items. Read-only. Prints a message to the user and adds the
same list to Claude's context. Never fails the session: on any error it exits 0.
"""
import datetime
import json
import os
import re
import sys

TOP_N = 3
PRIORITY_WEIGHT = {"Critical": 40, "High": 25, "Medium": 10, "Low": 0}
THRESHOLD = 60


def load_tasks(path):
    src = open(path, encoding="utf-8").read()
    block = src[src.index("function seedTasks"):src.index("seeds.forEach")]
    tasks = []
    for i, obj in enumerate(re.findall(r"\{(.*?)\n    \}", block, re.S), 1):
        t = {k: v for k, v in re.findall(r'(\w+):\s*"((?:[^"\\]|\\.)*)"', obj)}
        t["id"] = "ABC-ITPM-%04d" % i
        tasks.append(t)
    return tasks


def score(t, today):
    if t["status"] == "Done":
        return 0, []
    due = datetime.date.fromisoformat(t["dueDate"])
    late = max(0, (today - due).days)
    s = PRIORITY_WEIGHT.get(t["priority"], 0)
    why = [t["priority"] + " priority"]
    if late > 0:
        s += 25 + min(15, late)
        why.append("overdue %dd" % late)
    if t["status"] == "Blocked":
        s += 15
        why.append("blocked")
    if t["category"] in ("Compliance", "Cybersecurity"):
        s += 10
        why.append(t["category"].lower() + " exposure")
    return s, why


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    today = datetime.date.today()
    tasks = load_tasks(os.path.join(root, "index.html"))
    scored = []
    for t in tasks:
        s, why = score(t, today)
        if t["status"] != "Done" and (t["priority"] == "Critical" or s >= THRESHOLD):
            scored.append((s, t, why))
    scored.sort(key=lambda x: (-x[0], x[1]["dueDate"]))
    top = scored[:TOP_N]
    if not top:
        msg = "No critical items to resolve right now."
    else:
        lines = ["TOP %d CRITICAL ITEMS TO RESOLVE/CLOSE (as of %s, %d critical in total):" % (len(top), today, len(scored))]
        for n, (s, t, why) in enumerate(top, 1):
            lines.append("%d. [!] %s %s | %s | due %s | %s | impact %d (%s)" % (
                n, t["id"], t["title"], t["assignee"], t["dueDate"], t["status"], s, ", ".join(why)))
        lines.append("Source: board seed data; the live board may differ.")
        msg = "\n".join(lines)
    print(json.dumps({
        "systemMessage": msg,
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg},
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a reporting hook must never block a session
        print(json.dumps({"systemMessage": "critical-items hook skipped: %s" % exc}))
    sys.exit(0)
