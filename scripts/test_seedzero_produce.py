import contextlib
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name("seedzero-produce")
LOADER = importlib.machinery.SourceFileLoader("seedzero_produce", str(SCRIPT))
SPEC = importlib.util.spec_from_loader("seedzero_produce", LOADER)
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)


class ProductionCompleteTest(unittest.TestCase):
    def test_accepts_exact_marker(self):
        self.assertTrue(
            MODULE.production_complete(
                "Published three videos.\nPRODUCTION_STATUS: COMPLETE\n"
            )
        )

    def test_rejects_incomplete_report(self):
        self.assertFalse(
            MODULE.production_complete("Both processing gates are still running.")
        )

    def test_rejects_marker_with_extra_text(self):
        self.assertFalse(MODULE.production_complete("PRODUCTION_STATUS: COMPLETE soon"))


class StateTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.state_home = Path(temporary.name)
        patcher = mock.patch.dict(os.environ, {"XDG_STATE_HOME": temporary.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = self.state_home / "seedzero"

    def write_report(self, timestamp):
        path = self.root / timestamp / "result.html"
        path.parent.mkdir(parents=True)
        path.write_text("<pre>report</pre>")
        return path

    def test_uses_home_without_xdg_state_home(self):
        with mock.patch.dict(os.environ, {"HOME": "/home/test"}):
            del os.environ["XDG_STATE_HOME"]
            self.assertEqual(
                MODULE.state_root(),
                Path("/home/test/.local/state/seedzero"),
            )

    def test_last_result_picks_newest_timestamp(self):
        self.write_report("20260923T100000.000000Z")
        newest = self.write_report("20260924T100000.000000Z")
        self.write_report("20260922T100000.000000Z")
        self.assertEqual(MODULE.last_result(), newest)

    def test_last_result_skips_run_without_report(self):
        report = self.write_report("20260923T100000.000000Z")
        (self.root / "20260924T100000.000000Z").mkdir()
        self.assertEqual(MODULE.last_result(), report)

    def test_last_result_ignores_non_timestamp_dirs(self):
        report = self.write_report("20260924T100000.000000Z")
        self.write_report("latest")
        self.write_report("old")
        self.assertEqual(MODULE.last_result(), report)

    def test_last_result_fails_with_only_non_timestamp_dirs(self):
        self.write_report("latest")
        with self.assertRaisesRegex(RuntimeError, "no result.html under"):
            MODULE.last_result()

    def test_last_result_fails_without_state(self):
        with self.assertRaisesRegex(RuntimeError, "no production state at"):
            MODULE.last_result()

    def test_last_result_fails_without_report(self):
        (self.root / "20260924T100000.000000Z").mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError, "no result.html under"):
            MODULE.last_result()

    def test_open_last_opens_newest_report_without_new_run(self):
        report = self.write_report("20260924T100000.000000Z")
        with (
            mock.patch.object(MODULE.subprocess, "run") as run,
            mock.patch.object(MODULE, "run_claude") as run_claude,
        ):
            run.return_value.returncode = 0
            self.assertEqual(MODULE.main(["--open-last"]), 0)
        run.assert_called_once_with(["xdg-open", report], check=False)
        run_claude.assert_not_called()
        self.assertEqual(os.listdir(self.root), ["20260924T100000.000000Z"])

    def test_open_last_returns_xdg_open_status(self):
        self.write_report("20260924T100000.000000Z")
        with mock.patch.object(MODULE.subprocess, "run") as run:
            run.return_value.returncode = 4
            self.assertEqual(MODULE.main(["--open-last"]), 4)

    def test_open_runs_production_then_opens_its_report(self):
        with (
            mock.patch.object(MODULE.subprocess, "run") as run,
            mock.patch.object(MODULE, "run_claude") as run_claude,
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            run_claude.return_value = ("done\nPRODUCTION_STATUS: COMPLETE\n", "", 0)
            run.return_value.returncode = 3
            self.assertEqual(MODULE.main(["--open"]), 3)
        (run_dir,) = self.root.iterdir()
        run.assert_called_once_with(
            ["xdg-open", run_dir / "result.html"], check=False
        )

    def test_open_last_without_state_does_not_create_it(self):
        with mock.patch.object(MODULE.subprocess, "run") as run:
            with self.assertRaises(RuntimeError):
                MODULE.main(["--open-last"])
        run.assert_not_called()
        self.assertFalse(self.root.exists())


class LogsTest(unittest.TestCase):
    def test_logs_replaces_process_with_journalctl(self):
        with (
            mock.patch.object(MODULE.os, "execvp") as execvp,
            mock.patch.object(MODULE, "state_dir") as state_dir,
            mock.patch.object(MODULE, "run_claude") as run_claude,
        ):
            MODULE.main(["--logs"])
        execvp.assert_called_once_with(
            "journalctl",
            ["journalctl", "--user", "-fu", "seedzero-produce.service"],
        )
        state_dir.assert_not_called()
        run_claude.assert_not_called()


class ArgumentTest(unittest.TestCase):
    def test_modes_are_mutually_exclusive(self):
        modes = ["--detach", "--open", "--open-last", "--logs"]
        for first in modes:
            for second in modes:
                if first == second:
                    continue
                with self.subTest(first=first, second=second):
                    with (
                        contextlib.redirect_stderr(io.StringIO()),
                        self.assertRaises(SystemExit),
                    ):
                        MODULE.parse_args([first, second])

    def test_modes_parse_alone(self):
        self.assertTrue(MODULE.parse_args(["--logs"]).logs)
        self.assertTrue(MODULE.parse_args(["--open-last"]).open_last)
        self.assertTrue(MODULE.parse_args(["--open"]).open)
        self.assertTrue(MODULE.parse_args(["-d"]).detach)


if __name__ == "__main__":
    unittest.main()
