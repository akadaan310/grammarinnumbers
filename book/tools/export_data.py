"""Export machine-generated data consumed by the book build (book/data/):

* sdk_reference.json   -- API reference generated from ginsdk docstrings
* contracts.json       -- the operation contracts (schema gin-contracts/1)
* ledger_ids.json      -- every GIN-* identifier present in the ledger files
* cgt_ids.json         -- CGT-* identifiers of the separate CGT ledger, refreshed only
                          when CGT_REPO points at a checkout (read-only; otherwise the
                          committed file is kept, so this repository builds alone)
* lab_fixtures.json    -- reference outcomes computed by the SDK, which the browser
                          laboratory (gin-core.js) must reproduce exactly (`npm test`)
* experiments.json     -- compact experiment numbers quoted by the book
* num_fixtures.json    -- reference results of the research lane's library (research/the-number/numlab)
                          that the lane's browser port num-core.js must reproduce (`npm test`)
* num_results.json     -- the lane's stored experiment results (NUM-EXP-001..004), shown by its labs

Run from anywhere:  python3 book/tools/export_data.py
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
REPO = os.path.dirname(BOOK)
sys.path.insert(0, os.path.join(REPO, "sdk", "src"))

import ginsdk  # noqa: E402
from ginsdk import contracts, expr  # noqa: E402

OUT = os.path.join(BOOK, "data")
MODULES = ["ginsdk", "ginsdk.numerals", "ginsdk.peano", "ginsdk.converse", "ginsdk.expr", "ginsdk.contracts", "ginsdk.ieee",
           "ginsdk.machine", "ginsdk.circuits", "ginsdk.bigint", "ginsdk.numbertheory", "ginsdk.cost"]
LEDGER_FILES = ["RESULTS.md", "DEFINITIONS.md", "HYPOTHESES.md", "COUNTEREXAMPLES.md", "OPEN_PROBLEMS.md", "EXPERIMENTS.md",
                "DECISION_LOG.md", "PROVENANCE.md", "LITERATURE_REVIEW.md", "NUMBER_GRAMMAR.md", "ARITHMETIC_GRAMMAR.md",
                "FORMAL_MODELS.md", "MACHINE_MODEL.md", "NUMBER_THEORY.md", "CGT_CONCEPT_MAP.md", "RESEARCH_CHARTER.md",
                "PUBLICATION_STATUS.md", "EDITION_HISTORY.md", "experiments/results/SUMMARY.md"]


def sdk_reference():
    mods, seen = [], set()
    for name in MODULES:
        m = importlib.import_module(name)
        members = []
        names = getattr(m, "__all__", None) if name == "ginsdk" else None
        names = names or [n for n in dir(m) if not n.startswith("_")]
        for n in sorted(names):
            obj = getattr(m, n, None)
            if obj is None or not (inspect.isclass(obj) or inspect.isfunction(obj)):
                continue
            if getattr(obj, "__module__", "").split(".")[0] != "ginsdk":
                continue
            key = (obj.__module__, obj.__qualname__)
            if name == "ginsdk" or key in seen or obj.__module__ != name:
                continue
            seen.add(key)
            try:
                sig = str(inspect.signature(obj))
            except (TypeError, ValueError):
                sig = ""
            members.append({"name": n, "kind": "class" if inspect.isclass(obj) else "function", "signature": sig,
                            "doc": inspect.cleandoc(obj.__doc__ or "")})
        mods.append({"name": name, "doc": inspect.cleandoc(m.__doc__ or ""), "members": members})
    suite = unittest.defaultTestLoader.discover(os.path.join(REPO, "sdk", "tests"), top_level_dir=os.path.join(REPO, "sdk", "tests"))
    return {"version": ginsdk.__version__, "tests": suite.countTestCases(), "modules": mods}


def ledger_ids(files, prefix):
    ids = set()
    for f in files:
        p = os.path.join(REPO, f) if not os.path.isabs(f) else f
        if os.path.exists(p):
            ids |= set(re.findall(rf"\b{prefix}-[A-Z]+-\d+[a-z]?\b", open(p, encoding="utf8").read()))
    return sorted(ids)


# The laboratory's fixture set: every expression of the book's "laboratory" examples,
# in every domain the browser core implements.
FIXTURE_EXPRS = ["1 + 1", "2 + 2", "6 / 3", "0 / 1", "1 / 0", "0 / 0", "0 - 1", "7 / 2", "-7 / 2", "-7 // 2", "7 % 3", "-7 % 2",
                 "2 * 3", "3 * 2", "2 * 0", "0 * 0", "1 / 3", "0.1 + 0.2", "(0.1 + 0.2) + 0.3", "0.1 + (0.2 + 0.3)", "2 ^ 10",
                 "2 ^ -1", "0 ^ 0", "0 ^ -1", "2147483647 + 1", "-2147483648 / -1", "(-2147483647 - 1) / -1", "-2147483647 - 2",
                 "65536 * 65536", "1 / 0 - 1 / 0", "0 * (1 / 0)", "0b101 + 0x1F", "10₂ + 1", "1e3", "1 +", "(1 + 2", "sqrt(4)",
                 "sqrt(2)", "sqrt(0 - 1)", "gcd(12, 18)", "3 - 5", "2 / 4", "3 / 4", "1 / 10", "9007199254740992 + 1",
                 "1.5 * 2", "100 / 7", "5 - 5", "4 / 2 / 2", "-(3)", "2 ^ 3 ^ 2", "-2 ^ 2", "0.5", "1 / (2 - 2)"]
FIXTURE_DOMAINS = ["N", "Z", "Q", "Z/7", "Z/6", "Z/2", "binary64", "binary32", "JS Number", "Python", "JS BigInt", "int32 x86-64",
                   "int32 AArch64", "int32 RISC-V", "int32 C", "int32 Java", "int32 Rust (debug)", "int32 Go"]


def lab_fixtures():
    rows = []
    for e in FIXTURE_EXPRS:
        for d in FIXTURE_DOMAINS:
            o = expr.evaluate(e, d)
            rows.append({"e": e, "d": d, "status": o.status, "layer": o.layer, "display": o.display if o.status in ("value", "special") else "",
                         "flags": sorted(o.flags)})
    rel = []
    for e in ["1 / 0", "0 / 0", "6 / 3", "0.1 + 0.2", "2147483647 + 1", "-7 / 2", "-7 // 2", "1 + 1"]:
        for d in FIXTURE_DOMAINS:
            r = contracts.inspect(e, d)
            rel.append({"e": e, "d": d, "relation": r["relation"]["kind"], "math": r["mathematics"]["status"]})
    return {"generated_by": "book/tools/export_data.py", "sdk_version": ginsdk.__version__, "outcomes": rows, "relations": rel}


def experiments():
    res = os.path.join(REPO, "experiments", "results")
    out = {}
    for f in sorted(os.listdir(res)):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(res, f)))
            out[f[:-5]] = {k: v for k, v in d.items() if k not in ("environment",)} if isinstance(d, dict) else d
    return out


def num_fixtures():
    """Fixtures for num-core.js from the research lane's Python library (not part of the edition's claims)."""
    lane = os.path.join(REPO, "research", "the-number")
    sys.path.insert(0, lane)
    from numlab import fibers as F, layout as L, systems as S
    keys = ["base2", "base3", "base10", "base16", "bijective2", "bijective10", "balanced-ternary", "negabinary", "negadecimal",
            "sign-magnitude2", "twos8", "factoradic", "zeckendorf", "roman-strict"]
    signed = {"balanced-ternary", "negabinary", "negadecimal", "sign-magnitude2", "twos8"}
    values = sorted(set(list(range(-130, 131)) + [255, 256, 999, 1000, 1994, 3999, 4000, 65535, 10 ** 6, 123456789]))
    enc = []
    for k in keys:
        s = S.SYSTEMS[k]()
        for n in values:
            if n < 0 and k not in signed:
                continue
            w = s.encode(n)
            enc.append({"s": k, "n": n, "w": None if w is None else S.show(w)})
    prof = {str(n): F.zmod(n).profile("*") for n in range(1, 13)}
    trans = {}
    for m in range(1, 13):
        for k in range(1, m + 1):
            if m % k == 0:
                mp = F.Map("", F.zmod(m), F.zmod(k), lambda x, k=k: x % k, ("*",), False, True)
                trans[f"{m}->{k}"] = F.transfer(mp, "*")["matrix"]
    chan = {f"{a}{b}": L.channel_independence(str(a), str(b))["table"] for a in range(1, 10) for b in range(1, 10) if a != b}
    maya = [{"n": n, "glyphs": [m.glyph for m in L.maya_layout(n)], "cal": L.maya_value(L.maya_layout(n), True)}
            for n in list(range(0, 450, 7)) + [1000, 7999, 8000, 159999]]
    return {"generated_by": "book/tools/export_data.py from research/the-number/numlab", "encode": enc, "profiles": prof,
            "transfer": trans, "channels": chan, "maya": maya}


def num_results():
    res = os.path.join(REPO, "research", "the-number", "results")
    return {f[:-5]: json.load(open(os.path.join(res, f), encoding="utf8")) for f in sorted(os.listdir(res)) if f.endswith(".json")}


def main():
    os.makedirs(OUT, exist_ok=True)

    def dump(name, obj):
        with open(os.path.join(OUT, name), "w", encoding="utf8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=None, separators=(",", ":"), default=str)
            f.write("\n")
    dump("sdk_reference.json", sdk_reference())
    dump("contracts.json", contracts.contracts_document())
    dump("ledger_ids.json", ledger_ids(LEDGER_FILES, "GIN"))
    cgt = os.environ.get("CGT_REPO")
    if cgt and os.path.isdir(os.path.join(cgt, "book", "dist", "ledger")):
        # map each CGT identifier to the ledger page of the CGT website that anchors it
        led = os.path.join(cgt, "book", "dist", "ledger")
        anchors = {}
        for f in sorted(os.listdir(led)):
            if f.endswith(".html") and f != "index.html":
                for i in re.findall(r'id="(CGT-[A-Z]+-\d+[a-z]?)"', open(os.path.join(led, f), encoding="utf8").read()):
                    anchors.setdefault(i, f[:-5])
        dump("cgt_ids.json", anchors)
    elif cgt:
        print("CGT_REPO given but its book has not been built (book/dist/ledger missing): cgt_ids.json kept")
    dump("lab_fixtures.json", lab_fixtures())
    dump("experiments.json", experiments())
    dump("num_fixtures.json", num_fixtures())
    dump("num_results.json", num_results())
    print(f"exported book/data (ginsdk {ginsdk.__version__})")


if __name__ == "__main__":
    main()
