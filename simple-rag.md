---
title: "A Simple RAG Example"
teaching: 14
exercises: 6
---

:::::::::::::::::::::::::::::::::::::: questions

- How do I make a model answer using *my* documents instead of its training data?
- How much of RAG is really about searching for the right text?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Explain retrieval-augmented generation (RAG) in one sentence.
- Write a keyword search that finds the most relevant abstracts for a question.
- Put the retrieved text into the prompt so the model answers from it.

::::::::::::::::::::::::::::::::::::::::::::::::

## What RAG is

So far the model has answered from what it saw in its training data. With
**RAG** (**R**etrieval-**A**ugmented **G**eneration) you give it the source text
*with the question*, and ask it to answer from that text. The idea splits into
two steps:

1. **Retrieve** — find the documents (or passages) most relevant to the
   question.
2. **Generate** — ask the model to answer using only the passages you found.

Production systems (like Purdue's AnvilGPT) do the retrieval with *vector
search* — they turn text into numbers and compare those. That is a whole
subject of its own. For one folder of 12 short abstracts, a plain keyword
search retrieves well, and you can see every line of the logic. That is the
point of this episode: RAG is mostly the **retrieve** step, and the
**generate** step is the exact same `chat.completions.create` call you already
know.

We reuse the 12 abstracts from the *Build the research tool* episode, so run
that episode (or the notebook's section 3a) first.

## Step 1 — Retrieve: find the relevant abstracts

The whole trick: count how many meaningful words from the question appear in
each document, and rank the documents by that count. Words like *the*, *and*,
*what* carry no information, so we drop them first. Words that appear in a
**title** count twice, because titles name the topic.

```python
import re

# Short, common words that carry little information on their own.
STOPWORDS = set("""a an the and or of to in for with is are was were be been
this that these those we our you your it its as by on at from into about
what which who when where how can could would should may might do does did
paper papers study studies result results method approach propose proposes
show shows using used use new based here more also other such than then
them they their there here have has had not no but if while""".split())

def terms(text):
    """Lower-case words of 3+ letters, with stopwords removed."""
    return [t for t in re.findall(r"[a-z]{3,}", text.lower()) if t not in STOPWORDS]

def retrieve(question, k=3):
    """Return the k abstracts that share the most words with the question."""
    q = terms(question)
    scored = []
    for i, rec in enumerate(ABSTRACTS):
        title = terms(rec["title"])
        body = terms(rec["abstract"])
        score = 0
        for t in q:
            if t in title:
                score += 2
            if t in body:
                score += 1
        scored.append((score, i, rec))
    scored.sort(key=lambda item: -item[0])
    return scored[:k]
```

Run a question and look at what comes back:

```python
QUESTION = "Which of these papers uses satellite data, and what is it trying to predict?"
top = retrieve(QUESTION)
for score, i, rec in top:
    print(f"{score:2d}  [{rec['field']}] {rec['title'][:70]}")
```

The satellite paper should be first: *satellite* and *forecast* appear in its
title and abstract, so it outranks the rest. Try another question — the
scorer is dumb, but for a small set of texts it is good enough, and every
line is something you can read and change.

## Step 2 — Generate: answer from the passages you found

Now build a prompt that contains (a) an instruction to answer *only* from the
passages, and (b) the passages themselves. Nothing else changes — same client,
same `MODEL`, same `create()` call:

```python
def rag_answer(question, k=3):
    retrieved = retrieve(question, k)
    passages = "\n\n".join(
        f"[{i+1}] ({rec['field']}) {rec['title']}\n{rec['abstract']}"
        for score, i, rec in retrieved
    )
    prompt = (
        "Answer the question using ONLY the passages below. Cite the passage "
        "number(s) [1], [2], ... for each claim. If the passages do not contain "
        "the answer, say so.\n\n"
        f"Question: {question}\n\nPassages:\n{passages}"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content

print(rag_answer(QUESTION))
```

You should get an answer that names the satellite paper and says what it
predicts, with citations like `[1]`.

### What you just built

That is a real, if tiny, RAG pipeline. The pieces map directly onto the big
systems:

| This episode | A production RAG system |
|---|---|
| `retrieve()` — count matching words | vector search over embedded passages |
| the 12 abstracts | a document store (files, a database) |
| `rag_answer()` — passages + question in the prompt | the same: context in the prompt |
| "answer using ONLY the passages" | grounding + citation instructions |

The `generate` step is identical in both. Almost all of the engineering in RAG
lives in the `retrieve` step — finding the right text, and only that text,
before the model ever sees the question.

::::::::::::::::::::::::::::::::::::: callout
### Two honest limits of keyword retrieval

- **Synonyms miss.** A question that says *pollution* will not match a paper
  that only says *air quality*. Bigger systems embed words into vectors so
  near-synonyms land near each other.
- **It scales down, not up.** Counting words is fast for 12 texts. For 12
  million, you need the index a vector database builds.

For a small corpus of your own notes or papers, this keyword version is a
legitimate tool — and a good first step.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::: exercises

**Try it on your own text.** Replace `ABSTRACTS` with a list of 5–10
dictionaries you write yourself (each with a `title` and `body` string —
meeting notes, your lab's SOPs, anything non-sensitive), then reuse
`retrieve` and `rag_answer` on them. What question does the keyword scorer
get wrong, and why?
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::: keypoints

- RAG = **retrieve** the relevant passages, then **generate** an answer from
  them.
- For a small corpus, a keyword search (drop stopwords, weight the title)
  retrieves well enough to be useful.
- The generate step is the same `create()` call as anywhere else in the
  lesson — the passages just join the prompt.

::::::::::::::::::::::::::::::::::::::::::::::::
