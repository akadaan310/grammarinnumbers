# The arithmetic laboratory

Every widget on this page computes live in your browser with `gin-core.js`, a second implementation of the book's reference semantics. It is not an illustration: on a fixture set of 972 expression–domain pairs exported from the Python SDK, the book's test suite requires it to agree with the SDK exactly — status, layer, displayed value and floating-point flags — and the build fails otherwise. Each widget has a written description that remains authoritative if JavaScript is unavailable.

<div class="lab-section">

## Inspect an expression, layer by layer {#sec:lab-arith}

::: demo arith
Text alternative: enter an arithmetic expression and choose a domain. The laboratory reports (1) whether the string is well formed and its tokens; (2) whether every literal names an element of the domain; (3) what exact mathematics prescribes in the corresponding exact domain — a value, *no solution* (for example `1 / 0`: no $c$ satisfies $0 \cdot c = 1$), or *non-unique* (for example `0 / 0`: every $c$ satisfies $0 \cdot c = 0$); (4) what the selected machine or language does — a value, an IEEE special datum with flags, a trap, an exception, or undefined behaviour; (5) how the machine relates to the mathematics: agrees, rounds, wraps, totalizes, selects, signals. It also draws the parse tree, the representation of the result, and the step trace. The same analysis is available offline as `python3 -m ginsdk inspect "1 / 0" --domain "int32 RISC-V"`.
:::

</div>
<div class="lab-section">

## One expression, every machine {#sec:lab-machines}

::: demo machines
Text alternative: the same expression evaluated in eighteen domains side by side — exact ℕ, ℤ, ℚ and ℤ/n; IEEE binary16, binary32, binary64 and JavaScript numbers; Python; JavaScript BigInt; and 32-bit integers under x86-64, AArch64, RISC-V, ISO C, Java, Rust (debug) and Go semantics. For `1 / 0` the table shows no solution (exact domains), `Infinity` with divideByZero (IEEE), ZeroDivisionError (Python), a trap (x86-64), $0$ (AArch64), $-1$ (RISC-V), undefined behaviour (C), and exceptions or panics (Java, Rust, Go, BigInt). See Chapter 24.
:::

</div>
<div class="lab-section">

## Binary addition and the carry monoid {#sec:lab-carry}

::: demo carry
Text alternative: two numbers are written in binary, position by position. Each position is classified as **K** (kill: both bits 0, the carry out is 0), **P** (propagate: one bit 1, the carry passes through) or **G** (generate: both bits 1, the carry out is 1). The carry into each position is the result of composing these three maps from the lowest position upward. For $11 + 1$ in eight bits: positions 0 and 1 propagate a carry generated at position 0, giving $1100_2 = 12$. See Chapter 11.
:::

</div>
<div class="lab-section">

## Floating-point encodings {#sec:lab-float}

::: demo float
Text alternative: a decimal number is converted exactly to a rational and rounded once to binary16, binary32 and binary64, showing the sign, exponent and fraction fields, whether rounding occurred, and the exact stored value. For `0.1` every format rounds: $0.1$ is not a dyadic rational. See Chapter 25.
:::

</div>
<div class="lab-section">

## Division in ℤ/n {#sec:lab-zmod}

::: demo zmod
Text alternative: a table with one row per divisor $b$ and one column per dividend $a$ in ℤ/n. A cell shows the unique quotient, ∅ when $b c \equiv a$ has no solution (image failure), or the number of solutions when there are several (kernel failure). In ℤ/6 the rows $b = 1$ and $b = 5$ (the units) are complete; row $b = 0$ has one solvable column ($a = 0$, with six solutions); exactly $n\varphi(n) = 12$ of the 36 pairs have a unique quotient. See Chapter 16.
:::

</div>
<div class="lab-section">

## The numerals of a number {#sec:lab-numerals}

::: demo numerals
Text alternative: a natural number $n$ written in unary (as a successor term), bijective base 2, binary, ternary, balanced ternary, decimal and hexadecimal, together with its address in the heap grammar of Computational Grammar Theory (node $n + 1$). The value is invariant; only the word changes. Zero's canonical numeral is the empty word. See Chapters 5–7.
:::

</div>
<div class="lab-section">

## Euclid's algorithm with its invariant {#sec:lab-euclid}

::: demo euclid
Text alternative: the extended Euclidean algorithm on two integers, one row per step $(a, b) \to (b, a \bmod b)$, with Bézout coefficients $s, t$ and a check that $r = s a + t b$ holds at every row. For $1071$ and $462$: three division steps, $\gcd = 21 = -3 \cdot 1071 + 7 \cdot 462$. See Chapter 33.
:::

</div>
<div class="lab-section">

## Measured cost of big-number arithmetic {#sec:lab-cost}

::: demo cost
Text alternative: a log–log plot of counted 32-bit limb operations against operand length (64 to 16,384 bits) for addition, schoolbook and Karatsuba multiplication, division, Euclid's gcd and modular exponentiation, from the stored results of GIN-EXP-008. The measured slopes are about 1 (addition), 2 (schoolbook multiplication and division), 1.6 (Karatsuba; the theory says $\log_2 3 \approx 1.585$) and 3 (modular exponentiation). See Chapter 37.
:::

</div>
