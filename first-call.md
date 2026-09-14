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

- Put your key and endpoint in a `.env` file (never hardcode them).
- Make a first call with the `openai` Python package.
- Read the model's reply out of the response.

::::::::::::::::::::::::::::::::::::::::::::::::

## Set your key (don't hardcode it)

Your key is a secret. Treat it like a password: **don't share it, don't commit
it to Git.** The notebook reads it from a **`.env` file** so it never sits in
your code. A `.env` file is plain text, one `NAME=value` line at a time.

In the **same folder as the notebook**, create a file named `.env` (no
extension) with exactly these two lines:

```
OPENAI_API_KEY=<paste your key here>
OPENAI_BASE_URL=https://openai.rc.asu.edu/v1
```

The [Setup page](../learners/setup.md) shows how to create that file on Anvil
and on a laptop. Then run the **"Set your key"** cell in the notebook — it
loads the file and verifies the key is present (masked):

```python
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key and base URL
key = os.getenv("OPENAI_API_KEY")
base = os.getenv("OPENAI_BASE_URL")

if not key or not base:
    missing = ", ".join(n for n, v in
                        (("OPENAI_API_KEY", key), ("OPENAI_BASE_URL", base)) if not v)
    raise SystemExit(
        f"Missing {missing}. Create a .env file in this folder with these two "
        "lines, then re-run this cell:\n"
        "    OPENAI_API_KEY=<your-key>\n"
        "    OPENAI_BASE_URL=https://openai.rc.asu.edu/v1"
    )

# Mask the key so we can show it is present without revealing it
print(f"key set:   {key[:4]}...{key[-4:]}  ({len(key)} chars)")
print(f"base url:  {base}")
```

Two things to notice. `load_dotenv()` reads the `.env` file into the
environment, and `os.getenv()` looks a name up in that environment — so the
key only lives in the file, which you keep out of Git. Because the cell reads
the file every time it runs, **if you edit `.env` you only re-run the cell** —
no kernel restart.

## The first call — *checkpoint: everyone gets a response*

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor
This is the non-negotiable checkpoint. Have the whole room run this ONE cell
together before anyone drifts off. Use the TA to sweep the room: if a chunk can't
get a response, that's the egress problem — go to the instructor guide §8
immediately, don't let it simmer.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

The next cell picks one of the three models this lesson prefers — **at random** —
from your key's live list, so you can run the first call right away. It also
prints up to eight models your key can use. If none of the three preferred
models is available, it falls back to the first model on the list; if nothing
prints at all, set `MODEL` yourself and re-run.

```python
from openai import OpenAI
import random

client = OpenAI()   # reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment

# Pick a model at random from the live list for your key.
PREFERRED = ["qwen36-27b", "muse-glimmer-30b", "gemma4-31b-it"]
try:
    available = [m.id for m in client.models.list()]
except Exception as e:
    available = []
    print(f"Could not list models: {e}")

# A preferred name can be a prefix of the full model ID, so match by
# substring. Then pick one of the matches at random.
matches = [a for a in available if any(p in a for p in PREFERRED)]
if matches:
    MODEL = random.choice(matches)
elif available:
    MODEL = available[0]   # none of the three is available; use the first
else:
    raise SystemExit(
        "No model could be selected. Set one manually, e.g.\n"
        "    MODEL = 'llama3.1'\n"
        "then re-run."
    )
print(f"Using model: {MODEL}  (picked at random)")
if available:
    print(f"Your key can use {len(available)} model(s). Here are the first eight:")
    for a in available[:8]:
        print(f"   - {a}")
```

Now send the first request with the selected model:

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain what an API is, in one sentence."}],
)
print("\n--- MODEL SAYS ---")
print(resp.choices[0].message.content)
print(f"\n(tokens used: {resp.usage.total_tokens if resp.usage else '?'})")
```

You should see a sentence from the model. If text appears, your first call worked.

### Try a setting: `temperature`

The API has small controls, often called *settings* or *knobs*, that change how
the model answers. `temperature` is a good first one to try: `0` asks for the
most consistent wording the model can give, while larger values usually make the
wording more varied.

Run the cell below a few times. Then change `temperature` to `0`, `0.7`, or
`1.0` and compare what happens.

```python
for temp in [0, 0.7, 1.0]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Give me a friendly one-sentence definition of an API."}],
        temperature=temp,
    )
    print(f"temperature={temp}")
    print(resp.choices[0].message.content)
    print()
```

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
  "model": "gemma4-31b-it",                 // 4 — the model that actually
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

Three fields matter most for the rest of the lesson:

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

- `401` / "No api key" → the `.env` file is missing, in the wrong folder, or
  has a typo (a stray space or a `<` left in). Check both lines, then re-run
  the "Set your key" cell — the cell re-reads the file, so no restart is
  needed.
- `ModuleNotFoundError: No module named 'dotenv'` → you're outside the venv,
  or the install didn't include `python-dotenv`. Re-run
  `pip install openai python-dotenv` and restart the kernel.
- `404` / "Model Not Found" → bad model name. List models and copy an exact ID.
- `429` → rate limit. Wait a few seconds and retry.
- Connection/timeout/SSL → possible **egress** problem. See the [Reference
  page](../learners/reference.md) or raise a hand.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- Put the key and endpoint in a `.env` file; `load_dotenv()` reads it, so
  nothing is hardcoded.
- `client = OpenAI()` reads `OPENAI_API_KEY` and `OPENAI_BASE_URL` from the
  environment.
- The first call is `client.chat.completions.create(model=..., messages=[...])`.
- The answer is at `resp.choices[0].message.content`; `finish_reason` tells you
  why generation stopped and `usage.total_tokens` is the cost meter.

::::::::::::::::::::::::::::::::::::::::::::::::
