"""Spatial numeral grammars: layouts, read-order maps and interpretations (NUM-EXP-003).

A *layout* is a finite set of marks placed in the plane: (glyph, x, y, size,
orientation).  A notation's semantics is factored into two maps (NUM-DEF-030):

    layout --ρ (read-order / parse)--> structured word --⟦·⟧--> value

ρ decides which spatial relations matter (left/right order, baseline vs raised,
vertical stacking, rod orientation) and ⟦·⟧ gives them meaning.  The question of
NUM-HYP-003 is whether two spatial axes can carry *independent* information,
i.e. whether the interpretation depends non-trivially on both the horizontal and
the vertical relation.  Nothing here assumes any particular script is special;
the comparators are chosen from several traditions (see FOUNDATIONS.md §6 for
sources and their verification status).
"""
from __future__ import annotations

import itertools
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Mark:
    glyph: str
    x: float
    y: float = 0.0
    size: float = 1.0
    orient: str = ""        # e.g. "v" / "h" for rod numerals


# -- a minimal 2-D arithmetic grammar ----------------------------------------------------
def read_baseline(marks) -> list:
    """ρ for a tiny grammar: sort by x; a mark is 'raised' if y > 0 and smaller
    than its left neighbour, 'lowered' if y < 0 and smaller."""
    ms = sorted(marks, key=lambda m: m.x)
    out = []
    for m in ms:
        rel = "base"
        if out and m.size < 1:
            rel = "sup" if m.y > 0 else "sub" if m.y < 0 else "base"
        out.append((m.glyph, rel))
    return out


def interpret(word) -> int | None:
    """⟦·⟧: baseline digit runs are decimal numerals; a raised run is an exponent
    of the preceding baseline run; a lowered run is the base in which the
    preceding baseline run is read (positional, digits must be < base)."""
    runs = []
    for g, rel in word:
        if runs and runs[-1][1] == rel:
            runs[-1][0].append(int(g))
        else:
            runs.append(([int(g)], rel))
    if not runs or runs[0][1] != "base":
        return None
    val, i = None, 0
    while i < len(runs):
        digits, rel = runs[i]
        if rel != "base":
            return None
        nxt = runs[i + 1] if i + 1 < len(runs) else None
        if nxt and nxt[1] == "sub":
            b = int("".join(map(str, nxt[0])))
            if b < 2 or any(d >= b for d in digits):
                return None
            v = 0
            for d in digits:
                v = v * b + d
            i += 2
        else:
            v = int("".join(map(str, digits)))
            i += 1
        if i < len(runs) and runs[i][1] == "sup":
            v = v ** int("".join(map(str, runs[i][0])))
            i += 1
        if val is not None:          # two baseline runs side by side: not in this grammar
            return None
        val = v
    return val


def two_glyph_layouts(a: str, b: str):
    """All layouts of two glyphs with x-order in {ab, ba} and vertical relation of
    the right glyph in {base, sup, sub}: the horizontal and vertical channels."""
    for order in ((a, b), (b, a)):
        for rel, y, s in (("base", 0, 1), ("sup", 0.5, 0.6), ("sub", -0.4, 0.6)):
            yield order, rel, [Mark(order[0], 0), Mark(order[1], 1, y, s)]


def channel_independence(a: str, b: str) -> dict:
    """Value table over (x-order, vertical relation), and whether each channel,
    holding the other fixed, changes the value."""
    table = {}
    for order, rel, ms in two_glyph_layouts(a, b):
        table[("".join(order), rel)] = interpret(read_baseline(ms))
    orders = sorted({k[0] for k in table})
    rels = ["base", "sup", "sub"]
    x_matters = len(orders) > 1 and any(table[(orders[0], r)] != table[(orders[1], r)] for r in rels)
    y_matters = any(len({table[(o, r)] for r in rels}) > 1 for o in orders)
    defined = {k: v for k, v in table.items() if v is not None}
    return {"table": {f"{o}/{r}": table[(o, r)] for o, r in table}, "x_changes_value": x_matters,
            "y_changes_value": y_matters, "distinct_values": len(set(defined.values())),
            "distinct_values_x_only": len({table[(o, 'base')] for o in orders}),
            "distinct_values_y_only": len({table[(orders[0], r)] for r in rels} - {None})}


# -- Maya-style vertical place value -----------------------------------------------------
def maya_digit(d: int) -> str:
    """A within-place digit 0..19 as bars (5) and dots (1); 0 as a shell mark."""
    if d == 0:
        return "shell"
    bars, dots = divmod(d, 5)
    return "|" * bars + "." * dots


def maya_layout(n: int, calendrical: bool = False) -> list:
    """Places stacked bottom (units) to top.  Pure vigesimal weights 20^k; the
    calendrical (Long Count) variant uses weights 1, 20, 360, 7200, ... ."""
    weights = maya_weights(calendrical, 8)
    digits = []
    for k in reversed(range(len(weights))):
        if weights[k] <= n or digits:
            q, n = divmod(n, weights[k])
            digits.append((k, q))
    if not digits:
        digits = [(0, 0)]
    return [Mark(maya_digit(q), 0, k) for k, q in digits]


def maya_weights(calendrical: bool, places: int) -> list:
    w = [1, 20]
    while len(w) < places:
        w.append(w[-1] * (18 if calendrical and len(w) == 2 else 20))
    return w[:places]


