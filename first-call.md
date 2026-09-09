---
title: "Your First Call"
teaching: 16
exercises: 3
---

:::::::::::::::::::::::::::::::::::::: questions

- How do I set my key without pasting it into my code?
- How do I make the very first call and know it worked?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Set your API key from the environment (never hardcode it).
- Make a first call with the `openai` Python SDK.
- Read the model's reply out of the response.

::::::::::::::::::::::::::::::::::::::::::::::::

## Set your key (don't hardcode it)

Your key is a secret. Treat it like a password: **don't share it, don't commit
it to Git.** The notebook reads it from the environment so it never sits in your
code.

In the shell first (the [Setup page](../learners/setup.md) has all three OS variants):

```bash
# macOS / Linux
read -rs OPENAI_API_KEY        # paste your key, press Enter (nothing prints)
export OPENAI_API_KEY
export OPENAI_BASE_URL="https://openai.rc.asu.edu/v1"
```

Why `read -rs`? A normal prompt writes the key to your shell history in plain
text. `-s` silences the echo. Then, in the notebook, run the **"Set your key"**
cell — it verifies the key is present (masked) and that the base URL ends in
`/v1`:

```python
import os

key = os.environ.get("OPENAI_API_KEY")
base = os.environ.get("OPENAI_BASE_URL", "https://openai.rc.asu.edu/v1")

if not key:
    raise SystemExit(
        "OPENAI_API_KEY is not set. Set it first, then re-run this cell.\n"
        "\n"
        "  macOS / Linux      ->  read -rs OPENAI_API_KEY   (paste key, Enter)\n"
        "                         export OPENAI_API_KEY\n"
        "                         export OPENAI_BASE_URL=https://openai.rc.asu.edu/v1\n"
        "  Windows (PowerShell) ->  $env:OPENAI_API_KEY = 'paste-key-here'\n"
        "                         $env:OPENAI_BASE_URL = 'https://openai.rc.asu.edu/v1'\n"
        "\n"
        "Then re-run THIS cell."
    )

# Mask the key so we can show it is present without revealing it
print(f"key set:   {key[:4]}...{key[-4:]}  ({len(key)} chars)")
print(f"base url:  {base}")
assert base.rstrip('/').endswith('/v1'), "BASE_URL should end with /v1"
print("\nReady. Run the next cell for your first call.")
```

## The first call — *checkpoint: everyone gets a response*

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor
This is the non-negotiable checkpoint. Have the whole room run this ONE cell
together before anyone drifts off. Use the TA to sweep the room: if a chunk can't
get a response, that's the egress problem — go to the instructor guide §8
immediately, don't let it simmer.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

This cell picks a model from your key's live list automatically, so you can run
the first call right away. If it can't decide, it prints the list — copy any ID
into `MODEL` and re-run.

```python
from openai import OpenAI

client = OpenAI()   # reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment

# --- Pick a model from the live list -----------------------------------------
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
    MODEL = available[0]   # fall back to the first model the key can see

if not MODEL:
    raise SystemExit(
        "No model could be selected. If any printed above, set one manually, e.g.\n"
        "    MODEL = 'llama3.1'\n"
        "then re-run."
    )
print(f"Using model: {MODEL}")
if available:
    print(f"Your key can use {len(available)} model(s). Try others in the experiments:")
    for a in available[:8]:
        print(f"   - {a}")

# --- The first request --------------------------------------------------------
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain what an API is, in one sentence."}],
)
print("\n--- MODEL SAYS ---")
print(resp.choices[0].message.content)
print(f"\n(tokens used: {resp.usage.total_tokens if resp.usage else '?'})")
```

You should see a sentence back from the model. **If you see text — you're in.**

## Anatomy of a response

Every reply comes back as a JSON object with the same shape. Here is a typical
one, with each field explained:

```json
{
  "id": "chatcmpl-2d4be949-...",            // 1 — unique ID for this
                                            //    response; send it to support
                                            //    when reporting a problem
  "object": "chat.completion",              // 2 — the kind of object this
                                            //    is (almost always this value
                                            //    for chat completions)
  "created": 1757984284,                    // 3 — Unix timestamp (seconds since
                                            //    1970) of when the response
                                            //    was created
  "model": "llama3.1",                      // 4 — the model that actually
                                            //    handled the request (can
                                            //    differ from what you asked
                                            //    for, if the gateway routed
                                            //    it elsewhere)
  "choices": [                              // 5 — the answer(s). A list
    {                                       //    because n > 1 can request
      "index": 0,                           //    several alternatives; 0
                                            //    for the first one
      "message": {                          //    the model's reply lives
        "role": "assistant",                //    inside "message"
        "content": "This study proposes..."//    the text you wanted
      },
      "finish_reason": "stop",              // 6 — why generation stopped:
                                            //    "stop" = model finished
                                            //    naturally, "length" = hit
                                            //    max_tokens, "content_filter"
                                            //    = safety filter tripped
      "logprobs": null                      //    per-token probabilities;
                                            //    null unless requested
    }
  ],
  "usage": {                                // 7 — what this call consumed
    "prompt_tokens": 12,                    //    tokens in your messages
    "completion_tokens": 87,                //    tokens in the reply
    "total_tokens": 99                      //    sum; billing is based on
                                            //    this
  }
}
```

Three of these matter most for the rest of the lesson:

1. **`choices[0].message.content`** — the actual text. This is the field every
   call in the rest of the lesson reads.
2. **`choices[0].finish_reason`** — if it says `"length"`, your reply was cut
   off at `max_tokens`; raise the limit and try again.
3. **`usage.total_tokens`** — the cost meter. The first cell above prints it
   (`resp.usage.total_tokens`); when you write your own batch tool, summing it
   per call tells you what a whole run cost.

::::::::::::::::::::::::::::::::::: callout
### How does `resp` relate to this JSON?

The Python client unpacks the JSON into attributes: `resp.choices[0].message.content`
is the `choices[0].message.content` above, and `resp.usage` gives you the token
counts. Knowing the raw shape matters when you read documentation (which
describes the JSON, not the Python) or when you move to a language without a
client library.
::::::::::::::::::::::::::::::::::::::::::::::::

### Two ideas to hold onto

- **`messages`** is a list of `{role, content}` (recap the `role` field from
  the introduction).
- The answer lives at **`resp.choices[0].message.content`** — field 5 in the
  anatomy above.

You can list the models your key can use — you'll use this again in the
experiments:

```python
print([m.id for m in client.models.list()])
```

::::::::::::::::::::::::::::::::::::: callout
### Stuck? Read the error verbatim

- `401` / "No api key" → the key isn't set **in this kernel's** environment.
  Re-run the key cell; if you exported it in a terminal, **restart the kernel**
  first (a kernel only sees env vars set before it started).
- `404` / "Model Not Found" → bad model name. List models and copy an exact ID.
- `429` → rate limit. Wait a few seconds and retry.
- Connection/timeout/SSL → possible **egress** problem. See the [Reference
  page](../learners/reference.md) or raise a hand.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- Set the key from the environment (`OPENAI_API_KEY` + `OPENAI_BASE_URL`), never hardcoded.
- `client = OpenAI()` reads both from the environment.
- The first call is `client.chat.completions.create(model=..., messages=[...])`.
- The answer is at `resp.choices[0].message.content`; `finish_reason` tells you
  why generation stopped and `usage.total_tokens` is the cost meter.

::::::::::::::::::::::::::::::::::::::::::::::::
