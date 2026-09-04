# Using an API to Communicate with a Model — Participant Handout

*AI for All Workshop · MSU Starkville · September 15, 2026 · Beginner Track 2
The Mill, 600 Russell St, Starkville, MS 39759 · 2:45–4:15 PM CT*

In this session you will talk to a large language model the way researchers do
outside of notebooks: by sending an HTTP request to an API. You will make your
first API call to a production LLM in the first half of the hour, then turn
that call into a small research tool that summarizes 12 abstracts across six
fields and saves the results to a CSV.

## Objectives

After this session you will be able to:

- Send an authenticated request to the ASU Research Computing LLM API
- Explain the fields in an API request *and* the fields in its response
- Build a Python loop that batch-processes a list of inputs through the API
- Handle one failed request by catching the error and retrying it

**Before you arrive (5 minutes):** create your API key at
<https://voyager.rc.asu.edu>. You will need it in Step 1.

## What you will need

| Item | Where to get it |
|---|---|
| A laptop with a browser | Your own, or borrow one |
| A Purdue ACCESS account | The workshop provides logins to the Anvil Notebook (or use your own ACCESS account) |
| An ASU RC API key | Create one at [voyager.rc.asu.edu](https://voyager.rc.asu.edu) (~5 min) |
| The notebook | `03_notebook_talking_to_a_model.ipynb` (shared in the workshop folder) |

**Setup (10 min, start now):** log in to the Anvil Notebook at
<https://notebook.anvilcloud.rcac.purdue.edu>, upload the notebook, and open
it. If you are running from home, install the one dependency first:

```bash
pip install openai
```

## Step 1 — Set your key (don't hardcode it)

**Do this in a terminal *before* you open the notebook** — that way the kernel
starts with your key already in its environment:

**macOS / Linux**
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Windows PowerShell**
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

Then in the notebook, run the **"Set your key"** cell. It prints the key back
with the middle hidden — if you see `sk-abc…wxyz`, you're ready.

> **Note — "I exported the key but the notebook can't see it"**
> The notebook's kernel is a *separate process* from your terminal. It only
> sees environment variables that existed **when the kernel started**, so a
> key you exported afterwards (or typed into the notebook's own terminal tab)
> is invisible to it. Two fixes:
> - Run the **"or set it here, without restarting"** cell right below the key
>   cell. It asks for the key with the input hidden and never saves it.
> - Or restart the kernel (*Kernel → Restart Kernel* — no need to re-run
>   anything yet), then run the "Set your key" cell again.
>
> Either fix is fine. The instructor will call this out in the first ten
> minutes — it's the most common hiccup in the session.

## Step 2 — One call

Run the **"First call"** cell. You should see the model's reply printed, plus
how many tokens it used and how long it took. Change `MAX_TOKENS` to 10, 50,
or 200 and run it again — watch what happens to the reply, the usage, and the
latency.

### Anatomy of the request

Everything you sent is visible in the `client.chat.completions.create(...)`
call:

```python
client.chat.completions.create(
    model=MODEL,                         # 1 — which model to run (from the
                                         #    "pick a model" cell above)
    messages=[{                          # 2 — the conversation
        "role": "system", "content": "..." #   "system" = standing instructions
    }, {                                 #    "user" = this turn's input
        "role": "user", "content": "..."
    }],
    max_tokens=120,                       # 3 — stop generating after this
                                         #    many tokens (cost control)
    temperature=0.3,                      # 4 — sampling randomness, 0–1
                                         #    (lower = more predictable)
)
```

1. **`model`** — which model on the gateway runs your request.
2. **`messages`** — the conversation as a list of turns. `system` sets
   standing instructions; `user` is this turn's input.
3. **`max_tokens`** — a ceiling on how many tokens the model may generate.
   Token limits are the main way you keep costs and runtimes in check.
4. **`temperature`** — how much randomness goes into picking the next token.
   Low values make output predictable; high values make it creative.

> **Note:** the call itself doesn't include the base URL or the key. Both
> live in the `OpenAI(base_url=..., api_key=...)` line — one place each,
> so they can't drift out of sync inside your code.

### Anatomy of the response

Every reply comes back as a JSON object with the same shape. Here is a
typical one, with each field explained:

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

Three of these matter most for your work:

1. **`choices[0].message.content`** — the actual text. This is the field
   every loop in Step 3 reads.
2. **`choices[0].finish_reason`** — if it says `"length"`, your reply was
   cut off at `max_tokens`; raise the limit and try again.
3. **`usage.total_tokens`** — the cost meter. The batch tool in Step 3
   adds these up so you know what the whole run cost.

> **Note:** in the notebook you rarely touch these fields directly — the
> OpenAI client unpacks them into attributes. `response.choices[0].message.content`
> is the same as `choices[0].message.content` above, and `response.usage`
> gives you the token counts. Knowing the raw shape matters when you read
> documentation (which describes the JSON, not the Python) or when you move
> to a language without a client library.

## Step 3 — Turn the call into a tool (25 min)

The "batch tool" cells read the 12 embedded abstracts (2 per field, 6
fields), ask the model for a 2–3 sentence **summary** and the **method** for
each one, and write the results to `triage_table.csv`.

The interesting parts:

- **One loop, twelve calls.** The same `create()` you ran in Step 2 now runs
  inside a `for` loop. Nothing about the API call changes — only the number
  of times you make it.
- **Structured output.** The prompt asks for JSON with `summary` and
  `method` fields, and the code parses it out. Models don't always follow
  instructions perfectly, so the code strips stray code fences and retries
  once if parsing fails — a `result` column records what happened to each
  row.
- **Rate limits and retries.** If a request returns a 429 (rate limit), the
  code waits a few seconds and tries again instead of crashing.

Run the cells in order, then open `triage_table.csv`. You should have twelve
rows: one per abstract, each with a field, title, arXiv ID, summary, method,
and a status.

## Step 4 — Experiment (15 min)

Try at least two of these; the TA is nearby if you get stuck.

- **Change the prompt.** Ask for the summary in one sentence instead of
  three. Ask for a "significance" rating (1–5) instead of the method. How
  does the CSV change?
- **Change the temperature.** Run the same prompt at `temperature=0.0` and
  `temperature=0.9`. Which gives you more consistent summaries?
- **Change `max_tokens`.** Set it to 20. Watch `finish_reason` become
  `"length"` and your summaries get truncated.
- **Pick a different model.** Re-run the "pick a model" cell, choose a
  different one, and compare quality and speed on the same abstract.
- **Break it on purpose.** Set `max_tokens=1` in the batch loop. Read the
  error the retry logic produces, then fix it.

## Around the API (5 min, if we have time)

You don't need to use raw API calls in your daily work — several tools wrap
the same model for you. Here are the ones we have in the room:

- **OpenCode** — a terminal AI assistant you point at your repo
- **VS Code + BYOK** — your editor, using your own API key
- **Jupyter AI** — a chat cell inside Jupyter, with your notebook as context
- **AnvilGPT** — the Anvil-hosted assistant for job scripts and cluster
  questions

Same models, different wrappers. The API call in this notebook is what all
of them do under the hood.

## Key points

- A model call is just an HTTP request: a URL, a key, a JSON body. The
  OpenAI client hides the HTTP so you can focus on the conversation.
- The response has a fixed shape. `choices[0].message.content` is the text;
  `usage.total_tokens` is the cost meter; `finish_reason` tells you if your
  reply was cut off.
- Batch work is a `for` loop around one API call, plus error handling for
  the requests that fail.
- Never hardcode your API key. Read it from the environment or use the
  hidden-input cell.
