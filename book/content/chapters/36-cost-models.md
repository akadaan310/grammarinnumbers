---
title: "Three Cost Models, Kept Apart"
status: mixed
statusnote: The models and bounds are classical; the unit-cost counterexample is classical folklore; the table of non-equivalences and its executed checks are this book's.
description: Unit-cost arithmetic, the word RAM and bit complexity, each stated with what grows and what is held fixed; how the same algorithm has different costs in each; the classical pathology of unit-cost multiplication; and the rule this book follows when it reports a cost.
epigraph: "“Addition takes one step” is true, false, or meaningless, depending on what is allowed to grow."
---

::: objectives
- Define the unit-cost model, the word RAM and the bit-complexity model, naming in each what grows and what is fixed.
- Translate a cost statement between models, and recognize when the translation fails.
- Explain why unit-cost multiplication on unbounded integers is not a reasonable model, with an explicit computation.
- Use the lower bounds proved earlier in the book (linear time and logarithmic depth for addition) to anchor the models.
- Apply the reporting rule that every cost in this book names its model and its growing parameter.
:::

## Why a cost needs a model {#sec:why-model}

Chapters 10 to 19 gave many costs: addition in $\Theta(L)$ bit operations, schoolbook multiplication in $\Theta(L^2)$, Euclid's algorithm in $\Oh(L)$ steps and $\Oh(L^2)$ bit operations, modular exponentiation in $\Theta(L^3)$. Each is true in one model and false or meaningless in others. The three models below are classical \cite{knuth1997,clrs2009}; what this chapter adds is the discipline of never mixing them silently.

