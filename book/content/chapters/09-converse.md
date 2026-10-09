---
title: "Inverse Operations as Converse Relations"
status: mixed
statusnote: Relational converses and the coset structure of linear equations are classical; the admissibility vocabulary (no solution, unique, non-unique), the repair taxonomy and admissibility closure are this book's framework.
description: Subtraction, division, roots, logarithms and modular inverses as converse problems; the trichotomy no solution / unique / non-unique; why solution sets of linear converse problems are cosets of a kernel and those of non-linear ones need not be; seven ways systems give an inadmissible expression a value; and number systems as admissibility closures.
epigraph: "Undefined is not an answer. It is the name of a question that has not yet been asked precisely: no solution, or too many?"
---

::: objectives
- Define the converse problem of a forward operation and classify every inverse expression as having no solution, a unique solution, or several.
- Prove that the solution set of a linear converse problem is empty or a coset of a kernel, and give a non-linear converse problem for which this fails.
- Name the seven ways in which mathematical and computational systems give inadmissible expressions a value, and the cost of each.
- Read the constructions $\N \to \Z \to \Q$ as admissibility closures that keep an unanswered converse problem as data.
:::

## The converse problem {#sec:converse}

Every inverse operation of arithmetic is defined by an equation involving a forward operation:

$$
a - b = c \iff b + c = a, \qquad a / b = c \iff b \cdot c = a, \qquad \sqrt{a} = c \iff c \cdot c = a \ (\text{and } c \ge 0), \qquad \log a = c \iff e^c = a .
$$

The left-hand sides are written as if they named a single value. The right-hand sides are equations, and an equation may have no solution, exactly one, or several. This chapter takes the right-hand sides as the definition.

