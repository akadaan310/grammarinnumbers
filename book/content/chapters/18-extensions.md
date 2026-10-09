---
title: "Giving $1/0$ a Value: What Every Extension Gives Up"
status: mixed
statusnote: The systems surveyed are classical or standard; the trilemma formulation, the pair theorem and the exact law census are this book's, and the census is reproducible.
description: The extension trilemma — every system that gives 1/0 a value gives up the ring laws, the converse reading of division, or 0 ≠ 1; the projective line, the extended reals, wheels, meadows, proof assistants, IEEE 754 and instruction sets examined one by one; fractions as pairs, where every indeterminate form computes the same null pair; an exact census of the laws each system keeps; and Brahmagupta's 0/0 = 0 read as a selection.
epigraph: "There is no free way to divide by zero. There are only different bills."
---

::: objectives
- State the extension trilemma and derive it from the fact that no non-trivial ring inverts zero.
- For each of nine systems — fields, the projective line, the extended reals, wheels, meadows, proof assistants, IEEE 754, AArch64 and RISC-V — say what $1/0$ and $0/0$ are, and which laws are kept, weakened or lost.
- Prove that in the arithmetic of fractions as pairs, every indeterminate form computes the null pair $(0, 0)$, and that this pair cannot be an element.
- Read an exact census of ten laws across eight implemented systems, and interpret its counterexamples.
:::

## The trilemma {#sec:trilemma}

Theorem GIN-THM-003 showed that a ring with $0 \ne 1$ has no element $z$ with $0 \cdot z = 1$. Its proof used three ingredients: the ring laws that force $0 \cdot z = 0$; the reading of "$1/0$" as "the $z$ with $0 \cdot z = 1$"; and $0 \ne 1$. A system that assigns $1/0$ a value must therefore drop one of them.

