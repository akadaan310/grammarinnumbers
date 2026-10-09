---
title: "Overflow, Checked Arithmetic, and Arbitrary Precision"
status: mixed
statusnote: The policies and libraries described are standard; the measurements are this book's.
description: What happens when an exact result leaves the representable range — wraparound, saturation, traps, exceptions, undefined behaviour — and how languages let programmers choose; arbitrary-precision integers, their costs and the limits runtimes impose on them; and exact alternatives to binary floating point for decimal quantities.
epigraph: "Every fixed-width number system has an edge. The only choices are what happens there, and whether anyone is told."
---

::: objectives
- Tabulate the result of $\mathrm{MAX} + 1$ under each overflow policy at widths 8, 16, 32 and 64.
- Use checked, wrapping, saturating and overflowing operations deliberately, and know which languages provide them.
- Explain the cost model of arbitrary-precision integers, and why a runtime may refuse an operation that is mathematically trivial.
- Choose an exact representation for decimal quantities such as money.
:::

## The edge of a fixed width {#sec:edge}

An overflow is not a failure of arithmetic. The exact result exists and is unique; it is merely not an element of the set of representable values. In the four-layer model it is an *execution-layer* failure with a typing flavour: the operation is admissible, the result is not in the domain of the encoding. Each system decides what to do at the edge.

```python run
import json, pathlib, ginsdk
rows = json.loads((pathlib.Path(ginsdk.__file__).parents[3] / "experiments/results/exp012.json").read_text())["data"]["max_plus_one"]
print(f"{'width':>5s} {'MAX':>20s} {'wrap':>21s} {'saturate':>20s}  C           checked")
for r in rows:
    print(f"{r['width']:>5d} {r['MAX']:>20d} {r['wrap']:>21d} {r['saturate']:>20d}  {r['C']:11s} {r['checked']}")
```

```output
width                  MAX                  wrap             saturate  C           checked
    8                  127                  -128                  127  undefined   exception
   16                32767                -32768                32767  undefined   exception
   32           2147483647           -2147483648           2147483647  undefined   exception
   64  9223372036854775807  -9223372036854775808  9223372036854775807  undefined   exception
```

Wraparound sends $\mathrm{MAX} + 1$ to $\mathrm{MIN}$, the step across the seam of the cycle of Chapter 3 (\ledger{GIN-PROP-052}). Saturation clamps. Checked arithmetic refuses. ISO C declares signed overflow undefined — with the consequences for optimization described in Chapter 23 — while unsigned overflow in C is defined to wrap.

## Choosing the policy explicitly {#sec:explicit}

Because no single policy is right for every program, several languages let the programmer choose per operation.

| language | wrap | saturate | check | detect |
|---|---|---|---|---|
| Rust | `wrapping_add` | `saturating_add` | `checked_add` → `Option` | `overflowing_add` → (value, flag) |
| C (GCC, Clang extensions) | unsigned types | — | — | `__builtin_add_overflow` |
| C23 | unsigned types | — | — | `ckd_add` in `<stdckdint.h>` |
| Java | default for `int` | — | `Math.addExact` throws | — |
| Go | default | — | — | `math/bits.Add64` returns the carry |
| Swift | `&+` | — | default `+` traps | `addingReportingOverflow` |

Rust's design is the most explicit: the default `+` panics on overflow in debug builds and wraps in release builds — so the *same source* has two meanings depending on a compiler flag — and the four named methods make the intended policy part of the program text. In the vocabulary of this book, the methods name the repair: `wrapping_add` is the *quotient* repair, `saturating_add` a *totalization*, `checked_add` *absorption* into `Option`, and the debug-mode panic a *signal*.

```python run
from ginsdk import machine as M

for policy in ("wrap", "saturate", "trap", "c-undefined"):
    o = M.add_fixed(2 ** 31 - 1, 1, 32, policy)
    print(f"{policy:12s} {o.kind:10s} {o.value if o.value is not None else '':>12}  {o.name or o.note}")
```

```output
wrap         value       -2147483648  result reduced mod 2^w (overflow flag set on most ISAs)
saturate     value        2147483647  clamped to the representable range
trap         exception                overflow
c-undefined  undefined                undefined behaviour
```

## Arbitrary precision {#sec:bignum}

Arbitrary-precision ("big") integers move the edge from the width of a register to the size of memory. Python's `int`, Java's `BigInteger`, JavaScript's `BigInt` and libraries such as GMP represent an integer as a sequence of machine words ("limbs") and implement the algorithms of Parts V–VIII on them. Overflow disappears; cost appears. Every operation now costs time proportional to a function of the operands' lengths: linear for addition, quadratic or sub-quadratic for multiplication and division (Chapter 37 measures it). A loop that computes $2^n$ by repeated doubling takes quadratic time in $n$, because the numbers grow.

