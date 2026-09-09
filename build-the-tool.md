---
title: "Building the Research Tool"
teaching: 12
exercises: 2
---

:::::::::::::::::::::::::::::::::::::: questions

- How do I run the *same* structured question over a *list* of texts and get a table back?
- What is "structured output", and why does it make an LLM useful for research?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Batch-process a list of abstracts with one model call each.
- Use a `system` prompt to force strict JSON output.
- Write the structured rows to a CSV file.

::::::::::::::::::::::::::::::::::::::::::::::::

The goal for research is to run the *same* question over a *list* of things and
get a *table* back. Here: 12 paper abstracts in, one row each out — a one-line
summary, the main method, and the key result, in a spreadsheet. That's **batch
API calls + structured output**.

The trick is the **system prompt**: it tells the model to answer in *strict
JSON* with keys `summary`, `method`, `result`. That's **structured output** —
you control the *shape* of the answer, so the result comes back as clean columns
you can drop straight into a spreadsheet.

Run the three cells in order: load (3a) → batch (3b) → save (3c).

### 3a — Load the 12 abstracts (already in the notebook)

The 12 real arXiv abstracts (2 per field, 6 fields) are **already in the
notebook** and load directly from the cell. The first entry looks like this;
all 12 live in the notebook and in
[`data/research_abstracts.json`](data/research_abstracts.json):

```python
import json

ABSTRACTS = [
{
  "field": "Machine Learning (CS)",
  "title": "Learning Active Subspaces and Discovering Important Features with Gaussian Radial Basis Functions Neural Networks",
  "abstract": "Providing a model that achieves a strong predictive performance and is simultaneously interpretable by humans is one of the most difficult challenges in machine learning research due to the conflicting nature of these two objectives. To address this challenge, we propose a modification of the radial basis function neural network model by equipping its Gaussian kernel with a learnable precision matrix. We show that precious information is contained in the spectrum of the precision matrix that can be extracted once the training of the model is completed. In particular, the eigenvectors explain the directions of maximum sensitivity of the model revealing the active subspace and suggesting potential applications for supervised dimensionality reduction. At the same time, the eigenvectors highlight the relationship in terms of absolute variation between the input and the latent variables, thereby allowing us to extract a ranking of the input variables based on their importance to the prediction task enhancing the model interpretability. We conducted numerical experiments for regression, classification, and feature selection tasks, comparing our model against popular machine learning models, the state-of-the-art deep learning-based embedding feature selection techniques, and a transformer model for tabular data. Our results demonstrate that the proposed model does not only yield an attractive prediction performance compared to the competitors but also provides meaningful and interpretable results that potentially could assist the decision-making process in real-world applications. A PyTorch implementation of the model is available on GitHub at the following link. https://github.com/dannyzx/Gaussian-RBFNN",
  "id": "2307.05639v2"
},
  # ... 11 more abstracts (2 per field, 6 fields) ...
  # all embedded in this notebook
]

print(f"Loaded {len(ABSTRACTS)} abstracts:")
for i, a in enumerate(ABSTRACTS, 1):
    print(f"  {i:2d}. [{a['field']}] {a['title'][:70]}")
```

### 3b — Run the batch (one API call per abstract → structured rows)

This is the loop you'll reuse on your own data. It prints progress as it goes
(12 calls, usually 30–90 s), **retries once** if a response isn't clean JSON,
and is defensive about the common case where a model wraps the JSON in code
fences.

```python
import json, time

SYSTEM_PROMPT = (
    "You are a research literature assistant. Read the abstract and respond with "
    "ONLY a valid JSON object (no markdown, no commentary) with exactly these keys: "
    '{"summary": "<one-sentence summary>", '
    '"method": "<the main method or approach, one short phrase>", '
    '"result": "<the key result or contribution, one short phrase>"}. '
    'If a detail is not stated in the abstract, set it to "not stated". '
    "Return ONLY the JSON object."
)

def extract(record):
    # One model call for one abstract -> dict (or a PARSE-FAILED marker).
    user = (f"Field: {record['field']}\nTitle: {record['title']}\n"
            f"Abstract: {record['abstract']}")
    for attempt in range(2):   # one retry if the JSON is malformed
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        text = resp.choices[0].message.content.strip()
        # Strip any ```json ... ``` fence some models add around the object
        t = text
        if t.startswith("```"):
            t = t.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return {"summary": "PARSE FAILED", "method": text[:80], "result": ""}

rows, failures = [], 0
for i, rec in enumerate(ABSTRACTS, 1):
    row = extract(rec)
    ok = bool(row) and row.get("summary") != "PARSE FAILED"
    if not ok:
        failures += 1
        rows.append({"field": rec["field"], "title": rec["title"], "arxiv_id": rec["id"],
                     "summary": "PARSE FAILED", "method": "", "result": ""})
        print(f"  {i:2d}/{len(ABSTRACTS)}  {rec['field']:<22} -> PARSE FAILED (kept raw snippet)")
    else:
        rows.append({"field": rec["field"], "title": rec["title"], "arxiv_id": rec["id"],
                     **{k: row.get(k, "not stated") for k in ("summary", "method", "result")}})
        print(f"  {i:2d}/{len(ABSTRACTS)}  {rec['field']:<22} -> ok")

print(f"\nDone. {len(rows)} rows, {failures} parse failure(s).")
```

### 3c — Save & inspect the CSV

The rows go straight into `triage_table.csv` — one row per paper, ready for a
spreadsheet. `csv.DictWriter` quotes fields properly, so commas inside a summary
won't shift your columns.

```python
import csv

out = "triage_table.csv"
fields = ["field", "title", "arxiv_id", "summary", "method", "result"]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}\n")

# Show a readable slice
for r in rows[:4]:
    print(f"[{r['field']}] {r['title'][:55]}")
    print(f"   summary: {r['summary'][:100]}")
    print(f"   method:  {r['method'][:80]}")
    print()
```

::::::::::::::::::::::::::::::::::::: callout
### The loop generalizes

The same batch call works on grant proposals, lab notes, instrument logs —
anything you can turn into a list of texts.
::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor
12 min. The money segment — slow down on "structured output": *you control the
shape, not just the words.* If the 12-call batch runs long (>2 min), note it;
you can trim experiments or raise the buffer (pre-session checklist Step 4).
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- **Structured output** = a `system` prompt that forces a strict JSON *shape* (keys you define).
- Be defensive: strip code fences, retry once on a bad parse, keep a `PARSE FAILED` marker.
- `csv.DictWriter` writes clean, quote-safe CSV.

::::::::::::::::::::::::::::::::::::::::::::::::
