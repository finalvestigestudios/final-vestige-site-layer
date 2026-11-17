"""R490 Win32 job custody negative controls without real Windows execution."""
from __future__ import annotations

import unittest
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

from windows_job_custody_r490 import JobCustodyError, WindowsJob


class FakeKernel:
    def __init__(self, fail=""):
        self.fail = fail
        self.calls = []

    def create(self, *args):
        self.calls.append("create")
        return 0 if self.fail == "create" else 1234

    def enable_kill_on_close(self, job):
        self.calls.append("kill_on_close")
        return self.fail != "limits"

    def assign(self, job, process):
        self.calls.append(("assign", process))
        return self.fail != "assign"

    def terminate(self, job, code):
        self.calls.append("terminate")
        return self.fail != "terminate"

    def close(self, job):
        self.calls.append("close")
        return self.fail != "close"


class WindowsJobCustodyR490(unittest.TestCase):
    def test_success_configures_custody_before_assign(self):
        api = FakeKernel()
        job = WindowsJob(SimpleNamespace(_handle=987), api=api)
        self.assertEqual(api.calls, ["create", "kill_on_close", ("assign", 987)])
        job.terminate()
        job.close()
        self.assertEqual(api.calls[-2:], ["terminate", "close"])

    def test_create_failure_blocks_without_partial_job(self):
        api = FakeKernel("create")
        with self.assertRaises(JobCustodyError):
            WindowsJob(SimpleNamespace(_handle=987), api=api)
        self.assertEqual(api.calls, ["create"])

    def test_limits_failure_closes_and_never_assigns(self):
        api = FakeKernel("limits")
        with self.assertRaises(JobCustodyError):
            WindowsJob(SimpleNamespace(_handle=987), api=api)
        self.assertEqual(api.calls, ["create", "kill_on_close", "close"])

    def test_assign_failure_closes_and_blocks(self):
        api = FakeKernel("assign")
        with self.assertRaises(JobCustodyError):
            WindowsJob(SimpleNamespace(_handle=987), api=api)
        self.assertEqual(api.calls[-2:], [("assign", 987), "close"])

    def test_missing_process_handle_blocks_and_closes(self):
        api = FakeKernel()
        with self.assertRaises(JobCustodyError):
            WindowsJob(SimpleNamespace(), api=api)
        self.assertNotIn(("assign", None), api.calls)
        self.assertEqual(api.calls[-1], "close")

    def test_terminate_failure_is_explicit(self):
        api = FakeKernel("terminate")
        job = WindowsJob(SimpleNamespace(_handle=2), api=api)
        with self.assertRaises(JobCustodyError):
            job.terminate()
        job.close()
        self.assertEqual(api.calls[-2:], ["terminate", "close"])

    def test_close_failure_is_explicit_and_no_double_close(self):
        api = FakeKernel("close")
        job = WindowsJob(SimpleNamespace(_handle=2), api=api)
        with self.assertRaises(JobCustodyError):
            job.close()
        job.close()
        self.assertEqual(api.calls.count("close"), 1)

    def test_close_idempotent_after_success(self):
        api = FakeKernel()
        job = WindowsJob(SimpleNamespace(_handle=2), api=api)
        job.close()
        job.close()
        job.terminate()
        self.assertEqual(api.calls.count("close"), 1)

    def test_private_exception_is_replaced(self):
        class UnsafeKernel(FakeKernel):
            def assign(self, job, process):
                raise RuntimeError("secret customer invoice /home/private/report.csv")
        api = UnsafeKernel()
        with self.assertRaisesRegex(JobCustodyError, "Windows job custody unavailable") as caught:
            WindowsJob(SimpleNamespace(_handle=2), api=api)
        self.assertNotIn("secret customer", str(caught.exception))


    @unittest.skipUnless(os.name == "nt", "Requires native Windows Job Objects")
    def test_native_job_terminates_quiet_descendant_after_parent_success(self):
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "escaped.txt"
            ready = Path(temp) / "ready.txt"
            descendant = (
                "import time;from pathlib import Path;"
                "Path(%r).write_text('ready');time.sleep(1.5);"
                "Path(%r).write_text('escaped')" % (str(ready), str(marker)))
            parent = (
                "import subprocess,sys,time;from pathlib import Path;"
                "subprocess.Popen([sys.executable,'-c',%r],"
                "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
                "end=time.monotonic()+15;"
                "\nwhile not Path(%r).exists() and time.monotonic()<end: time.sleep(0.02)\n"
                "if not Path(%r).exists(): sys.exit(17)\n"
                "print('OK')" % (descendant, str(ready), str(ready)))
            process = subprocess.Popen(
                (sys.executable, "-u", "-c", parent),
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            try:
                job = WindowsJob(process)
            except Exception:
                process.kill()
                process.wait()
                if process.stdout is not None:
                    process.stdout.close()
                raise
            try:
                out, _ = process.communicate(timeout=20)
                self.assertEqual((process.returncode, out.strip()), (0, b"OK"))
                self.assertTrue(ready.exists(), "Native child start handshake missing")
            finally:
                job.terminate()
                job.close()
            time.sleep(1.8)
            self.assertFalse(marker.exists(), "Windows grandchild escaped job cleanup")


if __name__ == "__main__":
    unittest.main()
