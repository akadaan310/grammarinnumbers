---
title: "Positional Notation as an Operational Grammar"
status: mixed
statusnote: Positional numeration is classical; reading numerals as words of affine moves, canonical numerals as addresses, and zero's address as the empty word is this book's packaging.
description: Place value as a grammar of digit moves x ↦ b·x + d; value, Horner's rule, canonical numerals and leading zeros; zero's address is the empty word; the length of a numeral against the size of its value; numerals compiled to affine maps.
epigraph: "A numeral is a program. Its digits are instructions; its value is what the program computes when started at zero."
---

::: objectives
- Define a digit grammar and the value of a numeral, and evaluate a numeral by Horner's rule.
- Prove that two standard numerals have the same value exactly when they differ by leading zeros, and count the words that denote a given number.
- Explain why the canonical numeral of zero is the empty word and what the written `0` therefore is.
- Relate the length of a numeral to the size of its value: $\lfloor \log_b n \rfloor + 1$ digits.
- Compile a numeral to an affine map and use the concatenation law $\val(uv) = \val(u)\, b^{|v|} + \val(v)$.
:::

## Digits as moves {#sec:moves}

The decimal numeral `427` is usually explained as $4 \cdot 100 + 2 \cdot 10 + 7$. There is another reading, which is the one this book uses: `427` is a *sequence of three instructions*, executed from left to right on a register that starts at zero. The instruction for a digit $d$ is "multiply by ten and add $d$":

$$
0 \xrightarrow{\ 4\ } 4 \xrightarrow{\ 2\ } 42 \xrightarrow{\ 7\ } 427 .
$$

Each digit is a *move*, the numeral is a *word* of moves, and its value is the state reached from $0$.

