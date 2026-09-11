---
title: Reference
---

## Glossary

**API**
: Application Programming Interface. A defined way for one program to ask
  another for work or data. Here, a web service that accepts a JSON request
  and returns a JSON response.

**Client**
: Your code. The side that *sends* the request and *reads* the response. In
  this lesson you are always the client.

**Service**
: The side that *receives* the request and *runs* the model. The ASU RC LLM
  gateway is the service.

**Endpoint**
: The URL you send requests to — here `https://openai.rc.asu.edu/v1`.

**OpenAI-compatible**
: A de-facto standard for the shape of LLM requests/responses. Anything that
  talks to OpenAI's API (the `openai` Python SDK, OpenCode, VS Code, Jupyter
  AI) talks to this gateway too, by pointing it at a different `base_url`.

**API key**
: A secret string that authenticates you to the gateway. Treat it like a
  password: don't share it, don't commit it to Git. Created in
  [Voyager](https://voyager.rc.asu.edu). In this lesson it lives in a `.env`
  file, never in your code.

**`.env` file**
: A plain-text file with one `NAME=value` line at a time, used to store
  settings such as API keys. The notebook reads it with
  `load_dotenv()` (from the `python-dotenv` package). Keep it out of Git: put
  a `.gitignore` file containing the line `.env` in the same folder.

**`base_url`**
: The endpoint your SDK is told to use. Must end in `/v1`. Stored as
  `OPENAI_BASE_URL` in the `.env` file.

**Model**
: A specific language model that answers. Your key can use a list of models
  (see `GET /v1/models`). The names change over time — always list them.

**Messages**
: A list of `{role, content}` pairs that make up the conversation. `role` is
  `system`, `user`, or `assistant`.

**`role`**
: Who is speaking. `system` = standing instructions, `user` = your turn,
  `assistant` = the model's reply.

**`choices[0].message.content`**
: Where the model's text answer lives in the JSON response.

**`temperature`**
: A knob for randomness. `0` = as deterministic as the model allows; higher =
  more varied.

**Structured output**
: Telling the model the *shape* of the answer (e.g. return only a JSON object
  with keys `summary`, `method`, `result`), not just the words. This is what
  makes LLM output usable as a table rather than a paragraph.

**Batch processing**
: Running the *same* request over a *list* of inputs (here, 12 abstracts) and
  collecting the results into rows.

**RAG**
: Retrieval-Augmented Generation — grounding the model's answer in your own
  documents. The *A Simple RAG Example* episode builds a keyword version;
  Purdue's AnvilGPT does it out of the box with vector search.

## Quick troubleshooting table

The first three rows cover ~90% of what you'll see. Read the error **verbatim**
first.

| You see | It means | Fix |
|---|---|---|
| `401` / "No api key" | `.env` missing, in the wrong folder, or mistyped | Check the two lines in `.env` (same folder as the notebook; no stray spaces or a leftover `<`), then re-run the "Set your key" cell — it re-reads the file, no kernel restart needed. |
| `404` / "Model Not Found" | Model name invalid for this key | List models (`client.models.list()`) and copy an exact ID into `MODEL`. |
| `429` / "Rate limit" | Too many requests | Wait a few seconds and retry. |
| Connection error / timeout / `SSL` | Can't reach the endpoint (**egress** problem, or wrong base URL) | Confirm `OPENAI_BASE_URL=https://openai.rc.asu.edu/v1` (with `/v1`). If on Anvil and still failing, tell an instructor — your cluster may block outbound traffic. |
| `ModuleNotFoundError: No module named 'openai'` or `... 'dotenv'` | Ran outside the venv (laptop), or install incomplete | `source .venv/bin/activate`, `pip install openai python-dotenv`, **restart the kernel**. |
| `NameError: name 'client'/'MODEL'` | Ran cells out of order, or after a kernel restart | Run cells **top to bottom**; after a restart, re-run from the key cell. |
| `PARSE FAILED` in a row | Model returned prose, not JSON | Print the raw `message.content`; tighten the system prompt to "Return ONLY valid JSON, no other text." |

## Where to go next

- **ASU RC docs (canonical):** <https://docs.rc.asu.edu/ai/api>
- **Voyager (key management):** <https://voyager.rc.asu.edu>
- **Anvil Notebook:** <https://notebook.anvilcloud.rcac.purdue.edu>
- **AnvilGPT (Purdue's own LLM):** <https://anvilgpt.rcac.purdue.edu>
- **`openai` Python SDK:** <https://pypi.org/project/openai/>

## Data source

The 12 abstracts are public arXiv papers (2 per field, 6 fields). Source and
provenance (arXiv IDs, fetch date) is recorded in the dataset's `README` (see the
[data folder](data/research_abstracts.json))
