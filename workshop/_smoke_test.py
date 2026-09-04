"""Smoke-test the notebook's research-tool cells (3a, 3b, 3c) with a MOCK client.

Verifies, without hitting the real API:
  - 3a loads 12 abstracts
  - 3b's extract() handles: clean JSON, ```fenced``` JSON, and prose (-> retry -> PARSE FAILED)
  - the retry-once path actually fires
  - 3c writes a well-formed triage_table.csv with the right columns
"""
import json, types, sys, os
import nbformat

os.chdir('/Users/jgarc111/ai-workshop-api-lesson')
nb = nbformat.read('03_notebook_talking_to_a_model.ipynb', as_version=4)
cells = [c for c in nb.cells if c.cell_type == 'code']
src = [c.source for c in cells]

# Identify the cells by a stable marker in their source
def find(marker):
    for s in src:
        if marker in s:
            return s
    raise SystemExit(f"cell not found: {marker}")

load_cell  = find("ABSTRACTS =")
batch_cell = find("def extract")
csv_cell   = find('triage_table.csv')

# ---- Build a mock client whose .chat.completions.create returns canned text ---
class FakeMsg:
    def __init__(self, content): self.content = content
class FakeChoice:
    def __init__(self, content): self.message = FakeMsg(content)
class FakeUsage:
    total_tokens = 11
class FakeResp:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]
        self.usage = FakeUsage()

class FakeCompletions:
    def __init__(self, script): self.script = script; self.calls = 0
    def create(self, **kw):
        self.calls += 1
        return FakeResp(self.script(self.calls, kw))

# Script by call number:
#  calls 1..10  -> clean JSON
#  call  11     -> fenced JSON (tests fence-stripping)
#  call  12     -> prose that is NOT json (tests retry); call 13 (retry) -> clean JSON
def script(n, kw):
    if n == 11:
        return '```json\n{"summary": "s11", "method": "m11", "result": "r11"}\n```'
    if n == 12:
        return 'Sure! Here is the info you asked for: {"summary":"s12","method":"m12","result":"r12"} hope that helps'
    return json.dumps({"summary": f"sum{n}", "method": f"meth{n}", "result": f"res{n}"})

completions = FakeCompletions(script)
class FakeChat:
    completions = completions
class FakeClient:
    chat = FakeChat()
client = FakeClient()

# ---- Execute the three cells in a shared namespace ---------------------------
ns = {"client": client, "MODEL": "mock-model"}
exec(load_cell, ns)
print("3a: loaded", len(ns["ABSTRACTS"]), "abstracts")
assert len(ns["ABSTRACTS"]) == 12

exec(batch_cell, ns)
print("3b: total model calls =", completions.calls)
rows = ns["rows"]
print("3b: rows =", len(rows))
# Expect: 11 clean/fenced OK + 1 that failed-then-retried OK = 12 ok rows, 0 parse failures
parse_failed = [r for r in rows if r["summary"] == "PARSE FAILED"]
print("3b: PARSE FAILED rows =", len(parse_failed))
# call 12 returned prose -> first attempt JSON fails, retry (call 13) returns clean -> OK
assert completions.calls == 13, f"expected 13 calls (12 + 1 retry), got {completions.calls}"
assert len(rows) == 12
assert all(r["summary"] != "PARSE FAILED" for r in rows), "retry should have recovered row 12"
# verify the fenced row 11 parsed cleanly
r11 = rows[10]
assert r11["summary"] == "s11" and r11["method"] == "m11", f"fenced row wrong: {r11}"
print("3b: fence-stripping + retry both verified OK")

exec(csv_cell, ns)
with open("triage_table.csv") as f:
    head = f.readline().strip()
print("3c: csv header =", head)
assert head == "field,title,arxiv_id,summary,method,result"
import csv as _csv
with open("triage_table.csv") as f:
    n_rows = sum(1 for _ in _csv.reader(f)) - 1
print("3c: data rows in csv =", n_rows)
assert n_rows == 12
print("\nALL SMOKE TESTS PASSED")
