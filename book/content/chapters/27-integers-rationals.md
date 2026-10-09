---
title: "ℕ, ℤ, ℚ: Constructions, Order, and Representation"
status: mixed
statusnote: Constructions and properties are classical; the per-domain operation contracts and the measured costs of canonical forms are this book's packaging.
description: The first three number systems as computational domains — how each is constructed, which operations are total and which admissible, how each is ordered, how its elements are represented, how equality is decided, and what canonical forms cost — ending with an enumeration of all positive rationals by Stern's sequence.
epigraph: "ℕ counts, ℤ answers every subtraction, ℚ answers every division but one. Each answer is paid for in representation."
---

::: objectives
- Describe $\N$, $\Z$ and $\Q$ by construction, operations, closure, identities, inverses and order.
- Distinguish the properties that follow from the structure from those that come from a chosen representation.
- Decide equality in each domain and state what the canonical form costs.
- Enumerate the positive rationals without repetition, and connect the enumeration to Chapter 6.
:::

## Three domains at a glance {#sec:glance}

| | $\N$ | $\Z$ | $\Q$ |
|---|---|---|---|
| construction | successor algebra (Chapter 3) | pairs $(a, b) \in \N^2$ mod $a + d = b + c$ (Chapter 12) | pairs $(a, b) \in \Z \times (\Z \setminus 0)$ mod $ad = bc$ (Chapter 9) |
| algebraic structure | commutative semiring | commutative ring, integral domain | field |
| total operations | $+$, $\times$ | $+$, $-$, $\times$ | $+$, $-$, $\times$ |
| admissibility of $a - b$ | $a \ge b$ | always | always |
| admissibility of $a / b$ | $b \ne 0$ and $b \mid a$ | $b \ne 0$ and $b \mid a$ | $b \ne 0$ |
| units (invertible elements) | $\{1\}$ | $\{1, -1\}$ | $\Q \setminus \{0\}$ |
| order | well-order | discrete total order compatible with $+$ | dense total order, Archimedean |
| canonical representation | positional numeral | sign and magnitude numeral | reduced fraction $p/q$, $q > 0$, $\gcd(p, q) = 1$ |
| deciding equality | compare numerals | compare signs and magnitudes | compare reduced forms, or $ad = bc$ |

The table is classical; its arrangement follows the contract format of Chapter 8, and the SDK's contract data (`python3 -m ginsdk contracts /`) records the same admissibility conditions per domain.

## Order {#sec:order}

**$\N$ is well-ordered**: every non-empty set of natural numbers has a least element. This is equivalent to induction, and it is why algorithms that decrease a natural number at each step — Euclid's algorithm, the residue algorithm, long division — terminate. **$\Z$ is not well-ordered** ($\{-1, -2, \ldots\}$ has no least element), which is why termination arguments over integers measure an absolute value or some other natural number. **$\Q$ is dense**: between any two rationals lies another, $(a + b)/2$. There is no "next rational", and therefore no successor grammar for $\Q$ in its usual order — a fact that makes the enumeration below surprising.

The order of $\Z$ is *compatible* with its ring operations: $a \le b \Rightarrow a + c \le b + c$, and $a \le b, c \ge 0 \Rightarrow ac \le bc$. This compatibility is lost in $\Z/n$ (Chapter 29), where no order respects addition: $n - 1 + 1 = 0$.

## Representation and equality {#sec:representation}

A domain's *values* are independent of how they are written, but every computation manipulates *representations*, and the cost of deciding equality depends on whether representations are canonical.

- In $\N$ and $\Z$, positional numerals without leading zeros (and with a sign) are canonical: two numbers are equal iff their numerals are identical — a linear-time comparison.
- In $\Q$, the pair $(p, q)$ is not canonical: $(2, 4)$ and $(1, 2)$ are the same rational. Either every result is reduced by a gcd — the strategy of Python's `fractions` — or equality is decided by cross-multiplication, $ad = bc$, at the cost of a multiplication per comparison and of numerators and denominators that grow without bound.

```python run
from fractions import Fraction
from ginsdk import bigint
from ginsdk.cost import Cost
import random

random.seed(27)
x = Fraction(0)
for k in range(1, 61):
    x += Fraction(random.randint(-9, 9), random.randint(1, 30))
    if k % 15 == 0:
        print(f"after {k:2d} additions: numerator {x.numerator.bit_length():3d} bits, denominator {x.denominator.bit_length():3d} bits")
c = Cost()
bigint.gcd_euclid(bigint.from_int(abs(x.numerator)) or [1], bigint.from_int(x.denominator), c)
print("limb operations for one gcd at the end:", bigint.word_ops(c))
```

```output
after 15 additions: numerator  21 bits, denominator  21 bits
after 30 additions: numerator  23 bits, denominator  20 bits
after 45 additions: numerator  32 bits, denominator  28 bits
after 60 additions: numerator  35 bits, denominator  33 bits
limb operations for one gcd at the end: 45
```

The reduced denominator of a sum of fractions with denominators at most $30$ divides $\mathrm{lcm}(1, \ldots, 30)$, a 42-bit number, so in this run the denominator can never exceed 42 bits; after sixty additions it has reached 33. The numerator has no such bound: it grows with the magnitude of the sum. With unbounded denominators the growth continues without limit. Exact rational arithmetic is total and exact; its price is that the size of the data, and therefore the cost of each operation, depends on the history of the computation.

## Enumerating the rationals {#sec:enumerate}

$\Q$ is dense, so no rational has a successor in the usual order. Yet $\Q$ is *countable*: its elements can be listed in a sequence. A classical listing uses pairs and diagonals, and repeats every rational infinitely often ($1/2 = 2/4 = \cdots$). A more elegant one, due to Calkin and Wilf \cite{calkinwilf2000}, lists each positive rational exactly once, in lowest terms:

