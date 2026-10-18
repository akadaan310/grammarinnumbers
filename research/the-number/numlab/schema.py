"""The substrate schema 𝒩 = (D, Σ, L, ⟦·⟧, 𝒪, ℛ, C) and translation obligations.

This is a *modelling definition* (NUM-DEF-001), not a theorem: it fixes what must
be stated before two numerical substrates can be compared.  A translation between
substrates is a pair (t, h): t rewrites words, h maps values.  The obligations
(NUM-DEF-004) are checked on finite samples by :func:`check_translation`; a
failed obligation is a recorded *model failure*, not an error to be hidden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from .systems import System


@dataclass
class Substrate:
    """𝒩 = (D, Σ, L, ⟦·⟧, 𝒪, ℛ, C)."""
    name: str
    D: str                                  # description of the value carrier
    system: System                          # Σ (alphabet), L (admissible), ⟦·⟧ (value)
    ops: dict = field(default_factory=dict)  # 𝒪: name -> partial function on values (None = undefined)
    converse: dict = field(default_factory=dict)  # ℛ: name -> function (a, b) -> list of solutions (finite samples)
    cost: Callable[[tuple], int] = len      # C: cost of a word (default: its length in symbols)


@dataclass
class Report:
    obligation: str
    checked: int
    failures: int
    example: Optional[str] = None

    def as_dict(self):
        return {"obligation": self.obligation, "checked": self.checked, "failures": self.failures, "example": self.example}


def check_translation(src: Substrate, dst: Substrate, t: Callable[[tuple], Optional[tuple]],
                      h: Callable[[int], int], sample: Iterable[int], transforms: dict | None = None) -> list:
    """Check O1 (value preservation), O2 (commutation with each shared operation
    where both sides are defined), O3 (converse-class preservation for each shared
    converse relation), O4 (cost ratio) and O5 (commutation with word
    transformations such as reversal) on the canonical words of ``sample``."""
    sample = list(sample)
    reports = []
    # O1
    bad, ex, n = 0, None, 0
    for v in sample:
        w = src.system.encode(v)
        if w is None:
            continue
        n += 1
        tw = t(w)
        ok = tw is not None and dst.system.admissible(tw) and dst.system.value(tw) == h(v)
        if not ok:
            bad += 1
            ex = ex or f"{v}: {w} -> {tw}"
    reports.append(Report("O1 value preservation", n, bad, ex))
    # O2
    for name in src.ops.keys() & dst.ops.keys():
        bad, ex, n = 0, None, 0
        for x in sample:
            for y in sample:
                a, b = src.ops[name](x, y), dst.ops[name](h(x), h(y))
                if a is None or b is None:
                    continue
                n += 1
                if h(a) != b:
                    bad += 1
                    ex = ex or f"h({x} {name} {y}) = {h(a)} but h({x}) {name} h({y}) = {b}"
        reports.append(Report(f"O2 commutation with {name}", n, bad, ex))
    # O3
    for name in src.converse.keys() & dst.converse.keys():
        bad, ex, n = 0, None, 0
        k = lambda s: 0 if not s else 1 if len(s) == 1 else 2
        for a in sample:
            for b in sample:
                n += 1
                ka, kb = k(src.converse[name](a, b)), k(dst.converse[name](h(a), h(b)))
                if ka != kb:
                    bad += 1
                    ex = ex or f"Sol({a},{b}) class {ka} -> class {kb}"
        reports.append(Report(f"O3 converse class of {name}", n, bad, ex))
    # O4: cost ratio range
    ratios = []
    for v in sample:
        w = src.system.encode(v)
        if w and t(w):
            ratios.append(dst.cost(t(w)) / src.cost(w))
    if ratios:
        reports.append(Report(f"O4 cost ratio in [{min(ratios):.3f}, {max(ratios):.3f}]", len(ratios), 0))
    # O5
    for name, (f_src, f_dst) in (transforms or {}).items():
        bad, ex, n = 0, None, 0
        for v in sample:
            w = src.system.encode(v)
            if w is None:
                continue
            fw = f_src(w)
            if not src.system.admissible(fw):
                continue
            n += 1
            lhs, rhs = t(fw), f_dst(t(w))
            if lhs is None or rhs is None or dst.system.value(lhs) != dst.system.value(rhs):
                bad += 1
                ex = ex or f"{v}: t({name}(w)) ≠ {name}(t(w))"
        reports.append(Report(f"O5 commutation with {name}", n, bad, ex))
    return [r.as_dict() for r in reports]
