---
title: "Experiments & Tools Around the API"
teaching: 23
exercises: 15
---

:::::::::::::::::::::::::::::::::::::: questions

- What actually changes the model's answer — the prompt, or the model?
- How do I try my own data with the same batch loop?
- What other tools can I point at the same key and endpoint?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Systematically vary one variable at a time (prompt or model).
- Extend the JSON schema with new fields.
- Batch-process your own (non-sensitive) data.
- Name the researcher-facing tools that reuse the same OpenAI-compatible API.

::::::::::::::::::::::::::::::::::::::::::::::::

## Guided experiment time (15 minutes)

Pick whichever cells fit your own research. Each one changes **exactly one
variable** — that's how you learn what actually matters.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor
15 min, the highest-value overflow. TA role: help anyone whose JSON isn't
parsing or whose key is 401, but *nudge toward the "why", don't write it for
them.* Highest-yield questions: "What does the error actually say?" · "Where in
the JSON is the text you want?" · "If the structured output won't parse, what
did the model *actually* return?"
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

**Before Experiment 4:** do not send sensitive/regulated data — no health
records, no export-controlled work, no SSNs, no personal identifiers. If unsure,
ask your institution first.

### Experiment 1 — Vary the prompt (same abstract, 3 asks)

```python
rec = ABSTRACTS[0]   # pick any index 0..11

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
    print()
```

### Experiment 2 — Vary the model (same request, 2 models)

Set `B` to a second model ID from the list printed in the first-call episode.
Watch style, length, and what each gets right or wrong.

```python
A = MODEL
B = None   # <-- set me to another model ID, e.g. B = 'gpt-4o' (must be in your list)

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
        print(f"=== {label} ({m}) === FAILED: {e}\n")
```

### Experiment 3 — Tighten the structure (add a field to the schema)

Add `reproducible` and `confidence` keys and watch the model fill them:

```python
SYSTEM2 = (
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
    print()
```

### Experiment 4 — Your own data

Paste 3–5 short paragraphs from your own work into `MY_TEXTS` and run the same batch loop. *(Only send data that is fine to send.)*

```python
MY_TEXTS = [
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
    print()
```

## Tools around the API (10 minutes)

Because the API is **OpenAI-compatible**, a set of ready-made tools works with
the **same key and the same endpoint**. A quick tour:

- **OpenCode** — a terminal/desktop coding assistant. ASU RC has a setup guide,
  and Voyager even generates the provider config for you.
- **VS Code** — *Chat → Manage Language Models → Add Models → Custom Endpoint*;
  paste [`https://openai.rc.asu.edu/v1`][rc-gateway] + your key.
- **Jupyter AI** — the `%ai` magic, right inside your notebooks, same gateway.
- **AnvilGPT (Purdue)** — [anvilgpt.rcac.purdue.edu][anvilgpt], a separate
  service with its own access request, but the mental model is identical (it's
  RAG over a vector DB).

**Pick the shape that fits the task:** raw script → the API directly; coding →
OpenCode/VS Code; notebook work → Jupyter AI.

## Where to go next (same API, deeper)

- **Streaming** — `client.chat.completions.create(..., stream=True)`; watch tokens arrive.
- **Function / tool calling** — let the model call *your* Python functions.
- **RAG** — ground answers in your documents; that is the next episode
  (and what AnvilGPT does out of the box).
- **Canonical docs:** [docs.rc.asu.edu/ai/api][rc-api-docs].

::::::::::::::::::::::::::::::::::::: callout
### Data governance — read before you paste

Do **not** send data your institution would call sensitive or proprietary.
Never send regulated data (HIPAA records, export-controlled work, SSNs,
biometrics, personal identifiers). The gateway is a convenience, **not** a
secure enclave.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- Change **one variable at a time** — prompt or model — and compare the outputs.
- You can add fields to the JSON schema and the model will fill them.
- The same loop runs on your own (non-sensitive) data.
- OpenAI-compatible means OpenCode, VS Code, Jupyter AI, and AnvilGPT all reuse the same key + endpoint.

::::::::::::::::::::::::::::::::::::::::::::::::
