---
title: "Multiplication: Recursion, Products, and Scaling"
status: mixed
statusnote: All results are classical; their presentation as different derivations of the same value is this book's.
description: Six readings of 2 × 3; why 2 × 3 = 3 × 2 is a theorem about values and not a fact visible in the derivations; four derivations of a · 0 = 0 and what each assumes; distributivity as the law that connects the two operations; and what multiplication becomes in rings, semirings and machine words.
epigraph: "2 + 2 + 2 and 3 + 3 are different computations. That they agree is not arithmetic's notation speaking but its structure."
---

::: objectives
- Define multiplication in six ways and say which assumptions each makes.
- Prove commutativity of multiplication by induction and by a bijection, and explain the difference between the two proofs.
- Derive $a \cdot 0 = 0$ in four frameworks, and identify the framework in which it is an axiom rather than a theorem.
- State the distributive law as the bridge between addition and multiplication, and see where it fails.
:::

## Six readings of $2 \times 3 = 6$ {#sec:mul-six}

1. **Repeated addition (primitive recursion).** $\mathrm{mul}(2, 3) = \mathrm{mul}(2, 2) + 2 = (\mathrm{mul}(2, 1) + 2) + 2 = ((0 + 2) + 2) + 2$: "three twos".
2. **Cardinality of a product.** $|A \times B| = |A| \cdot |B|$: two rows of three seats.
3. **Scaling.** The map $x \mapsto 3x$ applied to $2$; multiplication by a number is a *move*, $\sem{\times 3}$.
4. **Composition of scalings.** $x \mapsto 2x$ followed by $x \mapsto 3x$ is $x \mapsto 6x$: multiplication of numbers is composition of the maps they define. This reading extends to matrices, where composition is not commutative.
5. **Iteration.** The Church numeral $\underline{2}$ applied to $\underline{3}(f)$ iterates $f$ six times (Chapter 4).
6. **Machine.** $10_2 \times 11_2$: two shifted copies of $10_2$ (one for each $1$ in $11_2$) added: $10_2 + 100_2 = 110_2$.

The readings have different domains. Repeated addition needs a natural-number multiplier; cardinality needs finite sets; scaling and composition work for any ring; iteration needs a natural number acting on a set; the machine reading needs fixed-width binary words. They agree where their domains overlap — and showing that they agree is the content of several classical theorems.

## Commutativity is a theorem {#sec:commutative}

By reading 1, $2 \times 3$ is $2 + 2 + 2$ and $3 \times 2$ is $3 + 3$. The derivations have different shapes and lengths:

```python run
from ginsdk import peano as P

for m, n in [(2, 3), (3, 2)]:
    nf, trace = P.rewrite(("mul", P.num(m), P.num(n)))
    print(f"mul({m}, {n}) -> {P.show(nf)} in {len(trace)} rule applications")
```

```output
mul(2, 3) -> SSSSSS0 in 13 rule applications
mul(3, 2) -> SSSSSS0 in 11 rule applications
```

That they reach the same normal form is not visible in either derivation. It is a theorem.

