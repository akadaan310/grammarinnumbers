---
title: "ℝ and ℂ: Completeness, Approximation, and Branches"
status: mixed
statusnote: The mathematics is classical; the comparisons of representations, the SDK domains and the floating-point measurements are this book's.
description: Why the rationals are not enough, how the reals are completed, why almost no real number can be written down, what a program can and cannot decide about a real number, how intervals and floating point approximate, and how the complex numbers buy universal square roots at the price of order and of single-valuedness — with measured branch cuts and complex division.
epigraph: "ℚ has a numeral for every element. ℝ has a numeral for almost none of them."
---

::: objectives
- Explain why $\Q$ is incomplete and how $\R$ repairs it, and state the cost of that repair for representation.
- Prove that $\R$ is uncountable, and conclude that almost every real number has no finite description.
- Distinguish the questions a program can decide about a computable real from those it cannot, and say how interval arithmetic and floating point respond.
- Show that $\C$ admits no order compatible with its field operations, and that the principal square root is a *selection* that breaks familiar laws.
- Compare naive and scaled complex division in binary64.
:::

## The gap in the rationals {#sec:gap}

Chapter 27 ended with $\Q$: a field, densely ordered, every element written by a pair of numerals. Yet the converse problem $c \cdot c = 2$ has no solution in $\Q$.

