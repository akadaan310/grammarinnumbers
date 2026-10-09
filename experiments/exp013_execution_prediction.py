"""GIN-EXP-013  Predicting real execution: operation contracts versus naive evaluation.

Question (Part XVI of the book).  Before running `a op b` in some language, can one
predict what will happen — a value (which one?), or a refusal (exception, trap,
panic)?  Three predictors are compared against what this host's toolchains
actually do:

  model    ginsdk.expr.evaluate in the domain that names the language and type
           (int32 C / int32 x86-64, int32 Java, int32 Go, int32 Rust (debug),
           JS BigInt, JS Number, Python): the book's operation contracts.
  naive-py "evaluate it in a Python REPL": unbounded integers, '/' is true
           division, '%' floors, a zero divisor raises.  This is what a programmer
           (or a code assistant) gets by trying the expression in Python.
  naive-c  "mathematical integers with C-style division": unbounded integers,
           '/' truncates toward zero, '%' takes the sign of the dividend, a zero
           divisor is an error.  This is the textbook mental model of integer
           arithmetic.

Corpus.  Operands V = {0, ±1, ±2, 3, ±7, 46341, 65536, INT_MAX, INT_MIN}, operators
{+, −, ×, /, %}: all 13 × 13 × 5 = 845 single operations, evaluated with operands
supplied at run time (no constant folding).  Hypothesis GIN-H-040: the model
predicts outcome class and value for every case its contracts cover, and the
naive predictors fail exactly on the boundary cases (overflow, negative
division, zero divisors, true division).

Ground truth: real executions (gcc -O0 on x86-64; OpenJDK; go; rustc debug; node;
CPython), one process per language, exceptions caught in-process.  ISO C leaves
signed overflow and division by zero undefined; for C two model domains are
scored: 'int32 C' (the language standard: it predicts "undefined", which is
scored as an abstention, never as a hit) and 'int32 x86-64' (the instruction set).

The AI-only baseline (asking a language model to predict the outcomes without
tools) was NOT run: no model API is available to this experiment's environment.
It is recorded as GIN-OPEN-013.
"""
import os
import shutil
import subprocess

from common import HERE, tool_version, write
from ginsdk import evaluate

SRC = os.path.join(HERE, "machine", "predict")
BUILD = os.path.join(HERE, "machine", "build", "predict")
os.makedirs(BUILD, exist_ok=True)
IMIN, IMAX = -2 ** 31, 2 ** 31 - 1
V = [0, 1, -1, 2, -2, 3, 7, -7, 46341, 65536, IMAX, IMIN, -3]
OPS = ["+", "-", "*", "/", "%"]
CASES = [(a, op, b) for a in V for op in OPS for b in V]


def oracle(cmd, stdin):
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=600)
    lines = p.stdout.strip().splitlines()
    if len(lines) != len(CASES):
        raise RuntimeError(f"{cmd[0]}: {len(lines)} lines for {len(CASES)} cases; stderr: {p.stderr[:300]}")
    return [l.split(" ", 1) for l in lines]


def build():
    exes = {}
    if shutil.which("gcc"):
        subprocess.run(["gcc", "-O0", "-o", os.path.join(BUILD, "eval_c"), os.path.join(SRC, "eval.c")], check=True)
        exes["C (gcc -O0, x86-64)"] = [os.path.join(BUILD, "eval_c")]
    if shutil.which("javac"):
        subprocess.run(["javac", "-d", BUILD, os.path.join(SRC, "Eval.java")], check=True, capture_output=True)
        exes["Java"] = ["java", "-cp", BUILD, "Eval"]
    if shutil.which("go"):
        subprocess.run(["go", "build", "-o", os.path.join(BUILD, "eval_go"), os.path.join(SRC, "eval.go")], check=True,
                       env={**os.environ, "GOCACHE": os.path.join(BUILD, "gocache"), "GO111MODULE": "off"})
        exes["Go"] = [os.path.join(BUILD, "eval_go")]
    if shutil.which("rustc"):
        subprocess.run(["rustc", "-C", "debug-assertions=on", "-C", "overflow-checks=on", "-o", os.path.join(BUILD, "eval_rs"),
                        os.path.join(SRC, "eval.rs")], check=True, capture_output=True)
        exes["Rust (debug)"] = [os.path.join(BUILD, "eval_rs")]
    if shutil.which("node"):
        exes["JavaScript BigInt"] = ["node", os.path.join(SRC, "eval.mjs"), "bigint"]
        exes["JavaScript Number"] = ["node", os.path.join(SRC, "eval.mjs"), "number"]
    exes["Python"] = ["python3", os.path.join(SRC, "eval.py")]
    return exes


