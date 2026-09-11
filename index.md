---
site: sandpaper::sandpaper_site
---

# Using an API to Communicate with a Model

In this lesson you talk to a large language model (LLM) through a
web API -- the same kind of service you call to look up the weather or query
a database. You begin by sending your first message with the `openai` Python
package and reading the model's reply. Then you turn that call into a small
**research tool**: a script that runs the same
structured question over 12 arXiv abstracts and collects the answers into
a table (CSV). One row per paper, with a one-line summary, the main
method, and the key result.

The model lives on Arizona State University's (ASU) Research Computing's
servers, so you are the client: you send it messages over HTTPS and receive
structured text you can drop straight into a spreadsheet.
By the end you will be able to point the same key and endpoint at the everyday
tools you already use (VS Code, Jupyter AI, OpenCode).

## What you'll use and how it fits together

- **The API:** the ASU Research Computing LLM gateway
  ([`https://openai.rc.asu.edu/v1`][rc-gateway]), an **OpenAI-compatible** API.
  Because it follows the OpenAI format, the standard [`openai` Python
  SDK][openai-sdk], and any other OpenAI-compatible tool, works with it as-is.
- **A notebook:** you run the lesson in a Jupyter notebook, either on the
  **Purdue Anvil Notebook** (in a browser, the environment is provided) or on
  your own laptop. The [Setup](learners/setup.md) page gets you started and sets
  your **API key**.
- **Basic Python:** reading a script and editing a few cells is all you need.

The lesson moves in six steps: **Setup**, then **What is an LLM API?**,
**Your first call**, **Building the research tool**, **A simple RAG example**,
and **Experiments & tools**. A **Reference** page (glossary, a quick
troubleshooting table, and links) is in the menu, and the working notebook is
available at [`data/talking_to_a_model.ipynb`](data/talking_to_a_model.ipynb).
