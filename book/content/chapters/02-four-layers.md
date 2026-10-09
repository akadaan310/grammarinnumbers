---
title: "Number, Numeral, Encoding, Machine"
status: mixed
statusnote: The distinctions are standard; making them four explicit layers with named maps between them is this book's framework.
description: Twelve readings of "3", the four layers of value, numeral, encoding and machine state, the maps between them, and what is assumed when we say that a number exists, that two numerals are equal, or that an operation returns a result.
epigraph: "A digit is not a number, a numeral is not a number, a bit pattern is not a number, and a register is not a number. Each of them can stand for one."
---

::: objectives
- Distinguish the value $3$ from the digit `3`, the numerals `3`, `11₂`, `III`, `SSS0`, the bit patterns that encode it, and a machine state that holds one of them.
- Define the four layers — value, numeral, encoding, machine state — and the four maps between them: denotation, encoding, decoding and execution.
- State precisely what is assumed when we say that a number exists, that two numerals denote the same number, and that an operation returns a result.
- Recognize statements that silently cross layers, and rewrite them so that they do not.
:::

## Twelve readings of "3" {#sec:twelve}

Write the character `3` on a page. What has been written? The question has at least twelve answers, and they are not interchangeable.

| Reading | What "3" is | Layer |
|---|---|---|
| mathematical object | the element $S(S(S(0)))$ of the natural numbers | value |
| count | the number of elements of $\{a, b, c\}$ | value (via cardinality) |
| position | the fourth place in $0, 1, 2, 3, \ldots$ — or the third, if one counts from $1$ | value with an order convention |
| state | a node of the successor transition system | value as state |
| address | the canonical numeral of $3$ in some digit grammar: `3`, `11₂`, `10₃`, `SSS` | numeral |
| digit | the symbol `3` of the decimal alphabet | numeral alphabet |
| symbol | a token in an expression such as `3 + 1` | syntax |
| sequence | the one-letter word `3` in the language of decimal numerals | numeral |
| machine representation | `0x00000003` as a 32-bit integer; `0x4008000000000000` as an IEEE binary64 number | encoding |
| transition result | the value of `1 + 2`, of $S(2)$, of `6 / 2` | value (output of an operation) |
| algebraic element | $3 \in \Z, \Q, \R, \C$; the class $3 + n\Z$ in $\Z/n$; and $3 = 0$ in $\Z/3$ | value in a chosen structure |
| computational value | what a register holds after `mov eax, 3` | machine state |

Where do the readings agree? Every one of them denotes, encodes or holds the same natural number. Where do they diverge? A *digit* is not a number: `3` is a symbol, and in base $3$ there is no digit `3` at all. A *numeral* is not a number: `03` and `3` are different words with the same value. A *binary representation* is not the number: `11₂` and `3` are different words. A *machine word* is not an integer: the 32-bit pattern `0xFFFFFFFF` is $-1$ under one reading and $4294967295$ under another. A *residue class* is not an integer: $3 = 0$ in $\Z/3$, while $3 \neq 0$ in $\Z$.

Most of the time nothing goes wrong when these readings are blurred. This chapter separates them so that, in the rest of the book, we can say precisely what goes wrong when something does.

## The four layers {#sec:layers}

