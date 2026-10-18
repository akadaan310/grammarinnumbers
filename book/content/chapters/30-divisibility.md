---
title: "Divisibility, Primes, and Unique Factorization"
status: mixed
statusnote: The theorems are classical; the readings of divisibility as admissibility and of the divisibility order as a lattice with 0 on top are presented in this book's vocabulary; the counts are computed here.
description: Divisibility as the admissibility condition of integer division, the divisibility order (in which 0 is the largest number), primes as the atoms of multiplication, the fundamental theorem of arithmetic proved from Bézout's identity, a ring in which factorization is not unique, Euclid's theorem as an algorithm, and the measured distribution of primes below one million.
epigraph: "In the divisibility order, 1 is the least number and 0 is the greatest."
---

::: objectives
- Read $b \mid a$ as the admissibility condition of the converse problem $bc = a$ in $\Z$.
- Describe the divisibility order on $\N$ as a lattice with meet $\gcd$, join $\mathrm{lcm}$, least element $1$ and greatest element $0$.
- Prove the fundamental theorem of arithmetic, and identify the step that fails in $\Z[\sqrt{-5}]$.
- Turn Euclid's proof of the infinitude of primes into a procedure, and run it.
- Compare the count of primes below $x$ with $x / \ln x$.
:::

## Divisibility is admissibility {#sec:divides}

Chapter 16 defined division as the converse problem: given $a$ and $b$, find $c$ with $bc = a$. In $\Z$ the problem is *admissible* exactly when $b \mid a$:

