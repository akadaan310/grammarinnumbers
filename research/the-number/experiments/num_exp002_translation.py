"""NUM-EXP-002 — representation translation and invariants.

(A) Fiber census: for each numeration system and every admissible word up to a
    length bound, how many words denote each value?  Uniqueness is a property of
    the language L, so it is measured, with lax and strict languages side by side.
(B) Translation obligations O1–O5 (FOUNDATIONS.md §3) for translations between
    systems, including ones expected to fail (Roman has no zero, 8-bit wrapping
    arithmetic does not commute with sign extension, reversal does not commute
    with base change).
(C) Conversion cost in counted 32-bit word operations (ginsdk.bigint): decimal
    to binary by Horner's rule and by divide and conquer, and hexadecimal to
    binary by regrouping.  These are classical complexity facts reproduced as
    counts, not new results.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LANE))
sys.path[:0] = [LANE, os.path.join(ROOT, "sdk", "src")]

from numlab import systems as S                      # noqa: E402
from numlab.schema import Substrate, check_translation  # noqa: E402
from ginsdk import bigint as B                       # noqa: E402
from ginsdk.cost import Cost                         # noqa: E402

CENSUS = {  # system -> max word length (chosen so each census enumerates ≤ ~10^5 words)
    "base2": 12, "base3": 8, "base10": 4, "base10-leading-zeros": 4, "base16": 3, "bijective2": 12, "bijective10": 4,
    "balanced-ternary": 8, "negabinary": 12, "negadecimal": 4, "sign-magnitude2": 9, "twos8": 8,
    "factoradic": 6, "zeckendorf": 14, "fibonacci-lax": 14, "roman-strict": 7, "roman-lax": 5,
}


def census():
    out = {}
    for k, L in CENSUS.items():
        sys_ = S.SYSTEMS[k]()
        alpha = sys_.alphabet[:7] if k == "factoradic" else None
        c = S.fiber_census(sys_, L, alpha)
        out[k] = {"max_len": L, **c}
    return out


def _wrap(w):
    return lambda x, y, f: ((f(x, y) + (1 << (w - 1))) % (1 << w)) - (1 << (w - 1))


def translations():
    rev = (lambda w: tuple(reversed(w)), lambda w: tuple(reversed(w)))
    exact = {"+": lambda x, y: x + y, "*": lambda x, y: x * y}
    zdiv = {"*": lambda a, b: [a // b] if b and a % b == 0 else (["all"] * 2 if b == 0 and a == 0 else [])}
    res = {}
    b10, b2, bij10 = S.standard(10), S.standard(2), S.bijective(10)
    N10 = Substrate("decimal", "N", b10, exact, zdiv)
    N2 = Substrate("binary", "N", b2, exact, zdiv)
    to = lambda dst: (lambda w: dst.encode(S.horner(w, 10)))
    res["decimal -> binary"] = check_translation(N10, N2, to(b2), lambda v: v, range(0, 64), {"reversal": rev})
    res["decimal -> bijective decimal"] = check_translation(N10, Substrate("bij10", "N", bij10, exact, zdiv), to(bij10), lambda v: v,
                                                            range(0, 120), {"reversal": rev})
    rs = S.roman(True)
    res["decimal -> Roman (strict)"] = check_translation(N10, Substrate("roman", "N≥1", rs), lambda w: rs.encode(S.horner(w, 10)),
                                                         lambda v: v, range(0, 4001))
    # sign extension 8 -> 16 bits, with each side's own wrapping arithmetic
    t8, t16 = S.twos_complement(8), S.twos_complement(16)
    w8, w16 = _wrap(8), _wrap(16)
    ops8 = {"+": lambda x, y: w8(x, y, lambda a, b: a + b), "*": lambda x, y: w8(x, y, lambda a, b: a * b)}
    ops16 = {"+": lambda x, y: w16(x, y, lambda a, b: a + b), "*": lambda x, y: w16(x, y, lambda a, b: a * b)}
    mulconv = lambda w: (lambda a, b: [c for c in range(-(1 << (w - 1)), 1 << (w - 1)) if ((b * c + (1 << (w - 1))) % (1 << w)) - (1 << (w - 1)) == a])
    sample8 = list(range(-128, 128, 5))
    res["int8 -> int16 (sign extension)"] = check_translation(
        Substrate("int8", "Z/2^8", t8, ops8, {"*": mulconv(8)}), Substrate("int16", "Z/2^16", t16, ops16, {"*": mulconv(16)}),
        lambda w: (w[0],) * 8 + w, lambda v: v, sample8)
    # the same obligation O3 exhaustively over all 256 x 256 pairs, using the classical count
    # |{c mod 2^w : b c ≡ a}| = gcd(b, 2^w) if gcd(b, 2^w) | a else 0 (checked by brute force on 8 bits)
    def cnt(a, b, w):
        g = math.gcd(b % (1 << w), 1 << w)
        return g if a % g == 0 else 0
    assert all(cnt(a, b, 8) == sum(1 for c in range(256) if (b * c - a) % 256 == 0) for a in range(256) for b in range(256))
    k = lambda n: min(n, 2)
    changed = sum(1 for a in range(-128, 128) for b in range(-128, 128) if k(cnt(a, b, 8)) != k(cnt(a, b, 16)))
    res["int8 -> int16 converse class of *, exhaustive"] = {"pairs": 65536, "class changes": changed}
    # reversal vs base change: fraction of n for which reverse-then-convert equals convert-then-reverse
    agree = sum(1 for n in range(1, 10000) if S.horner(tuple(reversed(b10.encode(n))), 10) == n)
    commute = 0
    for n in range(1, 10000):
        a = S.horner(tuple(reversed(b10.encode(n))), 10)
        b = S.horner(tuple(reversed(b2.encode(n))), 2)
        commute += a == b
    res["reversal in base 10 vs base 2, n < 10^4"] = {"decimal palindromes (reversal fixes value)": agree,
                                                      "n with rev10(n) == rev2(n)": commute}
    return res


def horner_cost(digits: str) -> int:
    c = Cost()
    x = []
    for ch in digits:
        x = B.add(B.mul_school(x, [10], c), B.from_int(int(ch)), c) if x else B.from_int(int(ch))
    return B.word_ops(c)


def dc_cost(digits: str) -> int:
    c = Cost()
    pw = {}

    def p10(k):
        if k not in pw:
            if k <= 9:
                pw[k] = B.from_int(10 ** k)
            else:
                h = k // 2
                pw[k] = B.mul_karatsuba(p10(h), p10(k - h), c)
        return pw[k]

    def conv(s):
        if len(s) <= 9:
            c.tick("mul", len(s))          # one small multiply-add per digit within a word
            return B.from_int(int(s))
        h = len(s) // 2
        hi, lo = conv(s[:-h]), conv(s[-h:])
        return B.add(B.mul_karatsuba(hi, p10(h), c), lo, c)
    v = conv(digits)
    assert B.to_int(v) == int(digits)
    return B.word_ops(c)


def hex_cost(digits: str) -> int:
    # regrouping: each hex digit is placed into its limb with one shift-or: one word op per digit
    limbs = [0] * ((len(digits) + 7) // 8)
    ops = 0
    for i, ch in enumerate(reversed(digits)):
        limbs[i // 8] |= int(ch, 16) << (4 * (i % 8))
        ops += 1
    assert sum(l << (32 * i) for i, l in enumerate(limbs)) == int(digits, 16)
    return ops


def costs():
    import random
    r = random.Random(20261017)
    rows = []
    for e in range(6, 13):
        n = 2 ** e
        dec = str(r.randint(1, 9)) + "".join(str(r.randint(0, 9)) for _ in range(n - 1))
        hx = "".join(r.choice("123456789abcdef") for _ in range(n))
        rows.append({"digits": n, "horner_decimal": horner_cost(dec), "divide_conquer_decimal": dc_cost(dec), "regroup_hex": hex_cost(hx)})
    fit = {}
    for k in ("horner_decimal", "divide_conquer_decimal", "regroup_hex"):
        a, b = rows[-3], rows[-1]
        fit[k] = round(math.log(b[k] / a[k]) / math.log(b["digits"] / a["digits"]), 3)
    return {"rows": rows, "log-log slope over the last 3 sizes": fit, "unit": "32-bit word operations (ginsdk.bigint add/mul/div/cmp)"}


def main():
    res = {"experiment": "NUM-EXP-002", "census": census(), "translations": translations(), "conversion_cost": costs()}
    os.makedirs(os.path.join(LANE, "results"), exist_ok=True)
    with open(os.path.join(LANE, "results", "num_exp002.json"), "w", encoding="utf8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, sort_keys=True)
    print("NUM-EXP-002 fiber census (unique? / fiber sizes / collision):")
    for k, v in res["census"].items():
        print(f"  {k:22s} len≤{v['max_len']:<2d} values={v['values']:<6d} unique={str(v['unique']):5s} sizes={v['fiber_sizes']} {v['example_collision'] or ''}")
    print("translations:")
    for k, v in res["translations"].items():
        print(" ", k, json.dumps(v, ensure_ascii=False))
    print("cost slopes:", res["conversion_cost"]["log-log slope over the last 3 sizes"])


if __name__ == "__main__":
    main()