::: definition {#def:value title="Number (value)" status="definition" ledger="GIN-DEF-001"}
A **natural number** is an element of a *successor algebra* $(\N, 0, S)$: a set $\N$ with a distinguished element $0$ and an injective map $S : \N \to \N$ with $0 \notin S(\N)$, such that every subset of $\N$ that contains $0$ and is closed under $S$ is all of $\N$. Integers, rationals, reals and complex numbers are defined from $\N$ by standard constructions (Part XI). A **value** is an element of one of these structures. Values are not strings and have no digits.
:::

The definition is Dedekind's (1888) and, in axiomatic form, Peano's (1889) \cite{dedekind1888,peano1889}. Its last clause — the induction axiom — is what makes $\N$ the *smallest* set reachable from $0$ by successor steps. Without it, a structure could contain extra elements that are never reached by counting.

::: theorem {#thm:categoricity title="Dedekind's categoricity theorem" status="classical" ledger="GIN-HIST-002"}
Any two successor algebras $(\N, 0, S)$ and $(\N', 0', S')$ are isomorphic, and the isomorphism is unique: there is exactly one bijection $h : \N \to \N'$ with $h(0) = 0'$ and $h(S n) = S'(h n)$ for all $n$.
:::

::: proof
*Existence.* By the recursion theorem — itself proved from the induction axiom — there is a unique map $h : \N \to \N'$ with $h(0) = 0'$ and $h \circ S = S' \circ h$; symmetrically there is a unique $g : \N' \to \N$ with $g(0') = 0$ and $g \circ S' = S \circ g$. Then $g \circ h : \N \to \N$ satisfies $(g \circ h)(0) = 0$ and $(g\circ h) \circ S = S \circ (g \circ h)$, as does the identity; by the uniqueness clause of the recursion theorem, $g \circ h = \mathrm{id}$. Likewise $h \circ g = \mathrm{id}$. *Uniqueness.* Any $h'$ with the same two properties agrees with $h$ on $0$, and agrees on $S n$ whenever it agrees on $n$; the set where $h' = h$ therefore contains $0$ and is closed under $S$, so by induction it is all of $\N$.
:::

This theorem is what entitles us to speak of *the* natural numbers. It is also our first example of a pattern that recurs throughout the book: a *structure* is characterized by its operations and their laws, and any two *representations* of it — sets, numerals, bit patterns — are related by a unique structure-preserving translation. The value $3$ is what all representations of the third successor of zero have in common.

::: definition {#def:numeral title="Numeral and digit" status="definition" ledger="GIN-DEF-002"}
A **numeral** is a word over a finite **digit** alphabet, read in a *numeral system* that assigns it a value. `2`, `10₂`, `II`, `SS0` and `0010` are numerals. A digit is a letter of a numeral alphabet; a digit is a symbol, not a number, even when a one-letter numeral and its only digit are spelled alike.
:::

::: definition {#def:encoding title="Encoding" status="definition" ledger="GIN-DEF-003"}
An **encoding** of a set $V$ of values in a format $F$ is a partial injective map $\enc : V \rightharpoonup \{0,1\}^w$ together with a total decoding map $\dec : \{0,1\}^w \to V \cup S_F$, where $S_F$ is a set of *special data* that are not values. For IEEE 754 binary formats, $S_F$ contains $+\infty$, $-\infty$ and NaN, and the sign of zero is extra information that is not part of the value.
:::

::: definition {#def:machine-state title="Machine state" status="definition" ledger="GIN-DEF-004"}
A **machine state** assigns bit strings to registers and memory, together with status information: flags, pending exceptions, the trap state. An **instruction** is a partial map on states. The **execution** of an expression is a sequence of instructions; its **outcome** is either a final state from which a value is decoded, or a trap or exception state.
:::

The four definitions give four layers, and between them four maps:

$$
\underbrace{\text{numeral}}_{\text{word}} \xrightarrow{\ \text{denotation}\ } \underbrace{\text{value}}_{\text{element}} \xrightarrow{\ \text{encoding (partial)}\ } \underbrace{\text{bit string}}_{w \text{ bits}} \xrightarrow{\ \text{decoding (total)}\ } \text{value} \cup \text{special data}, \qquad \text{state} \xrightarrow{\ \text{execution}\ } \text{state}.
$$

A claim about arithmetic names its layer. "$1 + 1 = 2$" is a statement about values. "$1 + 1 = 10_2$" is the same statement about values, with the right-hand side written in a different numeral system. "`0x7FFFFFFF + 1` is `0x80000000`" is a statement about encodings under wraparound. "After `add eax, 1` the overflow flag is set" is a statement about machine states. The statements are related, but they are not the same statement, and a proof of one is not a proof of another.

## Encodings are partial; decodings forget {#sec:encodings}

The asymmetry between encoding and decoding in Definition \ref{def:encoding} is deliberate. An encoding is *partial* because a fixed number of bits can name only finitely many values: $2^{53}+1$ is an integer, but it has no binary64 encoding (\chapref{25-floating-point}). A decoding is *total* because every bit pattern must be read as *something* — and the something need not be a value.

::: proposition {#prop:enc-dec title="Encoding and decoding are not inverse to each other" status="proved-here" ledger="GIN-PROP-050"}
For every encoding, $\dec(\enc(v)) = v$ for every $v$ in the domain of $\enc$. The other composite is not the identity in general:
1. In IEEE binary64, exactly $2^{53} - 2$ of the $2^{64}$ bit patterns decode to the single datum NaN, and two patterns (`0x0000000000000000` and `0x8000000000000000`) decode to the value $0$.
2. The same 32-bit pattern decodes to different values under different encodings: `0xFFFFFFFF` is $-1$ in two's complement and $4294967295$ as an unsigned integer, and it is a NaN as an IEEE binary32 pattern.
:::

::: proof
The first claim is the definition of a decoding as a left inverse of the encoding. (1) A binary64 pattern is a NaN exactly when its 11 exponent bits are all ones and its 52 fraction bits are not all zero: $2$ signs times $2^{52} - 1$ fractions gives $2^{53} - 2$ patterns. A pattern with all exponent and fraction bits zero decodes to $\pm 0$, and both signed zeros have the value $0$. (2) Two's complement reads a $w$-bit pattern $\beta$ as $\beta - 2^{w}$ when its top bit is set, so `0xFFFFFFFF` $= 2^{32} - 1$ reads as $-1$; unsigned reading gives $2^{32} - 1$; as binary32 the exponent field `11111111` with non-zero fraction is a NaN.
:::

The second part of the proposition is the source of a large class of programming errors: the bits are the same, the *type* — which encoding is in force — is not. A bit pattern carries no type of its own.

::: counterexample {#neg:bits-value title="A bit pattern determines a value" status="counterexample" ledger="GIN-NEG-018"}
The claim "a register holds a number" is false at the encoding layer. The pattern `0xFFFFFFFF` is $-1$, $4294967295$, or not a number at all, depending on the encoding in force; the pattern `0x40490FDB` is the integer $1078530011$ and also the binary32 approximation of $\pi$.
:::

Here is the second pattern decoded three ways by the SDK:

```python run
import struct
from ginsdk import ieee

w = 0x40490FDB
print("unsigned :", w)
print("signed   :", w - (1 << 32) if w >> 31 else w)
x = ieee.from_bits(ieee.BINARY32, w)
print("binary32 :", x, "  exact value", x.value())
```

```output
unsigned : 1078530011
signed   : 1078530011
binary32 : 3.1415927   exact value 13176795/4194304
```

The binary32 number is the dyadic rational $13176795 / 2^{22}$, which is close to $\pi$ but is not $\pi$; no finite bit pattern encodes $\pi$ in any of the formats of this book.

## What is assumed when we say a number exists {#sec:exists}

Three familiar sentences carry hidden assumptions.

**"The number $3$ exists."** At the value layer, this means: in a successor algebra, the term $S(S(S(0)))$ denotes an element. That is guaranteed once a successor algebra exists at all. Its existence is not provable from nothing; it is an axiom of the background mathematics (in set theory, the axiom of infinity supplies a set closed under $x \mapsto x \cup \{x\}$, from which von Neumann's $\N$ is cut out). In this book we take the existence of $\N$ for granted, as all of ordinary mathematics does, and we never need more. At the encoding layer, "$3$ exists" is a different and *falsifiable* claim: the format has an encoding of $3$. It is true for every format in this book; the corresponding claim for $2^{53}+1$ in binary64 is false.

**"The numerals `3` and `0011₂` denote the same number."** This is a statement about two words and a denotation map: $\val_{10}(3) = \val_2(0011)$. It is decidable — by computing both values, or by reducing both words to canonical form and comparing — and its proof is a computation, not an insight. Chapter 5 shows that for standard positional systems two words have the same value exactly when they differ by leading zeros, so equality of numerals within one base reduces to equality of words after deleting leading zeros (\ledger{GIN-PROP-001}). Across bases it requires conversion, whose cost is the subject of \chapref{37-measured-complexity}.

**"The operation returns a result."** Three things are asserted at once: the operation is *defined* at these arguments (totality), its result is *unique* (functionality), and the result is *in the domain* (closure). Each can fail independently. Subtraction in $\N$ fails closure at $(0, 1)$; division in $\Q$ fails totality at $(1, 0)$ and functionality at $(0, 0)$ — which are the same failures, seen as a converse problem, that Part VIII will call *no solution* and *non-unique*. A machine can fail in yet another way: it may return a result that is not the mathematical one (wraparound, rounding), or return nothing and transfer control (a trap).

::: remark
The words "undefined", "invalid" and "error" are used for all of these failures in ordinary speech, and in many programming languages. This book never uses "undefined" as a final answer, except in its technical sense in the C language standard ("undefined behaviour"), where it means that the *program* has no meaning. For every failure it says which condition fails, at which layer.
:::

## Crossing layers safely {#sec:crossing}

Every computation crosses layers: a program reads numerals, encodes values, executes instructions, decodes results and prints numerals again. The crossings are where meaning can change. A safe crossing has three properties, which can be checked:

1. **The source is in the domain of the map.** The value must have an encoding in the target format (otherwise rounding or overflow intervenes); the bit string must be read with the encoding that produced it.
2. **The map commutes with the operation, or the discrepancy is stated.** Hardware addition on 32-bit two's-complement words commutes with integer addition *modulo* $2^{32}$, not in $\Z$; binary64 multiplication commutes with real multiplication followed by one rounding.
3. **The reverse crossing recovers the value.** Printing a binary64 number with too few digits and reading it back can change it; printing with the shortest round-tripping digit string cannot.

The software of this book makes the crossings explicit. Its evaluator never reports a bare number; it reports the layer reached, the domain, and the representation:

```python run
from ginsdk import evaluate

for d in ["Z", "int32 x86-64", "binary32"]:
    o = evaluate("16777216 + 1", d)
    print(f"{d:13s} {o.display:10s} {o.representation}")
```

```output
Z             16777217   {'exact': '16777217', 'binary': '1000000000000000000000001', 'hexadecimal': '1000001', 'bit length': 25}
int32 x86-64  16777217   {"two's complement": '00000001000000000000000000000001', 'hex': '0x01000001'}
binary32      16777216   {'datum': '16777216', 'sign': '0', 'exponent': '10010111', 'fraction': '00000000000000000000000', 'exact value': '16777216'}
```

In binary32 the sum $2^{24} + 1$ is not representable: the format has 24 significant bits, and $2^{24}+1$ needs 25. The exact sum is rounded to the nearest representable number, which — a tie between $2^{24}$ and $2^{24}+2$, broken towards the even significand — is $2^{24}$ itself. The equation $x + 1 = x$ has a solution in binary32. Chapter 25 explains why, and which other familiar laws fail.

::: exercise {#ex:fl-readings}
Give the reading (row of the table in §\ref{sec:twelve}) of "3" in each sentence: (a) "Turn to page 3." (b) "The array has 3 elements." (c) "`x = 3` sets the register to 3." (d) "In $\Z/3$, $3 = 0$." (e) "`3` is not a base-2 digit."
:::

::: solution {of="ex:fl-readings"}
(a) position (an ordinal, with a convention about the first page); (b) count; (c) machine representation / computational value; (d) algebraic element (a residue class); (e) digit.
:::

::: exercise {#ex:fl-nan-count}
How many binary32 bit patterns are NaNs? How many encode the value $0$? How many encode an integer?
:::

::: solution {of="ex:fl-nan-count"}
NaNs: exponent `11111111`, fraction non-zero: $2 \cdot (2^{23} - 1) = 2^{24} - 2$. Zero: two patterns ($\pm 0$). Integers: every finite pattern whose value is an integer. With 23 fraction bits, a normal number $1.f \times 2^{e}$ is an integer iff $e \ge 23$ or the low $23 - e$ fraction bits are zero ($0 \le e \le 22$). Counting for one sign: exponents $e = 0, \ldots, 22$ contribute $2^{e}$ each, $2^{23} - 1$ in total; exponents $23, \ldots, 127$ contribute $2^{23}$ each, $105 \cdot 2^{23}$; subnormals are never non-zero integers. With both signs and the two zeros: $2(2^{23} - 1 + 105 \cdot 2^{23}) + 2 = 212 \cdot 2^{23}$ patterns.
:::

::: exercise {#ex:fl-commute}
Show that for 32-bit two's complement, $\dec(\enc(a) \oplus \enc(b)) \equiv a + b \pmod{2^{32}}$, where $\oplus$ is the hardware addition of bit patterns as unsigned integers modulo $2^{32}$. When is the congruence an equality?
:::

::: solution {of="ex:fl-commute"}
$\enc(a) \equiv a \pmod{2^{32}}$ by definition of two's complement, and $\oplus$ is addition modulo $2^{32}$, so the sum pattern is congruent to $a + b$; $\dec$ preserves the residue. It is an equality exactly when $-2^{31} \le a + b < 2^{31}$, i.e. when the sum does not overflow.
:::

::: exercise {#ex:fl-exists}
Is the sentence "the number $10^{400}$ exists in binary64" true? Rewrite it as one true sentence about values and one true sentence about encodings.
:::

::: solution {of="ex:fl-exists"}
As stated it conflates layers. Value layer: "$10^{400}$ is a natural number" — true. Encoding layer: "$10^{400}$ has no binary64 encoding; rounding it to binary64 overflows to $+\infty$" — true, since the largest finite binary64 number is about $1.8 \times 10^{308}$.
:::

::: exercise {#ex:fl-cross}
In Python, `float(2**53 + 1) == float(2**53)` is `True`. Which crossing of §\ref{sec:crossing} fails, and which property?
:::

::: solution {of="ex:fl-cross"}
The crossing from the value $2^{53} + 1$ (an exact Python integer) to the binary64 encoding. Property 1 fails: the value is not in the domain of the encoding, so `float` rounds it (a tie, broken to the even significand $2^{53}$).
:::

::: summary
- "3" has at least twelve readings; they agree on the value and diverge on everything else.
- The four layers are value, numeral, encoding and machine state; the maps between them are denotation, encoding, decoding and execution.
- Encodings are partial and injective; decodings are total and forget (Proposition \ref{prop:enc-dec}); a bit pattern has no type of its own.
- "A number exists", "two numerals are equal" and "an operation returns a result" each hide assumptions that can fail independently.
:::
