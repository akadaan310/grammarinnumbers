"""Operation contracts and layered inspection (GIN-DEF-080 … GIN-DEF-083).

A computational grammar can serve as an explicit *interface contract* between a
request ("compute 1 / 0") and an execution system.  This module makes that
interface concrete and machine-readable:

* :data:`CONTRACTS` — for every operator and every family of domains, the
  precondition under which the operation is admissible, the equation that
  defines its result, the failure classes it can report, and the cost model.
  ``contracts_document()`` returns the whole specification as JSON-ready data
  (schema ``gin-contracts/1``).
* :func:`inspect` — evaluates an expression in a selected domain **and** in the
  domain of exact mathematics it approximates, and returns one record that keeps
  apart the nine questions of the book: is it well formed, is it typed, is it
  defined, what does the mathematics prescribe, what representation is used,
  what does the selected machine do, how do the two compare, what does it cost,
  and how can the result be checked independently.
* :func:`verify` — an independent check of an outcome: every exact step is
  re-verified against its defining equation with Python's ``fractions``
  (a different code path from the evaluator).

Nothing here adds mathematics; it packages the evaluator of :mod:`ginsdk.expr`
so that a program — or a language model acting through a tool interface — can
ask the questions before trusting an answer.
"""
from __future__ import annotations

import json
from fractions import Fraction

from . import expr
from .expr import LAYER, STATUS_TEXT, evaluate

SCHEMA = "gin-contracts/1"

# --------------------------------------------------------------------------- statuses
STATUSES = [{"status": s, "layer": LAYER[s], "meaning": STATUS_TEXT[s]} for s in STATUS_TEXT]

# --------------------------------------------------------------------------- contracts
_EXACT = "exact domains N, Z, Q, R, C, Z/n"
_FLOAT = "IEEE 754 binary formats (binary64, binary32, binary16, binary8), JS Number"
_INT = "32-bit integer machine models (x86-64, AArch64, RISC-V, C, Java, Rust debug, Go)"


def _d(domain, pre, equation, failures, cost):
    return {"domain": domain, "pre": pre, "equation": equation, "failures": failures, "cost": cost}


