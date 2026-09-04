# Instructor Guide — "Using an API to Communicate with a Model"

**You are teaching:** Beginner Track 2, 2:45–4:15 PM CT, Sept 15, 2026, The Mill at MSU.
**Block:** 90 min. **The plan below is 75 min**, leaving the final 15 min as buffer
for questions, stragglers, and overflow into experiment time.
**Audience:** Mixed; most have basic Python. Keep the copy-paste path clean.

> Read this once through before the workshop. The "Say" lines are a suggested
> script — paraphrase freely. The "Do" lines are actions on screen. Times are
> cumulative from 2:45 PM.

---

## 1. Roles and room setup

- **Lead (you):** drives the demo, narrates, keeps the clock.
- **1–2 TAs:** move through the room, watch for the "stuck staring at the
  screen" look, and — most importantly — watch for the **egress** problem
  (see §8). If half the room can't reach the API, that becomes the whole
  session, so the TA should tell you within 5 minutes, not at the end.
- **On the room screen:** the notebook open, plus a second window with the
  raw `curl` (or the API response JSON) so people can see the wire format
  behind the SDK.
- **Before the first attendee logs in,** confirm the Anvil Notebook server is
  up and that one server per participant (or per pair) can start. Pre-launching
  a few servers is a good idea (see §9).

---

## 2. Materials to stage (day of, before doors)

1. **API keys:** one key per participant (per your decision). You create these
   in Voyager the day before. Hand them out at the start (see §6 for the
   secure-ish handoff).
2. **The notebook,** uploaded where attendees can grab it — a shared folder or
   a zip/repo link. Because the 12 abstracts are **embedded in the notebook**,
   attendees only need the one file. (Big win for the laptop crowd.)
3. **A working demo key + one demo model name** on your own machine, already
   tested, so your live demo never depends on the room's egress (fallback
   path, §8).
4. **A fallback laptop** with a known-good connection (phone hotspot as last
   resort) in case the venue Wi-Fi or cluster egress fails.

---

## 3. The 75-minute arc

| # | Start | Min | Segment | Goal |
|---|---|---|---|---|
| 1 | 2:45 | 5 | Cold open: what is an LLM API? | Frame the problem |
| 2 | 2:50 | 8 | Anatomy of a request | See the wire format |
| 3 | 2:58 | 10 | First call, hands-on | Everyone gets a real response |
| 4 | 3:08 | 10 | Reading the response | Learn the fields you'll use |
| 5 | 3:18 | 12 | Build the research tool | Batch abstracts → structured CSV |
| 6 | 3:30 | 7 | Tools around the API | OpenCode / VS Code / Jupyter AI / AnvilGPT |
| 7 | 3:37 | 18 | Guided experiment time | Attendees test their own prompts |
| 8 | 3:55 | 5 | Data governance + wrap | What not to send; where to go next |
| — | 4:00 | 15 | Buffer | Overflow, questions, stragglers |

*If the room is moving fast, spend the buffer on more experiment time — it's
the highest-value overflow. If the key trap (Segment 3) eats extra minutes,
trim Segment 6 to 30 seconds per tool.*

---

## 4. Segment-by-segment script

### Segment 1 — Cold open (5 min) — "What is an LLM API?"
**Say:** "Everything you'll do today is one thing: you send a message, you
get a message back — over the internet, to a model running on someone else's
servers. That's the whole API. No training, no GPUs on your side, no model
weights to download. You're a *client* talking to a *service*."

**Say:** "You're about to use a real one — ASU Research Computing's LLM
gateway, the same OpenAI-compatible API their own researchers use. You'll
have a key for it in a few minutes."

**Do:** Show the endpoint `https://openai.rc.asu.edu/v1` on screen. Point out
the words "OpenAI-compatible" — that's a standard, and it means any tool that
talks to OpenAI talks to this too. That one fact unlocks the tools tour later.

### Segment 2 — Anatomy of a request (8 min)
**Say:** "Before we code, let's look at what a request actually is. It's just
JSON."

**Do:** Show the raw `curl` (two windows: command + response):
```bash
curl https://openai.rc.asu.edu/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ***" \
  -d '{
    "model": "<MODEL_NAME>",
    "messages": [ { "role": "user", "content": "Explain quantum computing in one sentence." } ]
  }'
```
**Say:** "Three things you're always choosing: the **model**, the **messages**
(a list, each entry with a `role` and a `content`), and optional settings like
`temperature` and `max_tokens`. And keep this in mind for a few minutes from
now: the response is JSON too."

**Teach the `role` field** — it's the single most useful concept for the
research task: `system` = standing instructions, `user` = the turn,
`assistant` = the model's reply. You'll set a `system` message in Segment 5
to force *structured* output.

### Segment 3 — First call, hands-on (10 min) — **everyone gets a response**
**Do:** Open the notebook, walk to the "Set your key" cell first, then the
"First call" cell. Have the whole room run them *together*, before anyone
drifts off.

