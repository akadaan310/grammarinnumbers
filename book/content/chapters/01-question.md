---
title: "The Question: What Does $1 + 1$ Ask?"
status: mixed
statusnote: The method and vocabulary are this book's; every mathematical fact used in this chapter is classical.
description: The research question of the book, the thirteen layers beneath a familiar expression, the evidence vocabulary, and what the book does and does not claim.
epigraph: "Every expression sits on a network of definitions, representations, laws, algorithms and machine decisions. Familiar notation hides the network; it does not remove it."
---

::: objectives
- State the central research question of this book and explain why it is not assumed to be answered.
- Descend from the expression $1 + 1$ through thirteen layers, from mathematical object to counterexample, and say what each layer contributes.
- Recognize six familiar expressions — $1+1$, $0/1$, $1/0$, $0/0$, $1+1 = 10_2$ and $2147483647 + 1$ — as six *different kinds* of question.
- Read the evidence badges and ledger identifiers that accompany every formal claim in the book.
- Know exactly what this book claims to contribute, and what it does not.
:::

## Six familiar expressions {#sec:six}

Here are six things anyone who has been to school can read:

$$
1 + 1, \qquad 0/1, \qquad 1/0, \qquad 0/0, \qquad 1 + 1 = 10_2, \qquad 2147483647 + 1 .
$$

They look alike. Each is a short string of digits and operator symbols, and the first two have answers everyone knows. But they are not six instances of one kind of question. The first asks for a value and gets one. The second asks for a value and gets one too, although many people hesitate. The third asks for a value that does not exist: there is no number $c$ with $0 \cdot c = 1$. The fourth asks for a value that is not *determined*: every number $c$ satisfies $0 \cdot c = 0$. The fifth is not a computation at all but a claim that two different words name the same value. The sixth has the answer $2147483648$ in the integers, has the answer $-2147483648$ on most processors if the operands are 32-bit integers, and has *no meaning at all* in the C programming language, whose standard declares signed overflow undefined.

None of this is new mathematics. The point of this book is that it is not *visible* in the notation, and that making it visible is a computational task with a precise structure. We will spend seventeen parts making it visible.

## The research question {#sec:question}

The book investigates one question, formulated by Abed Kadaan as the founding question of this publication:

> **Can numerical objects, arithmetic operations, number representations and numerical algorithms be understood as computational grammars whose admissible transitions, semantics, representations and costs can be formally specified and experimentally validated?**

The question has a weak reading and a strong reading. The weak reading asks whether arithmetic can be *described* in this vocabulary: whether there is a consistent way to say, of every operation, what its inputs and outputs are, when it is admissible, how its result is represented, what algorithm computes it and what it costs. The strong reading asks whether the description *does work*: whether it yields new theorems, better algorithms, sharper explanations of machine behaviour, or interfaces that make computation more reliable.

We do not assume either answer. The weak reading turns out to be well supported: every operation studied in this book has a precise description of that kind, and every failure we study is classified by the layer at which it occurs and the condition that fails. The strong reading is answered more carefully, and partly negatively. The mathematics this book uses is, with very few exceptions, classical, and it is labelled so. What the framework adds is organization, vocabulary, executable reference semantics and measurements — and, in one case we will measure (\chapref{39-interfaces}), a demonstrable improvement in predicting what real programs do. The final part of the book (\chapref{41-findings}) states exactly which reading has been established and to what extent.

## Thirteen layers beneath $1 + 1$ {#sec:thirteen}

What does it take for $1 + 1$ to *be* $2$? The table below descends through thirteen layers. Each row is a question that someone — a mathematician, a compiler writer, a hardware designer, a person testing an answer — must have answered for the statement to mean anything.