::: definition {#def:divides title="Divisibility" status="classical" ledger="GIN-DEF-095"}
For integers $a, b$, *$b$ divides $a$*, written $b \mid a$, if $a = bc$ for some integer $c$. Equivalently: the converse problem $bc = a$ has a solution in $\Z$. If $b \ne 0$ the solution is unique; if $b = 0$ it exists only for $a = 0$, and then every integer is one.
:::

The definition contains the four-way case analysis of Chapter 17 in miniature. $0 \mid 0$ is true — the problem $0 \cdot c = 0$ is admissible, with every $c$ a solution — even though $0/0$ is undefined: *divisibility asks whether a solution exists, division asks for the solution*. Under the definition, $0 \mid 0$ holds; a programmer who implements `divides(a, b)` as `a % b == 0` gets an exception for $b = 0$ in most languages, and has silently changed the question.

```python run
def divides_by_definition(b, a, bound=50):
    return any(b * c == a for c in range(-bound, bound + 1))

def divides_by_remainder(b, a):
    return a % b == 0

for b, a in ((3, 12), (5, 12), (0, 0), (0, 7), (7, 0)):
    try:
        r = divides_by_remainder(b, a)
    except ZeroDivisionError as e:
        r = f"ZeroDivisionError: {e}"
    print(f"{b} | {a}:  definition {divides_by_definition(b, a)!s:5s}   a % b == 0 -> {r}")
```

```output
3 | 12:  definition True    a % b == 0 -> True
5 | 12:  definition False   a % b == 0 -> False
0 | 0:  definition True    a % b == 0 -> ZeroDivisionError: integer modulo by zero
0 | 7:  definition False   a % b == 0 -> ZeroDivisionError: integer modulo by zero
7 | 0:  definition True    a % b == 0 -> True
```

## The divisibility order {#sec:div-order}

On $\N$, divisibility is a partial order: reflexive ($a \mid a$), antisymmetric ($a \mid b$ and $b \mid a$ imply $a = b$ for natural numbers) and transitive. It is very different from the usual order:

- $1$ divides everything: it is the **least** element.
- Everything divides $0$ ($a \cdot 0 = 0$): $0$ is the **greatest** element.
- $\gcd(a, b)$ is the greatest lower bound and $\mathrm{lcm}(a, b)$ the least upper bound, so the order is a *lattice*; with $\gcd(0, a) = a$ and $\mathrm{lcm}(0, a) = 0$ the conventions for zero are not arbitrary but forced by the order.
- The elements just above $1$ — those whose only divisors are $1$ and themselves — are the **primes**: the *atoms* of the lattice.

::: proposition {#prop:div-lattice title="ℕ under divisibility is a lattice with 1 at the bottom and 0 at the top" status="classical" ledger="GIN-PROP-073"}
$(\N, \mid)$ is a partial order in which every pair has a greatest lower bound $\gcd(a, b)$ and a least upper bound $\mathrm{lcm}(a, b)$, with $1$ least and $0$ greatest. Its atoms are the primes.
:::

::: proof
Antisymmetry: $b = ac$, $a = bd$ give $a = acd$; if $a \ne 0$ then $cd = 1$ and $c = d = 1$ in $\N$; if $a = 0$ then $b = 0$. That $\gcd$ is the greatest lower bound in this order — every common divisor divides it, not merely is at most it — is Bézout's identity (Chapter 33): $\gcd(a, b) = ua + vb$, so any common divisor of $a, b$ divides the right-hand side. The statement for $\mathrm{lcm}$ follows from $\gcd(a, b)\,\mathrm{lcm}(a, b) = ab$ for $a, b > 0$ and is direct when one of them is $0$.
:::

The order restricted to the divisors of $60$ is a finite lattice whose shape is the product of chains for $2^2$, $3$ and $5$:

```python run
from ginsdk import numbertheory as nt

divisors = nt.divisors(60)
covers = [(a, b) for a in divisors for b in divisors if b != a and b % a == 0 and nt.is_prime(b // a)]
print("divisors of 60:", divisors)
print("covering pairs (b = a * prime):", len(covers), "  = edges of a 3 x 2 x 2 grid:", 2*2*2 + 3*1*2 + 3*2*1)
for d in divisors:
    up = [b for a, b in covers if a == d]
    print(f"  {d:>2} -> {up}")
```

```output
divisors of 60: [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]
covering pairs (b = a * prime): 20   = edges of a 3 x 2 x 2 grid: 20
   1 -> [2, 3, 5]
   2 -> [4, 6, 10]
   3 -> [6, 15]
   4 -> [12, 20]
   5 -> [10, 15]
   6 -> [12, 30]
  10 -> [20, 30]
  12 -> [60]
  15 -> [30]
  20 -> [60]
  30 -> [60]
  60 -> []
```

## Unique factorization {#sec:ufd}

Every natural number greater than $1$ is a product of primes: take any divisor other than $1$ and itself and recurse; the recursion stops because factors are smaller. The deep part is *uniqueness*, and it rests on one lemma.

::: lemma {#lem:euclid-lemma title="Euclid's lemma" status="classical" ledger="GIN-HIST-009"}
If a prime $p$ divides $ab$, then $p \mid a$ or $p \mid b$.
:::

::: proof
Suppose $p \nmid a$. The only positive divisors of $p$ are $1$ and $p$, so $\gcd(p, a) = 1$, and by Bézout's identity $1 = up + va$ for some integers $u, v$. Multiplying by $b$: $b = upb + v(ab)$. Both terms are multiples of $p$, so $p \mid b$.
:::

::: theorem {#thm:fta title="The fundamental theorem of arithmetic" status="classical" ledger="GIN-HIST-010"}
Every integer $n > 1$ is a product of primes, and the product is unique up to the order of the factors.
:::

::: proof
Existence as above. Uniqueness, by induction on $n$: if $p_1 \cdots p_r = q_1 \cdots q_s$, then $p_1$ divides the right side, so by the lemma (applied repeatedly) $p_1 \mid q_j$ for some $j$, hence $p_1 = q_j$ because $q_j$ is prime. Cancel it and apply the induction hypothesis to the smaller number $n / p_1$.
:::

The fundamental theorem says that $\N_{>0}$ under multiplication is the *free commutative monoid* on the primes: a number is the same thing as a finite multiset of primes, and multiplication is union of multisets. Exponent vectors are a second positional notation for natural numbers, with one "digit" per prime and no carries — in which multiplication is addition and $\gcd$ and $\mathrm{lcm}$ are componentwise minimum and maximum, while addition becomes intractable. Which operations are easy depends on the numeral, a theme of Part III that returns in Chapter 35, where finding this second numeral (factorization) is hard.

Uniqueness is not automatic. It fails as soon as Euclid's lemma fails:

::: counterexample {#neg:z-sqrt-5 title="Factorization into irreducibles is unique in every ring of integers" status="counterexample" ledger="GIN-NEG-023"}
In $\Z[\sqrt{-5}] = \{a + b\sqrt{-5}\}$, $6 = 2 \cdot 3 = (1 + \sqrt{-5})(1 - \sqrt{-5})$, and none of the four factors can be written as a product of two non-units. The element $2$ divides $(1 + \sqrt{-5})(1 - \sqrt{-5})$ but neither factor: it is *irreducible* without being *prime*.
:::

The check uses the multiplicative norm $N(a + b\sqrt{-5}) = a^2 + 5b^2$: a factorization of an element of norm $4$, $9$ or $6$ into two non-units would need factors of norm $2$ or $3$, and $a^2 + 5b^2$ takes neither value.

```python run
norm = lambda a, b: a * a + 5 * b * b
print("norms of 2, 3, 1+√-5, 1-√-5:", norm(2, 0), norm(3, 0), norm(1, 1), norm(1, -1))
values = {norm(a, b) for a in range(-3, 4) for b in range(-2, 3)}
print("norms 2 or 3 attained (|a| <= 3, |b| <= 2 suffices):", sorted(values & {2, 3}))
print("is (1+√-5)/2 in the ring? its coordinates are", (1 / 2, 1 / 2), "-> no")
```

```output
norms of 2, 3, 1+√-5, 1-√-5: 4 9 6 6
norms 2 or 3 attained (|a| <= 3, |b| <= 2 suffices): []
is (1+√-5)/2 in the ring? its coordinates are (0.5, 0.5) -> no
```

In the vocabulary of this book, unique factorization is a *uniqueness* clause of a converse problem — "which multisets of primes multiply to $n$?" — and $\Z[\sqrt{-5}]$ is a domain in which that problem is non-unique.

## Infinitely many primes {#sec:euclid-primes}

::: theorem {#thm:infinite-primes title="There are infinitely many primes (Euclid, Elements IX.20)" status="classical" ledger="GIN-HIST-011"}
For every finite set $S$ of primes there is a prime not in $S$.
:::

::: proof
Let $N = 1 + \prod_{p \in S} p$. $N > 1$, so it has a prime factor $q$. If $q \in S$, then $q$ divides both $N$ and $N - 1$, hence divides $1$ — impossible.
:::

The proof is an algorithm: from a list of primes it computes a new one. Starting from $\{2\}$ and always adding the *smallest* prime factor produces the Euclid–Mullin sequence:

```python run
import math
from ginsdk import numbertheory as nt

primes = [2]
for _ in range(7):
    N = math.prod(primes) + 1
    q = min(nt.factorize(N))
    print(f"1 + product of {len(primes)} primes = {N:<14d} smallest prime factor {q}")
    primes.append(q)
```

```output
1 + product of 1 primes = 3              smallest prime factor 3
1 + product of 2 primes = 7              smallest prime factor 7
1 + product of 3 primes = 43             smallest prime factor 43
1 + product of 4 primes = 1807           smallest prime factor 13
1 + product of 5 primes = 23479          smallest prime factor 53
1 + product of 6 primes = 1244335        smallest prime factor 5
1 + product of 7 primes = 6221671        smallest prime factor 6221671
```

The primes do not arrive in order — $5$ appears seventh — and whether every prime eventually appears is an open question. The algorithm is correct (each output is a new prime) but its outputs are not a *grammar* of the primes in the sense of Chapter 3: they are not produced by a successor that visits each exactly once.

## How many primes? {#sec:pnt}

The *prime number theorem* states that the number $\pi(x)$ of primes up to $x$ satisfies $\pi(x) \sim x / \ln x$ \cite{hardywright2008}. The ratio converges slowly:

```python run
import bisect, math
from ginsdk import numbertheory as nt

primes = nt.sieve(10 ** 6)
for k in range(2, 7):
    x = 10 ** k
    pi = bisect.bisect_right(primes, x)
    print(f"x = 10^{k}:  pi(x) = {pi:6d}   x/ln x = {x / math.log(x):9.1f}   ratio {pi / (x / math.log(x)):.4f}")
gaps = [b - a for a, b in zip(primes, primes[1:])]
g = max(gaps)
i = gaps.index(g)
print(f"largest gap below 10^6: {g}, between {primes[i]} and {primes[i + 1]}")
```

```output
x = 10^2:  pi(x) =     25   x/ln x =      21.7   ratio 1.1513
x = 10^3:  pi(x) =    168   x/ln x =     144.8   ratio 1.1605
x = 10^4:  pi(x) =   1229   x/ln x =    1085.7   ratio 1.1320
x = 10^5:  pi(x) =   9592   x/ln x =    8685.9   ratio 1.1043
x = 10^6:  pi(x) =  78498   x/ln x =   72382.4   ratio 1.0845
largest gap below 10^6: 114, between 492113 and 492227
```

The density of primes near $x$ is about $1/\ln x$: among 20-digit numbers about one in $46$ is prime, among 300-digit numbers about one in $690$. This is why random search for large primes works (Chapter 35): primes are rare, but not *too* rare, and testing one candidate is cheap.

::: exercise {#ex:div-zero}
Using only the definition, decide each of $0 \mid 5$, $5 \mid 0$, $0 \mid 0$, $-3 \mid 6$, and say which of the corresponding divisions $5/0$, $0/5$, $0/0$, $6/(-3)$ have a unique answer in $\Z$.
:::

::: solution {of="ex:div-zero"}
$0 \mid 5$ is false; $5 \mid 0$ true ($c = 0$); $0 \mid 0$ true (every $c$); $-3 \mid 6$ true ($c = -2$). Unique answers: $0/5 = 0$ and $6/(-3) = -2$. $5/0$ has none and $0/0$ has every integer.
:::

::: exercise {#ex:div-gcd-lcm}
Show that in the divisibility lattice $\gcd(a, \mathrm{lcm}(a, b)) = a$, and compute $\gcd(0, 0)$ and $\mathrm{lcm}(0, 0)$ from the order alone.
:::

::: solution {of="ex:div-gcd-lcm"}
$a \mid \mathrm{lcm}(a, b)$, so $a$ is a common lower bound of $a$ and the $\mathrm{lcm}$, and no common lower bound can exceed $a$ — this is the absorption law of lattices. $\gcd(0, 0)$ is the greatest element below $0$ and $0$, which is $0$ itself; $\mathrm{lcm}(0, 0) = 0$. (Python's `math.gcd(0, 0)` returns $0$, in agreement.)
:::

::: exercise {#ex:div-z-sqrt-5}
Show that $3$ is irreducible but not prime in $\Z[\sqrt{-5}]$.
:::

::: solution {of="ex:div-z-sqrt-5"}
Irreducible: a factorization into non-units would need two factors of norm $3$, and $a^2 + 5b^2 = 3$ has no integer solution. Not prime: $3 \mid 6 = (1 + \sqrt{-5})(1 - \sqrt{-5})$, but $(1 \pm \sqrt{-5})/3$ is not in the ring.
:::

::: summary
- $b \mid a$ means that the converse problem $bc = a$ is admissible in $\Z$; $0 \mid 0$ is true although $0/0$ is undefined.
- Divisibility orders $\N$ as a lattice with $\gcd$, $\mathrm{lcm}$, least element $1$, greatest element $0$, and the primes as atoms.
- Unique factorization rests on Euclid's lemma, which rests on Bézout; it fails in $\Z[\sqrt{-5}]$, where irreducible and prime differ.
- Euclid's proof is an algorithm producing new primes, not in order; $\pi(x) / (x / \ln x) \to 1$ slowly (1.0845 at $10^6$).
:::
