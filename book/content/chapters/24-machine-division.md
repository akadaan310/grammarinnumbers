---
title: "Integer Division by Zero on Real Machines"
status: mixed
statusnote: The behaviours are specified by architecture and language documents; the measurements are this book's, on one host (x86-64 natively, AArch64 and RISC-V under QEMU emulation).
description: What x86-64, AArch64, RISC-V, ISO C, Java, Rust, Go, Python and JavaScript actually do with x / 0 and with INT_MIN / −1 — from their specifications, measured natively on x86-64, and emulated for AArch64 and RISC-V — together with the SDK's models of each and their agreement with execution.
epigraph: "Ask seven toolchains on one computer to divide one by zero and you receive seven different answers, two of which look like numbers."
---

::: objectives
- State the behaviour of integer division at its two boundaries, $x/0$ and $-2^{w-1}/-1$, for three instruction sets and six languages, and cite where each is specified.
- Distinguish specified behaviour from behaviour measured on a host and from behaviour emulated by an independent implementation.
- Explain the design rationale of trapping (x86) and of totalizing (AArch64, RISC-V) instruction sets.
- Use the SDK's machine models, and know on what evidence they rest.
:::

## Two boundaries {#sec:two-boundaries}

Signed integer division on $w$-bit words has exactly two inputs at which the mathematical quotient is not a representable word: a zero divisor (no quotient exists, or every value is one) and $-2^{w-1} / -1$ (the quotient $2^{w-1}$ exists in $\Z$ but is one too large). Each system must decide what to do at both.

| system | $x / 0$ | $-2^{31} / -1$ | source; evidence |
|---|---|---|---|
| x86-64 `idiv` | `#DE` trap; Linux delivers `SIGFPE` | `#DE` trap | Intel SDM \cite{intelsdm}; measured via C |
| AArch64 `sdiv` | $0$, no signal, no flag | $-2^{31}$ (wraps) | Arm ARM \cite{armarm}; **emulated** (QEMU) |
| RISC-V `div` | $-1$; `rem` gives the dividend | $-2^{31}$; `rem` gives $0$ | RISC-V ISA \cite{riscv}; **emulated** (QEMU) |
| ISO C `int` | undefined behaviour | undefined behaviour | C17 §6.5.5 \cite{isoc17}; gcc on x86: `SIGFPE` |
| Java `int` | `ArithmeticException` | $-2^{31}$, no exception | JLS §15.17.2 \cite{jls21}; measured |
| Rust `i32` (debug and release) | panic: attempt to divide by zero | panic: attempt to divide with overflow | Rust reference \cite{rustref}; measured |
| Rust `checked_div` | `None` | `None` | measured |
| Go `int32` | run-time panic | $-2^{31}$, no panic | Go spec \cite{gospec}; measured |
| Python `int` `//` | `ZeroDivisionError` | $2^{31}$ (unbounded integers) | Python reference \cite{pyref}; measured |
| JavaScript BigInt | `RangeError` | $2^{31}$ | ECMA-262 \cite{ecma262}; measured |

Rust is the only system in the table that treats both boundaries the same way in both build modes; Go and Java treat them differently (an error for $x/0$, silent wraparound for $-2^{31}/-1$); x86 traps on both for reasons that go back to its double-width divide (Chapter 23).

## Measured on x86-64 {#sec:measured}

GIN-EXP-004 ran each toolchain on the session host with operands supplied at run time. The SDK's machine models agree with every behaviour that could be measured there (\ledger{GIN-IMP-002}). The experiment's raw records are part of the repository:

```python run
import json, pathlib, ginsdk
data = json.loads((pathlib.Path(ginsdk.__file__).parents[3] / "experiments/results/exp004.json").read_text())["data"]
rows = [("C gcc -O0, int 1/0", data["c_gcc"]["-O0"]["int 1/0"]), ("C gcc -O0, int MIN/-1", data["c_gcc"]["-O0"]["int INT_MIN/-1"]),
        ("Java, int 1/0", data["java"]["int 1/0"]), ("Java, int MIN/-1", data["java"]["int MIN/-1"]),
        ("Go, int32 1/0", data["go"]["int32 1/0"]), ("Go, int32 MIN/-1", data["go"]["int32 MIN/-1"]),
        ("Rust debug, 1/0", data["rust_debug"]["div 1/0"]), ("Rust debug, checked 1/0", data["rust_debug"]["checked 1/0"])]
for label, r in rows:
    segments = [x.strip() for x in r["stderr"].split("|")]
    shown = r["signal"] or r["stdout"] or next(x for x in segments if "divide by zero" in x)
    print(f"{label:25s} exit {r['exit']:4d}  {shown[:60]}")
print(f"{'Python, 1/0':25s} {data['python']['1/0']}")
print(f"{'JavaScript, 1n/0n':25s} {data['javascript']['1n/0n']}")
agree = data["model_agreement"]
print("model agreement:", sum(agree.values()), "of", len(agree))
```

```output
C gcc -O0, int 1/0        exit   -8  SIGFPE
C gcc -O0, int MIN/-1     exit   -8  SIGFPE
Java, int 1/0             exit    0  ArithmeticException: / by zero
Java, int MIN/-1          exit    0  -2147483648
Go, int32 1/0             exit    2  panic: runtime error: integer divide by zero
Go, int32 MIN/-1          exit    0  -2147483648
Rust debug, 1/0           exit  101  attempt to divide by zero
Rust debug, checked 1/0   exit    0  None
Python, 1/0               ZeroDivisionError: division by zero
JavaScript, 1n/0n         RangeError: Division by zero
model agreement: 14 of 14
```

