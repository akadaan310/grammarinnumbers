---
title: "Algorithms for Multiplication"
status: mixed
statusnote: The algorithms and their bounds are classical; the circuit sizes and counted limb operations are measured on this book's implementations.
description: Long multiplication and its invariant; binary shift-and-add and the array multiplier circuit; Karatsuba's three-for-four trick derived from distributivity, with measured exponents; the road to O(n log n); and what is and is not known about the cost of multiplying.
epigraph: "Four products of halves give the product of wholes. Karatsuba noticed that three are enough — and the exponent of multiplication fell for the first time in four thousand years."
---

::: objectives
- Analyse long multiplication: its invariant, its $\Theta(n^2)$ digit operations, and its gate-level form, the array multiplier.
- Derive Karatsuba's algorithm from distributivity and solve its recurrence.
- Read measured operation counts and log–log slopes, and relate them to the theoretical exponents.
- State what is known about the complexity of integer multiplication, separating proved upper bounds from conjectured lower bounds.
:::

## Long multiplication {#sec:long-mul}

To multiply an $n$-digit numeral $a$ by an $m$-digit numeral $b$, long multiplication forms the partial products $a \cdot b_j$ (one digit of $b$ at a time), shifts the $j$-th by $j$ places, and adds them. The algorithm is distributivity applied to the positional expansion of $b$:
$$
a \cdot b = a \cdot \sum_{j} b_j\, \beta^j = \sum_j (a \cdot b_j)\, \beta^j ,
$$
where $\beta$ is the base. In the usual organization each digit product $a_i b_j$ is formed once and added into position $i + j$ with carries. Its invariant after processing digit $j$ of $b$ is that the accumulator equals $a \cdot \sum_{k \le j} b_k \beta^k$. It performs $nm$ digit multiplications and about as many additions: $\Theta(nm)$ digit operations, $\Theta(n^2)$ for equal lengths.

In binary, each digit $b_j$ is $0$ or $1$, so each partial product is either $0$ or $a$ itself: **shift and add**. As a circuit, every product bit $a_i b_j$ is one AND gate, and the shifted partial products are summed by rows of adders — the **array multiplier**.

