---
title: "Division with Remainder, and How Machines Divide"
status: mixed
statusnote: Euclidean division, its conventions and the division algorithms are classical; the proof that a test-free restoring divider returns all ones on a zero divisor is written and checked here.
description: Quotient with remainder as a selection among the solutions of a = q·b + r; the four conventions in use (truncated, floored, Euclidean, rounded) and the languages that use them; long division and its invariant; restoring division in hardware and what it computes for a zero divisor; division of big numbers; and division by constants replaced by multiplication.
epigraph: "When b does not divide a, there is no quotient. There is a whole family of quotients-with-remainder, and every language picks one."
---

::: objectives
- State the division theorem and explain why quotient-with-remainder is a *selection*, not a converse.
- Compare truncated, floored, Euclidean and rounded division, and predict the sign of `-7 % 2` in C, Python and Rust.
- Prove the invariant of long division and analyse binary restoring division.
- Prove that a restoring divider without a divisor test returns quotient $2^n - 1$ and remainder equal to the dividend when the divisor is zero — the RISC-V convention.
- Explain how compilers divide by constants with a multiplication and a shift, and prove the method correct for one divisor.
:::

## Quotients when division fails {#sec:div-theorem}

In $\Z$, $7/2$ has no solution (Chapter 16). Yet everyone knows that "$7$ divided by $2$ is $3$ remainder $1$". The second statement is not about the converse problem $2c = 7$; it is about a different, weaker one:
$$
7 = q \cdot 2 + r, \qquad |r| < |2| .
$$
That problem has *two* solutions, $(q, r) = (3, 1)$ and $(4, -1)$. A further condition on $r$ selects one.

