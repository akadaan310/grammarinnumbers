---
title: "Arithmetic Circuits"
status: mixed
statusnote: Gates, adders, multipliers, dividers and the circuit-complexity classification of arithmetic are classical; gate counts and depths are measured on this book's constructions.
description: Circuits as grammars of gates with syntax, semantics and cost; the half and full adder in AND/OR/XOR and in NAND alone; a gallery of arithmetic circuits with measured size and depth; and what circuit complexity knows about arithmetic — addition in constant depth with unbounded fan-in, multiplication not, division in threshold circuits.
epigraph: "A circuit is an expression in which every subexpression is computed exactly once, by a piece of hardware, at the same time as all the others it does not depend on."
---

::: objectives
- Define a Boolean circuit with its syntax (well-formed wiring), semantics (the function computed) and cost (size and depth).
- Build half and full adders from AND, OR and XOR gates and from NAND gates alone, and verify them exhaustively.
- Read the size and depth of the adders, subtractor, multiplier and divider of the SDK, and relate them to the algorithms of earlier chapters.
- State the classical circuit-complexity facts about arithmetic: $\mathsf{AC}^0$ contains addition but not multiplication, and $\mathsf{TC}^0$ contains multiplication and division.
:::

## Circuits as grammars {#sec:circuit-grammar}

