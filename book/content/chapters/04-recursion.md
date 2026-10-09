---
title: "Recursion, Induction, and the Cost of Counting"
status: mixed
statusnote: Induction, recursion and the Peano laws are classical; the exact rule counts are elementary and checked here against actual derivations.
description: Induction and recursion as the two faces of the successor grammar; arithmetic defined by primitive recursion and executed by term rewriting with counted steps; numbers as iterators; ℕ as a least fixed point; and why unary arithmetic is exponentially expensive.
epigraph: "To define a function on the natural numbers, say what it does at 0 and what one more step does. To prove a property, say why it holds at 0 and why one more step preserves it."
---

::: objectives
- State the induction principle and the recursion theorem, and explain why they are two consequences of the same axiom.
- Define addition, multiplication and exponentiation by primitive recursion, and compute $1 + 1 = 2$ as a two-step derivation.
- Prove commutativity and associativity of addition from the recursive definitions.
- Count the rule applications of Peano arithmetic exactly, and explain why unary arithmetic is exponential in the length of a binary numeral.
- Read a number as an iterator (a Church numeral), and the set $\N$ as a least fixed point.
:::

## Induction and recursion {#sec:ind-rec}

The last clause of the definition of $\N$ (Definition GIN-DEF-001) says that the only subset of $\N$ containing $0$ and closed under $S$ is $\N$ itself. Read as a principle of proof, this is **induction**: to show that every natural number has a property $\Phi$, show $\Phi(0)$, and show that $\Phi(n)$ implies $\Phi(S n)$; then the set of numbers with the property contains $0$ and is closed under $S$, so it is everything.

Read as a principle of *definition*, the same clause gives recursion.

