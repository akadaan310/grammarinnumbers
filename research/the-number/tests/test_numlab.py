"""Tests for the research-lane library numlab (run: python3 -m unittest discover -s tests)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numlab import fibers as F, layout as L, systems as S  # noqa: E402


class TestSystems(unittest.TestCase):
    def test_round_trips(self):
        for k, mk in S.SYSTEMS.items():
            s = mk()
            rng = range(1, 600) if k.startswith("roman") else range(-130, 128) if k in (
                "balanced-ternary", "negabinary", "negadecimal", "sign-magnitude2", "twos8") else range(0, 600)
            for n in rng:
                w = s.encode(n)
                if w is not None:
                    self.assertTrue(s.admissible(w), (k, n, w))
                    self.assertEqual(s.value(w), n, (k, n, w))

    def test_uniqueness_depends_on_language(self):
        self.assertTrue(S.fiber_census(S.fibonacci(True), 10)["unique"])
        c = S.fiber_census(S.fibonacci(False), 3)
        self.assertFalse(c["unique"])             # 100 and 011 both denote 3
        self.assertEqual(S.fibonacci(False).value((1, 0, 0)), 3)
        self.assertEqual(S.fibonacci(False).value((1, 1)), 3)
        self.assertFalse(S.fiber_census(S.standard(10, True), 2)["unique"])
        self.assertEqual(S.fiber_census(S.sign_magnitude(2), 3)["example_collision"]["words"], ["+", "-"])

    def test_known_words(self):
        self.assertEqual(S.show(S.balanced_ternary().encode(5)), "1TT")
        self.assertEqual(S.show(S.negabase(2).encode(-3)), "1101")
        self.assertEqual(S.show(S.bijective(10).encode(10)), "A")
        # 463 = 3·5! + 4·4! + 1·3! + 0·2! + 1·1! (the always-zero 0! place is omitted)
        self.assertEqual(S.show(S.factoradic().encode(463)), "34101")
        self.assertEqual(S.show(S.roman(True).encode(1994)), "MCMXCIV")
        self.assertIsNone(S.roman(True).encode(0))


class TestFibers(unittest.TestCase):
    def test_counts_match_linear_congruence(self):
        from math import gcd
        for n in range(1, 13):
            A = F.zmod(n)
            for a in range(n):
                for b in range(n):
                    g = gcd(b, n)
                    self.assertEqual(len(A.sol("*", a, b)), g if a % g == 0 else 0)

    def test_homomorphism_preservation(self):
        m = F.Map("Z/12->Z/4", F.zmod(12), F.zmod(4), lambda x: x % 4, ("*",), False, True)
        self.assertTrue(F.is_hom(m, "*"))
        self.assertEqual(F.predicted_violations(m, F.transfer(m, "*")["matrix"]), [])

    def test_gf4_is_a_field(self):
        G = F.gf4()
        for a in G.elems:
            for b in G.elems[1:]:
                self.assertEqual(len(G.sol("*", a, b)), 1)


class TestLayout(unittest.TestCase):
    def test_two_channels(self):
        r = L.channel_independence("2", "3")
        self.assertEqual(r["table"]["23/sup"], 8)
        self.assertEqual(r["table"]["23/sub"], 2)
        self.assertTrue(r["x_changes_value"] and r["y_changes_value"])

    def test_display_order_hand_cases(self):
        # hand-derived from UAX #9 rules for these inputs
        self.assertEqual(L.display_order("abc 34 def", False), "abc 34 def")
        self.assertEqual(L.display_order("אב 34"), "34 בא")
        self.assertEqual(L.display_order("عد ٣٤"), "٣٤ دع")
        self.assertEqual(L.display_order("א 12 ב 34"), "34 ב 12 א")
        self.assertEqual(L.display_order("ab אב cd", False), "ab בא cd")

    def test_reversal_proposition(self):
        for b in (2, 3, 10):
            for n in range(1, 5):
                r = L.reversal_preserves_value(b, n)
                self.assertEqual(r["value_preserved"], r["palindromes"])

    def test_maya(self):
        for n in range(0, 8000, 7):
            self.assertEqual(L.maya_value(L.maya_layout(n)), n)
        self.assertEqual(L.maya_value(L.maya_layout(1000), True), 920)


if __name__ == "__main__":
    unittest.main()