Big integers also expose costs that fixed-width code never meets. Converting an integer to its decimal numeral is a change of base (Chapter 5), and with the schoolbook method it costs time quadratic in the number of digits. In 2022 this was recognized as a denial-of-service risk — a web service that parsed or printed numbers with millions of digits could be made to spend minutes on one request — and CPython 3.11 introduced a default limit on the number of decimal digits converted (CVE-2020-10735 \cite{cve2020_10735}).

```python run
import sys
print("default limit on int <-> decimal string conversion:", sys.get_int_max_str_digits(), "digits")
try:
    int("9" * 5000)
except ValueError as e:
    print("int('9' * 5000) ->", str(e)[:70] + "…")
print("binary is unaffected:", len(bin(10 ** 5000)) - 2, "bits written without complaint")
```

```output
default limit on int <-> decimal string conversion: 4300 digits
int('9' * 5000) -> Exceeds the limit (4300 digits) for integer string conversion: value h…
binary is unaffected: 16610 bits written without complaint
```

::: observation {#obs:cpython-limit title="A cost boundary enforced as an admissibility boundary" status="empirical" ledger="GIN-OBS-014"}
CPython ≥ 3.11 refuses int ↔ decimal-string conversion beyond 4,300 digits by default, because the conversion is quadratic and was a denial-of-service vector (CVE-2020-10735). Conversion to binary (a power-of-two base) is linear and is not limited. A runtime here treats a *cost* boundary as an *admissibility* boundary: the operation is well defined and refused anyway.
:::

## Exact decimals {#sec:decimals}

Binary floating point cannot hold most decimal fractions (\ledger{GIN-PROP-031}). Where decimal quantities must be exact — money is the standard example — three exact representations are common: integers counting the smallest unit (cents); rationals; and *decimal* floating point, standardized in IEEE 754 since 2008, in which the significand is a decimal integer and $0.1$ is exactly representable.

```python run
from decimal import Decimal
from fractions import Fraction

print("binary64 :", 0.1 + 0.2 == 0.3, "  ", 0.1 + 0.2)
print("decimal  :", Decimal("0.1") + Decimal("0.2") == Decimal("0.3"), "   ", Decimal("0.1") + Decimal("0.2"))
print("rational :", Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10), "   ", Fraction(1, 10) + Fraction(2, 10))
print("cents    :", 10 + 20 == 30)
print("but decimal is still finite:", Decimal(1) / Decimal(3), " * 3 =", Decimal(1) / Decimal(3) * 3)
```

```output
binary64 : False    0.30000000000000004
decimal  : True     0.3
rational : True     3/10
cents    : True
but decimal is still finite: 0.3333333333333333333333333333  * 3 = 0.9999999999999999999999999999
```

The last line is the decimal version of Chapter 7's theorem: $1/3$ has no finite numeral in base $10$, so a decimal format must round it. Changing the base moves the set of exactly representable fractions; it does not make every fraction representable. Only an exact rational representation does, at the cost of unbounded growth.

::: exercise {#ex:ov-loop}
A 32-bit signed counter starts at $0$ and is incremented once per millisecond. After how long does it overflow, and what value does it hold afterwards under wraparound?
:::

::: solution {of="ex:ov-loop"}
After $2^{31}$ ms $\approx 24.86$ days it would reach $2^{31}$, which wraps to $-2^{31}$. (A well-known class of bugs in long-running systems has exactly this period.)
:::

::: exercise {#ex:ov-rust}
For Rust `i8`, give the result of `100i8.wrapping_add(100)`, `100i8.saturating_add(100)`, `100i8.checked_add(100)` and `100i8.overflowing_add(100)`.
:::

::: solution {of="ex:ov-rust"}
$200 - 256 = -56$; $127$; `None`; `(-56, true)`.
:::

::: exercise {#ex:ov-decimal}
Show that no base $b$ represents every rational exactly with a finite numeral, and identify which rationals base $30$ does represent.
:::

::: solution {of="ex:ov-decimal"}
By Chapter 7, $p/q$ in lowest terms terminates in base $b$ iff every prime factor of $q$ divides $b$; any prime not dividing $b$ (there are infinitely many) gives a counterexample $1/q$. Base $30$ represents exactly the rationals whose reduced denominators have only the prime factors $2, 3, 5$.
:::

::: summary
- Overflow leaves an admissible result outside the encoding; systems wrap, saturate, signal or (C, signed) leave the behaviour undefined.
- Rust, C23 and others let the program name the policy per operation; each named method is one of the repairs of Chapter 9.
- Arbitrary precision trades overflow for cost; CPython limits decimal conversion because its cost was exploitable.
- Decimal formats represent decimal fractions exactly and still round $1/3$; only rationals are closed under division.
:::