def maya_value(marks, calendrical: bool = False) -> int:
    weights = maya_weights(calendrical, 1 + max(int(m.y) for m in marks))
    v = 0
    for m in marks:
        d = 0 if m.glyph == "shell" else 5 * m.glyph.count("|") + m.glyph.count(".")
        v += d * weights[int(m.y)]
    return v


# -- rod-numeral orientation as place-parity information -----------------------------------
def rod_render(n: int, alternate: bool, zero_mark: bool) -> tuple:
    """Decimal digits with an orientation per place: with ``alternate`` the units,
    hundreds, ... are 'v' and the tens, thousands, ... 'h' (the alternation
    described for counting-rod numerals); without it every place is 'v'.  Without
    ``zero_mark`` a zero place leaves no mark at all (a gap that is not written)."""
    s = str(n)
    out = []
    for i, ch in enumerate(s):
        place = len(s) - 1 - i
        if ch == "0" and not zero_mark:
            continue
        o = ("v" if place % 2 == 0 else "h") if alternate else "v"
        out.append((ch, o))
    return tuple(out)


def rod_ambiguity(limit: int, alternate: bool, zero_mark: bool) -> dict:
    fibers = {}
    for n in range(1, limit):
        fibers.setdefault(rod_render(n, alternate, zero_mark), []).append(n)
    amb = [v for v in fibers.values() if len(v) > 1]
    return {"renders": len(fibers), "numbers": limit - 1, "ambiguous_renders": len(amb),
            "numbers_in_ambiguous_renders": sum(len(v) for v in amb),
            "max_fiber": max(len(v) for v in fibers.values()),
            "example": next((v[:4] for v in amb), None)}


# -- logical order vs display order: a restricted bidi model --------------------------------
def bidi_class(ch: str) -> str:
    return unicodedata.bidirectional(ch)


def display_order(text: str, paragraph_rtl: bool = True) -> str:
    """Visual left-to-right order of ``text`` under a *restricted* subset of the
    Unicode Bidirectional Algorithm (UAX #9): input limited to classes L, R, AL,
    EN, AN, WS; rules W2, W3, W7 (simplified), N1/N2 for whitespace, I1/I2, L2.
    This is an executable model for the case study, not a conformant UBA; it is
    checked only on hand-derived cases (tests/test_layout.py)."""
    types = [bidi_class(c) for c in text]
    if any(t not in ("L", "R", "AL", "EN", "AN", "WS") for t in types):
        raise ValueError("restricted model: unsupported bidi class in input")
    base = 1 if paragraph_rtl else 0
    # W2: EN after AL (looking back past non-strong) becomes AN; W3: AL -> R
    last = "R" if paragraph_rtl else "L"
    for i, t in enumerate(types):
        if t in ("L", "R", "AL"):
            last = t
        elif t == "EN" and last == "AL":
            types[i] = "AN"
    types = ["R" if t == "AL" else t for t in types]
    # W7: EN after L (or in an LTR paragraph with no strong before) becomes L
    last = "L" if not paragraph_rtl else "R"
    for i, t in enumerate(types):
        if t in ("L", "R"):
            last = t
        elif t == "EN" and last == "L":
            types[i] = "L"
    # N1/N2: runs of WS take the direction of their neighbours if equal (EN/AN count as R), else base
    def strong(t):
        return "R" if t in ("R", "EN", "AN") else "L" if t == "L" else None
    i = 0
    while i < len(types):
        if types[i] == "WS":
            j = i
            while j < len(types) and types[j] == "WS":
                j += 1
            left = strong(types[i - 1]) if i > 0 else ("R" if base else "L")
            right = strong(types[j]) if j < len(types) else ("R" if base else "L")
            d = left if left == right else ("R" if base else "L")
            for k in range(i, j):
                types[k] = d
            i = j
        else:
            i += 1
    # I1/I2: embedding levels
    lv = []
    for t in types:
        if base == 0:
            lv.append(0 if t == "L" else 1 if t == "R" else 2)
        else:
            lv.append(2 if t in ("L", "EN", "AN") else 1)
    # L2: from the highest level down to the lowest odd level, reverse runs at that level or higher
    chars = list(text)
    top = max(lv) if lv else 0
    low_odd = min(l for l in lv if l % 2) if any(l % 2 for l in lv) else top + 1
    for level in range(top, low_odd - 1, -1):
        i = 0
        while i < len(chars):
            if lv[i] >= level:
                j = i
                while j < len(chars) and lv[j] >= level:
                    j += 1
                chars[i:j] = chars[i:j][::-1]
                lv[i:j] = lv[i:j][::-1]
                i = j
            else:
                i += 1
    return "".join(chars)


def digit_value(ch: str) -> int | None:
    try:
        return unicodedata.decimal(ch)
    except (TypeError, ValueError):
        return None


def reversal_preserves_value(b: int, length: int) -> dict:
    """For fixed-length base-b words (leading zeros allowed), count words with
    val(reverse w) == val(w) and compare with the number of palindromes."""
    same = pal = 0
    for w in itertools.product(range(b), repeat=length):
        v = r = 0
        for d in w:
            v = v * b + d
        for d in reversed(w):
            r = r * b + d
        same += v == r
        pal += w == w[::-1]
    return {"base": b, "length": length, "words": b ** length, "value_preserved": same, "palindromes": pal}
