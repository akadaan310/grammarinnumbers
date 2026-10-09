---
title: "Division as the Converse of Multiplication"
status: mixed
statusnote: The coset theorem and the arithmetic of ℤ/n are classical; their organization into image and kernel conditions, and the counting formula for solvable pairs, are written and checked here.
description: Six readings of 6 / 3; division defined by a / b = c ⇔ b · c = a; the image/kernel theorem for commutative rings; why 0 / 1 = 0 passes both conditions; division in ℤ/n with exact counts of unique, missing and multiple quotients; and integral domains as the rings where quotients, when they exist, are unique.
epigraph: "To divide a by b is to ask a question about multiplication: which c, multiplied by b, gives a? Everything about division follows from how that question can fail."
---

::: objectives
- Give six readings of $6/3 = 2$ and identify the one that defines division in every ring.
- State and prove the image/kernel theorem: the solutions of $b\,c = a$ form either the empty set or a coset of the annihilator of $b$.
- Analyse $0/1 = 0$ completely, and explain why it is not the mirror image of $1/0$.
- Decide admissibility of every division in $\Z/n$, and count exactly how many pairs have no quotient, one quotient, or several.
- Characterize the rings in which division, when possible, is unique.
:::

## Six readings of $6/3 = 2$ {#sec:div-six}

1. **Inverse multiplication.** $6/3$ is the number $c$ with $3 \cdot c = 6$; $c = 2$.
2. **Quotient and remainder.** $6 = 2 \cdot 3 + 0$: the quotient $2$ with remainder $0$.
3. **Partition.** Six objects in three equal groups: two per group.
4. **Repeated subtraction (measurement).** $6 - 3 - 3 = 0$: three can be taken away twice.
5. **Ratio.** $6 : 3 = 2 : 1$.
6. **Field operation.** $6 \cdot 3^{-1}$, where $3^{-1}$ is the multiplicative inverse of $3$ in $\Q$.

And the machine readings: binary long division $110_2 \div 11_2 = 10_2$ as two compare-and-subtract rows of a restoring divider; x86's `idiv`, AArch64's `sdiv`, RISC-V's `div`; Knuth's Algorithm D on multi-word integers.

The readings agree on $6/3$ and disagree elsewhere. Reading 2 gives a value for $7/3$ (quotient $2$, remainder $1$) where reading 1 gives none in $\Z$. Reading 6 requires an inverse, which $0$ never has, while reading 1 merely requires a solution, which $0/0$ has in abundance. Reading 3 makes no sense for $6/0$ ("zero groups") and reading 4 never terminates for it. To analyse division by zero precisely we need one reading that works in every ring and does not presuppose the answer. Reading 1 is that reading.

