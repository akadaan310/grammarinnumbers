---
title: "Arithmetic Functions and the Dirichlet Ring"
status: mixed
statusnote: The functions, identities and asymptotics are classical; the treatment of Möbius inversion as division in the Dirichlet ring, the SDK's convolution and solver, and the measurements are this book's.
description: The functions τ, σ, φ and μ; multiplicativity as a consequence of unique factorization; Dirichlet convolution as a multiplication on functions, with its units, its zero divisors (there are none) and Möbius inversion as a division; average orders measured against their asymptotic formulas; and the probability that two integers are coprime.
epigraph: "Möbius inversion is division by the constant function 1. It is admissible because 1(1) ≠ 0."
---

::: objectives
- Define $\tau$, $\sigma$, $\varphi$, $\mu$ and recognize multiplicative functions.
- Compute Dirichlet convolutions, and identify the units of the Dirichlet ring.
- Read Möbius inversion as division by $\mathbf{1}$, and decide when the converse problem $f * g = h$ is solvable.
- Compare measured averages of $\tau$ and $\varphi$ with their asymptotic formulas, and measure the probability that two random integers are coprime.
:::

## Functions on the positive integers {#sec:functions}

An *arithmetic function* is any $f : \N_{>0} \to \C$. The classical examples count or sum over divisors:

| function | definition | value at $12$ |
|---|---|---|
| $\tau(n)$ | number of divisors | $6$ |
| $\sigma(n)$ | sum of divisors | $28$ |
| $\varphi(n)$ | number of $1 \le k \le n$ with $\gcd(k, n) = 1$ | $4$ |
| $\mu(n)$ | $(-1)^r$ if $n$ is a product of $r$ distinct primes, else $0$ | $0$ |
| $\mathbf{1}(n)$ | $1$ | $1$ |
| $\mathrm{id}(n)$ | $n$ | $12$ |
| $\varepsilon(n)$ | $1$ if $n = 1$, else $0$ | $0$ |

A function is **multiplicative** if $f(1) = 1$ and $f(mn) = f(m) f(n)$ whenever $\gcd(m, n) = 1$. All seven functions in the table are multiplicative; $n \mapsto n + 1$ is not. By the fundamental theorem of arithmetic (\ledger{GIN-HIST-010}), a multiplicative function is determined by its values on prime powers — a statement about the *free commutative monoid* structure of Chapter 30, not about the functions. For instance $\varphi(p^k) = p^k - p^{k-1}$ gives $\varphi(n) = n \prod_{p \mid n} (1 - 1/p)$.

## Dirichlet convolution {#sec:dirichlet}

