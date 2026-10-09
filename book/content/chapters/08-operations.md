---
title: "What an Operation Is: Domains, Layers, and Contracts"
status: mixed
statusnote: Operations as functions and relations are standard; the four-layer outcome model, the outcome vocabulary and operation contracts are this book's framework.
description: An operation as a relation with a domain and a codomain; closure and partiality; the grammar of arithmetic expressions and its conventions; the four layers of an outcome — syntax, typing, semantics, execution — and their independence; and the operation contract, a machine-readable statement of when an operation is admissible and what it costs.
epigraph: "Before asking what 7 / 2 is, ask: in which domain, by which definition, and under which machine?"
---

::: objectives
- Define an operation as a relation, and distinguish totality, functionality and closure.
- Parse arithmetic expressions with a precise grammar, and recognize where precedence and associativity are conventions that differ between systems.
- State the four layers of an arithmetic outcome and give, for each pair of layers, an expression that fails at one and passes the other.
- Read and write an operation contract: domain, precondition, defining equation, failure classes, cost model.
- Use the SDK's layered inspection to answer the nine interface questions about an expression.
:::

## Operations as relations {#sec:relations}

A binary operation on a set $A$ is usually defined as a function $A \times A \to A$. For arithmetic this definition is too narrow: it presupposes that every pair has a result, that the result is unique, and that it lies in $A$. Each presupposition fails somewhere in this book, and we want to talk about the failures. So we begin with relations.

