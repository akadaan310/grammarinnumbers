"""Numeration systems as substrates (NUM-DEF-002, NUM-DEF-010).

Each system is a small record: an alphabet, an admissibility predicate on words
(the language L), a partial semantics ``value`` from words to integers, and an
``encode`` that returns the canonical word of an integer (or None when the
integer has no word in this system).  Uniqueness of representation is *not*
assumed: it is measured by :func:`fiber_census`, because it is a property of the
chosen language L, not of the digit set alone (NUM-EXP-002).

Words are tuples of symbols, written most significant symbol first unless a
system says otherwise.  Only the Python standard library is used.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


@dataclass(frozen=True)
class System:
    name: str
    alphabet: tuple
    admissible: Callable[[tuple], bool]
    value: Callable[[tuple], Optional[int]]
    encode: Callable[[int], Optional[tuple]]
    note: str = ""

    def parse(self, word: tuple) -> Optional[int]:
        return self.value(word) if self.admissible(word) else None


# -- positional: x -> b*x + d applied to 0 -------------------------------------------
def horner(word: Iterable[int], b: int) -> int:
    x = 0
    for d in word:
        x = b * x + d
    return x


def standard(b: int, leading_zeros: bool = False) -> System:
    """Base b, digits 0..b-1.  Zero is the empty word; with ``leading_zeros``
    the language admits words such as (0, 7), and uniqueness fails."""
    def adm(w):
        return all(isinstance(d, int) and 0 <= d < b for d in w) and (leading_zeros or not w or w[0] != 0)

    def enc(n):
        if n < 0:
            return None
        w = []
        while n:
            n, d = divmod(n, b)
            w.append(d)
        return tuple(reversed(w))
    return System(f"base {b}" + (" (leading zeros)" if leading_zeros else ""), tuple(range(b)), adm,
                  lambda w: horner(w, b), enc)


def bijective(b: int) -> System:
    def enc(n):
        if n < 0:
            return None
        w = []
        while n:
            d = n % b or b
            n = (n - d) // b
            w.append(d)
        return tuple(reversed(w))
    return System(f"bijective base {b}", tuple(range(1, b + 1)), lambda w: all(1 <= d <= b for d in w),
                  lambda w: horner(w, b), enc)


def balanced_ternary() -> System:
    def enc(n):
        w = []
        while n:
            r = n % 3
            d = -1 if r == 2 else r
            n = (n - d) // 3
            w.append(d)
        return tuple(reversed(w))
    return System("balanced ternary", (-1, 0, 1), lambda w: all(d in (-1, 0, 1) for d in w) and (not w or w[0] != 0),
                  lambda w: horner(w, 3), enc)


def negabase(b: int) -> System:
    """Base −b with digits 0..b−1: every integer, no sign symbol."""
    def enc(n):
        w = []
        while n:
            n, d = divmod(n, -b)
            if d < 0:
                n, d = n + 1, d + b
            w.append(d)
        return tuple(reversed(w))
    return System(f"base -{b}", tuple(range(b)), lambda w: all(0 <= d < b for d in w) and (not w or w[0] != 0),
                  lambda w: horner(w, -b), enc)


def sign_magnitude(b: int = 2) -> System:
    """A sign symbol followed by a base-b magnitude (leading zeros forbidden,
    zero magnitude = empty).  Both '+' and '−' are admitted before the empty
    magnitude, so zero has two words."""
    base = standard(b)

    def adm(w):
        return len(w) >= 1 and w[0] in ("+", "-") and base.admissible(w[1:])

    def val(w):
        m = horner(w[1:], b)
        return -m if w[0] == "-" else m

    def enc(n):
        return ("-" if n < 0 else "+",) + base.encode(abs(n))
    return System(f"sign-magnitude base {b}", ("+", "-") + tuple(range(b)), adm, val, enc)


def twos_complement(width: int) -> System:
    def adm(w):
        return len(w) == width and all(d in (0, 1) for d in w)

    def val(w):
        u = horner(w, 2)
        return u - (1 << width) if w[0] == 1 else u

    def enc(n):
        if not -(1 << (width - 1)) <= n < (1 << (width - 1)):
            return None
        u = n % (1 << width)
        return tuple((u >> i) & 1 for i in reversed(range(width)))
    return System(f"two's complement, {width} bits", (0, 1), adm, val, enc)


# -- factoradic and Zeckendorf ---------------------------------------------------------
def factoradic() -> System:
    """Mixed radix: the digit at place k (from the right, k ≥ 1) is 0..k and weighs k!."""
    def adm(w):
        n = len(w)
        return all(0 <= d <= n - i for i, d in enumerate(w)) and (not w or w[0] != 0)

    def val(w):
        x = 0
        n = len(w)
        for i, d in enumerate(w):          # Horner on mixed radix: place n-i weighs (n-i)!
            x = x * (n - i + 1) + d
        return x

    def enc(n):
        if n < 0:
            return None
        w, k = [], 2
        while n:
            n, d = divmod(n, k)
            w.append(d)
            k += 1
        return tuple(reversed(w))
    return System("factoradic", tuple(range(10)), adm, val, enc)


def _fibs(limit):
    f = [1, 2]
    while f[-1] <= limit:
        f.append(f[-1] + f[-2])
    return f


def fibonacci(zeckendorf: bool = True) -> System:
    """Fibonacci base: the bit at place k (from the right, k ≥ 0) weighs F_{k+2} (1, 2, 3, 5, ...).
    With ``zeckendorf`` the language forbids two adjacent 1s; without it,
    uniqueness fails (e.g. 100 and 011 both denote 3)."""
    def adm(w):
        ok = all(d in (0, 1) for d in w) and (not w or w[0] == 1)
        if zeckendorf:
            ok = ok and all(not (a == 1 and c == 1) for a, c in zip(w, w[1:]))
        return ok

    def val(w):
        f = _fibs(2 ** (len(w) + 2))
        return sum(f[i] for i, d in enumerate(reversed(w)) if d)

    def enc(n):
        if n < 0:
            return None
        if n == 0:
            return ()
        f = [x for x in _fibs(n) if x <= n]
        w = []
        for x in reversed(f):
            if x <= n:
                w.append(1)
                n -= x
            else:
                w.append(0)
        return tuple(w)
    return System("Zeckendorf" if zeckendorf else "Fibonacci base (unconstrained)", (0, 1), adm, val, enc)


# -- Roman (additive-subtractive, not positional) -------------------------------------
_ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
_RV = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_value_lax(w: tuple) -> Optional[int]:
    """The common lax reading: a symbol smaller than its right neighbour is subtracted."""
    if not w or any(s not in _RV for s in w):
        return None
    v = [_RV[s] for s in w]
    return sum(-x if i + 1 < len(v) and x < v[i + 1] else x for i, x in enumerate(v))


def roman(strict: bool = True) -> System:
    """Strict: only the canonical modern form of 1..3999 is admissible.  Lax: any
    word over I V X L C D M, read by the subtractive rule (IIII, IC, VX all admitted)."""
    def enc(n):
        if not 1 <= n <= 3999:
            return None
        out = ""
        for v, s in _ROMAN:
            while n >= v:
                out += s
                n -= v
        return tuple(out)

    def adm(w):
        if strict:
            v = roman_value_lax(w)
            return v is not None and 1 <= v <= 3999 and enc(v) == tuple(w)
        return roman_value_lax(w) is not None
    return System("Roman (strict)" if strict else "Roman (lax)", tuple("IVXLCDM"), adm, roman_value_lax, enc)


SYSTEMS = {
    "base2": lambda: standard(2), "base3": lambda: standard(3), "base10": lambda: standard(10),
    "base16": lambda: standard(16), "base10-leading-zeros": lambda: standard(10, True),
    "bijective2": lambda: bijective(2), "bijective10": lambda: bijective(10),
    "balanced-ternary": balanced_ternary, "negabinary": lambda: negabase(2), "negadecimal": lambda: negabase(10),
    "sign-magnitude2": lambda: sign_magnitude(2), "twos8": lambda: twos_complement(8),
    "factoradic": factoradic, "zeckendorf": lambda: fibonacci(True), "fibonacci-lax": lambda: fibonacci(False),
    "roman-strict": lambda: roman(True), "roman-lax": lambda: roman(False),
}


def fiber_census(sys: System, max_len: int, alphabet: Optional[tuple] = None) -> dict:
    """Enumerate every admissible word of length ≤ max_len and count how many
    words denote each value.  Returns the distribution of fiber sizes."""
    alphabet = alphabet or sys.alphabet
    fibers: dict[int, list] = {}
    for n in range(0, max_len + 1):
        for w in itertools.product(alphabet, repeat=n):
            if sys.admissible(w):
                v = sys.value(w)
                if v is not None:
                    fibers.setdefault(v, []).append(w)
    sizes: dict[int, int] = {}
    for ws in fibers.values():
        sizes[len(ws)] = sizes.get(len(ws), 0) + 1
    worst = max(fibers.items(), key=lambda kv: (len(kv[1]), -abs(kv[0])))
    return {"values": len(fibers), "words": sum(len(v) for v in fibers.values()),
            "fiber_sizes": dict(sorted(sizes.items())), "unique": set(sizes) == {1},
            "example_collision": None if len(worst[1]) == 1 else {"value": worst[0], "words": ["".join(map(_sym, w)) or "ε" for w in worst[1][:4]]}}


def _sym(d) -> str:
    if isinstance(d, str):
        return d
    if d == -1:
        return "T"
    return "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[d]


def show(word: tuple) -> str:
    return "".join(map(_sym, word)) or "ε"
