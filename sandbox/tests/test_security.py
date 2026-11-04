import json
import unittest

from sandbox.sandbox import run_code


class SecurityTests(unittest.TestCase):

    def assert_cleanup(self, result):
        self.assertTrue(
            result["cleanup_ok"],
            f"Container cleanup failed: {result}"
        )

    def test_network_isolation(self):
        code = """
import socket

try:
    connection = socket.socket()
    connection.settimeout(2)
    connection.connect(("1.1.1.1", 53))
    print("NETWORK_ALLOWED")
except OSError:
    print("NETWORK_BLOCKED")
finally:
    try:
        connection.close()
    except (NameError, OSError):
        pass
"""

        result = run_code(code)

        self.assertEqual(result["status"], "success")
        self.assertIn("NETWORK_BLOCKED", result["stdout"])
        self.assertNotIn("NETWORK_ALLOWED", result["stdout"])
        self.assert_cleanup(result)

    def test_identity_kernel_and_resource_limits(self):
        code = """
import json

status = {}

with open("/proc/self/status") as file:
    for line in file:
        key = line.split(":", 1)[0]
        if key in ("Uid", "Gid", "NoNewPrivs", "CapEff", "Seccomp"):
            status[key] = line.split(":", 1)[1].strip()

limits = {}

for name in ("memory.max", "cpu.max", "pids.max"):
    with open("/sys/fs/cgroup/" + name) as file:
        limits[name] = file.read().strip()

print(json.dumps({"status": status, "limits": limits}))
"""

        result = run_code(code)

        self.assertEqual(result["status"], "success")
        data = json.loads(result["stdout"])

        status = data["status"]
        limits = data["limits"]

        self.assertEqual(status["Uid"].split()[0], "10001")
        self.assertEqual(status["Gid"].split()[0], "10001")
        self.assertEqual(status["NoNewPrivs"], "1")
        self.assertEqual(status["CapEff"], "0000000000000000")
        self.assertEqual(status["Seccomp"], "2")

        self.assertEqual(limits["memory.max"], "134217728")
        self.assertEqual(limits["cpu.max"], "50000 100000")
        self.assertEqual(limits["pids.max"], "32")

        self.assert_cleanup(result)

    def test_readonly_filesystem_and_tmp_noexec(self):
        code = """
import os

try:
    with open("/workspace/proofrun-test-file", "w") as file:
        file.write("test")
    print("ROOTFS_WRITABLE")
except OSError:
    print("ROOTFS_READONLY")

tmp_options = None

with open("/proc/mounts") as file:
    for line in file:
        fields = line.split()
        if len(fields) >= 4 and fields[1] == "/tmp":
            tmp_options = fields[3].split(",")
            break

print("TMP_NOEXEC", tmp_options is not None and "noexec" in tmp_options)
"""

        result = run_code(code)

        self.assertEqual(result["status"], "success")
        self.assertIn("ROOTFS_READONLY", result["stdout"])
        self.assertNotIn("ROOTFS_WRITABLE", result["stdout"])
        self.assertIn("TMP_NOEXEC True", result["stdout"])
        self.assert_cleanup(result)


    def test_memory_limit_classification(self):
        code = """
data = bytearray(256 * 1024 * 1024)
print(len(data))
"""

        result = run_code(code)

        self.assertEqual(
            result["status"],
            "memory_limit",
            f"Expected memory_limit, received: {result}"
        )
        self.assertTrue(result["oom_killed"])
        self.assertEqual(result["container_state"], "exited")
        self.assert_cleanup(result)


if __name__ == "__main__":
    unittest.main()