::: proposition {#prop:sqrt2 title="√2 is irrational" status="classical" ledger="GIN-HIST-007"}
There is no rational $c$ with $c^2 = 2$.
:::

::: proof
Suppose $c = p/q$ in lowest terms with $p^2 = 2q^2$. Then $p^2$ is even, so $p$ is even, $p = 2r$, and $4r^2 = 2q^2$ gives $q^2 = 2r^2$, so $q$ is even too — contradicting lowest terms.
:::

The SDK reports this at the semantic layer: $\sqrt{2}$ is *well formed* and *well typed* in $\Q$, and the converse problem it names has *no solution* there. In $\R$ the problem has two solutions, and $\sqrt{\cdot}$ selects the non-negative one.

```python run
from ginsdk import converse, expr
print(converse.square_root(2, "Q").description, "   ", converse.square_root(2, "Q").reason)
print(converse.square_root(2, "R").description, "   ", converse.square_root(2, "R").reason)
o = expr.evaluate("sqrt(2)", "R")
print(o.status, o.display, o.notes[0])
```

```output
∅     2 is not the square of a rational (its root is irrational)
c ∈ {√2, −√2}     two real square roots; the principal branch √ selects the nonnegative one
value ≈1.414213562373095048801689 √2 is irrational; the value is a 40-digit approximation of the principal root of c · c = 2
```

The deeper defect is not one missing root but a missing *kind of limit*. The set $\{x \in \Q : x^2 < 2\}$ is non-empty and bounded above, and it has no least upper bound in $\Q$. A field with an order in which every non-empty bounded set has a least upper bound is called **complete**, and the classical theorem is that there is exactly one complete ordered field up to isomorphism: $\R$.

::: definition {#def:complete title="Complete ordered field" status="classical" ledger="GIN-DEF-092"}
An ordered field $K$ is *complete* if every non-empty subset of $K$ that has an upper bound has a least upper bound in $K$. Any two complete ordered fields are isomorphic by a unique order-preserving field isomorphism; their common type is $\R$.
:::

Two constructions realize it. **Dedekind cuts** \cite{dedekind1888} define a real number as a downward-closed set of rationals with no greatest element, bounded above — in effect, a real number *is* the set of rationals below it. **Cauchy sequences** define a real number as an equivalence class of sequences of rationals whose terms get arbitrarily close to each other, two sequences being equivalent when their difference tends to zero. Both constructions describe an element of $\R$ by an *infinite* object built from rationals. That is the first sign of what follows: completeness is bought with infinity, and a finite machine can hold only a finite part of it.

## Almost no real number can be written down {#sec:uncountable}

::: theorem {#thm:uncountable title="The reals are uncountable" status="classical" ledger="GIN-HIST-008"}
There is no sequence $x_1, x_2, \ldots$ that contains every real number in $[0, 1)$.
:::

::: proof
Write each $x_n$ in decimal. Define $y = 0.d_1 d_2 d_3 \ldots$ by $d_n = 2$ if the $n$-th decimal digit of $x_n$ is $1$, and $d_n = 1$ otherwise. Because $y$ uses only the digits $1$ and $2$, it has a unique decimal expansion (no tail of $0$s or $9$s), so $y \ne x_n$ for every $n$: they differ at the $n$-th digit, so it is in no position of the sequence.
:::

This is Cantor's diagonal argument; Cantor's own 1891 paper uses sequences of two symbols rather than digit expansions of reals \cite{cantor1891}, and the decimal version above avoids the digits $0$ and $9$ because $0.0999\ldots = 0.1000\ldots$ would otherwise let two expansions name the same number. The construction is itself an algorithm: given any finite list of digit strings, it produces one that differs from all of them.

```python run
import random
random.seed(28)
listed = ["".join(random.choice("01") for _ in range(12)) for _ in range(12)]
y = "".join("1" if listed[n][n] == "0" else "0" for n in range(12))
for n, x in enumerate(listed[:5]):
    print(f"x_{n + 1:<2d} {x}   differs from y at position {n + 1}: {x[n]} vs {y[n]}")
print("...")
print("y    ", y, "  in the list:", y in listed)
```

```output
x_1  000001100010   differs from y at position 1: 0 vs 1
x_2  000010001100   differs from y at position 2: 0 vs 1
x_3  101000110101   differs from y at position 3: 1 vs 0
x_4  001001110111   differs from y at position 4: 0 vs 1
x_5  000101000011   differs from y at position 5: 0 vs 1
...
y     110111010000   in the list: False
```

The consequence for computation is decisive. Every finite description — a numeral, a formula, a program — is a finite string over a finite alphabet, and finite strings can be listed in a sequence (by length, then alphabetically). So the set of real numbers that have *any* finite description is countable, and by the theorem it is a countable subset of an uncountable set: in the sense of cardinality, almost no real number can be named.

## Computable reals {#sec:computable}

Turing's 1936 paper, which introduced the machines now named after him, was about real numbers: its title is *On computable numbers* \cite{turing1936}. A real $x$ is **computable** if a program, given $n$, outputs a rational within $2^{-n}$ of $x$. $\sqrt{2}$, $\pi$ and $e$ are computable; because programs are finite strings, the computable reals are countable, and the diagonal argument applied to the list of all programs produces a real that no program computes.

Computable reals are closed under the field operations and under many functions — but not every question about them can be answered.

::: proposition {#prop:real-eq title="Equality of computable reals is not decidable" status="classical" ledger="GIN-PROP-069"}
There is no algorithm that, given two programs computing real numbers $x$ and $y$ in the sense above, always halts and correctly reports whether $x = y$. Inequality $x \ne y$ is *semi-decidable*: if it holds, computing both to increasing precision eventually separates them.
:::

::: proof
Given a program $P$, define $x_P$ by: the $n$-th approximation is $0$ if $P$ has not halted within $n$ steps, and $2^{-k}$ if $P$ halted at step $k \le n$. This is a computable real (the approximations are within $2^{-n}$ of the limit), and $x_P = 0$ if and only if $P$ never halts. A decision procedure for $x_P = 0$ would decide the halting problem \cite{turing1936}. For the second claim: if $|x - y| > 0$, approximations to precision $2^{-n}$ with $2^{-n+1} < |x - y|$ certify the difference.
:::

In the four-layer vocabulary, the semantic question "is this expression equal to zero?" has a definite answer for every real, and the execution layer cannot always deliver it. The SDK's $\R$ domain makes the gap concrete: it is exact on rationals and carries irrational square roots as flagged 40-digit approximations.

```python run
from ginsdk import expr
for src in ("sqrt(2) * sqrt(2) - 2", "(sqrt(2) + 1) * (sqrt(2) - 1) - 1", "4 * 4 - 16"):
    o = expr.evaluate(src, "R")
    print(f"{src:36s} {o.display:30s} flags {sorted(o.flags)}")
```

```output
sqrt(2) * sqrt(2) - 2                ≈1e-39                         flags ['approximate']
(sqrt(2) + 1) * (sqrt(2) - 1) - 1    ≈1e-39                         flags ['approximate']
4 * 4 - 16                           0                              flags []
```

Each of the first two expressions denotes exactly $0$. The domain cannot say so: it returns a tiny number flagged *approximate*, and no finite amount of further precision would turn "smaller than $10^{-39}$" into "equal to $0$". The third expression involves only rationals, and the domain answers exactly. The repair a computer algebra system applies here is to *change the representation*: treat $\sqrt{2}$ as a symbol with the rewriting rule $\sqrt{2}^2 \to 2$, in which equality of these expressions becomes decidable — at the cost of restricting which reals can be expressed.

## Approximating: intervals and floating point {#sec:approximate}

Two strategies represent a real number by finite data.

**Floating point** (Chapter 25) stores one nearby representable number and discards the error. The result of a computation is a number; how far it is from the real answer is not part of the result.

**Interval arithmetic** \cite{moore1966} stores two representable numbers that enclose the real one, and defines each operation so that the output interval contains every possible result. Bisection produces such an enclosure for $\sqrt{2}$:

```python run
from fractions import Fraction as F

lo, hi = F(1), F(2)
for k in range(1, 31):
    mid = (lo + hi) / 2
    if mid * mid <= 2:
        lo = mid
    else:
        hi = mid
    if k in (5, 10, 20, 30):
        print(f"step {k:2d}: [{float(lo):.12f}, {float(hi):.12f}]  width 2^-{k}")
```

```output
step  5: [1.406250000000, 1.437500000000]  width 2^-5
step 10: [1.414062500000, 1.415039062500]  width 2^-10
step 20: [1.414213180542, 1.414214134216]  width 2^-20
step 30: [1.414213561453, 1.414213562384]  width 2^-30
```

An interval result is *honest* — it never claims more than it knows — but it may claim less than is true. Interval operations treat each occurrence of a variable independently, so expressions that are equal as functions can produce different intervals:

```python run
from fractions import Fraction as F

def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])

def imul(a, b):
    p = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (min(p), max(p))

x = (F(1), F(2))
show = lambda i: f"[{i[0]}, {i[1]}]"
print("x       =", show(x))
print("x - x   =", show(isub(x, x)), "   (true range: [0, 0])")
print("x*x - x =", show(isub(imul(x, x), x)), "   (true range of x² − x on [1, 2]: [0, 2])")
print("x*(x-1) =", show(imul(x, isub(x, (F(1), F(1))))), "   (same function, rewritten)")
```

```output
x       = [1, 2]
x - x   = [-1, 1]    (true range: [0, 0])
x*x - x = [-1, 3]    (true range of x² − x on [1, 2]: [0, 2])
x*(x-1) = [0, 2]    (same function, rewritten)
```

This *dependency problem* is the interval version of a theme of this book: an arithmetic law ($x - x = 0$, or distributivity) holds in the mathematical domain and fails in the representation. Here the failure is conservative — the enclosure is too wide, never wrong — whereas the floating-point failures of Chapter 25 return a confident wrong value.

## The complex numbers {#sec:complex}

The converse problem $c \cdot c = -1$ has no real solution. The complex numbers adjoin one, and with it every polynomial equation acquires a root: by the fundamental theorem of algebra, $\C$ is *algebraically closed*. As a construction, $\C$ is $\R^2$ with
$$
(a, b) + (c, d) = (a + c, b + d), \qquad (a, b)(c, d) = (ac - bd, ad + bc),
$$
and $i = (0, 1)$ satisfies $i^2 = (-1, 0)$. Division by non-zero $(c, d)$ is
$$
\frac{a + bi}{c + di} = \frac{(ac + bd) + (bc - ad)i}{c^2 + d^2},
$$
and $\C$ is a field: $0$ is the only inadmissible divisor.

The extension has two prices.

::: proposition {#prop:no-order-c title="ℂ has no order compatible with its field operations" status="classical" ledger="GIN-PROP-070"}
There is no total order $\le$ on $\C$ such that $a \le b \Rightarrow a + c \le b + c$ and $0 \le a, 0 \le b \Rightarrow 0 \le ab$.
:::

::: proof
In such an order every square is $\ge 0$: if $x \ge 0$ then $x \cdot x \ge 0$ by the product condition; if $x \le 0$ then adding $-x$ to both sides gives $0 \le -x$, and $x^2 = (-x)(-x) \ge 0$. Hence $1 = 1^2 \ge 0$ and $-1 = i^2 \ge 0$. Adding $-1$ to both sides of $0 \le 1$ gives $-1 \le 0$. Together with $-1 \ge 0$ this forces $-1 = 0$, which is false in a field.
:::

The second price is single-valuedness. Every non-zero complex number has exactly two square roots, and $n$ distinct $n$-th roots. The function $\sqrt{\cdot}$ on $\C$ must *select* one — the *principal branch*, with real part $\ge 0$ — and it is the selection repair of Chapter 9 applied to a non-unique converse problem. The SDK's $\C$ domain (exact Gaussian rationals) reports the solution set and the selection:

```python run
from ginsdk import converse, expr
s = converse.square_root(-1, "C")
print(s.equation, "->", s.description, "|", s.reason)
for src in ("sqrt(-1)", "sqrt(-4)", "sqrt(-2)", "1/0"):
    o = expr.evaluate(src, "C")
    print(f"{src:9s} {o.status:12s} {o.display:4s} {(o.notes or [o.reason])[0]}")
```

```output
c · c = -1 -> c ∈ {1i, −1i} | every nonzero complex number has exactly two square roots
sqrt(-1)  value        i    √ is the principal branch: it selects i from c ∈ {1i, −1i}
sqrt(-4)  value        2i   √ is the principal branch: it selects 2i from c ∈ {2i, −2i}
sqrt(-2)  unsupported       √2 is irrational; this exact domain has no representation for it
1/0       no-solution       0 · c = 0 ≠ 1 for every complex c: C is a field, so 0 has no inverse
```

$\sqrt{-2}$ is `unsupported` in this domain: the solutions $\pm\sqrt{2}\,i$ exist in $\C$ but are not Gaussian rationals, so the *representation*, not the mathematics, refuses.

A selection can be consistent with some laws and not others. For non-negative reals, $\sqrt{xy} = \sqrt{x}\sqrt{y}$. For the principal complex square root it fails:

::: counterexample {#neg:sqrt-mult title="The principal square root is multiplicative" status="counterexample" ledger="GIN-NEG-022"}
$\sqrt{-1}\cdot\sqrt{-1} = i \cdot i = -1$, but $\sqrt{(-1)(-1)} = \sqrt{1} = 1$. The selection of one root from each two-element solution set cannot be made compatible with multiplication on all of $\C$.
:::

Floating-point complex arithmetic adds a further, subtle selection. The principal square root is discontinuous across the negative real axis (its *branch cut*): just above the axis $\sqrt{-1 + \varepsilon i} \approx i$, just below it $\approx -i$. IEEE 754's signed zero lets a library tell the two sides apart *on* the cut — the argument Kahan made for the sign of zero \cite{kahan1987}:

```python run
import cmath
print("sqrt(-1 + 0i)  =", cmath.sqrt(complex(-1, 0.0)))
print("sqrt(-1 - 0i)  =", cmath.sqrt(complex(-1, -0.0)))
print("sqrt(-1)*sqrt(-1) =", cmath.sqrt(-1) * cmath.sqrt(-1), "   sqrt((-1)*(-1)) =", cmath.sqrt((-1) * (-1)))
```

```output
sqrt(-1 + 0i)  = 1j
sqrt(-1 - 0i)  = -1j
sqrt(-1)*sqrt(-1) = (-1+0j)    sqrt((-1)*(-1)) = (1+0j)
```

Here $-0.0$, which compares equal to $0.0$, selects a different square root. The zero's sign is information about *which side of the cut* a computation approached from — a datum, not a number in the ordinary sense, in exactly the way Chapter 25 described.

## Complex division in floating point {#sec:complex-division}

The textbook formula for $(a + bi)/(c + di)$ forms $c^2 + d^2$. In binary64 that intermediate overflows when $|c|$ or $|d|$ exceeds about $10^{154}$, and underflows to zero when both are below about $10^{-162}$, even when the quotient itself is an ordinary number. Smith's 1962 algorithm \cite{smith1962} divides through by the larger of $|c|, |d|$ first and never forms $c^2 + d^2$.

```python run
def naive(a, b, c, d):
    den = c * c + d * d
    return complex((a * c + b * d) / den, (b * c - a * d) / den)

def smith(a, b, c, d):
    if abs(c) >= abs(d):
        r = d / c
        den = c + d * r
        return complex((a + b * r) / den, (b - a * r) / den)
    r = c / d
    den = c * r + d
    return complex((a * r + b) / den, (b * r - a) / den)

for x in (1e300, 1.0, 1e-300):
    try:
        n = naive(x, x, x, x)
    except ZeroDivisionError as e:
        n = f"ZeroDivisionError ({e})"
    print(f"(x + xi)/(x + xi), x = {x:<7g}: naive {str(n):38s} Smith {smith(x, x, x, x)}   Python {complex(x, x) / complex(x, x)}")
```

```output
(x + xi)/(x + xi), x = 1e+300 : naive (nan+nanj)                             Smith (1+0j)   Python (1+0j)
(x + xi)/(x + xi), x = 1      : naive (1+0j)                                 Smith (1+0j)   Python (1+0j)
(x + xi)/(x + xi), x = 1e-300 : naive ZeroDivisionError (float division by zero) Smith (1+0j)   Python (1+0j)
```

::: observation {#obs:complex-div title="Naive complex division fails on representable inputs whose quotient is 1" status="empirical" ledger="GIN-OBS-019"}
In binary64 (CPython 3.13 on x86-64), the textbook formula for $(x + xi)/(x + xi)$ returns `nan+nanj` for $x = 10^{300}$ (the denominator $c^2 + d^2$ overflows to $\infty$, and $\infty/\infty$ is NaN) and raises `ZeroDivisionError` for $x = 10^{-300}$ (the denominator underflows to $0$, and Python's `float` division raises rather than returning an IEEE infinity). Smith's algorithm and CPython's built-in complex division both return $1$.
:::

The two failures exhibit two layers again. At $10^{300}$ the operations proceed under IEEE rules and the error is carried *in the data* (NaN). At $10^{-300}$ the host language converts the special case into a *signal*. Neither failure is in the mathematics: the quotient is $1$.

::: exercise {#ex:rc-cauchy}
Show that the sequence $x_0 = 1$, $x_{n+1} = (x_n + 2/x_n)/2$ consists of rationals, is Cauchy, and has no limit in $\Q$. How many correct binary digits does $x_{n+1}$ have, roughly, if $x_n$ has $k$?
:::

::: solution {of="ex:rc-cauchy"}
Each step applies field operations to rationals. For $n \ge 1$, $x_n \ge \sqrt{2}$ (AM–GM) and $x_{n+1} - \sqrt{2} = (x_n - \sqrt{2})^2 / (2x_n)$, so the error squares (divided by about $2\sqrt{2}$) at each step: the sequence converges to $\sqrt{2}$, hence is Cauchy, and its limit is not rational (Proposition \ref{prop:sqrt2}). The number of correct digits roughly doubles: about $2k$. This is Newton's method; it is how arbitrary-precision libraries compute square roots.
:::

::: exercise {#ex:rc-order}
Exhibit an order on $\C$ that is total (for example, lexicographic on $(\mathrm{Re}, \mathrm{Im})$) and say which of the two compatibility conditions of Proposition \ref{prop:no-order-c} it satisfies.
:::

::: solution {of="ex:rc-order"}
The lexicographic order is total and compatible with addition: if $(a, b) \le (c, d)$ then adding $(e, f)$ preserves the comparison of first coordinates and, when they are equal, of second coordinates. It fails the product condition: $i = (0, 1) \ge 0$, but $i \cdot i = (-1, 0) < 0$.
:::

::: exercise {#ex:rc-interval}
Using interval arithmetic, evaluate $x^2 - 2x + 1$ and $(x - 1)^2$ on $x \in [0, 2]$ (computing a square as a product $x \cdot x$). Which encloses the true range $[0, 1]$ more tightly?
:::

::: solution {of="ex:rc-interval"}
$x \cdot x = [0, 4]$, $2x = [0, 4]$, so $x^2 - 2x + 1 = [0 - 4 + 1, 4 - 0 + 1] = [-3, 5]$. $x - 1 = [-1, 1]$, and $(x - 1)\cdot(x - 1) = [-1, 1]$. The second is tighter; neither achieves $[0, 1]$, because the product of an interval with itself is computed as if the two factors were independent. A dedicated *square* operation returns $[0, 1]$ for $(x - 1)^2$.
:::

::: summary
- $\Q$ lacks least upper bounds; $\R$ is the unique complete ordered field, built from infinite objects (cuts, Cauchy sequences).
- $\R$ is uncountable, finite descriptions are countable: almost no real has a name. Computable reals are countable.
- Equality of computable reals is undecidable; inequality is semi-decidable. Approximate representations cannot certify zero.
- Interval arithmetic encloses honestly but loses correlation (the dependency problem); floating point returns one confident value.
- $\C$ is algebraically closed but has no compatible order; the principal root is a selection that breaks $\sqrt{xy} = \sqrt{x}\sqrt{y}$.
- In binary64, naive complex division fails where Smith's scaling succeeds; signed zero selects a side of a branch cut.
:::
