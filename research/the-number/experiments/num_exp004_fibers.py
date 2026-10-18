"""NUM-EXP-004 — converse admissibility under translation.

(A) Fiber profiles (none / unique / many) of b ⊙ c = a for every (a, b) in
    Z/n (n ≤ 12), GF(p) (p ≤ 11), GF(4) and three monoids.
(B) Class changes along maps: surjections (Z/12 → Z/4, Z/12 → Z/3, Z → Z/n on a
    window), injections (GF(2) → GF(4); Z/4 → Z/12, x ↦ 3x, additive only; the
    inclusion of a window of Z into Q), and sign extension between word sizes.
    Predictions from the classical preservation theorem (NUM-HIST-001/002) are
    checked: a homomorphism never sends a solvable problem to an unsolvable one;
    an injective one never sends 'many' to fewer.  Every other change is recorded.
(C) Totalization: a total a ⊘ b built by selection loses the three-way class;
    the fraction of problems where its value is not a unique solution is counted.
(D) Evaluators against exact enumeration: ginsdk (Python) and the laboratory
    core gin-core.js (via node) on a / b in Z/n, n ≤ 12, all residues.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LANE))
sys.path[:0] = [LANE, os.path.join(ROOT, "sdk", "src")]

from numlab import fibers as F          # noqa: E402
from ginsdk import evaluate              # noqa: E402


def gfp(p):
    a = F.zmod(p)
    a.name = f"GF({p})"
    return a


def part_a():
    algs = [F.zmod(n) for n in range(1, 13)] + [gfp(p) for p in (2, 3, 5, 7, 11)] + [F.gf4()]
    out = {}
    for A in algs:
        out[A.name] = {op: A.profile(op) for op in A.ops}
    for A in (F.saturating(7), F.maxmonoid(7), F.zmod(8)):
        out[A.name + " (monoid +)"] = {"+": A.profile("+")}
    return out


def part_b():
    Z = lambda lo, hi: F.integers(lo, hi)
    maps = [
        F.Map("Z/12 -> Z/4 (reduction)", F.zmod(12), F.zmod(4), lambda x: x % 4, ("+", "*"), False, True),
        F.Map("Z/12 -> Z/3 (reduction)", F.zmod(12), F.zmod(3), lambda x: x % 3, ("+", "*"), False, True),
        F.Map("Z/8 -> Z/2 (reduction)", F.zmod(8), F.zmod(2), lambda x: x % 2, ("+", "*"), False, True),
        F.Map("Z/6 -> Z/2 x Z/3 (CRT isomorphism)", F.zmod(6), F.product(F.zmod(2), F.zmod(3)), lambda x: (x % 2, x % 3), ("+", "*"), True, True),
        F.Map("GF(2) -> GF(4) (subfield)", gfp(2), F.gf4(), lambda x: x, ("+", "*"), True, False),
        F.Map("Z/4 -> Z/12, x -> 3x (additive)", F.zmod(4), F.zmod(12), lambda x: 3 * x % 12, ("+",), True, False),
        F.Map("sat{0..7} -> sat{0..3}, x -> min(x,3)", F.saturating(7), F.saturating(3), lambda x: min(x, 3), ("+",), False, True),
        F.Map("max{0..7} -> max{0..3}, x -> min(x,3)", F.maxmonoid(7), F.maxmonoid(3), lambda x: min(x, 3), ("+",), False, True),
    ]
    out = {}
    for m in maps:
        for op in m.src.ops:
            if op not in m.dst.ops:
                continue
            hom = F.is_hom(m, op)
            t = F.transfer(m, op)
            viol = F.predicted_violations(m, t["matrix"]) if hom else []
            out[f"{m.name} [{op}]"] = {"homomorphism for op": hom, "injective": m.injective, "surjective": m.surjective,
                                       **t, "violations of the preservation prediction": viol}
    # Z (window, exact solution counts in Z) -> Z/n
    for n in (4, 6, 8):
        win = Z(-12, 12)
        m = F.Map(f"Z -> Z/{n} on a in [-12,12], b in [-12,12]", win, F.zmod(n), lambda x, n=n: x % n, ("+", "*"), False, True)
        for op in ("+", "*"):
            t = F.transfer(m, op, src_count=F.z_sol)
            out[f"{m.name} [{op}]"] = {"homomorphism for op": True, "injective": False, "surjective": True, **t,
                                       "violations of the preservation prediction": F.predicted_violations(m, t["matrix"])}
    # Z -> Q (injective): b c = a, counted exactly
    mat = {s: {t: 0 for t in (F.NONE, F.UNIQUE, F.MANY)} for s in (F.NONE, F.UNIQUE, F.MANY)}
    for a in range(-12, 13):
        for b in range(-12, 13):
            s = F.klass(F.z_sol("*", a, b))
            q = F.klass(2 if (b == 0 and a == 0) else 0 if b == 0 else 1)
            mat[s][q] += 1
    viol = [] if not (mat[F.UNIQUE][F.NONE] or mat[F.MANY][F.NONE] or mat[F.MANY][F.UNIQUE]) else ["violation"]
    out["Z -> Q inclusion on a, b in [-12,12] [*]"] = {"homomorphism for op": True, "injective": True, "surjective": False, "matrix": mat,
                                                     "examples": {"none->unique": "2c=1 in Z (none) -> 2c=1 in Q (unique)"},
                                                     "violations of the preservation prediction": viol}
    return out


def part_a_note():
    """Two non-isomorphic monoids with the same converse profile: the profile is not a complete invariant."""
    s, m = F.saturating(7), F.maxmonoid(7)
    iso = any(all(p[s.ops["+"](x, y)] == m.ops["+"](p[x], p[y]) for x in s.elems for y in s.elems)
              for p in __import__("itertools").permutations(s.elems) if p[0] == 0)
    return {"sat{0..7} profile": s.profile("+"), "max{0..7} profile": m.profile("+"),
            "isomorphic (exhaustive search over bijections fixing 0)": iso,
            "idempotent elements": {"sat": sum(s.ops["+"](x, x) == x for x in s.elems), "max": sum(m.ops["+"](x, x) == x for x in m.elems)}}


def part_c():
    out = {}
    for n in (6, 8, 12):
        A = F.zmod(n)
        tot = F.totalize(A, "*", "min", 0)
        stats = {"none": 0, "unique": 0, "many": 0, "total value is the unique solution": 0}
        for a in A.elems:
            for b in A.elems:
                s = A.sol("*", a, b)
                k = F.klass(len(s))
                stats[k] += 1
                if k == F.UNIQUE and tot(a, b) == s[0]:
                    stats["total value is the unique solution"] += 1
        stats["problems answered with a value that is not a unique solution"] = stats["none"] + stats["many"]
        stats["fraction"] = round((stats["none"] + stats["many"]) / n ** 2, 4)
        # collisions: a none-problem and a many-problem answered with the same value
        stats["none and many both answered 0"] = tot(1, 0) == 0 and tot(0, 0) == 0
        out[f"Z/{n}"] = stats
    return out


JS = r"""
require(process.argv[1]); const G = globalThis.GIN; const r = {};
for (let n = 1; n <= 12; n++) for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) {
  const o = G.evaluate(`${a} / ${b}`, `Z/${n}`); r[`${n}:${a}:${b}`] = o.status + (o.status === "value" ? " " + o.display : "");
}
console.log(JSON.stringify(r));
"""


def part_d():
    exact, py = {}, {}
    for n in range(1, 13):
        A = F.zmod(n)
        for a in range(n):
            for b in range(n):
                s = A.sol("*", a, b)
                k = F.klass(len(s))
                exact[f"{n}:{a}:{b}"] = {"none": "no-solution", "unique": f"value {s[0] if s else ''}", "many": "non-unique"}[k]
                o = evaluate(f"{a} / {b}", f"Z/{n}")
                py[f"{n}:{a}:{b}"] = o.status + (f" {o.display}" if o.status == "value" else "")
    out = {"cases": len(exact), "ginsdk disagreements with exact": [k for k in exact if exact[k] != py[k]][:10]}
    out["ginsdk agreement count"] = sum(exact[k] == py[k] for k in exact)
    node = shutil.which("node")
    if node:
        core = os.path.join(ROOT, "book", "site", "assets", "js", "gin-core.js")
        js = json.loads(subprocess.run([node, "-e", JS, core], capture_output=True, text=True, timeout=60).stdout)
        out["gin-core.js agreement count"] = sum(exact[k] == js.get(k) for k in exact)
        out["gin-core.js disagreements with exact"] = [f"{k}: {js.get(k)} vs {exact[k]}" for k in exact if exact[k] != js.get(k)][:10]
    else:
        out["gin-core.js"] = "NOT RUN (node not found)"
    return out


def main():
    res = {"experiment": "NUM-EXP-004", "A_profiles": part_a(), "A_profile_not_complete": part_a_note(), "B_transfer": part_b(), "C_totalization": part_c(), "D_evaluators": part_d()}
    os.makedirs(os.path.join(LANE, "results"), exist_ok=True)
    with open(os.path.join(LANE, "results", "num_exp004.json"), "w", encoding="utf8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, sort_keys=True)
    print("NUM-EXP-004")
    for k in ("Z/12", "Z/4", "GF(4)", "Z/1", "sat{0..7} (monoid +)", "max{0..7} (monoid +)"):
        print(" A", k, res["A_profiles"][k])
    for k, v in res["B_transfer"].items():
        changes = {f"{s}->{t}": c for s, row in v["matrix"].items() for t, c in row.items() if s != t and c}
        print(" B", k, "| hom:", v["homomorphism for op"], "| changes:", changes, "| violations:", v["violations of the preservation prediction"])
    print(" C", json.dumps(res["C_totalization"]))
    print(" D", json.dumps(res["D_evaluators"], ensure_ascii=False))


if __name__ == "__main__":
    main()
