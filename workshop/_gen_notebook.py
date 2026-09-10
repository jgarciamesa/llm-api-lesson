import json, nbformat

with open('data/research_abstracts.json') as f:
    abstracts = json.load(f)

DATA_JSON = json.dumps(abstracts, indent=2)

nb = nbformat.v4.new_notebook()
cells = []

def md(src):
    cells.append(nbformat.v4.new_markdown_cell(src))

def code(src):
    cells.append(nbformat.v4.new_code_cell(src))

# ============================================================ intro
md('''# Talking to a Model with an API

**AI for All Workshop · September 15, 2026 · Beginner Track 2**

## Questions

- What does a program actually send to a language model?
- What does it get back, and how do I read the answer?
- How do I run one question over many pieces of text and save the answers in a file?

## Objectives

After working through this notebook, you will be able to:

- make a request to a language model API with the `openai` Python package
- read each field of an API response
- run a request over a list of texts and save structured results to a CSV file

## The API and the plan

The API is the ASU Research Computing LLM gateway at
`https://openai.rc.asu.edu/v1`. It follows the OpenAI API format, so the standard
`openai` Python package works without changes. The 12 research abstracts used later
are already embedded in this notebook; you do not need to download anything.

Run the cells in order, top to bottom:

1. Set your key
2. Make a first call
3. Read the response
4. Build a research tool (12 abstracts to a CSV file)
5. Experiments (15 minutes)''')

# ============================================================ 1 key
md('''## 1 - Set your key

Run this cell. It reads your key from the environment so the key never appears in
your code or in the notebook file.

> **Note.** `echo $OPENAI_API_KEY` in your terminal may print your key, yet this cell
> may say the key is not set. This is not an error. A notebook kernel is a separate
> process from your terminal, and it only saw the environment when it started. The
> cell below explains the two ways to fix it.

Treat your key like a password. Do not share it and do not commit it to Git.''')

code(r'''import os

key = os.environ.get("OPENAI_API_KEY")
base = os.environ.get("OPENAI_BASE_URL", "https://openai.rc.asu.edu/v1")

if not key:
    raise SystemExit(
        "OPENAI_API_KEY is not set in this kernel.\n"
        "\n"
        "Why this happens: a notebook kernel is a separate process from your\n"
        "terminal. It only saw the environment when it started, so a key you\n"
        "exported in the terminal after starting the kernel is not visible here.\n"
        "Running this cell again will not help.\n"
        "\n"
        "Two fixes:\n"
        "\n"
        "  Fix 1 (fastest): run the next cell. It asks for your key with\n"
        "  getpass, so it stays hidden, and it sets the key for this kernel.\n"
        "  Then run this cell again.\n"
        "\n"
        "  Fix 2: in a terminal, run\n"
        "      read -rs OPENAI_API_KEY        # paste your key, press Enter\n"
        "      export OPENAI_API_KEY\n"
        "      export OPENAI_BASE_URL=https://openai.rc.asu.edu/v1\n"
        "  On Windows (PowerShell): $env:OPENAI_API_KEY = 'your-key'\n"
        "  Then choose Restart Kernel from the Kernel menu, and run this cell again.\n"
    )

# Show that the key is present without revealing it.
print(f"key set:   {key[:4]}...{key[-4:]}  ({len(key)} chars)")
print(f"base url:  {base}")
assert base.rstrip('/').endswith('/v1'), "BASE_URL should end with /v1"
print("\nReady. Run the next cell to make your first call.")''')

code(r'''# Run this cell only if the cell above said the key is not set in the kernel.
# getpass hides your input, and the key is never saved in the notebook file.
# (Pasting a key into a code cell would save it in the .ipynb.)
import os
from getpass import getpass

key = getpass("Paste your API key, then press Enter: ").strip()
if not key:
    raise SystemExit("No key entered. Run this cell again.")

os.environ["OPENAI_API_KEY"] = key
os.environ["OPENAI_BASE_URL"] = "https://openai.rc.asu.edu/v1"
del key   # it now lives only in this kernel's environment

print(f"key set in this kernel: {os.environ['OPENAI_API_KEY'][:4]}...{os.environ['OPENAI_API_KEY'][-4:]}")
print("Now run the 'Set your key' cell above again.")''')

