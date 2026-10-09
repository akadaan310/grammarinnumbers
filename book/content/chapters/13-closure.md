---
title: "Closure, Partiality, and the Price of Totality"
status: mixed
statusnote: The closure properties are classical; the exhaustive law census of 8-bit wrapping and saturating arithmetic is computed here.
description: Where each arithmetic operation is total, partial, or closed across ℕ, ℤ, ℚ, ℝ, ℂ and ℤ/n; four ways machines and languages make subtraction total — wraparound, saturation, truncation, signalling — and exactly which algebraic laws each one keeps, checked exhaustively on 8-bit integers.
epigraph: "A total operation is a promise that an answer always exists. Every way of keeping that promise is paid for in some other law."
---

::: objectives
- Tabulate the closure of $+, -, \times, /, \sqrt{\ }$ over the main number systems, and name the kind of failure where an operation is not closed.
- Compare four totalizations of fixed-width subtraction by the laws they preserve.
- Prove, by exhaustive computation, that saturating 8-bit addition is commutative but not associative, and quantify how often associativity fails.
- Explain why the choice of totalization matters to compilers and to programmers.
:::

## A closure table {#sec:closure-table}

For each number system and operation, the entry gives the outcome of the converse classification of Chapter 9: total (✓), or which kind of failure occurs and where.

| | $+$ | $\times$ | $-$ | $/$ | $\sqrt{\ }$ (non-negative branch) |
|---|---|---|---|---|---|
| $\N$ | ✓ | ✓ | no solution when $a < b$ | no solution unless $b \ne 0$, $b \mid a$; non-unique at $0/0$ | no solution unless $a$ is a square |
| $\Z$ | ✓ | ✓ | ✓ | as in $\N$ | no solution for $a < 0$ or non-squares |
| $\Q$ | ✓ | ✓ | ✓ | no solution at $b = 0$, $a \ne 0$; non-unique at $0/0$ | no solution unless $a$ is a rational square |
| $\R$ | ✓ | ✓ | ✓ | as in $\Q$ | no solution for $a < 0$; the branch selects $\ge 0$ |
| $\C$ | ✓ | ✓ | ✓ | as in $\Q$ | ✓ with a branch (two roots for $a \ne 0$) |
| $\Z/n$ | ✓ | ✓ | ✓ | no solution or non-unique when $\gcd(b, n) > 1$ | depends on $a$ and $n$ (Chapter 29) |
| $\Z/p$, $p$ prime | ✓ | ✓ | ✓ | as in $\Q$ | about half the non-zero elements are squares |

Two patterns stand out. Subtraction stops failing as soon as negative numbers exist, and never fails again; division by zero fails in every row; and the *kind* of failure of division by zero — no solution for $a \ne 0$, non-unique for $a = 0$ — is the same in every row. Chapter 16 proves that it must be.

## Four ways to make subtraction total {#sec:four-ways}

On a machine, numbers have a fixed width, and even $\Z$-subtraction can leave the representable range. The systems in use handle this in four ways.

| totalization | $w$-bit result of $a - b$ when the exact result does not fit | used by |
|---|---|---|
| **wraparound** (quotient) | the exact result reduced modulo $2^w$ | hardware `sub`; Java, Go; Rust release builds; C unsigned |
| **saturation** (clamp) | the nearest representable value | DSP and SIMD saturating instructions; some graphics code |
| **truncation** ($\monus$, for unsigned) | $0$ when $a < b$ | Peano arithmetic; `saturating_sub` on unsigned values |
| **signal** | no value: exception, trap or panic | Rust debug builds; checked arithmetic; Python never needs it |

