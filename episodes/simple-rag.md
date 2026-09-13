---
title: "A Simple RAG Example"
teaching: 15
exercises: 6
---

:::::::::::::::::::::::::::::::::::::: questions

- How do I make a model answer from *my* documents?
- Why does a vector database find the right paper even when no words match?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Explain retrieval-augmented generation (RAG) in one sentence.
- Store the 12 abstracts in a vector database and search them by meaning.
- Put the retrieved passages into the prompt so the model answers from them.

::::::::::::::::::::::::::::::::::::::::::::::::

## What RAG is

So far the model has answered from what it saw in its training data. With
**RAG** (**R**etrieval-**A**ugmented **G**eneration) you hand it the source
text *with the question* and ask it to answer from that text. The idea has
two steps:

1. **Retrieve** — find the documents (or passages) most relevant to the
   question.
2. **Generate** — ask the model to answer using only the passages you found.

Production systems (like Purdue's AnvilGPT) do the retrieving with a **vector
database**: a store that finds text by *meaning*. This episode builds one for
real, over the 12 abstracts from the *Build the research tool* episode, using
[ChromaDB](https://www.trychroma.com) — an open-source vector database that
installs with one `pip`.

You need `ABSTRACTS`, `client`, and `MODEL` from the earlier episodes, so run
*Build the research tool* (or the notebook's section 3a) first.

## Step 1 — Store: put the abstracts in a vector database

First install the library. On Anvil, re-run this cell after every server
restart — installed packages do not survive the session. The first install
takes a minute or two; it is worth the wait.

```python
%pip install chromadb
```

An **embedding** is a list of numbers that represents what a piece of text
*says*. Texts about similar things get similar numbers, so a paper about
"urban air pollution" lands near a question about "city air quality" even
though the words share nothing. A **vector database** stores one embedding
per document and returns the closest ones to whatever you query with.

```python
import chromadb
from chromadb.config import Settings

chroma = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
collection = chroma.get_or_create_collection("abstracts")

if collection.count() == 0:   # add only once; re-running the cell is safe
    collection.add(
        documents=[a["abstract"] for a in ABSTRACTS],
        metadatas=[{"title": a["title"], "field": a["field"]} for a in ABSTRACTS],
        ids=[a["id"] for a in ABSTRACTS],
    )
print(collection.count(), "abstracts stored")
```

Three things to notice. `EphemeralClient` keeps everything in memory — it is
gone when the kernel stops, which is exactly right for a lesson. `add()`
embeds each abstract (the first run downloads a small embedding model, about
80 MB, so give it a minute) and stores it with the metadata you attach. And
`ids` must be unique — they are how the database tells documents apart.

## Step 2 — Retrieve: ask by meaning

```python
QUESTION = "Which of these papers uses satellite data, and what is it trying to predict?"
result = collection.query(query_texts=[QUESTION], n_results=3)

for meta, distance in zip(result["metadatas"][0], result["distances"][0]):
    print(f"{distance:.2f}  [{meta['field']}] {meta['title'][:70]}")
```

```output
1.11  [Environmental Science] Urban Air Pollution Forecasting: a Machine Learning Approach leveraging Satelli
1.42  [Environmental Science] Predicting concentration levels of air pollutants by transfer learning and recur
1.51  [Energy] Lasso estimation for GEFCom2014 probabilistic electric load forecasting
```

`distance` is a dissimilarity score: **lower means closer** to the question.
The `title` and `field` come from the metadata you attached in `add()`. Your
distance numbers may differ slightly from the ones shown — they depend on the
embedding model version — but the ranking holds.

## Step 3 — Generate: answer from the passages you found

Now build a prompt that contains (a) an instruction to answer *only* from the
passages, and (b) the passages themselves. Nothing else changes — same
`client`, same `MODEL`, same `create()` call:

```python
def rag_answer(question, k=3):
    result = collection.query(query_texts=[question], n_results=k)
    passages = "\n\n".join(
        f"[{i+1}] ({meta['field']}) {meta['title']}\n{doc}"
        for i, (meta, doc) in enumerate(zip(result["metadatas"][0],
                                            result["documents"][0]))
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
| a ChromaDB collection | a vector database (Chroma, pgvector, FAISS, ...) |
| `collection.add(...)` — embed and store | an ingestion pipeline |
| `collection.query(...)` — nearest passages | the retriever |
| `rag_answer()` — passages + question in the prompt | the same: context in the prompt |

The `generate` step is identical in both. Most of the engineering in RAG
lives in the `retrieve` step — finding the right passages before the model
ever sees the question.

::::::::::::::::::::::::::::::::::::: callout
### Two honest limits

- **The default embedding model is small and general.** It works well here;
  for specialized text (medical jargon, law), pick an embedding model trained
  on that domain.
- **We embed whole abstracts.** Long documents must be split into passages
  (**chunking**) first, and chunk size is a real decision. Our 12 abstracts
  are already short enough.

A plain word-overlap search also works at this size — try it as an exercise
below and compare. The vector database earns its keep when synonyms and
paraphrase start mattering.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: exercises

**Find a match with no shared words.** Query the collection with questions
that use none of the words in any abstract, for example:

```python
for q in ["What do these papers say about air quality in cities?",
          "How can hospitals make MRI scans from different machines comparable?",
          "Which paper predicts electricity demand?"]:
    result = collection.query(query_texts=[q], n_results=1)
    m = result["metadatas"][0][0]
    print(f"{result['distances'][0][0]:.2f}  [{m['field']}] {m['title'][:70]}")
```

The first finds the pollution papers, the second the MRI-harmonization
papers, the third the load-forecasting papers — none of the question words
appear in those titles. That is meaning-based search. **Stretch:** create a
second collection with 5–10 pieces of your own writing (meeting notes, your
lab's SOPs — anything non-sensitive) and query it.
::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- RAG = **retrieve** the relevant passages, then **generate** an answer from
  them.
- A vector database finds text by meaning: embeddings turn text into numbers,
  and similar meaning lands nearby.
- The generate step is the same `create()` call as anywhere else in the
  lesson — the passages just join the prompt.

::::::::::::::::::::::::::::::::::::::::::::::::
