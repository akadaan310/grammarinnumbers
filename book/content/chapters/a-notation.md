---
title: "Notation and Conventions"
status: definition
statusnote: A reference list; every symbol is defined in the chapter cited.
description: The symbols, macros, typographic conventions and status badges used throughout the book.
---

## Sets and number systems {#sec:not-sets}

| symbol | meaning | defined in |
|---|---|---|
| $\N$ | natural numbers $0, 1, 2, \ldots$ (zero included) | Chapter 3 |
| $\Z, \Q, \R, \C$ | integers, rationals, reals, complex numbers | Chapters 27–28 |
| $\Zn$ | integers modulo $n$, residues $0, \ldots, n-1$ | Chapter 29 |
| $\F_q$, $\mathrm{GF}(2^8)$ | finite fields | Chapter 29 |
| $\Z_p$ | $p$-adic integers | Chapter 29 |
| $S$, $P$ | successor and predecessor moves | Chapter 3 |

## Numerals and representation {#sec:not-numerals}

| symbol | meaning | defined in |
|---|---|---|
| $\val_b(w)$, $\val(w)$ | value of the numeral $w$ in base $b$: the denotation of $w$ at $0$ | Chapter 5 |
| $\addr(n)$ | canonical numeral: shortlex-least word denoting $n$; $\addr(0) = \eps$ | Chapter 5 |
| $\eps$ | the empty word | Chapter 5 |
| $10_2$, `0b10` | a numeral read in base 2 | Chapter 5 |
| $\enc$, $\dec$ | encoding of values as bit strings; decoding (total on bit strings) | Chapter 7 |
| $\wrap$ | reduction to $w$-bit two's complement | Chapter 21 |
| $\trunc$ | rounding toward zero | Chapter 19 |
| $\fl(x)$, $\rnd$ | the floating-point value nearest $x$ (ties to even) | Chapter 25 |
| $\ulp(x)$ | unit in the last place | Chapter 25 |
| $\NaN$, $\pm 0$, $\pm\infty$ | IEEE 754 special data | Chapter 25 |
| $\Kk, \Pp, \Gg$ | kill, propagate, generate: the carry monoid | Chapter 11 |
| $\M$, $\Sq$ | multiply and square moves of the exponent program | Chapter 34 |

## Operations and solution sets {#sec:not-ops}

| symbol | meaning | defined in |
|---|---|---|
| $\sem{e}$ | the denotation of an expression or move word | Chapter 2 |
| $\Sol(a, b)$ | solution set $\{c : b \circ c = a\}$ of a converse problem | Chapter 9 |
| $\Ann(b)$ | annihilator $\{t : bt = 0\}$ | Chapter 16 |
| $\im f$, $\Ker f$ | image and kernel of a homomorphism | Chapter 16 |
| $a \divides b$, $a \ndivides b$ | divides, does not divide | Chapter 30 |
| $\gcd$, $\lcm$ | greatest common divisor, least common multiple (with $\gcd(0, 0) = 0$) | Chapter 30 |
| $a \monus b$ | truncated subtraction $\max(a - b, 0)$ | Chapter 12 |
| $\ord(a)$, $\varphi(n)$ | multiplicative order; Euler's totient | Chapter 31 |
| $\popcount(n)$ | number of $1$ digits in the binary numeral of $n$ | Chapter 34 |
| $\bott$ | the absorbing element of a wheel | Chapter 18 |

## Cost {#sec:not-cost}

| symbol | meaning | defined in |
|---|---|---|
| $L$ | bit length of the operands | Chapter 36 |
| $w$ | machine word length (the SDK's limbs: $w = 32$) | Chapter 36 |
| $M(L)$ | cost of multiplying two $L$-bit numbers | Chapter 15 |
| $\Oh$, $\Theta$ | asymptotic upper bound; tight bound | Chapter 36 |

Every cost names its model (unit cost, word RAM or bit complexity), its growing parameter, and whether it is a bound, an exact count or a measurement (\ledger{GIN-DEF-097}).

## Status badges and environments {#sec:not-status}

| badge | meaning |
|---|---|
| Definition | a precise object; not a discovery |
| Classical result | a known theorem, cited; a proof may be included for completeness |
| Proved here | proof written in this book and checked by computation on small cases; *not* a claim of novelty |
| Reinterpretation | a known fact restated in this book's vocabulary |
| Empirical observation | a reproducible measurement; not a proof |
| Implementation result | a property of the software, checked against an independent oracle |
| Counterexample | an instance in which a plausible claim fails |
| Conjecture / Open problem | not established |

Ledger identifiers have the form `GIN-KIND-nnn` (\chapref{c-ledger-guide}); identifiers of the separate CGT publication have the form `CGT-KIND-nnn`.

## Typographic conventions {#sec:not-typo}

- Code, numerals as strings and command lines are set in `monospace`; a numeral as a mathematical object is set in math.
- Executed examples are followed by their output, checked at every build: the book never shows output its code does not produce.
- Machine claims say whether they were **measured** (on the host named in Appendix B), **emulated** (QEMU) or **specified** (from a standard).
