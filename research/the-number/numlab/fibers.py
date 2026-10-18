"""Converse fibers in finite algebras and their behaviour under maps (NUM-EXP-004).

A finite algebra here is a carrier ``elems`` with named binary operations.  For an
operation ⊙ the converse problem at (a, b) is Sol(a, b) = {c : b ⊙ c = a}; its
class is none (|Sol| = 0), unique (1) or many (> 1), as in GIN-DEF-015.

A map h: A → B *translates* converse problems: (a, b) ↦ (h a, h b).  The functions
below measure how the class changes along h.  When h is a homomorphism for ⊙, the
classical preservation theorem for positive existential formulas predicts the
direction of every change (see FOUNDATIONS.md, NUM-HIST-001/002); the experiment
checks those predictions exhaustively and records every change.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

NONE, UNIQUE, MANY = "none", "unique", "many"


def klass(k: int) -> str:
    return NONE if k == 0 else UNIQUE if k == 1 else MANY


@dataclass
class Algebra:
    name: str
    elems: list
    ops: dict = field(default_factory=dict)        # name -> callable(x, y)

    def sol(self, op: str, a, b) -> list:
        f = self.ops[op]
        return [c for c in self.elems if f(b, c) == a]

    def profile(self, op: str) -> dict:
        out = {NONE: 0, UNIQUE: 0, MANY: 0}
        for a in self.elems:
            for b in self.elems:
                out[klass(len(self.sol(op, a, b)))] += 1
        return out


def zmod(n: int) -> Algebra:
    e = list(range(n))
    return Algebra(f"Z/{n}", e, {"+": lambda x, y: (x + y) % n, "*": lambda x, y: x * y % n})


def gf4() -> Algebra:
    """GF(4) = F2[t]/(t² + t + 1); elements 0, 1, t, t+1 encoded as 0, 1, 2, 3 (bit i = coefficient of t^i)."""
    def mul(x, y):
        r = 0
        for i in range(2):
            if (y >> i) & 1:
                r ^= x << i
        if r & 4:
            r ^= 0b111
        return r
    return Algebra("GF(4)", [0, 1, 2, 3], {"+": lambda x, y: x ^ y, "*": mul})


def product(A: Algebra, B: Algebra) -> Algebra:
    e = [(x, y) for x in A.elems for y in B.elems]
    ops = {op: (lambda f, g: (lambda p, q: (f(p[0], q[0]), g(p[1], q[1]))))(A.ops[op], B.ops[op]) for op in A.ops.keys() & B.ops.keys()}
    return Algebra(f"{A.name} x {B.name}", e, ops)


def saturating(m: int) -> Algebra:
    return Algebra(f"sat{{0..{m}}}", list(range(m + 1)), {"+": lambda x, y: min(x + y, m)})


def maxmonoid(m: int) -> Algebra:
    return Algebra(f"max{{0..{m}}}", list(range(m + 1)), {"+": max})


def integers(lo: int, hi: int) -> Algebra:
    """A window of Z.  Converse problems are solved in Z (not in the window), so the
    window is only the set of (a, b) examined: Sol is computed exactly."""
    return Algebra(f"Z[{lo}..{hi}]", list(range(lo, hi + 1)), {"+": lambda x, y: x + y, "*": lambda x, y: x * y})


def z_sol(op: str, a: int, b: int) -> int:
    """Exact |Sol| in Z (∞ encoded as 2, i.e. 'many')."""
    if op == "+":
        return 1
    if b == 0:
        return 2 if a == 0 else 0
    return 1 if a % b == 0 else 0


@dataclass
class Map:
    name: str
    src: Algebra
    dst: Algebra
    h: Callable
    ops: tuple            # operations h is claimed to preserve
    injective: bool
    surjective: bool


def is_hom(m: Map, op: str) -> bool:
    f, g = m.src.ops[op], m.dst.ops[op]
    return all(m.h(f(x, y)) == g(m.h(x), m.h(y)) for x in m.src.elems for y in m.src.elems)


def transfer(m: Map, op: str, src_count: Callable | None = None) -> dict:
    """Confusion matrix of converse classes along m, for every (a, b) in the source."""
    mat = {s: {t: 0 for t in (NONE, UNIQUE, MANY)} for s in (NONE, UNIQUE, MANY)}
    examples = {}
    for a in m.src.elems:
        for b in m.src.elems:
            ks = src_count(op, a, b) if src_count else len(m.src.sol(op, a, b))
            s = klass(ks)
            t = klass(len(m.dst.sol(op, m.h(a), m.h(b))))
            mat[s][t] += 1
            if s != t:
                examples.setdefault(f"{s}->{t}", f"{b}{op}c={a} in {m.src.name} ({s}) -> {m.h(b)}{op}c={m.h(a)} in {m.dst.name} ({t})")
    return {"matrix": mat, "examples": examples}


def predicted_violations(m: Map, mat: dict) -> list:
    """Class changes forbidden by the preservation theorems for a homomorphism m.

    - every homomorphism maps solutions to solutions: none ← solvable never happens,
      i.e. a solvable source problem never becomes 'none';
    - an injective homomorphism maps distinct solutions to distinct ones: 'many'
      never becomes 'unique' or 'none'.
    """
    bad = []
    for s in (UNIQUE, MANY):
        if mat[s][NONE]:
            bad.append(f"{s}->none ({mat[s][NONE]})")
    if m.injective and mat[MANY][UNIQUE]:
        bad.append(f"many->unique under an injective map ({mat[MANY][UNIQUE]})")
    return bad


def totalize(alg: Algebra, op: str, select: str = "min", default=0) -> Callable:
    """A total 'inverse' a ⊘ b: the unique solution when there is one, otherwise a
    selected element (smallest solution) or a default when there is none."""
    def inv(a, b):
        s = alg.sol(op, a, b)
        if not s:
            return default
        return min(s) if select == "min" else s[0]
    return inv
