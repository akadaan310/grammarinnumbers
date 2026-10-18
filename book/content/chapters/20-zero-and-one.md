---
title: "The Grammar of Zero and One"
status: mixed
statusnote: The facts are classical or are documented language and format semantics; their organization by role is this book's.
description: The many jobs of zero — identity, empty count, start state, empty address, placeholder, annihilator, origin, bit pattern — and the things zero is not: NULL, false, empty, uninitialized, NaN. Two zeros in IEEE 754. One as identity and as generator. Empty sums, empty products and 0⁰. Brahmagupta's zero, and what the history shows.
epigraph: "Zero is the number that does nothing in one operation and destroys everything in the other."
---

::: objectives
- List the roles of zero in the grammar of number and say which operation each role belongs to.
- Distinguish zero from the programming concepts it is often confused with: null references, false, empty strings, uninitialized memory, NaN.
- Explain why IEEE 754 has two zeros that compare equal and still behave differently.
- Distinguish one as the identity of multiplication from one as the generator of addition.
- Justify the conventions $\sum_{\varnothing} = 0$, $\prod_{\varnothing} = 1$ and $0^0 = 1$, and say where the last one stops being a convention.
:::

## The jobs of zero {#sec:zero-jobs}

Zero appears in this book in at least nine distinct roles.

| role | statement | where |
|---|---|---|
| additive identity | $a + 0 = a$ | every ring |
| empty count | $\lvert\varnothing\rvert = 0$ | cardinality |
| start state | the root of the successor grammar; the only state with no predecessor | Chapter 3 |
| empty address | the canonical numeral of $0$ is the empty word $\varepsilon$ | Chapter 5 |
| placeholder | the digit `0` inside `101` performs the move "multiply by the base, add nothing" | Chapter 5 |
| annihilator | $0 \cdot a = 0$ | a theorem in rings, an axiom in semirings (Chapter 14) |
| fixed point | $0^2 = 0$, $2 \cdot 0 = 0$: a fixed point of squaring and of scaling | Chapter 4 |
| origin | the point from which signed quantities are measured | ordered rings |
| bit pattern | `0…0` encodes $0$ in two's complement and $+0$ in IEEE formats | Chapter 2 |

The roles are compatible, but they are not the same role. In particular, zero is the identity of one operation (addition) and the annihilator of the other (multiplication). Every peculiarity of division by zero comes from that second role: an annihilator cannot be undone.

## What zero is not {#sec:zero-not}

Programming languages place several other concepts next to zero, and some encode them with the same bits. They are different things.

- **NULL** (a null reference) is the absence of a reference. Some languages encode it as the address $0$; the encoding coincides, the meaning does not. Dereferencing NULL is an error; using the integer $0$ is arithmetic.
- **false** is a truth value. In C and Python, `0` and `False` compare equal, and `0` is "falsy"; that is a language convention about conversion, not a fact about numbers.
- **the empty string** `""` is a numeral-like word of length zero — the spelling of zero's empty address, as it happens — but a string, not a number.
- **absence** (no value, `None`, a missing field, SQL `NULL`) is the absence of any value; SQL's `NULL` propagates through arithmetic like a NaN.
- **uninitialized memory** has no defined value at all; in C, reading it can be undefined behaviour, and it is not zero even if it often happens to contain zero bits.
- **NaN** is a datum that is not a number, and is unequal even to itself.

```python run
nan = float("nan")
print("0 == False:", 0 == False, "   0 is falsy:", not 0, "   0.0 and -0.0 are falsy:", not 0.0, not -0.0)
print("None == 0:", None == 0, "   '' == 0:", "" == 0, "   nan == nan:", nan == nan)
print("int(''):", end=" ")
try:
    int("")
except ValueError as e:
    print("ValueError —", e)
```

```output
0 == False: True    0 is falsy: True    0.0 and -0.0 are falsy: True True
None == 0: False    '' == 0: False    nan == nan: False
int(''): ValueError — invalid literal for int() with base 10: ''
```