::: definition {#def:division title="Division as a converse problem" status="definition" ledger="GIN-DEF-015"}
In a commutative ring $R$, the **quotient** $a / b$ is defined when the converse problem
$$
\Sol(a, b) = \{\, c \in R : b \cdot c = a \,\}
$$
has exactly one element, and then $a/b$ is that element. Otherwise $a/b$ is inadmissible: with *no solution* if $\Sol(a, b) = \varnothing$, *non-unique* if $|\Sol(a, b)| \ge 2$.
:::

## The image/kernel theorem {#sec:image-kernel}

The map $c \mapsto b \cdot c$ is additive: $b(c + c') = bc + bc'$. By the converse theorem for homomorphisms (\ledger{GIN-THM-007}), its solution sets are cosets of its kernel. The kernel of $c \mapsto bc$ has a classical name.

::: definition {#def:annihilator title="Annihilator" status="definition" ledger="GIN-DEF-091"}
The **annihilator** of $b$ in a commutative ring $R$ is $\Ann(b) = \{\, t \in R : b\, t = 0 \,\}$. An element $b \ne 0$ with $\Ann(b) \ne \{0\}$ is a **zero divisor**.
:::

::: theorem {#thm:image-kernel title="The structure of a converse in a commutative ring" status="classical" ledger="GIN-THM-001"}
Let $R$ be a commutative ring and $a, b \in R$. Then $\Sol(a, b)$ is either empty or a coset $c_0 + \Ann(b)$. Hence:
1. **image condition**: $\Sol(a, b) \ne \varnothing$ if and only if $a \in bR$;
2. **kernel condition**: when $\Sol(a, b) \ne \varnothing$, it has exactly $|\Ann(b)|$ elements; the quotient is unique if and only if $\Ann(b) = \{0\}$.
:::

::: proof
If $c_0 \in \Sol(a, b)$, then $b c = a \iff b c = b c_0 \iff b(c - c_0) = 0 \iff c - c_0 \in \Ann(b)$.
:::

The theorem says that a division can fail in exactly two ways, and that the two ways are independent of each other:

- an **image failure**: $a$ is not a multiple of $b$, so *nothing* solves the equation;
- a **kernel failure**: $b$ annihilates something non-zero, so *if* anything solves the equation, many things do.

The research ledger checks the theorem exhaustively on 30 finite commutative rings — $\Z/n$ for $n \le 24$, five products $\Z/m \times \Z/k$, and $\F_2[x]/(x^3)$ — over all $5737$ pairs $(a, b)$ (\ledger{GIN-THM-001}).

## $0/1 = 0$, completely {#sec:zero-over-one}

Many people hesitate at $0/1$. The converse reading removes the hesitation, and shows that $0/1$ and $1/0$ are not mirror images of each other.

::: proposition {#prop:zero-over-one title="0 / 1 = 0 as a complete case" status="classical" ledger="GIN-PROP-011"}
In every commutative ring with $1$, $0/1$ is admissible and equals $0$: the image condition holds because $0 = 1 \cdot 0 \in 1 \cdot R$, and the kernel condition holds because $\Ann(1) = \{0\}$. More generally $0/b = 0$ whenever $\Ann(b) = \{0\}$.
:::

::: proof
$1 \cdot t = t$, so $1 \cdot t = 0$ only for $t = 0$; and $c = 0$ solves $1 \cdot c = 0$.
:::

Swapping $0$ and $1$ is not a symmetry of division. A zero *numerator* tests the image condition with the element $0$, which lies in *every* ideal $bR$ — so the image condition always holds for $0/b$. A zero *denominator* shrinks the image to $0 \cdot R = \{0\}$ and enlarges the kernel to $\Ann(0) = R$: both conditions are put under maximal stress at once. The next chapter is devoted to that case.

| expression | equation | image: $a \in bR$? | kernel: $\Ann(b) = 0$? | outcome |
|---|---|---|---|---|
| $6/3$ | $3c = 6$ | ✓ | ✓ | $2$ |
| $0/1$ | $1c = 0$ | ✓ ($0 \in R$) | ✓ | $0$ |
| $0/x$, $x \ne 0$ in a field | $xc = 0$ | ✓ | ✓ | $0$ |
| $x/x$, $x \ne 0$ in a field | $xc = x$ | ✓ | ✓ | $1$ |
| $7/2$ in $\Z$ | $2c = 7$ | ✗ | ✓ | no solution |
| $1/0$ | $0c = 1$ | ✗ ($0R = \{0\}$) | ✗ | no solution |
| $0/0$ | $0c = 0$ | ✓ | ✗ ($\Ann(0) = R$) | non-unique |
| $2/4$ in $\Z/6$ | $4c = 2$ | ✓ | ✗ ($\Ann(4) = \{0, 3\}$) | non-unique: $\{2, 5\}$ |
| $3/4$ in $\Z/6$ | $4c = 3$ | ✗ | ✗ | no solution |

## Division in $\Z/n$ {#sec:zmod-div}

In the finite rings $\Z/n$ both conditions can be decided by a single gcd.

::: theorem {#thm:zmod-div title="Division in ℤ/n" status="classical" ledger="GIN-THM-002"}
In $\Z/n$, let $g = \gcd(b, n)$. Then $\Sol(a, b) \ne \varnothing$ iff $g \mid a$, and in that case $|\Sol(a, b)| = g$, the solutions forming $c_0 + (n/g)\,\Z/n$. Exactly $n\,\varphi(n)$ of the $n^2$ pairs $(a, b)$ have a unique quotient, where $\varphi$ is Euler's totient.
:::

::: proof
By Bézout's identity, $b\Z/n = g\Z/n$, which is the image condition. $bt \equiv 0 \pmod n$ iff $(n/g) \mid (b/g)\,t$ iff $(n/g) \mid t$, since $\gcd(b/g, n/g) = 1$; so $\Ann(b) = (n/g)\Z/n$ has $g$ elements. A unique quotient requires $g = 1$, i.e. $b$ is one of the $\varphi(n)$ units; then every $a$ works, giving $n\varphi(n)$ pairs.
:::

How many pairs are solvable at all? Summing the $n/g$ solvable numerators over all $b$ gives a classical arithmetic function.

::: proposition {#prop:solvable-count title="Counting the solvable divisions in ℤ/n" status="proved-here" ledger="GIN-PROP-064"}
The number of pairs $(a, b) \in (\Z/n)^2$ for which $b\,c \equiv a$ has a solution is
$$
\sum_{d \mid n} d\,\varphi(d) ,
$$
and the number with several solutions is that sum minus $n\varphi(n)$.
:::

::: proof
For each $b$, the solvable $a$ are the multiples of $g = \gcd(b, n)$, of which there are $n/g$. The number of $b \in \Z/n$ with $\gcd(b, n) = g$ is $\varphi(n/g)$. Hence the total is $\sum_{g \mid n} \varphi(n/g)\, (n/g) = \sum_{d \mid n} d\,\varphi(d)$ with $d = n/g$. Subtract the $n\varphi(n)$ pairs with a unique solution.
:::

```python run
from math import gcd
from ginsdk.converse import divide_mod, UNIQUE, NONE, MULTIPLE

def census(n):
    count = {UNIQUE: 0, NONE: 0, MULTIPLE: 0}
    for a in range(n):
        for b in range(n):
            count[divide_mod(a, b, n).kind] += 1
    return {"unique": count[UNIQUE], "none": count[NONE], "multiple": count[MULTIPLE]}

phi = lambda n: sum(gcd(k, n) == 1 for k in range(1, n + 1))
for n in (6, 7, 12, 30):
    c = census(n)
    formula = sum(d * phi(d) for d in range(1, n + 1) if n % d == 0)
    print(f"Z/{n:<3d} unique {c['unique']:4d} (n·φ(n) = {n * phi(n):4d})   none {c['none']:4d}   multiple {c['multiple']:4d}   solvable {c['unique'] + c['multiple']:4d} (Σ dφ(d) = {formula})")
```

```output
Z/6   unique   12 (n·φ(n) =   12)   none   15   multiple    9   solvable   21 (Σ dφ(d) = 21)
Z/7   unique   42 (n·φ(n) =   42)   none    6   multiple    1   solvable   43 (Σ dφ(d) = 43)
Z/12  unique   48 (n·φ(n) =   48)   none   67   multiple   29   solvable   77 (Σ dφ(d) = 77)
Z/30  unique  240 (n·φ(n) =  240)   none  459   multiple  201   solvable  441 (Σ dφ(d) = 441)
```

For a prime $p$, every division by a non-zero element is admissible, and the only inadmissible pairs are those with $b = 0$: $p - 1$ with no solution ($a \ne 0$) and exactly one, $0/0$, with $p$ solutions. A prime modulus behaves, with respect to division, exactly like the rationals.

::: demo zmod
Text alternative: a table for $\Z/n$ with one row per divisor $b$ and one column per dividend $a$. A cell shows the unique quotient, ∅ for no solution, or the number of solutions. In $\Z/6$, the rows of the units $1$ and $5$ are complete; row $0$ has a single solvable cell ($0/0$, six solutions); rows $2$ and $4$ are solvable exactly at even $a$ with two solutions each; row $3$ at $a \in \{0, 3\}$ with three solutions each.
:::

## When quotients are unique {#sec:domains}

Which rings never have kernel failures for non-zero divisors?

::: proposition {#prop:integral-domain title="Unique quotients characterize integral domains" status="classical" ledger="GIN-PROP-065"}
For a commutative ring $R$ with $1 \ne 0$, the following are equivalent: (i) for every $b \ne 0$ and every $a$, $\Sol(a, b)$ has at most one element; (ii) $R$ has no zero divisors (it is an integral domain); (iii) multiplication by any $b \ne 0$ is cancellable: $bc = bc' \Rightarrow c = c'$. A finite integral domain is a field: every non-zero element is invertible.
:::

::: proof
(i) ⇔ (ii) by Theorem \ref{thm:image-kernel}: uniqueness for all $a$ is $\Ann(b) = \{0\}$. (ii) ⇔ (iii): $bc = bc' \iff b(c - c') = 0$. If $R$ is finite and $b \ne 0$, the map $c \mapsto bc$ is injective by (iii), hence surjective, so $bc = 1$ for some $c$.
:::

So in $\Z$, $\Q$, $\R$, $\C$ and $\Z/p$, the *only* kernel failure is at $b = 0$, and in fields the *only* image failure is at $b = 0$ too. Division by zero is the one place where a field's division is inadmissible — and there, both conditions fail at once. That is the subject of Chapter 17.

::: exercise {#ex:div-z12}
In $\Z/12$, classify $8/4$, $9/4$, $9/3$ and $5/7$ and list the solution sets.
:::

::: solution {of="ex:div-z12"}
$8/4$: $g = 4 \mid 8$, solutions $\{2, 5, 8, 11\}$ — non-unique. $9/4$: $4 \nmid 9$ — no solution. $9/3$: $g = 3 \mid 9$, solutions $\{3, 7, 11\}$ — non-unique. $5/7$: $\gcd(7, 12) = 1$, unique: $7^{-1} = 7$ (since $49 \equiv 1$), so $c = 35 \bmod 12 = 11$.
:::

::: exercise {#ex:div-product-ring}
In $R = \Z/2 \times \Z/3$, compute $\Ann((1, 0))$ and decide whether $(1, 1)/(1, 0)$ and $(1, 0)/(1, 0)$ are admissible.
:::

::: solution {of="ex:div-product-ring"}
$(1, 0)(t_1, t_2) = (t_1, 0)$, so $\Ann((1, 0)) = \{(0, 0), (0, 1), (0, 2)\}$. $(1, 1) \notin (1, 0)R = \{(0,0), (1, 0)\}$: no solution. $(1, 0)$ is in the image; solutions $(1, 0) + \Ann = \{(1, 0), (1, 1), (1, 2)\}$: non-unique.
:::

::: exercise {#ex:div-formula}
Evaluate $\sum_{d \mid n} d\varphi(d)$ for $n = p^k$ (a prime power), and check it against the census for $n = 8$.
:::

::: solution {of="ex:div-formula"}
$\sum_{j=0}^{k} p^j \varphi(p^j) = 1 + \sum_{j=1}^k p^{2j - 1}(p - 1) = 1 + (p-1)p\,\frac{p^{2k} - 1}{p^2 - 1} = 1 + \frac{p(p^{2k} - 1)}{p + 1}$. For $n = 8$ ($p = 2$, $k = 3$): $1 + 2 \cdot 63/3 = 43$; directly, $d \in \{1, 2, 4, 8\}$ gives $1 \cdot 1 + 2 \cdot 1 + 4 \cdot 2 + 8 \cdot 4 = 43$, which is the number of solvable pairs in $\Z/8$.
:::

::: summary
- Division is the converse of multiplication: $a/b$ denotes the unique $c$ with $bc = a$, when there is one.
- In a commutative ring the solution set is empty or a coset of $\Ann(b)$: an image failure means no quotient, a kernel failure means many.
- $0/1 = 0$ passes both conditions; a zero numerator is harmless, a zero denominator stresses both conditions at once.
- In $\Z/n$ everything is decided by $g = \gcd(b, n)$: $n\varphi(n)$ pairs have unique quotients and $\sum_{d \mid n} d\varphi(d)$ are solvable.
- Integral domains are exactly the rings where non-zero divisors give unique quotients; in a field, $b = 0$ is the only failure.
:::
