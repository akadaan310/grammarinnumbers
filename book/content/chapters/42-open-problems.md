---
title: "Open Problems"
status: open
statusnote: Each problem is stated with what would settle it, what would count against the hypothesis behind it, and how to reproduce the current state. Priorities are the research program's judgement, not results.
description: The research frontier of the book, prioritized — each problem with its motivation, a falsifier or decision criterion, the literature to check first, and the commands that reproduce the current evidence.
epigraph: "An open problem is a promise about what would change our minds."
---

::: objectives
- Know the open problems of the program in priority order, and which are mathematical, empirical or bibliographic.
- For each, know what result would settle it and what result would count against the hypothesis behind it.
- Know how to reproduce the evidence each problem starts from.
:::

## How the problems are stated {#sec:how-stated}

A problem enters this list only when it can be stated so that someone else could work on it: a precise question, the result that would answer it, a **falsifier** (an outcome that would count against the hypothesis motivating it), the literature to read *first* — most questions about arithmetic have been asked before — and a reproduction path. The priorities reflect how much a solution would change the book's conclusions (Chapter 41).

## Priority 1: questions that could change the conclusions {#sec:p1}

**Novelty of the candidate statements** (\ledger{GIN-OPEN-005}). *Question:* are the heap/bijective-binary conjugacy (\ledger{GIN-PROP-006}) and the pair-level characterization of indeterminate forms (\ledger{GIN-THM-006}) stated in the literature? *Settled by:* a primary-source search of numeration systems, automatic structures, wheels and projective arithmetic, and outside review. *Falsifier for novelty:* an earlier statement of either — which would make it a classical result restated, and would be recorded as such. *Start with:* \cite{carlstrom2004} for the null pair; \cite{knuth1997} §4.1 and \cite{blumensath2000} for numerations.

**An AI-only baseline for execution prediction** (\ledger{GIN-OPEN-013}). *Question:* how accurately does a language model, without tools and then with `python3 -m ginsdk inspect`, predict the outcomes of the 845 operations × 7 toolchains of GIN-EXP-013? *Settled by:* the same corpus and scoring, with prompts, model versions and repeated samples recorded. *Falsifier for the usefulness of contracts as an AI interface:* tool-free accuracy matching the contract models', or no improvement when the tool is available. *Reproduce:* `python3 experiments/exp013_execution_prediction.py`.

**Hardware confirmation of emulated results** (\ledger{GIN-OPEN-012}). *Question:* do physical AArch64 and RISC-V processors behave as their QEMU emulations did for division by zero, $\mathrm{INT\_MIN}/-1$, and floating-point tininess? *Falsifier for the models:* any disagreement between a physical processor and its SDK model. *Reproduce:* the freestanding test program is `experiments/machine/isa_div.c`; `experiments/exp014_isa_emulation.py` currently always runs it under QEMU, so a hardware run needs the program compiled and executed natively on the target and its output compared field by field with `experiments/results/exp014.json`.

## Priority 2: mathematical structure {#sec:p2}

**A grammar-class hierarchy of arithmetic operations** (\ledger{GIN-OPEN-001}). *Question:* place gcd, modular exponentiation with variable modulus, integer square root and base conversion in a precise hierarchy of automata and transducer classes, related to bit complexity. *Known:* addition is synchronous rational and multiplication is not (\ledger{GIN-THM-005}). *Start with:* \cite{buchi1960,cobham1969,khoussainov1995,blumensath2000}. *Decision criterion:* a table in which every entry is a theorem with a citation or a proof.

**The cost of admissibility** (\ledger{GIN-OPEN-002}). *Question:* when is deciding whether a converse problem has a solution asymptotically cheaper than solving it? Divisibility costs a division; unit-ness costs a gcd; quadratic residuosity modulo a prime costs one exponentiation without finding the root; the discrete logarithm is decidable cheaply and believed hard to solve (Chapter 31). *Settled by:* a classification of the book's converse problems by decision and search complexity, with proofs or citations.

**Repairs as universal constructions** (\ledger{GIN-OPEN-003}). *Question:* which of the repairs of inadmissibility (extension, selection, restriction, quotient, totalization, absorption, signal; Chapter 18) are universal constructions — Grothendieck group, localization, completion, quotient — and which are not? *Falsifier for the trilemma's generality* (\ledger{GIN-THM-004}): a system giving $1/0$ a value that keeps the ring laws, the converse reading of division and $0 \ne 1$ — impossible by \ledger{GIN-THM-003}, so the open part is the categorical *statement*, not the impossibility.

