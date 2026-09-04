# Troubleshooting — "Using an API to Communicate with a Model"

Symptom → cause → fix. TAs: work top-down; the first three rows cover ~90% of what
you'll see. Read the error text **verbatim** to the room — that's the lesson too.

## A. API / key errors (most common)

| # | Symptom (what the screen shows) | Likely cause | Fix |
|---|---|---|---|
| A1 | `401` / `Authentication Error, No api key passed in` | `OPENAI_API_KEY` not set in this notebook's environment (fresh server, new terminal, or the export was in a *different* shell) | Re-run the **Set your key** step (handout Step 1), then re-run the key-check cell. A notebook kernel only sees env vars set *before the kernel started* — if they exported it in a terminal, **restart the kernel** first. |
| A1b | Cell says "key not in THIS kernel's environment" but `echo $OPENAI_API_KEY` in the terminal **shows the key** | The **terminal-vs-kernel trap** (the #1 first-10-minutes question): the kernel is a separate process and snapshotted the env at *its* start; the export happened after that. The key really is fine — the kernel just can't see it. | Have them run the **companion cell** right under "Set your key" (it uses `getpass`, so the key stays hidden and is never saved in the .ipynb), then re-run the Set-your-key cell. Alternative: **Kernel → Restart Kernel** in the menu, then re-run the Set-your-key cell (the terminal's vars are already there). Do **not** have them paste the key into a code cell — it would be saved in the notebook file. |
| A2 | `401` but key looks right | Stray spaces / line-break in the pasted key; or key was revoked | `print(repr(os.environ["OPENAI_API_KEY"]))` — check for `"` `\n` whitespace. Re-copy the key. |
| A3 | `404` / `Model Not Found` | Model ID not valid for this key (names change; e.g. `llama3` vs `llama3.1`) | List models: `[m.id for m in client.models.list()]`, copy an exact ID into `MODEL`. |
| A4 | `429` / `Rate limit reached` | Too many concurrent requests (whole room hitting at once) | Wait 5–15 s, retry. In the batch cell, errors on one abstract don't stop the loop. If it persists >2 min, stagger the room (half on Experiment 1, half on 2). |
| A5 | `openai.OpenAIError` / generic `Connection error`, `SSLError`, `NameResolutionError`, or a cell just hangs | **Egress problem** — the machine can't reach `openai.rc.asu.edu` (see E below). Also: wrong base URL. | Confirm `OPENAI_BASE_URL == "https://openai.rc.asu.edu/v1"` (with `/v1`). Then `curl -sS -o /dev/null -w '%{http_code}\n' https://openai.rc.asu.edu/v1/models` in a notebook terminal. `401` = network fine, back to A1/A3. `000`/timeout/SSL = E. |

## B. Notebook / environment errors

| # | Symptom | Likely cause | Fix |
|---|---|---|---|
| B1 | `ModuleNotFoundError: No module named 'openai'` (laptop path) | Ran outside the venv | `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then `pip install openai python-dotenv`. **Restart the kernel** after installing. |
| B2 | `python: command not found` | Python not on PATH (Windows install missed the checkbox) | Reinstall and check "Add python.exe to PATH"; or use `python3`. Reopen the terminal after any install. |
| B3 | Old env after setting vars in a terminal | Kernel outlives the shell | **Kernel → Restart** after changing env vars. (On Anvil Notebook, the kernel's env = the server's env; setting vars in the JupyterLab *terminal* does NOT propagate to an already-running kernel.) |
| B4 | `NameError: name 'client' is not defined` | Ran Section 4 before Section 2 (or after a kernel restart) | Run cells **top to bottom**. After any kernel restart, re-run from the key cell. |
| B5 | `NameError: name 'MODEL'` | Model cell raised (A3/A5) and was skipped | Fix the model first (A3), re-run the "First call" section. |
| B6 | Anvil Notebook: "server failed to start" / long wait | Allocation busy / queue | Wait; try again; if it never starts, file a quick note to the ACCESS help desk and switch that attendee to laptop mode. Pre-launched spares (checklist Step 5) absorb this. |

## C. Reading-the-response symptoms (Section 3)

| # | Symptom | Likely cause | Fix |
|---|---|---|---|
| C0 | Answer looks cut off mid-sentence; `finish_reason` is `length` | `max_tokens` was too small for the answer | Raise `max_tokens` (or shorten the prompt) and re-run. Teach the moment: `finish_reason` is the field that tells you this happened — it's the first thing to check on a suspicious answer. |
| C0b | `usage.total_tokens` is much bigger than expected | Long context (big abstracts) or a chatty `system` prompt | Note it as the cost meter; trim the prompt or the input. This is the number the gateway bills on — budget a batch job from it. |

## D. Research-tool errors (Section 4)

| # | Symptom | Likely cause | Fix |
|---|---|---|---|
| D1 | Row shows `PARSE FAILED` | Model returned prose around the JSON despite the system prompt | The cell already strips ``` fences and retries once. If it still fails, print the raw text, then tighten the system prompt: "Return ONLY valid JSON. No text before or after." Lower `temperature` (already 0). |
| D2 | JSON parses but keys missing | Model used slightly different key names | `row.get(k, "not stated")` already guards this — check which key is missing and make the system prompt list keys more explicitly. |
| D3 | CSV opens but columns shifted | A summary contains an unescaped comma/quote | We use `csv.DictWriter`, which quotes fields properly — if you see shifts, someone hand-edited the CSV. Re-run the "Save and inspect the CSV" cell (4c). |
| D4 | Batch is very slow (>3 min for 12) | Big model + rate limiting | Use a smaller/faster model from the list; or reduce to 6 abstracts for the live demo and let the rest finish in experiment time. |

## E. The egress wall (Anvil can't reach the internet)

Recognize it fast: `curl` to the endpoint returns `000`/timeout/SSL, **and** a
`curl https://www.google.com` from the same Anvil terminal also fails or hangs.

1. **Confirm it's the cluster, not the laptop:** run the same curl on a phone
   hotspot → works = cluster egress is the wall.
2. **Proxy path (if ACCESS has one):** ask the ACCESS help desk for the outbound
   proxy host:port, then add this cell **before** the key cell:
   ```python
   import os
   os.environ["HTTPS_PROXY"] = "http://<proxy-host>:<port>"
   os.environ["HTTP_PROXY"]  = "http://<proxy-host>:<port>"
   ```
   then **restart the kernel** and re-run.
3. **Laptop-first (if no proxy):** flip the room to the laptop path (handout Step 0,
   laptop variant). The notebook is self-contained, so it's a 1-line change. You demo
   from the room screen on your own connection.
4. **Never** route a participant's key through a third-party tunnel you set up
   ad hoc — it's their credential; use official paths only.

## F. Data-governance near-misses (be ready to interrupt)
If you catch an attendee pasting real patient data, grant-PII, or export-controlled
content into an experiment cell: stop them politely, point at the handout's
governance note, and steer them to Experiment 1–3 (public abstracts) or their own
*non-sensitive* text. This is a teaching moment, not a failure.

---

### 30-second TA triage
1. Read the error verbatim.
2. `401` → A1/A2 · `404` → A3 · `429` → A4 · connection/SSL → A5 then E.
3. `No module named` → B1 · `NameError: client/MODEL` → B4/B5.
4. Cut-off answer (`finish_reason: length`) → C0 · `PARSE FAILED` → D1.
5. Still stuck? Have them **restart the kernel and run top-to-bottom** — it fixes
   roughly a third of everything.