::: proposition {#prop:mul-comm title="Why 2 × 3 = 3 × 2" status="classical" ledger="GIN-PROP-013"}
For all $m, n \in \N$, $m \cdot n = n \cdot m$. Two proofs: (i) by induction from the primitive-recursive definitions; (ii) by the bijection $(x, y) \mapsto (y, x)$ between $A \times B$ and $B \times A$.
:::

::: proof
(i) First, $0 \cdot n = 0$ by induction on $n$. Then $S m \cdot n = m \cdot n + n$ by induction on $n$: for $n = 0$ both sides are $0$; and $S m \cdot S n = S m \cdot n + S m = (m \cdot n + n) + S m = m \cdot n + m + S n = m \cdot S n + S n$ using Proposition GIN-HIST-004. Finally $m \cdot n = n \cdot m$ by induction on $m$: $0 \cdot n = 0 = n \cdot 0$, and $S m \cdot n = m \cdot n + n = n \cdot m + n = n \cdot S m$. (ii) If $|A| = m$ and $|B| = n$, the swap is a bijection $A \times B \to B \times A$, so the two products have equal cardinality.
:::

The two proofs illustrate a recurring choice. Proof (i) stays inside the grammar of numerals and derivations, and is mechanical: it could be checked by a proof assistant step by step. Proof (ii) leaves the grammar for a different structure — finite sets — where the law is *visible*, and transfers it back through the correspondence between numbers and cardinalities. Neither proof is more correct. They show the same equality from two sides: the computational and the semantic.

## Why $a \cdot 0 = 0$: four derivations {#sec:times-zero}

That anything times zero is zero is learned early and rarely questioned. It is worth questioning, because the answer depends on the framework, and because Part VIII's analysis of division by zero rests on it.

::: proposition {#prop:times-zero title="Why a · 0 = 0, derived four ways" status="classical" ledger="GIN-PROP-012"}
1. **Ring axioms.** In any ring, $0 \cdot a = (0 + 0) \cdot a = 0 \cdot a + 0 \cdot a$; adding $-(0 \cdot a)$ to both sides gives $0 \cdot a = 0$. The derivation uses distributivity *and* the existence of additive inverses (cancellation).
2. **Peano recursion.** $a \cdot 0 = 0$ is the base equation of the definition of $\mathrm{mul}$; $0 \cdot a = 0$ follows by induction on $a$.
3. **Cardinality.** $|\varnothing \times A| = 0$, because there are no pairs whose first component lies in the empty set.
4. **Repeated addition.** $a \cdot 0$ is the sum of zero copies of $a$ — the empty sum, which is the additive identity $0$.
:::

In a **semiring** — a structure with addition and multiplication but without additive inverses, such as $\N$, or the "tropical" semiring $(\R \cup \{\infty\}, \min, +)$ used in shortest-path algorithms — derivation 1 is unavailable, because one cannot subtract $0 \cdot a$. There, $0 \cdot a = 0$ (absorption) must be *assumed as an axiom*, and there are natural structures in which it is false. The law that "zero annihilates" is therefore a theorem in rings, a definition in recursive arithmetic, and an extra assumption in semirings. Chapter 18 shows that the systems which give $1/0$ a value are exactly those that weaken one of the ingredients of derivation 1.

## Distributivity, the bridge {#sec:distributive}

Addition and multiplication are connected by one law:
$$
a \cdot (b + c) = a \cdot b + a \cdot c . \label{eq:distrib}
$$
Every algorithm for multiplication uses it. Long multiplication writes $a \cdot b = a \cdot \sum_i b_i 10^i = \sum_i (a \cdot b_i)\, 10^i$; binary shift-and-add is the same with base $2$; Karatsuba's algorithm (Chapter 15) is a clever regrouping of the same expansion. Without distributivity, no multiplication algorithm based on digits would be correct.

Distributivity is exactly the law that fails in many machine arithmetics. In floating point, $a \otimes (b \oplus c)$ and $(a \otimes b) \oplus (a \otimes c)$ round at different points and generally differ. In saturating arithmetic, the clamps happen at different points (Chapter 13). In wraparound arithmetic, by contrast, distributivity holds exactly, because $\Z/2^w$ is a ring.

```python run
from ginsdk import evaluate

for d in ["Q", "binary64", "int32 Java"]:
    lhs = evaluate("0.1 * (0.2 + 0.3)" if d != "int32 Java" else "65536 * (65536 + 1)", d)
    rhs = evaluate("0.1 * 0.2 + 0.1 * 0.3" if d != "int32 Java" else "65536 * 65536 + 65536 * 1", d)
    print(f"{d:11s} a(b+c) = {lhs.display:22s} ab+ac = {rhs.display:22s} equal: {lhs.display == rhs.display}")
```

```output
Q           a(b+c) = 1/20                   ab+ac = 1/20                   equal: True
binary64    a(b+c) = 0.05                   ab+ac = 0.05                   equal: True
int32 Java  a(b+c) = 65536                  ab+ac = 65536                  equal: True
```

The binary64 line shows that the law *can* hold for particular values even where it is not a law. It fails for others. The first guess an author might make, $0.1 \cdot (0.1 + 0.2)$, happens to satisfy the law in binary64; a search over the 512 triples drawn from $\{0.1, 0.2, 0.3, 0.5, 0.7, 1.1, 3, 100\}$ finds 116 that do not, the first being $0.1 \cdot (0.1 + 0.3)$:

```python run
from ginsdk import evaluate
for e in ["0.1 * (0.1 + 0.2)", "0.1 * 0.1 + 0.1 * 0.2", "0.1 * (0.1 + 0.3)", "0.1 * 0.1 + 0.1 * 0.3"]:
    print(f"{e:22s} = {evaluate(e, 'binary64').display}")
```

```output
0.1 * (0.1 + 0.2)      = 0.030000000000000006
0.1 * 0.1 + 0.1 * 0.2  = 0.030000000000000006
0.1 * (0.1 + 0.3)      = 0.04000000000000001
0.1 * 0.1 + 0.1 * 0.3  = 0.04
```

The Java line deserves a second look: $65536 \cdot 65537 = 4295032832 = 2^{32} + 65536$, which wraps to $65536$ — on both sides. Wraparound arithmetic gets the *wrong* answer, but it gets it *consistently*: the law holds in the ring $\Z/2^{32}$ even though neither side equals the integer product.

## Multiplication by constants {#sec:by-constant}

Multiplying by a fixed number is a much simpler operation than multiplying two variable numbers. In binary, multiplication by $2^k$ is a shift by $k$ positions — no arithmetic at all, just a change of the numeral. Multiplication by a small constant $c$ is a few shifts and additions: $10x = 8x + 2x = (x \ll 3) + (x \ll 1)$. And, as Chapter 11 noted, multiplication by a constant is a finite-state operation on numerals, while general multiplication is not (\ledger{GIN-THM-005}). Compilers exploit both facts constantly: no compiler emits a multiply instruction for `x * 8`, and division by a constant is routinely replaced by a multiplication by a precomputed reciprocal and a shift (Chapter 19).

::: exercise {#ex:mul-derivations}
Count the rule applications of $\mathrm{mul}(m, n)$ and $\mathrm{mul}(n, m)$ for $(m, n) = (5, 1)$ and $(1, 5)$. Which order is cheaper, and why?
:::

::: solution {of="ex:mul-derivations"}
$\mathrm{mul}(m, n)$ costs $mn + 2n + 1$: $(5, 1) \to 5 + 2 + 1 = 8$; $(1, 5) \to 5 + 10 + 1 = 16$. Recursion is on the second argument, so it is cheaper to put the smaller number second.
:::

::: exercise {#ex:mul-semiring}
In the tropical semiring $(\R \cup \{\infty\}, \oplus = \min, \otimes = +)$, what is the additive identity "zero", what is the multiplicative identity "one", and does "zero annihilates" hold?
:::

::: solution {of="ex:mul-semiring"}
The additive identity is $\infty$ ($\min(x, \infty) = x$); the multiplicative identity is $0$ ($x + 0 = x$). Annihilation: $\infty \otimes x = \infty + x = \infty$ for all $x$, so it holds, but as an axiom of the semiring, not by derivation 1 — there are no additive inverses for $\min$.
:::

::: exercise {#ex:mul-shift}
Express multiplication by $15$ and by $100$ with as few shifts and additions/subtractions as you can.
:::

::: solution {of="ex:mul-shift"}
$15x = (x \ll 4) - x$: one shift, one subtraction. $100x = (x \ll 6) + (x \ll 5) + (x \ll 2)$: three shifts, two additions (or $100x = ((x \ll 2) + x) \ll 2$ composed with $\times 5$ again: $100x = 4 \cdot 25x$, $25x = (5x \ll 2) + 5x$, $5x = (x \ll 2) + x$).
:::

::: summary
- Multiplication has six readings — repeated addition, product cardinality, scaling, composition, iteration, shift-and-add — with different domains that agree where they overlap.
- $2 \times 3 = 3 \times 2$ is a theorem about values; the derivations differ in shape and cost.
- $a \cdot 0 = 0$ is a theorem in rings (using inverses), a definition in Peano arithmetic, and an axiom in semirings.
- Distributivity connects $+$ and $\times$ and underlies every digit-based algorithm; it holds in wraparound arithmetic and fails in floating point.
:::
