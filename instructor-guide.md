---
title: "Instructor Guide"
---

**You are teaching:** Beginner Track 2, 2:45–4:15 PM CT, Sept 15, 2026, The Mill at MSU.
**Block:** 90 min. **Content below is 75 min.** Keep the final 15 min as buffer / overflow for the experiment phase.
**Audience (per your notes):** Mixed; most have basic Python. Keep a clean copy-paste path.

> Read this once through before the workshop. The "Say" lines are a suggested script —
> paraphrase freely. The "Do" lines are actions on screen. Times are cumulative from 2:45 PM.

---

## 1. Roles & room setup

- **Lead (you):** drives the demo, narrates, manages the clock.
- **1–2 TAs:** rove the room, watch for the "stuck in a wall" look, and — critically —
  watch the **egress** problem (see §8). If half the room can't reach the API, that's the
  session, and the TA should raise it to you within 5 minutes, not at the end.
- **On the room screen:** have the notebook open and a *second* window open showing the
  raw `curl` (or the API response JSON) so people see the wire format behind the SDK.
- **Before first attendee logs in**, confirm the Anvil Notebook server is up and one
  server per participant (or per pair) can start. Pre-launching a few servers is a good
  idea (see §9).

---

## 2. Materials you need staged (D-0, before doors)

1. **API keys:** one key per participant (per your decision). You create these in Voyager
   *before* the day. Distribute at the start (see §6 for the secure-ish handoff).
2. **The notebook** uploaded where attendees can grab it. Easiest: put it in a shared
   location or paste the repo/zip link. Because the 12 abstracts are **embedded in the
   notebook**, attendees do NOT need to download the dataset — one notebook file is all
   they need. (Big win for the mixed/laptop crowd.)
3. **A working demo key + one demo model name** on your own machine, already tested, so
   your live demo never depends on the room's egress (fallback path, §8).
4. **A fallback laptop** with a known-good connection (phone hotspot as last resort) in
   case the venue Wi-Fi or cluster egress fails.

---

## 3. The 75-minute arc

| # | Min (cumulative) | Time | Segment | Goal |
|---|---|---|---|---|
| 1 | 2:45 | 5 | Cold open: what is an LLM API? | Frame the problem |
| 2 | 2:50 | 10 | Anatomy of a request | See the wire format |
| 3 | 2:60→3:00 | 8 | First call, hands-on | Everyone gets a real response |
| 4 | 3:08 | 12 | Build the research tool | Batch abstracts → structured CSV |
| 5 | 3:20 | 10 | Tools around the API | OpenCode / VS Code / Jupyter AI / AnvilGPT |
| 6 | 3:30 | 15 | Guided experiment time | Attendees test their own prompts |
| 7 | 3:45 | 8 | Data governance + wrap | What not to send; where to go next |
| — | 3:53–4:15 | buffer | Overflow / Q&A / stragglers | 15 min cushion |

*Note the "2:60" above is 3:00 PM; the arc runs 2:45 → 3:53 for 68 min of planned content,
leaving ~20 min of the 90 for buffer, which is more than the 15 you asked for. If you want
to spend more of the room, expand Segment 6 (experiment time) — that's the highest-value
overflow.*

---

## 4. Segment-by-segment script

### Segment 1 — Cold open (5 min) — "What is an LLM API?"
**Say:** "Everything you'll do today is one thing: you send a message, you get a
message back — over the internet, to a model that's running on someone else's servers.
That's the whole API. No training, no GPUs on your side, no model weights to download.
You're a *client* talking to a *service*."

**Say:** "You're about to use a real one — ASU Research Computing's LLM gateway, the
same OpenAI-compatible API their own researchers use. You'll get a key for it in a few
minutes."

**Do:** Show the endpoint `https://openai.rc.asu.edu/v1` on screen. Point out the words
"openai-compatible" — that's a standard, and it means any tool that talks to OpenAI
talks to this too. That one fact unlocks the whole "tools around the API" segment later.

### Segment 2 — Anatomy of a request (10 min)
**Say:** "Before we code, let's see what a request actually is. It's just JSON."

**Do:** Show the raw `curl` (two windows: command + response):
```bash
curl https://openai.rc.asu.edu/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  -d '{
    "model": "<MODEL_NAME>",
    "messages": [ { "role": "user", "content": "Explain quantum computing in one sentence." } ]
  }'
```
**Say:** "Three things you're always choosing: the **model**, the **messages** (a list
with `role` + `content`), and optional knobs like `temperature`. The response is JSON too,
and the text you want is at `choices[0].message.content`. The Python SDK just types this
for you."

**Teach the `role` field** — it's the single most useful concept for the research task:
`system` = standing instructions, `user` = the turn, `assistant` = the model's reply.
You'll set a `system` message in Segment 4 to force *structured* output.

### Segment 3 — First call, hands-on (8 min) — **everyone gets a response**
**Do:** Open the notebook, walk to the "First call" cell. Have the whole room run it
*together* before anyone drifts off.

