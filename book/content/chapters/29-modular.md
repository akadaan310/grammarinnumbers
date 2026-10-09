---
title: "ℤ/n, Finite Fields, and the 2-adic Integers"
status: mixed
statusnote: The algebra is classical; the censuses, the GF(2⁸) implementation and the inverse-iteration counts are computed here.
description: Modular arithmetic as the arithmetic of a quotient — residues and their representatives, units and zero divisors, the prime fields, the field of 256 elements used by AES (in which the same bytes add without carries), multiplicative inverses modulo a power of two by Newton iteration, and the 2-adic integers that lie behind machine words.
epigraph: "A byte is not a number until you say which arithmetic it obeys. ℤ/256 and GF(2⁸) disagree about almost every sum."
---

::: objectives
- Describe $\Z/n$ as the quotient of $\Z$ by $n\Z$, and distinguish residues from their representatives.
- Prove that in a finite commutative ring every non-zero element is a unit or a zero divisor, and count both in $\Z/n$.
- Construct $\mathrm{GF}(2^8)$ from polynomials, and compute in it with shifts and exclusive-or.
- Compute the inverse of an odd number modulo $2^w$ by Newton iteration, and use it for exact division.
- Read a machine word as a truncation of a 2-adic integer.
:::

## A quotient and its representatives {#sec:quotient}

$\Z/n$ is the set of residue classes $[a] = a + n\Z$, with $[a] + [b] = [a + b]$ and $[a][b] = [ab]$. These operations are well defined — they do not depend on which element of the class is used — because $n\Z$ is an *ideal*: $a \equiv a'$ and $b \equiv b'$ imply $a + b \equiv a' + b'$ and $ab \equiv a'b'$. The map $a \mapsto [a]$ is a ring homomorphism, and $\Z/n$ is the arithmetic of what the homomorphism remembers: the last digit in base $n$, in the language of Chapter 5.

A class is not a number; to write it down one picks a **representative**. The usual choices are another instance of the *selection* repair:

| convention | representatives of $\Z/8$ | used by |
|---|---|---|
| least non-negative | $0, 1, \ldots, 7$ | mathematics texts; unsigned words; Python `%` with positive modulus |
| symmetric (balanced) | $-4, \ldots, 3$ | two's-complement signed words (Chapter 21); lattice cryptography |
| whatever arrives | any integer | lazy reduction in fast arithmetic (Chapter 34) |

The values in a signed and an unsigned 8-bit register are the same residues of $\Z/256$ with different representatives; addition, subtraction and multiplication do not care which, and that is why one adder serves both (Chapter 21). Division, comparison and conversion to a wider type *do* care, and that is where signed and unsigned instructions part.

Chapter 27 noted that no order on $\Z/n$ is compatible with addition. In terms of representatives: $7 + 1 = 0$ in $\Z/8$ under either convention, so "$x < x + 1$" must fail somewhere.

## Units and zero divisors {#sec:units}

Chapter 16 showed that $b$ is invertible in $\Z/n$ exactly when $\gcd(b, n) = 1$, and that otherwise the converse problem $bc = a$ has either no solution or $\gcd(b, n)$ of them (\ledger{GIN-THM-002}). In a finite ring there is no third kind of non-zero element:

::: proposition {#prop:unit-or-zd title="In a finite commutative ring, every non-zero element is a unit or a zero divisor" status="classical" ledger="GIN-PROP-071"}
Let $R$ be a finite commutative ring with $1 \ne 0$, and $b \ne 0$. Either $b$ has an inverse, or $bc = 0$ for some $c \ne 0$, and not both.
:::

::: proof
Consider the map $m_b : R \to R$, $c \mapsto bc$. If it is injective, it is bijective because $R$ is finite, so some $c$ has $bc = 1$. If it is not injective, $bc = bc'$ with $c \ne c'$, so $b(c - c') = 0$ with $c - c' \ne 0$. Both at once is impossible: $bc = 0$ and $b' b = 1$ give $c = b'bc = 0$.
:::

The proof is the image/kernel theorem of Chapter 16 in its finite form: $m_b$ is either a bijection (every division by $b$ has one answer) or has a non-trivial kernel (divisions by $b$ have none or several). Infinite rings escape the dichotomy: in $\Z$, the element $2$ is neither a unit nor a zero divisor.

```python run
from math import gcd
from ginsdk import numbertheory as nt

for n in (12, 30, 31, 256):
    units = [a for a in range(1, n) if gcd(a, n) == 1]
    zero_divisors = [a for a in range(1, n) if any(a * c % n == 0 for c in range(1, n))]
    assert sorted(units + zero_divisors) == list(range(1, n))
    print(f"Z/{n:<4d} units {len(units):3d} = phi(n) = {nt.phi(n):3d}   zero divisors {len(zero_divisors):3d}")
```

```output
Z/12   units   4 = phi(n) =   4   zero divisors   7
Z/30   units   8 = phi(n) =   8   zero divisors  21
Z/31   units  30 = phi(n) =  30   zero divisors   0
Z/256  units 128 = phi(n) = 128   zero divisors 127
```

The count of units is Euler's function $\varphi(n)$ (Chapter 32). For a prime $p$ there are no zero divisors at all: every non-zero element is a unit and $\Z/p$ is a field, often written $\mathbb{F}_p$. $\Z/256$, the arithmetic of a byte, has $128$ units — the odd bytes — and $127$ zero divisors.

## The field with 256 elements {#sec:gf256}

Since $256$ is not prime, $\Z/256$ is not a field. But there *is* a field with $256$ elements, and it is used on every computer that runs AES \cite{fips197}. It is built not from integers but from polynomials over $\mathbb{F}_2 = \{0, 1\}$:

::: definition {#def:gf2n title="The field GF(2ⁿ)" status="classical" ledger="GIN-DEF-093"}
Let $m(x)$ be an irreducible polynomial of degree $n$ over $\mathbb{F}_2$. $\mathrm{GF}(2^n)$ is the set of polynomials over $\mathbb{F}_2$ of degree less than $n$, with addition of polynomials (coefficientwise, modulo $2$) and multiplication of polynomials followed by reduction modulo $m(x)$. It is a field; any two choices of $m$ give isomorphic fields.
:::

An element is stored as $n$ bits — the coefficients. For AES, $n = 8$ and $m(x) = x^8 + x^4 + x^3 + x + 1$ (bits `0x11B`). The *same byte* now has a different arithmetic:

- **Addition is exclusive-or.** Coefficients add modulo $2$ independently: there are no carries. In the vocabulary of Chapter 11, the carry monoid is trivial — every position is *kill*.
- **Multiplication is shift-and-add without carries,** with a reduction whenever a term of degree $8$ appears.

```python run
def gf_mul(a, b):
    """Multiply in GF(2^8) with m(x) = x^8 + x^4 + x^3 + x + 1."""
    r = 0
    while b:
        if b & 1:
            r ^= a          # add (xor) the current shifted copy
        b >>= 1
        a <<= 1             # multiply by x
        if a & 0x100:
            a ^= 0x11B      # reduce modulo m(x)
    return r

a, b = 0x57, 0x83
print(f"{a:#04x} + {b:#04x}:  Z/256 -> {(a + b) % 256:#04x}   GF(2^8) -> {a ^ b:#04x}")
print(f"{a:#04x} * {b:#04x}:  Z/256 -> {(a * b) % 256:#04x}   GF(2^8) -> {gf_mul(a, b):#04x}")
print(f"0x53 * 0xca in GF(2^8) -> {gf_mul(0x53, 0xCA):#04x}")
inverses = {x: next(y for y in range(1, 256) if gf_mul(x, y) == 1) for x in range(1, 256)}
print("non-zero bytes with a GF(2^8) inverse:", len(inverses), "   odd bytes (units of Z/256):", 128)
```

```output
0x57 + 0x83:  Z/256 -> 0xda   GF(2^8) -> 0xd4
0x57 * 0x83:  Z/256 -> 0x85   GF(2^8) -> 0xc1
0x53 * 0xca in GF(2^8) -> 0x01
non-zero bytes with a GF(2^8) inverse: 255    odd bytes (units of Z/256): 128
```

::: example {#exm:gf-vs-z}
The bytes `0x57` and `0x83` sum to `0xda` in $\Z/256$ and to `0xd4` in $\mathrm{GF}(2^8)$; their products are `0x85` and `0xc1`. In $\mathrm{GF}(2^8)$ every non-zero byte is invertible — `0x53` and `0xca` are inverses — while in $\Z/256$ only the odd bytes are. The bit pattern is the same; the arithmetic is a choice of grammar, as Chapter 2 argued for the interpretation of bits.
:::

## Inverses modulo $2^w$ {#sec:inverse-2w}

An odd number $a$ is a unit of $\Z/2^w$, so it has an inverse $a^{-1}$ modulo $2^w$. It can be computed without division by *Newton iteration*:

::: proposition {#prop:newton-inverse title="Newton iteration for inverses modulo a power of two" status="classical" ledger="GIN-PROP-072"}
Let $a$ be odd. If $ax \equiv 1 \pmod{2^k}$, then $x' = x(2 - ax)$ satisfies $ax' \equiv 1 \pmod{2^{2k}}$. Since $a \cdot a \equiv 1 \pmod 8$ for every odd $a$, starting from $x_0 = a$ the iteration reaches $w$ correct bits after $\lceil \log_2(w/3) \rceil$ steps: four for $w = 32$, five for $w = 64$. If moreover $d$ is odd and $d \mid x$, then $x / d = x \cdot d^{-1} \bmod 2^w$ for $0 \le x < 2^w$.
:::

::: proof
Write $ax = 1 + t$ with $2^k \mid t$. Then $ax' = ax(2 - ax) = (1 + t)(1 - t) = 1 - t^2$, and $2^{2k} \mid t^2$. For odd $a = 2j + 1$, $a^2 = 4j(j + 1) + 1$ and $j(j + 1)$ is even, so $a^2 \equiv 1 \pmod 8$: $k_0 = 3$. After $s$ steps $k = 3 \cdot 2^s$, which is $\ge 32$ for $s = 4$ and $\ge 64$ for $s = 5$. Finally, if $x = qd$ with $0 \le q < 2^w$, then $x d^{-1} \equiv q d d^{-1} \equiv q$, and $q$ is its own least non-negative representative.
:::

```python run
def inverse_mod_2w(a, w):
    x, correct_bits, steps = a, 3, 0
    while correct_bits < w:
        x = x * (2 - a * x) % 2 ** w
        correct_bits, steps = 2 * correct_bits, steps + 1
    return x, steps

for a in (3, 7, 12345):
    for w in (32, 64):
        x, steps = inverse_mod_2w(a, w)
        assert a * x % 2 ** w == 1
        print(f"a = {a:<6d} w = {w}: inverse {x:#0{w // 4 + 2}x} after {steps} steps")

x, _ = inverse_mod_2w(7, 32)
print("exact division 7 * 123456789 / 7 by multiplication:", 7 * 123456789 * x % 2 ** 32)
print("inexact: 100 * inverse(7) mod 2^32 =", 100 * x % 2 ** 32, " (not 100 // 7 = 14)")
```

```output
a = 3      w = 32: inverse 0xaaaaaaab after 4 steps
a = 3      w = 64: inverse 0xaaaaaaaaaaaaaaab after 5 steps
a = 7      w = 32: inverse 0xb6db6db7 after 4 steps
a = 7      w = 64: inverse 0x6db6db6db6db6db7 after 5 steps
a = 12345  w = 32: inverse 0x55d4be09 after 4 steps
a = 12345  w = 64: inverse 0x4963847d55d4be09 after 5 steps
exact division 7 * 123456789 / 7 by multiplication: 123456789
inexact: 100 * inverse(7) mod 2^32 = 1840700284  (not 100 // 7 = 14)
```

Exact division by multiplication is used by compilers when the language guarantees divisibility — for instance in the subtraction of two pointers, whose byte difference is a known multiple of the element size. The last line shows the boundary: when $d \nmid x$, the product is the unique solution of $7c \equiv 100 \pmod{2^{32}}$ — a perfectly good element of $\Z/2^{32}$ that is *not* the integer quotient. The converse problem is solvable in $\Z/2^{32}$ and not in $\Z$, and the two answers have nothing to do with each other.

## The 2-adic integers {#sec:2adic-integers}

The inverse of $3$ modulo $2^{16}$ is `1010101010101011` in binary; modulo $2^{32}$ it is the same pattern, twice as long; modulo $2^{64}$, longer still. The patterns are *compatible*: each truncates the next. The limit object is an infinite string of bits extending to the left,
$$
\tfrac{1}{3} = \ldots 1010101010101011_2,
$$
a **2-adic integer**.

::: definition {#def:padic title="p-adic integers" status="classical" ledger="GIN-DEF-094"}
A $p$-adic integer is a sequence $(x_1, x_2, \ldots)$ with $x_k \in \Z/p^k$ and $x_{k+1} \equiv x_k \pmod{p^k}$ for every $k$; equivalently, an infinite base-$p$ numeral $\ldots d_2 d_1 d_0$. Addition and multiplication are computed position by position from the right, with carries, exactly as for finite numerals. The ring is written $\Z_p$.
:::

Chapter 21 proved that two's complement is the truncation of this numeral to $w$ digits (\ledger{GIN-PROP-050}): $-1 = \ldots 111_2$ because adding $1$ produces a carry that never stops. In $\Z_2$ every odd number is a unit, so $1/3$, $-1/7$ and $1/12345$ are 2-adic integers, though $1/2$ is not. A $w$-bit register holds the first $w$ digits of a 2-adic integer; the arithmetic of words is the arithmetic of $\Z_2$ seen through a window of width $w$. The window does not affect $+$, $-$ and $\times$, because their digits depend only on lower digits (carries move left). It does affect division, comparison and right shifts, which need digits from *outside* the window — and those are the operations whose machine behaviour Part X found most varied.

::: exercise {#ex:mod-units}
List the units and the zero divisors of $\Z/15$. Which elements $b$ make the converse problem $bc = 5$ solvable, and how many solutions does each have?
:::

::: solution {of="ex:mod-units"}
Units: $1, 2, 4, 7, 8, 11, 13, 14$ ($\varphi(15) = 8$). Zero divisors: $3, 5, 6, 9, 10, 12$. $bc = 5$ is solvable iff $\gcd(b, 15) \mid 5$: for the eight units (one solution each) and for $b \in \{5, 10\}$ ($\gcd = 5$, five solutions each); for $b \in \{3, 6, 9, 12\}$ ($\gcd = 3 \nmid 5$) there is none.
:::

::: exercise {#ex:mod-gf}
Show that $x^8 + x^4 + x^3 + x + 1$ has no root in $\mathbb{F}_2$. Why is that not enough to prove it irreducible, and what further check would be?
:::

::: solution {of="ex:mod-gf"}
At $x = 0$ it is $1$, at $x = 1$ it is $1 + 1 + 1 + 1 + 1 = 1$. No root means no linear factor, but a degree-8 polynomial may factor into irreducible factors of degrees $2$ to $4$. A complete check divides it by every irreducible polynomial of degree $2$, $3$ and $4$ over $\mathbb{F}_2$ (there are $1 + 2 + 3 = 6$), or verifies, as the code above effectively does, that every non-zero element of the resulting ring is invertible.
:::

::: exercise {#ex:mod-2adic}
Compute the last eight bits of the 2-adic integers $-1/3$ and $1/5$, and check the first by adding it to $1/3$.
:::

::: solution {of="ex:mod-2adic"}
$1/3 \equiv$ `10101011` and $-1/3 \equiv 256 - 171 = 85 =$ `01010101`; their sum is $256 \equiv 0$. $1/5$: $5 \cdot 205 = 1025 \equiv 1 \pmod{256}$, so $1/5 \equiv 205 =$ `11001101`.
:::

::: summary
- $\Z/n$ is a quotient; its elements are classes, and representatives are a selection (least non-negative, symmetric) that matters only for division, comparison and widening.
- In a finite commutative ring every non-zero element is a unit or a zero divisor; $\Z/n$ has $\varphi(n)$ units, and $\Z/p$ is a field.
- $\mathrm{GF}(2^8)$ gives the same 256 bytes a field arithmetic with carry-free addition (xor); AES computes in it.
- Odd numbers are invertible modulo $2^w$; Newton iteration finds the inverse in $\lceil \log_2(w/3) \rceil$ steps, and multiplication by it performs exact division.
- Machine words are truncated 2-adic integers; the truncation is invisible to $+, -, \times$ and visible to division, comparison and shifts.
:::