CONTRACTS = [
    {"op": "+", "name": "addition", "summary": "The forward operation of the additive grammar; total on every exact domain.",
     "domains": [
         _d("N, Z, Q, R, C", "always", "a + b (primitive recursion on the successor in N)", [], "Θ(L) bit operations for L-bit integers; L_a·L_b + max for fractions (schoolbook model)"),
         _d("Z/n", "always", "(a + b) mod n", [], "one modular operation"),
         _d(_FLOAT, "always (special data propagate)", "round(a + b) to nearest, ties to even", ["special"], "one floating-point operation; flags: inexact, overflow, invalid (∞ − ∞)"),
         _d(_INT, "always syntactically; the result must fit in 32 bits", "a + b mod 2³² (wrap), or a signal", ["overflow", "undefined", "exception"], "one instruction; ISO C: signed overflow is undefined; Rust debug: panic"),
         _d("Python, JS BigInt", "always", "a + b in unbounded integers", [], "Θ(L) limb operations"),
     ]},
    {"op": "-", "name": "subtraction", "summary": "The converse of addition: a − b is the unique c with b + c = a.",
     "domains": [
         _d("N", "a ≥ b", "b + c = a", ["no-solution"], "Θ(L)"),
         _d("Z, Q, R, C, Z/n", "always", "b + c = a", [], "Θ(L)"),
         _d(_FLOAT, "always", "round(a − b)", ["special"], "one floating-point operation"),
         _d(_INT, "the result must fit in 32 bits", "a − b mod 2³², or a signal", ["overflow", "undefined", "exception"], "one instruction"),
     ]},
    {"op": "*", "name": "multiplication", "summary": "The forward operation of the multiplicative grammar; total on every exact domain.",
     "domains": [
         _d("N, Z, Q, R, C, Z/n", "always", "a · b (primitive recursion on addition in N)", [], "Θ(L_a·L_b) schoolbook; Θ(L^1.585) Karatsuba; O(L log L) best known"),
         _d(_FLOAT, "always", "round(a · b)", ["special"], "one floating-point operation; invalid for 0 · ∞"),
         _d(_INT, "the result must fit in 32 bits", "a · b mod 2³², or a signal", ["overflow", "undefined", "exception"], "one instruction (multi-cycle)"),
     ]},
    {"op": "/", "name": "division", "summary": "The converse of multiplication: a / b is the unique c with b · c = a. Two distinct failures: no c (image failure, e.g. 1/0) and more than one c (kernel failure, e.g. 0/0).",
     "domains": [
         _d("N, Z", "b ≠ 0 and b | a", "b · c = a", ["no-solution", "non-unique"], "Θ(L²) schoolbook (as costly as computing the quotient: deciding b | a is a division)"),
         _d("Q, R, C", "b ≠ 0", "b · c = a", ["no-solution", "non-unique"], "Θ(L²) on numerators and denominators"),
         _d("Z/n", "gcd(b, n) | a for existence; gcd(b, n) = 1 for uniqueness", "b · c ≡ a (mod n)", ["no-solution", "non-unique"], "one extended Euclid: O(log n) steps"),
         _d(_FLOAT, "always (total by convention)", "round(a / b); x/±0 = ±∞ with divideByZero; 0/0 = NaN with invalid", ["special"], "one floating-point operation (tens of cycles)"),
         _d("int32 x86-64", "b ≠ 0 and (a, b) ≠ (−2³¹, −1)", "quotient truncated toward zero", ["trap"], "one IDIV instruction; #DE fault otherwise"),
         _d("int32 AArch64", "always (total by convention)", "truncated quotient; x/0 = 0; −2³¹/−1 = −2³¹", [], "one SDIV; the value for b = 0 is not a quotient (totalization)"),
         _d("int32 RISC-V", "always (total by convention)", "truncated quotient; x/0 = −1; −2³¹/−1 = −2³¹", [], "one DIV; the value for b = 0 is not a quotient (totalization)"),
         _d("int32 C", "b ≠ 0 and the quotient representable", "truncated quotient", ["undefined"], "ISO C17 6.5.5: otherwise undefined behaviour"),
         _d("int32 Java, int32 Go", "b ≠ 0", "truncated quotient; MIN/−1 = MIN", ["exception"], "ArithmeticException / run-time panic for b = 0"),
         _d("int32 Rust (debug)", "b ≠ 0 and the quotient representable", "truncated quotient", ["exception"], "panic otherwise"),
         _d("Python", "b ≠ 0", "int / int: true quotient rounded to binary64", ["exception"], "ZeroDivisionError for b = 0, also for floats"),
         _d("JS BigInt", "b ≠ 0", "quotient truncated toward zero", ["exception"], "RangeError for 0n"),
         _d("symbolic", "the divisor polynomial is not identically zero; the result is defined where it is non-zero", "b(x) · c(x) = a(x) in Q(x), with the condition b(x) ≠ 0 kept", ["no-solution", "non-unique"], "polynomial gcd per cancellation"),
     ]},
    {"op": "//", "name": "quotient with remainder", "summary": "A selection: among all (q, r) with a = q·b + r, the condition on r picks one. Euclidean (0 ≤ r < |b|) in the exact domains; floor in Python; truncation in C, Java, Go, Rust, x86, ARM, RISC-V, JS BigInt.",
     "domains": [
         _d("N, Z", "b ≠ 0", "a = q·b + r, 0 ≤ r < |b|", ["no-solution", "unsupported"], "Θ(L²)"),
         _d("Q", "never", "—", ["unsupported"], "—"),
         _d(_INT + ", JS BigInt", "as for /", "a = q·b + r, r has the sign of a (truncation)", ["trap", "undefined", "exception"], "one instruction"),
         _d("Python", "b ≠ 0", "a = q·b + r, r has the sign of b (floor)", ["exception"], "Θ(L²)"),
     ]},
    {"op": "%", "name": "remainder", "summary": "The r of the selected quotient-with-remainder; same admissibility as //.",
     "domains": [_d("N, Z", "b ≠ 0", "0 ≤ r < |b|", ["no-solution"], "Θ(L²)"),
                 _d(_INT + ", Python, JS BigInt", "as for //", "sign convention of the language", ["trap", "undefined", "exception"], "one instruction")]},
    {"op": "^", "name": "power", "summary": "An action of the integers on the domain (repeated multiplication), not a ring operation: the exponent is always evaluated in exact Z (GIN-NEG-013).",
     "domains": [
         _d("N, Z", "exponent ≥ 0, or base ±1", "a^k = a · a · … · a (k factors); a^0 = 1 (empty product)", ["no-solution"], "⌊log₂ k⌋ squarings + popcount(k) − 1 multiplications"),
         _d("Q, R, C", "base ≠ 0 when the exponent is negative", "a^−k = (a^k)⁻¹", ["no-solution"], "as above, plus one inversion"),
         _d("Z/n", "for k < 0: a must be a unit mod n", "a^k mod n", ["no-solution"], "O(log k) modular multiplications"),
         _d(_FLOAT + ", " + _INT, "not a basic operation", "—", ["unsupported"], "library function, not correctly rounded in general"),
     ]},
    {"op": "sqrt", "name": "square root", "summary": "The converse of squaring, made a function by a branch: √a is the non-negative c with c · c = a.",
     "domains": [
         _d("N, Z, Q", "a is the square of an element of the domain", "c · c = a, c ≥ 0", ["no-solution"], "integer square root: O(M(L)) with Newton"),
         _d("R", "a ≥ 0", "c · c = a, c ≥ 0 (two solutions for a > 0: a branch selects one)", ["no-solution"], "irrational results are carried as flagged approximations"),
         _d("C", "always", "principal branch", [], "—"),
         _d(_FLOAT, "always (total by convention)", "correctly rounded √a; √(negative) = NaN with invalid", ["special"], "one floating-point operation"),
     ]},
    {"op": "gcd", "name": "greatest common divisor", "summary": "Total on Z²; gcd(0, 0) = 0 by convention (the generator of the ideal aZ + bZ).",
     "domains": [_d("N, Z, Q (integers only)", "integer arguments", "the Euclid system (a, b) → (b, a mod b)", ["not-in-domain"], "O(log min(a, b)) division steps (Lamé); Θ(L²) bit operations")]},
]


