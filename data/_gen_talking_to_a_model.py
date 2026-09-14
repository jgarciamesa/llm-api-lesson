import ast
import json
import re
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[2]
EPISODES = [
    "introduction.md",
    "first-call.md",
    "build-the-tool.md",
    "experiments.md",
    "simple-rag.md",
]


LINKS = {
    "rc-gateway": "https://openai.rc.asu.edu/v1",
    "rc-api-docs": "https://docs.rc.asu.edu/ai/api",
    "voyager": "https://voyager.rc.asu.edu",
    "anvilgpt": "https://anvilgpt.rcac.purdue.edu",
    "openai-sdk": "https://pypi.org/project/openai/",
}


def split_yaml(text):
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.S)
    if not match:
        return {}, text
    metadata = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, match.group(2)


def remove_instructor_blocks(text):
    pattern = (
        r":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: instructor\n"
        r".*?"
        r"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n?"
    )
    return re.sub(pattern, "", text, flags=re.S)


def clean_carpentries_fences(text):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("::::::::::::::::") and stripped.endswith("questions"):
            lines.append("### Questions")
            continue
        if stripped.startswith("::::::::::::::::") and stripped.endswith("objectives"):
            lines.append("### Objectives")
            continue
        if stripped.startswith("::::::::::::::::") and stripped.endswith("keypoints"):
            lines.append("### Key Points")
            continue
        if stripped.startswith("::::::::::::::::") and stripped.endswith("exercises"):
            lines.append("### Exercises")
            continue
        if stripped.startswith("::::::::::::::::") and set(stripped) == {":"}:
            continue
        if stripped.startswith("::::::::::::::::"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def inline_reference_links(text):
    for label, url in LINKS.items():
        text = text.replace(f"][{label}]", f"]({url})")
    return text


def markdown_to_cells(text):
    cells = []
    pos = 0
    fence_re = re.compile(r"```(\w+)?\n(.*?)\n```", re.S)
    for match in fence_re.finditer(text):
        before = text[pos:match.start()].strip()
        if before:
            cells.append(nbformat.v4.new_markdown_cell(before))
        lang = match.group(1) or ""
        body = match.group(2)
        if lang == "python" and 'api_key="***"' not in body:
            cells.append(nbformat.v4.new_code_cell(body))
        else:
            cells.append(nbformat.v4.new_markdown_cell(match.group(0)))
        pos = match.end()
    after = text[pos:].strip()
    if after:
        cells.append(nbformat.v4.new_markdown_cell(after))
    return cells


def model_selection_cell():
    return r'''from openai import OpenAI
import random

client = OpenAI()   # reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment

# Pick a model at random from the live list for your key.
PREFERRED = ["qwen36-27b", "muse-glimmer-30b", "gemma4-31b-it"]
try:
    available = [m.id for m in client.models.list()]
except Exception as e:
    available = []
    print(f"Could not list models: {e}")

# A preferred name can be a prefix of the full model ID, so match by
# substring. Then pick one of the matches at random.
matches = [a for a in available if any(p in a for p in PREFERRED)]
if matches:
    MODEL = random.choice(matches)
elif available:
    MODEL = available[0]   # none of the three is available; use the first
else:
    raise SystemExit(
        "No model could be selected. Set one manually, e.g.\n"
        "    MODEL = 'llama3.1'\n"
        "then re-run."
    )

print(f"Using model: {MODEL}  (picked at random)")
if available:
    print(f"Your key can use {len(available)} model(s). Here are the first eight:")
    for a in available[:8]:
        print(f"   - {a}")'''


def first_call_cell():
    return r'''resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain what an API is, in one sentence."}],
)
print("\n--- MODEL SAYS ---")
print(resp.choices[0].message.content)
print(f"\n(tokens used: {resp.usage.total_tokens if resp.usage else '?'})")'''


def settings_section():
    md = """### Try a setting: `temperature`

The API has small controls, often called *settings* or *knobs*, that change how the model answers. `temperature` is a good first one to try: `0` asks for the most consistent wording the model can give, while larger values usually make the wording more varied.

Run the cell below a few times. Then change `temperature` to `0`, `0.7`, or `1.0` and compare what happens."""
    code = r'''for temp in [0, 0.7, 1.0]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Give me a friendly one-sentence definition of an API."}],
        temperature=temp,
    )
    print(f"temperature={temp}")
    print(resp.choices[0].message.content)
    print()'''
    return [nbformat.v4.new_markdown_cell(md), nbformat.v4.new_code_cell(code)]


def build_data_cell():
    abstracts = json.loads((ROOT / "episodes/data/research_abstracts.json").read_text())
    data_json = json.dumps(abstracts, indent=2)
    return f'''import json

ABSTRACTS = {data_json}

print(f"Loaded {{len(ABSTRACTS)}} abstracts:")
for i, a in enumerate(ABSTRACTS, 1):
    print(f"  {{i:2d}}. [{{a['field']}}] {{a['title'][:70]}}")'''


def rewrite_cells(cells):
    rewritten = []
    inserted_settings = False
    for cell in cells:
        source = cell.source
        if cell.cell_type == "markdown" and "### Try a setting: `temperature`" in source:
            inserted_settings = True
        if cell.cell_type == "code" and "# --- Pick a model at random" in source and "# --- The first request" in source:
            rewritten.append(nbformat.v4.new_code_cell(model_selection_cell()))
            rewritten.append(nbformat.v4.new_code_cell(first_call_cell()))
            rewritten.extend(settings_section())
            inserted_settings = True
            continue
        if cell.cell_type == "code" and "ABSTRACTS = [" in source and "# ... 11 more abstracts" in source:
            rewritten.append(nbformat.v4.new_code_cell(build_data_cell()))
            continue
        rewritten.append(cell)
    if not inserted_settings:
        raise RuntimeError("Could not find the episode 2 first-call cell to split")
    return rewritten


def main():
    nb = nbformat.v4.new_notebook()
    nb.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        }
    )

    cells = [
        nbformat.v4.new_markdown_cell(
            "# Using an API to Communicate with a Model\n\n"
            "This notebook follows the rendered lesson episodes in order. "
            "Run the cells from top to bottom."
        )
    ]

    for episode in EPISODES:
        text = (ROOT / "episodes" / episode).read_text()
        metadata, text = split_yaml(text)
        title = metadata.get("title", episode)
        cells.append(nbformat.v4.new_markdown_cell(f"## {title}"))
        text = inline_reference_links(clean_carpentries_fences(remove_instructor_blocks(text)))
        cells.extend(markdown_to_cells(text))

    nb.cells = rewrite_cells(cells)
    nbformat.validate(nb)

    for i, cell in enumerate(nb.cells, 1):
        if cell.cell_type == "code" and not cell.source.lstrip().startswith("%"):
            ast.parse(cell.source, filename=f"cell-{i}")

    out = ROOT / "episodes/data/talking_to_a_model.ipynb"
    out.write_text(json.dumps(nb, indent=1))
    print(f"wrote {out} ({len(nb.cells)} cells)")


if __name__ == "__main__":
    main()
