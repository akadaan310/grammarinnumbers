---
title: "Congruences, Orders, and the Converse of Exponentiation"
status: mixed
statusnote: The theorems are classical; their reading as converse problems with image/kernel structure, and the censuses, are this book's.
description: Congruence as an equality that forgets, linear congruences and the Chinese remainder theorem as converse problems, the theorems of Fermat, Euler and Wilson, the order of an element and primitive roots, the discrete logarithm as the converse of modular exponentiation with its census of none / one / many, and quadratic residues.
epigraph: "a ≡ b (mod n) is an equation that has agreed to forget everything but the last digit in base n."
---

::: objectives
- Use congruence as an equivalence compatible with $+$ and $\times$, and solve linear congruences and systems of them.
- State and prove Fermat's and Euler's theorems, and Wilson's theorem as a test that is exact and useless.
- Compute orders of elements, recognize primitive roots, and check the classification of moduli that have them.
- Treat the discrete logarithm as the converse of $x \mapsto g^x$, and predict its number of solutions from the image/kernel theorem.
- Decide quadratic residuosity with Euler's criterion.
:::

## An equality that forgets {#sec:congruence}

Gauss introduced the notation $a \equiv b \pmod n$ — "$n$ divides $a - b$" — in the *Disquisitiones Arithmeticae*, choosing the sign for its analogy with equality \cite{gauss1801}. The analogy is exact in one direction: congruence modulo $n$ is an equivalence relation compatible with addition and multiplication, so it can be used like an equality inside sums and products. It is an equality *after* the homomorphism $\Z \to \Z/n$ of Chapter 29, which keeps the residue and forgets the rest.

What it forgets matters for every operation that is not a ring operation:

- **Cancellation** requires a unit: $2 \cdot 3 \equiv 2 \cdot 8 \pmod{10}$, but $3 \not\equiv 8$.
- **Exponents** live in a different modulus: $a^{x}$ modulo $n$ depends on $x$ modulo the order of $a$, not modulo $n$ (below).
- **Division** is the converse problem of Chapter 16, with none, one or $\gcd(b, n)$ solutions (\ledger{GIN-THM-002}).

## Systems: the Chinese remainder theorem {#sec:crt}

A system $x \equiv r_1 \pmod{m_1}, \ldots, x \equiv r_k \pmod{m_k}$ asks for the converse of the map $x \mapsto (x \bmod m_1, \ldots, x \bmod m_k)$. That map is a ring homomorphism $\Z/L \to \prod \Z/m_i$ with $L = \mathrm{lcm}(m_i)$, and it is injective, so by the image/kernel theorem a solution, if it exists, is unique modulo $L$ (\ledger{GIN-PROP-042}). For pairwise coprime moduli it is also surjective: every system is solvable.

```python run
from ginsdk import numbertheory as nt

for residues, moduli in (([2, 3, 2], [3, 5, 7]), ([1, 3], [4, 6]), ([1, 2], [4, 6])):
    print(f"x ≡ {residues} mod {moduli}:  ->", nt.crt(residues, moduli))
```

```output
x ≡ [2, 3, 2] mod [3, 5, 7]:  -> (23, 105)
x ≡ [1, 3] mod [4, 6]:  -> (9, 12)
x ≡ [1, 2] mod [4, 6]:  -> None
```

The first system is Sunzi's classical example: $23$ is the unique solution modulo $105$. The second is solvable although the moduli share the factor $2$, because $1 \equiv 3 \pmod 2$; the solution is unique modulo $\mathrm{lcm}(4, 6) = 12$. The third asks for a number that is odd ($1 \bmod 4$) and even ($2 \bmod 6$): the image condition fails, and there is no solution.

## Fermat, Euler, Wilson {#sec:fermat}

