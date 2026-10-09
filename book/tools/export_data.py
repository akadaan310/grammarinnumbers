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
    if cgt and os.path.isdir(cgt):
        files = [os.path.join(cgt, f) for f in os.listdir(cgt) if f.endswith(".md")]
        dump("cgt_ids.json", ledger_ids(files, "CGT"))
    dump("lab_fixtures.json", lab_fixtures())
    dump("experiments.json", experiments())
    print(f"exported book/data (ginsdk {ginsdk.__version__})")


if __name__ == "__main__":
    main()
