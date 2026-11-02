"""R146 synthetic private Windows 11 reviewer CLI confidentiality and custody tests."""
from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import private_review_cli_r146 as private_cli
import windows11_manual_acceptance_r109 as qa
import windows11_witness_writer_r122 as writer
import windows11_review_progress_r123 as progress

SECRET = "PRIVATE-FAMILY-OFFICE-CLIENT-LEDGER-ALPHA-2026"


class PrivateReviewCliR146(unittest.TestCase):
    def setUp(self):
        self.pin = "a" * 64
        self.qa_args = [
            "template", "--dist", "C:/review-private/candidates",
            "--r9-report", "C:/review-private/r9.json",
            "--expected-r9-sha256", self.pin,
            "--review", "C:/review-private/review.json",
        ]
        self.writer_args = [
            "--dist", "C:/review-private/candidates",
            "--r9-report", "C:/review-private/r9.json",
            "--expected-r9-sha256", self.pin,
            "--review", "C:/review-private/review.json",
            "--witnesses", "C:/review-private/witnesses",
            "--app", qa.FREE[0], "--check", qa.FREE_CHECKS[0],
            "--state", "PASS", "--observation-file", "C:/review-private/note.txt",
        ]
        self.progress_args = [
            "--dist", "C:/review-private/candidates",
            "--r9-report", "C:/review-private/r9.json",
            "--expected-r9-sha256", self.pin,
            "--review", "C:/review-private/review.json",
            "--witnesses", "C:/review-private/witnesses",
        ]

    def _reject(self, entrypoint, arguments):
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.object(qa, "load_custody", side_effect=AssertionError("must not load")) as custody:
            with mock.patch.object(writer, "record_one", side_effect=AssertionError("must not write")) as recording:
                with mock.patch.object(progress, "inspect", side_effect=AssertionError("must not inspect")) as inspection:
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        status = entrypoint(arguments)
        self.assertEqual(status, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(errors.getvalue(), qa.ERROR + "\n")
        self.assertNotIn(SECRET, errors.getvalue())
        self.assertNotIn("usage:", errors.getvalue().lower())
        self.assertNotIn("Traceback", errors.getvalue())
        custody.assert_not_called()
        recording.assert_not_called()
        inspection.assert_not_called()

    def _help(self, entrypoint):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            with self.assertRaises(SystemExit) as caught:
                entrypoint(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("--expected-r9-sha256", output.getvalue())
        self.assertNotIn(SECRET, output.getvalue())
        self.assertEqual(errors.getvalue(), "")

    def test_r109_unknown_secret_option_is_redacted(self):
        self._reject(qa.main, self.qa_args + ["--unexpected-private", SECRET])

    def test_r109_secret_as_action_is_redacted(self):
        self._reject(qa.main, [SECRET] + self.qa_args[1:])

    def test_r109_missing_review_is_redacted(self):
        self._reject(qa.main, self.qa_args[:-2])

    def test_r109_duplicate_pin_is_rejected(self):
        self._reject(qa.main, self.qa_args + ["--expected-r9-sha256", SECRET])

    def test_r109_duplicate_equals_dist_is_rejected(self):
        self._reject(qa.main, self.qa_args + ["--dist=" + SECRET])

    def test_r109_abbreviated_review_option_is_rejected(self):
        self._reject(qa.main, self.qa_args[:-2] + ["--rev", SECRET])

    def test_r109_help_mixed_with_secret_is_hold(self):
        self._reject(qa.main, self.qa_args + ["--help", SECRET])

    def test_r109_help_alone_is_static(self):
        self._help(qa.main)

    def test_r122_unknown_secret_option_is_redacted(self):
        self._reject(writer.main, self.writer_args + ["--confidential", SECRET])

    def test_r122_secret_app_choice_is_redacted(self):
        data = self.writer_args.copy()
        data[data.index("--app") + 1] = SECRET
        self._reject(writer.main, data)

    def test_r122_secret_state_choice_is_redacted(self):
        data = self.writer_args.copy()
        data[data.index("--state") + 1] = SECRET
        self._reject(writer.main, data)

    def test_r122_missing_observation_file_is_redacted(self):
        self._reject(writer.main, self.writer_args[:-2])

    def test_r122_duplicate_pin_is_rejected(self):
        self._reject(writer.main, self.writer_args + ["--expected-r9-sha256=" + SECRET])

    def test_r122_duplicate_app_is_rejected(self):
        self._reject(writer.main, self.writer_args + ["--app=" + SECRET])

    def test_r122_abbreviated_observation_option_is_rejected(self):
        self._reject(writer.main, self.writer_args[:-2] + ["--observation", SECRET])

    def test_r122_help_mixed_with_secret_is_hold(self):
        self._reject(writer.main, self.writer_args + ["--help", SECRET])

    def test_r122_help_alone_is_static(self):
        self._help(writer.main)

    def test_r123_unknown_secret_option_is_redacted(self):
        self._reject(progress.main, self.progress_args + ["--confidential", SECRET])

    def test_r123_missing_witness_dir_is_redacted(self):
        self._reject(progress.main, self.progress_args[:-2])

    def test_r123_duplicate_pin_is_rejected(self):
        self._reject(progress.main, self.progress_args + ["--expected-r9-sha256", SECRET])

    def test_r123_duplicate_equals_report_is_rejected(self):
        self._reject(progress.main, self.progress_args + ["--r9-report=" + SECRET])

    def test_r123_abbreviated_review_option_is_rejected(self):
        data = self.progress_args.copy()
        data[data.index("--review")] = "--rev"
        self._reject(progress.main, data)

    def test_r123_unexpected_secret_positional_is_redacted(self):
        self._reject(progress.main, self.progress_args + [SECRET])

    def test_r123_help_mixed_with_secret_is_hold(self):
        self._reject(progress.main, ["--help", SECRET])

    def test_r123_unicode_secret_flag_is_redacted(self):
        self._reject(progress.main, self.progress_args + ["--" + SECRET + "\u200d", "VALUE"])

    def test_r123_help_alone_is_static(self):
        self._help(progress.main)

    def test_shared_parser_accepts_one_explicit_option(self):
        parser = private_cli.PrivateReviewParser(add_help=False)
        parser.add_argument("--evidence", required=True)
        self.assertEqual(parser.parse_args(["--evidence", SECRET]).evidence, SECRET)

    def test_shared_parser_rejects_duplicate_equals_forms(self):
        parser = private_cli.PrivateReviewParser(add_help=False)
        parser.add_argument("--evidence", required=True)
        with self.assertRaises(ValueError):
            parser.parse_args(["--evidence=" + SECRET, "--evidence", "other"])

    def test_shared_parser_never_embeds_rejected_choice_in_exception(self):
        parser = private_cli.PrivateReviewParser(add_help=False)
        parser.add_argument("--kind", choices=("allowlisted",), required=True)
        with self.assertRaises(ValueError) as caught:
            parser.parse_args(["--kind", SECRET])
        self.assertNotIn(SECRET, str(caught.exception))

    def test_shared_parser_disables_prefix_abbreviations(self):
        parser = private_cli.PrivateReviewParser(add_help=False)
        parser.add_argument("--evidence", required=True)
        with self.assertRaises(ValueError):
            parser.parse_args(["--ev", SECRET])

    def test_shared_parser_rejects_help_with_other_options(self):
        parser = private_cli.PrivateReviewParser()
        parser.add_argument("--evidence")
        with self.assertRaises(ValueError):
            parser.parse_args(["--help", "--evidence", SECRET])

    def test_valid_witness_writer_still_dispatches_to_record_one(self):
        output = io.StringIO()
        with mock.patch.object(writer, "record_one", return_value={"release_authorized": False}) as record:
            with contextlib.redirect_stdout(output):
                status = writer.main(self.writer_args)
        self.assertEqual(status, 0)
        self.assertEqual(record.call_args.kwargs["expected_pin"], self.pin)
        self.assertIn("release remains HOLD", output.getvalue())

    def test_valid_progress_still_dispatches_to_inspect(self):
        output = io.StringIO()
        with mock.patch.object(progress, "inspect", return_value={"status": "RELEASE_HOLD", "release_authorized": False}) as inspect:
            with contextlib.redirect_stdout(output):
                status = progress.main(self.progress_args)
        self.assertEqual(status, 0)
        self.assertEqual(inspect.call_args.kwargs["expected_pin"], self.pin)
        self.assertIn("RELEASE_HOLD", output.getvalue())


if __name__ == "__main__":
    unittest.main()
