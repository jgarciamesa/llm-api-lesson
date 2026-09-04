# Using an API to Communicate with a Model

> **This folder is the workshop delivery package** for the Sept 15, 2026
> "AI for All" session (MSU Starkville): instructor guide, handout, the
> participant notebook, and pre-session material. It is developed and
> versioned here, under `workshop/`, in this repo. The published Carpentries
> lesson in `episodes/` tracks the same content in sandpaper form.

**AI for All Workshop** — September 15, 2026, The Mill, MSU Starkville
**Slot:** Beginner Track 2 (2:45–4:15 PM CT, 90-min block; content designed for 75 min + 15 min buffer)
**System:** Purdue Anvil (ACCESS allocation) · **Gateway:** ASU RC LLM API (`https://openai.rc.asu.edu/v1`)

## What this lesson does
Participants make their first LLM API call, read every field of the response,
then build a small but real research tool: a batch loop that processes 12 real
arXiv abstracts into a structured triage table (CSV). They finish with free
experiment time and a tour of the researcher-facing tools that wrap the same
API (OpenCode, VS Code BYOK, Jupyter AI, AnvilGPT).

## Package contents
| File | Who uses it |
|---|---|
| `01_instructor_guide.md` | You — 75-min timeline, script, facilitation notes, key logistics, fallbacks |
| `02_participant_handout.md` | Attendees — copy-paste path, Anvil Notebook + laptop variants, experiments |
| `03_notebook_talking_to_a_model.ipynb` | Everyone — ready-to-run Jupyter notebook (main vehicle) |
| `04_presession_checklist.md` | You — D-7 → D-0 test plan, the single biggest risk (cluster egress) has a dedicated step |
| `05_troubleshooting.md` | You + TAs — symptom → cause → fix table |
| `data/research_abstracts.json` | Source dataset (12 real arXiv abstracts, provenance in `data/README.md`). **Also embedded in the notebook** so nothing needs downloading |

## The one thing to verify before anything else
**Can Anvil reach `https://openai.rc.asu.edu` on outbound HTTPS 443?** This is the
single biggest technical risk in the session. Step 2 of `04_presession_checklist.md`
exists to answer it days before the workshop. Fallbacks (laptop-first, proxy, demo-only)
are in the instructor guide §8.

## Key facts baked into the materials
- ASU RC gateway is **OpenAI-compatible**: `openai` Python SDK with `base_url=https://openai.rc.asu.edu/v1`, key from Voyager (`voyager.rc.asu.edu` → LLM Access → Create Key).
- Models list: `GET /v1/models` with the bearer key. The notebook auto-picks a model from the live list (defaults tried: `llama3.3`, `llama3.1`, `llama3`, `gpt-4o`, `mistral-large`).
- Anvil Notebook (browser JupyterHub, no SSH keys needed): `notebook.anvilcloud.rcac.purdue.edu`, log in with ACCESS credentials, any Anvil allocation works.
- Anvil usernames are `x-<ACCESS username>`; login nodes are not for real work — the notebook service is the clean path.
- Data governance: tell participants not to send sensitive/regulated data to the gateway (mirrors AnvilGPT's own policy language).