::: definition {#def:circuit title="Circuit" status="definition" ledger="GIN-DEF-040"}
A **circuit** is a directed acyclic graph whose sources are input wires and constants and whose internal nodes are gates from a fixed basis — here $\{\mathrm{NOT}, \mathrm{AND}, \mathrm{OR}, \mathrm{XOR}\}$ with fan-in at most $2$, or $\{\mathrm{NAND}\}$. *Syntax*: every gate input is a previously defined wire. *Semantics*: the Boolean function computed at the output wires. *Cost*: **size** (the number of gates) and **depth** (the length of the longest path from an input to an output).
:::

A circuit is an arithmetic expression over bits in which shared subexpressions are computed once (a straight-line program, Chapter 6) and in which everything that can be computed simultaneously is. Its size measures the hardware, its depth the time. The same Boolean function has many circuits, and the trade-off between size and depth is the hardware form of the trade-off between work and parallel time.

## Adders from gates {#sec:adder-gates}

The **half adder** adds two bits: sum $= a \oplus b$, carry $= a \wedge b$ — two gates, depth $1$. The **full adder** adds three: sum $= a \oplus b \oplus c$, carry $= (a \wedge b) \vee ((a \oplus b) \wedge c)$ — five gates, depth $3$. NAND is *universal*: every Boolean function has a NAND-only circuit. A full adder needs nine NAND gates in the SDK's construction.

```python run
from ginsdk import circuits as K
from itertools import product

for name, c in [("half adder", K.half_adder()), ("full adder", K.full_adder()), ("full adder (NAND)", K.full_adder_nand())]:
    ok = True
    for bits in product((0, 1), repeat=len(c.inputs)):
        out = c.run(dict(zip(c.inputs, bits)))
        total = sum(bits)
        ok &= out == [total % 2, total // 2]
    print(f"{name:18s} gates {c.size:2d}  depth {c.depth()}  {c.gate_counts()}  exhaustively correct: {ok}")
```

```output
half adder         gates  2  depth 1  {'XOR': 1, 'AND': 1}  exhaustively correct: True
full adder         gates  5  depth 3  {'XOR': 2, 'AND': 2, 'OR': 1}  exhaustively correct: True
full adder (NAND)  gates  9  depth 6  {'NAND': 9}  exhaustively correct: True
```

The full adder is the grammar of column addition (Chapter 10) frozen into hardware: three input digits, one output digit, one carry. Chaining $n$ of them gives the ripple-carry adder, whose carry path is the sequential composition of Chapter 11's carry monoid; prefix adders compute the same monoid products in a tree.

## A gallery of arithmetic circuits {#sec:gallery}

The SDK constructs every arithmetic circuit of this book explicitly and verifies it exhaustively for small widths (\ledger{GIN-IMP-003}). Their measured costs summarize Parts V–VIII in hardware terms:

| circuit ($n$-bit operands) | size | depth | algorithm | chapter |
|---|---|---|---|---|
| ripple-carry adder | $5n - 3$ | $2n - 1$ | column addition | 10, 11 |
| Kogge–Stone adder ($n = 256$) | $5891$ | $17$ | parallel prefix, doubling | 11 |
| Brent–Kung adder ($n = 256$) | $2018$ | $30$ | parallel prefix, tree | 11 |
| subtractor $a + \bar b + 1$ ($n = 6$) | $36$ | $14$ | complement and add | 12 |
| array multiplier | $6n^2 - 8n$ | $6n - 8$ | shift and add | 15 |
| restoring divider ($n = 4, 8, 16$) | $172, 632, 2416$ | $51, 163, 579$ | long division | 19 |

```python run
from ginsdk import circuits as K

for n in (4, 8, 16):
    rows = [("ripple adder", K.ripple_adder(n)), ("Kogge-Stone", K.kogge_stone_adder(n)),
            ("multiplier", K.array_multiplier(n)), ("divider", K.restoring_divider(n))]
    print(f"n = {n:2d}: " + "   ".join(f"{name} {c.size}/{c.depth()}" for name, c in rows))
```

```output
n =  4: ripple adder 17/7   Kogge-Stone 23/5   multiplier 64/16   divider 172/51
n =  8: ripple adder 37/15   Kogge-Stone 67/7   multiplier 320/40   divider 632/163
n = 16: ripple adder 77/31   Kogge-Stone 179/9   multiplier 1408/88   divider 2416/579
```

The pattern is the familiar hierarchy of the four operations: addition linear in size, multiplication and division quadratic. The restoring divider is the deepest, because each of its $n$ rows must wait for the previous row's subtraction to finish before it can decide whether to keep the difference — a sequential dependence that the multiplier, whose partial products are independent, does not have.

## What circuit complexity knows {#sec:complexity-classes}

Circuit complexity asks how small and how shallow circuits for a function can be, as $n$ grows. Two classes matter here. $\mathsf{AC}^0$ contains the functions computable by circuits of polynomial size and *constant* depth, with AND and OR gates of *unbounded* fan-in. $\mathsf{TC}^0$ allows, in addition, *threshold* (majority) gates.

::: theorem {#thm:circuit-classes title="The circuit complexity of the four operations" status="classical" ledger="GIN-HIST-006"}
1. Addition and comparison of $n$-bit numbers are in $\mathsf{AC}^0$.
2. Multiplication of $n$-bit numbers is not in $\mathsf{AC}^0$ (Furst, Saxe and Sipser \cite{furst1984}, by reduction from parity).
3. Multiplication, and also division and iterated multiplication, are in $\mathsf{TC}^0$; for division, membership in the *uniform* version of the class was established by Hesse, Allender and Barrington \cite{hesse2002}.
:::

::: proof
(1) The carry into position $i$ is $1$ iff some position $j < i$ generates and every position between $j$ and $i$ propagates: an OR over $j$ of ANDs over the positions above $j$ — depth two with unbounded fan-in, polynomial size. (2) and (3) are deep results; see the cited papers.
:::

The theorem is the circuit-level twin of the automaton-level Theorem GIN-THM-005. With finite automata, addition is regular and multiplication is not; with constant-depth circuits, addition is in $\mathsf{AC}^0$ and multiplication is not. In both settings, what makes addition easy is that a carry is a *local summary* — one of three monoid elements, or one OR of ANDs — while multiplication must combine every bit of one operand with every bit of the other.

::: remark
With *bounded* fan-in, as in the circuits of this book, no adder can have constant depth: the carry out depends on all $2n$ inputs, so the depth is at least $1 + \log_2 n$ (\ledger{GIN-PROP-059}). The constant-depth statements above rely on gates that read arbitrarily many wires at once; physical implementations pay for that fan-in in delay. Statements about circuit depth are meaningful only together with the gate model, just as statements about time are meaningful only together with a cost model (\chapref{36-cost-models}).
:::

::: exercise {#ex:circ-majority}
Show that the carry out of a full adder is the majority function of its three inputs, and give a circuit for it with four AND/OR gates.
:::

::: solution {of="ex:circ-majority"}
The carry is $1$ iff at least two of $a, b, c$ are $1$: that is majority. $\mathrm{maj}(a, b, c) = (a \wedge b) \vee (c \wedge (a \vee b))$: one AND, one OR, one AND, one OR — four gates, depth $3$.
:::

::: exercise {#ex:circ-ac0}
Write the depth-2 unbounded-fan-in formula for the carry into position $3$ of an addition, in terms of $g_i = a_i \wedge b_i$ and $p_i = a_i \oplus b_i$.
:::

::: solution {of="ex:circ-ac0"}
$c_3 = g_2 \vee (p_2 \wedge g_1) \vee (p_2 \wedge p_1 \wedge g_0)$ (with carry-in $0$). Given $g_i$ and $p_i$ (one more layer), it is an OR of ANDs.
:::

::: exercise {#ex:circ-divider-depth}
The SDK's divider has depth $51$ for $n = 4$ and $163$ for $n = 8$. Explain why its depth grows faster than linearly in $n$, and estimate the growth from its structure.
:::

::: solution {of="ex:circ-divider-depth"}
Each of the $n$ rows contains an $(n+1)$-bit ripple subtractor (depth about $2n$) followed by a selection, and row $i + 1$ depends on row $i$'s result. Total depth is about $n \cdot 2(n + 1)$, i.e. quadratic: $2 \cdot 4 \cdot 5 = 40$ plus selection layers $\approx 51$; $2 \cdot 8 \cdot 9 = 144$ plus selections $\approx 163$.
:::

::: summary
- A circuit is a straight-line program over bits; size is hardware, depth is time.
- Half and full adders are column addition in gates; NAND alone suffices (nine gates for a full adder here).
- Measured: adders linear, multiplier and divider quadratic in size; the restoring divider is the deepest because its rows are sequential.
- Addition is in $\mathsf{AC}^0$; multiplication is not; multiplication and division are in $\mathsf{TC}^0$ — the circuit-level twin of "addition is finite-state, multiplication is not".
:::
