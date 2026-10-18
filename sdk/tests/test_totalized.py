"""Tests for ginsdk.totalized: wheel axioms, and the trilemma for division by zero."""
import unittest

from ginsdk import totalized as T


class TestTotalized(unittest.TestCase):
    def test_wheel_axioms_hold(self):
        for name, (ok, tot) in T.check_wheel_axioms().items():
            self.assertEqual(ok, tot, name)

    def test_wheel_values(self):
        W = T.WheelZ()
        self.assertEqual(W.div(W.one, W.zero), (1, 0))       # 1/0 = ∞
        self.assertEqual(W.div(W.zero, W.zero), (0, 0))      # 0/0 = ⊥
        self.assertEqual(W.mul(W.zero, (1, 0)), (0, 0))      # 0·∞ = ⊥ ≠ 0

    def test_trilemma(self):
        for key in T.SYSTEMS:
            one, zero = T.one_over_zero(key)
            conv = next(r for r in T.law_census(key) if r["law"].startswith("y·(x / y)"))
            if one != "undefined" and zero != "undefined":
                self.assertGreater(conv["fail"], 0, key)      # total ⇒ the converse reading fails
            else:
                self.assertEqual(conv["fail"], 0, key)        # partial systems keep it where defined

    def test_meadow_keeps_ring_laws(self):
        rows = {r["law"]: r for r in T.law_census("meadow")}
        for law in ("x + y = y + x", "(x + y) + z = x + (y + z)", "x·(y + z) = x·y + x·z", "0·x = 0", "x − x = 0"):
            self.assertEqual(rows[law]["fail"], 0, law)
        self.assertEqual(rows["x / x = 1"]["fail"], 1)


if __name__ == "__main__":
    unittest.main()
