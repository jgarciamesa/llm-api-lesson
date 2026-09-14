# Using an API to Communicate with a Model

A 75-minute Carpentries-style lesson for the **"AI for All"** workshop (ASU
Research Computing / AIR). It takes researchers who are new to LLMs from
*zero* to a small, working research tool that calls a model through an
OpenAI-compatible API and returns structured JSON.

## The lesson

Participants run a Jupyter notebook (on Anvil in the browser, in Google Colab,
or on their own machine) and, step by step:

1. **Make their first LLM API call** and read the response.
2. **Build a research tool** that batches a set of real arXiv abstracts
   through the model and returns structured output.
3. **Run quick experiments** (prompt changes, temperature, structured output)
   to build intuition for how to talk to a model.

The API key points to ASU Research Computing's OpenAI-compatible gateway
(`openai.rc.asu.edu`), so no commercial account is needed.

## Lesson structure

| Path | What it is |
|------|------------|
| `episodes/` | The five learner episodes (introduction → first call → build the tool → experiments → simple RAG), each with inline code. |
| `episodes/data/` | The downloadable assets: the notebook (`talking_to_a_model.ipynb`) and the 12 abstracts (`research_abstracts.json`). |
| `learners/` | Setup instructions and a reference page (glossary + troubleshooting). |
| `instructors/` | Instructor guide, pre-session checklist, and a TA troubleshooting sheet (visible in the *Instructor* view). |
| `profiles/` | Who the lesson is for. |
| `config.yaml` | Site configuration (title, episode order, contact, etc.). |

## Where it's hosted

The lesson site is built automatically by [The Carpentries
Workbench][workbench] and deployed to GitHub Pages whenever you push to
`main`. The live site is:

**https://jgarciamesa.github.io/llm-api-lesson/**

Open it with the *Instructor View* toggle (top-right) to see the instructor
pages alongside the learner material.

## Editing and rebuilding

- Edit any Markdown file, `git commit`, and `git push` to `main`.
- Watch the **"01 Maintain: Build and Deploy Site"** GitHub Actions workflow;
  when it goes green, the site is updated.
- For a local preview: `Rscript -e 'sandpaper::build_lesson(".")'` (requires
  R and the `sandpaper` package), then open `site/docs/index.html`.

## Citing this lesson

See [`CITATION.cff`](CITATION.cff). The lesson content is licensed CC-BY 4.0
(see [`LICENSE.md`](LICENSE.md)).

[workbench]: https://carpentries.github.io/sandpaper-docs/
