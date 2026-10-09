import unittest
from fractions import Fraction

from ginsdk import numerals as N


class TestNumerals(unittest.TestCase):
    def test_standard_addresses_roundtrip(self):
        for b in (2, 3, 7, 10, 16):
            g = N.standard(b)
            for n in range(0, 3000):
                w = g.address(n)
                self.assertEqual(g.denote(w), n)
                if n:
                    self.assertEqual(int(g.render(w), b), n)
            self.assertEqual(g.address(0), ())          # zero's address is the empty word

    def test_leading_zeros_are_exactly_the_non_injectivity(self):
        g = N.standard(2)
        for n in range(0, 40):
            words = g.words_denoting(n, 8)
            canon = g.address(n)
            self.assertTrue(all(w == (0,) * (len(w) - len(canon)) + canon for w in words))
            self.assertEqual(len(words), 8 - len(canon) + 1)

    def test_bijective_is_a_bijection(self):
        for b in (1, 2, 3, 10):
            g = N.bijective(b)
            maxlen = 12 if b == 1 else 7 if b == 2 else 5 if b == 3 else 3
            seen = {}
            layer = [()]
            for _ in range(maxlen):
                layer = [w + (d,) for w in layer for d in g.digits]
                for w in layer:
                    v = g.denote(w)
                    self.assertNotIn(v, seen)
                    seen[v] = w
            # every value below the smallest unreached one has a word, and it is the address
            for v, w in seen.items():
                self.assertEqual(g.address(v), w)

    def test_unary_is_successor(self):
        self.assertEqual(N.UNARY.render(N.UNARY.address(4)), "SSSS")
        self.assertEqual(N.UNARY.denote((1, 1, 1)), 3)

    def test_heap_conjugacy(self):
        for n in range(0, 20000):
            self.assertEqual(N.bijective2_as_heap(n), N.heap_word(n + 1))

    def test_compile_and_concatenation(self):
        g = N.standard(10)
        for u in [(1, 2), (0,), (), (9, 9, 9)]:
            for v in [(3,), (0, 0), (), (4, 5, 6)]:
                self.assertEqual(g.denote(u + v), N.concat_value(g, u, v))
                f = g.compile(u + v)
                self.assertEqual(f.a, 10 ** len(u + v))
                self.assertEqual(f(0), g.denote(u + v))

    def test_parallel_value(self):
        from ginsdk.cost import Cost
        g = N.standard(10)
        for s in ["7", "42", "1234567890123", "0" * 9 + "1"]:
            c = Cost()
            w = g.parse(s)
            self.assertEqual(N.parallel_value(g, w, c), int(s))
            self.assertEqual(c["compose"], len(w) - 1)

    def test_balanced_ternary_covers_Z(self):
        g = N.BALANCED_TERNARY
        for n in range(-500, 501):
            self.assertEqual(g.denote(g.address(n)), n)

    def test_negative_in_base2_is_periodic_2adic(self):
        digits, status = N.BINARY.expand(-1, 50)
        self.assertEqual(status, "periodic")
        with self.assertRaises(ValueError):
            N.BINARY.address(-5)
        for n in range(-128, 128):
            self.assertEqual(N.twos_complement_from_2adic(n, 8), format(n & 0xFF, "08b"))

    def test_periodic_expansion(self):
        self.assertEqual(N.periodic_expansion(Fraction(1, 3), 10), "0.(3)")
        self.assertEqual(N.periodic_expansion(Fraction(1, 3), 2), "0.(01)")
        self.assertEqual(N.periodic_expansion(Fraction(1, 10), 2), "0.0(0011)")
        self.assertEqual(N.periodic_expansion(Fraction(1, 8), 10), "0.125")
        self.assertEqual(N.periodic_expansion(Fraction(-7, 6), 10), "−1.1(6)")



class TestCanonicalizeConvert(unittest.TestCase):
    def test_canonicalize(self):
        from ginsdk.numerals import canonicalize
        r = canonicalize("0042")
        self.assertEqual((r["value"], r["canonical"], r["was_canonical"], r["leading_zeros"]), (42, "42", False, 2))
        self.assertTrue(canonicalize("0")["was_canonical"])
        self.assertEqual(canonicalize("00")["leading_zeros"], 1)
        self.assertEqual(canonicalize("101", 2)["value"], 5)
        with self.assertRaises(ValueError):
            canonicalize("12", 2)
        with self.assertRaises(ValueError):
            canonicalize("")

    def test_convert_roundtrip(self):
        from ginsdk.numerals import convert
        self.assertEqual(convert("2", 10, 2), "10")
        self.assertEqual(convert("ff", 16, 10), "255")
        for n in range(0, 2000, 7):
            for b in (2, 3, 7, 16, 36):
                self.assertEqual(int(convert(str(n), 10, b), b), n)
                self.assertEqual(convert(convert(str(n), 10, b), b, 10), str(n))

    def test_numeral_table(self):
        from ginsdk.numerals import numeral_table
        t = numeral_table(4)
        self.assertEqual(t["binary"], "100")
        self.assertEqual(t["unary (bijective base 1)"], "SSSS")
        self.assertEqual(numeral_table(0)["bijective base 2"], "ε")


class TestOtherBases(unittest.TestCase):
    def test_negabinary_names_every_integer_once(self):
        from ginsdk.numerals import NEGABINARY as G
        seen = {}
        import itertools
        for L in range(0, 9):
            for w in itertools.product((0, 1), repeat=L):
                if w and w[0] == 0:
                    continue
                v = G.denote(w)
                self.assertNotIn(v, seen)
                seen[v] = w
        for n in range(-80, 81):
            self.assertEqual(G.denote(G.address(n)), n)

    def test_hyperbinary_counts_are_stern(self):
        from ginsdk.numerals import REDUNDANT_BINARY as R
        s = [0, 1]
        for k in range(2, 70):
            s.append(s[k // 2] if k % 2 == 0 else s[k // 2] + s[k // 2 + 1])
        for n in range(60):
            hb = sum(1 for w in R.words_denoting(n, 7) if not w or w[0] != 0)
            self.assertEqual(hb, s[n + 1], n)


if __name__ == "__main__":
    unittest.main()
