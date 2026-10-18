---
title: "$1 + 1 = 10_2$: Value and Representation"
status: mixed
statusnote: All the mathematics is classical; the exact flip count is elementary and checked here; the representation trade-off table is a reinterpretation.
description: Why the value stays fixed while its numeral changes; binary addition and the cost of the successor in bits; properties of values versus properties of numerals; divisibility as a finite automaton; periodic expansions of rationals; and representations as trade-offs between operations.
epigraph: "1 + 1 = 2 and 1 + 1 = 10₂ are the same equation. What differs is not the arithmetic but the alphabet in which its answer is spelled."
---

::: objectives
- Parse $1 + 1 = 10_2$ precisely and explain why it states the same fact as $1 + 1 = 2$.
- Perform binary addition with carries, and count exactly the bit flips needed to count from $0$ to $N$.
- Distinguish properties of a value ("is even", "is divisible by 3") from properties of a numeral ("ends in 0", "has digit sum 9"), and know when one can be read off the other.
- Build the finite automaton that decides divisibility by $m$ from a base-$b$ numeral.
- Explain why $1/3$ and $1/10$ have infinite expansions in some bases and finite ones in others.
- Compare representations — positional, prime-factorization, residue — by which operations they make cheap.
:::

## Reading the equation {#sec:reading}

The sentence $1 + 1 = 10_2$ has three parts. The left side, $1 + 1$, is an expression whose numerals are single digits; the digit `1` denotes the same value in every base $b \ge 2$, so the left side has no base to speak of. The right side, $10_2$, is the base-2 numeral with digits $1, 0$, whose value is $1 \cdot 2 + 0 = 2$. The equals sign asserts that the two sides denote the same *value*. The sentence is therefore the claim
$$
\val_{10}(1) + \val_{10}(1) = \val_2(10),
$$
which is true because both sides equal the natural number $2$. Nothing about addition changed when the base changed. What changed is the *word* used to spell the answer.

This is easy to say and easy to forget. "In binary, one plus one is ten" sounds like a different arithmetic; it is the same arithmetic in a different spelling, and "ten" there is a misreading of the word `10` as if it were decimal. The value is the invariant; the representation is the variable. This chapter is about what changes with the representation, and what does not.

## Binary addition, and the carry it generates {#sec:binary-add}

Binary addition follows the same column algorithm as decimal addition, with a smaller table. For two bits and an incoming carry, the sum bit is their parity and the outgoing carry is $1$ when at least two of the three are $1$:

| $a_i$ | $b_i$ | carry in | sum bit | carry out |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 | 1 |

(The other four rows follow by symmetry.) The case $1 + 1$ is the third row: sum bit $0$, carry $1$. The answer *needs one more position* than either operand: `1` and `1` are one-digit words, `10` is a two-digit word. Nothing of the sort happens in base $10$, where $1 + 1 = 2$ fits in one digit. *Whether an operation generates a carry depends on the base*, although the value does not.

The same phenomenon, iterated, governs counting. Adding $1$ to $0111_2$ turns three trailing ones into zeros and one zero into a one: four bits change to produce $1000_2$. How much does counting cost in bit flips?

