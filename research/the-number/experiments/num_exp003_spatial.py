"""NUM-EXP-003 — spatial and topological numeral grammars.

Hypothesis under test (NUM-HYP-003): a notation can carry information in two
spatial channels independently — the interpretation depends non-trivially on a
horizontal relation and on a vertical (or orientation) relation, each with the
other held fixed.  The claim is about notations in general; nothing here asserts
that any one script is uniquely able to do this, and comparators from several
traditions are included precisely to test that.

(A) a minimal 2-D arithmetic grammar (baseline / raised / lowered marks);
(B) reversal of read order versus value (palindrome proposition);
(C) case study: Arabic-Indic digits — code points, bidi classes, parsers in
    several substrates, logical vs display order inside right-to-left text, with
    Hebrew and Latin comparators;
(D) Maya-style vertical place value: vertical axis = place, horizontal marks =
    within-place cumulative count; one layout under two semantics;
(E) counting-rod-style orientation alternation as place-parity information.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LANE))
sys.path[:0] = [LANE, os.path.join(ROOT, "sdk", "src")]

from numlab import layout as L          # noqa: E402
from ginsdk import evaluate              # noqa: E402

DIGIT_SETS = {
    "ASCII (European)": "0123456789",
    "Arabic-Indic (U+0660)": "".join(chr(0x660 + i) for i in range(10)),
    "Extended Arabic-Indic (U+06F0)": "".join(chr(0x6F0 + i) for i in range(10)),
    "Devanagari (U+0966)": "".join(chr(0x966 + i) for i in range(10)),
    "Fullwidth (U+FF10)": "".join(chr(0xFF10 + i) for i in range(10)),
}


def part_a():
    pairs = [("2", "3"), ("1", "2"), ("2", "5"), ("1", "1")]
    rows = {"".join(p): L.channel_independence(*p) for p in pairs}
    return {"pairs": rows, "all pairs: both channels change value": all(r["x_changes_value"] and r["y_changes_value"] for k, r in rows.items() if k != "11"),
            "note": "for '11' the horizontal channel cannot change the value (swapping equal glyphs is the identity): a degenerate case, recorded"}


def part_b():
    out = [L.reversal_preserves_value(b, n) for b in (2, 3, 10) for n in range(1, 7) if b ** n <= 10 ** 6]
    return {"rows": out, "value_preserved == palindromes in every row": all(r["value_preserved"] == r["palindromes"] for r in out)}


JS_PARSE = r"""
const sets = JSON.parse(process.argv[1]); const r = {};
for (const [k, s] of Object.entries(sets)) { const w = s[3] + s[4]; r[k] = { Number: String(Number(w)), parseInt: String(parseInt(w, 10)) }; }
console.log(JSON.stringify(r));
"""


def part_c():
    digits = {}
    for name, s in DIGIT_SETS.items():
        digits[name] = {"code points": f"U+{ord(s[0]):04X}..U+{ord(s[9]):04X}", "bidi class": sorted({unicodedata.bidirectional(c) for c in s}),
                        "general category": sorted({unicodedata.category(c) for c in s}),
                        "decimal values 0..9": [unicodedata.decimal(c) for c in s] == list(range(10))}
    # same value, different glyphs: the numeral 34 in each set
    con = sqlite3.connect(":memory:")
    parsers = {}
    for name, s in DIGIT_SETS.items():
        w = s[3] + s[4]
        row = {"word": w}
        try:
            row["Python int()"] = int(w)
        except ValueError:
            row["Python int()"] = "ValueError"
        row["SQLite CAST AS INTEGER"] = con.execute("select cast(? as integer)", (w,)).fetchone()[0]
        o = evaluate(w, "Z")
        row["ginsdk evaluate in Z"] = o.status + (f" {o.display}" if o.status == "value" else "")
        parsers[name] = row
    mixed = DIGIT_SETS["Arabic-Indic (U+0660)"][3] + DIGIT_SETS["Extended Arabic-Indic (U+06F0)"][4]
    try:
        mixed_py = int(mixed)
    except ValueError:
        mixed_py = "ValueError"
    node = shutil.which("node")
    if node:
        js = json.loads(subprocess.run([node, "-e", JS_PARSE, json.dumps(DIGIT_SETS)], capture_output=True, text=True, timeout=30).stdout)
        for k, v in js.items():
            parsers[k]["JS Number()"] = v["Number"]
            parsers[k]["JS parseInt()"] = v["parseInt"]
    else:
        for k in parsers:
            parsers[k]["JS Number()"] = "NOT RUN (node not found)"
    # logical vs display order (restricted UBA model)
    ar, he = "عدد", "מספר"
    cases = {
        "Arabic text + Arabic-Indic 34": ar + " " + DIGIT_SETS["Arabic-Indic (U+0660)"][3:5],
        "Arabic text + Extended Arabic-Indic 34": ar + " " + DIGIT_SETS["Extended Arabic-Indic (U+06F0)"][3:5],
        "Arabic text + European 34": ar + " 34",
        "Hebrew text + European 34": he + " 34",
        "Latin text + European 34 (LTR paragraph)": "num 34",
        "Arabic text, two numbers 12 34": ar + " 12 " + ar + " 34",
        "Hebrew text, two numbers 12 34": he + " 12 " + he + " 34",
    }
    display = {}
    for k, t in cases.items():
        rtl = not k.startswith("Latin")
        d = L.display_order(t, rtl)
        logical_digits = "".join(c for c in t if unicodedata.category(c) == "Nd")
        visual_digits = "".join(c for c in d if unicodedata.category(c) == "Nd")
        letters_logical = "".join(c for c in t if unicodedata.category(c).startswith("L"))
        letters_visual = "".join(c for c in d if unicodedata.category(c).startswith("L"))
        runs_vis = [r for r in "".join(c if unicodedata.category(c) == "Nd" else " " for c in d).split()]
        runs_log = [r for r in "".join(c if unicodedata.category(c) == "Nd" else " " for c in t).split()]
        display[k] = {"logical": t, "display (left to right)": d,
                      "each digit run keeps its logical order left-to-right": sorted(runs_vis) == sorted(runs_log),
                      "letters reversed in display": letters_visual == letters_logical[::-1] if rtl else letters_visual == letters_logical,
                      "order of the numbers in display": runs_vis}
    return {"unicode_version": unicodedata.unidata_version, "digit_sets": digits, "parse_34": parsers,
            "mixed Arabic-Indic 3 + Extended 4, Python int()": mixed_py, "display_order": display,
            "model": "restricted UBA subset (numlab.layout.display_order); not a conformant implementation"}


def part_d():
    diff = 0
    for n in range(0, 20 ** 3):
        lay = L.maya_layout(n)
        assert L.maya_value(lay) == n
        diff += L.maya_value(lay, calendrical=True) != n
    cal_ok = all(L.maya_value(L.maya_layout(n, True), True) == n for n in range(0, 18 * 20 * 20))
    # independence of channels: changing a place (vertical) vs changing marks within a place (horizontal)
    base = L.maya_layout(421)                       # 1·400 + 1·20 + 1
    moved = [L.Mark(m.glyph, m.x, m.y) for m in base]
    moved[0] = L.Mark(base[0].glyph + ".", 0, base[0].y)   # one more dot in the top place
    return {"pure vigesimal round trip n < 8000": True, "calendrical round trip n < 7200": cal_ok,
            "layouts (pure, n < 8000) whose calendrical reading differs": diff,
            "example 1000": {"layout (top to bottom)": [m.glyph for m in L.maya_layout(1000)],
                             "pure vigesimal": L.maya_value(L.maya_layout(1000)), "calendrical": L.maya_value(L.maya_layout(1000), True)},
            "channel test 421": {"value": L.maya_value(base), "add one dot in the top place": L.maya_value(moved)},
            "source status": "structure as described in Chrisomalis 2010 (secondary); place weights of the calendrical variant are stated there and in standard accounts, page references not verified here"}


def part_e():
    lim = 10000
    return {"limit": lim,
            "no zero mark, one orientation": L.rod_ambiguity(lim, False, False),
            "no zero mark, alternating orientation": L.rod_ambiguity(lim, True, False),
            "zero mark, one orientation": L.rod_ambiguity(lim, False, True),
            "source status": "alternation of orientation by place as described for counting-rod numerals in Chrisomalis 2010 (secondary); the model idealizes a gap as invisible"}


def main():
    res = {"experiment": "NUM-EXP-003", "A_two_channel_grammar": part_a(), "B_reversal": part_b(), "C_arabic_indic_case": part_c(),
           "D_maya_vertical": part_d(), "E_rod_orientation": part_e()}
    os.makedirs(os.path.join(LANE, "results"), exist_ok=True)
    with open(os.path.join(LANE, "results", "num_exp003.json"), "w", encoding="utf8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, sort_keys=True)
    print("NUM-EXP-003")
    print(" A:", json.dumps(res["A_two_channel_grammar"]["pairs"]["23"], ensure_ascii=False))
    print(" B:", res["B_reversal"]["value_preserved == palindromes in every row"])
    for k, v in res["C_arabic_indic_case"]["parse_34"].items():
        print(" C parse:", k, json.dumps(v, ensure_ascii=False))
    for k, v in res["C_arabic_indic_case"]["display_order"].items():
        print(" C display:", k, "|", v["display (left to right)"], "| runs kept:", v["each digit run keeps its logical order left-to-right"], "| order:", v["order of the numbers in display"])
    print(" C digit bidi:", {k: v["bidi class"] for k, v in res["C_arabic_indic_case"]["digit_sets"].items()})
    print(" D:", json.dumps({k: v for k, v in res["D_maya_vertical"].items() if k != "source status"}, ensure_ascii=False))
    print(" E:", json.dumps({k: v for k, v in res["E_rod_orientation"].items() if k != "source status"}))


if __name__ == "__main__":
    main()
