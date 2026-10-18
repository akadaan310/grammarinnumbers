---
title: "From Symbol to Instruction"
status: mixed
statusnote: Compiler structure is standard; the traces, instruction selections and optimizer behaviour shown are measured on one host and recorded in GIN-EXP-004.
description: The journey of x / y from characters to a machine instruction — lexing, parsing, typing, intermediate representation, optimization, instruction selection, execution — traced in CPython and in a C compiler, with the measured instruction for each of three architectures and two types; and what an optimizer may do with an operation whose failure is undefined.
epigraph: "The slash in x / y is a promise of an operation. Seven stages later it is one of six different instructions, or none at all."
---

::: objectives
- Name the stages through which an arithmetic expression becomes machine execution, and say what each stage decides.
- Read the measured parse tree and bytecode of `x / y` in CPython and the instructions selected by clang for x86-64, AArch64 and RISC-V.
- Explain how operand types select between integer division, unsigned division and floating-point division.
- Explain why a C compiler may delete a zero test that follows a division, and show that two compilers measurably differ in whether they do.
:::

## Seven stages {#sec:stages}

1. **Lexical analysis.** The characters `x / y` become three tokens: identifier, operator, identifier.
2. **Parsing.** The tokens become a tree: a binary node for division with two leaves. Precedence and associativity (Chapter 8) are decided here.
3. **Typing.** The types of the operands select the *operation*: integer division, unsigned division, floating-point division, big-integer division, or an error. In Python 3, `int / int` is *true* division and returns a float; in C, Java, Go and Rust it is truncating integer division.
4. **Intermediate representation.** The tree is lowered to a sequence of simple operations — bytecode for an interpreter, an SSA-form IR for an optimizing compiler.
5. **Optimization.** The IR is transformed: constants are folded, divisions by constants become multiplications (Chapter 19), redundant computations are removed — under the rules of the language, including its rules about undefined behaviour.
6. **Instruction selection.** Each IR operation is mapped to instructions of the target architecture.
7. **Execution.** The processor runs the instructions. Division by zero, overflow, rounding and flags happen here — or have been anticipated, or excluded, by earlier stages.

In the four-layer vocabulary of this book, stages 1–2 are *syntax*, stage 3 is *typing*, the mathematical *semantics* is what stages 4–6 must preserve, and stage 7 is *execution*. The stages of a compiler are not the layers of meaning, but they line up with them.

## In CPython {#sec:cpython}

Python's own tools expose the first stages. The parse tree is stable across recent versions:

```python run
import ast
print(ast.dump(ast.parse("x / y", mode="eval").body))
print(ast.dump(ast.parse("-7 // 2", mode="eval").body))
```

```output
BinOp(left=Name(id='x', ctx=Load()), op=Div(), right=Name(id='y', ctx=Load()))
BinOp(left=UnaryOp(op=USub(), operand=Constant(value=7)), op=FloorDiv(), right=Constant(value=2))
```

The second tree confirms Chapter 8's convention: `-7 // 2` is unary minus applied to `7`, then floor division. The bytecode, which differs between CPython versions, was recorded by GIN-EXP-004 with CPython 3.13: `RESUME; LOAD_NAME x; LOAD_NAME y; BINARY_OP /; RETURN_VALUE`. A single generic instruction, `BINARY_OP /`, defers the choice of operation to run time, when the interpreter inspects the operand types: for two `int`s it computes a correctly rounded float quotient; for a zero divisor it raises `ZeroDivisionError` before any IEEE operation is attempted (\ledger{GIN-OBS-006}).

## In a C compiler: instruction selection {#sec:isel}

An optimizing compiler resolves the operation statically from the types. GIN-EXP-004 compiled the same three one-line C functions with clang 18 at `-O2` for three targets and recorded the instructions:

```python run
import json, pathlib, ginsdk
data = json.loads((pathlib.Path(ginsdk.__file__).parents[3] / "experiments/results/exp004.json").read_text())
for target, fns in data["data"]["instruction_selection"].items():
    picked = {k: [i.split("\t")[0] for i in v if i.split("\t")[0] in ("idivl", "divl", "divsd", "sdiv", "udiv", "fdiv", "divw", "divuw", "fdiv.d")] for k, v in fns.items()}
    print(f"{target:20s} int: {picked['idiv'][0]:6s} unsigned: {picked['udiv'][0]:6s} double: {picked['fdiv'][0]}")
```

```output
x86_64-linux-gnu     int: idivl  unsigned: divl   double: divsd
aarch64-linux-gnu    int: sdiv   unsigned: udiv   double: fdiv
riscv64-linux-gnu    int: divw   unsigned: divuw  double: fdiv.d
```