The last line is a small instance of Chapter 5: Python refuses to read the empty string as a numeral, although in the digit grammar the empty word *is* zero's address. A reasonable choice — an empty input field is far more often a mistake than a zero — and a reminder that a written convention (`0`) has been put in place of the canonical but invisible address.

## Two zeros {#sec:signed-zero}

IEEE 754 binary formats have two zeros, $+0$ (all bits zero) and $-0$ (only the sign bit set). They compare equal, and they are the same *value*: $\dec(+0) = \dec(-0) = 0$ (Proposition GIN-PROP-050). But they are different *data*, and some operations can tell them apart.

```python run
from fractions import Fraction
from ginsdk import ieee

pz = ieee.round_exact(ieee.BINARY64, Fraction(0))[0]
nz = ieee.neg(pz)
one = ieee.from_decimal("1")[0]
print("bits:", hex(pz.bits()), hex(nz.bits()), "  same value:", pz.value() == nz.value())
print("1 / +0 =", ieee.div(one, pz)[0], "   1 / -0 =", ieee.div(one, nz)[0])
print("+0 + -0 =", ieee.add(pz, nz)[0], "   -0 + -0 =", ieee.add(nz, nz)[0], "   -1 * 0 =", ieee.mul(ieee.neg(one), pz)[0])
```

```output
bits: 0x0 0x8000000000000000   same value: True
1 / +0 = Infinity    1 / -0 = -Infinity
+0 + -0 = 0    -0 + -0 = -0    -1 * 0 = -0
```

The sign of zero records the side from which a result underflowed to zero, and division by zero returns the infinity on that side: $1/(+0) = +\infty$, $1/(-0) = -\infty$, mirroring $\lim_{x \to 0^\pm} 1/x = \pm\infty$. Kahan argued that this information is essential for the correct behaviour of complex functions along branch cuts \cite{kahan1987}. It is also a source of surprise: $x = y$ does not imply $1/x = 1/y$ in IEEE arithmetic, so equality of data is not equality of values, and neither is a congruence for division.

## One: identity and generator {#sec:one}

One is the identity of multiplication ($1 \cdot a = a$), and it is the **generator** of the natural numbers under addition: every $n$ is $1 + 1 + \cdots + 1$, and $\N$ is the free monoid on the single generator $1$ (Chapter 4). The two roles are independent. In $\Z/n$ every element is still a sum of ones, but $1$ is no longer the only element with an inverse: the *units* of $\Z/n$ are the $\varphi(n)$ residues coprime to $n$. In $\Z$, $1$ and $-1$ are the units. In a field, everything except $0$ is.

Zero and one also share a role: they are the only solutions of $x^2 = x$ in an integral domain. In rings with zero divisors there can be more idempotents: in $\Z/6$, $x^2 = x$ has the four solutions $0, 1, 3, 4$, and each non-trivial idempotent splits the ring into a product ($\Z/6 \cong \Z/2 \times \Z/3$, with $3 \mapsto (1, 0)$ and $4 \mapsto (0, 1)$).

## Empty sums, empty products, and $0^0$ {#sec:empty}

A sum of no terms is $0$, and a product of no factors is $1$: these are the only values that keep the laws $\sum_{A \sqcup B} = \sum_A + \sum_B$ and $\prod_{A \sqcup B} = \prod_A \cdot \prod_B$ true when $A$ or $B$ is empty. From the empty product follow $a^0 = 1$ for every $a$, including $a = 0$, and $0! = 1$. In combinatorics and algebra, $0^0 = 1$ is therefore not a guess but the only consistent value: $x^0$ counts the functions from the empty set to a set of size $x$, and there is exactly one such function even when $x = 0$.

In analysis, the same symbol names a *limit form*: if $f(x) \to 0$ and $g(x) \to 0$, then $f(x)^{g(x)}$ can tend to any value in $[0, 1]$ or fail to converge. The SDK follows the algebraic convention and says so:

```python run
from ginsdk import evaluate

o = evaluate("0 ^ 0", "Q")
print(o.display, "—", o.notes[0])
```

```output
1 — 0^0 = 1 is a convention (the empty product); as a limit form it is indeterminate
```

