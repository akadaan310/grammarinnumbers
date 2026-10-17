---
title: "Numerical Grammar and Computational Grammar Theory"
status: mixed
statusnote: The correspondences are stated precisely and checked by computation; CGT is cited as a separate, read-only publication. Exact correspondences, refinements and non-equivalences are kept in separate sections.
description: A formal map from this book to Computational Grammar Theory — which CGT concepts apply to numbers unchanged, which need refinement, which have no arithmetic counterpart, and what arithmetic exposes that CGT had not isolated — with every correspondence checked or cited.
epigraph: "A correspondence is a claim; an analogy is a mood."
---

::: objectives
- State which definitions of Computational Grammar Theory (CGT) apply to numbers without change, and check the exact correspondences by computation.
- Identify the CGT notions that arithmetic refines: the number of evaluation layers, converse moves, and the growing parameter of cost.
- State the non-equivalences precisely, including a CGT property that digit grammars do *not* have.
- Distinguish exact correspondences from analogies, and know which proposals to CGT are only proposals.
:::

## Two publications {#sec:two}

Computational Grammar Theory, the research program of Abed Kadan, asks when the grammar of a computational structure — its moves, admissible operation sequences, semantics and costs — becomes part of the machinery that computes over it \cite{cgt2026}. This book was written afterwards and is, conceptually, its arithmetic prequel: numbers are the simplest structures on which CGT's questions can be asked. The two are independent. Each has its own ledger and software; no result here depends on a CGT result; CGT was read, never modified, and its identifiers below link to the separate CGT publication (\ledger{GIN-D-002}).

This chapter has three sections, and an item appears in only one of them: **exact correspondences** (a CGT definition instantiated on numbers, with a proof or check), **refinements** (a CGT notion that numbers force to change), and **non-equivalences** (where an apparent correspondence fails). Analogies that are none of these are not listed.

## Exact correspondences {#sec:exact}

**Numerals are operation expressions.** CGT defines an operational grammar as moves with a relational semantics on a structure and an admissibility language (\cgt{CGT-DEF-003}). A digit grammar with base $b$ and digit set $D$ is one: the structure is $\Z$, the moves are $x \mapsto bx + d$, and a numeral is a word over the moves whose value is its denotation at $0$ (Chapter 6). The CGT distinction between syntax and semantics *is* the distinction between numeral and number.

**Canonical numerals are grammatical addresses.** CGT's address of an element is the shortlex-least word reaching it from the root (\cgt{CGT-DEF-006}). For a standard digit grammar rooted at $0$ the address of $n$ is its numeral without leading zeros, and the address of $0$ is the empty word (\ledger{GIN-PROP-002}).

**CGT's heap numeration is bijective binary, shifted.** CGT studies the heap numbering of binary trees — root $1$, children $2x$ and $2x+1$ — as its main example of arithmetic addressing (\cgt{CGT-THM-003}, \cgt{CGT-THM-006}). The map $x \mapsto x + 1$ conjugates the bijective base-2 grammar (digits $1, 2$, root $0$) to it (\ledger{GIN-PROP-006}):

```python run
from ginsdk import numerals as N

pairs = [(n, N.bijective(2).render(N.bijective(2).address(n)), N.heap_word(n + 1)) for n in range(1, 9)]
for n, bij, heap in pairs:
    print(f"n = {n}: bijective binary {bij:4s}  heap address of node {n + 1}: {heap}")
print("conjugacy holds for all n < 100000:", all(N.bijective2_as_heap(n) == N.heap_word(n + 1) for n in range(100000)))
```

```output
n = 1: bijective binary 1     heap address of node 2: L
n = 2: bijective binary 2     heap address of node 3: R
n = 3: bijective binary 11    heap address of node 4: LL
n = 4: bijective binary 12    heap address of node 5: LR
n = 5: bijective binary 21    heap address of node 6: RL
n = 6: bijective binary 22    heap address of node 7: RR
n = 7: bijective binary 111   heap address of node 8: LLL
n = 8: bijective binary 112   heap address of node 9: LLR
conjugacy holds for all n < 100000: True
```

**The carry automaton is arithmetically compilable.** CGT calls a grammar *arithmetically compilable* when every word of moves compiles to one element of a class of $\Oh(1)$-word operations closed under composition (\cgt{CGT-DEF-011}). The carry automaton of binary addition has the three-element transition monoid $\{\Kk, \Pp, \Gg\}$ (\ledger{GIN-PROP-020}): every word of digit pairs compiles to one of three elements, and parallel prefix adders compute those compilations (Chapter 11).

**Same semantics, different shape, different cost.** CGT's theorem that grammar shape trades work against parallel depth (\cgt{CGT-THM-004}) has two exact arithmetic instances: ripple-carry versus prefix adders (\ledger{GIN-PROP-021}, Chapter 22) and Horner versus balanced numeral evaluation (Chapter 37).

## Refinements {#sec:refinements}

**Four layers, not three.** CGT separates syntax, semantics and execution (\cgt{CGT-PROP-002}). Arithmetic needs a fourth, *typing*, between syntax and semantics: the literal `0.5` in $\Z$ and the literal `2147483648` in a 32-bit integer domain are syntactically well formed and fail before any operation is applied. The four layers are independent (\ledger{GIN-PROP-056}).

