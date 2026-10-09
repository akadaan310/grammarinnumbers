---
title: "Subtraction and the Construction of the Integers"
status: mixed
statusnote: The construction of ℤ, column subtraction and two's-complement subtraction are classical; the saturating-monoid collapse and the borrow-bit identity are elementary and checked here.
description: Why 0 − 1 has no answer in ℕ, one in ℤ and another in hardware; the integers built from unanswered subtraction problems; why this construction needs cancellation; column subtraction with borrows; and subtraction in hardware as addition of the complement, whose carry bit answers "is a ≥ b?".
epigraph: "Asked for 0 − 1, the natural numbers have nothing to say. The integers answer −1. A 32-bit register answers 4294967295. All three are correct about their own structure."
---

::: objectives
- Classify $0 - 1$ in $\N$, $\Z$, $\Z/2^w$ and under truncated subtraction, and say what changed between them: the structure, not the operation.
- Construct $\Z$ from pairs of natural numbers, prove that the construction is well defined, and show why it requires the cancellation law.
- State the invariant of column subtraction with borrows.
- Derive hardware subtraction $a - b = a + \bar b + 1$ and prove that its carry out is the comparison $a \ge b$.
:::

## $0 - 1$ in four structures {#sec:sub-four}

Subtraction is the converse of addition: $a - b$ is the $c$ with $b + c = a$ (Chapter 9).

| structure | equation $1 + c = 0$ | outcome | what kind of answer |
|---|---|---|---|
| $\N$ | no solution: $1 + c \ge 1$ | inadmissible | none |
| $\Z$ | $c = -1$ | admissible | the converse solution, after **extension** |
| $\Z/2^w$ (unsigned machine words) | $c = 2^w - 1$ | admissible | the converse solution, after a **quotient** |
| $\N$ with truncated subtraction $\monus$ | — | $0 \monus 1 = 0$ | a **totalization**: $1 + 0 \neq 0$ |

The grammar of the operation — "the $c$ with $b + c = a$" — is the same in the first three rows. What changes is the *structure* in which the equation is solved. Extension enlarges the carrier until a solution exists; quotient identifies numbers modulo $2^w$ until one does. The fourth row changes the operation instead: $\monus$ is total on $\N$ and agrees with subtraction wherever subtraction is admissible, but at $0 \monus 1$ it returns a value that solves nothing.

