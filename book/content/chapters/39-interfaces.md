---
title: "Operation Contracts as an Interface Between Request and Execution"
status: mixed
statusnote: The contract format and the inspection relation are proposed here; their predictive accuracy against seven real toolchains is a reproducible measurement (GIN-EXP-013); an AI-only baseline was not run.
description: What a program, a person or an AI system needs to know before executing an arithmetic request — the operation contract and the machine–mathematics relation — and a measurement of how well contract models predict what real compilers and runtimes do, compared with two naive predictors, with the experiment's limits stated.
epigraph: "Before asking a machine for an answer, ask it which question it will answer."
---

::: objectives
- Read an operation contract: input grammar, domain, admissibility, outcome classes, signals and cost model of one operator in one domain.
- Use the machine–mathematics relation to compare an execution with the exact mathematical answer.
- Interpret GIN-EXP-013: what "the contract model predicts real execution" means, and what it does not.
- State the experiment's baselines precisely, including the one that was not run.
:::

## The interface problem {#sec:interface-problem}

A request such as "compute $(-2147483647 - 1) / -1$" passes from whoever writes it — a programmer, a user, an AI system generating code — to whatever executes it. The two sides can disagree about every layer of Chapter 2: the writer may mean the integer $2147483648$, while an x86-64 `idiv` instruction traps, Java returns $-2147483648$, and ISO C gives the program no meaning at all (Chapter 24). An **interface** between request and execution is a description, precise enough to compute with, of which question the executing system will actually answer.

