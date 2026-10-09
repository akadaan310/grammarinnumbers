---
title: "Floating Point: Rounding, Special Data, and Flags"
status: mixed
statusnote: IEEE 754 is a standard and its consequences are classical; the reference simulator, its bit-for-bit and flag-for-flag agreement with hardware, and the tininess measurements are this book's.
description: IEEE 754 binary formats as encodings of a finite set of dyadic rationals; correct rounding as exact computation followed by one rounding; the special data ±∞, NaN and −0 and the five exception flags; which integers and which decimals a format can hold; the algebraic laws that fail; a reference simulator checked against hardware on 80,600 operations, including flags; and how different processors detect underflow.
epigraph: "A floating-point number is an exact rational. What is inexact is the arithmetic: every operation is followed by one rounding."
---

::: objectives
- Describe a binary floating-point format as a finite set of dyadic rationals plus special data, and decode a bit pattern exactly.
- State the IEEE 754 requirement of correct rounding and implement it as exact rational computation followed by a single rounding.
- Name the five exception flags and the operations that raise each.
- Prove which integers and which decimal fractions a binary format represents exactly.
- List the algebraic laws that floating-point arithmetic keeps and those it breaks, with counterexamples.
- Interpret the agreement of the SDK's simulator with hardware, and the differences in tininess detection between architectures.
:::

## Formats as finite sets of rationals {#sec:formats}

