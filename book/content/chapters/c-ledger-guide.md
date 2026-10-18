---
title: "A Guide to the Research Ledger"
status: definition
statusnote: How the book's claims are recorded, numbered and classified, and how to trace any statement to its evidence.
description: The ledger files, the identifier namespaces, the ladder of claims, and how a reader can follow any formal statement in the book to its proof, check, experiment or citation.
---

## Why a ledger {#sec:ledger-why}

A book of this kind makes several hundred formal statements of very different standing: classical theorems, new proofs of elementary facts, measurements on one machine, emulator results, conjectures. The **research ledger** — a set of plain-text files at the root of the repository — is the canonical record of every one of them. The book cites the ledger; it does not replace it. When the two disagree, the ledger is corrected, and the correction is recorded rather than overwritten.

## The files {#sec:ledger-files}

| file | contents |
|---|---|
| `RESULTS.md` | propositions, theorems, historical results, reinterpretations, observations, implementation results, conjectures, corrections |
| `DEFINITIONS.md` | every definition, marked standard, classical or provisional |
| `HYPOTHESES.md` | hypotheses with their status (open, supported, established, rejected) |
| `COUNTEREXAMPLES.md` | counterexamples and rejected hypotheses |
| `EXPERIMENTS.md` | experiment protocols: design, falsification criterion, result, limitations |
| `OPEN_PROBLEMS.md` | open problems |
| `PROVENANCE.md` | who contributed what, and the status of each result relative to prior work |
| `DECISION_LOG.md` | dated methodological decisions |
| `LITERATURE_REVIEW.md` | prior work by area |
| `CGT_CONCEPT_MAP.md` | the relation to Computational Grammar Theory |
| `PUBLICATION_STATUS.md`, `EDITION_HISTORY.md` | the state of this edition and its history |
| `AUDIT_2026-10.md` | the October 2026 reproduction audit |

## Identifiers {#sec:ledger-ids}

| prefix | kind |
|---|---|
| `GIN-DEF` | definition |
| `GIN-THM`, `GIN-PROP`, `GIN-COR` | theorem, proposition, corollary (proved here or classical; the entry says which) |
| `GIN-HIST` | historical (classical) result, cited |
| `GIN-REI` | reinterpretation of a known fact |
| `GIN-OBS` | empirical observation |
| `GIN-IMP` | implementation result |
| `GIN-EXP` | experiment |
| `GIN-H` | hypothesis |
| `GIN-CONJ` | conjecture |
| `GIN-NEG`, `GIN-REJ` | counterexample, rejected hypothesis |
| `GIN-OPEN` | open problem |
| `GIN-D` | decision |
| `NUM-…` | the separate research lane *The Number* (not part of this edition's claims) |
| `CGT-…` | the separate Computational Grammar Theory publication |

Identifiers are never reused. A withdrawn claim keeps its identifier and gains a correction.

## The ladder of claims {#sec:ledger-ladder}

Each entry carries exactly one category, and no category is silently promoted to another: a visualization is not a proof, a benchmark is not a theorem, a new notation is not a new theory, a reinterpretation is not a new result, and an implementation is not an algorithmic improvement. "Proved here" means a proof is written in the ledger and its exact statement is checked on small cases by `experiments/check_theorems*.py`; it says nothing about novelty, which is assessed separately in `PROVENANCE.md` and Chapter 41.

## Following a statement to its evidence {#sec:ledger-follow}

Every formal environment in the book shows its status badge and ledger identifier. The identifier links to the ledger page on the website, where the entry gives the proof or its citation, the name of the check in `experiments/check_theorems*.py`, the experiment that measured it and the chapter that uses it. The build fails if a chapter cites an identifier that the ledger does not contain, if a citation key is missing from the bibliography, or if a cross-reference does not resolve.
