---
title: "Carry: Automata, Monoids, and Parallel Prefix"
status: mixed
statusnote: The carry automaton, carry-lookahead and the automaticity of addition are classical; their reading as CGT arithmetic compilation and the proposed mechanism M-ASSOC are this book's.
description: Binary addition as a two-state automaton; the three-element carry monoid {kill, propagate, generate}; why associativity lets all carries be computed in parallel; ripple-carry and prefix adders measured gate by gate; how long carry chains really are; and why addition is finite-state while multiplication is not.
epigraph: "A carry is a message from one column to the next. Addition is fast when the messages can be summarized before they are delivered."
---

::: objectives
- Describe binary addition as a two-state transducer reading digit pairs from least to most significant.
- Compute in the carry monoid $\{\Kk, \Pp, \Gg\}$ and prove that the carry into each position is a prefix product.
- Explain how associativity turns a sequential computation of depth $n$ into a parallel one of depth $\Oh(\log n)$, and state the gate cost of doing so.
- State, with the right attribution, the classical theorem that addition is finite-state and multiplication is not.
- Relate carry-lookahead to CGT's arithmetic compilation and grammar-shape trade-off.
:::

## The carry automaton {#sec:automaton}

Column addition (Chapter 10) keeps one piece of state between columns: the carry, which is $0$ or $1$ in every base. Read the two input numerals in parallel, least significant digit first, as a single word of digit *pairs*; then addition is performed by a machine with two states.