::: theorem {#thm:recursion title="The recursion theorem" status="classical" ledger="GIN-HIST-003"}
Let $X$ be a set, $x_0 \in X$ and $g : \N \times X \to X$. There is exactly one function $f : \N \to X$ with
$$
f(0) = x_0, \qquad f(S n) = g(n, f(n)) \quad \text{for all } n. \label{eq:rec}
$$
:::

::: proof
*Uniqueness.* If $f$ and $f'$ both satisfy \eqref{eq:rec}, the set where they agree contains $0$ and is closed under $S$; by induction it is $\N$. *Existence.* Call a relation $R \subseteq \N \times X$ *admissible* if $(0, x_0) \in R$ and $(n, y) \in R$ implies $(S n, g(n, y)) \in R$. The intersection $F$ of all admissible relations is admissible. One shows by induction on $n$ that for each $n$ there is exactly one $y$ with $(n, y) \in F$ (if there were two values at $S n$, removing the one not of the form $g(n, y)$ would leave an admissible relation, contradicting minimality; injectivity of $S$ and $0 \notin S(\N)$ ensure that the clauses never collide). So $F$ is the graph of a function, and it satisfies \eqref{eq:rec}.
:::

The proof uses all three axioms: induction (for uniqueness and the final argument), injectivity of $S$ and $0 \notin S(\N)$ (so that the two defining clauses never assign two values to the same argument). The fixed-width structure of Proposition GIN-PROP-052 fails the last axiom, and recursion fails with it: on a cycle of length $2^w$, the "definition" $f(0) = 0$, $f(S n) = f(n) + 1$ would require $f(0) = f(S(2^w - 1)) = 2^w$, a contradiction. One cannot define functions by counting up on a machine word and expect them to be well defined across the seam.

## Arithmetic by primitive recursion {#sec:primrec}

::: definition {#def:primrec title="Primitive recursion on the successor grammar" status="definition" ledger="GIN-DEF-010"}
$$
\begin{aligned}
\mathrm{add}(m, 0) &= m, & \mathrm{add}(m, S n) &= S(\mathrm{add}(m, n)),\\
\mathrm{mul}(m, 0) &= 0, & \mathrm{mul}(m, S n) &= \mathrm{add}(\mathrm{mul}(m, n), m),\\
\mathrm{pow}(m, 0) &= S 0, & \mathrm{pow}(m, S n) &= \mathrm{mul}(\mathrm{pow}(m, n), m),\\
\mathrm{pred}(0) &= 0, & \mathrm{pred}(S n) &= n,\\
\mathrm{monus}(m, 0) &= m, & \mathrm{monus}(m, S n) &= \mathrm{pred}(\mathrm{monus}(m, n)).
\end{aligned}
$$
Each is an instance of the recursion theorem in the second argument. The **cost** of a computation is the number of equations applied (rule applications).
:::

With these definitions, $1 + 1 = 2$ is not a fact to be memorized but a derivation of two steps:

$$
\mathrm{add}(S0, S0) \;=\; S(\mathrm{add}(S0, 0)) \;=\; S(S0).
$$

The SDK performs such derivations by literal term rewriting, and records each rule it uses:

```python run
from ginsdk import peano as P

nf, trace = P.rewrite(("add", P.num(1), P.num(1)))
for rule, term in trace:
    print(f"{rule:30s} -> {term}")
nf, trace = P.rewrite(("mul", P.num(2), P.num(3)))
print("2 x 3:", P.show(nf), "after", len(trace), "rule applications")
```

```output
add(m, S n) = S(add(m, n))     -> S(add(S0, 0))
add(m, 0) = m                  -> SS0
2 x 3: SSSSSS0 after 13 rule applications
```

Note that the definition of $\mathrm{pred}$ sets $\mathrm{pred}(0) = 0$. This is not a solution of $S(c) = 0$ — there is none — but a *choice*: it makes $\mathrm{pred}$ total. The same choice propagates into $\mathrm{monus}$, so that $\mathrm{monus}(0, 1) = 0$ although no $c$ satisfies $1 + c = 0$. Chapter 13 calls this a *totalization* and compares it with the other ways of making a partial operation total.

## The laws, proved from the definitions {#sec:laws}

Everybody knows that $a + b = b + a$. In the grammar of primitive recursion it is not obvious at all: $\mathrm{add}(m, n)$ recurses on its *second* argument, and the two sides of $a + b = b + a$ are computed by different derivations of different lengths. The law is a theorem about the *values* of the derivations.

::: proposition {#prop:add-laws title="Associativity and commutativity of addition" status="classical" ledger="GIN-HIST-004"}
For all $a, b, c \in \N$: (i) $0 + a = a$; (ii) $S a + b = S(a + b)$; (iii) $a + b = b + a$; (iv) $(a + b) + c = a + (b + c)$.
:::

::: proof
(i) Induction on $a$: $0 + 0 = 0$ by the first equation; if $0 + a = a$ then $0 + S a = S(0 + a) = S a$. (ii) Induction on $b$: $S a + 0 = S a = S(a + 0)$; if $S a + b = S(a + b)$ then $S a + S b = S(S a + b) = S(S(a + b)) = S(a + S b)$. (iii) Induction on $b$: $a + 0 = a = 0 + a$ by (i); if $a + b = b + a$ then $a + S b = S(a + b) = S(b + a) = S b + a$ by (ii). (iv) Induction on $c$: $(a + b) + 0 = a + b = a + (b + 0)$; and $(a + b) + S c = S((a + b) + c) = S(a + (b + c)) = a + S(b + c) = a + (b + S c)$.
:::

The proofs are short, but each uses the *structure* of the grammar — what happens at $0$ and what one more step does — and not any picture of objects being combined. The corresponding laws for multiplication, and distributivity, are proved the same way (Exercise \ref{ex:rec-distrib}).

::: remark
The proofs show something the notation hides: *commutativity is not computational symmetry*. The derivation of $2 + 3$ applies four rules and that of $3 + 2$ three; they reach the same normal form. The equation $2 + 3 = 3 + 2$ asserts that two different computations have the same result. This is the first instance of a theme of the book: an algebraic law is a statement that different evaluation paths agree, and the cost of the paths may differ. Chapter 37 measures how much.
:::

## The cost of counting {#sec:cost}

How expensive is arithmetic in this grammar?

::: proposition {#prop:peano-cost title="The cost of Peano arithmetic" status="proved-here" ledger="GIN-PROP-003"}
Under the definitions of GIN-DEF-010, $\mathrm{add}(m, n)$ uses exactly $n + 1$ rule applications and $\mathrm{mul}(m, n)$ uses exactly $mn + 2n + 1$. Hence on inputs whose binary numerals have $k$ bits, unary addition costs $\Theta(2^k)$ rule applications, against $\Theta(k)$ bit operations for binary addition: it is exponential in the length of the numeral.
:::

::: proof
Addition peels one $S$ from the second argument per step and finishes with the base equation: $n + 1$ steps. Multiplication: $\mathrm{mul}(m, 0)$ costs $1$; $\mathrm{mul}(m, S n)$ costs one rule, then $\mathrm{mul}(m, n)$, then an addition with second argument $m$, which costs $m + 1$. By induction the total is $1 + (mn + 2n + 1) + (m + 1) = m(n + 1) + 2(n + 1) + 1$.
:::

The derivations of the SDK confirm the formula — not by evaluating it, but by counting the steps of actual rewriting, for all $m, n < 7$ in the SDK's tests and on a larger range here:

```python run
from ginsdk import peano as P

bad = 0
for m in range(12):
    for n in range(12):
        _, trace = P.rewrite(("mul", P.num(m), P.num(n)))
        bad += len(trace) != m * n + 2 * n + 1
print("pairs checked:", 144, " mismatches:", bad)
for k in (4, 8, 12, 16, 20):
    n = 2 ** k - 1
    print(f"k = {k:2d} bits: unary addition of n = {n:>7d} takes {n + 1:>7d} rules; binary addition ~ {k + 1} bit steps")
```

```output
pairs checked: 144  mismatches: 0
k =  4 bits: unary addition of n =      15 takes      16 rules; binary addition ~ 5 bit steps
k =  8 bits: unary addition of n =     255 takes     256 rules; binary addition ~ 9 bit steps
k = 12 bits: unary addition of n =    4095 takes    4096 rules; binary addition ~ 13 bit steps
k = 16 bits: unary addition of n =   65535 takes   65536 rules; binary addition ~ 17 bit steps
k = 20 bits: unary addition of n = 1048575 takes 1048576 rules; binary addition ~ 21 bit steps
```

::: implementation {#imp:rewrite title="Rule counts witnessed by rewriting" status="implementation" ledger="GIN-IMP-004"}
`ginsdk.peano.rewrite` normalizes `add` and `mul` terms by applying the defining equations one at a time, leftmost-outermost. On all $m, n < 12$ the number of rewrite steps equals the counts of Proposition \ref{prop:peano-cost}, and the normal form is the successor term of the exact result.
:::

This is the quantitative reason why no one computes in unary, and the reason positional notation exists. It is also a warning about cost statements: "addition costs one step" is true of the move $S$, true of a machine `add` on bounded words, and false — by an exponential factor — of addition on unary numerals of unbounded size. A cost is a property of a *representation* and a *model*, never of an operation alone (\chapref{36-cost-models}).

## Numbers as iterators {#sec:church}

There is a reading of numbers in which they are not data at all but *programs*. The number $n$ is the operation "do it $n$ times".

::: definition {#def:church title="Church numeral" status="definition" ledger="GIN-DEF-013"}
The **Church numeral** of $n$ is the higher-order function $\underline{n} = (f \mapsto f^n)$, which maps any function $f : X \to X$ to its $n$-fold composite \cite{church1941}. In particular $\underline{0} = (f \mapsto \mathrm{id})$ and $\underline{S n} = (f \mapsto f \circ \underline{n}(f))$.
:::

The successor grammar read as a program *is* the Church numeral: $S^n(0)$ is $\underline{n}$ applied to $S$ and $0$. Addition is composition of iterations, $\underline{m + n}(f) = \underline{m}(f) \circ \underline{n}(f)$, and multiplication is iteration of iterations, $\underline{m \cdot n}(f) = \underline{m}(\underline{n}(f))$. These identities say that $\N$ acts on every set by iteration — a fact that will matter when we treat exponents, which are *not* elements of the domain they act on (\chapref{34-exponentiation}).

```python run
from ginsdk.peano import church, unchurch

two, three = church(2), church(3)
double = lambda x: 2 * x
print("3 applied to doubling, from 1:", three(double)(1))
add = lambda m, n: (lambda f: (lambda x: m(f)(n(f)(x))))
mul = lambda m, n: (lambda f: m(n(f)))
print("2 + 3 =", unchurch(add(two, three)), "   2 * 3 =", unchurch(mul(two, three)))
```

```output
3 applied to doubling, from 1: 8
2 + 3 = 5    2 * 3 = 6
```

## $\N$ as a least fixed point {#sec:lfp}

The induction axiom has a third reading. Consider the operator on sets $\Phi(X) = \{0\} \cup S(X)$. A set $X$ is *closed* under the grammar if $\Phi(X) \subseteq X$. The natural numbers are the **least** closed set: they are contained in every closed set, and they are closed themselves. In the language of order theory, $\N$ is the least fixed point of $\Phi$, and the Knaster–Tarski theorem guarantees that such a least fixed point exists for every monotone operator on a complete lattice of sets.

The phrase "fixed point" will appear in this book in three technically different senses, and it is worth separating them now (\ledger{GIN-REI-007}):

| sense | example | what is computed |
|---|---|---|
| an element with $f(x) = x$ | $x^2 = x$ has solutions $0$ and $1$ in $\Z$; four in $\Z/6$ | the solution of an equation (a converse problem) |
| the limit of an iteration | Newton's $x \mapsto (x + a/x)/2$ converges to $\sqrt{a}$ | existence, uniqueness, rate, stopping rule |
| a least fixed point of a set operator | $\N$ is the least $X$ with $\{0\} \cup S(X) \subseteq X$ | induction and recursion; the grammar itself |

They share a definition and nothing else: knowing how to find a least fixed point does not help to find the root of an equation, and conversely.

## Finite sequences and the free monoid {#sec:words}

A unary numeral $S^n0$ is, after deleting the final $0$, a word $S^n$ over a one-letter alphabet, and addition is concatenation: $S^m S^n = S^{m+n}$. More generally, the words over an alphabet $\Sigma$ form a monoid under concatenation, with the empty word $\varepsilon$ as identity, and the *length* map $|\cdot|$ is a homomorphism to $(\N, +, 0)$: $|uv| = |u| + |v|$, $|\varepsilon| = 0$. For a one-letter alphabet the length map is an isomorphism. In algebraic terms, $(\N, +, 0)$ is the free monoid on one generator; the generator is $1$, and every element is uniquely a sum $1 + 1 + \cdots + 1$. This is why, in the next part of the book, numerals with *more* than one letter can compress numbers: a richer alphabet breaks the one-to-one correspondence between length and value.

::: exercise {#ex:rec-distrib}
Prove from GIN-DEF-010 and Proposition \ref{prop:add-laws} that $a \cdot (b + c) = a \cdot b + a \cdot c$ (induction on $c$).
:::

::: solution {of="ex:rec-distrib"}
$c = 0$: $a(b + 0) = ab = ab + 0 = ab + a \cdot 0$. Step: $a(b + Sc) = a \cdot S(b + c) = a(b + c) + a = (ab + ac) + a = ab + (ac + a) = ab + a \cdot Sc$, using the induction hypothesis and associativity.
:::

::: exercise {#ex:rec-cost-pow}
Find the exact number of rule applications of $\mathrm{pow}(m, n)$ for $m = 2$ and $n = 0, 1, 2, 3$ by hand, and check your answer with `ginsdk.peano.power` and a `Cost` object.
:::

::: solution {of="ex:rec-cost-pow"}
$\mathrm{pow}(2, 0)$: 1 rule. $\mathrm{pow}(2, S n)$ costs $1 + \mathrm{cost}(\mathrm{pow}(2, n)) + \mathrm{cost}(\mathrm{mul}(2^n, 2)) = 1 + \mathrm{cost}(\mathrm{pow}(2,n)) + (2 \cdot 2^n + 5)$. So $n = 1$: $1 + 1 + 7 = 9$; $n = 2$: $1 + 9 + 9 = 19$; $n = 3$: $1 + 19 + 13 = 33$. The SDK charges the same counts (`Cost()["rule"]` after `power(2, n, c)`).
:::

::: exercise {#ex:rec-cycle}
Show directly that there is no function $f : \Z/4 \to \N$ with $f(0) = 0$ and $f(x + 1) = f(x) + 1$ for all $x \in \Z/4$.
:::

::: solution {of="ex:rec-cycle"}
Applying the rule four times gives $f(0) = f(0 + 4) = f(0) + 4$, so $0 = 4$ in $\N$, a contradiction. The recursion theorem fails because $0$ is a successor in $\Z/4$.
:::

::: exercise {#ex:rec-church-exp}
Show that applying the Church numeral $\underline{n}$ to the Church numeral $\underline{m}$ (as a function on functions) gives $\underline{m^n}$. What does this say about exponentiation as an operation?
:::

::: solution {of="ex:rec-church-exp"}
$\underline{n}(\underline{m})(f) = \underline{m}^{\circ n}(f) = f^{m \cdot m \cdots m} = f^{m^n}$, since composing the iterator "$m$ times" with itself $n$ times iterates $f$ $m^n$ times. Exponentiation is iteration of iteration: the exponent acts on the base, rather than being combined with it as an equal — which is why exponents are evaluated in $\N$ or $\Z$ even when the base lives in another structure.
:::

::: exercise {#ex:rec-commute-cost}
How many rule applications does $\mathrm{add}(a, b)$ use, and how many $\mathrm{add}(b, a)$? For which pairs are they equal?
:::

::: solution {of="ex:rec-commute-cost"}
$b + 1$ and $a + 1$; equal exactly when $a = b$. The two derivations of a commutative law have different costs.
:::

::: summary
- Induction and recursion are two readings of the same axiom; recursion needs all three Peano axioms, and fails on machine words.
- Arithmetic is defined by primitive recursion; $1 + 1 = 2$ is a two-step derivation, executed by literal rewriting in the SDK.
- The algebraic laws are theorems about derivations with different costs.
- Unary arithmetic costs time proportional to the values — exponential in the length of a binary numeral; costs belong to representations.
- A number can be read as an iterator, and $\N$ as a least fixed point; "fixed point" has three distinct senses.
:::