::: proposition {#prop:calkin-wilf title="Every positive rational, once: the Calkin–Wilf sequence" status="classical" ledger="GIN-PROP-068"}
Let $s$ be Stern's diatomic sequence ($s(0) = 0$, $s(1) = 1$, $s(2k) = s(k)$, $s(2k+1) = s(k) + s(k+1)$). Then $n \mapsto s(n)/s(n+1)$, for $n \ge 1$, is a bijection from the positive integers to the positive rationals, and every fraction $s(n)/s(n+1)$ is in lowest terms \cite{calkinwilf2000}.
:::

```python run
from fractions import Fraction

s = [0, 1]
for k in range(2, 4002):
    s.append(s[k // 2] if k % 2 == 0 else s[k // 2] + s[k // 2 + 1])
seq = [Fraction(s[n], s[n + 1]) for n in range(1, 4001)]
print("first terms:", ", ".join(f"{s[n]}/{s[n+1]}" for n in range(1, 16)))
print("4000 terms, distinct:", len(set(seq)) == len(seq),
      "  all in lowest terms:", all(__import__("math").gcd(s[n], s[n + 1]) == 1 for n in range(1, 4001)))
small = {Fraction(p, q) for p in range(1, 13) for q in range(1, 13)}
print("every p/q with p, q <= 12 appears among the first 4000:", small <= set(seq))
print("missing:", sorted(map(str, small - set(seq))))

def cf_sum(p, q):                       # sum of continued-fraction partial quotients of p/q
    total = 0
    while q:
        total, (p, q) = total + p // q, (q, p % q)
    return total
print("bit length of n equals that sum for all n < 4001:",
      all(n.bit_length() == cf_sum(s[n], s[n + 1]) for n in range(1, 4001)))
```

```output
first terms: 1/1, 1/2, 2/1, 1/3, 3/2, 2/3, 3/1, 1/4, 4/3, 3/5, 5/2, 2/5, 5/3, 3/4, 4/1
4000 terms, distinct: True   all in lowest terms: True
every p/q with p, q <= 12 appears among the first 4000: False
missing: ['11/12', '12']
bit length of n equals that sum for all n < 4001: True
```

The negative line is informative: the enumeration is complete in the limit but not uniformly fast. Of the 91 distinct fractions $p/q$ with $p, q \le 12$, two are missing from the first 4,000 terms, namely $11/12$ and $12$; they occur at positions $4094$ and $4095$. The last line explains why: the position $n$ of $p/q$ has as many binary digits as the sum of the partial quotients of the continued fraction of $p/q$ — its depth in the Calkin–Wilf tree, plus one. $12 = [12]$ and $11/12 = [0; 1, 11]$ both have sum $12$, while $8/13 = [0; 1, 1, 1, 1, 2]$, with sum $6$, already appears at position $42$. Stern's sequence — which counted hyperbinary representations in Chapter 6 (\ledger{GIN-PROP-054}) — thus also gives the rationals a *successor grammar of its own*: the move $x \mapsto 1/(2\lfloor x \rfloor + 1 - x)$ (Newman's formula) takes each term of the Calkin–Wilf sequence to the next. Density in one order and a successor structure in another are compatible; they are different grammars on the same set.

::: exercise {#ex:zq-units}
Prove that the only units of $\Z$ are $\pm 1$, and that every non-zero rational is a unit of $\Q$. What are the units of $\Z[1/2]$, the rationals with power-of-two denominators?
:::

::: solution {of="ex:zq-units"}
If $ab = 1$ in $\Z$ then $|a||b| = 1$ with $|a|, |b| \ge 1$, so $|a| = 1$. In $\Q$, $(p/q)^{-1} = q/p$ for $p \ne 0$. In $\Z[1/2]$ the units are $\pm 2^k$, $k \in \Z$: a unit $u = m/2^j$ has inverse $2^j/m$, which lies in $\Z[1/2]$ iff $m = \pm 2^i$.
:::

::: exercise {#ex:zq-newman}
Verify Newman's formula $x_{n+1} = 1/(2\lfloor x_n \rfloor + 1 - x_n)$ for the first eight Calkin–Wilf terms.
:::

::: solution {of="ex:zq-newman"}
$1 \to 1/(2 + 1 - 1) = 1/2 \to 1/(0 + 1 - 1/2) = 2 \to 1/(4 + 1 - 2) = 1/3 \to 1/(1 - 1/3) = 3/2 \to 1/(2 + 1 - 3/2) = 2/3 \to 1/(1 - 2/3) = 3 \to 1/(6 + 1 - 3) = 1/4$. ✓
:::

::: exercise {#ex:zq-dense}
Show that $\Z$ with its usual order is not dense and $\Q$ is, and give a property of $\Q$'s order that $\R$'s has and $\Q$'s lacks.
:::

::: solution {of="ex:zq-dense"}
No integer lies strictly between $0$ and $1$; between rationals $a < b$ lies $(a + b)/2$. $\Q$ lacks completeness: the set $\{x \in \Q : x^2 < 2\}$ is bounded above but has no least upper bound in $\Q$ (Chapter 28).
:::

::: summary
- $\N$, $\Z$, $\Q$ are a semiring, an integral domain and a field; each adds solutions to a family of converse problems.
- $\N$ is well-ordered (termination), $\Z$ discretely ordered, $\Q$ densely ordered.
- Canonical forms make equality cheap; reduced fractions require gcds, and rational data grow with the computation.
- The positive rationals have a successor grammar after all: the Calkin–Wilf sequence lists each exactly once.
:::