::: definition {#def:operation title="Operation grammar" status="definition" ledger="GIN-DEF-014"}
A binary operation $\circ$ on a carrier $A$ induces the relation
$$
\sem{\circ} \subseteq (A \times A) \times A,
$$
and, for each fixed $b$, the *move* $\sem{\circ b} : a \mapsto a \circ b$. The operation is **total** if every pair is related to at least one result, **functional** if to at most one, and **closed** on $A$ if its results lie in $A$.
:::

::: definition {#def:closure title="Closure of a domain" status="definition" ledger="GIN-DEF-018"}
A domain is **closed** under an operation if the operation is admissible — total, functional, with results in the domain — at every pair of arguments. $\N$ is closed under $+$ and $\times$; $\Z$ is closed under $-$; $\Q \setminus \{0\}$ is closed under $/$; $\Z/p$ for prime $p$ is closed under division by non-zero elements.
:::

Read as relations, the four operations of school arithmetic fall into two families. Addition and multiplication are *forward* operations: given the arguments, there is a recipe that produces the result (primitive recursion, Chapter 4). Subtraction and division are *converse* operations: their results are defined by an equation — $a - b$ is the $c$ with $b + c = a$, and $a / b$ is the $c$ with $b \cdot c = a$ — and an equation may have no solution or many. Chapter 9 makes this precise. Here we need only the vocabulary.

## The grammar of expressions {#sec:expr-grammar}

Before an expression can be evaluated it must be *parsed*. The SDK and the laboratory use the following grammar, with precedence increasing downwards.

::: definition {#def:expr-grammar title="Arithmetic expression language" status="definition" ledger="GIN-DEF-060"}
```
expr   := term  (('+' | '-') term)*
term   := unary (('*' | '/' | '//' | '%' | 'mod') unary)*
unary  := ('+' | '-') unary-at-level-30 | power
power  := atom ('^' unary)?                    -- right-associative
atom   := NUMBER | NAME | '(' expr ')' | ('sqrt' | 'gcd') '(' expr (',' expr)* ')'
NUMBER := decimal integer | decimal fraction | 0b… | …₂ | 0x…
```
The Unicode operators × · ÷ − are accepted as aliases. Exponents are evaluated in exact $\Z$ whatever the domain, because an exponent counts repetitions and is not an element of the domain (\ledger{GIN-NEG-013}).
:::

Three conventions in this grammar are not forced by mathematics:

1. **Unary minus binds more loosely than exponentiation**: $-2^2 = -(2^2) = -4$. This agrees with mathematical usage and with Python. Spreadsheet software commonly gives negation *higher* precedence, so that the same five characters compute $4$.
2. **Exponentiation is right-associative**: $2^{3^2} = 2^9 = 512$, not $(2^3)^2 = 64$.
3. **Division is left-associative**: $8 / 2 / 2 = (8/2)/2 = 2$, not $8 / (2/2) = 8$.

None of these is a fact about numbers. Each is a choice of grammar, made so that the most common reading is the default. They are among the most frequent sources of disagreement between people, calculators and programming languages — disagreements that are entirely syntactic.

```python run
from ginsdk import parse

for e in ["-2 ^ 2", "2 ^ 3 ^ 2", "8 / 2 / 2", "1 + 2 * 3", "-7 // 2"]:
    print(f"{e:10s} parses as {parse(e).show()}")
```

```output
-2 ^ 2     parses as (−(2 ^ 2))
2 ^ 3 ^ 2  parses as (2 ^ (3 ^ 2))
8 / 2 / 2  parses as ((8 / 2) / 2)
1 + 2 * 3  parses as (1 + (2 × 3))
-7 // 2    parses as ((−7) // 2)
```

## Four layers of an outcome {#sec:four-layers}

When an expression is evaluated, four questions are answered in order, and evaluation can stop at any of them.

::: definition {#def:four-layers title="Four evaluation layers" status="definition" ledger="GIN-DEF-061"}
1. **Syntax** — is the string a sentence of the expression grammar?
2. **Typing** — does every literal and variable denote an element of the chosen domain?
3. **Semantics** — does every operation have exactly one result in the domain?
4. **Execution** — what does the chosen machine model do: overflow, rounding, traps, exceptions, undefined behaviour, flags?
:::

Computational Grammar Theory separates syntax, semantics and execution. Arithmetic needs a fourth layer between the first two: a string can be perfectly well formed and still name something that is not in the domain. The decimal literal `0.5` is fine syntax and is not an integer. The literal `2147483648` is fine syntax and is not a 32-bit signed integer. These failures are neither syntactic nor semantic — no operation has been attempted — and calling them either hides what went wrong.

::: definition {#def:outcome title="Outcome" status="definition" ledger="GIN-DEF-062"}
The **outcome** of evaluating an expression in a domain is a record with a status, the layer at which evaluation stopped, a reason, the defining equation of the failing operation (if any), the IEEE flags raised, the step trace, the parse tree, the representation of the result, and a cost estimate. The statuses are:

| status | layer | meaning |
|---|---|---|
| `value` | — | a value |
| `special` | execution | a special datum (±∞, NaN): not a number in the mathematical sense |
| `no-solution` | semantics | the defining equation has no solution |
| `non-unique` | semantics | the defining equation has more than one solution |
| `not-in-domain` | typing | an operand or literal is outside the domain |
| `unsupported` | typing | the operation is not part of the domain's grammar |
| `overflow` | execution | the result is not representable |
| `trap` | execution | the hardware raises an exception |
| `exception` | execution | the language runtime raises an exception |
| `undefined` | execution | undefined behaviour: the program has no meaning |
| `syntax-error` | syntax | the string is not a well-formed expression |

No outcome is a bare "error".
:::

The layers are not a hierarchy of severity; they are independent. Knowing that an expression passes one layer tells you nothing about whether it passes another.

::: proposition {#prop:layers-independent title="The four layers are independent" status="proved-here" ledger="GIN-PROP-056"}
For each of the following combinations there is an expression and a domain realizing it:
1. well formed, ill-typed: `0.5 + 1` in $\Z$;
2. well typed, semantically inadmissible: `1 / 0` in $\Q$;
3. semantically admissible, failing at execution: `(-2147483647 - 1) / -1` in 32-bit x86-64 integers — the exact quotient $2147483648$ exists and is unique in $\Z$, but `idiv` traps;
4. semantically inadmissible, executing to an ordinary-looking value: `1 / 0` in 32-bit AArch64 integers, which yields $0$;
5. ill-typed at one width, admissible at another: `2147483648 - 1` fails typing in 32-bit integers and is a value in Python;
6. well formed and semantically admissible in $\Q$, unsupported in an IEEE format: `2 ^ 10`, since exponentiation is not a basic IEEE operation (it is a library function, not correctly rounded in general).
:::

::: proof
By evaluation, reproduced below.
:::

```python run
from ginsdk import evaluate

cases = [("0.5 + 1", "Z"), ("1 / 0", "Q"), ("(-2147483647 - 1) / -1", "int32 x86-64"),
         ("(-2147483647 - 1) / -1", "Z"), ("1 / 0", "int32 AArch64"), ("2147483648 - 1", "int32 Java"),
         ("2147483648 - 1", "Python"), ("2 ^ 10", "binary64")]
for e, d in cases:
    o = evaluate(e, d)
    print(f"{e:24s} {d:14s} -> {o.status:14s} layer={o.layer or '—':9s} {o.display}")
```

```output
0.5 + 1                  Z              -> not-in-domain  layer=typing    
1 / 0                    Q              -> no-solution    layer=semantics 
(-2147483647 - 1) / -1   int32 x86-64   -> trap           layer=execution 
(-2147483647 - 1) / -1   Z              -> value          layer=—         2147483648
1 / 0                    int32 AArch64  -> value          layer=—         0
2147483648 - 1           int32 Java     -> not-in-domain  layer=typing    
2147483648 - 1           Python         -> value          layer=—         2147483647
2 ^ 10                   binary64       -> unsupported    layer=typing
```

Case 4 deserves emphasis. The outcome status is `value`, because AArch64 does produce a value. A program that inspects only the status would conclude that `1 / 0` succeeded. Only by comparing with exact mathematics — where the status is `no-solution` — does one see that the value is a convention, not a quotient. The SDK's `inspect` function performs exactly this comparison (§\ref{sec:inspect}).

## Operation contracts {#sec:contracts}

Everything that must be known before an operation can be trusted can be written down in a fixed form.

::: definition {#def:contract title="Operation contract" status="definition" ledger="GIN-DEF-080"}
An **operation contract** for an operator $\circ$ in a domain (or family of domains) $D$ consists of: the **precondition** under which $a \circ b$ is admissible in $D$; the **defining equation** that characterizes the result; the **failure classes** (outcome statuses) that can occur when the precondition fails; and the **cost model** under which the operation's cost is stated. A contract is *machine-readable* when it is given as structured data, as in the SDK's schema `gin-contracts/1`.
:::

A contract is the arithmetic analogue of a function's documented preconditions and postconditions in software engineering — with the difference that, for arithmetic, the postcondition is a *mathematical equation*, so a result can be checked independently of the code that produced it. Here is the contract for division as the SDK publishes it, abridged to three domains:

```python run
from ginsdk.contracts import contract

c = contract("/")
print(c["name"], "—", c["summary"][:96] + "…")
for d in c["domains"]:
    if d["domain"] in ("Q, R, C", "Z/n", "int32 RISC-V"):
        print(f"  {d['domain']:13s} pre: {d['pre']}")
        print(f"  {'':13s} equation: {d['equation']};  failures: {d['failures'] or 'none'}")
```

```output
division — The converse of multiplication: a / b is the unique c with b · c = a. Two distinct failures: no …
  Q, R, C       pre: b ≠ 0
                equation: b · c = a;  failures: ['no-solution', 'non-unique']
  Z/n           pre: gcd(b, n) | a for existence; gcd(b, n) = 1 for uniqueness
                equation: b · c ≡ a (mod n);  failures: ['no-solution', 'non-unique']
  int32 RISC-V  pre: always (total by convention)
                equation: truncated quotient; x/0 = −1; −2³¹/−1 = −2³¹;  failures: none
```

The RISC-V row says "always (total by convention)" and lists no failures. That is accurate as a description of the instruction, and dangerous as a description of division: a program that relies on the instruction's totality computes $-1$ for $1/0$ and continues. The contract does not hide this; it names the defining equation ("x/0 = −1"), from which a reader can see that the result is not a solution of $0 \cdot c = 1$. Part XVI measures how much such contracts help in predicting what real programs do.

## Inspecting an expression {#sec:inspect}

The SDK's `inspect` evaluates an expression twice: in the selected domain, and in the exact mathematical domain that the selected one implements or approximates ($\Z$ for machine integers, $\Q$ for floating point and Python). It then classifies the relation between the two outcomes: the machine *agrees*, *rounds*, *wraps*, *totalizes*, *selects* (division with remainder), *signals*, or has *undefined* behaviour. The answer is a JSON record with a fixed schema (`gin-inspect/1`).

```python run
from ginsdk import inspect

for e, d in [("1 / 0", "int32 RISC-V"), ("0.1 + 0.2", "binary64"), ("2147483647 + 1", "int32 Java"), ("-7 / 2", "int32 C")]:
    r = inspect(e, d)
    print(f"{e:16s} {d:13s} math: {r['mathematics']['status']:11s} machine: {str(r['execution']['value']):20s} relation: {r['relation']['kind']}")
```

```output
1 / 0            int32 RISC-V  math: no-solution machine: -1                   relation: totalized
0.1 + 0.2        binary64      math: value       machine: 0.30000000000000004  relation: rounded
2147483647 + 1   int32 Java    math: value       machine: -2147483648          relation: wrapped
-7 / 2           int32 C       math: no-solution machine: -3                   relation: selected
```

The last line is worth reading slowly. In $\Z$, $-7/2$ has no solution: $2 \nmid 7$. C's integer division returns $-3$, which is not a quotient but a *selection* from the solutions of $-7 = 2q + r$ with $|r| < 2$ — namely the one that truncates toward zero. Python's `//` makes a different selection ($-4$, flooring). Both are well defined; neither is "the" quotient; and confusing them is a classical source of bugs in code that ports between languages. Chapter 19 treats division with remainder in detail.

::: exercise {#ex:op-total}
For each operation, say whether it is total, functional and closed on the given set: (a) $+$ on odd integers; (b) $\max$ on $\N$; (c) $\sqrt{\cdot}$ on $\{0, 1, 4, 9, \ldots\}$ viewed as the relation $\{(x, y) : y^2 = x\}$ on $\Z$; (d) $/$ on $\Z \setminus \{0\}$.
:::

::: solution {of="ex:op-total"}
(a) Total and functional, not closed (odd + odd is even). (b) Total, functional, closed. (c) Total on the squares, *not functional* ($y = \pm\sqrt{x}$ for $x > 0$), results in $\Z$; a branch ($y \ge 0$) makes it functional. (d) Not total ($1/2$ has no integer solution), functional where defined, closed where defined.
:::

::: exercise {#ex:op-parse}
Give the parse trees of `-3 ^ 2 ^ 2` and `2 * -3 ^ 2` in the grammar of Definition \ref{def:expr-grammar}, and their values in $\Z$.
:::

::: solution {of="ex:op-parse"}
`-3 ^ 2 ^ 2` = $-(3^{(2^2)}) = -81$. `2 * -3 ^ 2` = $2 \times (-(3^2)) = -18$: the unary minus starts a new `unary` inside the `term`, and binds more loosely than `^`.
:::

::: exercise {#ex:op-layer}
Classify the failure layer: (a) `2 ^ 0.5` in $\Q$; (b) `x + 1` in $\Z$ with no value for `x`; (c) `1 +` ; (d) `0 - 1` in $\N$; (e) `2147483647 * 2` in 32-bit C.
:::

::: solution {of="ex:op-layer"}
(a) typing (`not-in-domain`): exponents are evaluated in exact $\Z$, and $0.5$ is not an integer; a rational exponent would be a root, a converse problem outside this grammar. (b) typing: the variable denotes nothing. (c) syntax. (d) semantics: $1 + c = 0$ has no solution in $\N$. (e) execution: undefined behaviour (signed overflow), although the value $4294967294$ exists in $\Z$.
:::

::: exercise {#ex:op-contract}
Write an operation contract (precondition, defining equation, failure classes, cost model) for integer square root $\lfloor \sqrt{n} \rfloor$ on $\N$, and explain why it has no `non-unique` failure although $\sqrt{\cdot}$ does.
:::

::: solution {of="ex:op-contract"}
Precondition: always, on $\N$. Defining equation: the unique $c \in \N$ with $c^2 \le n < (c + 1)^2$. Failures: none on $\N$; `not-in-domain` for negative inputs if the domain is $\Z$. Cost: $\Oh(M(L))$ bit operations with Newton's method, where $M(L)$ is the cost of $L$-bit multiplication. The defining *inequalities* single out one $c$, which is why there is no ambiguity: the floor is a selection built into the definition, unlike $c^2 = n$, which has two solutions for $n > 0$.
:::

::: summary
- An operation is a relation; totality, functionality and closure can fail independently.
- Precedence and associativity are conventions of a grammar, and systems differ in them.
- Outcomes have four independent layers — syntax, typing, semantics, execution — and eleven statuses; none is a bare "error".
- An operation contract states precondition, defining equation, failure classes and cost model, as data.
- Comparing a machine's outcome with exact mathematics classifies it: agrees, rounds, wraps, totalizes, selects, signals, undefined.
:::