::: theorem {#thm:euler title="Euler's theorem (Fermat's little theorem for n = p)" status="classical" ledger="GIN-HIST-012"}
If $\gcd(a, n) = 1$ then $a^{\varphi(n)} \equiv 1 \pmod n$. In particular, for a prime $p \nmid a$, $a^{p-1} \equiv 1 \pmod p$.
:::

::: proof
The units of $\Z/n$ form a group $U$ of order $\varphi(n)$. Multiplication by the unit $a$ permutes $U$ (it is injective, Chapter 29). Hence $\prod_{u \in U} au = \prod_{u \in U} u$, that is, $a^{\varphi(n)} P = P$ with $P$ a unit, and cancelling $P$ gives the claim.
:::

The theorem is the basis of the Fermat primality test of Chapter 35 — and of its failure: the converse statement "if $a^{n-1} \equiv 1$ then $n$ is prime" is false (\ledger{GIN-PROP-043}).

::: theorem {#thm:wilson title="Wilson's theorem" status="classical" ledger="GIN-HIST-013"}
For $n \ge 2$: $n$ is prime if and only if $(n - 1)! \equiv -1 \pmod n$.
:::

::: proof
For a prime $p$, each $a \in \{1, \ldots, p - 1\}$ has an inverse in the same set, and $a = a^{-1}$ only for $a = \pm 1$ (since $a^2 \equiv 1$ means $p \mid (a - 1)(a + 1)$). Pairing every other element with its inverse leaves $(p - 1)! \equiv 1 \cdot (-1)$. For composite $n = ab$ with $1 < a < n$, $a$ divides $(n - 1)!$ and $n$, so it cannot divide $(n-1)! + 1$.
:::

```python run
import math
print("n < 40 with (n-1)! ≡ -1 (mod n):", [n for n in range(2, 40) if math.factorial(n - 1) % n == n - 1])
print("decimal digits of (n-1)! for n = 1,000,003:", int(math.lgamma(1_000_003) / math.log(10)) + 1)
```

```output
n < 40 with (n-1)! ≡ -1 (mod n): [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
decimal digits of (n-1)! for n = 1,000,003: 5565721
```

Wilson's theorem is an *exact* primality criterion, and computationally worthless: the factorial has millions of digits for a seven-digit $n$, and no method is known to compute $(n-1)! \bmod n$ in time polynomial in the number of digits of $n$. Exactness is not the same as feasibility — the cost model of Chapter 36 is part of what a "test" is.

## Orders and primitive roots {#sec:orders}

The **order** of a unit $a$ modulo $n$ is the least $d \ge 1$ with $a^d \equiv 1$. By Euler's theorem (and Lagrange's theorem for groups) $d$ divides $\varphi(n)$. Powers of $a$ repeat with period $d$: $a^x$ depends only on $x \bmod d$.

A **primitive root** is a unit of order $\varphi(n)$ — one whose powers run through all units. When it exists, the unit group is cyclic, and every unit is a power of one generator: a *successor grammar* (Chapter 3) for the multiplicative group, with "multiply by $g$" as the successor.

::: theorem {#thm:primitive-roots title="Which moduli have primitive roots" status="classical" ledger="GIN-HIST-014"}
$\Z/n$ has a primitive root if and only if $n$ is $1$, $2$, $4$, $p^k$ or $2p^k$ for an odd prime $p$ and $k \ge 1$ \cite{hardywright2008}.
:::

```python run
from math import gcd
from ginsdk import numbertheory as nt

def order(a, n):
    k, x = 1, a % n
    while x != 1:
        x, k = x * a % n, k + 1
    return k

def has_primitive_root(n):
    return any(order(a, n) == nt.phi(n) for a in range(1, n) if gcd(a, n) == 1)

def classified(n):
    f = nt.factorize(n)
    return n in (2, 4) or (len(f) == 1 and 2 not in f) or (len(f) == 2 and f.get(2) == 1)

print("n < 60 with a primitive root:", [n for n in range(2, 60) if has_primitive_root(n)])
print("search agrees with the classification for all 2 <= n < 400:",
      all(has_primitive_root(n) == classified(n) for n in range(2, 400)))
print("orders of the units mod 11:", {a: order(a, 11) for a in range(1, 11)})
```

```output
n < 60 with a primitive root: [2, 3, 4, 5, 6, 7, 9, 10, 11, 13, 14, 17, 18, 19, 22, 23, 25, 26, 27, 29, 31, 34, 37, 38, 41, 43, 46, 47, 49, 50, 53, 54, 58, 59]
search agrees with the classification for all 2 <= n < 400: True
orders of the units mod 11: {1: 1, 2: 10, 3: 5, 4: 5, 5: 5, 6: 10, 7: 10, 8: 10, 9: 5, 10: 2}
```

## The converse of exponentiation {#sec:dlog}

Modular exponentiation $x \mapsto g^x \bmod p$ is fast (Chapter 34). Its converse — given $g$ and $b$, find $x$ with $g^x \equiv b$ — is the **discrete logarithm** problem, and no polynomial-time classical algorithm is known for it in general; the security of Diffie–Hellman key exchange rests on that. Its *admissibility*, however, is completely understood, and it is a case of the image/kernel theorem (\ledger{GIN-THM-007}):

::: proposition {#prop:dlog-structure title="The structure of a discrete logarithm" status="proved-here" ledger="GIN-PROP-074"}
Let $p$ be prime and $g$ a unit of order $d$ modulo $p$. The map $E_g : \Z/(p-1) \to (\Z/p)^\times$, $x \mapsto g^x$, is a group homomorphism with kernel $d\Z/(p-1)$ and image the $d$ powers of $g$. Hence $g^x \equiv b$ has no solution if $b \notin \langle g \rangle$, and exactly $(p-1)/d$ solutions in $\Z/(p-1)$ if $b \in \langle g \rangle$. It has exactly one solution for every $b$ if and only if $g$ is a primitive root.
:::

::: proof
$g^{x + y} = g^x g^y$, and $g^{x}$ is well defined for $x \in \Z/(p-1)$ because $g^{p-1} \equiv 1$. $g^x \equiv 1$ iff $d \mid x$, which describes the kernel; it has $(p-1)/d$ elements. The image is $\langle g \rangle$, of size $d$. The solution set of $E_g(x) = b$ is empty or a coset of the kernel.
:::

```python run
from collections import Counter

p = 11
census = Counter()
for g in range(1, p):
    for b in range(1, p):
        census[sum(1 for x in range(p - 1) if pow(g, x, p) == b)] += 1
print(f"g^x ≡ b (mod {p}) over all 100 pairs (g, b): number of solutions x in Z/10 ->", dict(sorted(census.items())))
```

```output
g^x ≡ b (mod 11) over all 100 pairs (g, b): number of solutions x in Z/10 -> {0: 37, 1: 40, 2: 20, 5: 2, 10: 1}
```

The census is predicted exactly by the proposition. Modulo $11$ the unit orders are $1$ (for $g = 1$), $2$ ($g = 10$), $5$ (four elements) and $10$ (four primitive roots). The four primitive roots give $40$ pairs with one solution; the order-5 elements give $20$ pairs with $2$ solutions and $20$ with none; $g = 10$ gives $2$ pairs with $5$ solutions and $8$ with none; $g = 1$ gives one pair ($b = 1$) with $10$ solutions and $9$ with none: $40 + 20 + 2 + 1$ solvable, $20 + 8 + 9 = 37$ not.

The converse of exponentiation therefore has the same three outcomes as the converse of multiplication — none, one, many — with the same algebraic explanation. What differs is *cost*: for multiplication, the extended Euclidean algorithm finds a solution in polynomially many steps (Chapter 33); for exponentiation, the best general algorithms take time exponential in a fractional power of the number of digits. Admissibility can be easy when solving is hard.

## Quadratic residues {#sec:qr}

The converse of squaring, $c^2 \equiv a \pmod p$, is the first non-linear converse problem in this book whose solution sets are not cosets (\ledger{GIN-NEG-019}). For an odd prime $p$ and $a \not\equiv 0$, it has $0$ or $2$ solutions, and exactly half of the units are squares.

::: theorem {#thm:euler-criterion title="Euler's criterion" status="classical" ledger="GIN-HIST-015"}
For an odd prime $p$ and $p \nmid a$: $a$ is a square modulo $p$ iff $a^{(p-1)/2} \equiv 1 \pmod p$; otherwise $a^{(p-1)/2} \equiv -1$.
:::

```python run
p = 23
squares = sorted({x * x % p for x in range(1, p)})
print(f"squares mod {p}:", squares, f" ({len(squares)} of {p - 1})")
print("Euler's criterion agrees for every unit:", all((pow(a, (p - 1) // 2, p) == 1) == (a in squares) for a in range(1, p)))
```

```output
squares mod 23: [1, 2, 3, 4, 6, 8, 9, 12, 13, 16, 18]  (11 of 22)
Euler's criterion agrees for every unit: True
```

Euler's criterion decides admissibility with one exponentiation, without finding a root. Finding the root is a further step (for $p \equiv 3 \pmod 4$ the root is $a^{(p+1)/4}$; in general, the Tonelli–Shanks algorithm). Deciding *whether* a converse problem is solvable and *solving* it are different computational problems, as the discrete logarithm showed.

::: exercise {#ex:cong-cancel}
Show that if $ab \equiv ac \pmod n$ and $\gcd(a, n) = g$, then $b \equiv c \pmod{n/g}$, and that this cannot in general be strengthened to $\bmod n$.
:::

::: solution {of="ex:cong-cancel"}
$n \mid a(b - c)$ gives $(n/g) \mid (a/g)(b - c)$, and $\gcd(a/g, n/g) = 1$, so $(n/g) \mid (b - c)$ by Euclid's lemma generalized (Bézout). Example: $2 \cdot 3 \equiv 2 \cdot 8 \pmod{10}$ and $3 \equiv 8 \pmod 5$, but $3 \not\equiv 8 \pmod{10}$.
:::

::: exercise {#ex:cong-power}
Compute $3^{1000} \bmod 7$ by hand using the order of $3$.
:::

::: solution {of="ex:cong-power"}
$3^1 = 3, 3^2 = 2, 3^3 = 6, 3^4 = 4, 3^5 = 5, 3^6 = 1$: order $6$ (a primitive root). $1000 = 6 \cdot 166 + 4$, so $3^{1000} \equiv 3^4 \equiv 4$.
:::

::: exercise {#ex:cong-dlog}
Modulo $13$, how many solutions does $4^x \equiv 3$ have in $\Z/12$, and how many does $4^x \equiv 2$ have?
:::

::: solution {of="ex:cong-dlog"}
Powers of $4$ mod $13$: $4, 3, 12, 9, 10, 1$, so $4$ has order $6$ and $\langle 4 \rangle = \{1, 3, 4, 9, 10, 12\}$. $3 \in \langle 4 \rangle$: $12/6 = 2$ solutions ($x = 2, 8$). $2 \notin \langle 4 \rangle$: none.
:::

::: summary
- Congruence is equality after $\Z \to \Z/n$; it supports $+$ and $\times$ but not cancellation by non-units, and exponents live modulo orders.
- The Chinese remainder theorem is the converse of an injective homomorphism: solutions are unique modulo the lcm when they exist.
- Euler: $a^{\varphi(n)} \equiv 1$; Wilson's criterion is exact but infeasible.
- Primitive roots exist exactly for $n = 1, 2, 4, p^k, 2p^k$ (checked for $n < 400$); they make the unit group a successor grammar.
- The discrete logarithm is the converse of a homomorphism: none, or $(p-1)/d$ solutions; deciding admissibility is easy, solving is believed hard.
- Euler's criterion decides whether a square root exists without computing one.
:::
