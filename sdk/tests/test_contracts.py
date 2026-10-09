"""Tests for operation contracts, layered inspection, independent verification and the CLI."""
import io
import json
import unittest
from contextlib import redirect_stdout

from ginsdk import contracts, expr
from ginsdk.__main__ import main


class TestContracts(unittest.TestCase):
    def test_document_is_json_and_complete(self):
        doc = contracts.contracts_document()
        json.dumps(doc, ensure_ascii=False)
        self.assertEqual(doc["schema"], "gin-contracts/1")
        ops = {c["op"] for c in doc["contracts"]}
        self.assertEqual(ops, {"+", "-", "*", "/", "//", "%", "^", "sqrt", "gcd"})
        statuses = {s["status"] for s in doc["statuses"]}
        self.assertEqual(statuses, set(expr.STATUS_TEXT))

    def test_every_failure_class_is_a_status(self):
        for c in contracts.CONTRACTS:
            for d in c["domains"]:
                for f in d["failures"]:
                    self.assertIn(f, expr.STATUS_TEXT, (c["op"], d["domain"], f))

    def test_division_contract_lists_both_failures(self):
        q = [d for d in contracts.contract("/")["domains"] if d["domain"].startswith("Q")][0]
        self.assertEqual(set(q["failures"]), {"no-solution", "non-unique"})


class TestInspect(unittest.TestCase):
    CASES = [  # expression, domain, mathematics status, execution status, relation
        ("1 + 1", "N", "value", "value", "agrees"),
        ("6 / 3", "Q", "value", "value", "agrees"),
        ("0 / 1", "Q", "value", "value", "agrees"),
        ("1 / 0", "Q", "no-solution", "no-solution", "agrees"),
        ("0 / 0", "Q", "non-unique", "non-unique", "agrees"),
        ("1 / 0", "binary64", "no-solution", "special", "special-datum"),
        ("0 / 0", "binary64", "non-unique", "special", "special-datum"),
        ("1 / 0", "int32 AArch64", "no-solution", "value", "totalized"),
        ("1 / 0", "int32 RISC-V", "no-solution", "value", "totalized"),
        ("1 / 0", "int32 x86-64", "no-solution", "trap", "signalled"),
        ("1 / 0", "int32 C", "no-solution", "undefined", "undefined"),
        ("1 / 0", "Python", "no-solution", "exception", "signalled"),
        ("0.1 + 0.2", "binary64", "value", "value", "rounded"),
        ("2147483647 + 1", "int32 Java", "value", "value", "wrapped"),
        ("2147483647 + 1", "int32 C", "value", "undefined", "undefined"),
        ("-7 / 2", "int32 x86-64", "no-solution", "value", "selected"),
        ("-7 // 2", "int32 C", "value", "value", "different-selection"),
        ("-7 // 2", "Python", "value", "value", "agrees"),
        ("0 - 1", "N", "no-solution", "no-solution", "agrees"),
        ("2 / 4", "Z/6", "non-unique", "non-unique", "agrees"),
    ]

    def test_cases(self):
        for e, d, m, x, rel in self.CASES:
            with self.subTest(e=e, d=d):
                r = contracts.inspect(e, d)
                self.assertEqual(r["mathematics"]["status"], m)
                self.assertEqual(r["execution"]["status"], x)
                self.assertEqual(r["relation"]["kind"], rel)
                json.dumps(r, ensure_ascii=False, default=str)

    def test_layers_stop_where_expected(self):
        r = contracts.inspect("1 +", "Q")
        self.assertFalse(r["well_formed"])
        self.assertFalse(r["layers"]["syntax"]["ok"])
        r = contracts.inspect("0.5 + 1", "Z")
        self.assertTrue(r["layers"]["syntax"]["ok"])
        self.assertFalse(r["layers"]["typing"]["ok"])
        self.assertIsNone(r["layers"]["semantics"]["ok"])
        r = contracts.inspect("1 / 0", "Q")
        self.assertFalse(r["layers"]["semantics"]["ok"])

    def test_contracts_named(self):
        self.assertEqual(contracts.inspect("(1 + 2) * 3 / 4", "Q")["contracts"], ["*", "+", "/"])
        self.assertEqual(contracts.inspect("sqrt(4) - 1", "Q")["contracts"], ["-", "sqrt"])


class TestVerify(unittest.TestCase):
    def test_exact_steps_verified(self):
        for e in ["1 + 1", "(7 - 3) / 2", "6 / 3 - 1/2 * 4", "-(3/4) * 8"]:
            v = contracts.verify(expr.evaluate(e, "Q"))
            self.assertTrue(v["checked"])
            self.assertTrue(v["all_ok"], e)
            self.assertGreater(len(v["steps"]), 0)

    def test_failure_recorded(self):
        v = contracts.verify(expr.evaluate("1 / 0", "Q"))
        self.assertEqual(v["failure"]["status"], "no-solution")

    def test_detects_a_wrong_step(self):
        o = expr.evaluate("6 / 3", "Q")
        o.steps[0].result = "3"           # tamper: 3 · 3 ≠ 6
        self.assertFalse(contracts.verify(o)["all_ok"])

    def test_non_exact_domain_not_claimed(self):
        self.assertFalse(contracts.verify(expr.evaluate("1 + 1", "binary64"))["checked"])


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        f = io.StringIO()
        with redirect_stdout(f):
            code = main(list(args))
        return code, f.getvalue()

    def test_inspect(self):
        code, out = self.run_cli("inspect", "0 / 0", "--domain", "Q")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["mathematics"]["status"], "non-unique")

    def test_eval_and_x(self):
        code, out = self.run_cli("eval", "x / x", "--domain", "Q", "--x", "0")
        self.assertIn("non-unique", out)

    def test_contracts_and_domains(self):
        code, out = self.run_cli("contracts", "/")
        self.assertEqual(json.loads(out)["op"], "/")
        code, out = self.run_cli("domains")
        self.assertIn("int32 RISC-V", out)

    def test_compare(self):
        code, out = self.run_cli("compare", "1/0", "--domains", "Q,binary64")
        self.assertEqual(len(out.strip().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