::: proposition {#prop:monus title="Truncated subtraction is a totalization, not a converse" status="proved-here" ledger="GIN-PROP-016"}
$m \monus n = \max(m - n, 0)$ is total on $\N$, agrees with subtraction whenever $m \ge n$, and satisfies $(m + n) \monus n = m$; but $(m \monus n) + n = m$ fails whenever $m < n$, so $m \monus n$ is not a solution of $n + c = m$ there.
:::

::: proof
Immediate from the definition: for $m < n$, $(m \monus n) + n = n \ne m$.
:::

```python run
from ginsdk import evaluate, peano

for d in ["N", "Z", "Z/256", "Python", "int32 Java"]:
    o = evaluate("0 - 1", d)
    print(f"{d:10s} {o.status:12s} {o.display or o.reason}")
print("monus(0, 1) =", peano.monus(0, 1), "  and 1 + monus(0, 1) =", 1 + peano.monus(0, 1))
```

```output
N          no-solution  b + c ≥ b = 1 > 0 for every natural c (the only integer solution -1 is negative)
Z          value        -1
Z/256      value        255
Python     value        -1
int32 Java value        -1
monus(0, 1) = 0   and 1 + monus(0, 1) = 1
```

## The integers as answers to subtraction problems {#sec:construct-z}

How does one build a structure in which every subtraction problem has an answer, without assuming negative numbers exist? The classical answer keeps the unanswered problem as data.

::: proposition {#prop:z-construction title="The Grothendieck construction of ℤ" status="classical" ledger="GIN-PROP-017"}
On $\N \times \N$ define $(a, b) \sim (c, d) \iff a + d = b + c$. Then $\sim$ is an equivalence relation; addition $(a, b) + (c, d) = (a + c, b + d)$ and negation $-(a, b) = (b, a)$ are well defined on classes; the classes form an abelian group $\Z$ with zero $[(0, 0)]$; and $n \mapsto [(n, 0)]$ embeds $(\N, +)$ in it. In $\Z$, the class $[(a, b)]$ solves $b + c = a$.
:::

::: proof
Reflexivity and symmetry are clear. Transitivity: $a + d = b + c$ and $c + f = d + e$ give $a + d + f = b + c + f = b + d + e$, and cancelling $d$ gives $a + f = b + e$. Well-definedness of $+$: if $(a, b) \sim (a', b')$ then $(a + c) + (b' + d) = (a' + c) + (b + d)$. The inverse of $[(a, b)]$ is $[(b, a)]$ since $(a + b, b + a) \sim (0, 0)$. The embedding is injective: $(m, 0) \sim (n, 0)$ means $m + 0 = 0 + n$. Finally $[(b, 0)] + [(a, b)] = [(a + b, b)] = [(a, 0)]$.
:::

The proof of transitivity used the **cancellation law** $x + d = y + d \Rightarrow x = y$ in $\N$. That use is essential. For a commutative monoid without cancellation, the same construction (with $(a, b) \sim (c, d)$ iff $a + d + k = b + c + k$ for some $k$) still produces a group — but the map from the monoid into it can collapse elements, sometimes all of them.

::: proposition {#prop:saturating-collapse title="Adjoining negatives to saturating addition destroys it" status="proved-here" ledger="GIN-PROP-060"}
Let $M_K = \{0, 1, \ldots, K\}$ with saturating addition $x \boxplus y = \min(x + y, K)$. Every homomorphism $h$ from $(M_K, \boxplus, 0)$ to a group sends every element to the identity. In particular the group completion of saturating arithmetic is the trivial group: no structure in which saturating addition has inverses can distinguish any two values.
:::

::: proof
For every $x$, $K \boxplus x = K$, so $h(K) + h(x) = h(K)$ in the group, hence $h(x) = 0$.
:::

So the integers cannot be obtained from a machine's saturating arithmetic by "adding negatives": the information has already been destroyed. They can be obtained from wraparound arithmetic, because $\Z/2^w$ already is a group — but then they are not the integers.

## Column subtraction and the borrow {#sec:borrow}

The school algorithm for $a - b$ with $a \ge b$ mirrors column addition. Working from the least significant digit with a borrow $\beta_i \in \{0, 1\}$ ($\beta_0 = 0$): let $t = a_i - b_i - \beta_i$; if $t < 0$ write $s_i = t + b$ and borrow $\beta_{i+1} = 1$, else write $s_i = t$ and $\beta_{i+1} = 0$. The invariant is
$$
\sum_{j \le i} s_j b^j - \beta_{i+1}\, b^{i+1} = \sum_{j \le i} (a_j - b_j)\, b^j, \label{eq:borrow-inv}
$$
proved exactly like Proposition GIN-PROP-057. At the end, $\beta_n = 0$ if and only if $a \ge b$; a final borrow means that the converse problem has no solution in $\N$. The SDK's limb subtraction raises an error in precisely that case, saying so in the vocabulary of this book ("$a < b$ has no solution in N").

## Subtraction in hardware {#sec:hw-sub}

Processors do not contain a separate subtraction circuit. They add the complement.

::: proposition {#prop:hw-sub title="Subtraction as addition of the complement; the carry is the comparison" status="proved-here" ledger="GIN-PROP-061"}
For $w$-bit unsigned operands $0 \le a, b < 2^w$, let $\bar b = 2^w - 1 - b$ be the bitwise complement of $b$. Then
$$
a + \bar b + 1 = (a - b) + 2^w .
$$
Consequently the low $w$ bits of $a + \bar b + 1$ are $(a - b) \bmod 2^w$, and the carry out of the top position is $1$ exactly when $a \ge b$.
:::

::: proof
$a + (2^w - 1 - b) + 1 = a - b + 2^w$. If $a \ge b$, this is in $[2^w, 2^{w+1})$: carry $1$, low bits $a - b$. If $a < b$, it is in $[0, 2^w)$: carry $0$, low bits $a - b + 2^w = (a - b) \bmod 2^w$.
:::

The carry out, which addition uses to signal overflow, becomes in subtraction a "no borrow" flag: the hardware answer to the question "does $b + c = a$ have a solution in $\N$?". Instruction sets differ in how they expose it — x86 sets its carry flag to the *borrow* (the complement of this carry), while ARM sets it to the carry itself — another case of one mathematical fact with two machine encodings. The SDK's gate-level subtractor implements the proposition and is checked exhaustively:

```python run
from ginsdk import circuits as K

n = 6
c = K.subtractor(n)
bad = 0
for a in range(2 ** n):
    for b in range(2 ** n):
        out = K.apply_words(c, a=(a, n), b=(b, n))
        value = sum(bit << i for i, bit in enumerate(out[:n]))
        bad += value != (a - b) % 2 ** n or out[n] != (a >= b)
print(f"{n}-bit subtractor: {c.size} gates, depth {c.depth()}; {4 ** n} cases, {bad} errors")
```

```output
6-bit subtractor: 36 gates, depth 14; 4096 cases, 0 errors
```

## Signed subtraction and its overflow {#sec:signed-sub}

In two's complement the same circuit subtracts signed numbers: the bit patterns of $a - b \bmod 2^w$ are the same whether the operands are read as signed or unsigned (Chapter 21). What differs is the overflow condition. Unsigned subtraction overflows ("borrows") when $a < b$; signed subtraction overflows when the exact difference leaves $[-2^{w-1}, 2^{w-1})$, which happens exactly when the operands have different signs and the result's sign differs from $a$'s. The expression $-2147483647 - 2$ in 32-bit arithmetic has the exact value $-2147483649$, one below the range; wraparound gives $2147483647$, ISO C declares it undefined, Rust's debug build panics. These are the execution-layer outcomes of a subtraction that is perfectly admissible in $\Z$.

::: exercise {#ex:sub-z-classes}
Which pairs in $\N^2$ represent the integer $-3$? Show that $[(2, 5)] + [(7, 1)] = [(3, 0)]$ directly from the definitions.
:::

::: solution {of="ex:sub-z-classes"}
The pairs $(a, a + 3)$, $a \in \N$. $(2, 5) + (7, 1) = (9, 6) \sim (3, 0)$ because $9 + 0 = 6 + 3$.
:::

::: exercise {#ex:sub-monus-laws}
Which of these hold for all $m, n, p \in \N$? (a) $(m \monus n) \monus p = m \monus (n + p)$; (b) $m \monus (n \monus p) = (m \monus n) + p$; (c) $m \monus m = 0$.
:::

::: solution {of="ex:sub-monus-laws"}
(a) True: both are $\max(m - n - p, 0)$. (b) False: $m = 0, n = 1, p = 1$ gives $0$ on the left and $1$ on the right. (c) True.
:::

::: exercise {#ex:sub-flag}
Using Proposition \ref{prop:hw-sub}, compute the 8-bit result and carry for $a = 5$, $b = 9$. What does the result mean as a signed number?
:::

::: solution {of="ex:sub-flag"}
$\bar b = 246$, $5 + 246 + 1 = 252 < 256$: carry $0$ (so $a < b$), result $252$, which as a signed 8-bit number is $252 - 256 = -4 = 5 - 9$.
:::

::: exercise {#ex:sub-collapse}
Find a commutative monoid that is not cancellative but whose group completion is not trivial.
:::

::: solution {of="ex:sub-collapse"}
$(\N \times \{0, 1\}, +)$ with second coordinate under $\max$: $(m, a) + (n, b) = (m + n, \max(a, b))$. It is not cancellative ($(0,1) + (0,0) = (0,1) + (0,1)$) and its completion is $\Z$ (the first coordinate survives, the second collapses).
:::

::: summary
- $0 - 1$ has no solution in $\N$, the solution $-1$ in $\Z$ (extension), $2^w - 1$ in $\Z/2^w$ (quotient); truncated subtraction gives $0$ without solving anything (totalization).
- $\Z$ is built from pairs $(a, b)$ standing for "$a - b$"; the construction needs cancellation, and saturating addition, which lacks it, collapses completely.
- Column subtraction tracks a borrow with an invariant; a final borrow signals that the converse problem has no natural solution.
- Hardware computes $a - b$ as $a + \bar b + 1$; the carry out is the comparison $a \ge b$.
:::