::: theorem {#thm:division-algorithm title="The division theorem" status="classical" ledger="GIN-HIST-005"}
For integers $a$ and $b \ne 0$ there are exactly two pairs $(q, r)$ with $a = qb + r$ and $|r| < |b|$ when $b \nmid a$, and exactly one (with $r = 0$) when $b \mid a$. In particular there is exactly one pair with $0 \le r < |b|$ (the **Euclidean** division).
:::

::: proof
Uniqueness of the Euclidean pair: if $a = qb + r = q'b + r'$ with $0 \le r, r' < |b|$, then $|b| \cdot |q - q'| = |r - r'| < |b|$, so $q = q'$. Existence: let $r$ be the least non-negative element of $\{a - qb : q \in \Z\}$ (non-empty by choosing $q$ with the opposite sign of $a/b$); if $r \ge |b|$ then $r - |b|$ is a smaller non-negative element. Every pair with $|r| < |b|$ is either the Euclidean pair or, when $r \ne 0$, the pair $(q \pm 1, r \mp |b|)$ with negative remainder.
:::

In the vocabulary of Chapter 9, quotient-with-remainder is a **selection**: among the (one or two) solutions of a weaker equation, a rule chooses one. Different rules are in use, and they disagree exactly when the operands have different signs.

| convention | rule for $q$ | sign of $r$ | used by |
|---|---|---|---|
| truncated | $q = \trunc(a/b)$, rounded toward zero | sign of $a$ | C (since C99), C++, Java, Go, Rust `/` and `%`, JavaScript BigInt, x86 `idiv`, ARM `sdiv`, RISC-V `div` |
| floored | $q = \lfloor a/b \rfloor$ | sign of $b$ | Python `//` and `%`, Ruby, Haskell `div`/`mod` |
| Euclidean | $r \ge 0$ always | non-negative | Rust `div_euclid`/`rem_euclid`, Haskell-style definitions in number theory |
| rounded | $q$ = nearest integer to $a/b$ (ties to even) | either | IEEE 754 `remainder` |

```python run
from ginsdk import evaluate

for a, b in [(7, 2), (-7, 2), (7, -2), (-7, -2)]:
    row = []
    for d in ("int32 C", "Python", "Z"):
        q = evaluate(f"({a}) // ({b})", d).display
        r = evaluate(f"({a}) % ({b})", d).display
        row.append(f"{d}: q={q:>2s} r={r:>2s}")
    print(f"{a:>2d}, {b:>2d}   " + "   ".join(row))
```

```output
 7,  2   int32 C: q= 3 r= 1   Python: q= 3 r= 1   Z: q= 3 r= 1
-7,  2   int32 C: q=-3 r=-1   Python: q=-4 r= 1   Z: q=-4 r= 1
 7, -2   int32 C: q=-3 r= 1   Python: q=-4 r=-1   Z: q=-3 r= 1
-7, -2   int32 C: q= 3 r=-1   Python: q= 3 r=-1   Z: q= 4 r= 1
```

(The SDK's exact domain $\Z$ uses the Euclidean convention.) Every row satisfies $a = qb + r$ in every column; the columns differ only in which solution they select. A program that computes "the last digit" or "the day of the week" with `%` gets a negative answer for negative inputs in C and a non-negative one in Python. The C89 standard left the rounding direction of negative quotients to the implementation; C99 fixed it to truncation.

## Long division and its invariant {#sec:long-division}

Long division of $a$ by $b > 0$ in base $\beta$ processes the digits of $a$ from the most significant end, carrying a partial remainder $R$ with $0 \le R < b$. For each digit $a_i$: form $T = \beta R + a_i$, emit the quotient digit $q_i = \lfloor T / b \rfloor$ (which is less than $\beta$), and set $R = T - q_i b$. The invariant after processing the prefix $a_{k-1} \cdots a_i$ is
$$
\val(a_{k-1} \cdots a_i) = \val(q_{k-1} \cdots q_i) \cdot b + R, \qquad 0 \le R < b ,
$$
which at the end is the division theorem for $a$ and $b$. This is the same Horner-style recursion as reading a numeral (Chapter 5), with a division step attached to each digit move. In binary each $q_i$ is $0$ or $1$, and "emit $q_i$" becomes "compare and subtract": the **restoring** division algorithm.

## The divider circuit and the zero divisor {#sec:divider}

A restoring array divider performs the binary long-division step $n$ times in hardware: each row shifts the partial remainder, brings in the next dividend bit, subtracts the divisor with an $(n+1)$-bit subtractor, and keeps the difference if there was no borrow. The SDK builds this circuit gate by gate; for $n = 4, 8, 16$ it has $172$, $632$ and $2416$ gates. Nothing in it tests whether the divisor is zero. What does it compute then?

::: proposition {#prop:divider-zero title="A divider that never tests its divisor returns all ones" status="proved-here" ledger="GIN-PROP-023"}
The $n$-bit restoring array divider of `ginsdk.circuits` outputs quotient $2^n - 1$ and remainder equal to the dividend when the divisor is $0$. These are exactly the results that the RISC-V M extension specifies for `divu` and `remu` by zero.
:::

::: proof
Row $i$ computes $T = 2R + a_i$ and keeps $T - D$ if $T \ge D$. With $D = 0$, $T \ge D$ always holds, so every quotient bit is $1$ and $R \leftarrow T - 0 = T$. After the row for bit $i$, $R = \lfloor a / 2^i \rfloor < 2^{n - i}$, which fits in the $n$-bit register; after the last row ($i = 0$) $R = a$.
:::

```python run
from ginsdk import circuits as K
from ginsdk.machine import divu_riscv

n = 6
c = K.restoring_divider(n)
ok = all(K.run_divider(c, n, a, 0) == (2 ** n - 1, a) for a in range(2 ** n))
riscv = all(divu_riscv(a, 0, n).value == 2 ** n - 1 and divu_riscv(a, 0, n).remainder == a for a in range(2 ** n))
correct = all(K.run_divider(c, n, a, b) == divmod(a, b) for a in range(2 ** n) for b in range(1, 2 ** n))
print(f"{n}-bit divider: {c.size} gates; zero divisor gives (2^n - 1, a) for all a: {ok}; equals RISC-V divu/remu: {riscv}")
print(f"correct for every non-zero divisor: {correct}")
```

```output
6-bit divider: 366 gates; zero divisor gives (2^n - 1, a) for all a: True; equals RISC-V divu/remu: True
correct for every non-zero divisor: True
```

The RISC-V specification motivates its choice by exactly this: all ones is "the natural result for simple unsigned divider implementations", and avoiding a trap lets languages that need one insert a branch \cite{riscv}. The proposition supplies a proof for one such implementation; it is not a new fact. It is a vivid example of the grammar of a *circuit* determining the value of an expression that the grammar of *arithmetic* leaves without one: the value $-1$ (all ones) for $x/0$ is what the hardware does when nobody asks it to do anything else.

Modern processors use faster algorithms than restoring division — non-restoring division, which avoids the restore step; SRT division, which uses redundant quotient digits chosen from a small table (a famous defect in such a table, missing entries, caused the 1994 Pentium FDIV error); and Newton–Raphson or Goldschmidt iteration for floating point, which compute a reciprocal and multiply. Division remains the slowest of the four basic operations in hardware.

## Dividing big numbers {#sec:big-division}

For multi-word integers, Knuth's Algorithm D performs long division in base $2^{32}$ (or $2^{64}$), estimating each quotient digit from the leading words and correcting the estimate at most twice \cite{knuth1997}. Dividing a $2L$-bit number by an $L$-bit number costs $\Theta(L^2)$ word operations; the SDK's count has a log–log slope of $1.996$ at 16,384 bits (\ledger{GIN-OBS-010}). Asymptotically faster division reduces to multiplication by computing a reciprocal with Newton's iteration, at a constant factor times the cost of multiplication \cite{brentzimmermann2010}.

## Division by constants {#sec:const-div}

Division is slow, and division by a *constant* is common (`x / 10` to extract digits, `x / 7` for days of the week). Compilers replace it by a multiplication with a precomputed "magic" reciprocal and a shift. For unsigned 32-bit $x$ and $d = 7$:
$$
\left\lfloor \frac{x}{7} \right\rfloor = \left\lfloor \frac{x \cdot M}{2^{35}} \right\rfloor, \qquad M = \left\lceil \frac{2^{35}}{7} \right\rceil = 4908534053 .
$$

::: proposition {#prop:magic title="Division by an invariant integer using multiplication" status="classical" ledger="GIN-PROP-066"}
Let $0 \le x < 2^{N}$, $d \ge 1$, $s \ge 0$, and $M = \lceil 2^{N+s}/d \rceil$ with $e = M d - 2^{N+s} \le 2^{s}$. Then $\lfloor x M / 2^{N+s} \rfloor = \lfloor x / d \rfloor$ for all such $x$. (Granlund and Montgomery \cite{granlund1994}.) For $N = 32$, $d = 7$, $s = 3$: $M = 4908534053$ and $e = 3 \le 8$.
:::

::: proof
$\dfrac{xM}{2^{N+s}} = \dfrac{x}{d} + \dfrac{x e}{d\, 2^{N+s}}$, and the second term is non-negative and less than $\dfrac{2^N \cdot 2^s}{d\, 2^{N+s}} = \dfrac1d$. Write $x = qd + r$ with $0 \le r \le d - 1$; then $x/d = q + r/d$ and the sum lies in $[q, q + (r + 1)/d) \subseteq [q, q + 1)$, so its floor is $q$.
:::

```python run
import random

M, shift = 4908534053, 35
assert M * 7 - 2 ** 35 <= 2 ** 3
random.seed(7)
xs = list(range(1 << 20)) + [random.getrandbits(32) for _ in range(200000)] + [2 ** 32 - 1 - k for k in range(1000)]
bad = sum((x * M) >> shift != x // 7 for x in xs)
print(f"checked {len(xs)} values of x: {bad} mismatches;  x = 4294967295 -> {(4294967295 * M) >> shift} = {4294967295 // 7}")
```

```output
checked 1249576 values of x: 0 mismatches;  x = 4294967295 -> 613566756 = 613566756
```

The proposition is a theorem, so the check is a guard against a mis-stated constant rather than a proof. The same technique handles signed division and division by every constant; it is one of the reasons the cost of `x / 7` in a compiled program is a multiply and a shift, not a divide.

::: exercise {#ex:rem-conventions}
Compute $(-13) \div 4$ and $(-13) \bmod 4$ under the truncated, floored and Euclidean conventions. Then do the same for $13$ and $-4$.
:::

::: solution {of="ex:rem-conventions"}
$-13, 4$: truncated $q = -3$, $r = -1$; floored $q = -4$, $r = 3$; Euclidean $q = -4$, $r = 3$. $13, -4$: truncated $q = -3$, $r = 1$; floored $q = -4$, $r = -3$; Euclidean $q = -3$, $r = 1$. Check each with $a = qb + r$.
:::

::: exercise {#ex:rem-long}
Divide $1011011_2$ by $101_2$ by binary long division, listing the partial remainders.
:::

::: solution {of="ex:rem-long"}
$1011011_2 = 91$ and $101_2 = 5$. Processing the bits $1, 0, 1, 1, 0, 1, 1$ from the top with $T = 2R + a_i$: $T = 1$ ($q = 0$, $R = 1$); $T = 2$ ($0$, $2$); $T = 5$ ($1$, $0$); $T = 1$ ($0$, $1$); $T = 2$ ($0$, $2$); $T = 5$ ($1$, $0$); $T = 1$ ($0$, $1$). Quotient $0010010_2 = 18$, remainder $1$: $91 = 18 \cdot 5 + 1$.
:::

::: exercise {#ex:rem-magic}
Find the smallest $s$ for which Proposition \ref{prop:magic} applies to $N = 8$, $d = 3$, and the corresponding $M$.
:::

::: solution {of="ex:rem-magic"}
$s = 0$: $M = \lceil 256/3 \rceil = 86$, $e = 258 - 256 = 2 > 1$. $s = 1$: $M = \lceil 512/3 \rceil = 171$, $e = 513 - 512 = 1 \le 2$. So $s = 1$, $M = 171$: $\lfloor x/3 \rfloor = \lfloor 171x/512 \rfloor$ for $0 \le x < 256$.
:::

::: summary
- Quotient-with-remainder is a selection among the solutions of $a = qb + r$; truncated, floored, Euclidean and rounded conventions differ when signs differ.
- Long division is a digit-by-digit transition system with an explicit invariant; in binary it is restoring division.
- A restoring divider that never tests its divisor returns $2^n - 1$ and the dividend on a zero divisor — RISC-V's specified result.
- Big-number division costs $\Theta(L^2)$ schoolbook; division by constants becomes multiplication by a magic reciprocal, provably exact.
:::
