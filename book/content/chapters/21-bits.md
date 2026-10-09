---
title: "Bits, Words, and Two's Complement"
status: mixed
statusnote: All facts are classical; the 2-adic reading and the exhaustive checks are written here.
description: Bit strings are not numbers; signed representations compared (sign-magnitude, ones' complement, two's complement, offset); two's complement as the truncated 2-adic expansion; why one adder serves signed and unsigned numbers; overflow detection from carries; the asymmetry of the most negative number; shifts versus division; and bit operations read as numeral operations.
epigraph: "A word of thirty-two bits is not a number. It is a numeral in a finite alphabet, waiting for an encoding to say which number it names."
---

::: objectives
- Read a $w$-bit word under four signed encodings, and say which have two zeros and which are asymmetric.
- Prove that two's complement is the truncation of the 2-adic expansion, and explain why one adder serves signed and unsigned arithmetic.
- Detect signed overflow from the carries into and out of the top bit, and prove the rule.
- Distinguish arithmetic right shift from division, and $-x$ from $|x|$, at the most negative number.
- Interpret bit tricks such as `x & (x - 1)` as operations on numerals.
:::

## Words and encodings {#sec:machine-words}

A $w$-bit word is a string in $\{0, 1\}^w$. Read as an unsigned binary numeral it denotes a number in $[0, 2^w)$. To represent negative numbers, an *encoding* (Definition GIN-DEF-003) must be chosen, and several have been used.

| 4-bit word | unsigned | sign-magnitude | ones' complement | two's complement | offset (bias 7) |
|---|---|---|---|---|---|
| `0000` | 0 | +0 | +0 | 0 | −7 |
| `0001` | 1 | 1 | 1 | 1 | −6 |
| `0111` | 7 | 7 | 7 | 7 | 0 |
| `1000` | 8 | −0 | −7 | −8 | 1 |
| `1001` | 9 | −1 | −6 | −7 | 2 |
| `1110` | 14 | −6 | −1 | −2 | 7 |
| `1111` | 15 | −7 | −0 | −1 | 8 |

Sign-magnitude and ones' complement have **two zeros**, which complicates every equality test. Two's complement has one zero and is **asymmetric**: it can represent $-8$ but not $+8$. Offset ("biased") encoding is used for the exponent field of IEEE floating-point numbers, where it makes unsigned comparison of the bit patterns agree with numerical comparison. Modern processors use two's complement for integers because it has a property the others lack: the *same adder circuit* that adds unsigned numbers also adds signed ones.

## Two's complement is truncated 2-adic {#sec:2adic}

Why does the pattern `1111` denote $-1$? Run the residue algorithm of Chapter 5 on $-1$ in base $2$: the last digit is $-1 \bmod 2 = 1$, and the next state is $(-1 - 1)/2 = -1$ again. The algorithm never stops; it produces the infinite word $\ldots 1111$. That infinite word is the **2-adic expansion** of $-1$: the formal sum $1 + 2 + 4 + 8 + \cdots$, which in the 2-adic integers really does equal $-1$ (add $1$ and every carry propagates forever, leaving $\ldots 0000$).