::: definition {#def:ieee-format title="IEEE binary format" status="definition" ledger="GIN-DEF-030"}
A binary format has a precision $p$ (significand bits, including the implicit leading bit) and $e$ exponent bits, with $e_{\max} = 2^{e-1} - 1$ and $e_{\min} = 1 - e_{\max}$. Its finite data are $\pm m \cdot 2^{q}$ with integers $0 \le m < 2^p$ and $q \ge e_{\min} - p + 1$ (subject to the range), together with $\pm\infty$ and NaN \cite{ieee754}. binary16: $p = 11$, $e = 5$; binary32: $p = 24$, $e = 8$; binary64: $p = 53$, $e = 11$.
:::

Every finite floating-point number is therefore an **exact dyadic rational**: an integer times a power of two. Nothing about a floating-point number is approximate. The number stored for the literal `0.1` in binary64 is
$$
\frac{3602879701896397}{36028797018963968} = 0.1000000000000000055511151231257827021181583404541015625,
$$
exactly. What is approximate is the relation between the literal and the stored number — the literal was *rounded* when it was read — and every later arithmetic operation, which rounds again.

```python run
from ginsdk import ieee

for fmt in (ieee.BINARY16, ieee.BINARY32, ieee.BINARY64):
    x, flags = ieee.from_decimal("0.1", fmt)
    v = x.value()
    print(f"{fmt.name:9s} 0.1 is stored as {v.numerator}/{v.denominator}  ({sorted(flags)})  fields {x.fields()}")
```

```output
binary16  0.1 is stored as 819/8192  (['inexact'])  fields {'sign': '0', 'exponent': '01011', 'fraction': '1001100110'}
binary32  0.1 is stored as 13421773/134217728  (['inexact'])  fields {'sign': '0', 'exponent': '01111011', 'fraction': '10011001100110011001101'}
binary64  0.1 is stored as 3602879701896397/36028797018963968  (['inexact'])  fields {'sign': '0', 'exponent': '01111111011', 'fraction': '1001100110011001100110011001100110011001100110011010'}
```

Each stored value is a fraction whose denominator is a power of two; the more precise the format, the larger the denominator and the smaller the distance to $1/10$ — but the distance is never zero, because $1/10$ is not a dyadic rational (Chapter 7).

## Correct rounding {#sec:rounding}

::: definition {#def:correct-rounding title="Correct rounding" status="definition" ledger="GIN-DEF-031"}
An operation is **correctly rounded** if its result is the exact real result rounded once to the format — in the default mode, to the nearest representable number, with ties broken to the one with even significand. IEEE 754 requires correct rounding of $+$, $-$, $\times$, $\div$, $\sqrt{\ }$ and fused multiply–add.
:::

The definition is also an algorithm, and the SDK's reference simulator `ginsdk.ieee` implements it literally: decode both operands to exact rationals, compute the exact result with Python's `fractions`, and round once. That is slow and obviously correct, which is what a reference implementation should be. Its value lies in being checkable against hardware.

::: implementation {#imp:ieee-sim title="The IEEE simulator agrees with this CPU, results and flags" status="implementation" ledger="GIN-IMP-001"}
On the session's x86-64 host (SSE scalar arithmetic, gcc 13.3, flags read with `fenv.h`), `ginsdk.ieee` reproduces the hardware's results bit for bit (NaNs compared as NaNs) and all five exception flags on 40,300 binary32 and 40,300 binary64 operations ($+, -, \times, \div, \sqrt{\ }$ on random bit patterns, special values, subnormals, and a targeted family near the underflow threshold) — after signaling NaNs were modelled (\ledger{GIN-REJ-002}).
:::

The parenthesis records a correction. The first run of the experiment found 101 flag mismatches; every one involved a *signaling* NaN operand, on which hardware raises the invalid flag and the first version of the simulator did not. The simulator was fixed and the experiment re-run (\ledger{GIN-EXP-005}). The failed run is kept in the ledger: it is evidence that the experiment can find defects in the instrument.

## Special data and flags {#sec:flags}

::: definition {#def:flags title="Exception flags" status="definition" ledger="GIN-DEF-032"}
**invalid**: no useful real result ($0/0$, $\infty - \infty$, $0 \times \infty$, $\sqrt{\text{negative}}$, operations on signaling NaNs); **divideByZero**: an exact infinite result from finite operands ($x / 0$, $x \ne 0$ finite); **overflow**: the rounded result exceeds the largest finite number; **underflow**: the result is tiny (below the smallest normal number) and inexact, under default handling; **inexact**: the rounded result differs from the exact one.
:::

The flags are *sticky*: they accumulate until cleared, so a program can perform a long computation and then ask whether anything exceptional happened. Most high-level languages give no access to them; C exposes them through `fenv.h`. The measured behaviour on x86-64 for the divisions of this book:

| operation | result | flags |
|---|---|---|
| $1/0$ | $+\infty$ | divideByZero |
| $-1/0$, $1/(-0)$ | $-\infty$ | divideByZero |
| $0/0$ | NaN (printed `-nan`: the x86 default NaN has its sign bit set) | invalid |
| $0/1$ | $0$ | none |
| $1/3$ | $0.333\ldots$ | inexact |
| $10^{308}/10^{-10}$ | $+\infty$ | overflow, inexact |
| $10^{-310}/10^{10}$ | a subnormal number | underflow, inexact |
| $\sqrt{-1}$ | NaN | invalid |

Every row was also produced by the simulator, and Java, Go, Rust, JavaScript and C return the same data. Python, alone among the languages measured, raises `ZeroDivisionError` for `1.0 / 0.0`: it checks the divisor before invoking the IEEE operation (\ledger{GIN-NEG-010}).

## What a format can hold {#sec:representable}

::: proposition {#prop:least-int title="The least unrepresentable positive integer" status="classical" ledger="GIN-PROP-030"}
In a binary format with precision $p$ and $e_{\max} \ge p$, every integer $0, 1, \ldots, 2^p$ is representable and $2^p + 1$ is not.
:::

::: proof
An integer $m < 2^p$ is $m \cdot 2^0$ with a significand below $2^p$; $2^p = 2^{p-1} \cdot 2$. The binary numeral of $2^p + 1$ is $1\,0\cdots0\,1$ with $p + 1$ significant digits, more than $p$.
:::

So $2^{24} + 1 = 16777217$ is the first integer a binary32 number cannot hold, and $2^{53} + 1 = 9007199254740993$ the first for binary64 — and therefore for JavaScript's only number type. Above $2^{53}$, a JavaScript number cannot count by ones: $2^{53} + 1 = 2^{53}$.

::: proposition {#prop:decimals title="Which decimals are binary floating-point numbers" status="proved-here" ledger="GIN-PROP-031"}
A $k$-digit decimal fraction $d/10^k$ ($1 \le d < 10^k$) is exactly representable in a binary format with $p \ge k$ and sufficient exponent range if and only if $5^k \mid d$. Exactly $2^k - 1$ of the $10^k - 1$ such fractions are representable.
:::

::: proof
In lowest terms the denominator of $d/10^k$ is $2^i 5^j$; a binary fraction needs $j = 0$, i.e. $5^k \mid d$. Then $d/10^k = m / 2^k$ with $m = d / 5^k < 2^k \le 2^p$. The multiples of $5^k$ below $10^k = 2^k 5^k$ number $2^k - 1$.
:::

Of the 99 two-digit decimals $0.01, \ldots, 0.99$, exactly three — $0.25$, $0.5$, $0.75$ — are binary64 numbers. Of the 999 three-digit ones, seven. The decimal fractions people type are almost never the numbers a binary computer stores.

## Laws that hold, laws that fail {#sec:fp-laws}

Correct rounding guarantees that each single operation is as accurate as the format allows. It does not make floating-point arithmetic a field.

| law | holds? | reason or counterexample (binary64 unless stated) |
|---|---|---|
| $x \oplus y = y \oplus x$, $x \otimes y = y \otimes x$ | yes (non-NaN) | rounding of a commutative exact result |
| $(x \oplus y) \oplus z = x \oplus (y \oplus z)$ | no | $(0.1 + 0.1) + 0.4 = 0.6000000000000001 \ne 0.6$ (\ledger{GIN-PROP-032}) |
| $x \otimes (y \oplus z) = x \otimes y \oplus x \otimes z$ | no | $0.1 \cdot (0.1 + 0.3) \ne 0.1 \cdot 0.1 + 0.1 \cdot 0.3$ (Chapter 14) |
| $x \oplus 0 = x$ | yes, except $-0 \oplus +0 = +0$ | signed zeros |
| $x \oplus 1 > x$ | no | $2^{53} + 1 = 2^{53}$ |
| $x = y \Rightarrow 1/x = 1/y$ | no | $+0 = -0$ but $1/(+0) \ne 1/(-0)$ |
| $x = x$ | no | $\NaN \ne \NaN$ |
| $y \otimes (x \oslash y) = x$ | no | fails at $y = 0$ and through rounding; see the census of Chapter 18 |

::: observation {#obs:harmonic title="Summation order changes a sum" status="empirical" ledger="GIN-OBS-015"}
The harmonic sum $H_{20000}$ computed in binary32 is $10.480757$ summing forward ($1 + \tfrac12 + \cdots$) and $10.480734$ summing backward; the correctly rounded exact value is $10.480728$. The backward sum, which adds small terms first, has an error about five times smaller (GIN-EXP-012).
:::

## Tininess: one standard, two readings {#sec:tininess}

IEEE 754 allows an implementation to decide that a result is *tiny* — below the smallest normal number — either **before** or **after** rounding. The two readings differ only for results whose exact value lies just below the smallest normal number and rounds up to it: before-rounding detection calls them tiny (and raises underflow if inexact); after-rounding detection does not. The simulator implements both, which turns the question "which does this processor do?" into an experiment.

::: observation {#obs:tininess title="Tininess detection on three architectures" status="empirical" ledger="GIN-OBS-009"}
On the x86-64 host, in a targeted family of 300 products near the threshold, the after-rounding model matches every hardware underflow flag and the before-rounding model mismatches 158 (binary32) and 159 (binary64): this processor detects tininess **after rounding** (GIN-EXP-005). Under QEMU emulation, a single discriminating product shows AArch64 detecting **before rounding** and RISC-V **after rounding** (\ledger{GIN-OBS-018}, GIN-EXP-014; emulator, not hardware).
:::

```python run
from fractions import Fraction
from ginsdk import ieee

F = ieee.BINARY32
a = ieee.from_bits(F, 0x3F7FFFFE)        # 1 - 2^-23
b = ieee.from_bits(F, 0x00800001)        # 2^-126 (1 + 2^-23)
exact = a.value() * b.value()
print("exact product / smallest normal =", exact / F.min_normal, " (just below 1)")
for mode in ("after", "before"):
    r, flags = ieee.mul(a, b, tininess=mode)
    print(f"tininess {mode:6s}: result {hex(r.bits())}  flags {sorted(flags)}")
```

```output
exact product / smallest normal = 70368744177663/70368744177664  (just below 1)
tininess after : result 0x800000  flags ['inexact']
tininess before: result 0x800000  flags ['inexact', 'underflow']
```

The result bits are identical; only the flag differs. A program that tests the underflow flag will behave differently on x86-64 and on (emulated) AArch64 for exactly these inputs — a portability difference permitted by the standard itself.

::: exercise {#ex:fp-decode}
Decode the binary32 pattern `0x40490FDB` by hand into sign, exponent and significand, and give its exact value.
:::

::: solution {of="ex:fp-decode"}
Bits `0 10000000 10010010000111111011011`: sign $+$, biased exponent $128$, so $e = 1$; significand $1.10010010000111111011011_2 = 13176795/2^{23}$. Value $13176795/2^{22} \approx 3.14159274$ (Chapter 2).
:::

::: exercise {#ex:fp-integers}
What is the largest integer $N$ such that every integer in $[-N, N]$ is exactly representable in binary16? What does `2049` round to?
:::

::: solution {of="ex:fp-integers"}
$N = 2^{11} = 2048$. $2049$ is halfway between $2048$ and $2050$; ties go to the even significand, $2048$ ($1.0000000000 \times 2^{11}$).
:::

::: exercise {#ex:fp-decimals}
List the four-digit decimals in $(0, 1)$ that are binary64 numbers.
:::

::: solution {of="ex:fp-decimals"}
$d/10^4$ with $625 \mid d$: $0.0625, 0.125, 0.1875, \ldots, 0.9375$ — the fifteen multiples of $1/16$, as Proposition \ref{prop:decimals} predicts ($2^4 - 1 = 15$).
:::

::: summary
- Floating-point numbers are exact dyadic rationals; inexactness lies in rounding, which happens at reading and after every operation.
- Correct rounding = exact computation + one rounding; the SDK's simulator does exactly that and matches x86-64 hardware on 80,600 operations, flags included.
- ±∞, NaN and −0 are special data; five sticky flags record invalid, divideByZero, overflow, underflow and inexact events.
- binary64 holds every integer up to $2^{53}$ and only $2^k - 1$ of the $k$-digit decimals.
- Commutativity survives; associativity, distributivity, reflexivity of equality and the converse reading of division do not.
- Tininess detection differs: after rounding on x86-64, before rounding on emulated AArch64.
:::
