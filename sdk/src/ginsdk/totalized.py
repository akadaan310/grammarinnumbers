"""Systems that give division by zero a value, and a census of the laws each keeps
(GIN-THM-004, GIN-EXP-015).

Every system below implements +, −, ×, / on a small exact carrier.  A partial
operation returns ``UNDEF``.  ``law_census`` evaluates a fixed list of laws on all
tuples drawn from a sample of elements and reports, per law, how many instances
hold, fail, or are undefined (some side undefined), with a counterexample.

Systems
-------
field          ℚ with division restricted to b ≠ 0 (the reference: partial)
meadow         ℚ with 0⁻¹ = 0 (Bergstra & Tucker 2007; Lean/mathlib and Isabelle/HOL use
               the same convention): x/0 = 0
wheel          the wheel of fractions of ℤ (Carlström 2004): pairs (a, b) up to scaling by
               a non-zero integer; ℚ ∪ {∞ = [1, 0], ⊥ = [0, 0]}; /[a, b] = [b, a]
projective     the projective line ℚ ∪ {∞}: 1/0 = ∞; 0·∞, ∞ ± ∞, 0/0, ∞/∞ undefined
extended       the extended rationals ℚ ∪ {−∞, +∞}: x/0 undefined; 0·(±∞), ∞ − ∞ undefined
ieee16         IEEE 754 binary16 via ginsdk.ieee (laws compare data, NaN counts as equal to NaN)
riscv8, aarch64_8   8-bit integer division totalizations (x/0 = −1, resp. 0; truncation);
               +, −, × wrap modulo 2^8

The wheel axioms checked are Carlström's, as listed in the Wheel theory article of
Wikipedia (revision of 1 July 2026; the paper itself was not read): see WHEEL_AXIOMS.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

from . import ieee

UNDEF = object()   # result of a partial operation outside its domain


# ---------------------------------------------------------------------------
# meadow ℚ and field ℚ
# ---------------------------------------------------------------------------
class FieldQ:
    name = "field ℚ (division restricted to b ≠ 0)"
    zero, one = Fraction(0), Fraction(1)

    def add(self, x, y): return x + y
    def neg(self, x): return -x
    def mul(self, x, y): return x * y
    def div(self, x, y): return UNDEF if y == 0 else x / y
    def show(self, x): return str(x)
    sample = [Fraction(v) for v in ("0", "1", "-1", "2", "1/2", "-3", "5/3")]


class MeadowQ(FieldQ):
    name = "meadow ℚ (x/0 = 0)"
    def inv(self, x): return Fraction(0) if x == 0 else 1 / x
    def div(self, x, y): return x * self.inv(y)


# ---------------------------------------------------------------------------
# the wheel of fractions of ℤ
# ---------------------------------------------------------------------------
def _wnorm(a: int, b: int) -> tuple[int, int]:
    """Canonical representative of [a, b] under (a, b) ~ (sa, sb), s ≠ 0."""
    if a == 0 and b == 0:
        return (0, 0)              # ⊥
    if b == 0:
        return (1, 0)              # ∞
    if a == 0:
        return (0, 1)
    from math import gcd
    g = gcd(a, b) * (1 if b > 0 else -1)
    return (a // g, b // g)


class WheelZ:
    name = "wheel of fractions of ℤ (Carlström)"
    zero, one = (0, 1), (1, 1)

    def add(self, x, y): return _wnorm(x[0] * y[1] + x[1] * y[0], x[1] * y[1])
    def mul(self, x, y): return _wnorm(x[0] * y[0], x[1] * y[1])
    def rec(self, x): return _wnorm(x[1], x[0])                       # the unary /
    def neg(self, x): return _wnorm(-x[0], x[1])                      # −x = (−1)·x
    def div(self, x, y): return self.mul(x, self.rec(y))              # x/y = x · /y
    def show(self, x): return "⊥" if x == (0, 0) else "∞" if x == (1, 0) else (str(x[0]) if x[1] == 1 else f"{x[0]}/{x[1]}")
    sample = [_wnorm(a, b) for a, b in [(0, 1), (1, 1), (-1, 1), (2, 1), (1, 2), (-3, 1), (1, 0), (0, 0)]]


WHEEL_AXIOMS = [
    ("+ commutative", 2, lambda W, x, y: (W.add(x, y), W.add(y, x))),
    ("+ associative", 3, lambda W, x, y, z: (W.add(W.add(x, y), z), W.add(x, W.add(y, z)))),
    ("0 + x = x", 1, lambda W, x: (W.add(W.zero, x), x)),
    ("· commutative", 2, lambda W, x, y: (W.mul(x, y), W.mul(y, x))),
    ("· associative", 3, lambda W, x, y, z: (W.mul(W.mul(x, y), z), W.mul(x, W.mul(y, z)))),
    ("1 · x = x", 1, lambda W, x: (W.mul(W.one, x), x)),
    ("//x = x", 1, lambda W, x: (W.rec(W.rec(x)), x)),
    ("/(xy) = /x /y", 2, lambda W, x, y: (W.rec(W.mul(x, y)), W.mul(W.rec(x), W.rec(y)))),
    ("(x+y)z + 0z = xz + yz", 3, lambda W, x, y, z: (W.add(W.mul(W.add(x, y), z), W.mul(W.zero, z)), W.add(W.mul(x, z), W.mul(y, z)))),
    ("(x+yz)/y = x/y + z + 0y", 3, lambda W, x, y, z: (W.div(W.add(x, W.mul(y, z)), y), W.add(W.add(W.div(x, y), z), W.mul(W.zero, y)))),
    ("0·0 = 0", 0, lambda W: (W.mul(W.zero, W.zero), W.zero)),
    ("(x+0y)z = xz + 0y", 3, lambda W, x, y, z: (W.mul(W.add(x, W.mul(W.zero, y)), z), W.add(W.mul(x, z), W.mul(W.zero, y)))),
    ("/(x+0y) = /x + 0y", 2, lambda W, x, y: (W.rec(W.add(x, W.mul(W.zero, y))), W.add(W.rec(x), W.mul(W.zero, y)))),
    ("0/0 + x = 0/0", 1, lambda W, x: (W.add(W.div(W.zero, W.zero), x), W.div(W.zero, W.zero))),
]


def check_wheel_axioms(sample=None) -> dict[str, tuple[int, int]]:
    """(holds, total) for each wheel axiom on all tuples from ``sample``."""
    W = WheelZ()
    sample = sample or W.sample
    out = {}
    for name, arity, f in WHEEL_AXIOMS:
        ok = tot = 0
        for t in itertools.product(sample, repeat=arity):
            lhs, rhs = f(W, *t)
            ok += lhs == rhs
            tot += 1
        out[name] = (ok, tot)
    return out


# ---------------------------------------------------------------------------
# projective line and extended rationals (partial)
# ---------------------------------------------------------------------------
INF, PINF, NINF = "∞", "+∞", "−∞"


class Projective:
    name = "projective line ℚ ∪ {∞}"
    zero, one = Fraction(0), Fraction(1)

    def add(self, x, y):
        if x == INF and y == INF:
            return UNDEF
        return INF if INF in (x, y) else x + y

    def neg(self, x): return x if x == INF else -x

    def mul(self, x, y):
        if INF in (x, y):
            other = y if x == INF else x
            return UNDEF if other == 0 else INF
        return x * y

    def div(self, x, y):
        if x == INF and y == INF:
            return UNDEF
        if y == 0:
            return UNDEF if x == 0 else INF
        if y == INF:
            return Fraction(0)
        return INF if x == INF else x / y

    def show(self, x): return str(x)
    sample = [Fraction(0), Fraction(1), Fraction(-1), Fraction(2), Fraction(1, 2), INF]


class Extended:
    name = "extended rationals ℚ ∪ {−∞, +∞}"
    zero, one = Fraction(0), Fraction(1)

    @staticmethod
    def _sgn(x): return 1 if x == PINF else -1 if x == NINF else (x > 0) - (x < 0)

    def add(self, x, y):
        inf = [v for v in (x, y) if v in (PINF, NINF)]
        if len(inf) == 2 and inf[0] != inf[1]:
            return UNDEF
        return inf[0] if inf else x + y

    def neg(self, x): return NINF if x == PINF else PINF if x == NINF else -x

    def mul(self, x, y):
        if x in (PINF, NINF) or y in (PINF, NINF):
            s = self._sgn(x) * self._sgn(y)
            return UNDEF if s == 0 else (PINF if s > 0 else NINF)
        return x * y

    def div(self, x, y):
        if y == 0:
            return UNDEF
        if y in (PINF, NINF):
            return UNDEF if x in (PINF, NINF) else Fraction(0)
        if x in (PINF, NINF):
            s = self._sgn(x) * self._sgn(y)
            return PINF if s > 0 else NINF
        return x / y

    def show(self, x): return str(x)
    sample = [Fraction(0), Fraction(1), Fraction(-1), Fraction(2), Fraction(1, 2), PINF, NINF]


# ---------------------------------------------------------------------------
# IEEE binary16 and 8-bit integer division totalizations
# ---------------------------------------------------------------------------
class IEEE16:
    name = "IEEE 754 binary16"
    fmt = ieee.BINARY16

    def __init__(self):
        self.zero = ieee.round_exact(self.fmt, Fraction(0))[0]
        self.one = ieee.round_exact(self.fmt, Fraction(1))[0]

    def _c(self, x):
        return x
    def add(self, x, y): return ieee.add(x, y)[0]
    def neg(self, x): return ieee.neg(x)
    def mul(self, x, y): return ieee.mul(x, y)[0]
    def div(self, x, y): return ieee.div(x, y)[0]
    def show(self, x): return str(x)

    @property
    def sample(self):
        F = self.fmt
        vals = [ieee.round_exact(F, Fraction(v))[0] for v in ("0", "1", "-1", "2", "1/2", "3", "1/10", "65504")]
        vals.append(ieee.neg(vals[0]))                         # −0
        vals.append(ieee.FP(F, "inf", 0))
        vals.append(ieee.FP(F, "nan"))
        return vals


def _key(x):
    """Datum identity for laws: NaN equals NaN; +0 and −0 are distinct data but equal values."""
    if isinstance(x, ieee.FP):
        return ("nan",) if x.is_nan else (x.cls, x.sign, x.mag)
    return x


class Int8Div:
    def __init__(self, name, at_zero):
        self.name, self.at_zero = name, at_zero
        self.zero, self.one = 0, 1

    @staticmethod
    def _w(x): return ((x + 128) % 256) - 128
    def add(self, x, y): return self._w(x + y)
    def neg(self, x): return self._w(-x)
    def mul(self, x, y): return self._w(x * y)

    def div(self, x, y):
        if y == 0:
            return self.at_zero(x)
        q = abs(x) // abs(y) * (1 if (x < 0) == (y < 0) else -1)
        return self._w(q)

    def show(self, x): return str(x)
    sample = [0, 1, -1, 2, 3, -7, 100, -128]


SYSTEMS = {"field": FieldQ(), "meadow": MeadowQ(), "wheel": WheelZ(), "projective": Projective(), "extended": Extended(),
           "ieee16": IEEE16(), "riscv8": Int8Div("8-bit RISC-V DIV (x/0 = −1)", lambda x: -1),
           "aarch64_8": Int8Div("8-bit AArch64 SDIV (x/0 = 0)", lambda x: 0)}


# ---------------------------------------------------------------------------
# laws
# ---------------------------------------------------------------------------
def _ap(S, f, *xs):
    if any(x is UNDEF for x in xs):
        return UNDEF
    return f(*xs)


LAWS = [
    ("x + y = y + x", 2, lambda S, x, y: (_ap(S, S.add, x, y), _ap(S, S.add, y, x))),
    ("(x + y) + z = x + (y + z)", 3, lambda S, x, y, z: (_ap(S, S.add, _ap(S, S.add, x, y), z), _ap(S, S.add, x, _ap(S, S.add, y, z)))),
    ("x·(y + z) = x·y + x·z", 3, lambda S, x, y, z: (_ap(S, S.mul, x, _ap(S, S.add, y, z)), _ap(S, S.add, _ap(S, S.mul, x, y), _ap(S, S.mul, x, z)))),
    ("0·x = 0", 1, lambda S, x: (_ap(S, S.mul, S.zero, x), S.zero)),
    ("x − x = 0", 1, lambda S, x: (_ap(S, S.add, x, _ap(S, S.neg, x)), S.zero)),
    ("x / x = 1", 1, lambda S, x: (_ap(S, S.div, x, x), S.one)),
    ("y·(x / y) = x   (the converse reading)", 2, lambda S, x, y: (_ap(S, S.mul, y, _ap(S, S.div, x, y)), x)),
    ("(x / y) / z = x / (y·z)", 3, lambda S, x, y, z: (_ap(S, S.div, _ap(S, S.div, x, y), z), _ap(S, S.div, x, _ap(S, S.mul, y, z)))),
    ("1 / (1 / x) = x", 1, lambda S, x: (_ap(S, S.div, S.one, _ap(S, S.div, S.one, x)), x)),
    ("(x + y) / z = x / z + y / z", 3, lambda S, x, y, z: (_ap(S, S.div, _ap(S, S.add, x, y), z), _ap(S, S.add, _ap(S, S.div, x, z), _ap(S, S.div, y, z)))),
]


def law_census(system: str) -> list[dict]:
    """For each law: instances that hold, fail, are undefined; and the first counterexample."""
    S = SYSTEMS[system]
    rows = []
    for name, arity, f in LAWS:
        hold = fail = undef = 0
        example = None
        for t in itertools.product(S.sample, repeat=arity):
            lhs, rhs = f(S, *t)
            if lhs is UNDEF or rhs is UNDEF:
                undef += 1
            elif _key(lhs) == _key(rhs):
                hold += 1
            else:
                fail += 1
                if example is None:
                    example = f"{', '.join(S.show(v) for v in t)}: {S.show(lhs)} ≠ {S.show(rhs)}"
        rows.append({"law": name, "hold": hold, "fail": fail, "undefined": undef, "counterexample": example})
    return rows


def one_over_zero(system: str):
    S = SYSTEMS[system]
    one, zero = S.one, S.zero
    r1, r0 = S.div(one, zero), S.div(zero, zero)
    return ("undefined" if r1 is UNDEF else S.show(r1)), ("undefined" if r0 is UNDEF else S.show(r0))