::: observation {#obs:isel title="One symbol, six instructions per architecture family" status="empirical" ledger="GIN-OBS-007"}
For `int`, `unsigned` and `double` operands, clang 18 at `-O2` selects `idivl`/`divl`/`divsd` on x86-64, `sdiv`/`udiv`/`fdiv` on AArch64 and `divw`/`divuw`/`fdiv.d` on RISC-V 64 (GIN-EXP-004; compiled, not executed, for the non-x86 targets).
:::

The x86 integer sequence is `cltd; idivl`: the first instruction sign-extends the 32-bit dividend into the 64-bit register pair that `idiv` divides. That detail is the instruction set's own grammar showing through — the x86 divide instruction divides a double-width number by a single-width one, which is why its quotient can overflow (the case $-2^{31}/-1$) and why the instruction can trap for a reason other than division by zero.

## What the optimizer may assume {#sec:ub}

In ISO C, a division by zero, and a signed division whose quotient is not representable, have *undefined behaviour* (C17 §6.5.5). The standard imposes no requirement on such a program — and an optimizer may therefore assume that they do not happen. Consider:

```c
int f(int a, int b) {
    int q = a / b;
    if (b == 0) return -1;
    return q;
}
```

The test comes *after* the division. If $b = 0$, the division has already made the behaviour of the whole program undefined, so the compiler may reason: in every execution with defined behaviour, $b \ne 0$ at the test; the test is always false; delete it.

::: observation {#obs:ub-guard title="Compilers differ on deleting a zero test after a division" status="empirical" ledger="GIN-OBS-008"}
On the session host, clang 18.1.3 at `-O2` and `-O3` compiles `f` to `cltd; idivl; retq` — the test and the `-1` path are deleted — while gcc 13.3 at `-O2` keeps them (`idivl; testl; movl $-1; cmove`). Both are conforming (GIN-EXP-004).
:::

```python run
import json, pathlib, ginsdk
data = json.loads((pathlib.Path(ginsdk.__file__).parents[3] / "experiments/results/exp004.json").read_text())
for compiler, r in data["data"]["c_guard_after_division"].items():
    body = "; ".join(i.replace("\t", " ") for i in r["instructions"] if not i.startswith(("endbr", "push", "pop", "mov %rsp")))
    print(f"{compiler:10s} keeps the zero test: {r['has_compare_or_test']!s:5s}  {body[:90]}")
```

```output
gcc -O0    keeps the zero test: True   movq %rsp, %rbp; movl %edi, -20(%rbp); movl %esi, -24(%rbp); movl -20(%rbp), %eax; cltd; i
gcc -O2    keeps the zero test: True   movl %edi, %eax; cltd; idivl %esi; testl %esi, %esi; movl $-1, %edx; cmove %edx, %eax; ret
clang -O2  keeps the zero test: False  movl %edi, %eax; cltd; idivl %esi; retq
clang -O3  keeps the zero test: False  movl %edi, %eax; cltd; idivl %esi; retq
```

On x86-64 the difference is invisible in practice: the `idivl` traps when $b = 0$, before either version reaches the test. On AArch64, whose `sdiv` returns $0$ instead of trapping, the deleted test would change observable behaviour: gcc's version returns $-1$, clang's returns $0$. A programmer who wrote the test to *catch* division by zero has been told, by the language standard, that the test is too late; the compiler that removes it is not wrong. The repair is to test *before* dividing.

::: counterexample {#neg:ub-delete title="Compilers always exploit undefined division to delete later tests" status="counterexample" ledger="GIN-NEG-004"}
gcc 13.3 at `-O2` keeps the zero test in `f`; only clang 18 deletes it. Undefined behaviour *permits* the optimization; it does not require it, and different compilers (and versions, and flags) make different choices.
:::

## Constants at compile time {#sec:constants}

When the divisor is a *constant* zero, the failure can be detected before the program runs — and languages choose different layers for it. GIN-EXP-004 compiled `1 / 0` with integer operands in four languages:

| language | compile time | run time |
|---|---|---|
| C (gcc 13.3) | warning `division by zero [-Wdiv-by-zero]`; compiles | `SIGFPE` (x86 `#DE`) |
| Go | error: `invalid operation: division by zero` | — |
| Rust | error: `this operation will panic at runtime` | — |
| Java | compiles without warning | `ArithmeticException: / by zero` |

The same five characters fail at the typing layer in Go and Rust (constant expressions are checked as part of type checking), at execution in Java, and at execution with undefined meaning in C (\ledger{GIN-OBS-004}). In the vocabulary of Chapter 8, Go and Rust apply the *restriction* repair statically; Java and C defer to the execution layer.

::: exercise {#ex:sti-types}
For each language, give the operation selected by `7 / 2` with integer literals and the result: C, Java, Python 3, JavaScript (Number), JavaScript (BigInt `7n / 2n`).
:::

::: solution {of="ex:sti-types"}
C and Java: truncating integer division, $3$. Python 3: true division to binary64, $3.5$. JavaScript Number: IEEE division, $3.5$. JavaScript BigInt: truncating division, $3$n.
:::

::: exercise {#ex:sti-ub}
Rewrite `f` so that every conforming compiler must keep the zero test, and explain why your version has no undefined behaviour for $b = 0$. Is it still undefined for some input?
:::

::: solution {of="ex:sti-ub"}
`if (b == 0) return -1; return a / b;` — for $b = 0$ the division is never reached. It is still undefined for $a = $ `INT_MIN`, $b = -1$, which needs its own test.
:::

::: exercise {#ex:sti-cltd}
Why does the x86 division need `cltd` before `idivl`, and how does this explain that `idiv` can trap when the divisor is not zero?
:::

::: solution {of="ex:sti-cltd"}
`idivl` divides the 64-bit value in `edx:eax` by a 32-bit operand and must place a 32-bit quotient in `eax`. `cltd` sign-extends `eax` into `edx`. If the true quotient does not fit in 32 bits — as for $-2^{31} / -1 = 2^{31}$ — the instruction raises `#DE`, the same exception as for a zero divisor.
:::

::: summary
- An expression passes through lexing, parsing, typing, IR, optimization, instruction selection and execution; types choose the operation.
- CPython defers the choice to run time (`BINARY_OP /`); a C compiler selects one of `idivl`, `divl`, `divsd`, `sdiv`, `udiv`, `fdiv`, `divw`, `divuw`, `fdiv.d`.
- Because C division by zero is undefined, clang 18 deletes a zero test placed after the division and gcc 13.3 keeps it; both conform.
- Constant `1 / 0` fails at compile time in Go and Rust, at run time in Java, and with undefined meaning in C.
:::