::: definition {#def:contract-interface title="Operation contract" status="definition" ledger="GIN-DEF-080"}
An **operation contract** for an operator $\circ$ in a domain $D$ records: the input grammar (which literals and values belong to $D$); the admissibility condition of $a \circ b$; the outcome classes (value, special datum, no solution, non-unique, overflow, trap, exception, undefined behaviour); the signal raised for each failure; the representation of results; and the cost model. The SDK publishes the contracts of all its domains as a JSON document (schema `gin-contracts/1`).
:::

::: definition {#def:relation-interface title="Machine–mathematics relation" status="definition" ledger="GIN-DEF-081"}
For an expression $e$ evaluated in a machine domain and in the exact domain it implements ($\Z$ for machine integers, $\Q$ for floating point and Python), the **relation** classifies the pair of outcomes as one of: *agrees*; *rounded*; *wrapped*; *totalized* (a value where mathematics has none, as AArch64 returning $0$ for $1/0$); *selected* (a quotient with remainder where the exact quotient does not exist); *different-selection* (the machine selects a different answer from the one the reference selects); *special-datum*; *overflowed-to-special*; *signalled* (the machine refuses where mathematics has a value); *undefined*; *differs*.
:::

```python run
from ginsdk import contracts

for e, d in [("(-2147483647 - 1) / -1", "int32 x86-64"), ("(-2147483647 - 1) / -1", "int32 Java"),
             ("1 / 0", "int32 AArch64"), ("2147483647 + 1", "int32 C"), ("0.1 + 0.2", "binary64")]:
    r = contracts.inspect(e, d)
    print(f"{e:24s} {d:14s} machine: {r['execution']['status']:10s} {str(r['execution']['value'] or ''):12s} "
          f"mathematics: {str(r['mathematics']['value'] or r['mathematics']['status']):12s} -> {r['relation']['kind']}")
```

```output
(-2147483647 - 1) / -1   int32 x86-64   machine: trap                    mathematics: 2147483648   -> signalled
(-2147483647 - 1) / -1   int32 Java     machine: value      -2147483648  mathematics: 2147483648   -> wrapped
1 / 0                    int32 AArch64  machine: value      0            mathematics: no-solution  -> totalized
2147483647 + 1           int32 C        machine: undefined               mathematics: 2147483648   -> undefined
0.1 + 0.2                binary64       machine: value      0.30000000000000004 mathematics: 3/10         -> rounded
```

The same tuple — expression, domain, outcome, relation — is what the command-line tool prints (`python3 -m ginsdk inspect`, Chapter 40) and what the browser laboratory shows.

::: demo machines
Text alternative: type one integer expression; the widget evaluates it in every machine and language domain of the SDK side by side — x86-64, AArch64, RISC-V, ISO C, Java, Rust, Go, Python, JavaScript — and shows for each the outcome class, the value, and its relation to the exact integer answer.
:::

## Does the contract predict real execution? {#sec:prediction}

Chapter 1 promised one measurement in which the framework demonstrably improves a prediction. GIN-EXP-013 executed 845 single operations — 13 operands including $0$, $\pm 1$, the 32-bit extremes and squares near overflow, with the operators $+, -, \times, /, \%$ — at run time in C (gcc, x86-64), Java, Go, Rust (debug build), JavaScript (BigInt and Number) and Python, and predicted each outcome three ways:

- **model** — the SDK's contract model for that toolchain's domain;
- **naive-py** — evaluate the expression in Python;
- **naive-c** — unbounded integers with C's truncating division.

A prediction scores a hit when it gets both the outcome class (value or refusal) and the value right.

```python run
import json, os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
langs = json.load(open(os.path.join(ROOT, "experiments", "results", "exp013.json")))["data"]["languages"]
print(f"{'toolchain':22s} {'model':>17s} {'naive-py':>9s} {'naive-c':>8s}")
for name, r in langs.items():
    model = [(k, v) for k, v in r.items() if k.startswith("model[")]
    m = " / ".join(f"{v['hit']}" + (f" (+{v['abstain']} abst.)" if v["abstain"] else "") + (f" (+{v['not-modelled']} n/m)" if v["not-modelled"] else "") for k, v in model)
    print(f"{name:22s} {m:>17s} {r['naive-py']['hit']:9d} {r['naive-c']['hit']:8d}   of 845")
```

```output
toolchain                          model  naive-py  naive-c
C (gcc -O0, x86-64)    731 (+114 abst.) / 845       612      757   of 845
Java                                 845       613      758   of 845
Go                                   845       613      758   of 845
Rust (debug)                         845       612      757   of 845
JavaScript BigInt                    845       700      845   of 845
JavaScript Number         676 (+169 n/m)       767      718   of 845
Python                               845       845      700   of 845
```

::: observation {#obs:contracts-predict title="Contract models predict real execution; naive models do not" status="empirical" ledger="GIN-OBS-017"}
On the 845 operations of GIN-EXP-013, the contract models predicted outcome class and value in every case they covered, for every toolchain. For ISO C the model *abstained* on the 114 operations whose behaviour is undefined, and was right on the rest; for JavaScript Number the operator `%` was not modelled. "Evaluate in Python" was right on 612–767 of the 845 on the six non-Python toolchains, and "unbounded integers with C division" on 700–758 except JavaScript BigInt. The naive predictors fail on overflow, negative division, true versus integer division, and zero divisors.
:::

::: boundary
**What this measurement shows, and what it does not.**

- It shows that the SDK's domain models *cover* the behaviour of these seven toolchains on these operands: the model is an accurate executable summary of their specifications.
- It does **not** show that the model was learned, discovered or predicted independently: it was built from the same language and instruction-set specifications these toolchains implement. A perfect score validates coverage, not insight.
- It is one host, one version of each toolchain, single operations, and a fixed operand set chosen to include boundaries. Compound expressions, optimizer effects (Chapter 23 showed one) and other platforms are not covered.
- **Baselines.** The two naive predictors are the baselines that were run. A *tool-only* baseline — executing the expression in the target toolchain itself — is the ground truth, not a competitor. An **AI-only baseline** — asking a language model to predict each outcome without tools — was **not run**: no model API was available to the experiment, and no number for it is reported or implied (\ledger{GIN-OPEN-013}).
:::

## Why an interface needs all four layers {#sec:interface-layers}

The naive predictors fail exactly where a single layer is missing from their picture. "Evaluate in Python" has the right *semantics* for integers and the wrong *execution* model for 32-bit machines; "unbounded integers with C division" has the right *division rounding* and no *representation boundary*. The contract model is right because it records every layer separately — typing (which literals exist), semantics (the converse problem), execution (wrap, trap, undefined) — and reports which layer decided the outcome. An interface that reports only a value, or only "error", loses exactly the information that distinguishes the toolchains.

For AI systems that write or check code, the practical consequence is modest and concrete: an arithmetic request carries an implicit domain, and the domain changes the answer. A generator or checker that consults an explicit contract can state which answer a given toolchain will produce; one that reasons "mathematically" will be wrong in the cases measured above. Whether contracts measurably improve AI-generated code is a separate experiment that has not been done (\ledger{GIN-OPEN-013}).

::: exercise {#ex:if-relation}
Predict, without running anything, the relation of \ref{def:relation-interface} for `-7 // 2` in Python, `-7 / 2` in Java, and `-7 / 2` in exact $\Q$; then check with `contracts.inspect`.
:::

::: solution {of="ex:if-relation"}
Python `//` floors and gives $-4$, which is also the quotient that the reference integer domain selects (remainder $1 \ge 0$): *agrees*. Java truncates toward zero and gives $-3$: the exact quotient $-7/2$ is not an integer, and the machine returns *a* quotient with remainder — *selected*. In $\Q$ the value is $-7/2$: *agrees*. The two machines answer different questions, and the relation says which.
:::

::: exercise {#ex:if-design}
Design an experiment that would test whether giving an AI code generator the SDK's contract document reduces arithmetic bugs. State the outcome measure, the control condition, and what result would falsify the hypothesis.
:::

::: summary
- An operation contract states input grammar, admissibility, outcome classes, signals, representation and cost of one operator in one domain; the machine–mathematics relation compares an execution with the exact answer.
- On 845 operations in seven toolchains the contract models were right on every covered case; naive predictors were right on 612–767 (Python) and 700–758 (C-style) of 845 (GIN-OBS-017).
- The model was built from the toolchains' specifications: the measurement validates coverage, not independent prediction.
- The AI-only baseline was not run; no claim about AI systems' performance is made.
:::