::: definition {#def:converse title="Converse problem" status="definition" ledger="GIN-DEF-015"}
For a forward operation $\circ$ on a carrier $A$, the **converse problem** at $(a, b)$ is the solution set
$$
\Sol_\circ(a, b) = \{\, c \in A : b \circ c = a \,\}. \label{eq:sol}
$$
Division asks for $\Sol_\times(a, b)$, subtraction for $\Sol_+(a, b)$, the square root for $\{c : c \cdot c = a\}$, the logarithm for $\{c : e^c = a\}$, and the modular inverse of $b$ for $\Sol_\times(1, b)$ in $\Z/n$.
:::

::: definition {#def:admissibility title="Converse admissibility" status="definition" ledger="GIN-DEF-016"}
An inverse expression is
- **inadmissible: no solution** if $\Sol = \varnothing$;
- **admissible** if $|\Sol| = 1$, and then it denotes the unique solution;
- **inadmissible: non-unique** if $|\Sol| \ge 2$.

A **branch** (principal value, selection) is a choice function on non-unique solution sets that turns a non-unique converse into a function: $\sqrt{\cdot}$ selects the non-negative root; $\lfloor \cdot \rfloor$-division selects the quotient whose remainder is non-negative.
:::

Every inadmissibility in this book is one of these two kinds, and the distinction is not cosmetic. *No solution* means the question asks for something that does not exist; any answer is a fiction. *Non-unique* means the question does not determine its answer; any single answer is a choice. A system that reports both as "undefined" has lost the information needed to repair either.

| expression | carrier | equation | solutions | verdict |
|---|---|---|---|---|
| $0 - 1$ | $\N$ | $1 + c = 0$ | $\varnothing$ | no solution |
| $0 - 1$ | $\Z$ | $1 + c = 0$ | $\{-1\}$ | admissible |
| $7 / 2$ | $\Z$ | $2c = 7$ | $\varnothing$ | no solution |
| $7 / 2$ | $\Q$ | $2c = 7$ | $\{7/2\}$ | admissible |
| $1 / 0$ | $\Q$ | $0 \cdot c = 1$ | $\varnothing$ | no solution |
| $0 / 0$ | $\Q$ | $0 \cdot c = 0$ | $\Q$ | non-unique |
| $2 / 4$ | $\Z/6$ | $4c \equiv 2$ | $\{2, 5\}$ | non-unique |
| $\sqrt{2}$ | $\Q$ | $c^2 = 2$ | $\varnothing$ | no solution |
| $\sqrt{4}$ | $\Z$ | $c^2 = 4$ | $\{2, -2\}$ | non-unique; the branch selects $2$ |
| $\sqrt{-1}$ | $\R$ | $c^2 = -1$ | $\varnothing$ | no solution |
| $\log 1$ | $\C$ | $e^c = 1$ | $\{2\pi i k : k \in \Z\}$ | non-unique (infinitely many) |
| $\log 0$ | $\C$ | $e^c = 0$ | $\varnothing$ | no solution |

The SDK computes these solution sets exactly:

```python run
from ginsdk import converse as C

for s in [C.subtract(0, 1, "N"), C.divide(7, 2, "Z"), C.divide(1, 0, "Q"), C.divide(0, 0, "Q"),
          C.divide_mod(2, 4, 6), C.square_root(2, "Q"), C.square_root(4, "Z"), C.logarithm(1, "C")]:
    print(f"{s.carrier:4s} {s.equation:18s} {s.kind:9s} {s.description}")
```

```output
N    1 + c = 0          no-solution ∅
Z    2 · c = 7          no-solution ∅
Q    0 · c = 1          no-solution ∅
Q    0 · c = 0          non-unique every c in Q
Z/6  4 · c ≡ 2 (mod 6)  non-unique c ∈ {2, 5} = 2 + Ann(4)
Q    c · c = 2          no-solution ∅
Z    c · c = 4          non-unique c ∈ {2, -2}
C    e^c = 1            non-unique c = Ln 1 + 2πik, k ∈ Z
```

## Linear converse problems: cosets of a kernel {#sec:cosets}

Subtraction, division by a fixed element, the modular inverse and linear Diophantine equations have something in common: the forward map $c \mapsto b \circ c$ is a *homomorphism* of additive groups. For such maps the shape of every solution set is forced.

::: theorem {#thm:coset title="Converse of a homomorphism" status="classical" ledger="GIN-THM-007"}
Let $f : G \to H$ be a homomorphism of abelian groups and $a \in H$. The solution set $\{c \in G : f(c) = a\}$ is either empty or a coset $c_0 + \ker f$. Hence:
1. **image condition**: a solution exists iff $a \in f(G)$;
2. **kernel condition**: when solutions exist, there are exactly $|\ker f|$ of them; the solution is unique iff $\ker f = \{0\}$.
:::

::: proof
If $f(c_0) = a$, then $f(c) = a \iff f(c - c_0) = 0 \iff c - c_0 \in \ker f$.
:::

This is the theorem of every first course in linear algebra — the general solution of $Ax = a$ is a particular solution plus the null space — and it is the whole explanation of why there are *two* kinds of inadmissibility for linear converse problems and no others: the image condition can fail (no solution) and the kernel condition can fail (non-unique). Division is the converse of $c \mapsto b \cdot c$, which is additive in $c$; Chapter 16 specializes Theorem \ref{thm:coset} to rings and obtains the classification of $1/0$ and $0/0$.

For converse problems that are *not* linear, the solution set can have any shape.

::: counterexample {#neg:nonlinear title="Solution sets of converse problems need not be cosets" status="counterexample" ledger="GIN-NEG-019"}
In $\Z/8$ the equation $c \cdot c = 1$ has the four solutions $\{1, 3, 5, 7\}$, and $c \cdot c = 4$ has the two solutions $\{2, 6\}$. The two solution sets have different sizes, so they are not cosets of a common subgroup: squaring is not a homomorphism, and Theorem \ref{thm:coset} does not apply.
:::

```python run
from ginsdk.converse import converse_finite

sq = lambda b, c: (c * c) % 8           # the forward map c -> c*c (b is unused)
for a in range(8):
    s = converse_finite(sq, range(8), a, None, name="Z/8")
    print(f"c*c = {a} (mod 8): {s.kind:9s} {s.solutions}")
```

```output
c*c = 0 (mod 8): non-unique [0, 4]
c*c = 1 (mod 8): non-unique [1, 3, 5, 7]
c*c = 2 (mod 8): no-solution []
c*c = 3 (mod 8): no-solution []
c*c = 4 (mod 8): non-unique [2, 6]
c*c = 5 (mod 8): no-solution []
c*c = 6 (mod 8): no-solution []
c*c = 7 (mod 8): no-solution []
```

## Seven repairs {#sec:repairs}

When an inverse expression is inadmissible, mathematics and computation have developed exactly seven ways of giving it a value anyway, or of refusing to. Each changes the grammar, and each gives something up.

::: definition {#def:repairs title="Repairs of inadmissibility" status="proposed" ledger="GIN-DEF-017"}
1. **Extension** — enlarge the carrier so that the solution set becomes non-empty: $\N \to \Z$ for subtraction, $\Z \to \Q$ for division by non-zero elements, $\R \to \C$ for square roots of negatives, $\R \to \R \cup \{\infty\}$ for $1/0$.
2. **Selection** — choose one element of a non-unique solution set: principal branches; Euclidean quotients with conditions on the remainder.
3. **Restriction** — remove the bad inputs from the domain: $b \ne 0$; units only.
4. **Quotient** — identify elements so that the operation becomes total: $\Z \to \Z/2^w$ makes $0 - 1 = 2^w - 1$.
5. **Totalization** — define a value by convention without claiming that it solves the converse problem: $x / 0 := 0$ in meadows and in Lean's mathlib; AArch64 integer division by zero returns $0$; RISC-V returns $-1$; truncated subtraction $0 \monus 1 := 0$.
6. **Absorption** — adjoin a special element that absorbs further operations: NaN; the wheel element $\bot$; `Option` and `Result` types.
7. **Signal** — refuse to produce a value and transfer control: hardware traps, exceptions, panics, compile-time errors.
:::

| repair | what is kept | what is given up | typical home |
|---|---|---|---|
| extension | all identities of the old structure | the old carrier; sometimes order (ℂ) or other laws (∞) | mathematics |
| selection | functionality | symmetry between the solutions; continuity at branch cuts | analysis, integer division |
| restriction | everything, on a smaller domain | totality | algebra textbooks, preconditions |
| quotient | totality, the ring laws | order; the distinction between identified values | hardware integers, ℤ/n |
| totalization | totality, often the ring laws | the converse reading ($b \cdot (a/b) = a$ fails at $b = 0$) | proof assistants, some ISAs |
| absorption | totality; the information that something failed | equality (NaN ≠ NaN), some laws ($0 \cdot x = 0$ in wheels) | IEEE 754, wheels, typed APIs |
| signal | the meaning of every value produced | totality; control flow | x86, Java, Rust, Python |

The table is a reinterpretation of familiar facts, but it makes one point that is easy to miss: *every* repair gives something up. There is no free way to make division total. Chapter 18 proves this for division by zero in the strongest form we can state: every system that gives $1/0$ a value abandons the ring laws, the converse reading of division, or $0 \ne 1$ (\ledger{GIN-THM-004}).

## Number systems as admissibility closures {#sec:closures}

Read in this vocabulary, the familiar tower $\N \subset \Z \subset \Q \subset \R \subset \C$ is a sequence of extensions, each made so that a family of converse problems acquires solutions.

::: definition {#def:adm-closure title="Admissibility closure" status="proposed" ledger="GIN-DEF-019"}
Given $A \subseteq U$ and a family of converse problems, the **admissibility closure** of $A$ in $U$ is the least $B$ with $A \subseteq B \subseteq U$ such that every converse problem with data in $B$ that has a solution in $U$ has one in $B$.
:::

For example, the closure of $\N$ in $\Q$ under subtraction is $\Z$; the closure of $\Z$ in $\C$ under division by non-zero elements is $\Q$; the closure of $\Q$ in $\R$ under the field operations and square roots of positive elements is the field of real constructible numbers. The classical constructions do more than find the closure inside a given universe: they *build* the new elements out of the unanswered problems themselves.

::: proposition {#prop:grothendieck title="The integers and rationals keep unanswered converse problems as data" status="reinterpretation" ledger="GIN-PROP-017"}
$\Z$ is the set of pairs $(a, b) \in \N^2$ modulo $(a, b) \sim (c, d) \iff a + d = b + c$, with $(a, b)$ standing for the answer to "$a - b$"; $\Q$ is the set of pairs $(a, b) \in \Z \times (\Z \setminus \{0\})$ modulo $(a, b) \sim (c, d) \iff a d = b c$, with $(a, b)$ standing for "$a / b$". In each case the new element *is* the unanswered converse problem, kept as data, and two problems are identified when they must have the same answer. The exclusion $b \ne 0$ in the second construction is forced: admitting $(0, 0)$ breaks transitivity (\ledger{GIN-THM-006}).
:::

The first construction is the Grothendieck group of the monoid $(\N, +)$; the second is the field of fractions of the integral domain $\Z$. Both are classical. The reading — that an integer is a subtraction problem and a rational a division problem, up to having the same answer — is how this book connects them to the converse vocabulary. It also explains why the second construction has an exception and the first has none: the problem $b + c = a$ always has *at most one* solution in a cancellative monoid, but $b \cdot c = a$ has *every* $c$ as a solution when $a = b = 0$, and a class containing such a problem would have to equal every other class.

::: openproblem {#open:adm-cost title="The cost of admissibility" status="open" ledger="GIN-OPEN-002"}
Deciding whether $a / b$ is admissible in $\Z$ means deciding $b \mid a$, which costs about as much as dividing; deciding whether $b$ is invertible in $\Z/n$ costs a gcd. When is deciding admissibility asymptotically cheaper than computing the result, and when is it as hard? Is there a natural converse problem where admissibility is hard to decide but the solution, when it exists, is easy to compute?
:::

::: exercise {#ex:cv-classify}
Classify, with the solution set: (a) $5 - 8$ in $\N$; (b) $6 / 4$ in $\Z/10$; (c) $3 / 4$ in $\Z/10$; (d) $\sqrt{9}$ in $\N$; (e) $\log(-1)$ in $\R$ and in $\C$.
:::

::: solution {of="ex:cv-classify"}
(a) $8 + c = 5$: no solution in $\N$. (b) $4c \equiv 6 \pmod{10}$: $\gcd(4, 10) = 2 \mid 6$, solutions $\{4, 9\}$: non-unique. (c) $4c \equiv 3$: $2 \nmid 3$, no solution. (d) $c^2 = 9$ in $\N$: $\{3\}$, admissible (the negative root is not in $\N$). (e) In $\R$: $e^c > 0$, no solution. In $\C$: $\{i\pi + 2\pi i k\}$, infinitely many: non-unique; the principal branch selects $i\pi$.
:::

::: exercise {#ex:cv-coset}
Use Theorem \ref{thm:coset} to describe all integer solutions of $6x + 10y = 4$.
:::

::: solution {of="ex:cv-coset"}
The map $(x, y) \mapsto 6x + 10y$ is a homomorphism $\Z^2 \to \Z$ with image $2\Z$ (Bézout), so $4$ is in the image. A particular solution: $(x, y) = (-6, 4)$, since $-36 + 40 = 4$. The kernel is $\{(5t, -3t) : t \in \Z\}$. All solutions: $(-6 + 5t, 4 - 3t)$.
:::

::: exercise {#ex:cv-sq}
How many solutions does $c^2 \equiv 1 \pmod{n}$ have for $n = 2, 4, 8, 16, 15$? Why does Theorem \ref{thm:coset} not predict these counts?
:::

::: solution {of="ex:cv-sq"}
$n = 2$: 1; $n = 4$: 2 ($1, 3$); $n = 8$: 4; $n = 16$: 4 ($1, 7, 9, 15$); $n = 15$: 4 ($1, 4, 11, 14$). Squaring is not additive, so the solutions do not form cosets of a kernel; the counts come from the structure of the unit group (Chapter 29).
:::

::: exercise {#ex:cv-repair}
Name the repair in each case: (a) Python's `math.sqrt(-1)` raises `ValueError`; (b) `cmath.sqrt(-1)` returns `1j`; (c) `numpy.sqrt(-1.0)` returns `nan` with a warning; (d) a database's `NULLIF(x, 0)` used as a divisor makes `y / NULLIF(x, 0)` return `NULL`.
:::

::: solution {of="ex:cv-repair"}
(a) Signal. (b) Extension (to $\C$) plus selection (the principal root $i$, not $-i$). (c) Absorption (NaN), with a non-fatal signal. (d) Absorption: SQL's `NULL` propagates through the division.
:::

::: summary
- Inverse operations are converse problems; their solution sets classify every inverse expression as no solution, unique, or non-unique.
- For linear converse problems the solution set is empty or a coset of a kernel: the two failures are image failure and kernel failure. Non-linear converses ($c^2 = a$) need not behave this way.
- Seven repairs — extension, selection, restriction, quotient, totalization, absorption, signal — give inadmissible expressions a value or refuse to; each gives something up.
- $\Z$ and $\Q$ are admissibility closures that keep unanswered subtraction and division problems as data.
:::
