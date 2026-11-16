"""Render backlog.json to backlog.md and backlog.csv (ClickUp import format).

Run from the repository root:  python docs/backlog/render.py
backlog.json is the source; do not edit the two generated files by hand.
"""
import csv
import json
from pathlib import Path

here = Path(__file__).parent
data = json.loads((here / "backlog.json").read_text(encoding="utf-8"))
tasks = data["tasks"]
by_epic = {e["id"]: [t for t in tasks if t["epic"] == e["id"]] for e in data["epics"]}
ids = {t["id"] for t in tasks}
for t in tasks:
    missing = [d for d in t["deps"] if d not in ids]
    assert not missing, f"{t['id']} depends on unknown {missing}"

md = ["# Backlog", "",
      "Generated from `backlog.json` by `render.py`. Order within a phase follows the dependencies, not dates.", "",
      "Owners: " + "; ".join(f"**{k}** = {v}" for k, v in data["owners"].items()) + ".", ""]
for e in data["epics"]:
    md += [f"## {e['id']} {e['name']} (phase {e['phase']})", "", e["goal"], "",
           "| ID | Task | Owner | Depends on | Branch | Owns | Done when |", "|---|---|---|---|---|---|---|"]
    for t in by_epic[e["id"]]:
        md.append(f"| {t['id']} | **{t['title']}.** {t['detail']} | {t['owner']} | {', '.join(t['deps']) or '-'} | `{t['branch']}` | {t['owns']} | {t['done']} |")
    md.append("")
(here / "backlog.md").write_text("\n".join(md), encoding="utf-8")

with (here / "backlog.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Task Name", "List", "Description", "Owner", "Depends On", "Phase", "Status", "Branch", "Owns"])
    epics = {e["id"]: e for e in data["epics"]}
    for t in tasks:
        e = epics[t["epic"]]
        desc = f"{t['detail']}\n\nDone when: {t['done']}\n\nDepends on: {', '.join(t['deps']) or 'nothing'}"
        w.writerow([f"{t['id']} {t['title']}", f"{e['id']} {e['name']}", desc, t["owner"], ", ".join(t["deps"]), e["phase"], "to do", t["branch"], t["owns"]])

print(len(tasks), "tasks in", len(data["epics"]), "epics")