::: counterexample {#neg:zero-zero title="0⁰ has a determined value" status="counterexample" ledger="GIN-NEG-009"}
As the empty product, $0^0 = 1$ by the only consistent convention; as the limit form $\lim f^g$ with $f, g \to 0$, it is indeterminate ($x^{c/\ln x} = e^{c}$ for every $c$, while $x^x \to 1$ as $x \to 0^+$). The "value" depends on whether $0^0$ is read as a product or as a limit.
:::

## A brief history of zero as a number {#sec:zero-history}

Zero as a *placeholder* inside numerals predates zero as a *number*. Late Babylonian scribes used a separator sign for an empty sexagesimal place; positional decimal notation with a zero digit developed in India, and zero as a number with rules of arithmetic is stated explicitly by Brahmagupta in 628 CE \cite{kaplan1999,plofker2009}.

::: history {title="Brahmagupta's rules for zero (628 CE)" ledger="GIN-HIST-001"}
In the *Brāhmasphuṭasiddhānta*, Brahmagupta defines zero as the result of subtracting a number from itself and gives rules: the sum of zero and a number is the number, the product of zero and any number is zero, and $0/0 = 0$; a non-zero number divided by zero is a fraction with zero as denominator. Bhāskara II later called such a quantity *khahara* and described it as unchanged by adding or subtracting finite quantities — a description close to the modern $\infty$ of the projective line \cite{mactutor_brahmagupta,plofker2009}. In the vocabulary of this book, Brahmagupta's $0/0 = 0$ is a *selection* from a solution set that contains every number, the convention that meadows and proof assistants adopt today (Chapter 18). The account here relies on secondary sources; the primary text was not consulted.
:::

::: exercise {#ex:zo-idempotent}
Find all solutions of $x^2 = x$ in $\Z/12$ and $\Z/30$. How does their number relate to the prime factorization of the modulus?
:::

::: solution {of="ex:zo-idempotent"}
$\Z/12$: $0, 1, 4, 9$. $\Z/30$: $0, 1, 6, 10, 15, 16, 21, 25$. By the Chinese remainder theorem an idempotent is a choice of $0$ or $1$ in each prime-power factor: $2^k$ idempotents for $k$ distinct primes ($12 = 4 \cdot 3$: $4$; $30 = 2 \cdot 3 \cdot 5$: $8$).
:::

::: exercise {#ex:zo-signed}
Give three IEEE binary64 operations whose results differ only in the sign of zero, and one operation that turns the sign of zero into a difference of values.
:::

::: solution {of="ex:zo-signed"}
$0 \cdot 1 = +0$ versus $0 \cdot (-1) = -0$; $(+0) + (+0) = +0$ versus $(-0) + (-0) = -0$; $\sqrt{+0} = +0$ versus $\sqrt{-0} = -0$. Division turns the sign into a difference of values: $1/(+0) = +\infty$, $1/(-0) = -\infty$.
:::

::: exercise {#ex:zo-empty}
Using $\prod_{\varnothing} = 1$, justify $0! = 1$ and $\binom{n}{0} = 1$. What value does the empty $\min$ take, and why?
:::

::: solution {of="ex:zo-empty"}
$0!$ is the product of no factors: $1$. $\binom{n}{0} = n!/(0!\,n!) = 1$, and there is exactly one empty subset. The empty $\min$ must be the identity of $\min$, which is $+\infty$ (since $\min(x, +\infty) = x$); this is why minimization over an empty set is conventionally $+\infty$ in the extended reals.
:::

::: summary
- Zero is identity, empty count, start state, empty address, placeholder, annihilator, fixed point, origin and a bit pattern; division by zero fails because of the annihilator role.
- Zero is not NULL, false, empty, absent, uninitialized or NaN, even where encodings coincide.
- IEEE 754 has two zeros with one value; division can distinguish them.
- One is both the multiplicative identity and the additive generator; idempotents other than $0$ and $1$ signal a product decomposition.
- Empty sums and products force $0^0 = 1$ algebraically; as a limit form it is indeterminate.
- Zero as a number with arithmetic is documented from Brahmagupta (628 CE); his $0/0 = 0$ is a selection.
:::