::: definition {#def:cost-models title="Three cost models for arithmetic" status="definition" ledger="GIN-DEF-097"}
1. **Unit cost.** Each arithmetic operation on numbers costs $1$, whatever the numbers. The growing parameter is the number of operations. Admissible only when every operand is bounded by a fixed constant — and then it is the word RAM with a fixed word.
2. **Word RAM.** Numbers are stored in $w$-bit words; an operation on one or two words costs $1$; the model assumes $w \ge \log_2 n$ for an input of size $n$, so that a word can hold an index into the input. An $L$-bit number occupies $\lceil L/w \rceil$ words, and operations on it cost what the limb algorithms of Chapter 15 charge.
3. **Bit complexity.** Each operation on bits costs $1$ (Boolean circuits, or a Turing machine's steps). The growing parameter is the bit length $L$ of the operands. This is the model in which "$\Theta(L^2)$ for schoolbook multiplication" is a theorem.
:::

The counted limb operations of the SDK (Chapter 37) are the word RAM with $w = 32$: they become bit costs up to the constant factor $w$, and unit costs only while every operand fits in one limb.

## One algorithm, three costs {#sec:three-costs}

| task | unit cost | word RAM ($L$-bit operands, $w$-bit words) | bit complexity |
|---|---|---|---|
| add two numbers | $1$ | $\lceil L/w \rceil$ | $\Theta(L)$ (\ledger{GIN-PROP-058}) |
| multiply (schoolbook) | $1$ | $\Theta((L/w)^2)$ | $\Theta(L^2)$ |
| multiply (Karatsuba) | $1$ | $\Theta((L/w)^{\log_2 3})$ | $\Theta(L^{\log_2 3})$ (\ledger{GIN-PROP-063}) |
| gcd by Euclid | $\Oh(L)$ divisions | $\Oh(L^2/w)$ | $\Oh(L^2)$ (\ledger{GIN-HIST-017}) |
| $x^e \bmod n$ | $\Oh(\log e)$ | $\Oh(L (L/w)^2)$ | $\Theta(L^3)$ schoolbook |
| $x^e$ over $\Z$ | $\Oh(\log e)$ | $\ge e L / w$ (writing the output) | $\ge e L$ |
| add, as a circuit | — | — | depth $\ge 1 + \log_2 L$ (\ledger{GIN-PROP-059}) |

Two rows deserve emphasis. The last-but-one shows unit cost *undercounting by an exponential factor*: $\Oh(\log e)$ multiplications produce a number with about $e L$ bits, which no machine can even write in fewer than $eL$ bit steps. The gcd row shows that "the number of steps" is not a cost in any model until the cost of a step is fixed.

## The pathology of unit-cost multiplication {#sec:unit-pathology}

::: counterexample {#cex:unit-cost title="Unit-cost multiplication computes doubly exponential numbers in linear time" status="counterexample" ledger="GIN-NEG-025"}
Starting from $2$, $k$ squarings compute $2^{2^k}$, a number with $2^k + 1$ bits. Under unit cost this takes $k$ steps; in any model where a step reads and writes a bounded number of bits it takes at least $2^k$ steps. A model in which multiplication of unbounded integers costs $1$ can therefore "compute" objects whose mere description is exponentially longer than the computation, which is why the word RAM bounds the word size by $\Oh(\log n)$ \cite{clrs2009}.
:::

```python run
from ginsdk import bigint as B
from ginsdk.cost import Cost

x = B.from_int(2)
for k in range(1, 13):
    c = Cost()
    x = B.mul_school(x, x, c)
    print(f"square #{k:2d}: unit cost 1, value 2^(2^{k}) has {B.to_int(x).bit_length():5d} bits, limb operations for this square: {B.word_ops(c)}")
```

```output
square # 1: unit cost 1, value 2^(2^1) has     3 bits, limb operations for this square: 2
square # 2: unit cost 1, value 2^(2^2) has     5 bits, limb operations for this square: 2
square # 3: unit cost 1, value 2^(2^3) has     9 bits, limb operations for this square: 2
square # 4: unit cost 1, value 2^(2^4) has    17 bits, limb operations for this square: 2
square # 5: unit cost 1, value 2^(2^5) has    33 bits, limb operations for this square: 2
square # 6: unit cost 1, value 2^(2^6) has    65 bits, limb operations for this square: 8
square # 7: unit cost 1, value 2^(2^7) has   129 bits, limb operations for this square: 18
square # 8: unit cost 1, value 2^(2^8) has   257 bits, limb operations for this square: 50
square # 9: unit cost 1, value 2^(2^9) has   513 bits, limb operations for this square: 162
square #10: unit cost 1, value 2^(2^10) has  1025 bits, limb operations for this square: 578
square #11: unit cost 1, value 2^(2^11) has  2049 bits, limb operations for this square: 2178
square #12: unit cost 1, value 2^(2^12) has  4097 bits, limb operations for this square: 8450
```

Each squaring costs one unit. The limb work is constant while the value fits in one 32-bit limb, and then grows by a factor approaching $4$ per step, because the operand doubles in length and schoolbook multiplication is quadratic. After twelve unit steps the value has $4097$ bits.

## Floating point: unit cost of a different operation {#sec:fp-unit}

Floating-point arithmetic restores unit cost honestly by changing the *operation*: a binary64 multiplication costs one instruction because it computes the product rounded to $53$ significant bits, not the product (Chapter 25; \cite{goldberg1991}). A cost statement "multiplication is $\Oh(1)$" about floating point is therefore a statement about $\fl(x \cdot y)$, and an algorithm analysed this way must also be analysed for rounding error. The cost model and the semantic layer cannot be separated: cheaper here means *different*.

```python run
from ginsdk import evaluate

for e in ["9007199254740992 + 1", "(10000000000000000 + 1) - 10000000000000000", "0.1 * 3", "1 / 3 * 3"]:
    print(f"{e:44s}  Q: {evaluate(e, 'Q').display:18s} binary64: {evaluate(e, 'binary64').display or evaluate(e, 'binary64').status}")
```

```output
9007199254740992 + 1                          Q: 9007199254740993   binary64: 9007199254740992
(10000000000000000 + 1) - 10000000000000000   Q: 1                  binary64: 0
0.1 * 3                                       Q: 3/10               binary64: 0.30000000000000004
1 / 3 * 3                                     Q: 1                  binary64: 1
```

The second line loses the $1$ entirely: $10^{16} + 1$ is not a binary64 number, so it rounds to $10^{16}$ before the subtraction. The last line shows the opposite accident — $\fl(\fl(1/3) \cdot 3)$ rounds back to exactly $1$ — and is no evidence of exactness: correct answers produced by cancelling rounding errors are still produced by a different operation.

## Translating between models {#sec:translate}

Two rules suffice for every translation in this book:

1. **Word RAM to bit complexity**: multiply by the cost of a word operation — $\Oh(w)$ for addition, $\Oh(w^2)$ for schoolbook word multiplication, or $\Oh(1)$ if words are treated as hardware.
2. **Unit cost to word RAM**: valid only when every intermediate value fits in $\Oh(1)$ words. The operation counts of Chapters 33–35 (division steps, squarings) are unit-cost counts; their word-RAM costs require the operand lengths, which is why each of those chapters states both.

The translation fails in exactly the situations the earlier chapters measured: operands that grow (exponentiation over $\Z$, Peano arithmetic in Chapter 4, the doubly exponential squarings above); and operations whose unit-cost version computes something else (floating point, wraparound integers).

::: demo cost
Text alternative: choose an operation and a bit length; the widget plots the counted 32-bit limb operations from the book's experiment GIN-EXP-008 against the bit length on logarithmic axes, with the fitted slope, and states the model ("word RAM, w = 32") under the chart.
:::

## The reporting rule {#sec:reporting-rule}

Every cost in this book is reported with (i) the model, (ii) the growing parameter and what is held fixed, (iii) whether it is a bound, an exact count or a measurement. "Addition is $\Oh(1)$" is reported as "one instruction for operands of at most $64$ bits"; "addition is $\Theta(L)$" as "bit operations, $L$ the operand length". The rule is not decoration: Chapter 4 showed a factor-$2^k$ difference hiding behind "addition takes one step", and the pathology above an exponential one.

::: exercise {#ex:cost-matmul}
Under unit cost, an $n \times n$ integer matrix product takes $n^3$ operations. Give its word-RAM cost if all entries have $L$ bits, and explain why entries of the $k$-th power of the matrix may not have $L$ bits.
:::

::: solution {of="ex:cost-matmul"}
$n^3$ products of $L$-bit numbers and sums of $n$ terms: $\Oh(n^3 (L/w)^2 + n^3 L/w)$ with schoolbook multiplication. Entries of $A^k$ can grow to about $k(L + \log_2 n)$ bits, so the cost of later products grows with $k$ — the unit-cost count $kn^3$ is not a word-RAM bound.
:::

::: exercise {#ex:cost-sieve}
Restate the cost of the sieve of Eratosthenes (Chapter 35) in bit complexity, as a function of the number of digits of $N$.
:::

::: solution {of="ex:cost-sieve"}
With $L = \log_2 N$, the sieve performs $\Theta(N \log \log N) = \Theta(2^L \log L)$ crossings, each on an index of $L$ bits: exponential in $L$. It is polynomial only in $N$ itself — the classic distinction between pseudo-polynomial and polynomial time.
:::

::: summary
- Unit cost, word RAM and bit complexity differ in what grows; every cost names its model and its growing parameter.
- Unit cost is valid only for bounded operands; unbounded unit-cost multiplication computes $2^{2^k}$ in $k$ steps, a number of $2^k + 1$ bits (executed).
- The word RAM ($w \ge \log n$) is the model of the SDK's counted limb operations; bit complexity is the model of the book's theorems.
- Floating point has unit cost because it computes a rounded result: cost and semantics change together.
- Step counts (divisions, squarings) become costs only with the operand lengths.
:::