**Say:** "Run the 'Set your key' cell. If it prints a masked key — `abcd...wxyz`
— you're in. If it says the key is missing but you *can* see it in your
terminal, don't panic — that's the classic trap, and the notebook tells you
exactly how to fix it in 20 seconds."

**TA tip — the trap to pre-announce (the #1 question in the first 10
minutes):** the notebook kernel is a separate process from the terminal; it
only saw the environment when *it* started. So a key exported in the terminal
*after* the kernel started is invisible to the cells. Fixes, in order of
preference: (1) have them run the **companion cell** under "Set your key"
(asks via `getpass`, so the key stays hidden and never gets stored in the
notebook), or (2) **Kernel → Restart Kernel**, then re-run "Set your key".
Never let anyone paste the key into a code cell — it gets saved in the
`.ipynb`.

**Checkpoint (non-negotiable):** *every* attendee gets at least one real
response before you move on. Use the TA to sweep the room. Key-missing errors
are the trap above — 30 seconds to fix. Anything that smells like network or
SSL is the egress problem — go to §8 immediately, don't let it simmer.

### Segment 4 — Reading the response (10 min)
**Say:** "Now open the hood. That reply you just printed was a Python object
wrapping a JSON document. Let's look at the document."

**Do:** Run the "Read the response" cells: `model_dump()` prints the raw
JSON, then the next cell pulls out the three fields that matter. Walk the
annotated sample in the notebook (or the handout) field by field — it's the
mirror of the request anatomy from Segment 2.

**Say (the three that matter):** "There are eleven fields, but for research
you'll live in three. `choices[0].message.content` is the answer.
`choices[0].finish_reason` tells you *why* the model stopped — if it says
`length`, the answer was cut off at `max_tokens` and you should re-run with a
bigger limit. And `usage.total_tokens` is the cost meter: the gateway bills
on this, and the batch tool in the next segment adds it up so you know what
a whole run costs."

**Say (why the raw JSON matters):** "You'll rarely type these fields by hand
— the OpenAI client unpacks them for you. But the documentation describes
the *JSON*, not the Python. Knowing the raw shape is what lets you read the
docs, and it's exactly what you'd write if you used a language without a
client library."

### Segment 5 — Build the research tool (12 min)
**Say:** "Now the part you'll actually take back to your lab. Researchers
don't usually want a chat box — they want to run the *same* question over a
*list* of things and get a table back. Example: you have 12 paper abstracts
and you want a one-line summary, the main method, and the key result for
each, as rows in a spreadsheet. That's batch API calls + structured output."

**Do:** Walk the notebook's "Build the tool" cells:
1. Load the 12 abstracts (already embedded — no download).
2. Define a `system` prompt that says: *answer in strict JSON with keys
   `summary`, `method`, `result`.*
3. Loop over the abstracts, call the API, parse the JSON.
4. Write the rows to `triage_table.csv`.

**Say the key idea out loud:** "This is *structured output* — you're telling
the model the *shape* of the answer, not just the content. For research,
that's what makes it usable: you get columns, not paragraphs. The same loop
works on your grant proposals, your lab notes, your instrument logs —
whatever you can turn into a list of texts."

**Land the pattern:** *list of inputs → one model call each → structured rows
→ save to file.* Repeat it; it's the whole lesson in a sentence.

### Segment 6 — Tools around the API (7 min)
**Say:** "Because it's OpenAI-compatible, a whole shelf of tools just works
with the same key and the same endpoint. Quick tour, 30 seconds each:"
- **OpenCode** (terminal/desktop assistant) — ASU RC has a guide; Voyager
  even generates the provider config for you.
- **VS Code BYOK** — Chat: Manage Language Models → Custom Endpoint → paste
  the RC endpoint + key.
- **Jupyter AI** — `%ai` magic inside notebooks, same gateway.
- **AnvilGPT** — Purdue's own LLM service (UI + API, RAG via a vector DB).
  *It's a separate service with its own access request, but the mental model
  is identical.*

**Say:** "You don't have to use the raw API. Pick the shape that fits your
task: a script → raw API; coding → OpenCode or VS Code; notebook work →
Jupyter AI."

### Segment 7 — Guided experiment time (18 min)
**Say:** "Your turn. The notebook has four experiments. Pick the ones that
fit your own research and go. The point is to feel what different *prompts*
and *models* do to the same input."

Experiments (in the notebook and handout):
1. **Vary the prompt.** Same abstract, ask for (a) a one-sentence summary,
   (b) summary + 3 limitations, (c) "explain to a first-year PhD student."
   Compare.
2. **Vary the model.** Run the same request against 2 different models from
   `/v1/models`. What changed?
3. **Tighten the structure.** Add a field (`confidence`, or
   `reproducible: yes/no/maybe`) to the JSON schema and see the model fill
   it.