::: proposition {#prop:twos-2adic title="Two's complement is the truncated 2-adic expansion" status="classical" ledger="GIN-PROP-008"}
For every integer $n$ and width $w$, the first $w$ digits $d_0, \ldots, d_{w-1}$ of the base-2 residue expansion of $n$ ($d = x \bmod 2$, $x \leftarrow (x - d)/2$) are the bits of $n \bmod 2^w$ — the $w$-bit two's-complement encoding when $-2^{w-1} \le n < 2^{w-1}$. For $n < 0$ the expansion never terminates: the state reaches $-1$, a fixed point of $x \mapsto (x - 1)/2$, after which every digit is $1$.
:::

::: proof
After $w$ steps $n = \sum_{i < w} d_i 2^i + 2^w x_w$, so $\sum d_i 2^i \equiv n \pmod{2^w}$ and lies in $[0, 2^w)$. For $x < 0$ the map $x \mapsto \lfloor x/2 \rfloor$ increases toward $-1$ and fixes it, and at $-1$ the digit is $1$.
:::

```python run
from ginsdk.numerals import BINARY, twos_complement_from_2adic

digits, status = BINARY.expand(-5, max_digits=12)
print("residue expansion of -5, least significant first:", digits, status)
for n in (5, -5, -1, -128, 127):
    print(f"{n:5d}: 8-bit two's complement {twos_complement_from_2adic(n, 8)}   n mod 256 = {n % 256}")
```

```output
residue expansion of -5, least significant first: (1, 1, 0, 1) periodic
    5: 8-bit two's complement 00000101   n mod 256 = 5
   -5: 8-bit two's complement 11111011   n mod 256 = 251
   -1: 8-bit two's complement 11111111   n mod 256 = 255
 -128: 8-bit two's complement 10000000   n mod 256 = 128
  127: 8-bit two's complement 01111111   n mod 256 = 127
```

The expansion of $-5$ stops after four digits with status "periodic": the state has returned to $-1$, and every later digit is $1$. A $w$-bit machine keeps the first $w$ digits and discards the rest — which is exactly reduction modulo $2^w$. That is why one adder suffices: unsigned and two's-complement addition are both addition in $\Z/2^w$; only the *labels* of the $2^w$ residues differ, $[0, 2^w)$ in one case and $[-2^{w-1}, 2^{w-1})$ in the other.

## Detecting overflow {#sec:overflow}

The adder computes the correct result modulo $2^w$ in both readings. Whether the result is also correct *as an integer* depends on the reading. For unsigned numbers, overflow is the carry out of the top bit. For signed numbers the rule is different.

::: proposition {#prop:signed-overflow title="Signed overflow is a disagreement of carries" status="classical" ledger="GIN-PROP-067"}
Add two $w$-bit two's-complement numbers with a binary adder, and let $c_{w-1}$ be the carry *into* the top position and $c_w$ the carry *out* of it. The exact sum lies outside $[-2^{w-1}, 2^{w-1})$ if and only if $c_{w-1} \ne c_w$. Equivalently, overflow occurs iff both operands have the same sign and the result's sign differs from it.
:::

::: proof
Write the operands as $a = -a_{w-1}2^{w-1} + a'$ and $b = -b_{w-1}2^{w-1} + b'$ with $0 \le a', b' < 2^{w-1}$. Then $a' + b' = s' + c_{w-1} 2^{w-1}$ with $s'$ the low $w - 1$ bits of the result, and the top bit and carry out satisfy $a_{w-1} + b_{w-1} + c_{w-1} = s_{w-1} + 2c_w$. The exact sum is $a + b = -(a_{w-1} + b_{w-1})2^{w-1} + s' + c_{w-1}2^{w-1}$. The encoded result is $-s_{w-1}2^{w-1} + s'$. Their difference is $(-(a_{w-1} + b_{w-1}) + c_{w-1} + s_{w-1}) 2^{w-1} = (2c_{w-1} - 2c_w) 2^{w-1}$ after substituting $s_{w-1} = a_{w-1} + b_{w-1} + c_{w-1} - 2c_w$. It is zero iff $c_{w-1} = c_w$.
:::

```python run
def check(w):
    lo, hi, bad = -2 ** (w - 1), 2 ** (w - 1), 0
    for a in range(lo, hi):
        for b in range(lo, hi):
            ua, ub = a % 2 ** w, b % 2 ** w
            low = (ua % 2 ** (w - 1)) + (ub % 2 ** (w - 1))
            c_in = low >> (w - 1)
            c_out = (ua + ub) >> w
            overflow = not (lo <= a + b < hi)
            bad += overflow != (c_in != c_out)
    return bad
print({w: check(w) for w in range(2, 9)}, "mismatches by width")
```

```output
{2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0} mismatches by width
```

Processors compute both flags on every addition: the *carry* flag for the unsigned reading and the *overflow* flag for the signed reading. The hardware does not know which reading the program intends; the program chooses which flag to test — or, in most high-level languages, tests neither.

## The most negative number {#sec:int-min}

Two's complement's asymmetry has consequences that every systems programmer meets eventually. In 32 bits the most negative number is $-2^{31}$, and its negation, $2^{31}$, is not representable: wraparound negation returns $-2^{31}$ itself. So does the absolute value function of most C libraries, and so does $-2^{31} / -1$ on machines that do not trap (Chapter 24). The equation $-x = x$ has *two* solutions in $\Z/2^{32}$, namely $0$ and $2^{31}$; in $\Z$ it has one.

```python run
from ginsdk import evaluate

for e, d in [("0 - (-2147483647 - 1)", "int32 Java"), ("(-2147483647 - 1) / -1", "int32 Java"),
             ("(-2147483647 - 1) / -1", "int32 x86-64"), ("0 - (-2147483647 - 1)", "int32 Rust (debug)")]:
    o = evaluate(e, d)
    print(f"{e:24s} {d:19s} {o.status:10s} {o.display or o.reason.split(':')[0].split(' —')[0]}")
```

```output
0 - (-2147483647 - 1)    int32 Java          value      -2147483648
(-2147483647 - 1) / -1   int32 Java          value      -2147483648
(-2147483647 - 1) / -1   int32 x86-64        trap       #DE (divide error)
0 - (-2147483647 - 1)    int32 Rust (debug)  exception  subtraction overflows 32 bits (exact result 2147483648)
```

## Shifts are not divisions {#sec:shifts}

Shifting a binary numeral left by $k$ places multiplies its value by $2^k$, modulo $2^w$; in the move language of Chapter 5 it appends $k$ zero digits. Shifting right drops digits. For unsigned words, a right shift by $k$ is $\lfloor x / 2^k \rfloor$. For signed words, an *arithmetic* right shift copies the sign bit into the vacated positions and computes $\lfloor x / 2^k \rfloor$ — *floored* division. C's integer division truncates. The two disagree on negative odd numbers: $-7 \gg 1 = -4$, but $-7 / 2 = -3$ in C. A compiler that replaces `x / 2` by a shift must add a correction for negative $x$; one that replaces `x >> 1` by `x / 2` would introduce a bug.

## Bit operations as numeral operations {#sec:bit-tricks}

Bitwise operations act on numerals, not on values, but some of them have clean meanings on values:

- `x & (x - 1)` clears the lowest set bit: subtracting $1$ turns the trailing zeros into ones and the lowest one into a zero (the successor's carry pattern, reversed), and the AND keeps everything above. Hence `x & (x - 1) == 0` tests whether $x$ is zero or a power of two.
- `x & -x` isolates the lowest set bit, $2^{v_2(x)}$, where $v_2$ is the 2-adic valuation: in two's complement, $-x = \bar x + 1$ agrees with $x$ exactly at the lowest set bit.
- `popcount(x)`, the number of ones, is the digit sum of the binary numeral; Chapter 7 used it to count the cost of counting.

These identities hold for unsigned words and, with the 2-adic reading, for signed ones; they are classical tools of bit-level programming. They also show the point of this chapter in miniature: a bit operation is a statement about the numeral, and it says something about the number only through an encoding.

::: exercise {#ex:bits-encodings}
Write $-3$ in 6-bit sign-magnitude, ones' complement, two's complement and offset-31 encoding.
:::

::: solution {of="ex:bits-encodings"}
Sign-magnitude `100011`; ones' complement `111100`; two's complement `111101`; offset 31: $-3 + 31 = 28$ = `011100`.
:::

::: exercise {#ex:bits-overflow}
In 8-bit two's complement, compute $100 + 50$, $-100 + (-50)$ and $100 + (-50)$ with an adder, giving the carries $c_7, c_8$ and the overflow verdict.
:::

::: solution {of="ex:bits-overflow"}
$100 + 50 = 150$: low 7 bits $100 + 50 = 150 \ge 128$, so $c_7 = 1$; top bits $0 + 0 + 1$, $c_8 = 0$: overflow (result $-106$). $-100 + -50$: patterns $156 + 206 = 362$; low 7 bits $28 + 78 = 106 < 128$, $c_7 = 0$; top bits $1 + 1 + 0$, $c_8 = 1$: overflow (result $106$). $100 + (-50)$: $100 + 206$; low bits $100 + 78 = 178 \ge 128$, $c_7 = 1$; top $0 + 1 + 1$, $c_8 = 1$: no overflow (result $50$).
:::

::: exercise {#ex:bits-lowest}
Prove that in $w$-bit two's complement, $x \mathbin{\&} (-x) = 2^{v_2(x)}$ for every $x \ne 0$, where $v_2(x)$ is the number of trailing zeros.
:::

::: solution {of="ex:bits-lowest"}
Write $x = u\,1\,0^k$ (bits), $k = v_2(x)$. Then $\bar x = \bar u\,0\,1^k$ and $-x = \bar x + 1 = \bar u\,1\,0^k$: the carry from the trailing ones stops at the $0$. The AND of $u10^k$ and $\bar u10^k$ is $0\cdots010^k = 2^k$.
:::

::: summary
- A word is a numeral; an encoding gives it a value. Sign-magnitude and ones' complement have two zeros; two's complement is asymmetric.
- Two's complement is the truncated 2-adic expansion: $w$-bit arithmetic is $\Z/2^w$, so one adder serves both readings.
- Signed overflow is detected by $c_{w-1} \ne c_w$; unsigned overflow by $c_w$.
- $-2^{w-1}$ is its own negative; arithmetic right shift floors while C's division truncates.
- Bit tricks are numeral operations whose meaning on values passes through the encoding.
:::