::: definition {#def:digit-grammar title="Digit grammar" status="definition" ledger="GIN-DEF-005"}
A **digit grammar** is a pair $(b, D)$ of a base $b \ge 1$ and a finite set $D \subset \Z$ of digits. Each digit $d \in D$ is a move on the integers,
$$
\sem{d} : x \mapsto b \cdot x + d, \label{eq:digit-move}
$$
the start state is $0$, and the admissible words are $D^*$ (or a sublanguage of canonical words). **Standard base $b$** has $b \ge 2$ and $D = \{0, \ldots, b-1\}$. Bijective base $b$, balanced ternary and redundant systems are other choices of $D$ (\chapref{06-digit-grammars}).
:::

::: definition {#def:numeral-value title="Value of a numeral" status="definition" ledger="GIN-DEF-006"}
The **value** of a word $w = d_1 d_2 \cdots d_k$ (most significant digit first) is
$$
\val(w) = \sem{w}(0) = \sum_{i=1}^{k} d_i\, b^{\,k-i}, \label{eq:val}
$$
where $\sem{w} = \sem{d_k} \circ \cdots \circ \sem{d_1}$. Evaluating $\sem{w}$ from left to right is **Horner's rule**.
:::

The two expressions in \eqref{eq:val} — the composite of moves and the sum of digit-times-power — are equal by an easy induction, and both are classical. The move reading, however, makes three things visible that the sum hides. It explains why the *last* digit of a numeral is the residue of the value modulo $b$ (the last move adds it after the final multiplication). It explains why appending a digit multiplies the value by $b$ and adds the digit — the basis of every conversion algorithm. And it turns a numeral into a program, so that questions about numerals become questions about programs: which programs compute the same value, which is shortest, and what does running one cost.

```python run
from ginsdk.numerals import standard

dec = standard(10)
w = dec.parse("427")
x = 0
for d in w:
    y = 10 * x + d
    print(f"digit {d}:  x = 10 * {x} + {d} = {y}")
    x = y
print("value:", dec.denote(w), "  last digit = value mod 10:", dec.denote(w) % 10 == w[-1])
```

```output
digit 4:  x = 10 * 0 + 4 = 4
digit 2:  x = 10 * 4 + 2 = 42
digit 7:  x = 10 * 42 + 7 = 427
value: 427   last digit = value mod 10: True
```

## Many words, one value {#sec:many-words}

The value map $\val$ goes from words to numbers. It is not injective: `7`, `07` and `007` all denote seven. Exactly how non-injective is it?

::: proposition {#prop:numeral-number title="Numeral ≠ number" status="classical" ledger="GIN-PROP-001"}
For standard base $b \ge 2$, the value map $\val : \{0, \ldots, b-1\}^* \to \N$ is surjective, and $\val(u) = \val(v)$ if and only if $u$ and $v$ differ only by leading zeros. Consequently, for $n \ge 1$ with canonical numeral of length $\ell$, exactly $L - \ell + 1$ words of length at most $L$ denote $n$ (for $L \ge \ell$).
:::

::: proof
Leading zeros do not change the value, because $\sem{0}(0) = b \cdot 0 + 0 = 0$, so $\sem{0w}(0) = \sem{w}(0)$. Conversely, let $u$ and $v$ have no leading zeros and $\val(u) = \val(v) = n$. If $n = 0$ both are empty: a non-empty word without a leading zero has value at least $b^{|w|-1} \ge 1$. Otherwise $b^{|u| - 1} \le n < b^{|u|}$, and likewise for $v$, so $|u| = |v|$. The last digits of both are $n \bmod b$, and deleting them leaves two words of the same value $(n - n \bmod b)/b$; by induction on the length they are equal. Surjectivity is the **residue algorithm**: for $n > 0$ emit $d = n \bmod b$ and continue with $(n - d)/b < n$; it stops at $0$ and, read backwards, gives a word of value $n$. The count: the words of length at most $L$ denoting $n$ are $0^j \addr(n)$ for $j = 0, \ldots, L - \ell$.
:::

Exhaustive enumeration agrees:

```python run
from ginsdk.numerals import standard

g = standard(3)
for n in (0, 1, 5, 9):
    words = g.words_denoting(n, 4)
    print(f"n = {n}: {len(words)} ternary words of length <= 4:", ", ".join(g.render(w) for w in words))
```

```output
n = 0: 5 ternary words of length <= 4: ε, 0, 00, 000, 0000
n = 1: 4 ternary words of length <= 4: 1, 01, 001, 0001
n = 5: 3 ternary words of length <= 4: 12, 012, 0012
n = 9: 2 ternary words of length <= 4: 100, 0100
```

## Canonical numerals and zero's empty address {#sec:canonical}

Among the many words that denote a number, one is singled out as *the* numeral.

::: definition {#def:canonical title="Canonical numeral (address)" status="definition" ledger="GIN-DEF-007"}
The **canonical numeral** $\addr(n)$ of a value $n$ in a digit grammar is the shortlex-least word $w$ with $\sem{w}(0) = n$, when one exists. In standard base $b$ it is the ordinary numeral without leading zeros.
:::

The word *address* is deliberate. In Computational Grammar Theory, the address of an element of a structure is the shortlex-least word of moves that reaches it from the root (\cgt{CGT-DEF-006}); a canonical numeral is exactly the address of a number in the structure whose moves are the digits. The grammar of positional notation *is* an address grammar. For numbers, the founding observation of CGT — that an address can carry the operations needed to compute with the element it names — is the familiar fact that one computes with numbers by manipulating their numerals.

Apply Definition \ref{def:canonical} to the number zero and something curious appears.

::: proposition {#prop:zero-address title="Zero's canonical numeral is the empty word" status="reinterpretation" ledger="GIN-PROP-002"}
In every digit grammar, $\addr(0) = \varepsilon$. In standard base $b$ the words denoting $0$ are exactly $\varepsilon, 0, 00, 000, \ldots$, and the written numeral `0` is the shortest *non-empty* one — a conventional, non-canonical spelling of the empty address.
:::

::: proof
$\varepsilon$ is the shortlex-least of all words and $\sem{\varepsilon}(0) = 0$. The second claim is Proposition \ref{prop:numeral-number} with $n = 0$.
:::

Why, then, do we write `0`? Because an empty word cannot be seen. The zero digit has two distinct jobs in positional notation, and the grammar separates them:

1. a **placeholder inside** numerals: `101` and `11` are different numerals because the middle `0` performs a move — multiply by the base, add nothing;
2. a **visible spelling** of the empty address: the numeral `0` is "do nothing", written down.

Historically, the first job came before the second: late Babylonian sexagesimal texts used a placeholder sign inside numerals long before zero was treated as a number in its own right \cite{kaplan1999}; zero as a number with its own arithmetic is documented in Brahmagupta's *Brāhmasphuṭasiddhānta* of 628 CE \cite{mactutor_brahmagupta} (\chapref{20-zero-and-one}). The grammar shows why the two jobs could be separated: one is a move, the other is the absence of moves.

## Length and size {#sec:length}

A numeral is short when its value is small, and its length grows like the logarithm of its value.

::: proposition {#prop:numeral-length title="The length of a canonical numeral" status="classical" ledger="GIN-PROP-053"}
For $b \ge 2$ and $n \ge 1$, the canonical base-$b$ numeral of $n$ has exactly $\lfloor \log_b n \rfloor + 1$ digits. In particular a number with a $k$-digit binary numeral satisfies $2^{k-1} \le n < 2^k$, and the binary numeral is $\log_2 10 \approx 3.32$ times as long as the decimal one, up to one digit.
:::

::: proof
A canonical word of length $\ell \ge 1$ has a non-zero leading digit, so its value lies in $[b^{\ell - 1}, b^{\ell})$, and every integer in that interval has such a word. Hence $\ell - 1 \le \log_b n < \ell$, that is, $\ell = \lfloor \log_b n \rfloor + 1$. The ratio of lengths is $\log_2 n / \log_{10} n = \log_2 10$ up to the floors.
:::

The proposition is elementary, but it is the hinge on which every cost statement in this book turns. Algorithms on numbers take as input numerals, not numbers, and the *size of the input* is the length of the numeral: $\Theta(\log n)$, not $n$. An algorithm that takes $n$ steps on input $n$ — counting up, trial division to $n$, unary arithmetic — is *exponential* in its input size. This is why Chapter 4's unary addition was so expensive, and why, in Part XIII, "trial division is slow" is a precise statement.

## Compiling a numeral {#sec:compile}

Since every digit move is an affine map $x \mapsto bx + d$, and affine maps are closed under composition, a whole numeral compiles to a single affine map.

::: proposition {#prop:compile title="Compilation and the concatenation law" status="classical" ledger="GIN-PROP-005"}
For a digit grammar $(b, D)$ and words $u, v$:
$$
\sem{w} = \bigl(x \mapsto b^{|w|} x + \val(w)\bigr), \qquad \sem{uv} = \sem{v} \circ \sem{u}, \qquad \val(uv) = \val(u)\, b^{|v|} + \val(v). \label{eq:concat}
$$
The transition monoid of the grammar is $\{x \mapsto b^k x + c\}$.
:::

::: proof
Induction on $|w|$, using $(x \mapsto bx + d) \circ (x \mapsto b^k x + c) = (x \mapsto b^{k+1} x + (bc + d))$.
:::

The concatenation law is used every day without being named: `42` followed by `7` is $42 \cdot 10 + 7$; `427` followed by `000` is $427 \cdot 10^3$. It is also the basis of fast conversion: to evaluate a long numeral, split it into halves, evaluate each, and combine with \eqref{eq:concat} — an idea measured in \chapref{37-measured-complexity}.

```python run
from ginsdk.numerals import standard

dec = standard(10)
f = dec.compile(dec.parse("427"))
print("427 compiles to", f, "   applied to 0:", f(0), "  applied to 1:", f(1))
u, v = dec.parse("42"), dec.parse("7")
print("val(42 . 7) =", dec.denote(u) * 10 ** len(v) + dec.denote(v))
```

```output
427 compiles to x ↦ 1000·x + 427    applied to 0: 427   applied to 1: 1427
val(42 . 7) = 427
```

Applying the compiled map to $1$ instead of $0$ gives $1427$: running the program `427` after the program `1`. Numerals compose like programs because they are programs.

::: remark
CGT calls a structure *arithmetically compilable* when every word of moves compiles to an element of its transition monoid that fits in $\Oh(1)$ machine words (\cgt{CGT-DEF-011}). Positional numerals are *not* compilable in that sense for unbounded words: the compiled pair $(b^{|w|}, \val(w))$ has $\Theta(|w|)$ bits. The grammar compiles, but the compiled object grows with the program. Chapter 11 contrasts this with the carry automaton of binary addition, whose transition monoid has only three elements.
:::

## Conversion between bases {#sec:conversion}

Since the value is the invariant and the numeral is a representation, converting a numeral from base $b$ to base $b'$ means: compute the value from the base-$b$ word (Horner's rule in base $b$), then compute the base-$b'$ word of the value (the residue algorithm in base $b'$). The SDK's `canonicalize` and `convert` do exactly this, and report leading zeros instead of silently dropping them:

```python run
from ginsdk.numerals import canonicalize, convert

print(canonicalize("000427"))
for text, b1, b2 in [("427", 10, 2), ("110101011", 2, 10), ("ff", 16, 2), ("0", 10, 2)]:
    print(f"{text} (base {b1}) = {convert(text, b1, b2)} (base {b2})")
```

```output
{'input': '000427', 'base': 10, 'value': 427, 'canonical': '427', 'address': '427', 'was_canonical': False, 'leading_zeros': 3, 'note': '3 leading zero(s) removed; leading zeros do not change the value (GIN-PROP-001)'}
427 (base 10) = 110101011 (base 2)
110101011 (base 2) = 427 (base 10)
ff (base 16) = 11111111 (base 2)
0 (base 10) = 0 (base 2)
```

For bases that are powers of a common base — $2$, $8$, $16$ — conversion needs no arithmetic at all: each hexadecimal digit is exactly four binary digits. For other pairs, such as $10$ and $2$, it needs genuine multiplication and division, and its cost grows faster than linearly in the length of the numeral. Python, for instance, refuses by default to convert integers of more than $4300$ decimal digits to strings, because the quadratic conversion was used for denial-of-service attacks (\ledger{GIN-OBS-014}). A change of representation is a computation, with a cost, and sometimes with a limit.

::: exercise {#ex:pos-horner}
Evaluate the base-7 numeral `2304` by Horner's rule, showing each state, and check the result against \eqref{eq:val}.
:::

::: solution {of="ex:pos-horner"}
States $0 \to 2 \to 17 \to 119 \to 837$: $7 \cdot 0 + 2 = 2$, $7 \cdot 2 + 3 = 17$, $7 \cdot 17 + 0 = 119$, $7 \cdot 119 + 4 = 837$. Sum: $2 \cdot 343 + 3 \cdot 49 + 0 \cdot 7 + 4 = 686 + 147 + 4 = 837$.
:::

::: exercise {#ex:pos-count}
How many binary words of length at most $10$ denote the number $37$? How many words of length at most $10$ denote some number less than $37$?
:::

::: solution {of="ex:pos-count"}
$37 = 100101_2$ has length $6$, so $10 - 6 + 1 = 5$ words. Every word of length at most $10$ denotes a number below $1024$; the words denoting numbers $< 37$ are, for each $n < 37$, $10 - |\addr(n)| + 1$ words ($11$ for $n = 0$, counting $\varepsilon$). Summing: $n = 0$: 11; $n = 1$: 10; $n = 2, 3$: $9$ each; $n = 4..7$: 8 each; $8..15$: 7 each; $16..31$: 6 each; $32..36$: 5 each. Total $11 + 10 + 18 + 32 + 56 + 96 + 25 = 248$.
:::

::: exercise {#ex:pos-length}
How many decimal digits does $2^{100}$ have? How many binary digits does $10^{30}$ have?
:::

::: solution {of="ex:pos-length"}
$\lfloor 100 \log_{10} 2 \rfloor + 1 = \lfloor 30.103 \rfloor + 1 = 31$. $\lfloor 30 \log_2 10 \rfloor + 1 = \lfloor 99.66 \rfloor + 1 = 100$.
:::

::: exercise {#ex:pos-concat}
Using \eqref{eq:concat}, show that a decimal numeral is divisible by $4$ if and only if the number formed by its last two digits is.
:::

::: solution {of="ex:pos-concat"}
Write the numeral as $uv$ with $|v| = 2$. Then $\val(uv) = 100\,\val(u) + \val(v)$, and $4 \mid 100$, so $\val(uv) \equiv \val(v) \pmod 4$.
:::

::: exercise {#ex:pos-zero}
In the grammar of this chapter, what does the numeral `00` do as a program? What does it do when applied, after compilation, to the state $5$? Relate the answer to the two jobs of the zero digit.
:::

::: solution {of="ex:pos-zero"}
`00` compiles to $x \mapsto 100x$. From the state $0$ it reaches $0$: as a numeral it is a (non-canonical) spelling of zero's empty address. Applied to $5$ it gives $500$: the zeros act as placeholders, shifting the value two places. The same word performs both jobs depending on where it is run.
:::

::: summary
- A numeral is a word of digit moves $x \mapsto bx + d$; its value is the state reached from $0$, computed by Horner's rule.
- Two standard numerals have the same value iff they differ by leading zeros; the canonical numeral is the shortlex-least word — a grammatical address in the sense of CGT.
- Zero's address is the empty word; the written `0` is a convention. The zero digit is both a placeholder and a spelling of "no moves".
- A numeral of $n$ has $\lfloor\log_b n\rfloor + 1$ digits, so the size of a number as input is logarithmic in its value.
- A numeral compiles to an affine map; concatenation of numerals is composition of maps.
:::