::: definition {#def:carry-automaton title="Carry automaton and carry monoid" status="definition" ledger="GIN-DEF-041"}
Binary addition, read least significant digit first, is a two-state transducer whose state is the carry. On the digit pair $(a_i, b_i)$ it outputs $a_i \oplus b_i \oplus c$ and moves to the new carry, which is a function of the old one:
- $\Kk$ (**kill**, $c \mapsto 0$) for the pair $(0, 0)$;
- $\Pp$ (**propagate**, $c \mapsto c$) for $(0, 1)$ and $(1, 0)$;
- $\Gg$ (**generate**, $c \mapsto 1$) for $(1, 1)$.

The **carry monoid** is $\{\Kk, \Pp, \Gg\}$ under composition.
:::

The addition $1 + 1 = 10_2$ is a single generate: the pair $(1, 1)$ maps any incoming carry to $1$. The successor's worst case, $0111_2 + 1 = 1000_2$, is a generate at position $0$ followed by two propagates. The laboratory shows the classes position by position.

::: demo carry
Text alternative: two numbers are written in binary. Each position is classified K (both bits 0), P (exactly one bit 1) or G (both bits 1); the carry into each position is obtained by composing the classes from the lowest position upward. For $11 + 1$ in 8 bits: G at position 0, P at positions 1 and 3, giving carries into positions 1, 2 and the result $1100_2 = 12$.
:::

## The monoid and its prefix products {#sec:monoid}

Composing the effect of a lower position $x$ with the effect of the next higher position $y$ gives a single map; write $x \then y$ for "first $x$, then $y$".

::: proposition {#prop:carry-monoid title="The carry monoid; carries are prefix products" status="classical" ledger="GIN-PROP-020"}
In the carry monoid, $x \then y = y$ if $y \in \{\Kk, \Gg\}$ and $x \then y = x$ if $y = \Pp$:
$$
\begin{array}{c|ccc} x \then y & y = \Kk & y = \Pp & y = \Gg \\ \hline x = \Kk & \Kk & \Kk & \Gg \\ x = \Pp & \Kk & \Pp & \Gg \\ x = \Gg & \Kk & \Gg & \Gg \end{array}
$$
$\Pp$ is the identity, every element is idempotent, and the operation is associative. The carry into position $i + 1$ is the image of the input carry $0$ under the prefix product $x_0 \then x_1 \then \cdots \then x_i$ of the classes of positions $0, \ldots, i$.
:::

::: proof
$\Kk$ and $\Gg$ are constant maps on $\{0, 1\}$ and $\Pp$ is the identity, so a composite is determined by its last non-$\Pp$ factor: that gives the table. Composition of functions is associative. By induction, the carry after position $i$ is the composite map applied to $c_0 = 0$.
:::

This is the whole theory of carry-lookahead in one table. It is known in substance from the parallel-prefix literature of Ladner and Fischer \cite{ladner1980} and Brent and Kung \cite{brentkung1982}, who formulated the carry computation with exactly such an associative operator on (generate, propagate) pairs.

```python run
from ginsdk.circuits import carry_class, carry_compose, carries
from functools import reduce

x, y, n = 0b01110110, 0b00011011, 8
classes = [carry_class(x >> i & 1, y >> i & 1) for i in range(n)]
prefix = [reduce(carry_compose, classes[:i + 1]) for i in range(n)]
from_prefix = [0] + [1 if p == "G" else 0 for p in prefix]     # image of carry-in 0
print("classes (pos 0..7):", " ".join(classes))
print("prefix products   :", " ".join(prefix))
print("carries via prefix:", from_prefix)
print("carries sequential:", carries(x, y, n))
```

```output
classes (pos 0..7): P G P P G P P K
prefix products   : P G G G G G G K
carries via prefix: [0, 0, 1, 1, 1, 1, 1, 1, 0]
carries sequential: [0, 0, 1, 1, 1, 1, 1, 1, 0]
```

## From sequential to parallel {#sec:parallel}

The sequential algorithm computes the prefix products one after another: depth $n$. But because $\then$ is associative, the product $x_0 \then \cdots \then x_i$ can be bracketed in any way — in particular, as a balanced tree of depth $\lceil \log_2 (i + 1) \rceil$. Computing *all* $n$ prefix products at once is the **parallel prefix** problem, solvable for any associative operation in depth $\Oh(\log n)$ \cite{ladner1980,blelloch1990}. Different networks trade the number of operations against the depth:

| network | idea | combine operations | depth |
|---|---|---|---|
| ripple (sequential) | left to right | $n - 1$ | $n - 1$ |
| Sklansky (1960) \cite{sklansky1960} | divide and conquer; each half's last prefix broadcast to the other half | $\tfrac{n}{2}\log_2 n$ | $\log_2 n$ |
| Kogge–Stone (1973) \cite{koggestone1973} | doubling: at round $j$ combine with the element $2^j$ positions down | $n\log_2 n - n + 1$ | $\log_2 n$ |
| Brent–Kung (1982) \cite{brentkung1982} | up-sweep a tree, then down-sweep | $\le 2n - 2 - \log_2 n$ | $2\log_2 n - 1$ |

The SDK builds each adder as an explicit gate-level circuit (gates AND, OR, XOR with two inputs) and counts gates and depth:

::: observation {#obs:adders title="Gate counts and depths of four adders" status="empirical" ledger="GIN-EXP-006"}
For $n$-bit addition, the circuits of `ginsdk.circuits` have the following (size, depth). All are correct exhaustively for $n \le 8$ and on random inputs to $n = 64$.

| $n$ | ripple-carry | Sklansky | Kogge–Stone | Brent–Kung |
|---|---|---|---|---|
| 4 | 17, 7 | 20, 6 | 23, 5 | 20, 6 |
| 16 | 77, 31 | 128, 10 | 179, 9 | 110, 14 |
| 64 | 317, 127 | 704, 14 | 1091, 13 | 488, 22 |
| 256 | 1277, 511 | 3584, 18 | 5891, 17 | 2018, 30 |
:::

::: proposition {#prop:ripple-count title="Ripple-carry cost" status="proved-here" ledger="GIN-PROP-021"}
The $n$-bit ripple-carry adder of `ginsdk.circuits` (a half adder at position $0$, full adders built from XOR, XOR, AND, AND, OR above it) has exactly $5n - 3$ gates and depth $2n - 1$.
:::

::: proof
$2 + 5(n - 1)$ gates. The carry out of position $0$ has depth $1$, and each full adder adds an AND followed by an OR to the carry path, so the carry out of position $n - 1$ has depth $1 + 2(n - 1)$; the sum bits are no deeper.
:::

How much better can depth get? Not much better than the prefix networks:

::: proposition {#prop:depth-lower title="Addition needs logarithmic depth" status="classical" ledger="GIN-PROP-059"}
Every circuit of fan-in-2 gates computing the carry out of $n$-bit addition has depth at least $\lceil \log_2(2n) \rceil = 1 + \lceil \log_2 n \rceil$.
:::

::: proof
The carry out depends on all $2n$ input bits (Proposition GIN-PROP-058's adversary argument). A gate of depth $d$ with fan-in 2 depends on at most $2^d$ inputs, so $2^d \ge 2n$.
:::

At $n = 256$ the lower bound is $9$; Kogge–Stone achieves $17$ — within a factor of two — at the price of more than four times as many gates as the ripple adder. Brent–Kung achieves $30$ with fewer than twice as many. This is the typical shape of a trade-off between *work* and *depth*, and it is the arithmetic instance of a theorem of the parent program: the same semantics computed by grammars of different shape has different cost (\cgt{CGT-THM-004}).

## How long are carry chains? {#sec:chains}

The ripple adder is slow only if carries actually travel far. On random inputs they usually do not.

::: observation {#obs:chains title="Mean longest carry chain" status="empirical" ledger="GIN-OBS-002"}
For random pairs of $n$-bit numbers, the mean length of the longest carry chain (a generate followed by the propagates it travels through) measured over 3,000 samples (1,000 for $n > 1024$) is $\log_2 n - c$ with $c$ between $0.66$ and $0.84$ for $n = 4, \ldots, 4096$; the class frequencies are $\Kk \approx \Pp/2 \approx \Gg \approx 1/4$. This agrees with the classical estimate $\log_2 n + \Oh(1)$ of Burks, Goldstine and von Neumann and of Knuth \cite{bgvn1946,knuth1978}; the constant depends on how a chain is counted.
:::

The reason is visible in the monoid: a chain continues only through propagates, each occurring with probability $1/2$, so a chain of length $\ell$ has probability about $2^{-\ell}$, and among $n$ starting points the longest is about $\log_2 n$. Asynchronous adders that detect completion exploit exactly this: on average they finish in $\Oh(\log n)$ gate delays even with a ripple structure. Worst-case design, however, must budget for a chain of length $n$.

## Addition is finite-state; multiplication is not {#sec:automatic}

The carry automaton has two states, whatever the length of the numbers. This puts addition in a very small class of computations.

::: theorem {#thm:automatic title="Addition is finite-state; multiplication is not" status="classical" ledger="GIN-THM-005"}
Fix a base $b \ge 2$ and read numerals least significant digit first, padded to equal length. (1) The graph of addition $\{(x, y, x + y)\}$ is recognized by a synchronous finite automaton, so $(\N, +)$ is an *automatic structure*. (2) The graph of multiplication is not synchronous-rational in any presentation in which addition is: otherwise $(\N, +, \times)$ would be automatic; every automatic structure has a decidable first-order theory; and the first-order theory of $(\N, +, \times)$ is undecidable.
:::

::: proof
(1) The carry automaton, reading triples of digits and checking the output digit, recognizes the graph. (2) Decidability of automatic structures is due to Hodgson \cite{hodgson1983} and Khoussainov and Nerode \cite{khoussainov1995} (see also Blumensath and Grädel \cite{blumensath2000}); the decidability of the theory of $(\N, +)$ via automata goes back to Büchi \cite{buchi1960}. The undecidability of the theory of $(\N, +, \times)$ follows from Gödel's and Church's work \cite{godel1931,church1936}.
:::

The theorem has classical refinements. Multiplication by a *fixed* constant $k$ is finite-state: the carry is bounded by $k$. Reduction modulo a fixed $m$ is finite-state, read most significant digit first (the divisibility automaton of Chapter 7). Comparison $x < y$ is finite-state. What is not finite-state is the product of two *unbounded* numbers: the "carry" of schoolbook multiplication grows with the length of the operands. In this book's vocabulary, the successor, addition, comparison, multiplication and division by constants, and reduction modulo constants live in the class of **regular** operational grammars over numerals; general multiplication does not.

## The CGT reading {#sec:cgt-carry}

Computational Grammar Theory calls a structure *arithmetically compilable* when every word of moves compiles to an element of a transition monoid that fits in $\Oh(1)$ machine words (\cgt{CGT-DEF-011}). The carry automaton is the cleanest arithmetic example: any word of digit pairs, however long, compiles to one of three elements. Carry-lookahead *is* this compilation, performed in parallel. Positional numerals themselves (Chapter 5) are the contrasting case: they compile to affine maps whose coefficients grow with the word. The difference between a finite and an infinite transition monoid is the difference between addition, which a finite automaton can do, and multiplication, which it cannot (\ledger{GIN-REI-005}).

::: conjecture {#conj:m-assoc title="Re-association as a mechanism" status="conjecture" ledger="GIN-CONJ-001"}
CGT's taxonomy of mechanisms of advantage (\cgt{CGT-DEF-009}) should include **M-ASSOC**: when a computation is a product in an associative operation, re-associating a right-linear evaluation into a balanced tree trades work for depth (prefix adders, balanced numeral evaluation, parallel prefix, repeated squaring), and changes *total work* only together with a cost model that rewards balanced operands. Whether M-ASSOC is genuinely distinct from CGT's grammar-shape effect or merely names it is open (\ledger{GIN-OPEN-004}).
:::

::: exercise {#ex:carry-classes}
Classify the positions of $x = 10110111_2$, $y = 01001001_2$ and compute all carries by prefix products. What is the sum?
:::

::: solution {of="ex:carry-classes"}
Positions 0–7 (low to high): $x$ bits $1,1,1,0,1,1,0,1$; $y$ bits $1,0,0,1,0,0,1,0$; classes $\Gg, \Pp, \Pp, \Pp, \Pp, \Pp, \Pp, \Pp$. Every prefix product is $\Gg$, so carries into positions $1..8$ are all $1$; sum bits are $0$ everywhere and the carry out is $1$: $183 + 73 = 256 = 100000000_2$.
:::

::: exercise {#ex:carry-assoc}
Verify associativity of $\then$ by checking all $27$ triples, and show that the monoid has no inverses except for $\Pp$.
:::

::: solution {of="ex:carry-assoc"}
Associativity holds because both bracketings equal the last non-$\Pp$ element of the triple (or $\Pp$ if there is none). $\Kk \then y = \Pp$ has no solution ($\Kk \then y \in \{\Kk, \Gg\}$), and likewise for $\Gg$: constant maps are not invertible.
:::

::: exercise {#ex:carry-const}
Design a finite automaton that multiplies by $3$: reading $x$ least significant bit first, it outputs the bits of $3x$. How many states does it need?
:::

::: solution {of="ex:carry-const"}
$3x = x + 2x$: at position $i$ add $x_i$, $x_{i-1}$ and the carry. The state must remember the previous input bit and the carry, which is at most $1$ (bit sum $\le 3$): states $(x_{i-1}, c) \in \{0,1\}^2$, so at most $4$ states (fewer suffice after minimization), plus a final flush of the remaining state.
:::

::: exercise {#ex:carry-lb}
What is the lower bound of Proposition \ref{prop:depth-lower} for $n = 64$, and how far from it are the four adders of Observation \ref{obs:adders}?
:::

::: solution {of="ex:carry-lb"}
$1 + \log_2 64 = 7$. Ripple $127$, Sklansky $14$, Kogge–Stone $13$, Brent–Kung $22$. The prefix adders are within a factor of about $2$ to $3$; ripple is about $18$ times the bound.
:::

::: summary
- Binary addition is a two-state transducer; its transitions form the carry monoid $\{\Kk, \Pp, \Gg\}$, in which $\Pp$ is the identity and every element is idempotent.
- Carries are prefix products; associativity lets them be computed in parallel in depth $\Oh(\log n)$, at the price of more gates. Depth below $1 + \log_2 n$ is impossible.
- Measured: ripple $5n - 3$ gates, depth $2n - 1$; at $n = 256$, Kogge–Stone 5891 gates, depth 17.
- Random carry chains are about $\log_2 n$ long.
- Addition is finite-state and $(\N, +)$ is automatic; multiplication is not finite-state (classical).
:::
