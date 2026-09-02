# Dataset — research_abstracts.json

12 real, publicly-available arXiv abstracts (2 per field, 6 fields), used as the
hands-on input for the "batch-process a list → structured CSV" pattern.

- **Source:** arXiv open API (`export.arxiv.org/api/query`), fetched 2026-08-28.
- **Fields:** `field`, `title`, `abstract`, `arxiv_id`.
- **Size:** ~1,900 words total — small on purpose. A 12-call batch finishes in
  30–90 s, which fits the 75-min slot.

## Fields covered
Machine Learning (CS) · Biology · Materials Science · Environmental Science ·
Medicine / Health · Energy

## Provenance (arXiv IDs)
| # | Field | arXiv ID |
|---|---|---|
| 1 | Machine Learning (CS) | 2307.05639v2 |
| 2 | Machine Learning (CS) | 1901.06610v2 |
| 3 | Biology | 1711.08927v2 |
| 4 | Biology | 1801.04087v2 |
| 5 | Materials Science | 1506.09003v1 |
| 6 | Materials Science | 1711.03818v2 |
| 7 | Environmental Science | 2502.01654v1 |
| 8 | Environmental Science | 2405.19901v1 |
| 9 | Medicine / Health | 2102.06315v2 |
| 10 | Medicine / Health | 2007.09465v2 |
| 11 | Energy | 1603.01376v1 |
| 12 | Energy | 2302.12168v2 |

## Notes for the instructor
- These abstracts are **embedded in the notebook** (`03_notebook_talking_to_a_model.ipynb`,
  Section 3a), so participants never need to download this file. This file is the
  editable source-of-truth if you want to swap in different abstracts or your own
  institution's papers before the workshop.
- To swap the data: edit this JSON, then re-run `_gen_notebook.py` to regenerate the
  notebook. (Keep it to ~10–15 abstracts / ~2,000 words to stay inside the slot.)
- All are public scientific abstracts — safe to send to the gateway. When you later
  let participants use *their own* data (Experiment 4), the governance note applies.