def contracts_document() -> dict:
    """The full contract specification as JSON-ready data (schema gin-contracts/1)."""
    return {"schema": SCHEMA, "statuses": STATUSES, "contracts": CONTRACTS,
            "domains": [{"name": n, "description": getattr(d, "description", "")} for n, d in expr.DOMAINS.items()] +
                       [{"name": "Z/n", "description": "integers modulo n, for any n ≥ 1 (e.g. Z/7, Z/6)"}]}


def contract(op: str) -> dict:
    """Return the contract of one operator (``+ - * / // % ^ sqrt gcd``)."""
    for c in CONTRACTS:
        if c["op"] == op:
            return c
    raise KeyError(op)


# --------------------------------------------------------------------------- inspection
def reference_domain(dom: str) -> str:
    """The domain of exact mathematics that a domain approximates or implements."""
    if dom.startswith("int32") or dom == "JS BigInt":
        return "Z"
    if dom == "Python":
        return "Q"
    if dom in ("binary64", "binary32", "binary16", "binary8", "JS Number"):
        return "Q"
    return dom


def _ops_in(tree) -> list[str]:
    out = []

    def walk(t):
        if not t:
            return
        if t.get("kind") in ("bin", "neg", "call"):
            lab = t.get("label", "")
            out.append({"neg": "-", "−": "-", "×": "*", "·": "*", "÷": "/", "√": "sqrt", "mod": "%"}.get(lab, lab))
        for c in t.get("children", []):
            walk(c)
    walk(tree)
    return sorted(set(out))


def _relation(sel: expr.Outcome, ref: expr.Outcome) -> tuple[str, str]:
    """Classify how the selected domain's execution relates to exact mathematics."""
    s, r = sel.status, ref.status
    if r in ("value",) and s == "value":
        try:
            same = Fraction(str(sel.value)) == Fraction(str(ref.value)) if not hasattr(sel.value, "value") else sel.value.value() == Fraction(ref.value)
        except (ValueError, TypeError, ZeroDivisionError):
            same = sel.display == ref.display
        if same:
            return "agrees", "the machine value equals the mathematical value"
        if "overflow" in sel.flags:
            return "wrapped", "the machine value differs from the mathematical value by a multiple of 2^w (fixed-width wraparound)"
        if "inexact" in sel.flags or hasattr(sel.value, "value"):
            return "rounded", "the machine value is a rounding of the mathematical value"
        if any(st.op in ("//", "%", "/") for st in sel.steps):
            return "different-selection", ("both values satisfy a = q·b + r with |r| < |b|; the reference uses the Euclidean "
                                           "selection 0 ≤ r < |b|, the machine truncates toward zero (r has the sign of a)")
        return "differs", "the machine value differs from the mathematical value"
    if r in ("no-solution", "non-unique") and s == "value":
        divs = [st for st in sel.steps if st.op in ("/", "//", "%")]
        if divs and all(st.operands[1] not in ("0", "-0") for st in divs) and r == "no-solution":
            return "selected", ("mathematics has no exact quotient in the reference domain; the machine applies a selection "
                                f"(quotient with remainder, truncated toward zero or floored) and returns {sel.display}")
        return "totalized", f"mathematics gives no value ({r}); the machine returns {sel.display} by convention, which is not a solution of the defining equation"
    if r in ("no-solution", "non-unique") and s == "special":
        return "special-datum", f"mathematics gives no value ({r}); the format returns the special datum {sel.display}, which is not a number"
    if r == "value" and s == "special":
        return "overflowed-to-special", "the mathematical value exists but is outside the format's range"
    if s in ("trap", "exception", "undefined"):
        return "signalled" if s != "undefined" else "undefined", f"the machine refuses ({s}); mathematics {'has the value ' + ref.display if r == 'value' else 'gives ' + r}"
    if s == r:
        return "agrees", f"both fail in the same way ({s})"
    return "differs", f"mathematics: {r}; machine: {s}"