DOMAINS = {"C (gcc -O0, x86-64)": ["int32 C", "int32 x86-64"], "Java": ["int32 Java"], "Go": ["int32 Go"], "Rust (debug)": ["int32 Rust (debug)"],
           "JavaScript BigInt": ["JS BigInt"], "JavaScript Number": ["JS Number"], "Python": ["Python"]}


def num(s):
    s = s.strip()
    if s in ("Infinity", "inf"):
        return float("inf")
    if s in ("-Infinity", "-inf"):
        return float("-inf")
    if s in ("NaN", "nan"):
        return "nan"
    try:
        return int(s)
    except ValueError:
        return float(s)


def same(x, y):
    if x == "nan" or y == "nan":
        return x == y
    return x == y or (isinstance(x, float) or isinstance(y, float)) and float(x) == float(y)


def predict_model(dom, a, op, b):
    # operands are run-time values, not literals: pass them as variables (a literal -2147483648 is
    # unary minus applied to 2147483648, which the typing layer rightly rejects: GIN-NEG-011)
    o = evaluate(f"a {op} b", dom, {"a": a, "b": b})
    if o.status in ("value", "special"):
        return "value", num(o.display)
    if o.status in ("exception", "trap"):
        return "refuse", None
    if o.status == "undefined":
        return "abstain", None
    return "not-modelled", o.status


def predict_naive_py(a, op, b):
    if op in "/%" and b == 0:
        return "refuse", None
    return "value", {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else None, "%": a % b if b else None}[op]


def predict_naive_c(a, op, b):
    if op in "/%" and b == 0:
        return "refuse", None
    if op in "/%":
        q = abs(a) // abs(b) * (-1 if (a < 0) != (b < 0) else 1)
        return "value", q if op == "/" else a - b * q
    return "value", {"+": a + b, "-": a - b, "*": a * b}[op]


def score(pred, truth):
    kind, val = pred
    tk, tv = truth
    if kind == "abstain":
        return "abstain"
    if kind == "not-modelled":
        return "not-modelled"
    if tk == "value":
        return "hit" if kind == "value" and same(val, num(tv)) else "miss"
    return "hit" if kind == "refuse" else "miss"


def main():
    exes = build()
    stdin = "\n".join(f"{a} {op} {b}" for a, op, b in CASES) + "\n"
    data = {"versions": {"gcc": tool_version(["gcc", "--version"]), "java": tool_version(["java", "-version"]), "go": tool_version(["go", "version"]),
                         "rustc": tool_version(["rustc", "--version"]), "node": tool_version(["node", "--version"]), "python": tool_version(["python3", "--version"])},
            "cases": len(CASES), "operands": V, "operators": OPS, "languages": {}}
    for lang, cmd in exes.items():
        truth = [("value" if k == "value" else "refuse", v) for k, v in oracle(cmd, stdin)]
        res = {"truth_refusals": sum(t[0] == "refuse" for t in truth)}
        for name, fn in [("naive-py", lambda a, op, b: predict_naive_py(a, op, b)), ("naive-c", lambda a, op, b: predict_naive_c(a, op, b))] + \
                        [(f"model[{d}]", (lambda d: lambda a, op, b: predict_model(d, a, op, b))(d)) for d in DOMAINS[lang]]:
            tally = {"hit": 0, "miss": 0, "abstain": 0, "not-modelled": 0}
            misses = []
            for (a, op, b), t in zip(CASES, truth):
                s = score(fn(a, op, b), t)
                tally[s] += 1
                if s == "miss" and len(misses) < 6:
                    misses.append(f"{a} {op} {b}: truth {t[0]} {t[1] or ''}".strip())
            covered = tally["hit"] + tally["miss"]
            tally["accuracy_on_covered"] = round(tally["hit"] / covered, 4) if covered else None
            tally["example_misses"] = misses
            res[name] = tally
        data["languages"][lang] = res
    write("GIN-EXP-013", ["GIN-H-040"], None, data)
    for lang, r in data["languages"].items():
        print(f"{lang:22s}", "  ".join(f"{k}: {v['hit']}/{v['hit'] + v['miss']}" + (f" (+{v['abstain']} abstain)" if v['abstain'] else "") + (f" (+{v['not-modelled']} n/m)" if v['not-modelled'] else "")
                                       for k, v in r.items() if isinstance(v, dict)))


if __name__ == "__main__":
    main()