::: definition {#def:layered-analysis title="Layered analysis of an arithmetic request" status="definition" ledger="GIN-DEF-090"}
A **layered analysis** of an arithmetic expression $e$ evaluated in a domain $D$ answers, in order: (1) which *mathematical objects* are involved; (2) which *symbols and numerals* name them; (3) whether $e$ is a sentence of the *formal syntax*; (4) what $e$ *denotes* under the semantic interpretation; (5) whether every operation in $e$ is *admissible* at its arguments; (6) which *state transition* each operation performs; (7) how values are *represented*; (8) which *algorithm* computes each operation; (9) what the *machine* executes; (10) which *invariants* make the algorithm correct; (11) what the computation *costs* under a stated model; (12) how the result is *verified* empirically; (13) where the analysis *fails*: its limits and counterexamples.
:::

The thirteen questions are not independent, and several are classical subjects of their own (logic answers (1)–(4), algorithm analysis (8), (10) and (11), computer architecture (9)). Their value as a list is that they force each answer to be stated, rather than assumed.

| Layer | For $1 + 1$ | Where in the book |
|---|---|---|
| 1. object | the element $S(S(0))$ of the natural numbers, reached from $0$ by two successor moves | \chapref{03-successor} |
| 2. symbol and numeral | the digit `1`, the operator symbol `+`; the result named `2`, `10₂`, `II`, `SS0` | \chapref{05-positional} |
| 3. syntax | `1 + 1` is a sentence of the expression grammar: a binary node `+` with two numeral leaves | \chapref{08-operations} |
| 4. semantics | the value of the tree is $\mathrm{add}(1, 1)$, defined by primitive recursion | \chapref{04-recursion} |
| 5. admissibility | addition is total on $\N$: no condition can fail | \chapref{08-operations} |
| 6. transition | one application of the move "add 1", that is, one successor step from state $1$ to state $2$ | \chapref{03-successor} |
| 7. representation | in binary the digits `1` and `1` produce sum bit `0` and carry `1`: the word `10` | \chapref{07-value-and-representation} |
| 8. algorithm | schoolbook addition with carry, least significant digit first | \chapref{10-addition} |
| 9. machine | an `add` instruction on two registers; a half adder computes $\mathrm{XOR}(1,1)=0$ and $\mathrm{AND}(1,1)=1$ | \chapref{22-circuits} |
| 10. invariant | after position $i$, the bits written so far plus $2^{i+1}$ times the carry equal the sum of the operands' low $i+1$ bits | \chapref{10-addition} |
| 11. cost | $\Theta(L)$ bit operations for $L$-bit operands; one instruction while operands fit in a word | \chapref{36-cost-models} |
| 12. verification | executed: every implementation in this book agrees, and the result is checked against independent arithmetic | \chapref{b-reproducibility} |
| 13. limits | in 32-bit hardware arithmetic the same algorithm computes $2147483647 + 1 = -2147483648$; in ISO C that expression is undefined | \chapref{26-overflow} |

A reader who already knows arithmetic will find nothing surprising in any single row. The surprise, if there is one, is the length of the table — and the fact that row 13 exists at all: the most familiar algorithm in mathematics has a domain outside which it computes something else.

## The same request in many domains {#sec:many-domains}

The software that accompanies this book, the Python package `ginsdk` (\chapref{40-sdk}), evaluates an arithmetic expression in a chosen domain and reports the layer at which evaluation stopped. Here is the first example of the book, executed when the book is built:

```python run
from ginsdk import evaluate

for e in ["1 + 1", "0 / 1", "1 / 0", "0 / 0"]:
    o = evaluate(e, "Q")
    print(f"{e:6s} in Q:  {o.status:12s} {o.display or o.reason}")
```

```output
1 + 1  in Q:  value        2
0 / 1  in Q:  value        0
1 / 0  in Q:  no-solution  0 · c = 0 for every c, so 0 · c = 1 would require 0 = 1
0 / 0  in Q:  non-unique   0 · c = 0 holds for every c: the equation does not determine c
```

The two failures are different, and the program says so: `1 / 0` fails because *no* rational number solves the defining equation; `0 / 0` fails because *every* rational number does. This distinction is the subject of Part VIII. It is classical — it is the difference between the image and the kernel of the map $c \mapsto 0 \cdot c$ — but it is lost whenever both cases are reported as "undefined" or "error".

Now hold the expression fixed and change the domain:

```python run
from ginsdk import evaluate

for d in ["Q", "binary64", "Python", "int32 x86-64", "int32 AArch64", "int32 RISC-V", "int32 C", "int32 Java"]:
    o = evaluate("1 / 0", d)
    print(f"{d:14s} {o.status:12s} {o.display or o.reason.split(' — ')[0].split('  [')[0]}")
```

```output
Q              no-solution  0 · c = 0 for every c, so 0 · c = 1 would require 0 = 1
binary64       special      Infinity
Python         exception    ZeroDivisionError: division by zero
int32 x86-64   trap         #DE (divide error)
int32 AArch64  value        0
int32 RISC-V   value        -1
int32 C        undefined    undefined behaviour
int32 Java     exception    ArithmeticException: / by zero
```

The same five characters `1 / 0` have, across these domains, *seven* distinct outcomes: no solution, a special datum that is not a number (`Infinity`), a language exception, a hardware trap, the value $0$, the value $-1$, and no meaning at all. Two of the outcomes look like ordinary numbers. They are not solutions of anything: $0 \cdot 0 \ne 1$ and $0 \cdot (-1) \ne 1$. They are *conventions* adopted by the designers of the AArch64 and RISC-V instruction sets, for reasons we will examine in \chapref{24-machine-division}. In this book they are called **totalizations**: values supplied where the mathematics supplies none.

## Kinds of claim, and how this book labels them {#sec:evidence}

A book about the foundations of arithmetic is surrounded by millennia of mathematics. Almost every true statement in it is known. The danger is not that the book will say false things — although it may, and every claim is set out so that it can be checked — but that it will present known things as discoveries, or present a reformulation as if it were a theorem. To prevent this, every formal claim carries one of the labels below, and a stable identifier in the research ledger.

| Label | Meaning in this book |
|---|---|
| Definition | a precise object; not a discovery |
| Axiom | an assumption of a formal system under study |
| Lemma, Proposition, Theorem, Corollary | a statement with a proof, given here or cited |
| <span class="status status-classical">Classical result</span> | known in the literature; cited; a proof may be included for completeness |
| <span class="status status-proved-here">Proved here</span> | the proof in this book was written for it and checked by computation on small cases; *this is not a claim of novelty* |
| <span class="status status-reinterpretation">Reinterpretation</span> | a known fact re-expressed in this book's vocabulary; not a new result |
| <span class="status status-reproduced">Reproduced result</span> | a published result reproduced here independently by computation |
| <span class="status status-implementation">Implementation result</span> | a property of code written for this book, on a stated test domain |
| <span class="status status-empirical">Empirical observation</span> | a reproducible measurement, with its environment; not a proof |
| <span class="status status-counterexample">Counterexample</span> | an instance where a plausible claim fails |
| <span class="status status-conjecture">Conjecture</span> | believed, not established |
| <span class="status status-open">Open problem</span> | a precisely stated question this book cannot answer |

Identifiers have the form `GIN-THM-001`, `GIN-OBS-009`, `GIN-NEG-005`. Each links to its entry in the research ledger, which records its proof or data, its relation to prior work and its history. The ledger is the canonical record; the book is its exposition. Identifiers of the parent research program, Computational Grammar Theory, have the form \cgt{CGT-THM-003} and link to that separate publication.

::: boundary
**What the badges do not mean.** "Proved here" means the proof is in this book and machine-checked on small instances by `experiments/check_theorems.py`; it does not mean independently reviewed, and it almost never means new. No result in this book has been peer reviewed. "Empirical" results hold on the stated host, toolchain and version; the book never generalizes a measurement on one machine to "the machine".
:::

## Relationship to Computational Grammar Theory {#sec:cgt}

This book is the second publication of a research program whose first publication, *Computational Grammar Theory* (CGT), studies how computational structures — arrays, trees, graphs, ranked collections — expose and constrain their operations through grammars, and when such grammars change the cost of computing. CGT is the *earlier* book. This book is its sequel in the order of research, but in the order of ideas it is a prequel: it descends beneath CGT's data structures to the numbers, numerals and arithmetic operations from which every address, index and cost in CGT is built.

The two publications are independent. Each has its own numbering, ledger, software and evidence; no claim here depends on a claim there. Where a concept genuinely corresponds — CGT's grammatical *address* and the positional numeral, for instance (\chapref{05-positional}) — the correspondence is stated precisely and both sides are cited. Part XV (\chapref{38-cgt}) collects the correspondences and also the places where the analogy breaks.

## How to read this book {#sec:paths}

The parts build on each other, but readers with different purposes can take different paths.

- **A reader who knows ordinary arithmetic** should read Parts I–IV in order, then Part VIII (division and zero), then whatever interests them. The executable examples can be skipped; the prose does not depend on them.
- **A programmer** should read Parts I, IV, VIII, IX and X, and then Part XVI, which shows how operation contracts predict what real programs do.
- **A mathematician** will find the mathematics classical and is invited to read the proofs critically. Parts VIII, XI and XII contain the most mathematics; the open problems are in \chapref{42-open-problems}.
- **A computer scientist** should read Parts V, VII, IX, X and XIV, where every cost is stated in an explicit model and measured.
- **An AI researcher** should read Part IV and Part XVI, and the counterexamples throughout: they are the cases in which a fluent description of arithmetic is wrong.

Every chapter ends with exercises, most with solutions that can be expanded.

::: exercise {#ex:q-six}
For each of the six expressions of §\ref{sec:six}, say whether it asks for a value, makes a claim, or both; and if it asks for a value, say whether the integers supply exactly one.
:::

::: solution {of="ex:q-six"}
$1+1$ asks for a value; ℤ supplies exactly one ($2$). $0/1$ asks for a value; exactly one ($0$). $1/0$ asks for a value; none exists in ℤ (or ℚ, ℝ, ℂ). $0/0$ asks for a value; every integer satisfies the defining equation, so none is determined. $1 + 1 = 10_2$ makes a claim (that the value of the left side equals the value denoted by the binary numeral $10$); it is true. $2147483647 + 1$ asks for a value; ℤ supplies exactly one, $2147483648$ — the trouble arises only when the domain is changed to 32-bit machine integers.
:::

::: exercise {#ex:q-layers}
Write the thirteen-layer table of §\ref{sec:thirteen} for the expression $6 / 3$. Which layer would change if the expression were $6 / 4$ evaluated in ℤ?
:::

::: solution {of="ex:q-layers"}
Objects: $6$, $3$, the operation of division as the converse of multiplication. Admissibility: $3 \ne 0$ and $3 \mid 6$. Transition: the unique $c$ with $3 \cdot c = 6$, namely $2$. Representation: `110₂ / 11₂ = 10₂`. Algorithm: long division, which in binary performs two compare-and-subtract rows. Machine: `idiv`, `sdiv` or `div` depending on the instruction set. Invariant of long division: dividend $=$ quotient so far $\times$ divisor $+$ remainder. Cost: $\Theta(L^2)$ bit operations schoolbook. For $6/4$ in ℤ, layer 5 changes: $4 \nmid 6$, so the converse problem has no integer solution; ℚ would give $3/2$, and an integer machine would give the truncated quotient $1$ — a *selection* (\chapref{19-remainder}), not a quotient.
:::

::: exercise {#ex:q-totalization}
On AArch64, integer division of $1$ by $0$ yields $0$. Explain in one sentence why $0$ is not "the answer" to $1 / 0$, and in one sentence why returning it is nevertheless a consistent design.
:::

::: solution {of="ex:q-totalization"}
It is not the answer because $0 \cdot 0 = 0 \ne 1$: it does not satisfy the equation that defines division. It is consistent because a total operation that returns a fixed value on a zero divisor contradicts nothing, provided nobody reads the value as a solution; it is a convention, like $0^0 = 1$, and programs that care must test the divisor themselves.
:::

::: exercise {#ex:q-checker}
The book's example checker executes every code block marked as runnable and refuses to build the book if the printed output differs from the output shown. Name one kind of error in this chapter that the checker *cannot* catch.
:::

::: solution {of="ex:q-checker"}
Any error in the prose that does not change the program's output: for instance, a sentence saying "eight domains produce seven outcomes" when they produce eight, or a misdescription of what an outcome means. The checker verifies the agreement of code and output, nothing more; claims about the output need their own checks or a careful reader.
:::

::: exercise {#ex:q-evidence}
Classify each statement with one of the labels of §\ref{sec:evidence}: (a) "In ℤ/6 the equation $4c = 2$ has exactly two solutions." (b) "On this host, `1.0/0.0` in Python raises ZeroDivisionError." (c) "Positional notation is a compression of unary notation." (d) "Every finite integral domain is a field."
:::

::: solution {of="ex:q-evidence"}
(a) A proposition — classical, checkable by exhaustion. (b) An empirical observation (measured on one host and Python version), backed by the language specification. (c) A reinterpretation: a known fact (binary numerals are short straight-line programs for unary terms) stated in this book's vocabulary. (d) A classical result.
:::

::: summary
- The book asks whether arithmetic can be specified and tested as computational grammars, and does not assume the answer.
- Thirteen layers lie beneath $1+1$, from mathematical object to counterexample; the book states each one.
- Six familiar expressions are six different kinds of question; `1 / 0` alone has seven distinct outcomes across common domains.
- Every claim is labelled by kind of evidence and identified in the research ledger; "proved here" never means "new".
:::
