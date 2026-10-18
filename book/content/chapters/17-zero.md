---
title: "$1/0$ and $0/0$: Two Different Failures"
status: mixed
statusnote: The algebra is classical; the classification of the two failures and their consequences for symbolic and numerical computation is this book's organization of it.
description: Why 1/0 has no solution and 0/0 has too many; why no ring with 0 ≠ 1 can invert zero; the families x/0, 0/x and x/x; symbolic simplification that silently enlarges domains; limits as questions about functions rather than numbers; and the floating-point boundary where overflow and division by zero meet.
epigraph: "Ask for c with 0 · c = 1 and nothing answers. Ask for c with 0 · c = 0 and everything does. Both are called 'undefined'; they are opposite failures."
---

::: objectives
- Classify $1/0$ as an image failure (no solution) and $0/0$ as a kernel failure (every element is a solution), in every field and every commutative ring.
- Prove that no ring with $0 \ne 1$ contains an inverse of zero, and identify the single ring in which division by zero is admissible.
- Analyse the families $x/0$, $0/x$ and $x/x$ exactly and symbolically, and explain why cancelling a common factor changes the domain of an expression.
- Separate the number $0/0$ from the limit form "$0/0$", and the value $1/0$ from the limit $\lim_{x \to 0} 1/x$.
- Locate the floating-point boundary between overflow and division by zero.
:::

## The two failures {#sec:two-failures}

Specialize the image/kernel theorem (\ledger{GIN-THM-001}) to $b = 0$. In every ring, $0 \cdot c = 0$ for all $c$ (\ledger{GIN-PROP-012}), so the map $c \mapsto 0 \cdot c$ is the zero map: its image is $\{0\}$ and its kernel is everything.

