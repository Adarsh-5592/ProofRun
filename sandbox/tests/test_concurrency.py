import threading
import unittest
from unittest.mock import patch

from sandbox import sandbox


class ConcurrencyTests(unittest.TestCase):

    def test_rejects_third_simultaneous_execution(self):
        both_started = threading.Event()
        release = threading.Event()
        lock = threading.Lock()

        active = 0
        maximum_active = 0
        results = []

        def fake_execution(code, timeout_seconds):
            nonlocal active, maximum_active

            with lock:
                active += 1
                maximum_active = max(maximum_active, active)

                if active == 2:
                    both_started.set()

            release.wait(timeout=3)

            with lock:
                active -= 1

            return {"status": "success"}

        with patch.object(
            sandbox, "_run_code", side_effect=fake_execution
        ), patch.object(sandbox, "SLOT_WAIT_SECONDS", 0.1):

            threads = [
                threading.Thread(
                    target=lambda: results.append(
                        sandbox.run_code("print(1)")
                    )
                )
                for _ in range(2)
            ]

            try:
                for thread in threads:
                    thread.start()

                self.assertTrue(both_started.wait(timeout=2))

                third = sandbox.run_code("print(3)")
                self.assertEqual(third["status"], "busy")

            finally:
                release.set()

                for thread in threads:
                    thread.join(timeout=4)

        self.assertTrue(all(not t.is_alive() for t in threads))
        self.assertEqual(len(results), 2)
        self.assertEqual(maximum_active, 2)

    def test_execution_slot_released_after_exception(self):
        with patch.object(
            sandbox,
            "_run_code",
            side_effect=RuntimeError("simulated failure"),
        ):
            with self.assertRaises(RuntimeError):
                sandbox.run_code("print(1)")

        with patch.object(
            sandbox,
            "_run_code",
            return_value={"status": "success"},
        ):
            result = sandbox.run_code("print(2)")

        self.assertEqual(result["status"], "success")


if __name__ == "__main__":
    unittest.main()
