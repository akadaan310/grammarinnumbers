# THE NUMBER — integration plan (Phase 3 proposal)

Status: **proposal**. What is already done is marked ✅. Nothing here is deployed. Promoting anything to production remains a decision for a human.

## 1. What is integrated now (conservative)

- ✅ **A separate research lane.** It lives in `research/the-number/`, with its own identifiers (`NUM-*`), runner, results and tests. It is not part of `experiments/run_all.sh` and adds no claims to edition 1.0.
- ✅ **A website page for the lane**, `the-number.html`, outside the chapter sequence, with four labs:
  - `num-zero`: the zero/empty/absent probes, run in the reader's own JavaScript engine;
  - `num-translate`: fourteen numeration systems side by side;
  - `num-spatial`: the two-channel layout grammar, a Maya-style comparator, and digit order rendered by the browser;
  - `num-fibers`: converse classes under reduction Z/m → Z/k.

  Every computed result comes from `num-core.js`. `npm test` checks it against fixtures exported from `numlab`: canonical words, converse profiles, transfer matrices, channel tables and Maya layouts. Stored results are labelled as such and name their file.
- ✅ **The status page** links to the lane and says that its results are not claims of the edition.
- ✅ **One correction flowed back into the edition**: C-006, the SDK accepting non-ASCII digits (see `RESULTS.md` §L). This is the only change the lane made to edition material.

## 2. Proposed: a "Chapter 0" without renumbering

The proposal is an unnumbered prologue, `0-the-number.md`, titled **"Before the Number: Distinction, Substrate, Translation"**. It would be built as a page linked from the contents before Chapter 1, and it would not shift any chapter number, label or cross-reference.

Proposed contents:
1. The schema 𝒩 as a modelling definition.
2. The seven layers as a reading guide that maps to existing chapters:
   - identity → Chapter 2, layer 2;
   - state → Chapters 16–18;
   - operation → Chapter 9;
   - temporal → Chapters 5–7;
   - topology → Chapter 7 and the heap;
   - machine → Chapters 23–26;
   - meta → Chapter 39.
3. The four NUM experiments, presented as worked examples.

**Gate for promotion.** Each NUM item quoted in the prologue must first be entered in the edition ledger with a status badge, and the build must be able to check it. That means extending `ledger_ids` to the `NUM-` prefix, or quoting only results that already carry GIN identifiers.

**Not proposed:** renumbering chapters, moving chapters, or renaming the book, the SDK or the repository.

## 3. Title decision (for Abed Kadan)

| option | what changes | evidence for | evidence against |
|---|---|---|---|
| **A. Retain** *Grammar in Numbers* | nothing | edition 1.0 is complete and internally consistent; the lane has produced no result that changes the book's thesis | — |
| **B. Dual title**: *Grammar in Numbers*, with *THE NUMBER — From Distinction to Computation* as the title of the lane or a Volume 0 | the lane page and the prologue carry the second title | keeps continuity; lets the lane grow its own identity if later results justify it | two titles need careful wording on the cover and in the metadata |
| **C. Rebrand** to *THE NUMBER* | book title, site, PDF and metadata (the repository and SDK names would stay) | a broader reader-facing title | NUM-HYP-010 is open and currently negative; the lane's results so far are classical confirmations and software measurements, so a rebrand would let a title outrun the evidence |

**Recommendation: B.** Use the dual title, keep the book's title as it is, and use *THE NUMBER* for the lane and a possible Volume 0. Revisit option C only if NUM-HYP-010 produces a positive result.