# ============================================================ 2 first call
md('''## 2 - First call

This is the moment of truth. Before you run it, look at what the request actually is,
because the response (next section) has the same shape of JSON.

The request body sent to `POST /v1/chat/completions` is a JSON document:

```json
{
  "model": "llama3.1",
  "messages": [
    { "role": "system", "content": "You are a research literature assistant." },
    { "role": "user", "content": "Explain what an API is, in one sentence." }
  ],
  "temperature": 0
}
```

| Field | What it is |
|---|---|
| `model` | Which model should answer. Use an exact name from the models list. |
| `messages` | The conversation, as a list. Each entry has a `role` and a `content`. |
| `messages[i].role` | Who is speaking: `system` (standing instructions), `user` (you), or `assistant` (the model). |
| `messages[i].content` | The text of that turn. |
| `temperature` | Optional. How much the model varies its wording. `0` is the most consistent; higher is more varied. |

The SDK sends this document for you and also adds the `Authorization` and
`Content-Type` headers (you will see both in a raw `curl` during the session).

The next cell picks a model from your key's live models list, so you do not need to
know the exact name. If it cannot decide, it prints the list; copy any ID into
`MODEL` and run the cell again.''')

code(r'''from openai import OpenAI

client = OpenAI()   # reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment

# Pick a model from the live list for your key.
PREFERRED = ["llama3.3", "llama3.1", "llama3", "gpt-4o", "gpt-4.1", "mistral-large"]
try:
    available = [m.id for m in client.models.list()]
except Exception as e:
    available = []
    print(f"Could not list models: {e}")

MODEL = None
for cand in PREFERRED:
    for a in available:
        if cand in a:
            MODEL = a
            break
    if MODEL:
        break
if MODEL is None and available:
    MODEL = available[0]   # fall back to the first model your key can see

if not MODEL:
    raise SystemExit(
        "No model could be selected. If a list printed above, choose one\n"
        "manually, for example:\n"
        "    MODEL = 'llama3.1'\n"
        "and run this cell again."
    )
print(f"Using model: {MODEL}")
if available:
    print(f"Your key can use {len(available)} model(s). You will try others in the experiments:")
    for a in available[:8]:
        print(f"   - {a}")

# The first request.
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain what an API is, in one sentence."}],
)
print("\n--- MODEL SAYS ---")
print(resp.choices[0].message.content)
print(f"\nTokens used: {resp.usage.total_tokens if resp.usage else 'n/a'}")''')

# ============================================================ 3 anatomy of the response
md('''## 3 - Read the response

The request was JSON. The response is JSON too. The SDK handed you a Python object
that wraps the response document; the next cell converts it back to plain JSON so
you can see exactly what the server sent.

Here is a typical response, with the same fields you will see in your own:

```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1757830800,
  "model": "llama3.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "An API is a set of rules that lets one program ask another program to do something."
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 16,
    "total_tokens": 34
  }
}
```

| Field | What it is |
|---|---|
| `id` | A unique identifier for this completion. Quote it if you report a problem. |
| `object` | Always `chat.completion` for this endpoint. |
| `created` | Unix timestamp for when the response was made. |
| `model` | The model that actually answered. This can differ from the name you requested if the gateway resolves an alias. |
| `choices` | A list of candidate answers. A normal request returns one, at index 0. |
| `choices[0].message` | The answer: `role` is `assistant` and `content` is the text you want. |
| `choices[0].finish_reason` | Why the model stopped: `stop` (finished on its own), `length` (ran out of room; the text is cut off), or `tool_calls` / `content_filter`. |
| `choices[0].logprobs` | Token probabilities. `null` unless you ask for them. |
| `usage.prompt_tokens` | Number of tokens in your request. |
| `usage.completion_tokens` | Number of tokens in the answer. |
| `usage.total_tokens` | The sum. This is what you are billed on. |

Three fields matter most for research work:

1. `choices[0].message.content` — the answer itself.
2. `choices[0].finish_reason` — if this is `length`, the answer was cut off and you should raise `max_tokens` or shorten the prompt.
3. `usage.total_tokens` — the cost of the call, which is how you budget a batch job.

> **Note.** Some gateways add extra fields (for example `system_fingerprint`) and some
> omit optional ones. The fields above are the ones defined by the OpenAI-compatible
> format and the ones you will use.''')

