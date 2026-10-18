---
title: "Euclid's Algorithm as a Transition System"
status: mixed
statusnote: The algorithms and their bounds are classical (Euclid, Lamé, Bézout, Stein, Heilbronn–Dixon); the binary-gcd iteration bound is proved here; the counted costs are this book's measurements.
description: The Euclidean algorithm as states, one move and an invariant; Lamé's worst case; the extended algorithm and Bézout's identity as the solver for the converse problems of Chapter 29; the bit cost of gcd; the average number of steps; and Stein's binary algorithm.
epigraph: "Of two unequal numbers, the less being continually subtracted from the greater… — Euclid, Elements VII.1"
---

::: objectives
- Present the Euclidean algorithm as a transition system with a state space, one move, an invariant and a termination measure, and prove it correct.
- Prove Lamé's bound and identify the Fibonacci pairs as the worst case.
- Use the extended algorithm to produce Bézout coefficients, and use them to solve the linear converse problems of Chapters 16 and 29.
- Distinguish the number of division steps from the bit cost, and bound the latter by $\Oh(L^2)$.
- State what is known about the average number of steps, and check it against measurement.
- Prove a bound for Stein's binary algorithm, and compare the two algorithms by counted operations rather than by step counts.
:::

## States, one move, one invariant {#sec:euclid-system}

Chapter 30 defined $\gcd(a, b)$ through the divisibility order. Computing it is a different matter, and the oldest non-trivial algorithm in mathematics does it \cite{euclid}. As a transition system it has:

- **states** — pairs $(a, b)$ of natural numbers;
- **one move** — $(a, b) \to (b, a \bmod b)$, admissible exactly when $b \neq 0$ (the remainder of Chapter 19 is a converse problem with a selection, and it has no answer for $b = 0$);
- **terminal states** — pairs $(g, 0)$, where no move is admissible;
- **an invariant** — the set of common divisors, and therefore $\gcd(a, b)$, does not change under the move;
- **a termination measure** — the second component strictly decreases, since $0 \le a \bmod b < b$.

