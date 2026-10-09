"""Command-line interface:  python3 -m ginsdk <command> ...

  inspect EXPR [--domain D] [--x VALUE]   layered record (JSON) of one expression
  eval    EXPR [--domain D]               one-line outcome
  compare EXPR [--domains D1,D2,...]      the same expression across domains
  contracts [OP]                          machine-readable operation contracts (JSON)
  domains                                 list evaluation domains
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction

from . import contracts, expr


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m ginsdk", description="Grammar in Numbers SDK")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("inspect", "eval"):
        q = sub.add_parser(name)
        q.add_argument("expression")
        q.add_argument("--domain", default="Q")
        q.add_argument("--x", default=None, help="value of the variable x (exact rational)")
    c = sub.add_parser("compare")
    c.add_argument("expression")
    c.add_argument("--domains", default=None)
    k = sub.add_parser("contracts")
    k.add_argument("op", nargs="?")
    sub.add_parser("domains")
    a = p.parse_args(argv)
    if a.cmd in ("inspect", "eval"):
        env = {"x": Fraction(a.x)} if a.x is not None else None
        try:
            expr.domain(a.domain)
        except KeyError as e:
            print(e.args[0], file=sys.stderr)
            return 2
        if a.cmd == "inspect":
            print(contracts.dumps(contracts.inspect(a.expression, a.domain, env)))
        else:
            print(expr.evaluate(a.expression, a.domain, env).headline())
        return 0
    if a.cmd == "compare":
        names = a.domains.split(",") if a.domains else None
        for o in expr.compare(a.expression, names):
            print(o.headline())
        return 0
    if a.cmd == "contracts":
        doc = contracts.contract(a.op) if a.op else contracts.contracts_document()
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return 0
    if a.cmd == "domains":
        for n, d in expr.DOMAINS.items():
            print(f"{n:20s} {d.description}")
        print(f"{'Z/n':20s} integers modulo n (any n ≥ 1)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
