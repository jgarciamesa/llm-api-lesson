# Pre-Session Checklist — "Using an API to Communicate with a Model"

Work backwards from doors (Tue, Sept 15, 2:45 PM slot). Each step is independent —
do them in any order, but **Step 2 is the one that can sink the session, so do it first.**

## Step 1 — Confirm attendee accounts on Anvil (D-7 → D-3)
- [ ] Every participant has an **ACCESS account** and is on the workshop's ACCESS
      allocation (PI adds users). Without this they can't log into Anvil Notebook.
- [ ] Verify the list: names, ACCESS usernames. (Anvil shell usernames are
      `x-<ACCESS username>` — notebook login uses the ACCESS username, so this mostly
      matters for the SSH fallback.)
- [ ] Confirm the allocation is an **Anvil** allocation (not just NAIRR cloud), so
      the Anvil Notebook service is available to them.

## Step 2 — TEST EGRESS: can Anvil reach the ASU gateway?  ⚠️ THE BIG ONE
The whole session assumes `https://openai.rc.asu.edu` is reachable from Anvil
(outbound HTTPS 443). **Unverified. Test it days early.**

- [ ] From an Anvil Notebook (or interactive Anvil job), run:
      ```bash
      curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://openai.rc.asu.edu/v1/models
      ```
      - `401` + fast response = **reachable** (it just wants a key — perfect).
      - `000` / timeout / `SSL error` = **blocked** → go to the fallbacks below.
- [ ] If blocked, ask the ACCESS help desk (support.access-ci.org) for:
      - the outbound **proxy host:port** (then set `HTTPS_PROXY` in the notebook), or
      - confirmation that egress to `*.rc.asu.edu` is allowed / can be allowed.
- [ ] **Record the outcome here:**  ☐ reachable directly  ☐ via proxy `____`  ☐ blocked (use laptop-first)

**Fallback decision (make by D-2):**
| Outcome | Primary path |
|---|---|
| Reachable directly | Anvil Notebook (as written in the handout) |
| Reachable via proxy | Anvil Notebook + one extra cell setting `HTTPS_PROXY` |
| Blocked | **Laptop-first** (identical notebook, own Wi-Fi/hotspot); Anvil shown as context |

## Step 3 — API keys (D-3 → D-1)
- [ ] Create **one key per participant** in Voyager (voyager.rc.asu.edu → LLM Access →
      Create Key).
- [ ] Note which **models** each key can use (`GET /v1/models` with a key) — the
      notebook auto-picks, but you should know at least one works.
- [ ] Decide the handoff method (instructor guide §6): pre-session email/ShareLink
      (cleanest) / on-screen table / paper slips.
- [ ] Keep **your own demo key + a known-good model name** separate and tested.

## Step 4 — Test the full flow end-to-end with your demo key (D-2 → D-1)
- [ ] In a **fresh** environment (new venv, or a fresh Anvil Notebook server), run the
      notebook top to bottom: key cell → first call → batch → CSV.
- [ ] Confirm the **model auto-pick** works: if it prints a model list, pick the ID
      that actually responds and note it as your manual override.
- [ ] Time the 12-call batch. If it's >2 min, trim Section 5 experiments or raise the
      buffer. (Expected: 30–90 s.)
- [ ] Verify `triage_table.csv` opens correctly in a spreadsheet.

## Step 5 — Materials to the room (D-1 → doors)
- [ ] Notebook distributed: shared link / repo / zip. (Single file is enough — data is
      embedded.)
- [ ] Participant handout projected or linked on the room screen.
- [ ] Anvil Notebook URL on the screen: `https://notebook.anvilcloud.rcac.purdue.edu`
- [ ] Pre-launch **2–3 Anvil Notebook servers** to confirm login → start → open works
      and to have spares.
- [ ] Venue Wi-Fi tested for the laptop-fallback crowd (or plan phone hotspots).
- [ ] A **fallback laptop** with a known-good connection (hotspot ready).

## Step 6 — Doorgame (D-0, ~30 min before)
- [ ] Your demo environment is live and the first call returns text *right now*.
- [ ] TAs know: (a) the egress status from Step 2, (b) the top 3 errors
      (401 key / 404 model / connection) and their fixes, (c) the room-screen
      run-of-show (instructor guide §10).
- [ ] Keys are ready to hand out at the start.

---

### One-liner to remember
If Step 2 says *blocked*, flip the handout's default to **laptop-first** and rehearse
the proxy cell. Everything else in this package works identically either way.