**Say:** "Run this one cell. It loads your key from the `.env` file, calls the model,
prints the answer. If you see a sentence back — you're in."

**Checkpoint (non-negotiable):** *every* attendee gets at least one real response before
you move on. Use the TA to sweep the room. If a chunk can't get a response, that's the
egress problem — go to §8 immediately, don't let it simmer.

### Segment 4 — Build the research tool (12 min)
**Say:** "Now the part you'll actually take back to your lab. Researchers don't usually
want a chat box — they want to run the *same* question over a *list* of things and get a
table back. Example: you have 12 paper abstracts and you want a one-line summary, the
main method, and the key result for each, as rows in a spreadsheet. That's batch API
calls + structured output."

**Do:** Walk the notebook's "Build the tool" cells:
1. Load the 12 abstracts (already embedded — no download).
2. Define a `system` prompt that says: *answer in strict JSON with keys
   `summary`, `method`, `result`.*
3. Loop over the abstracts, call the API, parse the JSON.
4. Write the rows to `triage_table.csv`.

**Say the key idea out loud:** "This is *structured output* — you're telling the model
the *shape* of the answer, not just the content. For research, that's what makes it
usable: you get columns, not paragraphs. The same loop works on your grant proposals,
your lab notes, your instrument logs — whatever you can turn into a list of texts."

**Land the pattern:** *list of inputs → one model call each → structured rows → save to
file.* Repeat it; it's the whole lesson in a sentence.

### Segment 5 — Tools around the API (10 min)
**Say:** "Because it's OpenAI-compatible, a whole shelf of tools just works with the same
key and the same endpoint. Quick tour, 30 seconds each:"
- **OpenCode** (terminal/desktop assistant) — ASU RC has a guide; Voyager even generates
  the provider config for you.
- **VS Code BYOK** — Chat: Manage Language Models → Custom Endpoint → paste the RC
  endpoint + key.
- **Jupyter AI** — `%ai` magic inside notebooks, same gateway.
- **AnvilGPT** — Purdue's own LLM service (UI + API, RAG via a vector DB). *Note: it's a
  separate service with its own access request, but the mental model is identical.*

**Say:** "You don't have to use the raw API. Pick the shape that fits your task: script →
raw API; coding → OpenCode/VS Code; notebook work → Jupyter AI."

### Segment 6 — Guided experiment time (15 min)
**Say:** "Your turn. The notebook has 4 experiment prompts. Pick the ones that fit your
own research and go. The point is to feel what different *prompts* and *models* do to
the same input."

Experiments (in the handout + notebook):
1. **Vary the prompt.** Same abstract, ask for (a) one-line summary, (b) summary +
   3 limitations, (c) "explain to a first-year PhD student." Compare.
2. **Vary the model.** Run the same request against 2 different models from `/v1/models`.
   What changed?
3. **Tighten the structure.** Add a field (`confidence`, or `reproducible: yes/no/maybe`)
   to the JSON schema and see the model fill it.
4. **Your own data.** Swap the 12 abstracts for 3–5 paragraphs from your own work and
   batch-process them. *(Remind them of the data-governance rule before they paste.)*

**TA role:** help anyone whose JSON isn't parsing, whose key is 401, or who's stuck.
Don't write it for them — nudge toward the "why" (see §7).

### Segment 7 — Data governance + wrap (8 min)
**Say (governance — be direct):** "Before you send anything to a gateway, know the rules.
Do **not** send data your institution would call sensitive or proprietary, and never
regulated data — no HIPAA, no export-controlled, no SSNs, no biometrics. If you're not
sure whether your data crosses a line, ask your institution *before* you paste it. The
gateway is a convenience, not a secure enclave."

**Say (where to go next):** "Today was the API as a *client*. From here you can go
deeper on the *same* API: streaming responses, function/tool calling, and RAG (which is
what AnvilGPT is doing for you). All the links are in the handout."

**Do:** Close on the one-sentence pattern: *list in → one call each → structured rows out.*

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
notebook reads the key from a **`.env` file** (`load_dotenv()`), never hardcoded —
reinforce that habit in Segment 3.

---

## 7. If a participant is stuck — the "why," not the answer
Nudge, don't fix. The highest-yield questions:
- "What does the error actually say? Read it back to me." (401 = key, 404 = model name,
  429 = rate limit — all in `05_troubleshooting.md`.)
- "Where in the JSON is the text you want?" (`choices[0].message.content`.)
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
3:00  FIRST CALL — every attendee gets a response  ← CHECKPOINT
3:08  Build the research tool (12 abstracts → CSV)
3:20  Tools around the API (OpenCode/VS Code/Jupyter AI/AnvilGPT)
3:30  Experiment time (4 prompts)                     ← 15 min
3:45  Data governance + where to go next
3:53  Buffer / Q&A / overflow (to 4:15)
```