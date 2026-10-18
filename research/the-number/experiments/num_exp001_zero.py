"""NUM-EXP-001 — census of zero, empty and absence across substrates.

Question: are "zero", "empty" and "absent" one notion or several?  For each
candidate object in several substrates (Python, IEEE 754 via Python floats,
SQLite through the standard library, JavaScript via node when available, the GiN
SDK), record: its identity tests, whether equality is substitutive (x == y but
f(x) != f(y)), additive-identity behaviour, and how aggregates over an empty
collection answer.  Prediction under NUM-HYP-001: at least three behaviourally
distinct classes (numeric zero, empty structure, absence marker) are separated
by an observable in every substrate examined.  Falsifier: a substrate in which
no observable separates them.
"""
from __future__ import annotations

import json
import math
import os
import platform
import shutil
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LANE))
sys.path[:0] = [LANE, os.path.join(ROOT, "sdk", "src")]

from ginsdk import evaluate                      # noqa: E402
from ginsdk import converse                       # noqa: E402


def py_census():
    objs = {"int 0": 0, "float +0.0": 0.0, "float -0.0": -0.0, "False": False, "Fraction 0": __import__("fractions").Fraction(0),
            "complex 0j": 0j, "Decimal 0": __import__("decimal").Decimal(0), "Decimal -0": __import__("decimal").Decimal("-0"),
            "empty str": "", "empty tuple": (), "empty list": [], "empty frozenset": frozenset(), "range(0)": range(0),
            "None": None, "NaN": float("nan")}
    rows = {}
    for k, v in objs.items():
        r = {"type": type(v).__name__, "truthy": bool(v), "== 0": v == 0, "is identical to itself under ==": v == v}
        try:
            r["hash == hash(0)"] = hash(v) == hash(0)
        except TypeError:
            r["hash == hash(0)"] = "unhashable"
        try:
            r["v + 0"] = repr(v + 0)
        except TypeError as e:
            r["v + 0"] = "TypeError"
        try:
            r["len"] = len(v)
        except TypeError:
            r["len"] = "TypeError"
        rows[k] = r
    # equality classes under ==
    names = list(objs)
    classes = []
    for n in names:
        for c in classes:
            if objs[c[0]] == objs[n] and objs[n] == objs[c[0]]:
                c.append(n)
                break
        else:
            classes.append([n])
    # dictionary key collapse: equal and equal-hash keys merge
    d = {}
    for n in ("int 0", "float +0.0", "float -0.0", "False", "Fraction 0", "complex 0j", "Decimal 0"):
        d[objs[n]] = n
    # substitutivity failures: x == y but f(x) != f(y)
    subst = []
    if 0.0 == -0.0 and math.copysign(1, 0.0) != math.copysign(1, -0.0):
        subst.append("+0.0 == -0.0 but copysign(1, x) gives 1.0 vs -1.0")
    if 0.0 == -0.0 and math.atan2(0.0, -1.0) != math.atan2(-0.0, -1.0):
        subst.append(f"+0.0 == -0.0 but atan2(x, -1) gives {math.atan2(0.0, -1.0)} vs {math.atan2(-0.0, -1.0)}")
    if 0 == False and repr(0) != repr(False):
        subst.append("0 == False but repr differs ('0' vs 'False')")
    if 0 == 0.0 and type(0 // 1) != type(0.0 // 1):
        subst.append("0 == 0.0 but x // 1 has type int vs float")
    nan = float("nan")
    reflex = {"NaN == NaN": nan == nan, "NaN in [NaN] (same object)": nan in [nan], "float('nan') in [float('nan')]": float("nan") in [float("nan")]}
    empties = {"sum([])": sum([]), "math.prod([])": math.prod([]), "min([], default=None)": min([], default=None),
               "max of empty raises": _raises(lambda: max([])), "all([])": all([]), "any([])": any([]),
               "''.join([])": "", "len(())": 0}
    return {"objects": rows, "equality_classes": classes, "dict_after_inserting_7_zero_keys": {repr(k): v for k, v in d.items()},
            "substitutivity_failures": subst, "reflexivity": reflex, "empty_aggregates": {k: repr(v) for k, v in empties.items()}}


def _raises(f):
    try:
        f()
        return False
    except Exception as e:
        return type(e).__name__


def sqlite_census():
    con = sqlite3.connect(":memory:")
    q = lambda s: con.execute(s).fetchall()[0]
    con.execute("create table t(x)")
    con.execute("create table e(x)")
    con.executemany("insert into t values (?)", [(1,), (None,), (0,), ("",)])
    return {
        "sqlite_version": sqlite3.sqlite_version,
        "NULL = NULL": q("select NULL = NULL")[0],
        "NULL IS NULL": q("select NULL IS NULL")[0],
        "0 = ''": q("select 0 = ''")[0],
        "0 = 0.0": q("select 0 = 0.0")[0],
        "SUM over empty table": q("select sum(x) from e")[0],
        "TOTAL over empty table": q("select total(x) from e")[0],
        "COUNT over empty table": q("select count(x) from e")[0],
        "COUNT(x) with a NULL row (4 rows)": q("select count(x) from t")[0],
        "COUNT(*) (4 rows)": q("select count(*) from t")[0],
        "SUM(x) ignoring NULL and ''": q("select sum(x) from t")[0],
        "1/0": q("select 1/0")[0],
        "1.0/0": q("select 1.0/0")[0],
        "0/0": q("select 0/0")[0],
        "NULL + 1": q("select NULL + 1")[0],
        "CAST('' AS INTEGER)": q("select cast('' as integer)")[0],
        "CAST('abc' AS INTEGER)": q("select cast('abc' as integer)")[0],
    }


JS = r"""
const r = {};
const t = (k, f) => { try { r[k] = String(f()); } catch (e) { r[k] = "throws " + e.constructor.name; } };
t("0 === -0", () => 0 === -0); t("Object.is(0, -0)", () => Object.is(0, -0)); t("1/-0", () => 1/-0);
t("NaN === NaN", () => NaN === NaN); t("Object.is(NaN, NaN)", () => Object.is(NaN, NaN)); t("[NaN].includes(NaN)", () => [NaN].includes(NaN)); t("[NaN].indexOf(NaN)", () => [NaN].indexOf(NaN));
t("null == 0", () => null == 0); t("null >= 0", () => null >= 0); t("null > 0", () => null > 0);
t("undefined == null", () => undefined == null); t("undefined == 0", () => undefined == 0);
t("[] == 0", () => [] == 0); t("'' == 0", () => '' == 0); t("[] == ''", () => [] == '');
t("null + 1", () => null + 1); t("undefined + 1", () => undefined + 1); t("[] + []", () => JSON.stringify([] + []));
t("Number('')", () => Number('')); t("Number(null)", () => Number(null)); t("Number(undefined)", () => Number(undefined));
t("[].reduce((a,b)=>a+b)", () => [].reduce((a,b)=>a+b)); t("[].reduce((a,b)=>a+b, 0)", () => [].reduce((a,b)=>a+b, 0));
t("Math.max()", () => Math.max()); t("Math.min()", () => Math.min());
t("0n === -0n", () => 0n === -0n); t("1n/0n", () => 1n/0n);
t("new Map([[0,'a'],[-0,'b']]).size", () => new Map([[0,'a'],[-0,'b']]).size);
console.log(JSON.stringify(r));
"""


def js_census():
    node = shutil.which("node")
    if not node:
        return {"status": "NOT RUN", "reason": "node not found", "replicate": "install Node.js >= 18 and rerun"}
    out = subprocess.run([node, "-e", JS], capture_output=True, text=True, timeout=30)
    ver = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    return {"node": ver, "results": json.loads(out.stdout)}


def gin_census():
    exprs = ["0", "0 - 0", "1 / 0", "0 / 0", "0 / 1", "0 ^ 0", "0 ^ -1"]
    doms = ["Z", "Q", "binary64", "Python", "Z/6", "int32 C", "JS BigInt"]
    table = {}
    for e in exprs:
        table[e] = {d: (lambda o: f"{o.status}" + (f" {o.display}" if o.status in ('value', 'special') else ""))(evaluate(e, d)) for d in doms}
    s = converse.divide_mod(0, 0, 6)
    return {"evaluate": table, "solution set of 0·c = 0 in Z/6": {"kind": s.kind, "size": s.size}}


def classify_three_way(py, sq, js):
    """Does each substrate separate numeric zero, empty structure and absence by some observable?"""
    out = {}
    o = py["objects"]
    out["Python"] = {
        "zero vs empty": o["int 0"]["v + 0"] != o["empty tuple"]["v + 0"],
        "zero vs absence": o["int 0"]["== 0"] and not o["None"]["== 0"],
        "empty vs absence": o["empty tuple"]["len"] == 0 and o["None"]["len"] == "TypeError",
        "observables": "v + 0 (TypeError for () and None), == 0, len (0 for (), TypeError for None)",
    }
    out["SQLite"] = {
        "zero vs absence": sq["NULL = NULL"] is None and sq["0 = 0.0"] == 1,
        "empty sum is absence, not zero": sq["SUM over empty table"] is None and sq["TOTAL over empty table"] == 0.0,
        "zero vs empty string": sq["0 = ''"] == 0,
        "observables": "= (three-valued), SUM vs TOTAL over empty, typed comparison",
    }
    if "results" in js:
        r = js["results"]
        out["JavaScript"] = {
            "zero vs absence (null)": r["null == 0"] == "false" and r["null >= 0"] == "true",
            "comparison is not an order on {null, 0}": r["null >= 0"] == "true" and r["null > 0"] == "false" and r["null == 0"] == "false",
            "empty array coerces to zero": r["[] == 0"] == "true",
            "observables": "==, >=, coercion by +",
        }
    return out


def main():
    py, sq, js, gin = py_census(), sqlite_census(), js_census(), gin_census()
    res = {"experiment": "NUM-EXP-001", "python": platform.python_version(),
           "python_census": py, "sqlite_census": sq, "js_census": js, "gin_census": gin,
           "three_way_separation": classify_three_way(py, sq, js)}
    py_classes = len(py["equality_classes"])
    res["summary"] = {
        "python_objects": len(py["objects"]), "python_equality_classes_under_==": py_classes,
        "python_zero_keys_surviving_in_dict": len(py["dict_after_inserting_7_zero_keys"]),
        "substitutivity_failures_found": len(py["substitutivity_failures"]),
        "sqlite_empty_sum": sq["SUM over empty table"], "sqlite_empty_total": sq["TOTAL over empty table"],
    }
    os.makedirs(os.path.join(LANE, "results"), exist_ok=True)
    with open(os.path.join(LANE, "results", "num_exp001.json"), "w", encoding="utf8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, sort_keys=True, default=str)
    print("NUM-EXP-001:", json.dumps(res["summary"], ensure_ascii=False))
    print("  three-way separation:", json.dumps(res["three_way_separation"], ensure_ascii=False))


if __name__ == "__main__":
    main()