::: theorem {#thm:euclid-correct title="Correctness of Euclid's algorithm" status="classical" ledger="GIN-PROP-040"}
From any state $(a, b)$ the move can be applied only finitely often, and the terminal state is $(\gcd(a, b), 0)$.
:::

::: proof
Write $a = qb + r$. A common divisor of $a$ and $b$ divides $r = a - qb$; a common divisor of $b$ and $r$ divides $a = qb + r$. So $(a, b)$ and $(b, r)$ have the same common divisors and the same greatest one. The second component is a natural number that strictly decreases, so the run is finite. At a terminal state $(g, 0)$ the common divisors are the divisors of $g$, whose greatest is $g$ (with the convention $\gcd(0, 0) = 0$ in the divisibility order, Chapter 30).
:::

The SDK records each run as a trace of rows $(a, b, q)$ with $a = qb + (a \bmod b)$:

```python run
from ginsdk import numbertheory as nt

for row in nt.euclid_trace(1071, 462):
    a, b, q = row
    print(f"{a:5d} = {q} * {b:4d} + {a - q * b}")
print("gcd =", nt.gcd(1071, 462), " steps =", nt.euclid_steps(1071, 462))
```

```output
 1071 = 2 *  462 + 147
  462 = 3 *  147 + 21
  147 = 7 *   21 + 0
gcd = 21  steps = 3
```

Each line is one transition; the invariant says every line has the same gcd. The algorithm never computes a divisor — it only takes remainders — and still ends at the greatest common one. That is what an invariant buys: the answer is carried through states that do not mention it.

## The worst case: Lamé {#sec:lame}

How many moves can a run take? Large quotients make fast progress, so the slowest runs have every quotient equal to $1$, and running such a run backwards from $(1, 0)$ gives the recurrence of the Fibonacci numbers.

::: theorem {#thm:lame title="Lamé's theorem" status="classical" ledger="GIN-PROP-040"}
If the algorithm started at $a > b > 0$ takes $k$ division steps, then $a \ge F_{k+2}$ and $b \ge F_{k+1}$, where $F_1 = F_2 = 1$ and $F_{n+1} = F_n + F_{n-1}$. The pair $(F_{k+2}, F_{k+1})$ takes exactly $k$ steps. Consequently $k \le \log_\varphi a + \Oh(1)$ with $\varphi = (1 + \sqrt 5)/2$ \cite{lame1844}.
:::

::: proof
By induction on $k$. For $k = 1$: $b \ge 1 = F_2$ and $a > b$ gives $a \ge 2 = F_3$. For $k \ge 2$, the first step leads to $(b, r)$ with $r > 0$, from which $k - 1$ steps remain; by induction $b \ge F_{k+1}$ and $r \ge F_k$. Since $a = qb + r$ with $q \ge 1$, $a \ge b + r \ge F_{k+1} + F_k = F_{k+2}$. For the Fibonacci pair, $F_{k+2} = 1 \cdot F_{k+1} + F_k$ with $F_k < F_{k+1}$ for $k \ge 2$, so the run visits the consecutive Fibonacci pairs down to $(F_3, F_2) = (2, 1)$ and then $(1, 0)$: $k$ steps. Finally $F_{k+2} \ge \varphi^{k}$, so $k \le \log_\varphi a$.
:::

```python run
from ginsdk import numbertheory as nt

first = {}
for a in range(2, 2000):
    for b in range(1, a):
        first.setdefault(nt.euclid_steps(a, b), (a, b))
ok = all(first[k] == nt.lame_worst_pair(k) for k in first)
print("smallest pair needing k steps is (F_{k+2}, F_{k+1}) for every k seen:", ok, " max k =", max(first))
print("k = 15:", first[15], "  2^64 - 1 needs at most", next(k for k in range(200) if nt.fibonacci(k + 2) > 2**64 - 1) - 1, "steps")
```

```output
smallest pair needing k steps is (F_{k+2}, F_{k+1}) for every k seen: True  max k = 15
k = 15: (1597, 987)   2^64 - 1 needs at most 91 steps
```

Lamé's bound is a statement about the *grammar* of the run: each step at least multiplies the "distance to the end" by the golden ratio. It is also the first theorem in the history of algorithm analysis — an 1844 bound on the running time of an algorithm in terms of the size of its input.

## Running the algorithm backwards: Bézout {#sec:bezout}

Chapter 29 showed that $b \cdot c \equiv a \pmod n$ has a solution iff $\gcd(b, n) \divides a$, but did not say how to find one. The **extended algorithm** carries, alongside each remainder, a record of how it was made from the inputs.

::: theorem {#thm:bezout title="Bézout's identity, constructively" status="classical" ledger="GIN-HIST-016"}
For integers $a, b$ not both $0$, the extended Euclidean algorithm computes integers $s, t$ with $sa + tb = \gcd(a, b)$. Its rows $(r_i, s_i, t_i)$, started at $(a, 1, 0)$ and $(b, 0, 1)$ and updated by $r_{i+1} = r_{i-1} - q_i r_i$ (likewise for $s$ and $t$), satisfy the invariant $r_i = s_i a + t_i b$ \cite{knuth1997}.
:::

::: proof
The invariant holds for the two initial rows by inspection, and it is preserved because the update is the same linear combination applied to all three components: $r_{i-1} - q_i r_i = (s_{i-1} - q_i s_i) a + (t_{i-1} - q_i t_i) b$. The $r$-column is exactly Euclid's sequence of remainders, so its last non-zero entry is $\gcd(a, b)$ by \ref{thm:euclid-correct}.
:::

```python run
from ginsdk import numbertheory as nt

print(" r      s      t      q")
for row in nt.extended_euclid_trace(240, 46):
    print(f"{row.r:3d} {row.s:6d} {row.t:6d}   {row.q if row.q is not None else ''}")
g, s, t = nt.bezout(240, 46)
print(f"gcd = {g} = {s}*240 + {t}*46")
print("inverse of 7 mod 40:", nt.mod_inverse(7, 40), "  inverse of 6 mod 40:", nt.mod_inverse(6, 40))
```

```output
 r      s      t      q
240      1      0   
 46      0      1   5
 10      1     -5   4
  6     -4     21   1
  4      5    -26   1
  2     -9     47   2
  0     23   -120   
gcd = 2 = -9*240 + 47*46
inverse of 7 mod 40: 23   inverse of 6 mod 40: None
```

The last line is the converse problem of Chapter 29 solved: $7c \equiv 1 \pmod{40}$ has the unique solution the extended algorithm finds, while $6c \equiv 1 \pmod{40}$ fails the image condition ($\gcd(6, 40) = 2 \ndivides 1$) and the SDK returns `None` rather than a number. The algorithm *decides* admissibility and *solves* the problem in one run, which is not true of every converse problem — Chapter 31 showed the discrete logarithm, where deciding is easy and solving is believed hard.

The same coefficients solve the linear Diophantine equation $ax + by = c$: it is solvable iff $g = \gcd(a, b) \divides c$, a particular solution is $(sc/g, tc/g)$, and all solutions form a coset of the kernel $\{(bk/g, -ak/g) : k \in \Z\}$ — the image/kernel theorem once more (\ledger{GIN-THM-007}).

## What a gcd costs {#sec:euclid-cost}

Lamé bounds the number of *steps* by $\Oh(L)$ for $L$-bit inputs. A step is a division with remainder, whose bit cost is not constant (Chapter 36), so the step count is not the cost.

::: theorem {#thm:euclid-bits title="The bit cost of Euclid's algorithm" status="classical" ledger="GIN-HIST-017"}
With schoolbook division, Euclid's algorithm on $L$-bit inputs uses $\Oh(L^2)$ bit operations — not $\Oh(L^3)$, as "$\Oh(L)$ steps times $\Oh(L^2)$ per division" would suggest \cite{knuth1997}.
:::

::: proof
Dividing $r_{i-1}$ by $r_i$ with quotient $q_i$ costs $\Oh((1 + \log q_i) \cdot \log r_i) \subseteq \Oh((1 + \log q_i) L)$ bit operations. Since $r_{i-1} \ge q_i r_i$, the product of the quotients is at most $a$, so $\sum_i \log q_i \le \log a \le L$. With $\Oh(L)$ steps by Lamé, the total is $\Oh(L \cdot (k + \sum \log q_i)) = \Oh(L^2)$.
:::

The theorem is an example of a cost argument that uses the *invariant structure of the run* — the quotients cannot all be large — rather than a worst case per step. Measured with the SDK's limb arithmetic (Chapter 37 has the full data):

```python run
import random
from ginsdk import bigint as B
from ginsdk.cost import Cost

rng = random.Random(33)
prev = None
for L in (256, 512, 1024, 2048):
    a, b = rng.getrandbits(L) | 1 << (L - 1), rng.getrandbits(L) | 1 << (L - 1)
    c = Cost()
    _, steps = B.gcd_euclid(B.from_int(a), B.from_int(b), c)
    ops = B.word_ops(c)
    print(f"L = {L:5d}: {steps:5d} division steps, {ops:9d} limb operations" + (f"   ratio to previous {ops / prev:.2f}" if prev else ""))
    prev = ops
```

```output
L =   256:   146 division steps,      1510 limb operations
L =   512:   283 division steps,      5567 limb operations   ratio to previous 3.69
L =  1024:   608 division steps,     22422 limb operations   ratio to previous 4.03
L =  2048:  1242 division steps,     86838 limb operations   ratio to previous 3.87
```

Doubling $L$ roughly doubles the number of steps (Lamé: linear) and roughly quadruples the limb operations (\ref{thm:euclid-bits}: quadratic). Faster gcd algorithms exist — Lehmer's method works on leading digits, and "half-gcd" algorithms reach $\Oh(M(L) \log L)$ with fast multiplication \cite{brentzimmermann2010} — and are not implemented in this book's SDK.

## The average run {#sec:euclid-average}

Lamé describes the worst case. For a typical pair the number of steps is smaller by a constant factor, and its average is known with remarkable precision.

::: theorem {#thm:heilbronn title="The average number of steps" status="classical" ledger="GIN-PROP-040"}
For fixed $n$, the average number of division steps over $1 \le m < n$ with $\gcd(m, n) = 1$ is $\frac{12 \ln 2}{\pi^2} \ln n + C_P + \Oh(n^{-1/6+\epsilon})$, where $C_P \approx 1.4671$ is Porter's constant \cite{heilbronn1969,dixon1970,porter1975}.
:::

Measured counts for prime $n$ agree with this formula *after* an exact offset of one step (\ledger{GIN-OBS-011}): the classical count $\tau_n$ applies the algorithm to $(m, n)$ with $m < n$, whose first step merely swaps the arguments, while the SDK starts at $(n, m)$. The difference is a convention of counting, and the book reports it rather than correcting it away:

```python run
import math
from ginsdk import numbertheory as nt

c = 12 * math.log(2) / math.pi ** 2
for n in (1009, 10007, 100003):
    avg = sum(nt.euclid_steps(n, m) for m in range(1, n)) / (n - 1)
    print(f"n = {n:6d}: measured {avg:.4f}   formula {c * math.log(n) + 1.4670780794:.4f}   difference {avg - c * math.log(n) - 1.4670780794:+.4f}")
```

```output
n =   1009: measured 6.2877   formula 7.2962   difference -1.0086
n =  10007: measured 8.2308   formula 9.2298   difference -0.9991
n = 100003: measured 10.1704   formula 11.1698   difference -0.9994
```

## Stein's binary algorithm {#sec:binary-gcd}

Division is the most expensive of the four operations in hardware (Chapter 19). Stein's algorithm \cite{stein1967} replaces it by subtraction, halving and comparison, which are cheap on binary words. Its moves on a pair of positive integers are: *halve both* while both are even (recording a factor $2$); *halve* an even component; *subtract* the smaller odd component from the larger.

::: proposition {#prop:binary-gcd-bound title="An iteration bound for the binary algorithm" status="proved-here" ledger="GIN-PROP-076"}
On odd $a$ and positive $b$, each iteration of the main loop of Stein's algorithm (halve $b$ until odd, order the pair, subtract) at least halves the product of the two components. Hence the number of subtractions is at most $\log_2(ab) + 1$.
:::

::: proof
At the start of an iteration both components are odd after halving $b$, say $a \le b$. The subtraction replaces $b$ by $b - a$, which is even, and the next iteration halves it at least once: $b' \le (b - a)/2 < b/2$, while $a$ is unchanged. So the product $a b'$ is less than half of $ab$. The product is a positive integer while the loop runs, so the number of iterations is at most $\log_2(ab) + 1$.
:::

```python run
import random
from ginsdk import numbertheory as nt

rng = random.Random(7)
worst, total, total_e = 0.0, 0, 0
for _ in range(3000):
    a, b = rng.getrandbits(64) | 1, rng.getrandbits(64) | 1
    g, moves = nt.binary_gcd_trace(a, b)
    subs = moves.count("subtract")
    worst = max(worst, subs / ((a * b).bit_length()))
    total += subs
    total_e += nt.euclid_steps(a, b)
print("largest subtractions / log2(ab) observed:", round(worst, 3))
print(f"mean over 3000 pairs of 64-bit odd numbers: {total / 3000:.1f} subtractions (binary) vs {total_e / 3000:.1f} divisions (Euclid)")
```

```output
largest subtractions / log2(ab) observed: 0.433
mean over 3000 pairs of 64-bit odd numbers: 45.4 subtractions (binary) vs 37.7 divisions (Euclid)
```

The binary algorithm takes *more* steps than Euclid's — about $45$ against $38$ on 64-bit inputs — and is often faster anyway, because each of its steps is a subtraction and a shift instead of a division. Comparing algorithms by step counts alone compares the grammars of their runs, not their costs; the cost needs the model of the machine that executes a step (Chapter 36).

::: demo euclid
Text alternative: enter two integers; the widget runs the Euclidean algorithm and the extended algorithm, prints every row $(r, s, t, q)$ with the invariant $r = sa + tb$ checked at each row, and reports the gcd, the Bézout coefficients and the number of steps.
:::

::: exercise {#ex:euclid-fib}
Run the extended algorithm on $(F_{12}, F_{11}) = (144, 89)$. What are the Bézout coefficients, and what do you notice about them?
:::

::: solution {of="ex:euclid-fib"}
Ten division steps, with quotient $1$ in the first nine and $2$ in the last; $\gcd = 1 = 34 \cdot 144 - 55 \cdot 89$. The coefficients are themselves Fibonacci numbers up to sign — a consequence of Cassini's identity $F_{n+1}F_{n-1} - F_n^2 = (-1)^n$.
:::

::: exercise {#ex:euclid-dioph}
Find all integer solutions of $240x + 46y = 6$, and show that $240x + 46y = 5$ has none.
:::

::: solution {of="ex:euclid-dioph"}
$\gcd = 2 = -9 \cdot 240 + 47 \cdot 46$, so $(x, y) = (-27, 141)$ is a solution of $240x + 46y = 6$, and all solutions are $(-27 + 23k, 141 - 120k)$, $k \in \Z$. Since $2 \ndivides 5$, the second equation fails the image condition.
:::

::: exercise {#ex:euclid-bits}
Explain why the proof of \ref{thm:euclid-bits} would fail if each division cost $\Theta(L^2)$ regardless of the quotient, and which implementations of division have that property.
:::

::: summary
- Euclid's algorithm is a transition system: states $(a, b)$, one move $(a, b) \to (b, a \bmod b)$ admissible iff $b \neq 0$, invariant $\gcd$, measure $b$.
- Lamé: $k$ steps need $a \ge F_{k+2}$; Fibonacci pairs are the worst case; $k \le \log_\varphi a + \Oh(1)$ (checked for all pairs below $2000$).
- The extended algorithm keeps the invariant $r_i = s_i a + t_i b$ and solves linear congruences and Diophantine equations; it decides admissibility and solves in one run.
- Steps are not cost: Euclid uses $\Oh(L)$ steps but $\Oh(L^2)$ bit operations, because the quotients' logarithms sum to at most $L$ (measured: limb operations roughly quadruple when $L$ doubles).
- The average step count follows Heilbronn–Dixon–Porter, with an exact one-step convention offset in the SDK's count.
- Stein's binary algorithm halves the product $ab$ per iteration; it takes more steps than Euclid's and cheaper ones.
:::
