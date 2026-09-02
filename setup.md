---
title: Setup
---

You'll run the notebook either **on Anvil** (browser, no install) or **on your
laptop**. Both use the same notebook and the same key. The notebook **already
contains the 12 abstracts** — you don't need to download data.

**The API you'll use** (ASU Research Computing LLM gateway, OpenAI-compatible):

- Endpoint: `https://openai.rc.asu.edu/v1`
- Your key: the one provided to you for this workshop — **treat it like a
  password** (don't share it, don't commit it to Git).

## Data

There is nothing to download. The 12 arXiv abstracts are embedded in the
notebook. If you want the editable source, it's
[`data/research_abstracts.json`](data/research_abstracts.json)

## Software Setup

You need the **`openai` Python package** (and `python-dotenv`). On a laptop,
create a virtual environment so you don't pollute your system Python:

```bash
python3 --version            # need 3.9+
mkdir api-lesson && cd api-lesson
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install openai python-dotenv
```

On **Anvil**, the environment is provided — you just log in and start a
notebook (below).

:::::::::::::::: spoiler

### On Anvil (browser, no install)

1. Go to `https://notebook.anvilcloud.rcac.purdue.edu`
2. Log in with your **ACCESS** credentials.
3. Pick **Anvil Notebook**, choose your allocation, **Start**.
4. Wait for JupyterLab to open, then open the `talking_to_a_model` notebook.

::::::::::::::::

:::::::::::::::: spoiler

### macOS (laptop)

1. Check Python: `python3 --version` (install via `brew install python` if
   missing).
2. Create the venv and install as above.
3. Open the notebook in that folder (JupyterLab or VS Code).

::::::::::::::::

:::::::::::::::: spoiler

### Windows (laptop)

1. Install Python 3.9+ from python.org — **check "Add python.exe to PATH."**
2. Create the venv and install as above.
3. Open the notebook in that folder (JupyterLab or VS Code).

::::::::::::::::

## Set your key (one-time, per session)

Your key is a secret, so set it in the **environment**, not in code. Pick your
platform:

:::::::::::::::: spoiler

### macOS / Linux

```bash
read -rs OPENAI_API_KEY        # paste your key, press Enter (nothing prints)
export OPENAI_API_KEY
export OPENAI_BASE_URL="https://openai.rc.asu.edu/v1"
```

::::::::::::::::

:::::::::::::::: spoiler

### Windows (PowerShell)

```powershell
$env:OPENAI_API_KEY = Read-Host -AsSecureString "API key" | ForEach-Object { [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($_)) }
$env:OPENAI_BASE_URL = "https://openai.rc.asu.edu/v1"
```

::::::::::::::::

:::::::::::::::: spoiler

### On Anvil (environment variable for the kernel)

Set it in a notebook cell **before** the first call, then the rest of the
notebook reads it from `os.environ`:

```python
import os
os.environ["OPENAI_API_KEY"] = "paste-your-key-here"
os.environ["OPENAI_BASE_URL"] = "https://openai.rc.asu.edu/v1"
```

(Or, if the workshop pre-configured it for you, skip this — the "Set your key"
cell will confirm it's present.)

::::::::::::::::

> **Why not just type it at a prompt?** A normal prompt writes the key to your
> shell history in plain text. `read -rs` (and `Read-Host -AsSecureString`)
> keep it out of view and out of history. The same rule applies to `.env`
> files: keep them out of Git (a `.gitignore` with `.env` and `.venv/`).
>
> **Kernel gotcha:** a notebook kernel only sees environment variables that were
> set **before the kernel started**. If you exported the key in a separate
> terminal, **restart the kernel** before running the "Set your key" cell.
