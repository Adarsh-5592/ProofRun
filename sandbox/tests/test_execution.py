import unittest

from sandbox.sandbox import run_code


class ExecutionTests(unittest.TestCase):

    def assert_cleanup(self, result):
        self.assertTrue(
            result["cleanup_ok"],
            f"Container cleanup failed: {result}"
        )

    def test_simple_python_execution(self):
        result = run_code("print(1 + 1)")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"].strip(), "2")
        self.assertEqual(result["exit_code"], 0)
        self.assert_cleanup(result)

    def test_large_python_script(self):
        padding = "\n".join(
            ["#" + "x" * 1000 for _ in range(200)]
        )
        code = padding + "\nprint('large-input-ok')"

        result = run_code(code)

        self.assertEqual(result["status"], "success")
        self.assertIn("large-input-ok", result["stdout"])
        self.assert_cleanup(result)

    def test_python_exception(self):
        result = run_code("print(1 / 0)")

        self.assertEqual(result["status"], "error")
        self.assertIn("ZeroDivisionError", result["stderr"])
        self.assertNotEqual(result["exit_code"], 0)
        self.assert_cleanup(result)

    def test_execution_timeout(self):
        result = run_code("while True: pass", timeout_seconds=2)

        self.assertEqual(result["status"], "timeout")
        self.assertTrue(result["timed_out"])
        self.assert_cleanup(result)

    def test_output_limit(self):
        result = run_code("print('A' * 1100000)")

        self.assertEqual(result["status"], "output_limit")
        self.assertTrue(result["output_limited"])
        self.assertLessEqual(
            len(result["stdout"].encode("utf-8")),
            1024 * 1024
        )
        self.assert_cleanup(result)


if __name__ == "__main__":
    unittest.main()