::: observation {#obs:go-java title="Asymmetric treatment of the two boundaries" status="empirical" ledger="GIN-OBS-005"}
On the host, Go and Java return $-2^{31}$ for `int32` $-2^{31}/-1$ without any signal, while raising an error for division by zero; Rust panics on both in debug and release builds; C on x86 receives `SIGFPE` for both (GIN-EXP-004).
:::

## Emulated: AArch64 and RISC-V {#sec:emulated}

No AArch64 or RISC-V hardware was available. The first edition of the research ledger therefore marked these models "specification only" (GIN-OPEN-009). For this edition, GIN-EXP-014 compiled a freestanding probe (no C library; results written with a raw system call; the floating-point status register read directly) for both architectures and ran it under QEMU's user-mode emulation. QEMU is an independent implementation of the two instruction sets, so agreement tests the SDK's models against something other than their own source documents; it is not a measurement of silicon.

```python run
import json, pathlib, ginsdk
data = json.loads((pathlib.Path(ginsdk.__file__).parents[3] / "experiments/results/exp014.json").read_text())["data"]
print("emulator:", data["versions"]["qemu-aarch64"])
for isa in ("aarch64", "riscv64"):
    r = data[isa]
    zero = [(x["a"], x["quotient"], x["remainder"]) for x in r["int"] if x["b"] == 0]
    mn = [x for x in r["int"] if x["a"] == -2 ** 31][0]
    print(f"{isa:8s} x/0 -> (a, q, r): {zero}   MIN/-1 -> {mn['quotient']}   model agreement {r['model_agreement']}")
```

```output
emulator: qemu-aarch64 version 8.2.2 (Debian 1:8.2.2+ds-0ubuntu1.18)
aarch64  x/0 -> (a, q, r): [(1, 0, 1), (0, 0, 0), (-7, 0, -7)]   MIN/-1 -> -2147483648   model agreement 8/8
riscv64  x/0 -> (a, q, r): [(1, -1, 1), (0, -1, 0), (-7, -1, -7)]   MIN/-1 -> -2147483648   model agreement 8/8
```

::: implementation {#imp:isa-models title="ISA models agree with an emulator" status="implementation" ledger="GIN-IMP-008"}
The SDK's AArch64 and RISC-V division models agree with QEMU 8.2.2 on all probed cases (8 signed and 8 unsigned 32-bit divisions each, including $x/0$ and $-2^{31}/-1$). On AArch64, which has no remainder instruction, C's `%` compiles to `sdiv` followed by `msub` ($a - qb$ modulo $2^{32}$); for a zero divisor it therefore yields the dividend, as on RISC-V, although by a different route.
:::

## Why some machines trap and others do not {#sec:rationale}

Trapping and totalizing are both reasonable designs; they place the cost of division by zero in different places.

- **Trapping** (x86) guarantees that no program silently continues with a meaningless quotient. The cost is that every division is a potential control transfer, which complicates out-of-order execution, and that languages which want to *return* an error instead of crashing must test the divisor anyway.
- **Totalizing** (AArch64, RISC-V) keeps division an ordinary data operation with no side effects. The RISC-V specification says so explicitly: the chosen results are what a simple divider produces, and a language that needs an exception can insert a single branch before the division \cite{riscv}. Chapter 19 proved that a test-free restoring divider indeed returns all ones (\ledger{GIN-PROP-023}). The cost is moved to software, which must remember to test.

Languages then add their own layer. Java and Go always test (by hardware trap or software check) and raise a language-level error; Rust's debug and release builds both panic; Python never reaches the hardware for a zero divisor. C alone adds nothing, and leaves the behaviour undefined — which, as Chapter 23 showed, licenses the optimizer to assume the divisor is not zero.

::: exercise {#ex:md-port}
A C program computes `int q = a / b;` and is known to run correctly on x86-64 Linux, where a zero divisor crashes it. It is ported to AArch64. What can change, and what single change to the source makes the behaviour the same on both, and defined?
:::

::: solution {of="ex:md-port"}
On AArch64 a zero divisor no longer crashes: the program continues with $q = 0$, and an optimizer may also have removed later checks. The portable fix is to test `b == 0` (and, for signed types, `a == INT_MIN && b == -1`) *before* dividing, and to handle the case explicitly.
:::

::: exercise {#ex:md-remainder}
Using the table and Implementation \ref{imp:isa-models}, give the value of `a % 0` in C compiled for AArch64 and for RISC-V, and say why neither is a remainder in the sense of the division theorem.
:::

::: solution {of="ex:md-remainder"}
Both yield $a$: RISC-V's `rem` is specified to return the dividend, and on AArch64 `msub` computes $a - 0 \cdot b = a$. The division theorem requires $|r| < |b| = 0$, which no $r$ satisfies; the value is a totalization (and in ISO C the expression is undefined anyway).
:::

::: summary
- Integer division has two boundaries: $x/0$ and $-2^{w-1}/-1$; systems treat them differently, and some treat the two differently from each other.
- On x86-64 the toolchains measured trap, raise, panic or (Python, BigInt) never overflow; the SDK's models agree with all 14 measurable behaviours.
- Under QEMU, AArch64 returns $0$ and RISC-V $-1$ for $x/0$, as specified; the models agree 8/8. This is emulator evidence, not hardware.
- Trapping and totalizing are both reasonable; they move the cost of the boundary between hardware and software.
:::
