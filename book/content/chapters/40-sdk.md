---
title: "The SDK as Executable Semantics"
status: implementation
statusnote: A description of the software that accompanies the book; every example on this page is executed at build time; test counts are those of the 2026-10 audit.
description: The ginsdk package as the book's executable reference semantics — its modules, the stable API, the command-line tool, the outcome and inspection records, how its correctness is checked, and exactly where its models stop.
epigraph: "A definition you can run is a definition you can test."
---

::: objectives
- Know what each module of `ginsdk` implements and which chapter defines it.
- Evaluate, compare and inspect expressions from Python and from the command line.
- Read the `Outcome` and `gin-inspect/1` records.
- Know how the SDK is tested and cross-checked, and list its domain limitations before relying on it.
:::

## Why the book has software {#sec:why-sdk}

Every definition in this book that can be executed has been: the digit grammars of Chapter 6, the converse problems of Chapter 9, the IEEE 754 formats of Chapter 25, the machine division models of Chapter 24, the circuits of Chapter 22, the limb arithmetic of Chapter 15, the number-theoretic algorithms of Chapters 30–35. The package `ginsdk` collects them. It has two jobs: to make the book's definitions precise enough that a computer can disagree with them, and to produce every printed output in the book — 92 executed examples in the first 32 chapters were reproduced by the audit, and each chapter since adds more (\ledger{GIN-D-016}).

It is written in Python using only the standard library, so that it runs wherever Python $\ge 3.10$ does, without installing anything.

| module | implements | chapters |
|---|---|---|
| `numerals` | digit grammars, canonical numerals, conversion, compilation to affine maps | 5–7 |
| `peano` | successor terms, primitive recursion with rule counts, segments | 3–4 |
| `converse` | solution sets of converse problems; fractions as pairs | 9, 16–18 |
| `expr` | the expression language and evaluation in 20+ domains with layered outcomes | 2, 8, 23 |
| `contracts` | operation contracts, `inspect`, `verify` (schemas `gin-contracts/1`, `gin-inspect/1`) | 8, 39 |
| `ieee` | IEEE 754 binary formats by exact rational rounding, with all five flags | 25 |
| `machine` | integer division and overflow semantics of x86-64, AArch64, RISC-V, C, Java, Rust, Go, Python, JavaScript | 24, 26 |
| `circuits` | gate-level adders, multiplier, divider; the carry monoid | 11, 22 |
| `bigint` | limb arithmetic with counted word operations | 15, 36–37 |
| `numbertheory` | Euclid, Bézout, CRT, exponentiation, primality, factoring, arithmetic functions | 30–35 |
| `totalized` | totalized division systems and their law census | 18 |
| `cost` | explicit cost counters | 36 |

## Evaluating, comparing, inspecting {#sec:sdk-use}

Three entry points cover most uses: `evaluate` returns an `Outcome`; `compare` evaluates one expression in many domains; `contracts.inspect` adds the reference mathematics and the machine–mathematics relation of Chapter 39.

```python run
from ginsdk import evaluate, compare

o = evaluate("1 / 0", "Q")
print(o.status, "|", o.layer, "|", o.reason)
print(o.equation, "|", o.solutions)
for out in compare("7 / -2", ["Z", "Q", "binary64", "Python", "int32 Java"]):
    print(f"  {out.domain:10s} {out.status:12s} {out.display}")
```

```output
no-solution | semantics | 0 · c = 0 for every c, so 0 · c = 1 would require 0 = 1
0 · c = 1 | ∅
  Z          no-solution  
  Q          value        -7/2
  binary64   value        -3.5
  Python     value        -3.5
  int32 Java value        -3
```

The same operations are available from a shell, which is how the SDK is meant to be used by other programs — including AI systems — that need to know which question an execution system will answer:

```python run
import subprocess, sys

out = subprocess.run([sys.executable, "-m", "ginsdk", "eval", "2147483647 + 1", "--domain", "int32 C"], capture_output=True, text=True).stdout
print(out.strip())
out = subprocess.run([sys.executable, "-m", "ginsdk", "inspect", "0 / 0", "--domain", "binary64"], capture_output=True, text=True).stdout
import json
r = json.loads(out)
print(r["schema"], "| machine:", r["execution"]["status"], r["execution"]["value"], r["execution"]["flags"],
      "| mathematics:", r["mathematics"]["status"], "| relation:", r["relation"]["kind"])
```

```output
2147483647 + 1  in int32 C: undefined (execution) — addition overflows 32 bits (exact result 2147483648); C17 6.5p5: signed overflow is undefined
gin-inspect/1 | machine: special NaN ['invalid'] | mathematics: non-unique | relation: special-datum
```

::: demo arith
Text alternative: type an expression and choose a domain; the widget shows the tokens, the parse tree, the four layers with the one that decided the outcome, the converse equation and its solution set for inverse operations, the step trace, the representation of the result and the cost estimate — computed in the browser by a JavaScript port of `ginsdk.expr` that is tested against fixtures exported from the SDK.
:::

## The records {#sec:records}

