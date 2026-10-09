"""Small-case checks of the "proved here" statements added in the first edition
(RESULTS.md §K).  Like check_theorems.py, these guard against mis-statement; they
are not proofs.  Each check names the ledger identifier it tests; the script exits
non-zero on any failure.
"""
import itertools
import math
import sys
from fractions import Fraction

from common import write
from ginsdk import circuits as K, converse as C, expr as X, ieee as I, machine as M, numbertheory as T, numerals as N, peano as P

results = {}


def check(ident, fn):
    try:
        results[ident] = {"ok": True, "detail": fn()}
    except AssertionError as e:
        results[ident] = {"ok": False, "detail": f"assertion failed: {e}"}


def prop050():
    for fmt in (I.BINARY16, I.MINI8):
        pats = [I.from_bits(fmt, b) for b in range(1 << fmt.width)]
        nans = sum(x.is_nan for x in pats)
        zeros = sum(x.is_zero for x in pats)
        assert nans == 2 ** (fmt.width - fmt.ebits) - 2, (fmt.name, nans)
        assert zeros == 2
    assert I.from_bits(I.BINARY32, 0xFFFFFFFF).is_nan and M.wrap(0xFFFFFFFF, 32) == -1
    assert I.from_bits(I.BINARY32, 0x40490FDB).value() == Fraction(13176795, 2 ** 22)
    return "binary16 and binary8 enumerated; binary32 patterns decoded"


def prop051():
    n = 0
    for a in range(-6, 7):
        for b in range(a + 1, 7):
            for c in range(b + 1, 7):
                s1, s2 = P.parse_segment(f"{a}{{{','.join(map(str, range(a + 1, b)))}}}{b}"), P.parse_segment(f"{b}{{{','.join(map(str, range(b + 1, c)))}}}{c}")
                glued = f"{a}{{{','.join(map(str, list(range(a + 1, b)) + [b] + list(range(b + 1, c))))}}}{c}"
                g = P.parse_segment(glued)
                assert s1.ok and s2.ok and g.ok, glued
                assert {a, b} ^ {b, c} == {a, c}
                n += 1
    return f"{n} glued pairs with endpoints in [-6, 6]"


def prop052():
    for w in range(1, 13):
        m = 2 ** w
        s = lambda x: (x + 1) % m
        assert len({s(x) for x in range(m)}) == m          # injective
        orbit, x = {0}, s(0)
        while x != 0:
            orbit.add(x)
            x = s(x)
        assert orbit == set(range(m))                      # induction: the closure of {0} is everything
        assert s(m - 1) == 0                               # 0 is a successor
    return "w = 1 .. 12"


def prop057():
    n = 0
    for b in range(2, 8):
        for x in range(b ** 3):
            for y in range(0, b ** 3, 3):
                A = [(x // b ** i) % b for i in range(3)]; B = [(y // b ** i) % b for i in range(3)]
                c, s = 0, []
                for i in range(3):
                    t = A[i] + B[i] + c
                    s.append(t % b); c = t // b
                    assert c in (0, 1)
                    assert sum(s[j] * b ** j for j in range(i + 1)) + c * b ** (i + 1) == sum((A[j] + B[j]) * b ** j for j in range(i + 1))
                assert sum(d * b ** j for j, d in enumerate(s + [c])) == x + y
                n += 1
    return f"{n} additions in bases 2..7"


def prop060():
    for K_ in range(1, 7):
        # completion relation: (a, b) ~ (c, d) iff a + d + k = b + c + k for some k (saturating sums)
        sat = lambda x, y: min(x + y, K_)
        pairs = [(a, b) for a in range(K_ + 1) for b in range(K_ + 1)]
        rel = lambda p, q: any(sat(sat(p[0], q[1]), k) == sat(sat(p[1], q[0]), k) for k in range(K_ + 1))
        # every element n, i.e. the pair (n, 0), is related to the zero pair (0, 0)
        assert all(rel((n, 0), (0, 0)) for n in range(K_ + 1))
    return "K = 1..6: every (n, 0) is identified with (0, 0)"


def prop061():
    n = 0
    for w in range(1, 9):
        M = 1 << w
        for a in range(M):
            for b in range(M):
                t = a + (M - 1 - b) + 1
                assert t % M == (a - b) % M and (t >> w) == (1 if a >= b else 0)
                n += 1
    return f"{n} pairs, widths 1..8"


def prop062():
    lo, hi = -128, 127
    sat = lambda x: max(lo, min(hi, x))
    R = range(lo, hi + 1)
    bad = sum(sat(sat(a + b) + c) != sat(a + sat(b + c)) for a in R for b in R for c in R)
    assert bad == 4177792, bad
    assert all(sat(a + b) == sat(b + a) for a in R for b in R)
    assert not any(sat(-128 + b) == 0 for b in R)
    assert sat(2 * sat(100 - 100)) == 0 and sat(sat(200) + sat(-200)) == -1
    return "2^24 triples: 4177792 non-associative"


def prop064():
    for n in range(1, 40):
        phi = lambda m: sum(math.gcd(k, m) == 1 for k in range(1, m + 1))
        solv = sum(1 for a in range(n) for b in range(n) if C.divide_mod(a, b, n).kind != C.NONE)
        uniq = sum(1 for a in range(n) for b in range(n) if C.divide_mod(a, b, n).kind == C.UNIQUE)
        assert solv == sum(d * phi(d) for d in range(1, n + 1) if n % d == 0), n
        assert uniq == n * phi(n), n
    return "n < 40"


CHECKS = [("GIN-PROP-064", prop064), ("GIN-PROP-062", prop062), ("GIN-PROP-060", prop060), ("GIN-PROP-061", prop061), ("GIN-PROP-057", prop057), ("GIN-PROP-050", prop050), ("GIN-PROP-051", prop051), ("GIN-PROP-052", prop052)]

if __name__ == "__main__":
    for ident, fn in CHECKS:
        check(ident, fn)
        print(f"{ident}: {'ok' if results[ident]['ok'] else 'FAIL'} — {results[ident]['detail']}")
    write("GIN-CHECKS-EDITION1", [], None, results)
    sys.exit(0 if all(r["ok"] for r in results.values()) else 1)
