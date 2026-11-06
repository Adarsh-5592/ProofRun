import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from subprocess import CompletedProcess
from unittest.mock import patch

from sandbox import cleanup


def container_inspection(container_id, name, age_seconds, status='exited'):
    created = (
        datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    ).isoformat()

    return json.dumps([{
        "Id": container_id,
        "Name": f"/{name}",
        "Created": created,
        "State": {"Status": status},
    }])


class CleanupTests(unittest.TestCase):

    @patch("sandbox.cleanup.docker_command")
    def test_identifies_old_managed_container(self, docker):
        docker.side_effect = [
            CompletedProcess([], 0, "old123\n", ""),
            CompletedProcess(
                [], 0, container_inspection("old123", "proofrun-old", 600), ""
            ),
        ]

        stale = cleanup.find_stale_containers(300)

        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]["name"], "proofrun-old")

    @patch("sandbox.cleanup.docker_command")
    def test_ignores_recent_container(self, docker):
        docker.side_effect = [
            CompletedProcess([], 0, "recent123\n", ""),
            CompletedProcess(
                [], 0,
                container_inspection("recent123", "proofrun-recent", 60), ""
            ),
        ]

        stale = cleanup.find_stale_containers(300)

        self.assertEqual(stale, [])

    @patch("sandbox.cleanup.docker_command")
    def test_never_selects_old_running_container(self, docker):
        docker.side_effect = [
            CompletedProcess([], 0, "running123\\n", ""),
            CompletedProcess(
                [], 0,
                container_inspection(
                    "running123", "proofrun-active", 600, status="running"
                ),
                "",
            ),
        ]

        stale = cleanup.find_stale_containers(300)

        self.assertEqual(stale, [])

    @patch("sandbox.cleanup.docker_command")
    def test_queries_only_managed_containers(self, docker):
        docker.return_value = CompletedProcess([], 0, "", "")

        cleanup.find_stale_containers(300)

        docker.assert_called_once_with([
            "ps", "-aq",
            "--filter", "label=proofrun.managed=true",
        ])

    @patch("sandbox.cleanup.docker_command")
    def test_docker_query_failure_is_reported(self, docker):
        docker.return_value = CompletedProcess(
            [], 1, "", "Docker unavailable"
        )

        with self.assertRaises(RuntimeError):
            cleanup.find_stale_containers(300)

    @patch("sandbox.cleanup.docker_command")
    def test_invalid_inspection_is_skipped(self, docker):
        docker.side_effect = [
            CompletedProcess([], 0, "bad123\n", ""),
            CompletedProcess([], 0, "invalid-json", ""),
        ]

        stale = cleanup.find_stale_containers(300)

        self.assertEqual(stale, [])

    @patch("sandbox.cleanup.docker_command")
    @patch("sandbox.cleanup.find_stale_containers")
    def test_dry_run_does_not_delete(
        self, find_stale, docker
    ):
        find_stale.return_value = [{
            "id": "old123",
            "name": "proofrun-old",
            "status": "exited",
            "age": 600,
        }]

        output = io.StringIO()

        with patch.object(sys, "argv", ["cleanup.py"]):
            with redirect_stdout(output):
                result = cleanup.main()

        self.assertEqual(result, 0)
        self.assertIn("DRY RUN", output.getvalue())
        docker.assert_not_called()

    @patch("sandbox.cleanup.docker_command")
    @patch("sandbox.cleanup.find_stale_containers")
    def test_delete_requires_explicit_flag(
        self, find_stale, docker
    ):
        find_stale.return_value = [{
            "id": "old123",
            "name": "proofrun-old",
            "status": "exited",
            "age": 600,
        }]
        docker.return_value = CompletedProcess([], 0, "", "")

        with patch.object(sys, "argv", ["cleanup.py", "--delete"]):
            result = cleanup.main()

        self.assertEqual(result, 0)
        docker.assert_called_once_with(
            ["rm", "--force", "old123"],
            timeout=15,
        )


if __name__ == "__main__":
    unittest.main()
