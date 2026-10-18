# Publication status

**Content version** `{{content_version}}` · **source build** `{{build}}` · **print edition** {{pdf_pages}} pages ([PDF]({{pdf_link}})).

## What this is

*Grammar in Numbers* is a **research monograph by Abed Kadan**, published as a website and a print edition generated from the same sources. It is **not peer reviewed**, is not a textbook endorsed by any institution, and claims no university affiliation. It was developed with an AI research assistant (Claude); the contribution of each party is recorded in the [provenance record](ledger/provenance.html). The AI assistant is not an author.

## Completeness

| item | state |
|---|---|
| numbered chapters planned / present | 42 / {{stat_chapters}} |
| appendices planned / present | 3 / {{stat_appendices}} |
| theorems, propositions, lemmas, corollaries | {{stat_results}} |
| definitions and axioms | {{stat_defs}} |
| observations and implementation results | {{stat_obs}} |
| counterexamples | {{stat_neg}} |
| conjectures and open problems | {{stat_open}} |
| bibliography entries (all cited) | {{stat_refs}} |
| executed examples (all reproduce their printed output) | {{stat_examples}} |

## Evidence classes

- **Proved here**: proofs written in this book and checked by computation on small cases; not externally reviewed; not claims of novelty.
- **Classical**: cited results of the literature.
- **Measured**: on one x86-64 Linux host with named toolchains (Appendix B).
- **Emulated**: AArch64 and RISC-V under QEMU user mode 8.2.2 — not physical hardware.
- **Specified**: taken from a standard or architecture manual, not executed.

## Verification of this build

The October 2026 audit re-ran every test, experiment and check in a clean environment (`AUDIT_2026-10.md`): SDK tests, all experiment results (counted fields identical to the recorded ones), both theorem checkers, the laboratory-versus-SDK fixture tests, every executed example, and the internal link check. The build fails on any LaTeX error, unresolved reference, unknown citation or ledger identifier, missing exercise, objective or summary, or placeholder text.

## Known issues and limits

- Not peer reviewed; the novelty of the two candidate statements (GIN-PROP-006, the pair form of GIN-THM-006) is unverified (Chapter 41).
- Machine claims cover one host and one version of each toolchain; AArch64 and RISC-V results are emulated (GIN-OPEN-012).
- The AI-only baseline of GIN-EXP-013 was not run (GIN-OPEN-013).
- The website edition is built and tested locally; **it is not deployed** by this build, and no online address is claimed for it.
- Wall-clock timings are host-specific and secondary; no asymptotic claim rests on them.

## Research lane: THE NUMBER

A separate research lane, *THE NUMBER — From Distinction to Computation* (identifiers `NUM-*`), studies what must be fixed before two notations, data types or machines can be said to denote "the same number". Its results are **not** claims of this edition. It has its own [page and laboratories](the-number.html) and its foundations and falsification matrix are in `research/the-number/`. So far its results confirm classical mathematics on small cases and record measured software behaviour. It has also found one defect in this edition's SDK, which is now corrected (C-006).

## History

See the [edition history](edition.html) and `EDITION_HISTORY.md`.