::: definition {#def:dirichlet title="Dirichlet convolution and the Dirichlet ring" status="classical" ledger="GIN-DEF-096"}
For arithmetic functions $f, g$, $(f * g)(n) = \sum_{d \mid n} f(d)\, g(n/d)$. With pointwise addition and $*$ as multiplication, arithmetic functions form a commutative ring with identity $\varepsilon$ \cite{apostol1976}.
:::

The convolution is the multiplication of a positional system with one digit per *divisor*: in the generating-function view it is the product of Dirichlet series $\sum f(n) n^{-s}$, just as ordinary convolution is the product of power series. Many classical identities are products in this ring:

$$
\tau = \mathbf{1} * \mathbf{1}, \qquad \sigma = \mathbf{1} * \mathrm{id}, \qquad \varphi * \mathbf{1} = \mathrm{id}, \qquad \mu * \mathbf{1} = \varepsilon.
$$

The SDK tabulates functions on $1..N$ and convolves them; the cost of one convolution is the number of pairs $(d, m)$ with $dm \le N$, which is $\sum_{n \le N} \tau(n)$:

```python run
from ginsdk import numbertheory as nt
from ginsdk.cost import Cost

N = 10_000
one, ident = nt.table(lambda n: 1, N), nt.table(lambda n: n, N)
eps = nt.table(lambda n: int(n == 1), N)
mu, phi = nt.table(nt.mobius, N), nt.table(nt.phi, N)
print("1 * 1 = tau:     ", nt.dirichlet(one, one) == nt.table(lambda n: len(nt.divisors(n)), N))
print("1 * id = sigma:  ", nt.dirichlet(one, ident) == nt.table(nt.sigma, N))
print("phi * 1 = id:    ", nt.dirichlet(phi, one) == ident)
print("mu * 1 = epsilon:", nt.dirichlet(mu, one) == eps)
c = Cost()
nt.dirichlet(one, one, c)
print(f"multiplications for one convolution on 1..{N}: {c.counts['mul']}")
```

```output
1 * 1 = tau:      True
1 * id = sigma:   True
phi * 1 = id:     True
mu * 1 = epsilon: True
multiplications for one convolution on 1..10000: 93668
```

## Möbius inversion is division {#sec:mobius}

The converse problem in this ring is: given $f$ and $h$, find $g$ with $f * g = h$. Evaluating at $n = 1$ gives $f(1) g(1) = h(1)$, and at each larger $n$,
$$
f(1)\, g(n) = h(n) - \sum_{d \mid n,\ d > 1} f(d)\, g(n/d),
$$
which determines $g(n)$ from values at proper divisors — a recursion over the divisibility order of Chapter 30, from the bottom element $1$ upward.

::: proposition {#prop:dirichlet-units title="Units and division in the Dirichlet ring" status="proved-here" ledger="GIN-PROP-075"}
Over a field (e.g. $\Q$ or $\C$):

1. $f$ is a unit if and only if $f(1) \ne 0$, and then $f * g = h$ has exactly one solution for every $h$.
2. The ring has no zero divisors. Hence when $f \ne 0$ and $f(1) = 0$, $f * g = h$ has at most one solution, and none unless $h(1) = 0$.

Over $\Z$, $f$ is a unit if and only if $f(1) = \pm 1$.
:::

::: proof
(1) If $f(1) \ne 0$ the recursion above defines $g$ uniquely, by induction on $n$. Conversely $(f * g)(1) = f(1) g(1)$, which cannot be $\varepsilon(1) = 1$ if $f(1) = 0$. (2) Let $n_0$ be the least $n$ with $f(n) \ne 0$ and $m_0$ the least with $g(m) \ne 0$. In $(f * g)(n_0 m_0) = \sum_{dm = n_0 m_0} f(d) g(m)$, a term is non-zero only if $d \ge n_0$ and $m \ge m_0$, which with $dm = n_0 m_0$ forces $d = n_0$; so the sum is $f(n_0) g(m_0) \ne 0$. Uniqueness follows: $f * g = f * g'$ gives $f * (g - g') = 0$. Over $\Z$ the recursion divides by $f(1)$ at every step, and $f(1) g(1) = 1$ requires $f(1) = \pm 1$; conversely $f(1) = \pm 1$ keeps every step integral.
:::

**Möbius inversion** is the special case $f = \mathbf{1}$: since $\mathbf{1}(1) = 1$, every $h$ is uniquely $\mathbf{1} * g$, and $g = \mu * h$. In the classical formulation: if $h(n) = \sum_{d \mid n} g(d)$ for all $n$, then $g(n) = \sum_{d \mid n} \mu(d) h(n/d)$. The theorem that textbooks state as an inversion formula is, in this book's vocabulary, the statement that division by $\mathbf{1}$ is *admissible and unique* in the Dirichlet ring, and $\mu$ is the reciprocal of $\mathbf{1}$.

```python run
from fractions import Fraction
from ginsdk import numbertheory as nt

N = 30
one = nt.table(lambda n: 1, N)
eps = nt.table(lambda n: int(n == 1), N)
kind, inv = nt.dirichlet_divide(eps, one)
print("epsilon / 1:", kind, "->", [int(x) for x in inv[1:]])
print("mu         :", " " * len(kind) + "    ", [nt.mobius(n) for n in range(1, N + 1)])
kind, g = nt.dirichlet_divide(nt.table(lambda n: n, N), one)
print("id / 1 = phi:", kind, all(g[n] == nt.phi(n) for n in range(1, N + 1)))
not_unit = nt.table(lambda n: 0 if n == 1 else 1, N)
print("epsilon / f with f(1) = 0:", nt.dirichlet_divide(eps, not_unit)[0])
```

```output
epsilon / 1: unique -> [1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0, -1, 1, 1, 0, -1, 0, -1, 0, 1, 1, -1, 0, 0, 1, 0, 0, -1, -1]
mu         :            [1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0, -1, 1, 1, 0, -1, 0, -1, 0, 1, 1, -1, 0, 0, 1, 0, 0, -1, -1]
id / 1 = phi: unique True
epsilon / f with f(1) = 0: not-solved
```

The last line is the solver *declining*, not deciding: for $f(1) = 0$ the proposition guarantees at most one solution, and none for $h = \varepsilon$ because $\varepsilon(1) \ne 0$; the SDK's solver reports `not-solved` rather than claiming an answer it has not computed. A complete decision procedure for $f(1) = 0$ is possible on a finite range (the equations become a triangular system shifted by the least $n_0$ with $f(n_0) \ne 0$), and Exercise \ref{ex:af-nonunit} works one case.

## Averages {#sec:averages}

Arithmetic functions fluctuate wildly — $\tau(p) = 2$ for every prime, while $\tau(720720) = 240$ — but their averages are smooth. Two classical formulas \cite{apostol1976, hardywright2008}:
$$
\sum_{n \le x} \tau(n) = x \ln x + (2\gamma - 1)x + O(\sqrt{x}), \qquad \sum_{n \le x} \varphi(n) = \frac{3}{\pi^2} x^2 + O(x \ln x),
$$
with $\gamma \approx 0.5772$ Euler's constant.

```python run
import math

N = 10 ** 5
tau = [0] * (N + 1)
for d in range(1, N + 1):
    for m in range(d, N + 1, d):
        tau[m] += 1
phi = list(range(N + 1))
for p in range(2, N + 1):
    if phi[p] == p:                                  # p is prime
        for m in range(p, N + 1, p):
            phi[m] -= phi[m] // p
gamma = 0.5772156649015329
for x in (10 ** 3, 10 ** 4, 10 ** 5):
    T, P = sum(tau[1:x + 1]), sum(phi[1:x + 1])
    print(f"x = {x:>6d}: sum tau = {T:>8d}  vs x ln x + (2γ-1)x = {x * math.log(x) + (2 * gamma - 1) * x:>11.1f}"
          f"   sum phi / (3x²/π²) = {P / (3 * x * x / math.pi ** 2):.7f}")
```

```output
x =   1000: sum tau =     7069  vs x ln x + (2γ-1)x =      7062.2   sum phi / (3x²/π²) = 1.0007516
x =  10000: sum tau =    93668  vs x ln x + (2γ-1)x =     93647.7   sum phi / (3x²/π²) = 1.0000372
x = 100000: sum tau =  1166750  vs x ln x + (2γ-1)x =   1166735.7   sum phi / (3x²/π²) = 1.0000050
```

The second formula has a probabilistic reading. Since $\sum_{n \le x} \varphi(n)$ counts pairs $1 \le k \le n \le x$ with $\gcd(k, n) = 1$, about $\tfrac{6}{\pi^2} \approx 0.6079$ of all pairs of integers are coprime:

```python run
import math, random

random.seed(32)
trials = 100_000
for bits in (16, 64):
    coprime = sum(math.gcd(random.getrandbits(bits), random.getrandbits(bits)) == 1 for _ in range(trials))
    print(f"{bits}-bit pairs: fraction coprime {coprime / trials:.4f}   6/π² = {6 / math.pi ** 2:.4f}")
```

```output
16-bit pairs: fraction coprime 0.6089   6/π² = 0.6079
64-bit pairs: fraction coprime 0.6078   6/π² = 0.6079
```

This probability governs the converse problems of earlier chapters. A random division $b c = a$ in $\Z/n$ with random $b$ is uniquely solvable with probability $\varphi(n)/n$; a random fraction $p/q$ is already in lowest terms with probability about $0.61$, so more often than not the gcd computed by a rational-arithmetic library finds nothing to cancel (Chapter 27).

## Perfect, abundant and deficient {#sec:perfect}

The oldest question about $\sigma$ is Euclid's: when is $\sigma(n) = 2n$? Euclid proved that $2^{k-1}(2^k - 1)$ is perfect when $2^k - 1$ is prime, and Euler proved that every even perfect number has this form \cite{hardywright2008}. Whether an odd perfect number exists is open.

```python run
N = 10_000
sigma = [0] * (N + 1)
for d in range(1, N + 1):
    for m in range(d, N + 1, d):
        sigma[m] += d
print("perfect numbers up to 10^4:", [n for n in range(1, N + 1) if sigma[n] == 2 * n])
print("abundant (sigma(n) > 2n):", sum(sigma[n] > 2 * n for n in range(1, N + 1)),
      "  deficient:", sum(sigma[n] < 2 * n for n in range(1, N + 1)))
```

```output
perfect numbers up to 10^4: [6, 28, 496, 8128]
abundant (sigma(n) > 2n): 2488   deficient: 7508
```

::: exercise {#ex:af-phi}
Prove $\sum_{d \mid n} \varphi(d) = n$ by sorting the fractions $1/n, 2/n, \ldots, n/n$ by their reduced denominators.
:::

::: solution {of="ex:af-phi"}
Each $k/n$ reduces to a unique $a/d$ with $d \mid n$, $1 \le a \le d$ and $\gcd(a, d) = 1$; conversely each such $a/d$ arises from exactly one $k = an/d$. There are $\varphi(d)$ fractions with reduced denominator $d$, so $n = \sum_{d \mid n} \varphi(d)$, i.e. $\varphi * \mathbf{1} = \mathrm{id}$.
:::

::: exercise {#ex:af-inverse}
Compute the Dirichlet inverse of $\mathrm{id}$ on $n = 1, \ldots, 6$, and guess a formula.
:::

::: solution {of="ex:af-inverse"}
$g(1) = 1$; $g(n) = -\sum_{d \mid n, d > 1} d \cdot g(n/d)$ gives $g(2) = -2$, $g(3) = -3$, $g(4) = -(2 g(2) + 4 g(1)) = 0$, $g(5) = -5$, $g(6) = -(2g(3) + 3g(2) + 6g(1)) = 6$. Formula: $g(n) = \mu(n)\, n$. (For a completely multiplicative $f$, the inverse is $\mu f$.)
:::

::: exercise {#ex:af-nonunit}
Let $f(1) = 0$, $f(2) = 1$, and $f(n) = 0$ otherwise. For which $h$ does $f * g = h$ have a solution, and what is it?
:::

::: solution {of="ex:af-nonunit"}
$(f * g)(n) = g(n/2)$ if $n$ is even and $0$ if $n$ is odd. So a solution exists iff $h(n) = 0$ for every odd $n$, and then $g(m) = h(2m)$ — unique, as Proposition \ref{prop:dirichlet-units} predicts.
:::

::: summary
- $\tau$, $\sigma$, $\varphi$, $\mu$ are multiplicative; unique factorization makes them determined by prime powers.
- Dirichlet convolution makes arithmetic functions a commutative ring with identity $\varepsilon$ and no zero divisors; its units are the $f$ with $f(1) \ne 0$ (over $\Z$: $\pm 1$).
- Möbius inversion is division by $\mathbf{1}$, admissible because $\mathbf{1}(1) = 1$; $\mu = \mathbf{1}^{-1}$.
- Averages are smooth: $\sum \tau \approx x \ln x + (2\gamma - 1)x$, $\sum \varphi \approx 3x^2/\pi^2$; two random integers are coprime with probability $6/\pi^2$.
- Even perfect numbers are $2^{k-1}(2^k - 1)$ with $2^k - 1$ prime; odd ones are unknown.
:::