**Converse moves.** CGT's relational semantics allows a move to have no result or several. Arithmetic singles out a systematic source of both: every inverse operation is the converse of a forward one, and its admissibility is decided by the size of a solution set — none, one or many (Chapter 9; \ledger{GIN-THM-007}). CGT has no separate notion of a converse move; the book proposes one (below), and does not claim CGT needs it.

**The growing parameter of cost.** CGT's cost profiles use the word RAM with $w = \Theta(\log n)$ for structure size $n$ (\cgt{CGT-DEF-005}). For arithmetic the growing parameter is the *bit length of the operands*, and unit cost is admissible only while operands fit in a word (Chapter 36). The CGT bound "arithmetic addressing is $\Oh(1)$ only while the address fits in a word" (\cgt{CGT-THM-003}) is the arithmetic statement that $L$-bit numbers cost $\lceil L/w \rceil$ words.

## Non-equivalences {#sec:non-equivalences}

**Digit grammars are not arithmetically compilable.** A word of digit moves compiles to the affine map $x \mapsto b^{k}x + c$ (\ledger{GIN-PROP-005}) — one element, closed under composition, as CGT-DEF-011 requires — but the element is not $\Oh(1)$ words: its coefficients grow with the word.

```python run
from ginsdk import numerals as N

g = N.DECIMAL
for k in (4, 16, 64, 256):
    f = g.compile(g.parse("7" * k))
    print(f"word of {k:3d} digits compiles to x -> a*x + c with a of {f.a.bit_length():4d} bits and c of {f.c.bit_length():4d} bits")
```

```output
word of   4 digits compiles to x -> a*x + c with a of   14 bits and c of   13 bits
word of  16 digits compiles to x -> a*x + c with a of   54 bits and c of   53 bits
word of  64 digits compiles to x -> a*x + c with a of  213 bits and c of  213 bits
word of 256 digits compiles to x -> a*x + c with a of  851 bits and c of  851 bits
```

The carry monoid has three elements; the affine monoid of a digit grammar is infinite. That difference is the difference between an operation a finite automaton can perform on numerals (addition) and one it cannot (multiplication; \ledger{GIN-THM-005}, \cite{buchi1960,cobham1969}). It is the sharpest single statement this book has found connecting a CGT property to a classical boundary.

**No arithmetic counterpart.** CGT's material on PageRank, retrieval and AI-system grammars has no counterpart here beyond fixed-point iteration, and CGT's boundary result that grammars cannot move problems across complexity classes (\cgt{CGT-PROP-006}) has no arithmetic refinement in this book: nothing here bears on the complexity of factoring or discrete logarithms (Chapters 31 and 35).

**Analogies that are not correspondences.** The book sometimes uses CGT words informally — "the exponent is a program" (Chapter 34), "long division is a transition system" — and in those places the precise statement is the proposition cited next to the phrase, not the phrase. Such phrases are explanatory; the correspondences in \ref{sec:exact} are the claims.

## Proposals to CGT {#sec:proposals}

These are proposals for the CGT researcher, not changes made to CGT:

1. add a notion of *converse move* and the none/one/many classification of its admissibility;
2. add a typing layer to the three-layer model;
3. consider re-association as a sixth mechanism of computational advantage, alongside CGT's five (\cgt{CGT-DEF-009}); whether it is distinct from the grammar-shape effect is open (\ledger{GIN-CONJ-001}, \ledger{GIN-OPEN-004});
4. record the heap conjugacy (\ledger{GIN-PROP-006}) next to CGT's heap numeration.

::: exercise {#ex:cgt-address}
For the balanced-ternary digit grammar (digits $-1, 0, 1$), what is the CGT address of $-4$, and why does the address of every integer exist?
:::

::: solution {of="ex:cgt-address"}
By the residue algorithm: $-4 \equiv -1 \pmod 3$, so the last digit is $-1$ and the state becomes $(-4 + 1)/3 = -1$; then the digit is $-1$ again and the state becomes $0$. The address is `TT` (writing T for $-1$): $(-1) \cdot 3 + (-1) = -4$. Every integer has one because the residue algorithm strictly decreases $|n|$ (\ledger{GIN-PROP-004}).
:::

::: exercise {#ex:cgt-compile}
Show that the words over the digit moves of base $b$ that compile to maps with $a = b^k$ for a *fixed* $k$ form a finite set, and explain why that does not make the grammar arithmetically compilable.
:::

::: summary
- Exact correspondences: numerals are CGT operation expressions; canonical numerals are CGT addresses; CGT's heap numeration is bijective binary shifted by one (checked for $n < 100000$); the carry automaton is arithmetically compilable; adders and numeral evaluation instantiate CGT's shape theorem.
- Refinements: a fourth (typing) layer; converse moves with none/one/many admissibility; bit length as the growing parameter of cost.
- Non-equivalences: digit grammars compile to single affine maps whose size grows with the word — finite versus infinite transition monoids separate addition from multiplication; CGT's PageRank and complexity-class material has no arithmetic counterpart here.
- Proposals to CGT are proposals; CGT is cited, not modified.
:::