4. **Your own data.** Swap the 12 abstracts for 3–5 paragraphs from your own
   work and batch-process them. *(Remind them of the data-governance rule
   before they paste.)*

**TA role:** help anyone whose JSON isn't parsing, whose key is 401, or who
is stuck. Don't write it for them — nudge toward the "why" (see §7).

### Segment 8 — Data governance and wrap (5 min)
**Say (governance — be direct):** "Before you send anything to a gateway,
know the rules. Do **not** send data your institution would call sensitive
or proprietary, and never regulated data — no health records, no
export-controlled work, no SSNs, no biometrics. If you're not sure whether
your data crosses a line, ask your institution *before* you paste it. The
gateway is a convenience, not a secure enclave."

**Say (where to go next):** "Today was the API as a *client*. From here you
can go deeper on the *same* API: streaming responses, function and tool
calling, and RAG (which is what AnvilGPT is doing for you). All the links
are in the handout."

**Do:** Close on the one-sentence pattern: *list in → one call each →
structured rows out.*

---

## 5. The pattern to keep repeating (the whole lesson in one line)
**List of inputs → one model call each → structured JSON rows → save to a file.**
If a participant can repeat that sentence, they've got the lesson. Everything else is
detail.

---

## 6. Key-handoff (secure-ish)
Per your decision, you create one key per participant. Practical, low-friction options —
pick the one that fits your room logistics:
- **Pre-session email/ShareLink:** each attendee gets their own key by name before the
  workshop. Cleanest; no reading keys aloud.
- **On-screen, by row:** project a table of `name → key` and let people grab theirs.
  Fast, but keys are on screen — fine for a workshop, say so.
- **Physical handout:** paper slip per seat. Most private, most prep.

Whichever you choose, **tell them to treat the key as a password**: don't commit it to
Git, don't share it, and they can rotate it in Voyager if they think it leaked. The
notebook reads the key from the **environment** (or the hidden-input companion cell),
never hardcoded — reinforce that habit in Segment 3.

---

## 7. If a participant is stuck — the "why," not the answer
Nudge, don't fix. The highest-yield questions:
- "What does the error actually say? Read it back to me." (401 = key, 404 = model name,
  429 = rate limit — all in `05_troubleshooting.md`.)
- "Where in the JSON is the text you want?" (`choices[0].message.content`.)
- "What does `finish_reason` say? If it's `length`, what happened?" (The answer was cut
  off at `max_tokens` — raise the limit.)
- "If your structured output isn't parsing, what did the model *actually* return?"
  (Usually prose wrapping the JSON — fix the system prompt to demand *only* JSON.)

---

## 8. The big risk: Anvil can't reach the API (egress)
**This is the #1 failure mode.** Some clusters block or proxy outbound internet, so
`openai.rc.asu.edu` may simply not be reachable from Anvil. You verified the ASU
endpoint is up (it is — a 401 "no api key" is a *good* sign: the server is reachable,
it just wants a key), but **reachability from Anvil is a different question** and is
untested.

**Mitigations, in order:**
1. **Test it now** — Step 2 of `04_presession_checklist.md`. Get the answer days early.
2. **Laptop-first:** if Anvil egress is blocked, everyone runs the identical notebook on
   their own laptop (Wi-Fi/hotspot). The notebook is self-contained, so this is a 1-line
   change. *This is why we embedded the data.*
3. **Proxy:** if Anvil has an outbound proxy, set `HTTPS_PROXY`/`HTTP_PROXY` in the
   notebook cell. Ask the ACCESS help desk for the proxy host:port.
4. **Demo-only fallback:** if the venue network is dead, you demo from your laptop (its
   own connection) and the room follows along. The lesson still works; they lose the
   "everyone gets a response" checkpoint.

**Decide the primary path (Anvil vs laptop) by D-2** so the handout's default instructions
match reality. The handout is written to work either way.

---

## 9. Pre-launch tips
- Start **2–3 Anvil Notebook servers early** so you can confirm the flow (login → start →
  notebook opens) and have spares. If a server is slow to start, that's on the service,
  not the attendee — the TA absorbs it.
- Have your **own demo environment fully working** (key + model + notebook) and tested
  minutes before doors. Your demo must not depend on the room's egress.
- Know the **current model names** from `/v1/models` the day-of (they change). The
  notebook auto-selects, but have a known-good model name written down as a manual
  override.

---

## 10. One-page run-of-show (stick on the screen)
```
2:45  Cold open — what is an LLM API
2:50  Anatomy of a request (curl → JSON)
2:58  FIRST CALL — every attendee gets a response  ← CHECKPOINT
3:08  Reading the response (11 fields, 3 you'll use)
3:18  Build the research tool (12 abstracts → CSV)
3:30  Tools around the API (OpenCode, VS Code, Jupyter AI, AnvilGPT)
3:37  Experiment time (4 prompts)                     ← 18 min
3:55  Data governance + where to go next
4:00  Buffer, questions, overflow (to 4:15)
```