::: proposition {#prop:counter title="The cost of the successor in binary" status="proved-here" ledger="GIN-PROP-010"}
Counting from $0$ to $N$ in binary flips exactly $2N - \popcount(N)$ bits in total, where $\popcount(N)$ is the number of ones in the binary numeral of $N$. The successor therefore costs fewer than $2$ bit flips on average, and $\lfloor \log_2 N \rfloor + 1$ in the worst case, at $N = 2^k - 1 \to 2^k$.
:::

::: proof
The increment $x \to x + 1$ turns the $t(x)$ trailing ones of $x$ into zeros and the zero above them into a one: it flips $t(x) + 1$ bits and changes the popcount by $1 - t(x)$. Summing over $x = 0, \ldots, N - 1$, the flips are $\sum (t(x) + 1) = \sum \bigl(2 - (1 - t(x))\bigr) = 2N - (\popcount(N) - \popcount(0)) = 2N - \popcount(N)$.
:::

The amortized bound is textbook material \cite{clrs2009}; the exact closed form is elementary. The SDK confirms it by counting:

```python run
total, worst = 0, (0, 0)
for x in range(1 << 16):
    flips = bin(x ^ (x + 1)).count("1")
    total += flips
    worst = max(worst, (flips, x))
N = 1 << 16
print("flips counting 0 ->", N, ":", total, "  formula 2N - popcount(N):", 2 * N - bin(N).count("1"))
print("average per increment:", total / N, "  worst:", worst[0], "flips at", worst[1], "->", worst[1] + 1)
```

```output
flips counting 0 -> 65536 : 131071   formula 2N - popcount(N): 131071
average per increment: 1.9999847412109375   worst: 17 flips at 65535 -> 65536
```

## Properties of values, properties of numerals {#sec:properties}

Some properties belong to a value and can be stated without any numeral: "$n$ is even", "$n$ is prime", "$n$ is a perfect square". Others belong to a numeral: "ends in the digit 0", "has digit sum 9", "is a palindrome". The two kinds are easily confused because, *in a fixed base*, some numeral properties detect value properties:

- in base $10$, "ends in 0, 2, 4, 6 or 8" detects evenness, because $10$ is even and the last digit is the residue modulo $10$;
- in base $10$, "digit sum divisible by 3" detects divisibility by 3, because $10 \equiv 1 \pmod 3$, so $\val(d_1 \cdots d_k) \equiv d_1 + \cdots + d_k$;
- in base $2$, "ends in 0" detects evenness; "digit sum divisible by 3" does *not* detect divisibility by 3 ($2 \not\equiv 1 \pmod 3$); instead the *alternating* digit sum does, because $2 \equiv -1 \pmod 3$.

Palindromicity, by contrast, is not a property of any value: $5 = 101_2$ is a palindrome in binary and not in base $3$ ($12_3$). "Is a palindrome" is a property of words that happens to be readable as a relation between a value and a base.

### Divisibility is a finite automaton

For any base and any modulus, divisibility can be decided by reading the numeral once, from the left, while remembering only a residue.

::: proposition {#prop:div-automaton title="Divisibility automata" status="classical" ledger="GIN-PROP-055"}
For a base $b \ge 2$ and a modulus $m \ge 1$, the deterministic automaton with states $\{0, \ldots, m-1\}$, start state $0$, transition $r \xrightarrow{d} (b r + d) \bmod m$ and accepting state $0$ accepts exactly the base-$b$ words whose value is divisible by $m$. The language of base-$b$ numerals of multiples of $m$ is therefore regular, recognized with at most $m$ states.
:::

::: proof
By Horner's rule, after reading a prefix $u$ the automaton is in the state $\val(u) \bmod m$: the transition applies the digit move $x \mapsto bx + d$ modulo $m$, and reduction modulo $m$ commutes with it. The word is accepted iff $\val(w) \bmod m = 0$.
:::

This is the digit-move reading of Chapter 5 at work: the automaton is the digit grammar *reduced modulo $m$*. Its states are the finitely many residues, so it is finite; its transitions are the digit moves, so it reads numerals as programs. Chapter 11 shows that addition is also a finite automaton, and that multiplication is not (\ledger{GIN-THM-005}).

```python run
def accepts(word, b, m):
    r = 0
    for ch in word:
        r = (b * r + int(ch, b)) % m
    return r == 0

for n in [0, 3, 21, 22, 1023]:
    w = bin(n)[2:]
    print(f"{n:5d} = {w:>10s}_2   divisible by 3: {accepts(w, 2, 3)!s:5s}  "
          f"alternating digit sum: {sum((-1) ** i * int(d) for i, d in enumerate(reversed(w)))}")
bad = sum(accepts(format(n, 'b'), 2, m) != (n % m == 0) for n in range(4000) for m in range(1, 20))
print("checked n < 4000, m < 20, base 2:", bad, "disagreements")
```

```output
    0 =          0_2   divisible by 3: True   alternating digit sum: 0
    3 =         11_2   divisible by 3: True   alternating digit sum: 0
   21 =      10101_2   divisible by 3: True   alternating digit sum: 3
   22 =      10110_2   divisible by 3: False  alternating digit sum: 1
 1023 = 1111111111_2   divisible by 3: True   alternating digit sum: 0
checked n < 4000, m < 20, base 2: 0 disagreements
```

## Rationals: when expansions stop {#sec:rationals}

A rational number has a positional expansion too, with digits after a radix point. Long division produces it, and long division is itself a small transition system.

::: proposition {#prop:periodic title="Long division is a finite transition system" status="classical" ledger="GIN-PROP-009"}
Expanding $p/q$ ($0 \le p < q$, lowest terms) in base $b$ runs the transition system on remainders $r \mapsto (b r) \bmod q$, emitting the digit $\lfloor b r / q \rfloor$ at each step, starting from $r = p$. The expansion terminates if and only if every prime factor of $q$ divides $b$; otherwise it is eventually periodic with period at most $q - 1$.
:::

::: proof
The state space $\{0, \ldots, q - 1\}$ is finite, so every trajectory is eventually periodic. The expansion terminates iff the trajectory reaches $0$, iff $p/q = m/b^k$ for some integers $m$, $k$, iff $q \mid b^k$ (since $\gcd(p, q) = 1$), iff every prime factor of $q$ divides $b$. A periodic trajectory avoids $0$, so its cycle has at most $q - 1$ states.
:::

So $1/3 = 0.\overline{3}$ in base $10$ but $1/3 = 0.1$ in base $3$; and $1/10 = 0.1$ in base $10$ but in base $2$
$$
\frac{1}{10} = 0.0\overline{0011}_2,
$$
an infinite expansion, because $5$ divides $10$ but not $2$. This single fact is why the decimal literal `0.1` is not exactly representable in any binary floating-point format, and why $0.1 + 0.2 \neq 0.3$ in binary64 arithmetic (\chapref{25-floating-point}).

```python run
from fractions import Fraction
from ginsdk.numerals import periodic_expansion

for q in (Fraction(1, 3), Fraction(1, 10), Fraction(1, 7), Fraction(3, 8)):
    print(f"{str(q):5s} base 10: {periodic_expansion(q, 10):12s} base 2: {periodic_expansion(q, 2):22s} base 3: {periodic_expansion(q, 3)}")
```

```output
1/3   base 10: 0.(3)        base 2: 0.(01)                 base 3: 0.1
1/10  base 10: 0.1          base 2: 0.0(0011)              base 3: 0.(0022)
1/7   base 10: 0.(142857)   base 2: 0.(001)                base 3: 0.(010212)
3/8   base 10: 0.375        base 2: 0.011                  base 3: 0.(10)
```

Whether a number has a *finite* numeral is a property of the pair (number, base), not of the number alone: $3/8$ terminates in bases $2$ and $10$ but not in base $3$; $1/3$ terminates only in bases divisible by $3$. Irrational numbers have no finite or periodic numeral in any integer base — a fact that sets the limit of every finite representation of the real numbers (\chapref{28-reals-complex}).

## Representations are trade-offs {#sec:tradeoffs}

If the value is invariant, why choose one representation over another? Because each representation makes some operations cheap and others expensive. Positional notation is not the only choice; it is the choice that balances the operations people use most.

::: proposition {#prop:rep-tradeoff title="Representations trade operations against each other" status="reinterpretation" ledger="GIN-REI-011"}
For integers of $L$ bits, the following representations are each exact and complete, and their costs (in bit operations, for the stated operations) differ as shown:

| representation | addition | multiplication | comparison | divisibility by a fixed prime $p$ |
|---|---|---|---|---|
| unary | $\Theta(2^L)$ | $\Theta(4^L)$ | $\Theta(2^L)$ | $\Theta(2^L)$ |
| positional (binary) | $\Theta(L)$ | $\Oh(L \log L)$ | $\Theta(L)$ | $\Theta(L)$ |
| prime-exponent vector | no known polynomial method (requires factoring the sum) | add exponents: cheap | requires conversion | read one exponent |
| residues modulo coprime $m_1, \ldots, m_k$ (CRT) | digit-wise, carry-free | digit-wise, carry-free | requires reconstruction (mixed-radix conversion) | depends on whether $p$ is among the moduli |

All entries are classical facts about algorithms; the table is a reinterpretation of them as properties of grammars.
:::

The residue representation deserves a word. By the Chinese remainder theorem (\chapref{31-congruences}), an integer in $[0, M)$ with $M = m_1 \cdots m_k$ is determined by its residues modulo pairwise coprime $m_i$. In that representation addition and multiplication act independently on each residue — there is no carry between "digits" at all — but comparing two numbers or detecting overflow requires reconstructing them. Residue number systems are used in some signal processing and cryptographic hardware precisely for the carry-free operations, and avoided elsewhere precisely for the expensive comparison. No representation is free; each moves the cost somewhere else.

::: exercise {#ex:vr-parse}
Parse each statement and decide whether it is true: (a) $10_2 + 10_2 = 100_2$; (b) $10 + 10 = 100$ in base 10; (c) $11_3 = 100_2$; (d) "$7$ is a palindrome" .
:::

::: solution {of="ex:vr-parse"}
(a) True: $2 + 2 = 4$. (b) False: $10 + 10 = 20$; the equation holds in base $2$ only, read as (a). (c) True: $3 + 1 = 4 = 4$. (d) Ill-posed: palindromicity is a property of numerals; $7 = 111_2$ is a binary palindrome and $7 = 21_3$ is not a ternary one.
:::

::: exercise {#ex:vr-flips}
How many bit flips does counting from $0$ to $1000$ take? From $0$ to $1024$?
:::

::: solution {of="ex:vr-flips"}
$1000 = 1111101000_2$ has popcount $6$: $2000 - 6 = 1994$. $1024 = 2^{10}$ has popcount $1$: $2048 - 1 = 2047$.
:::

::: exercise {#ex:vr-div7}
Draw (or tabulate) the divisibility-by-7 automaton for base 10 and run it on `1001`.
:::

::: solution {of="ex:vr-div7"}
Transitions $r \xrightarrow{d} (10r + d) \bmod 7$. On `1001`: $0 \xrightarrow{1} 1 \xrightarrow{0} 3 \xrightarrow{0} 2 \xrightarrow{1} 0$. Accepted: $1001 = 7 \cdot 143$.
:::

::: exercise {#ex:vr-terminate}
In which integer bases $b$ between $2$ and $30$ does $1/12$ have a finite expansion?
:::

::: solution {of="ex:vr-terminate"}
$12 = 2^2 \cdot 3$, so exactly when both $2$ and $3$ divide $b$: $b \in \{6, 12, 18, 24, 30\}$.
:::

::: exercise {#ex:vr-rns}
Represent $17$ and $23$ by their residues modulo $(3, 5, 7)$, add and multiply them residue-wise, and reconstruct the results. Which reconstruction is correct, and why does the other fail?
:::

::: solution {of="ex:vr-rns"}
$17 \mapsto (2, 2, 3)$, $23 \mapsto (2, 3, 2)$. Sum: $(1, 0, 5)$, which reconstructs to $40$ — correct, since $40 < 105$. Product: $(1, 1, 6)$, which reconstructs to $76$; but $17 \cdot 23 = 391 \equiv 76 \pmod{105}$. The product exceeds the range $[0, 105)$ and wraps around; residue arithmetic is arithmetic modulo $M = 105$, and detecting the overflow requires a comparison the representation does not make cheap.
:::

::: summary
- $1 + 1 = 10_2$ and $1 + 1 = 2$ state the same equality of values; only the spelling of the answer differs.
- Binary $1 + 1$ generates a carry; counting to $N$ flips exactly $2N - \popcount(N)$ bits.
- Value properties and numeral properties differ; some numeral properties detect value properties only in suitable bases.
- Divisibility by $m$ is decided by an $m$-state automaton reading the numeral; long division is a finite transition system, so rationals have eventually periodic expansions, terminating iff the denominator's primes divide the base.
- Representations trade operations: positional notation is a compromise, not the only exact choice.
:::