(A fifth answer, ISO C's for *signed* overflow, is not a totalization at all: the behaviour is undefined, so a program that overflows has no meaning.)

Each is reasonable, and each preserves different laws. Which laws?

::: proposition {#prop:law-census title="Laws kept by wraparound and by saturation (8-bit census)" status="proved-here" ledger="GIN-PROP-062"}
On 8-bit signed integers $[-128, 127]$:
1. wraparound addition $a \oplus b = \wrap(a + b)$ forms an abelian group, and wraparound $+$ and $\times$ form a commutative ring: it is the ring $\Z/256$ with the signed labels;
2. saturating addition $a \boxplus b = \max(-128, \min(127, a + b))$ is commutative and has identity $0$, but is **not associative**: exactly $4\,177\,792$ of the $2^{24}$ triples $(a, b, c)$ — about $24.9\%$ — satisfy $(a \boxplus b) \boxplus c \ne a \boxplus (b \boxplus c)$;
3. saturating addition has no inverse for $-128$, and saturating multiplication does not distribute over saturating addition.
:::

::: proof
(1) Reduction modulo $256$ is a ring homomorphism $\Z \to \Z/256$, and the signed labels are a bijection with $\Z/256$. (2) Commutativity and identity are inherited from $\Z$, since clamping is applied to the same exact sum. The associativity count is by exhaustive enumeration of all $2^{24}$ triples (reproduced below). (3) $-128 \boxplus b = 0$ requires $b = 128$, which is not representable; a counterexample to distributivity is $a = 2$, $b = 100$, $c = -100$: $2 \cdot (100 \boxplus -100) = 0$ but $(2 \cdot 100) \boxplus (2 \cdot -100)$ clamps to $127 \boxplus -128 = -1$.
:::

::: counterexample {#neg:sat-assoc title="Saturating addition is associative" status="counterexample" ledger="GIN-NEG-021"}
In 8-bit signed saturating arithmetic, $(100 \boxplus 100) \boxplus (-100) = 127 \boxplus (-100) = 27$, while $100 \boxplus (100 \boxplus (-100)) = 100 \boxplus 0 = 100$.
:::

```python run
lo, hi = -128, 127
sat = lambda x: max(lo, min(hi, x))
wrap = lambda x: (x - lo) % 256 + lo
R = range(lo, hi + 1)
bad_sat = sum(sat(sat(a + b) + c) != sat(a + sat(b + c)) for a in R for b in R for c in R)
bad_wrap = sum(wrap(wrap(a + b) + c) != wrap(a + wrap(b + c)) for a in R for b in R for c in R)
print(f"associativity failures, saturating: {bad_sat} of {256 ** 3} ({bad_sat / 256 ** 3:.2%})")
print(f"associativity failures, wraparound: {bad_wrap}")
print("example:", sat(sat(100 + 100) - 100), "vs", sat(100 + sat(100 - 100)))
```

```output
associativity failures, saturating: 4177792 of 16777216 (24.90%)
associativity failures, wraparound: 0
example: 27 vs 100
```

## Why the choice matters {#sec:why}

The census is not a curiosity. Associativity is what allows a compiler to evaluate $a + b + c + d$ as $(a + b) + (c + d)$ and use two adders in parallel, or to vectorize a sum. For wraparound integers the transformation is always valid, which is why compilers may freely reassociate unsigned C arithmetic and Java `int` arithmetic. For saturating arithmetic it is invalid, and code using saturating instructions must be evaluated in exactly the written order. For IEEE floating point it is also invalid (Chapter 25), which is why compilers do not reassociate floating-point sums unless explicitly permitted to (for example with "fast-math" options that trade exactness for speed).

ISO C's choice for signed integers is the most interesting. By making signed overflow *undefined*, the standard allows a compiler to assume it never happens, and therefore to treat signed arithmetic as the exact arithmetic of $\Z$ — reassociating, simplifying $x + 1 > x$ to *true*, and eliminating code that tests for overflow after the fact. The totalization is replaced by a promise from the programmer. Chapter 24 measures a compiler acting on such a promise.

::: exercise {#ex:cl-table}
Fill in the closure table row for the even integers $2\Z$ under $+$, $\times$, $-$, $/$.
:::

::: solution {of="ex:cl-table"}
$+$, $\times$, $-$: closed. $/$: $a/b$ for $a, b \in 2\Z$ has a solution in $2\Z$ iff $b \ne 0$ and $2b \mid a$ (e.g. $4/2 = 2$ but $2/2 = 1 \notin 2\Z$), and is non-unique at $0/0$.
:::

::: exercise {#ex:cl-sat-small}
For 2-bit signed saturating addition on $\{-2, -1, 0, 1\}$, count the non-associative triples by hand or by program.
:::

::: solution {of="ex:cl-sat-small"}
Enumerating the $64$ triples gives $10$ failures, e.g. $(1 \boxplus 1) \boxplus (-1) = 1 - 1 = 0$ versus $1 \boxplus (1 \boxplus -1) = 1$.
:::

::: exercise {#ex:cl-monus-assoc}
Is truncated subtraction associative on $\N$? Is it commutative? Give the laws it does satisfy that ordinary subtraction on $\Z$ also satisfies.
:::

::: solution {of="ex:cl-monus-assoc"}
Neither: $(3 \monus 2) \monus 1 = 0$ but $3 \monus (2 \monus 1) = 2$; $3 \monus 2 = 1 \ne 0 = 2 \monus 3$. It satisfies $a \monus 0 = a$, $a \monus a = 0$, $(a + b) \monus b = a$ and $(a \monus b) \monus c = a \monus (b + c)$, all of which hold for $-$ on $\Z$.
:::

::: summary
- Subtraction is closed from $\Z$ upward; division by zero fails in every number system, always in the same two ways.
- Machines make subtraction total by wraparound, saturation, truncation or signal; ISO C instead makes signed overflow undefined.
- Wraparound is the ring $\Z/2^w$ and keeps every ring law; saturating 8-bit addition is commutative but fails associativity on $24.9\%$ of triples, and has no inverse for $-128$.
- Associativity is what licenses reassociation and parallel evaluation; a totalization that loses it constrains compilers and programmers.
:::