def inspect(src: str, dom: str = "Q", env: dict | None = None) -> dict:
    """Answer the nine interface questions for ``src`` in ``dom`` as one JSON-ready record.

    1 well formed?  2 typed?  3 defined (admissible)?  4 what result does the
    mathematics prescribe?  5 what representation?  6 what does the selected
    machine do?  7 how do machine and mathematics relate?  8 what does it cost?
    9 how can it be verified independently?
    """
    sel = evaluate(src, dom, env)
    ref_name = reference_domain(sel.domain if dom != sel.domain else dom)
    ref = evaluate(src, ref_name, env) if ref_name != dom else sel
    if ref.status == "unsupported" and ref_name == "Q":     # // and % are operations on integers
        ref = evaluate(src, "Z", env)
    layers = {}
    stop = sel.layer
    order = ["syntax", "typing", "semantics", "execution"]
    for L in order:
        if stop == L:
            layers[L] = {"ok": False, "status": sel.status, "reason": sel.reason}
        elif stop is None or order.index(L) < order.index(stop):
            layers[L] = {"ok": True}
        else:
            layers[L] = {"ok": None, "reason": f"not reached: evaluation stopped at {stop}"}
    relation, explanation = _relation(sel, ref) if sel.status != "syntax-error" else ("not-applicable", "the string is not an expression")
    ops = _ops_in(sel.tree)
    return {
        "schema": "gin-inspect/1",
        "expression": src,
        "domain": sel.domain,
        "reference_domain": ref.domain,
        "well_formed": sel.status != "syntax-error",
        "layers": layers,
        "mathematics": {"status": ref.status, "value": ref.display if ref.status == "value" else None,
                        "equation": ref.equation, "solutions": ref.solutions, "reason": ref.reason},
        "execution": {"status": sel.status, "value": sel.display if sel.status in ("value", "special") else None,
                      "flags": sel.flags, "notes": sel.notes, "reason": sel.reason},
        "relation": {"kind": relation, "explanation": explanation},
        "representation": sel.representation,
        "cost": {"amount": sel.cost, "unit": sel.cost_unit, "model": "see contracts: " + ", ".join(ops) if ops else ""},
        "contracts": ops,
        "trace": [s.__dict__ for s in sel.steps],
        "verification": verify(ref),
    }


def verify(out: expr.Outcome) -> dict:
    """Independently re-check an outcome of an exact domain.

    Every step of an exact evaluation is re-verified against its defining
    equation using :mod:`fractions` directly (b + c = a for −, b · c = a for /,
    and recomputation for + and ×).  Failures are re-checked too: for a
    no-solution division b must be 0 and a ≠ 0; for non-unique, both 0.
    """
    if out.domain not in ("N", "Z", "Q"):
        return {"checked": False, "reason": f"independent verification is implemented for the exact domains N, Z, Q (not {out.domain})"}
    checks = []
    for st in out.steps:
        try:
            xs = [Fraction(x) for x in st.operands]
            r = Fraction(st.result)
        except (ValueError, ZeroDivisionError):
            continue
        op = st.op
        if op == "+":
            ok, eq = xs[0] + xs[1] == r, f"{xs[0]} + {xs[1]} = {r}"
        elif op in ("−", "-"):
            ok, eq = xs[1] + r == xs[0], f"{xs[1]} + {r} = {xs[0]}"
        elif op in ("×", "*"):
            ok, eq = xs[0] * xs[1] == r, f"{xs[0]} · {xs[1]} = {r}"
        elif op == "/":
            ok, eq = xs[1] * r == xs[0] and xs[1] != 0, f"{xs[1]} · {r} = {xs[0]}"
        elif op == "neg":
            ok, eq = xs[0] + r == 0, f"{xs[0]} + {r} = 0"
        else:
            continue
        if out.domain == "N":
            ok = ok and r >= 0
        if out.domain in ("N", "Z"):
            ok = ok and r.denominator == 1
        checks.append({"step": f"{op} {st.operands}", "equation": eq, "ok": ok})
    failure = None
    if out.status in ("no-solution", "non-unique") and out.equation:
        failure = {"status": out.status, "equation": out.equation}
    return {"checked": True, "method": "each step re-verified against its defining equation with Python fractions",
            "steps": checks, "all_ok": all(c["ok"] for c in checks), "failure": failure}


def dumps(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, indent=1, default=str)
