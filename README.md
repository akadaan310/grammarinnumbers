# Grammar in Numbers

**Arithmetic, Number Theory, and the Computational Grammar of Number**

Founding Principal Researcher: **Abed Kadan**. Parent research program: [Computational Grammar Theory](https://github.com/akadaan310/computationalgrammartheory) (CGT), used here as a read-only reference corpus.

An independent **research monograph** (not peer reviewed) that asks: *what is the computational grammar of number?* For every arithmetic expression it asks what the objects, symbols, states, admissible operations and transitions are, what is preserved, what it costs in bit operations, what machinery implements it, and — when an expression asks for a transition the grammar does not admit — exactly *which* condition fails.

## State of this branch (2026-10-17)

- **Book:** first complete edition (1.0) — 42 chapters and 3 appendices, a website and a print edition generated from the same sources. Strict build, 121 executed examples, laboratory-vs-SDK tests and link check pass. Print edition: `book/site/downloads/grammar-in-numbers.pdf` (page count, SHA-256 and content version in `pdf.json`). The website is **not deployed**.
- **SDK:** `ginsdk` 1.0 (Python, standard library only), 74 tests.
- **Evidence:** experiments EXP-001 – 015 and 33 exhaustive theorem checks, re-run in a clean environment by the October 2026 audit (`AUDIT_2026-10.md`).
- **Status and limits:** `PUBLICATION_STATUS.md`; history: `EDITION_HISTORY.md`. The 53-page PDF of 2026-10-08 was a compilation of the research ledger, not this book; it is archived unchanged in `archive/`.
- **Research frontier:** *The Number* — a separate, falsifiable research lane in `research/the-number/` (identifiers `NUM-*`), not part of the edition's claims.

## Findings in brief (details: `RESULTS.md`, book Chapter 41)

- **Numerals are programs**: a positional numeral is a word of moves x ↦ b·x + d applied to 0; zero's canonical numeral is the empty word (GIN-PROP-002); CGT's heap numeration is bijective binary shifted by one (GIN-PROP-006).
- **Inverse operations are converses, and "undefined" has two kinds**: solutions of b·c = a in a commutative ring are empty or a coset of Ann(b) (GIN-THM-001); 1/0 fails the image condition, 0/0 the kernel condition, and 0/1 = 0 passes both.
- **Every way of giving 1/0 a value gives something up** (GIN-THM-003/004); with fractions as pairs, every indeterminate form computes the null pair (0, 0) (GIN-THM-006).
- **Machines disagree, measurably**: seven toolchains on one host answer 1/0 in seven ways; clang deletes a post-division zero test, gcc keeps it; an IEEE 754 simulator matches the CPU's results and flags on 80,600 cases.
- **Contract models predict real execution** in every covered case where naive "mathematical" predictors fail on a quarter of cases (EXP-013) — a validation of coverage, not an independent discovery; the AI-only baseline was not run.
- **What is new?** A framing, a vocabulary of failure, executable semantics and measurements — not new theorems, algorithms or complexity results. No priority is claimed.

## Navigate
`AUDIT_2026-10.md` · `PUBLICATION_STATUS.md` · `EDITION_HISTORY.md` · `RESEARCH_CHARTER.md` · `PROVENANCE.md` · `CGT_CONCEPT_MAP.md` · `DEFINITIONS.md` · `NUMBER_GRAMMAR.md` · `ARITHMETIC_GRAMMAR.md` · `FORMAL_MODELS.md` · `MACHINE_MODEL.md` · `NUMBER_THEORY.md` · `HYPOTHESES.md` · `EXPERIMENTS.md` · `RESULTS.md` · `COUNTEREXAMPLES.md` · `LITERATURE_REVIEW.md` · `OPEN_PROBLEMS.md` · `BOOK_OUTLINE.md` · `DECISION_LOG.md`

## Reproduce
```sh
# SDK (Python ≥ 3.10, standard library only)
cd sdk && PYTHONPATH=src python3 -m unittest discover -s tests

# All experiments, theorem checks and the summary (≈ 1.5 min; EXP-004/005 need gcc, optionally clang, java, rustc, go, node)
sh experiments/run_all.sh && cat experiments/results/SUMMARY.md
python3 experiments/verify_reproduction.py      # re-run and compare counted fields

# The book and website (Node ≥ 18)
cd book && npm ci && npm run verify              # strict build + JS tests + executed examples + link check
npm run pdf && npm run build                     # print edition with release checks, then rebuild
npm run serve                                    # http://localhost:8080 (local only)
```

## Layout
`sdk/` the `ginsdk` package and tests · `experiments/` scripts, machine sources, JSON results · `book/content/` chapters, glossary, bibliography · `book/tools/` build, checks · `book/site/` styles and the laboratory's JavaScript · `book/tests/` lab-vs-SDK fixture tests.