code('''# The SDK returned a Python object. model_dump() converts it into the plain
# dictionary that matches the JSON document on the wire.
import json

print(json.dumps(resp.model_dump(), indent=2))''')

code(r'''# The three fields you will use most often.
answer = resp.choices[0].message.content
reason = resp.choices[0].finish_reason
tokens = resp.usage.total_tokens

print("answer:  ", answer[:100])
print("stopped: ", reason)
print("tokens:  ", tokens)

# "stop" means the model finished on its own.
# "length" means the answer was cut off at max_tokens.''')

# ============================================================ 4 research tool
md('''## 4 - Build the research tool

Researchers rarely want a chat box. They want to run the same question over a list of
things and get a table back. That is what this section builds.

The approach is a list of inputs, one model call for each input, structured JSON
output for each answer, and the results saved to a file.

We will use the 12 real arXiv abstracts embedded in section 4a. A *system prompt*
tells the model to answer in strict JSON with the keys `summary`, `method`, and
`result`. That is **structured output**: you control the shape of the answer, not just
the words, so the result is rows you can put in a spreadsheet instead of paragraphs
you have to read.

Run the cells in order: load the data (4a), run the batch (4b), save and inspect (4c).''')

md("### 4a - Load the 12 abstracts (already embedded)")

code('''import json

ABSTRACTS = __DATA_JSON__

print(f"Loaded {len(ABSTRACTS)} abstracts:")
for i, a in enumerate(ABSTRACTS, 1):
    print(f"  {i:2d}. [{a['field']}] {a['title'][:70]}")'''.replace("__DATA_JSON__", DATA_JSON))

md('''### 4b - Run the batch (one API call per abstract)

This is the loop you will reuse on your own data. It prints progress as it goes.
Twelve calls usually take 30 to 90 seconds, depending on the model. If a response is
not clean JSON, the cell tries once more. Some models wrap the JSON in code fences
(```json ... ```), so the cell removes those too.''')

code(r'''import json, time

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
    # One model call for one abstract, returning a dict (or a PARSE FAILED marker).
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
        # Remove a ```json ... ``` fence if the model added one.
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

print(f"\nDone. {len(rows)} rows, {failures} parse failure(s).")''')

md("### 4c - Save and inspect the CSV")

code(r'''import csv

out = "triage_table.csv"
fields = ["field", "title", "arxiv_id", "summary", "method", "result"]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}\n")

# Show a readable slice.
for r in rows[:4]:
    print(f"[{r['field']}] {r['title'][:55]}")
    print(f"   summary: {r['summary'][:100]}")
    print(f"   method:  {r['method'][:80]}")
    print()''')

# ============================================================ 5 experiments
md('''## 5 - Experiments (your 15 minutes)

Run whichever experiments fit your research. Each one changes exactly one thing, so
you can see what that thing does.

> **Note.** Before Experiment 4, read the data rules: do not send data your
> institution would call sensitive or proprietary, and never send regulated data
> (health records, export-controlled work, SSNs, personal identifiers). If you are
> unsure, ask your institution first.''')

md("### Experiment 1 - Change the prompt (same abstract, three asks)")

code(r'''rec = ABSTRACTS[0]   # pick any index 0..11

asks = [
    "Summarize this abstract in one sentence.",
    "Summarize this abstract in one sentence, then list up to 3 limitations the authors mention or that are implied.",
    "Explain the core idea of this abstract to a first-year PhD student in a different field. Keep it under 80 words.",
]
for i, ask in enumerate(asks, 1):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": f"{ask}\n\nAbstract: {rec['abstract']}"},
        ],
    )
    print(f"--- Ask {i}: {ask[:60]}...")
    print(resp.choices[0].message.content.strip()[:300])
    print()''')

md('''### Experiment 2 - Change the model (same request, two models)

Set `B` to a second model ID from the list printed in section 2. Leave `A` as the
current model. Compare the style, length, and accuracy of the two answers.''')