An `Outcome` (Chapter 8; \ledger{GIN-DEF-062}) records the expression and domain, the **status** (value, special, no-solution, non-unique, not-in-domain, unsupported, overflow, trap, exception, undefined, syntax-error), the **layer** at which evaluation stopped, a **reason** in words, the **equation** and **solutions** of a failed converse problem, IEEE **flags**, **notes**, the **steps** with the rule each applied, the parse **tree**, the **representation** of the result, and a **cost** in a named unit. No outcome is a bare "error".

A `gin-inspect/1` record (Chapter 39) contains, in addition, the reference domain, a per-layer verdict, the mathematical outcome, and the relation between execution and mathematics. Both records are stable parts of the public API (version 1.x): fields may be added, not removed or renamed.

## How the SDK is checked {#sec:sdk-checked}

Software that defines the semantics of a book needs independent checks; agreeing with itself proves nothing. The checks are of four kinds:

1. **Unit tests** — 74 tests at the time of the 2026-10 audit, 75 in this edition (`python3 -m unittest discover -s sdk/tests`), including exhaustive small-case checks of every circuit and every converse-problem formula.
2. **Independent oracles** — the IEEE simulator against the host processor's own arithmetic and exception flags on 80,600 cases (\ledger{GIN-IMP-001}); the machine models against real executions in seven toolchains (\ledger{GIN-IMP-002}, \ledger{GIN-OBS-017}) and against QEMU's emulation of AArch64 and RISC-V (\ledger{GIN-IMP-008}); the limb arithmetic against Python's integers.
3. **Theorem checks** — exhaustive small-case checks of every "proved here" statement (`experiments/check_theorems*.py`).
4. **The book itself** — every executed example must reproduce its printed output, and the browser laboratory must reproduce the SDK on the exported fixtures (`npm test`).

These checks found real defects, and the book records them rather than hiding them: exponents were once evaluated inside $\Z/n$ (\ledger{GIN-NEG-013}); signaling NaNs were once ignored (\ledger{GIN-REJ-002}); and during the writing of Chapter 39 the 32-bit division path was found not to flag the wraparound of $\mathrm{INT\_MIN}/-1$, which made the inspection relation call it a "selection" — fixed in both the SDK and the laboratory, with a regression test. Later, an experiment of the separate research lane *The Number* found that the SDK's tokenizer accepted any Unicode decimal digits (`٣٤` evaluated to 34) where the laboratory accepted only `0`–`9`; the SDK now follows the laboratory (correction C-006 in the results ledger).

## Where the models stop {#sec:sdk-limits}

::: boundary
**Limitations of `ginsdk` 1.0.** The SDK is a reference, not a production numerical library.

- **IEEE 754**: binary formats with round-to-nearest-even only; NaN payloads and signs not modelled; no fused multiply–add, conversions beyond the basic ones, or decimal formats (\ledger{GIN-OPEN-007}).
- **Machines**: 32-bit integer models from specifications; measured on one x86-64 host, emulated for AArch64 and RISC-V, never run on physical AArch64 or RISC-V hardware (\ledger{GIN-OPEN-012}). Compound expressions and compiler optimizations are not modelled (the post-division zero test of Chapter 23 shows why that matters).
- **Exact reals**: irrational square roots are carried as flagged 40-digit decimal approximations; there is no exact real arithmetic.
- **Symbolic domain**: rational functions of one variable over $\Q$ only.
- **Performance**: limb arithmetic is written for counting, not speed; Python's built-in integers are far faster.
- **Cost estimates** in `evaluate` are schoolbook models, not measurements; the measurements are in `bigint` and Chapter 37.
:::

::: exercise {#ex:sdk-new-domain}
Sketch how you would add a domain for 16-bit two's-complement integers with saturating arithmetic: which class in `ginsdk.expr` you would instantiate, which overflow policy you would pass, and which test you would write first.
:::

::: solution {of="ex:sdk-new-domain"}
Instantiate `IntModel` with width $16$ and a saturating policy (the `machine.add_fixed` function already implements `saturate`), register it in `DOMAINS`, and first test the boundary: `32767 + 1` must give `32767` with an `overflow` flag, and `-32768 - 1` must give `-32768`. Then export fixtures and add the domain to `gin-core.js`, or `npm test` will fail — by design.
:::

::: exercise {#ex:sdk-verify}
Use `contracts.verify` on the outcome of `evaluate("0.1 + 0.2", "binary64")` and explain what is being verified independently of the evaluator.
:::

::: summary
- `ginsdk` is the book's executable reference semantics: standard-library Python, twelve modules, a stable 1.x API.
- `evaluate`, `compare` and `contracts.inspect` (also `python3 -m ginsdk eval|compare|inspect`) return layered records, never a bare error.
- It is checked by 75 unit tests, by independent oracles (hardware, seven toolchains, QEMU, Python integers), by theorem checks, and by the book's executed examples and laboratory fixtures; defects found by these checks are recorded.
- Its limits — binary IEEE formats with one rounding mode, 32-bit specification models, approximated reals — are stated, not discovered by the reader.
:::