::: implementation {#imp:array-mul title="The array multiplier: size and depth" status="implementation" ledger="GIN-IMP-006"}
The $n \times n \to 2n$-bit array multiplier of `ginsdk.circuits` (AND partial products summed by ripple-carry rows) has exactly $6n^2 - 8n$ gates and depth $6n - 8$ for $n = 3, \ldots, 32$ (for $n = 2$: $8$ gates, depth $3$), and computes the product correctly for all inputs with $n \le 6$.
:::

```python run
from ginsdk import circuits as K

for n in (4, 8, 16, 32):
    c = K.array_multiplier(n)
    print(f"n = {n:2d}: {c.size:5d} gates (6n²-8n = {6*n*n - 8*n:5d}), depth {c.depth():3d} (6n-8 = {6*n - 8})")
n, bad = 5, 0
c = K.array_multiplier(n)
for x in range(2 ** n):
    for y in range(2 ** n):
        out = K.apply_words(c, a=(x, n), b=(y, n))
        bad += sum(bit << i for i, bit in enumerate(out)) != x * y
print(f"exhaustive check, n = {n}: {bad} errors in {4 ** n} products")
```

```output
n =  4:    64 gates (6n²-8n =    64), depth  16 (6n-8 = 16)
n =  8:   320 gates (6n²-8n =   320), depth  40 (6n-8 = 40)
n = 16:  1408 gates (6n²-8n =  1408), depth  88 (6n-8 = 88)
n = 32:  5888 gates (6n²-8n =  5888), depth 184 (6n-8 = 184)
exhaustive check, n = 5: 0 errors in 1024 products
```

The quadratic size is unavoidable for this design: it forms all $n^2$ bit products explicitly. Real multipliers reduce the *depth* — not the size — by summing partial products with trees of carry-save adders (Wallace and Dadda trees), which use the redundant representations of Chapter 6 to postpone carry propagation until a single final addition. Depth then falls to $\Oh(\log n)$; size stays $\Theta(n^2)$.

## Karatsuba: three products instead of four {#sec:karatsuba}

For a long time it was assumed that multiplying $n$-digit numbers needs about $n^2$ digit operations. In 1960 Karatsuba found otherwise \cite{karatsuba1962}. Split each operand in half, $a = a_1 \beta^{k} + a_0$ and $b = b_1 \beta^{k} + b_0$. Distributivity gives
$$
a b = a_1 b_1\, \beta^{2k} + (a_1 b_0 + a_0 b_1)\, \beta^{k} + a_0 b_0,
$$
four half-size products. But the middle coefficient can be obtained from *one* further product:
$$
a_1 b_0 + a_0 b_1 = (a_1 + a_0)(b_1 + b_0) - a_1 b_1 - a_0 b_0 . \label{eq:karatsuba}
$$
So three half-size products, and a constant number of additions, suffice.

::: proposition {#prop:karatsuba title="Karatsuba's bound" status="classical" ledger="GIN-PROP-063"}
Karatsuba multiplication of two $n$-digit numbers uses $\Theta(n^{\log_2 3}) \approx \Theta(n^{1.585})$ digit operations.
:::

::: proof
The cost satisfies $T(n) = 3\,T(n/2) + \Theta(n)$ (three recursive products of half size, plus additions and shifts of linear cost; the sums $a_1 + a_0$ may have one extra digit, which does not change the asymptotics). Unfolding $\log_2 n$ levels gives $3^{\log_2 n} = n^{\log_2 3}$ leaf multiplications and a geometric sum of linear work dominated by the last level.
:::

The algorithm is the clearest example in this book of a gain obtained *from algebra alone*: identity \eqref{eq:karatsuba} is a rearrangement of the distributive law, and it changes the exponent of the cost. The SDK counts the 32-bit limb operations of both algorithms on random operands:

::: observation {#obs:karatsuba title="Measured exponents of schoolbook and Karatsuba multiplication" status="empirical" ledger="GIN-OBS-010"}
Counted 32-bit limb operations (GIN-EXP-008), random operands, Karatsuba threshold 16 limbs:

| bits | schoolbook limb products | Karatsuba limb products |
|---|---|---|
| 1,024 | 2,048 | 1,796 |
| 4,096 | 32,768 | 18,409 |
| 16,384 | 524,288 | 172,598 |

The log–log slope of the Karatsuba counts between successive sizes falls from $2.0$ (below the threshold) to $1.604$ at 16,384 bits, approaching $\log_2 3 \approx 1.585$; schoolbook stays at $2.0$. At 16,384 bits Karatsuba uses $3.04$ times fewer limb operations.
:::

The threshold matters. Below about sixteen limbs, the additions of Karatsuba cost more than the product they save, and every practical library — GMP, the multiplication inside CPython's `int` — switches between algorithms at tuned thresholds \cite{brentzimmermann2010}.

## Toward $\Oh(n \log n)$ {#sec:fft}

Karatsuba's idea generalizes. Splitting into three parts and evaluating at five points gives Toom–Cook multiplication, with exponent $\log_3 5 \approx 1.465$; more parts give exponents approaching $1$. The decisive step treats the digits of a number as the coefficients of a polynomial, multiplies the polynomials by evaluating them at roots of unity with the fast Fourier transform, and carries at the end. Schönhage and Strassen's algorithm of 1971 achieved $\Oh(n \log n \log\log n)$; after a sequence of improvements, Harvey and van der Hoeven proved in 2021 that $n$-bit integers can be multiplied in $\Oh(n \log n)$ bit operations \cite{harvey2021,knuth1997,brentzimmermann2010}.

What is *not* known is a matching lower bound. No proof shows that multiplication requires more than linear time in general models of computation; the $\Oh(n \log n)$ bound is conjectured to be optimal, and is known to be optimal only under additional assumptions. In the summary table of costs (Chapter 36) the entry for multiplication therefore has a proved upper bound and an open lower bound — unlike addition, whose $\Theta(n)$ is settled (\ledger{GIN-PROP-058}).

| algorithm | digit-operation count | in practice |
|---|---|---|
| repeated addition | $\Theta(\beta^n \cdot n)$ — exponential | never |
| long multiplication | $\Theta(n^2)$ | small operands |
| Karatsuba | $\Theta(n^{1.585})$ | from tens of machine words |
| Toom–Cook 3-way | $\Theta(n^{1.465})$ | hundreds of words |
| FFT-based (Schönhage–Strassen) | $\Oh(n \log n \log\log n)$ | thousands of words and up |
| Harvey–van der Hoeven | $\Oh(n \log n)$ | a theoretical result; the constant is astronomically large |

## Multiplication in machines {#sec:mul-machine}

A processor's multiply instruction computes a product of two words in a few cycles with a dedicated tree multiplier; on 64-bit machines it typically produces either the low 64 bits (enough for wraparound arithmetic) or the full 128-bit product split over two registers. Wraparound multiplication is multiplication in $\Z/2^{64}$, a ring, so all ring laws hold for it — including the ones that make overflow invisible: $2^{32} \cdot 2^{32} = 0$ in 64-bit unsigned arithmetic. Multiplication is where overflow happens soonest: the product of two $w$-bit numbers needs up to $2w$ bits, so even moderately sized operands overflow a word. Arbitrary-precision libraries exist largely because of this.

::: exercise {#ex:ma-karatsuba}
Multiply $47 \times 83$ by Karatsuba's method with $\beta = 10$, $k = 1$, showing the three products.
:::

::: solution {of="ex:ma-karatsuba"}
$a_1 = 4, a_0 = 7, b_1 = 8, b_0 = 3$. $z_2 = 4 \cdot 8 = 32$; $z_0 = 7 \cdot 3 = 21$; $(4 + 7)(8 + 3) = 121$, so the middle coefficient is $121 - 32 - 21 = 68$. Product $= 3200 + 680 + 21 = 3901$. ✓
:::

::: exercise {#ex:ma-recurrence}
Solve $T(n) = 4T(n/2) + n$ and $T(n) = 3T(n/2) + n$ for $n$ a power of two with $T(1) = 1$, exactly.
:::

::: solution {of="ex:ma-recurrence"}
$T(n) = 4T(n/2) + n$: $T(n) = 2n^2 - n$. $T(n) = 3T(n/2) + n$: $T(n) = 3n^{\log_2 3} - 2n$. (Check $n = 2$: $4 + 2 = 6 = 8 - 2$ and $3 + 2 = 5 = 9 - 4$.)
:::

::: exercise {#ex:ma-wrap}
Show that in $\Z/2^{64}$ the product of two non-zero elements can be zero, and find all pairs of powers of two with that property.
:::

::: solution {of="ex:ma-wrap"}
$2^i \cdot 2^j = 2^{i + j} \equiv 0 \pmod{2^{64}}$ iff $i + j \ge 64$, for $0 \le i, j \le 63$. Example: $2^{32} \cdot 2^{32} = 0$. So $\Z/2^{64}$ has zero divisors; it is a ring but not an integral domain — which matters for division (Chapter 16).
:::

::: summary
- Long multiplication is distributivity over digits: $\Theta(n^2)$; its circuit form, the array multiplier, has $6n^2 - 8n$ gates in this book's construction.
- Karatsuba rearranges distributivity to use three half-size products: $\Theta(n^{\log_2 3})$; measured slopes approach $1.585$.
- FFT methods reach $\Oh(n \log n)$ (Harvey–van der Hoeven 2021); no superlinear lower bound is known.
- Machine multiplication is multiplication in $\Z/2^w$: a ring with zero divisors, where overflow is silent.
:::
