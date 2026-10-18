---
title: "Findings: What Was Proved, Measured, Conjectured, Refuted, and Not Shown"
status: mixed
statusnote: A classification of every formal claim of the book by evidence category, counted from the ledger at build time; the answer to the founding question; and an explicit list of what the book does not claim.
description: The book's results sorted by kind of evidence — classical results restated, statements proved here, measurements, implementation results, conjectures, counterexamples and corrections — with the answer to the founding question in its weak and strong readings, and the novelty assessment.
epigraph: "The most useful sentence in a research report is the one that says what was not found."
---

::: objectives
- Know how many of the book's formal claims fall into each evidence category, and where to find each.
- State the answer to the founding question in its weak and its strong reading.
- Distinguish the book's candidate contributions from its restatements of classical mathematics.
- List what the book does not claim.
:::

## The ledger, counted {#sec:ledger-count}

Every formal statement in this book carries a ledger identifier, and the ledger files are the canonical record (\chapref{c-ledger-guide}). The count below is computed from those files when the book is built:

```python run
import os, re, collections, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
ids = set()
for f in ("RESULTS.md", "DEFINITIONS.md", "COUNTEREXAMPLES.md", "HYPOTHESES.md", "OPEN_PROBLEMS.md", "EXPERIMENTS.md"):
    ids |= set(re.findall(r"GIN-[A-Z]+-\d+", open(os.path.join(ROOT, f), encoding="utf8").read()))
kinds = collections.Counter(i.split("-")[1] for i in ids)
names = {"DEF": "definitions", "HIST": "classical results (historical)", "THM": "theorems", "PROP": "propositions",
         "COR": "corollaries", "REI": "reinterpretations", "OBS": "empirical observations", "IMP": "implementation results",
         "EXP": "experiments", "H": "hypotheses", "CONJ": "conjectures", "NEG": "counterexamples", "REJ": "rejected hypotheses",
         "OPEN": "open problems"}
for k in names:
    print(f"{names[k]:32s} {kinds.get(k, 0):4d}")
text = open(os.path.join(ROOT, "RESULTS.md"), encoding="utf8").read()
heads = re.findall(r"^### (GIN-(?:PROP|THM|COR)-\d+).*?\*\((.*?)\)\*", text, re.M)
here = sum(1 for _, s in heads if "proved here" in s)
print(f"\nof {len(heads)} propositions/theorems/corollaries: {here} with a proof written here, {len(heads) - here} classical or packaged")
```

```output
definitions                        45
classical results (historical)     19
theorems                            7
propositions                       54
corollaries                         1
reinterpretations                  11
empirical observations             22
implementation results              8
experiments                        15
hypotheses                         42
conjectures                         1
counterexamples                    25
rejected hypotheses                 4
open problems                      13

of 62 propositions/theorems/corollaries: 15 with a proof written here, 47 classical or packaged
```

The counts are deliberately unflattering in one respect: "proved here" means that the proof was written by this project and checked on small cases by computation — not that the statement is new. Most such statements are elementary, and several are almost certainly folklore (\ledger{GIN-REI-010}, \ref{sec:novelty}).

## Findings by kind of evidence {#sec:by-kind}