::: corollary {#cor:two-failures title="Why 1/0 and 0/0 fail differently, and why 0/1 = 0" status="classical" ledger="GIN-COR-001"}
In a field $F$ (and in $\Z$, $\Q$, $\R$, $\C$):
- for $b \ne 0$, $\Ann(b) = \{0\}$ and $bF = F$, so $a/b$ is admissible for every $a$; in particular $0/1 = 0$;
- $1/0$: since $0 \cdot F = \{0\}$, the image condition fails: $0 \cdot c = 1$ has **no solution** (it would require $0 = 1$);
- $0/0$: the image condition holds ($0 \in 0 \cdot F$), but $\Ann(0) = F$, so **every** $c$ solves $0 \cdot c = 0$: the kernel condition fails maximally;
- $x/0$ for an unknown $x$: no solution where $x \ne 0$ and every $c$ where $x = 0$ — a case split.
:::

The two failures call for different responses. When an equation has *no* solution, any value offered as its answer is a fiction, and the honest responses are to extend the structure (add an element that solves it), to refuse, or to supply a conventional value labelled as such. When an equation has *every* element as a solution, the question is underdetermined, and the honest responses are to select one solution by an explicit rule, to refuse, or to return the whole solution set. A system that answers both with the same word — "undefined", `NaN`, "error" — cannot apply the right response to either.

```python run
from ginsdk import evaluate

for e in ["1 / 0", "0 / 0", "0 / 1", "5 / 0", "0 / 5"]:
    o = evaluate(e, "Q")
    print(f"{e:6s} {o.status:12s} equation: {o.equation or '—':10s} solutions: {o.solutions or o.display}")
```

```output
1 / 0  no-solution  equation: 0 · c = 1  solutions: ∅
0 / 0  non-unique   equation: 0 · c = 0  solutions: every c in Q
0 / 1  value        equation: —          solutions: 0
5 / 0  no-solution  equation: 0 · c = 5  solutions: ∅
0 / 5  value        equation: —          solutions: 0
```

## No ring inverts zero {#sec:no-inverse}

Could a cleverer structure supply an inverse of zero? Not if it is a ring and $0 \ne 1$.

::: theorem {#thm:no-zero-inverse title="No non-trivial ring can invert zero" status="classical" ledger="GIN-THM-003"}
If $R$ is a ring with $1$ in which $0 \cdot z = 1$ for some $z$, then $R = \{0\}$.
:::

::: proof
$0 \cdot z = 0$ in every ring (\ledger{GIN-PROP-012}), so $1 = 0$, and then every $x = x \cdot 1 = x \cdot 0 = 0$.
:::

The **zero ring** $\{0\}$, in which $0 = 1$, is the only ring in which $1/0$ is admissible — and there it equals $0$, which is also $1$. It is a legitimate ring and a useless number system: it cannot count. The theorem therefore says that giving $1/0$ a value requires giving up something: one of the ring laws used in the proof of $0 \cdot z = 0$ (distributivity, additive inverses), or the reading of $1/0$ as a solution of $0 \cdot c = 1$, or $0 \ne 1$. Chapter 18 shows that every system in use makes exactly one of these choices.

## The three families {#sec:families}

Consider the expressions $x/0$, $0/x$ and $x/x$ as $x$ ranges over $\Q$.

| family | $x \ne 0$ | $x = 0$ |
|---|---|---|
| $x / 0$ | no solution (image failure) | non-unique (kernel failure) |
| $0 / x$ | $0$ | non-unique |
| $x / x$ | $1$ | non-unique |

Every family meets $0/0$ at $x = 0$, and in two of them the value elsewhere is constant. It is tempting to "fill in" $0/0$ with the constant — $0$ for the family $0/x$, $1$ for $x/x$ — and the temptation is the source of a classical error: the two families demand different values at the same point. $0/0$ is the meeting point of every family $\lambda x / x$ ($\lambda$ any constant), and each family suggests its own $\lambda$. That is the kernel failure seen from the outside.

## Symbolic simplification is not evaluation {#sec:symbolic}

In the field $\Q(x)$ of rational functions, $x/x = 1$ is a true identity: the rational function $x/x$ *is* the constant $1$. As an *expression to be evaluated* at points of $\Q$, however, $x/x$ is admissible exactly on $\Q \setminus \{0\}$. Simplifying first and evaluating afterwards silently changes the answer at $0$ from "non-unique" to $1$.

::: proposition {#prop:symbolic title="Symbolic simplification is not evaluation" status="classical" ledger="GIN-PROP-014"}
Cancelling a common factor $g$ from a quotient preserves its values on $\{g \ne 0\}$ and enlarges its domain to include the zeros of $g$. A simplifier that is to agree with evaluation must record $g \ne 0$ as a side condition. For example, $(x^2 - 1)/(x - 1) = x + 1$ only for $x \ne 1$.
:::

The SDK's symbolic domain keeps every condition it creates while cancelling, and reports what happens at the excluded points:

```python run
from ginsdk import evaluate

for e in ["x / x", "(x^2 - 1) / (x - 1)", "1 / (x - 2)"]:
    o = evaluate(e, "symbolic")
    r = o.representation
    print(f"{e:20s} simplifies to {r['simplified']:14s} under {', '.join(r['conditions'])}")
    for pt, what in r.get("at excluded points (exact Q)", {}).items():
        print(f"{'':20s}   at x = {pt}: {what.split(':')[0]}")
```

```output
x / x                simplifies to 1              under x ≠ 0
                       at x = 0: non-unique
(x^2 - 1) / (x - 1)  simplifies to x + 1          under x − 1 ≠ 0
                       at x = 1: non-unique
1 / (x - 2)          simplifies to (1) / (x − 2)  under x − 2 ≠ 0
                       at x = 2: no-solution
```

Computer algebra systems differ in how strictly they observe this; many simplify $x/x$ to $1$ without recording a condition, which is correct in $\Q(x)$ and wrong as a statement about every rational $x$. The counterexample is recorded as \ledger{GIN-NEG-006}.

## Limits answer a different question {#sec:limits}

"$0/0$ is indeterminate" is a phrase from calculus, and it is about *limits*: if $f(x) \to 0$ and $g(x) \to 0$ as $x \to a$, then $\lim f(x)/g(x)$ can be anything, depending on $f$ and $g$. That is a statement about *functions near a point*, and it is consistent with — but different from — the statement that the *number* $0/0$ has every number as a solution. Likewise $\lim_{x \to 0^+} 1/x = +\infty$ is a statement that $1/x$ grows without bound as $x$ shrinks; it does not say that $1/0$ is a number, and in $\R$ it is not. The limit has a sign that depends on the side of approach ($\lim_{x \to 0^-} 1/x = -\infty$), which the number $0$ does not have.

These facts matter because the most common "value" of $1/0$ in computing — IEEE 754's $+\infty$ — is motivated by the limit, not by the equation. Chapter 25 shows that IEEE records the side of approach in the *sign of zero*, so that $1/(+0) = +\infty$ and $1/(-0) = -\infty$, and that $\infty$ is nevertheless not a solution of $0 \cdot c = 1$, because IEEE defines $0 \cdot \infty = \NaN$ (\ledger{GIN-PROP-015}).

## The floating-point boundary {#sec:fp-boundary}

On a computer, numbers close to zero raise a further question. When does $1/x$ stop being a large number and become a division by zero? The reference simulator of the SDK answers exactly, in binary64:

```python run
from ginsdk import ieee

one = ieee.from_decimal("1")[0]
for t in ["1e-300", "1e-308", "1e-310", "1e-323", "1e-330"]:
    x, flags_in = ieee.from_decimal(t)
    r, flags = ieee.div(one, x)
    print(f"x = {t:7s} is stored as {str(x):10s}  1/x = {str(r):22s} flags: {', '.join(sorted(flags))}")
```

```output
x = 1e-300  is stored as 1e-300      1/x = 9.999999999999999e299  flags: inexact
x = 1e-308  is stored as 1e-308      1/x = 1e308                  flags: inexact
x = 1e-310  is stored as 1e-310      1/x = Infinity               flags: inexact, overflow
x = 1e-323  is stored as 1e-323      1/x = Infinity               flags: inexact, overflow
x = 1e-330  is stored as 0           1/x = Infinity               flags: divideByZero
```

The last three rows produce the same datum, `Infinity`, for two different reasons. For $x = 10^{-310}$ and $10^{-323}$ — subnormal numbers, not zero — the exact quotient exists and is simply too large for the format: an *overflow*. For $10^{-330}$, the literal itself rounds to $+0$ when it is read, and the division is then a genuine division by zero: the flag is *divideByZero*. The datum is the same; the status flags, which IEEE 754 requires the hardware to record, distinguish the two events (\ledger{GIN-OBS-016}).

::: counterexample {#neg:overflow-dbz title="Overflow and division by zero are the same event" status="counterexample" ledger="GIN-NEG-017"}
In binary64, $1/10^{-320}$ yields $+\infty$ with the *overflow* flag (the divisor is subnormal, not zero), while $1/10^{-330}$ yields $+\infty$ with the *divideByZero* flag (the literal rounded to $+0$).
:::

## A vocabulary of "undefined" {#sec:vocabulary}

The word "undefined" is used for at least six different things, and this book keeps them apart:

| term | meaning | example |
|---|---|---|
| no solution | the defining equation has no solution in the domain | $1/0$ in $\Q$; $0 - 1$ in $\N$ |
| non-unique | the defining equation has several solutions | $0/0$ in $\Q$; $2/4$ in $\Z/6$ |
| not in the domain | an operand or literal names nothing in the domain | `0.5` in $\Z$ |
| special datum | a format returns a value that is not a number | IEEE NaN, $\pm\infty$ |
| exception or trap | the system refuses and transfers control | Python `ZeroDivisionError`; x86 `#DE` |
| undefined behaviour | the program has no meaning at all | `1 / 0` on `int` in ISO C |

::: exercise {#ex:zero-family}
For which $\lambda$ is the family $\lambda x / x$ consistent with each of the following conventions at $x = 0$: (a) meadows ($0/0 = 0$); (b) "$0/0 = 1$"; (c) wheels ($0/0 = \bot$)?
:::

::: solution {of="ex:zero-family"}
(a) $\lambda = 0$ only. (b) $\lambda = 1$ only. (c) No $\lambda \in \Q$: $\bot$ is not a number; in a wheel, $\lambda x / x$ at $x = 0$ is $\bot$ for every $\lambda$ (Chapter 18). Each convention makes exactly one family continuous at $0$, or none.
:::

::: exercise {#ex:zero-ring}
Show directly that in the zero ring every axiom of a commutative ring holds and $0 \cdot 0 = 1$.
:::

::: solution {of="ex:zero-ring"}
There is one element, so every equation between elements holds: $0 + 0 = 0$, $0 \cdot 0 = 0$, and $1 = 0$, so $0 \cdot 0 = 0 = 1$. All ring axioms are equations, hence true.
:::

::: exercise {#ex:zero-simplify}
Find the domain of $\dfrac{x^3 - x}{x^2 - x}$ as an evaluated expression on $\Q$, simplify it, and classify the failures at the excluded points.
:::

::: solution {of="ex:zero-simplify"}
$x^2 - x = x(x - 1)$ vanishes at $0$ and $1$; $x^3 - x = x(x - 1)(x + 1)$ also vanishes there, so both points are kernel failures ($0/0$, non-unique). The simplified form is $x + 1$ under the conditions $x \ne 0$, $x \ne 1$.
:::

::: exercise {#ex:zero-limits}
Give functions $f, g$ with $f(x), g(x) \to 0$ as $x \to 0$ such that $f/g \to 7$, $f/g \to 0$, and $f/g$ has no limit. Why does this not contradict the claim that the number $0/0$ is non-unique rather than "indeterminate"?
:::

::: solution {of="ex:zero-limits"}
$f = 7x, g = x$; $f = x^2, g = x$; $f = x \sin(1/x), g = x$. The limits concern functions near $0$; the solution set of $0 \cdot c = 0$ concerns the number $0$. Both say that "$0/0$" carries no information about a value, but they are statements about different objects, and a value chosen for one does not answer the other.
:::

::: summary
- $1/0$ is an image failure: no $c$ satisfies $0 \cdot c = 1$. $0/0$ is a kernel failure: every $c$ satisfies $0 \cdot c = 0$.
- No ring with $0 \ne 1$ inverts zero; the zero ring is the only exception.
- The families $x/0$, $0/x$ and $x/x$ all meet $0/0$, and each suggests a different value there.
- Cancellation enlarges domains; a correct simplifier records the conditions it creates.
- Limits concern functions, not the number $0/0$; IEEE's $\pm\infty$ follows the limit, not the equation.
- In binary64, overflow and division by zero yield the same datum and different flags.
:::
