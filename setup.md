---
title: Setup
---

**The API you'll use** (ASU Research Computing LLM gateway, OpenAI-compatible):

- Endpoint: `https://openai.rc.asu.edu/v1`
- Your key: the one provided to you for this workshop — **treat it like a
  password** (don't share it, don't commit it to Git).

## Data

The 12 arXiv abstracts are embedded in the notebook, so you can start right
away. If you want the editable source, it's
[`data/research_abstracts.json`](data/research_abstracts.json)

## Software Setup

### On Anvil

1. Go to [`https://notebook.anvilcloud.rcac.purdue.edu`](https://notebook.anvilcloud.rcac.purdue.edu).
2. Log in with your **ACCESS** credentials.
3. Pick **Anvil Notebook**, choose your allocation, **Start**.
4. Wait for JupyterLab to open, then open the `talking_to_a_model` notebook.
5. If a first cell fails with `ModuleNotFoundError: No module named 'dotenv'`
   (or `'chromadb'`), add a cell with `!pip install python-dotenv chromadb`,
   run it, then restart the kernel.

### On Google Colab

If Anvil is unavailable, you can run the same notebook in Google Colab:

1. Open
   [`https://colab.research.google.com/github/jgarciamesa/llm-api-lesson/blob/main/episodes/data/talking_to_a_model.ipynb`](https://colab.research.google.com/github/jgarciamesa/llm-api-lesson/blob/main/episodes/data/talking_to_a_model.ipynb).
2. Choose **Runtime → Run all** only after setting your key.
3. If Colab asks whether to run a notebook from GitHub, choose **Run anyway**
   for this workshop notebook.

Colab runtimes are temporary, so create the `.env` file again each time you
start a new runtime. See **Set your key** below for the notebook cell that does
that.

Then run the notebook's **Set your key** cell. If a package is missing, run
`%pip install openai python-dotenv chromadb` in a cell and restart the runtime.

:::::::::::::::: spoiler

### On your laptop

Create a virtual environment so the install stays out of your system Python:

```bash
python3 --version            # need 3.9+
mkdir api-lesson && cd api-lesson
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install openai python-dotenv chromadb
```

Then put the notebook in that folder and open it (JupyterLab or VS Code).

- **macOS:** if `python3 --version` fails, first `brew install python`.
- **Windows:** install Python 3.9+ from python.org and **check "Add
  python.exe to PATH"** before creating the venv.

::::::::::::::::

## Set your key (one-time)

Your key is a secret, so it goes in a **`.env` file**, not in your code. A
`.env` file is plain text with one `NAME=value` line at a time. In the **same
folder as the notebook**, create a file named `.env` (no extension) with
exactly these two lines:

```
OPENAI_API_KEY=<paste your key here>
OPENAI_BASE_URL=https://openai.rc.asu.edu/v1
```

- **On Anvil:** in JupyterLab, open a terminal (`File → New → Terminal`) and
  run `touch .env`, then click `.env` in the file browser and type the two
  lines.
- **On your laptop:** create it with any text editor (VS Code works well), or
  in a terminal with `nano .env` (Windows: `notepad .env`).

If you are working inside a notebook environment like Google Colab, you can
create the `.env` file from a notebook cell instead:

```python
from getpass import getpass
from pathlib import Path

key = getpass("Paste your API key, then press Enter: ").strip()
Path(".env").write_text(
    f"OPENAI_API_KEY={key}\n"
    "OPENAI_BASE_URL=https://openai.rc.asu.edu/v1\n"
)
del key
print("Wrote .env for this notebook session.")
```

The notebook's **Set your key** cell reads the file with `load_dotenv()`. If
you change the file later, just re-run that cell — no kernel restart needed.

> **Keep `.env` out of Git.** If your folder is a repository, add a file named
> `.gitignore` containing the line `.env`. And remember: the key is a
> password — don't share it, and if you think it leaked, rotate it in Voyager.