| kind | representative findings | where |
|---|---|---|
| **classical, restated** | Dedekind's categoricity; the recursion theorem; Euclid, Lamé, Bézout; Fermat, Euler, Wilson, Korselt; Karatsuba's bound; Miller–Rabin's error bound | Ch. 3–4, 14–15, 30–35 |
| **proved here (elementary)** | numerals as operation expressions and zero's empty address (\ledger{GIN-PROP-002}); the converse of a homomorphism and the none/one/many classification (\ledger{GIN-THM-007}); fractions as pairs and the null pair (\ledger{GIN-THM-006}); the CGT heap as shifted bijective binary (\ledger{GIN-PROP-006}); a test-free divider returns all ones on zero (\ledger{GIN-PROP-023}); unique quotients characterize integral domains (\ledger{GIN-PROP-065}); the binary-gcd iteration bound (\ledger{GIN-PROP-076}) | Ch. 5–9, 16–18, 22, 33 |
| **reinterpretations** | inverse operations as converse relations; number constructions as admissibility repairs; carry-lookahead as CGT compilation | Ch. 9, 13, 27, 38 |
| **implementation results** | an IEEE 754 simulator matching x86-64 results and all five flags on 80,600 cases (\ledger{GIN-IMP-001}); machine models agreeing with seven toolchains and with QEMU (\ledger{GIN-IMP-002}, \ledger{GIN-IMP-008}); gate-level circuits verified exhaustively | Ch. 22, 24–25 |
| **measurements** | seven toolchains disagree on `1/0` and `INT_MIN/-1`; clang deletes a post-division zero test, gcc keeps it (\ledger{GIN-OBS-008}); the host detects tininess after rounding, QEMU-AArch64 before (\ledger{GIN-OBS-009}, \ledger{GIN-OBS-018}); contract models predict every covered real execution (\ledger{GIN-OBS-017}); classical cost exponents reproduced by counted operations (\ledger{GIN-OBS-022}) | Ch. 23–26, 37, 39 |
| **counterexamples** | float addition is not associative; Fermat pseudoprimes; exponent reduction without a unit (\ledger{GIN-NEG-024}); unit-cost multiplication (\ledger{GIN-NEG-025}); principal roots are not multiplicative | throughout |
| **corrections of this project's own errors** | exponents evaluated inside $\Z/n$; signaling NaNs ignored; a division-overflow misclassification; stale experiment records | RESULTS §J, §L |
| **conjecture** | re-association as a sixth CGT mechanism (\ledger{GIN-CONJ-001}) | Ch. 37–38 |

## The founding question {#sec:answer}

Chapter 1 asked whether numerical objects, operations, representations and algorithms can be understood as computational grammars whose admissible transitions, semantics, representations and costs can be formally specified and experimentally validated.

**The weak reading — can arithmetic be described this way? — is answered yes.** Every operation in the book has a statement of its domain, admissibility, outcome classes, representation, algorithm and cost; every failure studied is classified by the layer at which it occurs and by the condition that fails; and the description is executable and validated against independent oracles (hardware, compilers, an emulator, Python's integers).

**The strong reading — does the description yield new mathematics, faster algorithms or better predictions? — is answered mostly no, with one qualified yes.** No new theorem of number theory, no new algorithm and no new complexity bound was found; the measured costs reproduce textbook exponents. The qualified yes is predictive: on GIN-EXP-013, explicit contract models predicted the behaviour of seven real toolchains in every covered case where naive "mathematical" predictors failed on a quarter or more of the cases (Chapter 39). That result validates the models' coverage of published specifications; it is not an independent discovery, and the AI-only comparison was not run.

## Novelty, honestly {#sec:novelty}

The candidate contributions are a **framing** — arithmetic as computational grammars with four separable layers and converse admissibility — a **vocabulary of failure** (no solution versus non-unique; image versus kernel), **executable reference semantics** with tests, and **reproducible measurements of real machines**. The statements most likely to be absent from the literature reviewed are elementary: the heap/bijective-binary conjugacy and the pair-level characterization of indeterminate forms. Their novelty has not been verified against primary sources or by outside review, and no priority is claimed for them or for anything else in this book (\ledger{GIN-OPEN-005}).

::: boundary
**This book does not claim:** a new theorem of number theory; a new or faster algorithm; a new complexity bound or lower bound; that any behaviour measured on one x86-64 host holds elsewhere; that QEMU results describe physical AArch64 or RISC-V processors; anything about the performance of AI systems; peer review, institutional affiliation or endorsement; that "proved here" means "new".
:::

::: exercise {#ex:find-classify}
Choose three formal items from Chapters 16–18 and classify each as classical, proved here, reinterpretation or counterexample, giving the reason from its status badge and ledger entry.
:::

::: exercise {#ex:find-strong}
Propose one experiment whose positive outcome would move the strong reading of the founding question from "mostly no" toward "yes", and state in advance what result would count against it.
:::

::: summary
- The ledger, counted at build time, separates classical results, statements proved here, reinterpretations, measurements, implementation results, counterexamples, conjectures and open problems.
- Weak reading of the founding question: established. Strong reading: no new theorems, algorithms or bounds; one qualified predictive result whose limits are stated.
- The candidate contributions are a framing, a vocabulary, executable semantics and measurements; novelty of individual statements is unverified and not claimed.
:::
