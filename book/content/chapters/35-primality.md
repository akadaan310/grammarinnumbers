---
title: "Sieves, Primality Tests, and Factoring Baselines"
status: mixed
statusnote: The theorems and algorithms are classical (Eratosthenes, Fermat, Korselt, Miller, Rabin, Pollard); the counts below 10⁶ reproduce published values; the census of strong liars is an exhaustive computation in this book.
description: Primality as an admissibility question — "does n have a non-trivial divisor?" — answered by precomputation (sieves), by search (trial division), and by tests that check a necessary condition (Fermat, Miller–Rabin); the counterexamples to each test; deterministic versus probabilistic error statements; and the two factoring baselines the book implements.
epigraph: "A test that can only say 'probably' must say what the probability is over."
---

::: objectives
- Treat primality as a question about the solution set of $n = d \cdot e$ with $1 < d < n$ — a converse problem of multiplication — and classify the methods by how they answer it.
- Analyze the sieve of Eratosthenes and trial division, by counted operations.
- Prove why Fermat's test can be fooled, identify pseudoprimes and Carmichael numbers, and reproduce their published counts.
- State the Miller–Rabin test precisely, distinguish its probabilistic and deterministic uses, and say exactly what its error bound is a probability over.
- Measure two factoring baselines and state their costs.
:::

## Primality as admissibility {#sec:prime-adm}

Chapter 30 defined a prime as a number with exactly two divisors. In the vocabulary of Chapter 9, $n > 1$ is composite exactly when the converse problem "find $d, e$ with $d \cdot e = n$ and $1 < d, e < n$" has a solution. Methods for primality differ in what they do with that problem:

| method | how it answers | cost for $L$-bit $n$ | can it be wrong? |
|---|---|---|---|
| sieve | precomputes the answer for all $m \le N$ | $\Oh(N \log \log N)$ crossings, then $\Oh(1)$ per query | no |
| trial division | searches for a solution $d \le \sqrt n$ | up to $\approx \sqrt n / 2 = 2^{L/2}/2$ divisions | no |
| Fermat test | checks a property every prime has | one modular exponentiation | yes: says "probably prime" for some composites |
| Miller–Rabin | checks a stronger property | one modular exponentiation per base | yes, with a bounded error per random base |
| factoring | exhibits a solution $(d, e)$ | super-polynomial for the best known methods | no (it proves compositeness) |

The two kinds of answer have different evidential status: a sieve, trial division or a found factor *prove* their answer; a Fermat or Miller–Rabin "probably prime" is only the failure to find a witness of compositeness. In CGT's terms the sieve is precomputation, trial division is search, and the tests are cheap admissibility checks that are **sound for one answer only** — a found witness proves compositeness, and its absence proves nothing.

## The sieve: precomputation {#sec:sieve}

Eratosthenes' sieve writes $2, \ldots, N$ and, for each prime $p \le \sqrt N$ not yet crossed out, crosses out $p^2, p^2 + p, \ldots$. Every composite $m \le N$ has a prime factor $\le \sqrt m$ and is crossed out by its smallest one. The number of crossings is $\sum_{p \le \sqrt N} (N - p^2)/p \approx N \ln \ln N$ by Mertens' theorem \cite{hardywright2008}.

```python run
import math
from ginsdk import numbertheory as nt
from ginsdk.cost import Cost

for N in (10**4, 10**5, 10**6):
    c = Cost()
    ps = nt.sieve(N, c)
    print(f"N = {N:>8}: {len(ps):6d} primes, {c['cross']:8d} crossings = {c['cross'] / (N * math.log(math.log(N))):.3f} x N ln ln N")
```

```output
N =    10000:   1229 primes,    16981 crossings = 0.765 x N ln ln N
N =   100000:   9592 primes,   193078 crossings = 0.790 x N ln ln N
N =  1000000:  78498 primes,  2122048 crossings = 0.808 x N ln ln N
```

The ratio is below $1$ and slowly rising: the approximation $N \ln \ln N$ omits lower-order terms that are still visible at $N = 10^6$ (\ledger{GIN-H-027}). A sieve answers every query up to $N$ in constant time after $\Oh(N \log \log N)$ preprocessing and $N$ bits of storage — exactly CGT's precomputation mechanism, with its usual price: the table is exponential in the number of digits of $N$.

## Fermat's test and its counterexamples {#sec:fermat-test}

Euler's theorem (Chapter 31) says that every prime $p$ satisfies $a^{p-1} \equiv 1 \pmod p$ for every $a$ coprime to $p$. The **Fermat test** to base $a$ checks this condition for a given $n$. A failure proves $n$ composite without finding a factor — $a$ is then a *Fermat witness*. Success proves nothing, and the converse of Euler's theorem is false (\ledger{GIN-PROP-043}):