code(r'''A = MODEL
B = None   # set this to another model ID, for example B = 'gpt-4o' (must be in your list)

if not B:
    raise SystemExit("Set B = 'some-model-id' (from the list in Section 2) and re-run.")

prompt = ("In under 60 words, what is the main method and the key result of this "
          f"abstract?\n\nAbstract: {ABSTRACTS[1]['abstract']}")

for label, m in (("Model A", A), ("Model B", B)):
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        print(f"=== {label} ({m}) ===")
        print(resp.choices[0].message.content.strip())
        print()
    except Exception as e:
        print(f"=== {label} ({m}) === FAILED: {e}\n")''')

md("### Experiment 3 - Tighten the structure (add fields to the schema)")

code(r'''SYSTEM2 = (
    "Respond with ONLY a valid JSON object (no other text) with exactly these keys: "
    '{"summary": "<one sentence>", '
    '"method": "<main method, short>", '
    '"result": "<key result, short>", '
    '"reproducible": "yes | no | maybe", '
    '"confidence": "high | medium | low"}. '
    "Use 'not stated' where the abstract gives no information. Return ONLY the JSON."
)

for rec in ABSTRACTS[:3]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM2},
            {"role": "user", "content": f"Title: {rec['title']}\nAbstract: {rec['abstract']}"},
        ],
        temperature=0,
    )
    print(rec["title"][:60])
    print(resp.choices[0].message.content.strip())
    print()''')

md('''### Experiment 4 - Your own data

Paste 3 to 5 short paragraphs from your own work into `MY_TEXTS` below and run the
same batch loop. Only send data that is fine to send (see the note at the start
of section 5).

**Challenge.** Add your own key to the JSON schema in `SYSTEM_PROMPT` and watch the
model fill it.''')

code(r'''MY_TEXTS = [
    "Paste paragraph 1 here",
    "Paste paragraph 2 here",
    "Paste paragraph 3 here",
]

if all(t.startswith("Paste") for t in MY_TEXTS):
    raise SystemExit("Replace the MY_TEXTS list with your own text, then re-run.")

for i, text in enumerate(MY_TEXTS, 1):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Text: {text}"},
        ],
        temperature=0,
    )
    print(f"--- Text {i} ---")
    print(resp.choices[0].message.content.strip())
    print()''')

# ============================================================ next steps + key points
md('''## Where to go next (the same API, deeper)

- **Streaming:** `client.chat.completions.create(..., stream=True)` sends the answer
  as it is generated, so you can watch it arrive.
- **Function and tool calling:** let the model call your own Python functions.
- **RAG (retrieval-augmented generation):** ground answers in your own documents.
  Purdue's AnvilGPT does this out of the box.
- **Tools that use the same key and endpoint** (the format is OpenAI-compatible, so
  they work without changes):
  - **OpenCode** — a terminal and desktop assistant. ASU Research Computing has a
    setup guide, and Voyager generates the provider config for you.
  - **VS Code** — Chat, Manage Language Models, Add Models, Custom Endpoint: paste
    `https://openai.rc.asu.edu/v1` and your key.
  - **Jupyter AI** — the `%ai` magic inside notebooks.
- **Reference:** the ASU Research Computing API documentation is at
  <https://docs.rc.asu.edu/ai/api>. Purdue's AnvilGPT is at
  <https://anvilgpt.rcac.purdue.edu>.''')

md('''## Key points

- A request to a language model API is a JSON document: a model name, a list of
  messages with roles and content, and optional settings such as `temperature`.
- A response is also JSON. The answer is at `choices[0].message.content`.
- Check `choices[0].finish_reason` before you trust an answer. `length` means the
  answer was cut off.
- `usage` counts the tokens in the request and the answer. That count is what you
  are billed on and how you budget a batch job.
- The batch loop works on any list of texts: one request per input, structured
  JSON output, and the results saved to a file.''')

nb.cells = cells
nbformat.validate(nb)
path = '03_notebook_talking_to_a_model.ipynb'
with open(path, 'w') as f:
    json.dump(nb, f, indent=1)
print("wrote", path, f"({len(cells)} cells)")

# ---- self-check: every code cell must parse ---------------------------------
import ast
for i, c in enumerate(nb.cells):
    if c.cell_type == 'code':
        ast.parse(c.source)
print("all code cells parse cleanly")
