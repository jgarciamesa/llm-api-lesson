---
site: sandpaper::sandpaper_site
---

# Using an API to Communicate with a Model

In this 75-minute lesson you make your first **LLM API call**, then build a small
but real **research tool**: a Python script that batch-processes 12 real arXiv
abstracts into a structured triage table (CSV). You finish with free experiment
time and a tour of the researcher-facing tools that wrap the same API.

**No GPUs. No model downloads. No training.** You are a *client* sending messages
over HTTPS to a *service*; text goes in, structured text comes out.

## What you'll use

- The **ASU Research Computing LLM gateway** ([`https://openai.rc.asu.edu/v1`][rc-gateway]),
  an **OpenAI-compatible** API — so the standard [`openai` Python SDK][openai-sdk] just works.
- A **Jupyter notebook** (the main vehicle) you can run on the **Purdue Anvil
  Notebook** (browser, no install) or on your own laptop.

## The pattern (the whole lesson in one line)

> **list of inputs → one model call each → structured JSON rows → save to a file**

If you can repeat that sentence, you have the lesson. Everything else is detail.

## The materials

- [**Setup**](learners/setup.md) — how to get a notebook (Anvil or laptop) and set your key.
- The **episodes** — introduction, your first call, building the research tool, and experiments.
- [**Reference**](learners/reference.md) — glossary, a quick troubleshooting table, and links.
- **Instructor resources** (instructor guide, pre-session checklist, troubleshooting)
  are in the *Instructor* section of the menu.

## Before the workshop (instructors)

The single biggest risk is **network egress**: can the Anvil cluster reach
`https://openai.rc.asu.edu` on outbound HTTPS 443? Test it days early —
see the [pre-session checklist](instructors/presession-checklist.md). Fallbacks
(laptop-first, proxy, demo-only) are in the instructor guide.
