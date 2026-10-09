---
title: "Other Digit Grammars"
status: mixed
statusnote: Bijective, balanced, negative-base and redundant numeration are classical; the heap conjugacy is elementary and probably folklore; the compression reading is a reinterpretation.
description: Changing the digit set changes the grammar. Bijective numeration has no zero digit and no redundancy; balanced ternary and base −2 name every integer; redundant digits make numerals non-unique and addition carry-free; CGT's heap numeration is bijective binary in disguise; and positional notation is a compression of unary.
epigraph: "The base fixes how much one more digit is worth; the digit set fixes what can be said, and how many ways there are of saying it."
---

::: objectives
- State when a digit grammar names every number, when it names each number exactly once, and how to compute numerals by the residue algorithm.
- Use bijective, balanced-ternary, negative-base and redundant numeration, and say what each gains and loses compared with standard notation.
- Prove that CGT's heap numeration of binary trees is bijective binary shifted by one.
- Read a positional numeral as a straight-line program that compresses a unary term, and relate it to exponentiation by squaring.
:::

## The residue algorithm, in general {#sec:residue}

Chapter 5 computed numerals by repeatedly taking the last digit as a residue. The same idea works for any digit set that contains one representative of each residue class modulo the base.

::: proposition {#prop:residue-systems title="Residue digit systems; bijective numeration" status="classical" ledger="GIN-PROP-004"}
Let $b \ge 2$ and let $D$ be a complete residue system modulo $b$ (or $b = 1$ and $D = \{1\}$).
1. If a word $w$ denotes $n$, its last digit is the unique $d \in D$ with $d \equiv n \pmod b$, and its prefix denotes $(n - d)/b$. So the words denoting $n$ are determined by the residue algorithm, up to prefixes that denote $0$.
2. *Standard* digits $\{0, \ldots, b-1\}$ and *balanced ternary* ($b = 3$, $D = \{-1, 0, 1\}$): every $n \in \N$ (respectively every $n \in \Z$) has a canonical numeral, and the words denoting $n$ are exactly $0^k \addr(n)$.
3. *Bijective* digits $D = \{1, \ldots, b\}$: the value map $D^* \to \N$ is a bijection.
:::

::: proof
(1) $\val(w'd) = b\,\val(w') + d$, so $d \equiv \val(w'd) \pmod b$, and $D$ contains exactly one such $d$. (2) The residue algorithm terminates: for standard digits as in Chapter 5; for balanced ternary, $|(n - d)/3| \le (|n| + 1)/3 < |n|$ whenever $|n| \ge 1$. A prefix denoting $0$ must end in the digit $\equiv 0$, which is $0$, and so consists of zeros. (3) A non-empty word of positive digits has positive value, so only $\varepsilon$ denotes $0$; for $n \ge 1$ the step $n \mapsto (n - d)/b$ with $d \in \{1, \ldots, b\}$ strictly decreases $n$, so the algorithm terminates, and by (1) the word it produces is the only one.
:::

The hypothesis "complete residue system" guarantees existence of a last digit at every step; it does not guarantee *termination* or *uniqueness*.

::: counterexample {#neg:residue title="A complete residue system need not give unique numerals" status="counterexample" ledger="GIN-NEG-014"}
For $b = 2$ and $D = \{-1, 2\}$ (a complete residue system modulo $2$), the non-empty word $(-1)(2)$ denotes $2 \cdot (-1) + 2 = 0$. Prefixes denoting zero are then not just runs of a zero digit, and uniqueness fails.
:::

## Bijective numeration: no zero digit {#sec:bijective}

Bijective base $b$ uses the digits $1, \ldots, b$ and no zero. Its words are in one-to-one correspondence with the natural numbers: there are no leading zeros to strip, and no two words share a value. Bijective base $1$ is unary, with the single digit "$1$", that is, the successor move. Bijective base $26$ with digits `A`–`Z` is the column-naming scheme of spreadsheets: `A`, …, `Z`, `AA`, `AB`, …, where `Z` is the digit $26$ and `AA` $= 26 \cdot 1 + 1 = 27$. The scheme was studied as "$k$-adic" notation by Smullyan \cite{smullyan1961} and proposed as a practical alternative by Forslund \cite{forslund1995}.

```python run
from ginsdk.numerals import bijective

b2 = bijective(2)
print("n :", " ".join(f"{n:>4d}" for n in range(9)))
print("w :", " ".join(f"{b2.render(b2.address(n)):>4s}" for n in range(9)))
cols = bijective(26)
letters = {d: chr(64 + d) for d in range(1, 27)}
for n in (1, 26, 27, 52, 702, 703, 16384):
    print(f"spreadsheet column {n:>5d} = {''.join(letters[d] for d in cols.address(n))}")
```

```output
n :    0    1    2    3    4    5    6    7    8
w :    ε    1    2   11   12   21   22  111  112
spreadsheet column     1 = A
spreadsheet column    26 = Z
spreadsheet column    27 = AA
spreadsheet column    52 = AZ
spreadsheet column   702 = ZZ
spreadsheet column   703 = AAA
spreadsheet column 16384 = XFD
```

In bijective notation zero is written only as the empty word. The convention problem of Chapter 5 disappears: there is no `0` digit, so there is nothing to be mistaken for a spelling of the empty address. The price is that the familiar shortcuts change: in bijective base $10$, the number ten is written with a single digit (the digit "ten", often written `A`), and multiplying by the base is no longer "append a zero".

## Naming the negative numbers {#sec:negative}

Standard positional notation names only natural numbers; a minus sign is an extra symbol outside the digit grammar. Two classical digit grammars name every integer with digits alone.

**Balanced ternary** uses base $3$ and digits $-1, 0, 1$, written `T`, `0`, `1`. By Proposition \ref{prop:residue-systems} every integer has a unique numeral without leading zeros. Negation is digit-wise: swap `1` and `T`. The Soviet Setun computer (1958) used balanced ternary arithmetic.

**Base $-2$** ("negabinary") uses digits $0, 1$ and the negative base $-2$. The residue algorithm still applies — the last digit is $n \bmod 2$ and the prefix denotes $(n - d)/(-2)$ — and the magnitude of the state strictly decreases once $|n| \ge 2$, so every integer has a unique finite numeral \cite{knuth1997}.

```python run
from ginsdk.numerals import BALANCED_TERNARY as B3, NEGABINARY as NB

for n in (-6, -1, 0, 1, 5, 13):
    print(f"{n:>3d}:  balanced ternary {B3.render(B3.address(n)):>5s}    base -2 {NB.render(NB.address(n)):>6s}")
```

```output
 -6:  balanced ternary   T10    base -2   1110
 -1:  balanced ternary     T    base -2     11
  0:  balanced ternary     ε    base -2      ε
  1:  balanced ternary     1    base -2      1
  5:  balanced ternary   1TT    base -2    101
 13:  balanced ternary   111    base -2  11101
```

Ordinary binary, by contrast, cannot name $-1$ in finitely many digits. Running the residue algorithm on $-1$ gives the digit $1$ and the new state $(-1 - 1)/2 = -1$: the algorithm never stops, and produces the infinite word $\ldots 1111$. Chapter 21 shows that this infinite word is the $2$-adic expansion of $-1$, and that a computer's 32-bit representation of $-1$ is its last thirty-two digits (\ledger{GIN-PROP-008}).

## Redundant digits {#sec:redundant}

What if the digit set has *more* digits than residues? Take base $2$ with digits $\{0, 1, 2\}$. Now $2 = 10_2 = 2_2$ (the one-digit word "2"), and $4 = 100 = 20 = 12$. Numerals are no longer unique, even without leading zeros. How many are there?

::: proposition {#prop:hyperbinary title="Hyperbinary representations are counted by Stern's sequence" status="reproduced" ledger="GIN-PROP-054"}
The number of words over $\{0, 1, 2\}$ without leading zero whose base-$2$ value is $n$ equals $s(n+1)$, where $s$ is Stern's diatomic sequence: $s(0) = 0$, $s(1) = 1$, $s(2k) = s(k)$, $s(2k+1) = s(k) + s(k+1)$. (Classical; see Calkin and Wilf \cite{calkinwilf2000}.) Reproduced here by exhaustive enumeration for $n < 60$.
:::

::: proof
Let $h(n)$ be the count, with $h(0) = 1$ (the empty word). A word for $2k+1$ must end in the digit $1$, and its prefix is any word for $k$: $h(2k+1) = h(k)$. A word for $2k + 2$ ends in $0$ (prefix for $k + 1$) or in $2$ (prefix for $k$): $h(2k+2) = h(k+1) + h(k)$. The sequence $t(n) = s(n+1)$ satisfies the same recurrences, $t(2k+1) = s(2k+2) = s(k+1) = t(k)$ and $t(2k+2) = s(2k+3) = s(k+1) + s(k+2) = t(k) + t(k+1)$, with $t(0) = 1$; so $h = t$.
:::

Redundancy is usually a defect in a notation. In arithmetic hardware it is a resource. With redundant digits, the sum of two numerals can be formed *without carry propagation*: each output digit depends only on a bounded window of input digits, because a redundant digit can absorb an incoming carry without passing it on. Signed-digit representations of this kind, introduced by Avizienis \cite{avizienis1961}, are the basis of fast multipliers and dividers; the carry-save representation used inside nearly every hardware multiplier is another example. Chapter 11 shows why ordinary binary addition *must* propagate carries, and Chapter 22 returns to redundant representations in circuits.

## The heap of Computational Grammar Theory {#sec:heap}

Computational Grammar Theory numbers the nodes of a complete binary tree as in a binary heap: the root is $1$, the left child of $x$ is $2x$ and the right child is $2x + 1$ (\cgt{CGT-DEF-006}). The address of a node is the word over $\{L, R\}$ leading to it from the root; the number of the node is computed from the address by the moves $L : y \mapsto 2y$ and $R : y \mapsto 2y + 1$ — a digit grammar with base $2$, digits $0, 1$, started at $1$ instead of $0$.

::: proposition {#prop:heap title="CGT's heap numeration is bijective binary, shifted by one" status="proved-here" ledger="GIN-PROP-006"}
Let $\varphi(x) = x + 1$. The bijective base-2 grammar (digits $1, 2$; moves $x \mapsto 2x + 1$ and $x \mapsto 2x + 2$; root $0$) is conjugate by $\varphi$ to the heap grammar (moves $L : y \mapsto 2y$, $R : y \mapsto 2y + 1$; root $1$):
$$
\varphi \circ \sem{1} = L \circ \varphi, \qquad \varphi \circ \sem{2} = R \circ \varphi .
$$
Consequently the bijective base-2 numeral of $n$, with $1 \mapsto L$ and $2 \mapsto R$, is the heap address of node $n + 1$: the binary numeral of $n + 1$ with its leading $1$ removed.
:::

::: proof
$(2x + 1) + 1 = 2(x + 1)$ and $(2x + 2) + 1 = 2(x + 1) + 1$. By induction on words, $\varphi \circ \sem{w} = \sem{h(w)} \circ \varphi$ where $h$ replaces $1$ by $L$ and $2$ by $R$; evaluating at $0$ gives $\sem{w}(0) + 1 = \sem{h(w)}(1)$. Both numerations are bijections from words to their sets of values (Proposition \ref{prop:residue-systems}(3) for the first; uniqueness of tree paths for the second), so the words correspond.
:::

```python run
from ginsdk.numerals import bijective, heap_word, bijective2_as_heap

b2 = bijective(2)
for n in range(8):
    print(f"n = {n}:  bijective binary {b2.render(b2.address(n)):>4s}  ->  heap address of node {n + 1}: "
          f"{heap_word(n + 1) or 'ε':>4s}   (binary of {n + 1} = {bin(n + 1)[2:]})")
assert all(bijective2_as_heap(n) == heap_word(n + 1) for n in range(100000))
print("checked n < 100000")
```

```output
n = 0:  bijective binary    ε  ->  heap address of node 1:    ε   (binary of 1 = 1)
n = 1:  bijective binary    1  ->  heap address of node 2:    L   (binary of 2 = 10)
n = 2:  bijective binary    2  ->  heap address of node 3:    R   (binary of 3 = 11)
n = 3:  bijective binary   11  ->  heap address of node 4:   LL   (binary of 4 = 100)
n = 4:  bijective binary   12  ->  heap address of node 5:   LR   (binary of 5 = 101)
n = 5:  bijective binary   21  ->  heap address of node 6:   RL   (binary of 6 = 110)
n = 6:  bijective binary   22  ->  heap address of node 7:   RR   (binary of 7 = 111)
n = 7:  bijective binary  111  ->  heap address of node 8:  LLL   (binary of 8 = 1000)
checked n < 100000
```

The proposition is elementary and very likely folklore; the literature search recorded in the ledger did not find it stated in this form, and no priority is claimed. Its interest is as a bridge: the address insight that motivated CGT — an address carries operations, and a grammar of addresses can compute instead of store — is, for numbers, the observation that a numeral is a program.

## Numerals as compression {#sec:compression}

The unary numeral of $n$ has $n$ symbols; the binary numeral has about $\log_2 n$. In what precise sense is the second a compressed form of the first?

A **straight-line program** (SLP) is a grammar in which every nonterminal has exactly one production and there is no recursion; it generates exactly one word. For example, $A_1 \to a$, $A_2 \to A_1 A_1$, $A_3 \to A_2 A_2$, $A_4 \to A_3 A_1$ generates $a^5$ with four productions.

::: proposition {#prop:slp title="Positional numerals are straight-line programs for unary terms" status="reinterpretation" ledger="GIN-PROP-007"}
For $n \ge 1$ with a binary numeral of length $k$ and $\nu$ ones, the unary word $a^n$ has a straight-line program with $k + \nu - 1 \le 2k - 1$ productions: $A \to a$ for the leading bit; then, for each later bit, a doubling production $A' \to AA$, followed for a bit $1$ by $A'' \to A' a$. The program has exactly the shape of left-to-right binary exponentiation of $x^n$: $k - 1$ squarings and $\nu - 1$ multiplications (\ledger{GIN-PROP-041}). Conversely, an SLP of size $m$ for $a^n$ yields an addition chain for $n$ of length at most $m$ \cite{charikar2005,knuth1997}.
:::

::: proof
Horner's rule for the binary numeral maps the current length $\ell$ to $2\ell + \beta$ for each bit $\beta$. Doubling a length is concatenating a word with itself; adding one is appending a letter. Counting the productions gives $1 + (k - 1) + (\nu - 1)$.
:::

In CGT's vocabulary, this is the mechanism of *sharing* (M-SHARE, \cgt{CGT-DEF-009}) applied to the successor grammar: positional notation is exponential compression of unary numerals, achieved by reusing a subterm instead of repeating it. Three classical objects turn out to be one: the binary numeral of $n$, the square-and-multiply program for $x^n$, and a small grammar for $a^n$. The shortest such programs are the *shortest addition chains*, whose length is not known in closed form; computing a shortest addition chain is a hard problem in its own right \cite{knuth1997}.

::: exercise {#ex:dg-bij}
Write $100$ in bijective base $10$ (use `A` for the digit ten). Why does it have only two digits?
:::

::: solution {of="ex:dg-bij"}
Residue algorithm: $100 \equiv 10$, digit `A`, next state $(100 - 10)/10 = 9$; digit `9`, next $0$. So `9A`: $9 \cdot 10 + 10 = 100$. Two digits suffice because the largest two-digit bijective numeral is `AA` $= 110$.
:::

::: exercise {#ex:dg-neg}
Convert $-7$ to base $-2$ by the residue algorithm, showing the states.
:::

::: solution {of="ex:dg-neg"}
$-7$: digit $1$ (since $-7$ is odd), next $(-7 - 1)/(-2) = 4$; $4$: digit $0$, next $-2$; $-2$: digit $0$, next $1$; $1$: digit $1$, next $0$. Reading backwards: `1001`$_{-2} = -8 + 1 = -7$.
:::

::: exercise {#ex:dg-hyper}
List all hyperbinary representations of $6$ and check the count against $s(7)$.
:::

::: solution {of="ex:dg-hyper"}
`110`, `102`, `22`: three words. $s(7) = s(3) + s(4) = 2 + 1 = 3$.
:::

::: exercise {#ex:dg-slp}
Give the straight-line program of Proposition \ref{prop:slp} for $a^{13}$ and the corresponding square-and-multiply sequence for $x^{13}$.
:::

::: solution {of="ex:dg-slp"}
$13 = 1101_2$: $A_1 \to a$; bit 1: $A_2 \to A_1 A_1$, $A_3 \to A_2 a$ ($a^3$); bit 0: $A_4 \to A_3 A_3$ ($a^6$); bit 1: $A_5 \to A_4 A_4$, $A_6 \to A_5 a$ ($a^{13}$). Six productions $= k + \nu - 1 = 4 + 3 - 1$. Exponentiation: $x$, $x^2$, $x^3$, $x^6$, $x^{12}$, $x^{13}$: three squarings and two multiplications.
:::

::: exercise {#ex:dg-heap}
Which heap node has address `RLR`? What is its bijective base-2 numeral, shifted by one?
:::

::: solution {of="ex:dg-heap"}
From the root $1$: $R \to 3$, $L \to 6$, $R \to 13$. Node $13$; the bijective base-2 numeral of $12$ is `212` ($2\cdot4 + 1\cdot2 + 2 = 12$), which maps to `RLR`.
:::

::: summary
- Complete residue digit sets let the residue algorithm compute numerals; termination and uniqueness need more (counterexample $D = \{-1, 2\}$).
- Bijective numeration has no zero digit and is a bijection from words to $\N$; balanced ternary and base $-2$ name every integer without a sign.
- Redundant digits make numerals non-unique — hyperbinary representations are counted by Stern's sequence — and make carry-free addition possible.
- CGT's heap numeration is bijective binary shifted by one: an address grammar is a numeral system.
- Positional notation is a straight-line-program compression of unary, with the shape of exponentiation by squaring.
:::