::: theorem {#thm:trilemma title="The extension trilemma for 1/0" status="reinterpretation" ledger="GIN-THM-004"}
Any system that gives $1/0$ a value gives up at least one of:
- **(A)** the ring laws that force $0 \cdot c = 0$ (distributivity with additive inverses);
- **(B)** the *converse reading* of division — that $a/b$ denotes a $c$ with $b \cdot c = a$;
- **(C)** $0 \ne 1$.

Every system in the literature and in hardware takes route A or route B, or refuses to give a value (it *signals*); none takes route C, which yields the zero ring.
:::

| system | $1/0$ | $0/0$ | route | what gives way |
|---|---|---|---|---|
| $\Q$, $\R$, $\C$ (fields) | no solution | non-unique | restriction | division is defined only for $b \ne 0$ |
| projective line $\Q \cup \{\infty\}$, Riemann sphere $\C \cup \{\infty\}$ | $\infty$ | undefined | A | $0 \cdot \infty$, $\infty \pm \infty$, $\infty/\infty$, $0/0$ undefined; no field structure, no order |
| extended reals $\R \cup \{\pm\infty\}$ | usually undefined | undefined | A | $0 \cdot (\pm\infty)$ and $\infty - \infty$ undefined; $\pm\infty$ are not field elements |
| IEEE 754 | $\pm\infty$, flag divideByZero | NaN, flag invalid | B | $0 \times \infty = \NaN$, so $\infty$ does not solve $0 \cdot c = 1$; $\NaN \ne \NaN$ |
| meadows (Bergstra & Tucker) | $0$ | $0$ | B | $x \cdot x^{-1} = 1$ only for $x \ne 0$; all ring axioms kept |
| Lean's mathlib, Isabelle/HOL | $0$ | $0$ | B | theorems such as $a \cdot a^{-1} = 1$ carry the hypothesis $a \ne 0$ |
| wheels (Carlström) | $\infty = /0$ | $\bot$ (absorbing) | A | $0 \cdot x = 0$ fails; distributivity weakened |
| AArch64 `sdiv`/`udiv` | $0$ | $0$ | B (totalization) | the result is not a quotient of anything |
| RISC-V `div`/`divu` | $-1$ / $2^w - 1$ | the same | B (totalization) | as above |
| x86-64 `idiv`, Java, Rust, Go, Python | trap / exception / panic | the same | signal | no value is produced |
| ISO C (integers) | undefined behaviour | the same | none | the program has no meaning |

The rest of this chapter examines the rows, and then checks the table by computation.

## Route A: adjoining infinity {#sec:route-a}

**The projective line.** Adjoin to $\Q$ (or $\R$, $\C$) a single new element $\infty$ with $x/0 = \infty$ for $x \ne 0$, $x/\infty = 0$, $x + \infty = \infty$ for $x \ne \infty$, and $x \cdot \infty = \infty$ for $x \ne 0$. Geometrically, $\R \cup \{\infty\}$ is a circle and $\C \cup \{\infty\}$ the Riemann sphere; Möbius transformations $z \mapsto (az + b)/(cz + d)$ act on them as bijections, which is the main reason the construction exists. The price: the expressions $0 \cdot \infty$, $\infty + \infty$, $\infty - \infty$, $\infty / \infty$ and $0/0$ have no value. The projective line is not a ring, and it has no order compatible with its operations: $\infty$ is both "very large" and "very negative".

**The extended reals.** Adjoin two elements $\pm\infty$, keeping the order: $-\infty < x < +\infty$. Now $x + (+\infty) = +\infty$ and $x \cdot (+\infty) = +\infty$ for $x > 0$; but $+\infty - \infty$ and $0 \cdot \infty$ are undefined, and so, usually, is $x/0$ — which sign of infinity would it be? The extended reals are indispensable in measure theory and optimization (where $\sup \varnothing = -\infty$ is a useful convention), and they are not a field.

**Wheels.** Carlström's wheels \cite{carlstrom2004} make division total by replacing it with a unary operation $/x$ (an involution: $//x = x$, multiplicative: $/(xy) = /x \cdot /y$) and writing $x/y$ for $x \cdot /y$. Addition and multiplication remain commutative monoids, but they are no longer required to form a ring; the distributive law is weakened to $(x + y)z + 0z = xz + yz$. The *wheel of fractions* of $\Z$ consists of the classes of pairs $[a, b]$, where $[a, b] = [sa, sb]$ for non-zero integers $s$, with $[a, b] + [c, d] = [ad + bc, bd]$, $[a, b][c, d] = [ac, bd]$ and $/[a, b] = [b, a]$. Its elements are the rationals, $\infty = [1, 0]$ and $\bot = [0, 0]$, and
$$
1/0 = \infty, \qquad 0/0 = \bot, \qquad 0 \cdot \infty = \bot, \qquad \infty + \infty = \bot, \qquad \bot + x = \bot .
$$
The element $\bot$ absorbs every operation, like a NaN with algebraic laws. The ring identities $0 \cdot x = 0$, $x - x = 0$ and $x/x = 1$ fail exactly at elements that involve $\infty$ or $\bot$.

::: implementation {#imp:wheel title="The wheel of fractions of ℤ satisfies the wheel axioms" status="implementation" ledger="GIN-IMP-007"}
`ginsdk.totalized.WheelZ` implements the wheel of fractions of $\Z$. All fourteen axiom instances of a wheel — the monoid laws for $+$ and $\cdot$, $//x = x$, $/(xy) = /x/y$, $(x + y)z + 0z = xz + yz$, $(x + yz)/y = x/y + z + 0y$, $0 \cdot 0 = 0$, $(x + 0y)z = xz + 0y$, $/(x + 0y) = /x + 0y$ and $0/0 + x = 0/0$ — hold on every tuple drawn from an eight-element sample containing $0, 1, -1, 2, \tfrac12, -3, \infty, \bot$. The axiom list was taken from a secondary source (the Wikipedia article on wheel theory, which cites Carlström); the primary paper was not read (\ledger{GIN-OPEN-005}).
:::

## Route B: dropping the converse reading {#sec:route-b}

**Meadows** \cite{bergstra2007} keep every axiom of a commutative ring and add a total inverse operation with two axioms, $(x^{-1})^{-1} = x$ and $x \cdot (x \cdot x^{-1}) = x$. Together they force $0^{-1} = 0$: applying the second axiom to $x = 0^{-1}$ and using the first gives $0^{-1} = 0^{-1}(0^{-1} \cdot 0) = 0$. The rationals with $0^{-1} := 0$ form a meadow. Division $x/y := x \cdot y^{-1}$ is then total, with $x/0 = 0$. (A later variant, *common meadows*, instead sends $0^{-1}$ to an absorbing error element, in the spirit of wheels and NaN \cite{bergstraponse2015}.) All ring laws hold; the price is that $y \cdot (x/y) = x$ fails at $y = 0$ — division by zero no longer means "the solution of $0 \cdot c = x$".

**Proof assistants** adopt the same convention for the same reason. Lean's mathlib defines $0^{-1} = 0$ in every field and division ring, so that the functions $x \mapsto x^{-1}$ and $(x, y) \mapsto x/y$ are total; lemmas that need the converse reading carry an explicit hypothesis, as in "$a \ne 0 \Rightarrow a \cdot a^{-1} = 1$" \cite{mathlib2020}. Isabelle/HOL's division rings have the axiom $\mathit{inverse}\ 0 = 0$, from which $a / 0 = 0$ is derived \cite{isabelle_fields}. The convention is a *totalization*: it makes formal statements shorter and machine reasoning simpler, at the cost of making $x/0$ a number that solves nothing. The converse vocabulary of this book is exactly what a formalization needs to state admissibility explicitly (\ledger{GIN-OPEN-011}).

**IEEE 754** returns $\pm\infty$ for a finite non-zero number divided by zero, with the sign determined by the signs of the operands (including the sign of zero), and raises the divideByZero flag; it returns NaN for $0/0$ and raises *invalid*. These are limit-motivated values: $\lim_{x \to 0^+} 1/x = +\infty$.

::: proposition {#prop:ieee-not-converse title="IEEE division by zero is not the converse of IEEE multiplication" status="classical" ledger="GIN-PROP-015"}
For finite non-zero $x$, IEEE 754 gives $x/(\pm 0) = \pm\infty$ and $0/0 = \NaN$. But $0 \times (\pm\infty) = \NaN$ and $0 \times c = \pm 0$ for every finite $c$; so no IEEE datum $c$ satisfies $0 \otimes c = 1$. The infinity returned by $1/0$ records the side from which zero was approached (Kahan's signed zero \cite{kahan1987}), not a solution.
:::

**Instruction sets** take route B in its barest form. AArch64's `sdiv` returns $0$ for a zero divisor and RISC-V's `div` returns $-1$ (all bits set), with no flag and no trap. Chapter 19 shows that $-1$ is precisely what a divider circuit computes if it never tests its divisor — the RISC-V specification's rationale says as much \cite{riscv} — and Chapter 24 measures both under emulation.

## Fractions as pairs: the null pair {#sec:pairs}

The construction of $\Q$ from pairs (Chapter 9) shows *why* there is a second failure. Take all pairs of integers, including those with second component zero, and see how far the arithmetic of fractions extends.

::: theorem {#thm:pairs title="Fractions as pairs: ∞ can be adjoined, 0/0 cannot" status="proved-here" ledger="GIN-THM-006"}
On $\Z^2$ let $(a, b) \sim (c, d)$ iff $ad = bc$, and define $(a,b) + (c,d) = (ad + bc, bd)$, $(a, b)\cdot(c, d) = (ac, bd)$, $(a, b)/(c, d) = (ad, bc)$.
1. $\sim$ is reflexive and symmetric on $\Z^2$. On $\Z^2 \setminus \{(0, 0)\}$ it is an equivalence relation whose classes are the points of the projective line $\Q \cup \{\infty\}$, where $\infty$ is the single class of all $(a, 0)$ with $a \ne 0$.
2. $(0, 0)$ is related to *every* pair, so on $\Z^2$ transitivity fails: $(1, 0) \sim (0, 0) \sim (0, 1)$ but $(1, 0) \not\sim (0, 1)$. Admitting "$0/0$" as a pair would identify everything.
3. The operations are well defined on classes, and the result is the null pair $(0, 0)$ exactly in the cases $\infty + \infty$ (hence $\infty - \infty$), $0 \cdot \infty$, $0/0$ and $\infty/\infty$; every other combination of elements of $\Q \cup \{\infty\}$ is defined. In particular $1/0 = \infty$ and $1/\infty = 0$.
:::

::: proof
(1) Reflexivity and symmetry are immediate. Transitivity for $p = (a, b) \sim q = (c, d) \sim r = (e, f)$ with $q \ne (0, 0)$: if $d \ne 0$, from $ad = bc$ and $cf = de$ we get $adf = bcf = bde$, so $d(af - be) = 0$ and $af = be$. If $d = 0$ then $c \ne 0$; $ad = bc$ gives $b = 0$ and $cf = de$ gives $f = 0$, so $af = 0 = be$. (2) $a \cdot 0 = 0 \cdot b$ for every $(a, b)$. (3) Scaling one operand by $k \ne 0$ scales both components of each result by $k$, so classes map to classes and the null pair to itself. A sum is null iff $bd = 0$ and $ad + bc = 0$; if $b = 0$ then $a \ne 0$ forces $d = 0$, so both operands are $\infty$. A product is null iff $ac = 0$ and $bd = 0$ with neither operand null: one factor is $0$ and the other $\infty$. A quotient is null iff $ad = 0$ and $bc = 0$: either $a = c = 0$ ($0/0$) or $b = d = 0$ ($\infty/\infty$).
:::

So in the arithmetic of pairs, **every indeterminate form computes the same object — the null pair — and the null pair is exactly the one pair that cannot be an element of the quotient.** The projective line is what remains when that pair is excluded; the wheel of fractions is what one obtains by *keeping* it as an absorbing element $\bot$, at the price of the ring laws. The pair-level statement is elementary; it is not found in the sources reviewed, it is very probably folklore, and no priority is claimed (\ledger{GIN-THM-006}).

```python run
from ginsdk.converse import pair_of, pair_add, pair_mul, pair_div, Pair

def show(p):
    p = p.normal()
    return "(0,0) NULL" if (p.a, p.b) == (0, 0) else "∞" if p.b == 0 else f"{p.a}/{p.b}" if p.b != 1 else str(p.a)

inf, zero, one = Pair(1, 0), Pair(0, 1), Pair(1, 1)
for label, r in [("1/0", pair_div(one, zero)), ("1/∞", pair_div(one, inf)), ("0/0", pair_div(zero, zero)),
                 ("∞/∞", pair_div(inf, inf)), ("0·∞", pair_mul(zero, inf)), ("∞+∞", pair_add(inf, inf)), ("∞+1", pair_add(inf, one))]:
    print(f"{label:4s} = {show(r)}")
```

```output
1/0  = ∞
1/∞  = 0
0/0  = (0,0) NULL
∞/∞  = (0,0) NULL
0·∞  = (0,0) NULL
∞+∞  = (0,0) NULL
∞+1  = ∞
```

## The census {#sec:census}

The claims of the table in §\ref{sec:trilemma} can be checked by computation, on finite samples, for systems that can be implemented exactly. The SDK module `ginsdk.totalized` implements eight of them and evaluates ten laws on every tuple drawn from a fixed sample of each (six to eleven elements, including the special elements of each system). An instance *holds*, *fails*, or is *undefined* (some side is undefined in a partial system). For IEEE binary16, laws compare data: $+0$ and $-0$ are different data, and NaN is treated as equal to NaN.

::: observation {#obs:census title="Which laws each way of dividing by zero keeps" status="empirical" ledger="GIN-EXP-015"}
"ok" means no failure and nothing undefined; "ok\*" means no failure, but some instances undefined; "×k" means $k$ failing instances.

| system | $1/0$ | $0/0$ | $(x{+}y){+}z$ | $x(y{+}z)$ | $0x = 0$ | $x - x = 0$ | $x/x = 1$ | $y(x/y) = x$ | $(x/y)/z = x/(yz)$ | $(x{+}y)/z$ |
|---|---|---|---|---|---|---|---|---|---|---|
| field $\Q$ | undef. | undef. | ok | ok | ok | ok | ok\* | ok\* | ok\* | ok\* |
| meadow $\Q$ | $0$ | $0$ | ok | ok | ok | ok | ×1 | ×6 | ok | ok |
| wheel of $\Z$ | $\infty$ | $\bot$ | ok | ×45 | ×2 | ×2 | ×3 | ×21 | ok | ×45 |
| projective line | $\infty$ | undef. | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* |
| extended rationals | undef. | undef. | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* | ok\* |
| IEEE binary16 | $\infty$ | NaN | ×8 | ×94 | ×4 | ×2 | ×4 | ×49 | ×67 | ×123 |
| 8-bit RISC-V | $-1$ | $-1$ | ok | ok | ok | ok | ×1 | ×35 | ×111 | ×140 |
| 8-bit AArch64 | $0$ | $0$ | ok | ok | ok | ok | ×1 | ×35 | ×23 | ×76 |

Every system that makes division total — meadow, wheel, IEEE, RISC-V, AArch64 — fails the converse law $y(x/y) = x$; every system that keeps it (where defined) leaves some quotients undefined. The census is exact and reproducible (`experiments/exp015_law_census.py`).
:::

Three remarks prevent misreading the table. First, it counts failures on a *sample*, so the numbers are not frequencies; what matters is zero versus non-zero, and the counterexamples. Second, for the integer instruction sets most failures of the division laws are caused by *truncation*, not by zero: $y(x/y) = x$ fails for $x = 3, y = 2$ because $3/2$ truncates to $1$ — a selection (Chapter 19) — while the zero-divisor convention adds its own failures, such as $x/x = 1$ at $x = 0$. Third, the IEEE failures of $0 \cdot x = 0$ come from signed zeros and NaN: $0 \cdot (-1) = -0$ is a different datum from $+0$, and $0 \cdot \infty = \NaN$.

```python run
from ginsdk import totalized as T

for system in ("meadow", "wheel", "ieee16", "riscv8"):
    for row in T.law_census(system):
        if row["law"].startswith("y·(x / y)") or row["law"] == "0·x = 0":
            law = row["law"].split("   ")[0]
            print(f"{system:7s} {law:14s} first counterexample: {row['counterexample']}")
```

```output
meadow  0·x = 0        first counterexample: None
meadow  y·(x / y) = x  first counterexample: 1, 0: 0 ≠ 1
wheel   0·x = 0        first counterexample: ∞: ⊥ ≠ 0
wheel   y·(x / y) = x  first counterexample: 0, 0: ⊥ ≠ 0
ieee16  0·x = 0        first counterexample: -1: -0 ≠ 0
ieee16  y·(x / y) = x  first counterexample: 0, 0: NaN ≠ 0
riscv8  0·x = 0        first counterexample: None
riscv8  y·(x / y) = x  first counterexample: 1, 0: 0 ≠ 1
```

## Brahmagupta's rules {#sec:brahmagupta}

The question is old. In the *Brāhmasphuṭasiddhānta* of 628 CE, Brahmagupta defined zero as the result of subtracting a number from itself and gave rules of arithmetic with zero, including $0/0 = 0$; for a non-zero number divided by zero he described a fraction with zero as denominator. Bhāskara II later called a quantity with zero divisor *khahara* \cite{mactutor_brahmagupta,plofker2009}.

::: history {title="Brahmagupta's 0/0 = 0"}
Brahmagupta's rule has often been described as an error. In the vocabulary of this chapter it is not an error of derivation but a **selection**: since every $c$ satisfies $0 \cdot c = 0$, choosing $c = 0$ is consistent, and it is exactly the convention adopted, thirteen centuries later, by meadows and by Lean's mathlib and Isabelle/HOL. The modern objection is that $0$ is not *the* solution — the equation has no unique one — not that the rule is inconsistent (\ledger{GIN-HIST-001}, \ledger{GIN-NEG-012}).
:::

::: exercise {#ex:ext-route}
Classify by route (A, B, C or signal): (a) SQL's `1 / 0`, which raises an error in most databases; (b) Excel's `=1/0`, which displays `#DIV/0!`; (c) a programming language whose integer division by zero is specified to return $0$; (d) the field with one element "$\F_1$" read as the zero ring.
:::

::: solution {of="ex:ext-route"}
(a) Signal. (b) Absorption into an error value, which propagates through dependent cells: route B in the sense that no number is claimed to solve $0 \cdot c = 1$ — an error datum, like NaN. (c) Route B (totalization). (d) Route C: in the zero ring $1 = 0$, and $1/0 = 0$ is a solution — of a trivial structure.
:::

::: exercise {#ex:ext-pairs}
Compute in pairs: $(\infty + 1) \cdot 0$ and $\infty \cdot (1 + 0)$, and explain the result with Theorem \ref{thm:pairs}.
:::

::: solution {of="ex:ext-pairs"}
$\infty + 1 = (1, 0) + (1, 1) = (1, 0) = \infty$, and $\infty \cdot 0 = (1, 0)(0, 1) = (0, 0)$: null. $\infty \cdot (1 + 0) = \infty \cdot 1 = \infty$. The two sides of a "distributive" rearrangement differ because the null pair appears in one evaluation order and not the other.
:::

::: exercise {#ex:ext-meadow}
In a meadow, prove that $x \cdot x^{-1}$ is idempotent, and determine its value at $x = 0$ and at $x \ne 0$ in $\Q$.
:::

::: solution {of="ex:ext-meadow"}
$e = x x^{-1}$; $e^2 = x x^{-1} x x^{-1} = (x \cdot (x \cdot x^{-1})) \cdot x^{-1} = x x^{-1} = e$ using $x(xx^{-1}) = x$. In $\Q$ with $0^{-1} = 0$: $e = 0$ at $x = 0$ and $e = 1$ otherwise. The idempotent $xx^{-1}$ is the meadow's own record of whether $x$ was zero.
:::

::: summary
- Every system that gives $1/0$ a value drops the ring laws (A), the converse reading (B), or $0 \ne 1$ (C); in practice A or B, or a signal.
- The projective line and the extended reals adjoin infinities and leave several forms undefined; wheels make everything total with an absorbing $\bot$ and weaker laws.
- Meadows and proof assistants keep the ring laws and set $x/0 = 0$; IEEE returns limit-motivated infinities and NaN; AArch64 and RISC-V return $0$ and $-1$.
- In fractions as pairs, all indeterminate forms compute the null pair, the one pair that cannot be an element.
- An exact census confirms: every total system fails $y(x/y) = x$; the partial ones keep it where defined.
:::
