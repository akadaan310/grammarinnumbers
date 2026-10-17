---
title: "Exponentiation: The Exponent's Numeral as a Program"
status: mixed
statusnote: Binary exponentiation, addition chains and their lower bound are classical; the reading of the exponent's numeral as a program and the domain-restriction counterexample are this book's presentation.
description: Square-and-multiply as the execution of the exponent's binary numeral; left-to-right and right-to-left variants; addition chains and their lower bound; modular exponentiation and its cost; and what exponents are — integers acting on a domain, not elements of it — with the counterexamples that follow.
epigraph: "To compute x¹⁰⁰⁰, read 1000 in binary and do what it says."
---

::: objectives
- Read left-to-right binary exponentiation as the execution of a program whose text is the exponent's binary numeral, and count its squarings and multiplications exactly.
- Compare left-to-right and right-to-left exponentiation, and relate both to addition chains.
- Prove that every addition chain for $n$ has at least $\lceil \log_2 n \rceil$ steps.
- State the bit cost of modular exponentiation.
- Explain why exponents are not elements of the domain, when they may be reduced, and what negative exponents require.
:::

## The exponent is a program {#sec:exp-program}

To compute $x^{13}$ one may multiply twelve times. Positional notation offers something better. The binary numeral of $13$ is `1101`. Read it left to right, starting from $x$ for the leading `1`; for each later digit **square** the accumulator, and if the digit is `1` also **multiply** by $x$:

$$x \xrightarrow{\ 1\ :\ \Sq\M\ } x^{3} \xrightarrow{\ 0\ :\ \Sq\ } x^{6} \xrightarrow{\ 1\ :\ \Sq\M\ } x^{13}.$$

The accumulator after reading a prefix $u$ of the numeral is $x^{\val_2(u)}$, because squaring doubles the exponent and multiplying adds one — the two moves of the binary digit grammar of Chapter 6, $e \mapsto 2e$ and $e \mapsto 2e + 1$, applied to the *exponent*. The numeral of the exponent is literally the program (\ledger{GIN-PROP-041}).