**Admissibility closures** (\ledger{GIN-OPEN-010}). *Question:* make the correspondence between sets of converse problems and classical closures (constructible numbers, real algebraic numbers) precise, with bit complexities.

**Is re-association a distinct mechanism?** (\ledger{GIN-OPEN-004}, \ledger{GIN-CONJ-001}). *Falsifier:* a reduction of every re-association example to CGT's grammar-shape theorem without loss, which would make M-ASSOC a name rather than a mechanism.

## Priority 3: completeness of the models {#sec:p3}

**Completeness of the four-layer outcome model** (\ledger{GIN-OPEN-006}). *Falsifier:* a failure mode of a real numerical system — decimal floating point, posits, interval arithmetic, a computer-algebra system — that fits none of syntax, typing, semantics and execution.

**A complete IEEE 754 reference** (\ledger{GIN-OPEN-007}). Extend the simulator to all rounding attributes, fused multiply–add, conversions, remainder, decimal formats and NaN payloads; validate against an established test suite and more than one ISA.

**Machine semantics on more hosts** (\ledger{GIN-OPEN-009}). Repeat GIN-EXP-004 on other operating systems, compilers and versions, and map which compilers delete post-division zero tests under which flags (\ledger{GIN-OBS-008}).

**Mechanized proofs** (\ledger{GIN-OPEN-011}). Formalize \ledger{GIN-THM-001} to \ledger{GIN-THM-007} and \ledger{GIN-PROP-006} in a proof assistant. A useful complication: Lean's mathlib totalizes $0^{-1} = 0$, so the statements must carry explicit admissibility hypotheses — a test of whether the converse vocabulary survives formalization. Small-case computation, which this book uses throughout, is not a substitute for these proofs.

## Closed or answered {#sec:closed}

**Does the segment notation generalize?** (\ledger{GIN-OPEN-008}). Answered: a calculus of segments exists and is the classical calculus of paths and 1-chains modulo 2 (\ledger{GIN-PROP-051}); it adds no new content. The notation `0{1,2,3}4` remains a checkable display of boundary and interior.

## Reproducing the starting point {#sec:reproduce-open}

Every problem above starts from evidence that can be regenerated without accounts or privileged access:

```python run
import os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
scripts = sorted(f for f in os.listdir(os.path.join(ROOT, "experiments")) if f.startswith(("exp0", "check_theorems")) and f.endswith(".py"))
print(len(scripts), "experiment and check scripts:")
print("  " + "\n  ".join(scripts))
print("run all:  sh experiments/run_all.sh   (Appendix B lists the toolchains each one needs)")
```

```output
17 experiment and check scripts:
  check_theorems.py
  check_theorems_edition1.py
  exp001_numerals.py
  exp002_increment_carries.py
  exp003_converse_census.py
  exp004_machine_division.py
  exp005_ieee_validation.py
  exp006_adder_circuits.py
  exp007_mul_div_circuits.py
  exp008_bit_complexity.py
  exp009_euclid.py
  exp010_primes.py
  exp011_numeral_shapes.py
  exp012_representation_boundaries.py
  exp013_execution_prediction.py
  exp014_isa_emulation.py
  exp015_law_census.py
run all:  sh experiments/run_all.sh   (Appendix B lists the toolchains each one needs)
```

::: exercise {#ex:open-falsifier}
Choose one problem from Priority 2 and write its falsifier in the form "if an experiment or proof shows X, the hypothesis Y is rejected", with X stated precisely enough to check.
:::

::: exercise {#ex:open-new}
Formulate a new open problem raised by a chapter of your choice, in the format of this chapter: question, decision criterion, falsifier, literature to read first, reproduction path.
:::

::: summary
- Priority 1: verify or refute the novelty of the two candidate statements; run the AI-only baseline of GIN-EXP-013; confirm the emulated ISA results on hardware.
- Priority 2: a grammar-class hierarchy of operations; the cost of admissibility; repairs as universal constructions; admissibility closures; whether re-association is a mechanism.
- Priority 3: completeness of the four-layer model; a complete IEEE reference; more hosts; mechanized proofs.
- The segment-notation question is closed: the calculus exists and is classical.
- Every problem starts from evidence that `sh experiments/run_all.sh` regenerates.
:::