::: theorem {#thm:korselt title="Korselt's criterion" status="classical" ledger="GIN-PROP-043"}
A composite $n$ satisfies $a^{n-1} \equiv 1 \pmod n$ for every $a$ coprime to $n$ if and only if $n$ is squarefree and $p - 1 \divides n - 1$ for every prime $p \divides n$. Such $n$ are **Carmichael numbers**; there are infinitely many \cite{korselt1899,agp1994}.
:::

::: proof
(Sufficiency.) If $n = p_1 \cdots p_k$ with distinct primes and $p_i - 1 \divides n - 1$, then for $a$ coprime to $n$, $a^{n-1} = (a^{p_i - 1})^{(n-1)/(p_i - 1)} \equiv 1 \pmod{p_i}$ for each $i$, hence modulo $n$ by the Chinese remainder theorem. (Necessity is proved with primitive roots modulo $p_i$ and $p_i^2$; see the cited sources.) The infinitude is the theorem of Alford, Granville and Pomerance.
:::

```python run
from ginsdk import numbertheory as nt

N = 10**5
psp = [n for n in range(3, N, 2) if not nt.is_prime(n) and nt.fermat_test(n, 2)]
carm = [n for n in range(3, N, 2) if nt.is_carmichael(n)]
print(f"base-2 Fermat pseudoprimes below {N}: {len(psp)}, the first: {psp[:6]}")
print(f"Carmichael numbers below {N}: {len(carm)}, the first: {carm[:6]}")
print("561 = 3 * 11 * 17 passes every coprime base:",
      all(pow(a, 560, 561) == 1 for a in range(2, 561) if all(a % p for p in (3, 11, 17))))
```

```output
base-2 Fermat pseudoprimes below 100000: 78, the first: [341, 561, 645, 1105, 1387, 1729]
Carmichael numbers below 100000: 16, the first: [561, 1105, 1729, 2465, 2821, 6601]
561 = 3 * 11 * 17 passes every coprime base: True
```

Below $10^6$ the book's experiment finds $245$ base-2 pseudoprimes and $43$ Carmichael numbers, the published values (\ledger{GIN-EXP-010}, \cite{psw1980}).

## Miller–Rabin: a stronger necessary condition {#sec:miller-rabin}

Write $n - 1 = 2^s d$ with $d$ odd. For a prime $p$ the only square roots of $1$ modulo $p$ are $\pm 1$, so the sequence $a^d, a^{2d}, \ldots, a^{2^s d} \equiv 1$ either starts at $1$ or reaches $-1$ before reaching $1$. A base $a$ for which this fails is a **strong witness** of compositeness; a composite $n$ for which $a$ is not a witness has $a$ as a **strong liar** \cite{miller1976,rabin1980}.

::: theorem {#thm:rabin title="At most a quarter of the bases lie" status="classical" ledger="GIN-HIST-019"}
For an odd composite $n > 9$, at most $\varphi(n)/4$ of the bases $1 \le a < n$ are strong liars; for $n = 9$ the two liars are $2/8$ of the bases \cite{rabin1980}.
:::

The theorem is about one fixed $n$ and a **base chosen at random**: if $k$ bases are chosen independently and uniformly, a composite $n$ survives all $k$ rounds with probability at most $4^{-k}$. It is *not* a statement that a random number which passes is prime with probability $1 - 4^{-k}$ — that probability depends on how the candidates were produced, and requires a separate argument. The census below checks the bound exhaustively for small $n$:

```python run
from ginsdk import numbertheory as nt

worst, worst_n, count = 0.0, None, 0
for n in range(9, 5001, 2):
    if nt.is_prime(n):
        continue
    liars = sum(1 for a in range(1, n) if nt.strong_probable_prime(n, a))
    count += 1
    if liars / (n - 1) > worst:
        worst, worst_n = liars / (n - 1), n
print(f"odd composites 9..5000 checked: {count}; largest fraction of strong liars: {worst:.4f} at n = {worst_n}")
print("strong base-2 pseudoprimes below 10^5:", [n for n in range(3, 10**5, 2) if not nt.is_prime(n) and nt.strong_probable_prime(n, 2)][:8], "...")
```

```output
odd composites 9..5000 checked: 1831; largest fraction of strong liars: 0.2500 at n = 9
strong base-2 pseudoprimes below 10^5: [2047, 3277, 4033, 4681, 8321, 15841, 29341, 42799] ...
```

The largest fraction of liars in the census is exactly $1/4$, attained at $n = 9$ — and, by \ref{thm:rabin}, nowhere else (\ledger{GIN-OBS-021}).

**Probabilistic and deterministic use.** With random bases, Miller–Rabin is a probabilistic algorithm whose error probability is bounded for every input. With a *fixed* list of bases it is deterministic, and it is correct below a bound found by exhaustive computation: the first $13$ prime bases suffice for all $n < 3\,317\,044\,064\,679\,887\,385\,961\,981$ \cite{sorenson2017}. That is how the SDK's `is_prime` works, and it agrees with the sieve on every $n \le 10^6$ (\ledger{GIN-EXP-010}). Above the bound the fixed-base test has no proved error bound at all — a fact that should be visible in any interface that offers it.

## Factoring baselines {#sec:factoring}

When a number is composite, a factor is the strongest possible answer. The SDK implements two baselines:

- **trial division** — at most about $\sqrt n / 2$ divisions by odd $d$, exponential in the number of digits;
- **Pollard's rho** — iterate $x \mapsto x^2 + c \bmod n$ and detect, with Floyd's cycle finding, two values congruent modulo an unknown prime factor $p$; heuristically about $\sqrt p$ steps \cite{pollard1975}.

```python run
import math
from ginsdk import numbertheory as nt
from ginsdk.cost import Cost

for p, q in ((1009, 1013), (104729, 1299709), (15485863, 32452843)):
    n = p * q
    c = Cost()
    d = nt.pollard_rho(n, 1, c)
    print(f"n = {n:16d}: rho found {d} after {c['step']:5d} steps (sqrt(min factor) = {math.isqrt(min(p, q)):5d})")
```

```output
n =          1022117: rho found 1013 after    17 steps (sqrt(min factor) =    31)
n =     136117223861: rho found 104729 after   278 steps (sqrt(min factor) =   323)
n =  502560280658509: rho found 32452843 after  3615 steps (sqrt(min factor) =  3935)
```

Both methods are exponential in the number of digits; rho replaces $\sqrt n$ by about $\sqrt p$ for the smallest prime factor $p$ (\ledger{GIN-OBS-012}). The asymptotically fastest known methods (the quadratic and number field sieves) are sub-exponential and are not implemented here. No polynomial-time classical factoring algorithm is known, and nothing in this book suggests one: the admissibility vocabulary describes *what* factoring asks, not how to answer it faster (Chapter 41).

::: exercise {#ex:prime-341}
Show that $341 = 11 \cdot 31$ passes the Fermat test to base $2$ but is not a Carmichael number, and find a base that exposes it.
:::

::: solution {of="ex:prime-341"}
$2^{10} = 1024 \equiv 1 \pmod{341}$ ($1024 = 3 \cdot 341 + 1$), so $2^{340} = (2^{10})^{34} \equiv 1$. Korselt fails: $31 - 1 = 30 \ndivides 340$. Base $3$: $3^{340} \equiv 56 \not\equiv 1 \pmod{341}$, so $3$ is a Fermat witness.
:::

::: exercise {#ex:prime-strong}
Show that $2$ is a strong witness for $341$ even though it is not a Fermat witness.
:::

::: solution {of="ex:prime-strong"}
$340 = 2^2 \cdot 85$. $2^{85} \equiv 32 \pmod{341}$ and $32^2 = 1024 \equiv 1$. The sequence $32, 1$ reaches $1$ from $32 \not\equiv -1$: a non-trivial square root of $1$, which a prime modulus cannot have.
:::

::: exercise {#ex:prime-prob}
A program draws random odd $512$-bit integers and outputs the first one passing $k = 20$ Miller–Rabin rounds with random bases. Explain why "the output is composite with probability at most $4^{-20}$" does not follow from \ref{thm:rabin} alone, and what additional fact is needed.
:::

::: summary
- Primality is a converse problem of multiplication; sieves precompute, trial division searches, tests check necessary conditions, factoring exhibits a solution.
- The sieve performs $\approx N \ln \ln N$ crossings (measured $0.77$–$0.81$ of that for $N = 10^4, 10^5, 10^6$).
- Fermat's test is fooled by pseudoprimes and by every Carmichael number (Korselt's criterion); published counts below $10^6$ are reproduced.
- Miller–Rabin: at most $1/4$ of bases lie for odd composite $n$ (census: maximum exactly $1/4$, at $n = 9$); the bound is a probability over random bases for a fixed $n$.
- With the first $13$ prime bases the test is deterministic below $\approx 3.3 \cdot 10^{24}$, and unproved above.
- Trial division and Pollard's rho are exponential baselines; no faster factoring is claimed.
:::