::: proposition {#prop:exp-count title="The cost of the exponent program" status="classical" ledger="GIN-PROP-041"}
Left-to-right binary exponentiation computes $x^e$ ($e \ge 1$) with exactly $\lfloor \log_2 e \rfloor$ squarings and $\popcount(e) - 1$ multiplications. Reading the move word back (each $\M$ or $\Sq\M$ as `1`, each $\Sq$ as `0`) recovers the binary numeral of $e$ \cite{knuth1997}.
:::

::: proof
The numeral of $e$ has $\lfloor \log_2 e \rfloor + 1$ digits; every digit after the first costs one squaring, and every `1` after the first costs one multiplication. The invariant "accumulator $= x^{\val_2(\text{prefix})}$" holds initially and is preserved by both moves, so at the end the accumulator is $x^e$. The move word is a letter-by-letter recoding of the digit word.
:::

```python run
from ginsdk import numbertheory as nt

value, rows = nt.powmod_trace(3, 13, 1000)
for bit, moves, acc in rows:
    print(f"digit {bit}: {moves:2s} -> accumulator {acc}")
print("3^13 mod 1000 =", value, "=", pow(3, 13, 1000), "  counts:", nt.powmod_count(13))
e = 1000
print(f"e = {e} = {bin(e)[2:]}:", nt.powmod_count(e), " instead of", e - 1, "multiplications")
```

```output
digit 1: M  -> accumulator 3
digit 1: SM -> accumulator 27
digit 0: S  -> accumulator 729
digit 1: SM -> accumulator 323
3^13 mod 1000 = 323 = 323   counts: {'square': 3, 'multiply': 2}
e = 1000 = 1111101000: {'square': 9, 'multiply': 5}  instead of 999 multiplications
```

The same correspondence appeared in Chapter 14 as a statement about unary numerals: the binary numeral of $n$ is a straight-line program for the unary word $a^n$, with doublings for squarings and appended letters for multiplications (\ledger{GIN-PROP-007}). Positional notation, repeated squaring and grammar compression are one object seen three ways.

## Right to left, and addition chains {#sec:addition-chains}

The digits can also be read from the least significant end: keep a running square $x, x^2, x^4, \ldots$ and multiply it into the result whenever the digit is `1`. The counts are the same — one squaring per digit after the first and one multiplication per further `1` — and the order of the operations differs. Right-to-left needs one extra register; left-to-right always multiplies by the *same* $x$, which matters when $x$ is small and the accumulator is large, and which makes "windowed" variants (precomputing $x^3, x^5, \ldots$ and reading several digits at a time) natural.

Both are special cases of an **addition chain** for $e$: a sequence $1 = a_0 < a_1 < \cdots < a_r = e$ in which every $a_i$ is the sum of two earlier terms (possibly equal). Each term is one multiplication of earlier powers, so a chain of length $r$ computes $x^e$ with $r$ multiplications. Binary exponentiation gives chains of length $\lfloor \log_2 e \rfloor + \popcount(e) - 1$; shorter chains often exist.

::: theorem {#thm:chain-lower title="The doubling lower bound for addition chains" status="classical" ledger="GIN-HIST-018"}
Every addition chain for $e$ has length at least $\lceil \log_2 e \rceil$. Hence binary exponentiation is optimal up to a factor of $2$, and optimal exactly when $e$ is a power of $2$ \cite{knuth1997}.
:::

::: proof
By induction $a_i \le 2^i$: true for $a_0 = 1$, and $a_i = a_j + a_k$ with $j, k < i$ gives $a_i \le 2 \cdot 2^{i-1}$. So $e = a_r \le 2^r$, i.e. $r \ge \log_2 e$. Binary uses at most $2\lfloor \log_2 e \rfloor$ steps, and exactly $\log_2 e$ when $e$ is a power of $2$.
:::

```python run
from itertools import count

def shortest_chain(e):
    # iterative deepening over star-free chains (any two earlier terms); fine for small e
    best = None
    def extend(chain, depth):
        nonlocal best
        if chain[-1] == e:
            best = list(chain); return True
        if depth == 0 or chain[-1] * 2 ** depth < e:
            return False
        sums = sorted({a + b for a in chain for b in chain if chain[-1] < a + b <= e}, reverse=True)
        return any(extend(chain + [s], depth - 1) for s in sums)
    for d in count(0):
        if extend([1], d):
            return best

for e in (15, 23, 31, 127):
    c = shortest_chain(e)
    binary = e.bit_length() - 1 + bin(e).count("1") - 1
    print(f"e = {e:3d}: shortest chain length {len(c) - 1} {c}   binary method {binary}")
```

```output
e =  15: shortest chain length 5 [1, 2, 4, 5, 10, 15]   binary method 6
e =  23: shortest chain length 6 [1, 2, 4, 5, 9, 18, 23]   binary method 7
e =  31: shortest chain length 7 [1, 2, 4, 8, 10, 20, 30, 31]   binary method 8
e = 127: shortest chain length 10 [1, 2, 4, 8, 16, 32, 40, 42, 84, 126, 127]   binary method 12
```

For $e = 15$ binary exponentiation uses $6$ multiplications, while the search finds the chain $1, 2, 4, 5, 10, 15$ of length $5$ (another is $1, 2, 3, 6, 12, 15$): reusing an intermediate power is better than following the digits. Finding a shortest chain is a hard search problem in general (the search above is exponential and only works for small exponents), and its relation to smallest grammars for unary strings was noted in Chapter 14 \cite{charikar2005}.

## Modular exponentiation and its cost {#sec:modexp}

Over the integers, $x^e$ has about $e \log_2 x$ bits: exponentiation is the first operation in this book whose *output* is exponentially larger than its input, and no algorithm can be faster than writing the output. Modulo $n$ every intermediate value stays below $n$, and the exponent program runs in about $2 \log_2 e$ multiplications of $L$-bit numbers followed by reductions.

::: proposition {#prop:modexp-cost title="Bit cost of modular exponentiation" status="classical" ledger="GIN-PROP-041"}
With schoolbook multiplication and division, computing $x^e \bmod n$ for $L$-bit $x, e, n$ costs $\Theta(L)$ multiplications and reductions of $\Theta(L^2)$ bit operations each: $\Theta(L^3)$ in total. With multiplication in time $M(L)$ it costs $\Oh(L \cdot M(L))$.
:::

The measured exponent for $L \le 512$ is about $2.9$ (\ledger{GIN-OBS-010}), approaching the predicted $3$ as the lower-order terms fade. This cost — cubic but polynomial — is what makes the Fermat and Miller–Rabin tests of Chapter 35 and the RSA and Diffie–Hellman systems practical; its *converse*, the discrete logarithm (Chapter 31), has no known polynomial algorithm.

## What an exponent is {#sec:exponent-type}

In $a + b$ and $a \cdot b$ both arguments come from the same domain. In $a^k$ they do not. Repeated multiplication defines $a^k$ for a natural number $k$ and an element $a$ of any monoid; negative $k$ makes sense exactly when $a$ has an inverse. The exponent is an integer **acting on** the domain, not an element of it — and an evaluator that forgets this computes nonsense. The first evaluator written for this book did: it evaluated $0^{-1}$ in $\Z/6$ by reducing $-1$ to the residue $5$ and returning $0^5 = 0$ (\ledger{GIN-NEG-013}).

```python run
from ginsdk import evaluate

for e, d in [("0^-1", "Z/6"), ("3^-1", "Z/7"), ("2^-1", "Z/6"), ("2^0.5", "Q"), ("(2/3)^-2", "Q"), ("0^0", "Q")]:
    o = evaluate(e, d)
    print(f"{e:9s} in {d:4s}: {o.status:13s} {o.display or o.reason}")
```

```output
0^-1      in Z/6 : no-solution   0^-1 needs the inverse of 0 mod 6: gcd(0, 6) = 6 does not divide 1
3^-1      in Z/7 : value         5
2^-1      in Z/6 : no-solution   2^-1 needs the inverse of 2 mod 6: gcd(2, 6) = 2 does not divide 1
2^0.5     in Q   : not-in-domain in the exponent: the literal 0.5 denotes 1/2, which is not in Z
(2/3)^-2  in Q   : value         9/4
0^0       in Q   : value         1
```

Exponents *can* sometimes be reduced — but modulo the order of the base, not modulo the modulus. For a unit $a$ modulo $n$, Euler's theorem gives $a^{e} \equiv a^{e \bmod \varphi(n)}$. For a non-unit the reduction is false:

::: counterexample {#cex:exp-reduce title="Reducing an exponent modulo φ(n) without a unit" status="counterexample" ledger="GIN-NEG-024"}
Modulo $n = 4$, $\varphi(4) = 2$, but $2^{3} \equiv 0$ while $2^{3 \bmod 2} = 2^1 = 2$. The rule $a^e \equiv a^{e \bmod \varphi(n)}$ requires $\gcd(a, n) = 1$.
:::

```python run
from math import gcd
from ginsdk import numbertheory as nt

bad = [(a, e, n) for n in range(2, 40) for a in range(n) for e in range(1, 3 * n)
       if pow(a, e, n) != pow(a, e % nt.phi(n), n)]
units_ok = all(pow(a, e, n) == pow(a, e % nt.phi(n), n)
               for n in range(2, 40) for a in range(n) if gcd(a, n) == 1 for e in range(1, 3 * n))
print("violations of a^e ≡ a^(e mod φ(n)) for n < 40:", len(bad), " all with gcd(a, n) > 1:", all(gcd(a, n) > 1 for a, e, n in bad))
print("the rule holds for every unit tested:", units_ok, "  first violation:", bad[0])
```

```output
violations of a^e ≡ a^(e mod φ(n)) for n < 40: 2665  all with gcd(a, n) > 1: True
the rule holds for every unit tested: True   first violation: (0, 1, 2)
```

Every violation found involves a non-unit, and the rule holds for every unit, as Euler's theorem says. The pattern is the one Chapter 9 called *typing*: the expression `a ^ e` is well formed, but the rewrite "reduce $e$ modulo $\varphi(n)$" is admissible only under a hypothesis about $a$, and a system that applies it unconditionally changes the meaning of programs.

::: exercise {#ex:exp-word}
Write the exponent program for $e = 45$, and compute $2^{45} \bmod 1000$ by hand with it.
:::

::: solution {of="ex:exp-word"}
$45 = $ `101101`; after the leading digit the program is S, SM, SM, S, SM. Accumulators mod $1000$: $2$; $4$; $4^2 \cdot 2 = 32$; $32^2 \cdot 2 = 2048 \to 48$; $48^2 = 2304 \to 304$; $304^2 \cdot 2 = 184832 \to 832$. So $2^{45} \equiv 832 \pmod{1000}$; indeed $2^{45} = 35184372088832$. Five squarings and three multiplications, as \ref{prop:exp-count} predicts ($\popcount(45) = 4$).
:::

::: exercise {#ex:exp-rtl}
Show that right-to-left binary exponentiation also uses $\lfloor \log_2 e \rfloor$ squarings and $\popcount(e) - 1$ multiplications, if multiplications by the initial value $1$ are not counted.
:::

::: exercise {#ex:exp-chain}
Find an addition chain for $e = 63$ shorter than the binary method's, and explain why every chain for $e = 2^k$ of length $k$ must consist of doublings.
:::

::: solution {of="ex:exp-chain"}
Binary uses $5 + 5 = 10$; the chain $1, 2, 3, 6, 12, 24, 48, 60, 63$ uses $8$ (and $1, 2, 4, 8, 16, 32, 64$ cannot be used since chains must end exactly at $e$ without subtraction). For $e = 2^k$ and length $k$, the bound $a_i \le 2^i$ must be tight at every step, so every step doubles the previous term.
:::

::: summary
- Left-to-right binary exponentiation executes the exponent's binary numeral: $\lfloor \log_2 e \rfloor$ squarings, $\popcount(e) - 1$ multiplications, and the move word recovers the numeral.
- Exponentiation methods are addition chains; every chain has length $\ge \lceil \log_2 e \rceil$, so binary is optimal within a factor $2$ and shorter chains exist (e.g. $5$ instead of $6$ steps for $e = 15$).
- Modular exponentiation costs $\Theta(L^3)$ bit operations with schoolbook arithmetic (measured slope $\approx 2.9$ at small $L$); its converse, the discrete logarithm, is believed hard.
- Exponents are integers acting on a domain: negative exponents need inverses, and reduction modulo $\varphi(n)$ is valid only for units (counterexample $2^3 \bmod 4$).
:::
