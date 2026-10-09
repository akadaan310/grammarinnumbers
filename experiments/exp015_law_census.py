"""GIN-EXP-015  What each way of giving 1/0 a value gives up: an exact law census.

Hypothesis GIN-H-041 (the extension trilemma, GIN-THM-004, checked by computation):
every system that makes division total violates the converse law y·(x/y) = x
somewhere; systems that keep it (where defined) leave some quotients undefined;
and each total system's other losses are exactly those stated in the book.

Systems and laws: ginsdk.totalized (field ℚ, meadow ℚ, wheel of fractions of ℤ,
projective line, extended rationals, IEEE binary16, 8-bit RISC-V and AArch64
integer division).  Every tuple of a fixed sample of 6–11 elements is evaluated
for ten laws; the wheel is also checked against Carlström's fourteen axiom
instances (as listed in the Wheel theory article; the paper was not read).
Exact, deterministic; no randomness.
"""
from common import write
from ginsdk import totalized as T

data = {"systems": {}, "wheel_axioms": {k: list(v) for k, v in T.check_wheel_axioms().items()}}
for key, S in T.SYSTEMS.items():
    one, zero = T.one_over_zero(key)
    data["systems"][key] = {"name": S.name, "1/0": one, "0/0": zero, "laws": T.law_census(key)}
write("GIN-EXP-015", ["GIN-H-041"], None, data)
total = [k for k, v in data["systems"].items() if v["1/0"] != "undefined" and v["0/0"] != "undefined"]
conv = {k: next(r for r in v["laws"] if r["law"].startswith("y·(x / y)")) for k, v in data["systems"].items()}
print("EXP-015 wheel axioms all hold:", all(a == b for a, b in data["wheel_axioms"].values()))
for k, v in data["systems"].items():
    c = conv[k]
    print(f"  {k:10s} 1/0={v['1/0']:10s} 0/0={v['0/0']:10s} converse law: hold {c['hold']}, fail {c['fail']}, undefined {c['undefined']}")
assert all(conv[k]["fail"] > 0 for k in total), "a total system kept the converse law"
assert all(conv[k]["fail"] == 0 and conv[k]["undefined"] > 0 for k in ("field", "projective", "extended"))
