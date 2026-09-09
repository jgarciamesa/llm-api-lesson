---
title: "Introduction: What Is an LLM API?"
teaching: 15
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- What exactly is a "large language model API", and how is it different from running a model yourself?
- What does a request to this API look like under the hood?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Explain the client / service relationship behind an LLM API.
- Describe the three things you choose in a request: the model, the messages, and the knobs.
- Locate the answer in the response JSON.

::::::::::::::::::::::::::::::::::::::::::::::::

## You are a client talking to a service

The core idea of this lesson is one thing: **you send a message, you get a
message back** — over the internet, to a model running on someone else's
servers. You are a *client* talking to a *service*: the model is hosted for
you, so you simply send it text and read the structured text it returns.

You'll use a real one: **ASU Research Computing's LLM gateway**, the same
OpenAI-compatible API its own researchers use:

- **Endpoint:** [`https://openai.rc.asu.edu/v1`][rc-gateway]
- **SDK:** the standard [`openai` Python package][openai-sdk]
- **Your key:** created in [Voyager][voyager] and given to you for this workshop

The word **"OpenAI-compatible"** does a lot of work. It's a standard: any tool
that talks to OpenAI talks to this too. That single fact is what unlocks the
"tools around the API" at the end of the lesson.

## Anatomy of a request

Before we code, see what a request actually is. It's just **JSON**. The whole
API in one `curl`:

```bash
curl https://openai.rc.asu.edu/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ***" \
  -d '{
    "model": "<MODEL_NAME>",
    "messages": [ { "role": "user", "content": "Explain quantum computing in one sentence." } ]
  }'
```

Three things you're always choosing:

1. **the `model`** — which model answers (from your key's live list),
2. **the `messages`** — a list of `{role, content}` pairs,
3. **optional knobs** — like `temperature` (0 = deterministic).

The response is JSON too, and the text you actually want lives at
**`choices[0].message.content`**. The Python SDK just types this for you.

### The `role` field — the most useful concept today

- `system` = standing instructions (the *shape* you want back)
- `user` = the turn (your actual text)
- `assistant` = the model's reply

You'll set a `system` message later to force *structured* output.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor
Timing: 15 min (5 cold-open, 10 anatomy). Land the "client / service" frame and
the `role` concept here — everything downstream depends on it. Show the endpoint
and the word "openai-compatible" on screen; that's the seed for the tools tour.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- An LLM API is a *service*; you are a *client*. You send JSON, you get JSON back.
- You always choose the **model**, the **messages** (`role` + `content`), and the **knobs**.
- The answer is at `choices[0].message.content`.
- It's **OpenAI-compatible**, so the `openai` Python SDK (and many other tools) just work.

::::::::::::::::::::::::::::::::::::::::::::::::
