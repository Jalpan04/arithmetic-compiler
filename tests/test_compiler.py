"""
Unit and integration test suite for the Interactive Arithmetic Expression Compiler.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "python_gui"))

from compiler_bridge import compile_expr


class TestCompilerPipeline(unittest.TestCase):
    def test_basic_arithmetic(self):
        cases = [
            ("1 + 2", 3.0),
            ("10 - 4", 6.0),
            ("3 * 7", 21.0),
            ("20 / 4", 5.0),
            ("14 % 4", 2.0),
            ("2 ^ 3", 8.0),
        ]
        for expr, expected in cases:
            res = compile_expr(expr)
            self.assertTrue(res.get("success"), f"Failed on {expr}: {res.get('error_message')}")
            self.assertAlmostEqual(res.get("final_result"), expected, places=5)

    def test_operator_precedence(self):
        cases = [
            ("2 + 3 * 4", 14.0),
            ("(2 + 3) * 4", 20.0),
            ("2 ^ 3 ^ 2", 512.0), # Right associative: 2 ^ (3 ^ 2) = 2 ^ 9 = 512
            ("(2 ^ 3) ^ 2", 64.0),
            ("10 - 3 + 2", 9.0),   # Left associative: (10 - 3) + 2 = 9
            ("100 / 5 / 2", 10.0), # Left associative: (100 / 5) / 2 = 10
        ]
        for expr, expected in cases:
            res = compile_expr(expr)
            self.assertTrue(res.get("success"), f"Failed on {expr}: {res.get('error_message')}")
            self.assertAlmostEqual(res.get("final_result"), expected, places=5)

    def test_unary_operators(self):
        cases = [
            ("-5 + 12", 7.0),
            ("-(3 + 4)", -7.0),
            ("2 * -3", -6.0),
            ("+10 - -5", 15.0),
        ]
        for expr, expected in cases:
            res = compile_expr(expr)
            self.assertTrue(res.get("success"), f"Failed on {expr}: {res.get('error_message')}")
            self.assertAlmostEqual(res.get("final_result"), expected, places=5)

    def test_floats_and_scientific(self):
        cases = [
            ("3.5 + 2.25", 5.75),
            (".5 * 4", 2.0),
            ("1e3 + 2.5e2", 1250.0),
        ]
        for expr, expected in cases:
            res = compile_expr(expr)
            self.assertTrue(res.get("success"), f"Failed on {expr}: {res.get('error_message')}")
            self.assertAlmostEqual(res.get("final_result"), expected, places=5)

    def test_bytecode_generation(self):
        res = compile_expr("(3 + 5) * 2 ^ 3")
        self.assertTrue(res.get("success"))
        bytecode = res.get("bytecode", [])
        self.assertGreater(len(bytecode), 0)
        mnemonics = [bc.get("mnemonic") for bc in bytecode]
        self.assertIn("ADD", mnemonics)
        self.assertIn("POW", mnemonics)
        self.assertIn("MUL", mnemonics)
        self.assertIn("HALT", mnemonics)

    def test_division_by_zero_runtime_error(self):
        res = compile_expr("10 / (5 - 5)")
        self.assertFalse(res.get("success"))
        self.assertEqual(res.get("error_stage"), "Runtime Execution (VM)")
        self.assertIn("Division by zero", res.get("error_message"))

    def test_syntax_errors(self):
        cases = [
            "3 + * 5",
            "(4 + 2",
            "4 + 2)",
            "10 %",
            "",
        ]
        for expr in cases:
            res = compile_expr(expr)
            self.assertFalse(res.get("success"), f"Should fail on syntax error: '{expr}'")


if __name__ == "__main__":
    unittest.main()
