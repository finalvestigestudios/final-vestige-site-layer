"""End-to-end deterministic checks for each packaged Windows executable.

Invoked with --smoke-test. Uses only temporary synthetic files, no network,
telemetry, external data, GUI, credentials, or production side effects.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
from pathlib import Path

from . import engine, evidence_vault, exception_review
from .vault_smoke_scope import check_scoped_vault_roundtrip
from .smoke_output_roles_r389 import verify_smoke_output_roles


def _csv(folder: Path, name: str, fields: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    path = folder / name
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)
    return str(path)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _check(condition: bool, invariant: str) -> None:
    """Use explicit failure: Python -O strips assertions and must not bypass checks."""
    if not condition:
        raise RuntimeError("Packaged executable smoke check failed: " + invariant)


def run_smoke(app_id: str) -> list[Path]:
    """Exercise a packaged application's real engine and verify its outputs.

    Any exception is fatal and must produce a nonzero executable exit code.
    The tests must validate specific behavior, not merely check for a file.
    """
    with tempfile.TemporaryDirectory(prefix="fvs-smoke-") as temp:
        root = Path(temp)
        if app_id == "ledger":
            left = _csv(root, "ledger-left.csv", ("id", "amount"), [
                ("A", "10.00"), ("B", "8.00")])
            right = _csv(root, "ledger-right.csv", ("id", "amount"), [
                ("A", "10.00"), ("B", "7.00")])
            outputs = engine.ledger_diff(left, right, str(root))
            rows = _rows(outputs[0])
            _check({r["id"]: r["status"] for r in rows} == {
                "A": "matched", "B": "variance"}, "smoke invariant 01")
            _check(all(r["left_source_sha256"] == hashlib.sha256(
                    Path(left).read_bytes()).hexdigest()
                    and r["right_source_sha256"] == hashlib.sha256(
                    Path(right).read_bytes()).hexdigest()
                    and r["input_identity_review"] == "" for r in rows),
                   "smoke invariant 34")
            same_report = _rows(engine.ledger_diff(left, left, str(root))[0])
            _check(same_report and all(
                   r["input_identity_review"] == "identical_source_bytes_review"
                   for r in same_report), "smoke invariant 35")
            # R72: verify the packaged ledger importer does not disclose
            # private filenames when a real source row is rejected.
            private_name = "CLIENT_462_PRIVATE_PAYROLL_DO_NOT_LOG.csv"
            private_source = _csv(root, private_name, ("id", "amount"), [("---", "1")])
            reports_before = set(root.glob("ledger-diff-*.csv"))
            try:
                engine.ledger_diff(private_source, right, str(root))
            except ValueError as error:
                _check("CLIENT_462_PRIVATE_PAYROLL_DO_NOT_LOG" not in str(error),
                       "smoke invariant 43")
                _check("Blank transaction ID at physical CSV row 2" in str(error),
                       "smoke invariant 44")
            else:
                raise RuntimeError("Packaged executable smoke check failed: smoke invariant 43")
            _check(set(root.glob("ledger-diff-*.csv")) == reports_before,
                   "smoke invariant 45")
        elif app_id == "invoices":
            source = _csv(root, "invoices.csv", ("vendor", "invoice_number", "amount", "date"), [
                ("ACME", "INV-100", "200.00", "2026-01-01"),
                ("Acme", "INV-100", "200", "2026-01-02")])
            outputs = engine.invoice_twins(source, str(root))
            invoice_rows = _rows(outputs[0])
            _check(invoice_rows[0]["status"] == "exact_invoice_key", "smoke invariant 02")
            _check(invoice_rows[0]["source_sha256"] == hashlib.sha256(
                   Path(source).read_bytes()).hexdigest(), "smoke invariant 36")
            candidate_ref = invoice_rows[0]["candidate_ref"]
            _check(len(candidate_ref) == 64 and
                   all(char in "0123456789abcdef" for char in candidate_ref),
                   "smoke invariant 37")
        elif app_id == "spend":
            source = _csv(root, "spend.csv", ("vendor", "amount", "date"), [
                ("ACME", "10", "2026-01-01"), ("ACME", "10", "2026-02-01"),
                ("ACME", "10", "2026-03-01"), ("ACME", "30", "2026-04-01")])
            outputs = engine.spend_map(source, str(root))
            checked = _rows(outputs[0])[-1]
            _check(checked["flag"] == "review_spike", "smoke invariant 03")
            _check(checked["baseline_median"] == "10.00"
                   and checked["history_months"] == "3"
                   and checked["source_rows"] == "5", "smoke invariant 31")
            _check(checked["source_sha256"] == hashlib.sha256(
                   Path(source).read_bytes()).hexdigest(), "smoke invariant 33")
            collision_input = _csv(root, "spend-collision.csv",
                ("vendor", "amount", "date"), [
                ("A-CME", "2", "2026-01-01"),
                ("ACME", "3", "2026-02-01")])
            collision_output = engine.spend_map(collision_input, str(root))
            collision_rows = _rows(collision_output[0])
            _check(len(collision_rows) == 2 and
                   all("normalized_vendor_collision_review" in row["flag"]
                       for row in collision_rows) and
                   [row["source_rows"] for row in collision_rows] == ["2", "3"],
                   "smoke invariant 32")
        elif app_id == "policy":
            before = root / "before.txt"
            after = root / "after.txt"
            before.write_text("Review within 30 days.\n", encoding="utf-8")
            after.write_text("Review within 15 days.\n", encoding="utf-8")
            outputs = engine.policy_delta(str(before), str(after), str(root))
            diff = outputs[0].read_text(encoding="utf-8")
            _check("-Review within 30 days." in diff, "smoke invariant 04")
            _check("+Review within 15 days." in diff, "smoke invariant 05")
            _check(hashlib.sha256(before.read_bytes()).hexdigest() in diff
                   and hashlib.sha256(after.read_bytes()).hexdigest() in diff,
                   "smoke invariant 38")
            same_version = engine.policy_delta(str(before), str(before), str(root))[0]
            _check("Both source files have identical bytes" in
                   same_version.read_text(encoding="utf-8"),
                   "smoke invariant 39")
            # R76: ensure the real packaged Policy Delta workflow visibly
            # distinguishes CRLF, literal backslashes and tab characters.
            cr_before = root / "before-controls.txt"
            cr_after = root / "after-controls.txt"
            cr_before.write_bytes(b"Review\twithin 30 days.\r\n")
            cr_after.write_bytes(b"Review\\twithin 15 days.\n")
            cr_report = engine.policy_delta(str(cr_before), str(cr_after),
                                            str(root))[0].read_bytes()
            _check(b"\r" not in cr_report and b"\t" not in cr_report,
                   "smoke invariant 46")
            _check(b"-Review\\twithin 30 days.\\r\n" in cr_report
                   and b"+Review\\\\twithin 15 days.\n" in cr_report,
                   "smoke invariant 47")
            _check(hashlib.sha256(cr_before.read_bytes()).hexdigest().encode() in cr_report
                   and hashlib.sha256(cr_after.read_bytes()).hexdigest().encode() in cr_report,
                   "smoke invariant 48")
            # R77: permitted invisible Unicode formatting must be explicit
            # in the ACTUAL packaged policy engine's human-review report.
            invisible_before = root / "before-invisible.txt"
            invisible_after = root / "after-invisible.txt"
            invisible_before.write_bytes("Approve\u200b now.\n".encode("utf-8"))
            invisible_after.write_bytes("Approve\ufe0f now.\n".encode("utf-8"))
            invisible_report = engine.policy_delta(
                str(invisible_before), str(invisible_after), str(root)
            )[0].read_text(encoding="utf-8")
            _check("-Approve\\u200b now.\n+Approve\\ufe0f now.\n" in
                   invisible_report, "smoke invariant 49")
            _check("\u200b" not in invisible_report and
                   "\ufe0f" not in invisible_report, "smoke invariant 50")
            _check(hashlib.sha256(invisible_before.read_bytes()).hexdigest() in
                   invisible_report and
                   hashlib.sha256(invisible_after.read_bytes()).hexdigest() in
                   invisible_report, "smoke invariant 51")
        elif app_id == "grants":
            claims = _csv(root, "claims.csv", ("id", "amount", "program"), [
                ("C1", "20", "G1")])
            ledger = _csv(root, "ledger.csv", ("id", "amount", "program"), [
                ("C1", "20", "G1")])
            budget = _csv(root, "budget.csv", ("program", "budget"), [
                ("G1", "10")])
            outputs = engine.grant_audit(claims, ledger, budget, str(root))
            _check(len(outputs) == 3, "smoke invariant 06")
            _check(_rows(outputs[1])[0]["status"] == "over_budget_review", "smoke invariant 07")
            _check("SHA-256" in outputs[2].read_text(encoding="utf-8"), "smoke invariant 08")
            # Also smoke-test explicit multi-program allocation and linked credit.
            linked_claims = _csv(root, "linked-claims.csv",
                ("claim_id","amount","program","ledger_reference","claim_type","related_claim"), [
                ("A1","60","G1","TX100","claim",""),
                ("A2","40","G2","TX100","claim",""),
                ("A3","10","G1","TX200","claim",""),
                ("CR3","2","G1","TX200","credit","A3")])
            linked_ledger = _csv(root, "linked-ledger.csv", ("id","amount","program"), [
                ("TX100","100","Shared"), ("TX200","8","G1")])
            linked_budget = _csv(root, "linked-budget.csv", ("program","budget"), [
                ("G1","100"), ("G2","100")])
            outputs = engine.grant_audit(linked_claims, linked_ledger,
                                         linked_budget, str(root))
            details = {row["id"]: row for row in _rows(outputs[0])}
            _check(len(outputs) == 3, "smoke invariant 09")
            _check("split_allocation_review" in details["TX100"]["status"], "smoke invariant 10")
            _check(details["TX100"]["claim_amount"] == "100.00", "smoke invariant 11")
            _check(details["TX200"]["net_claim_amount"] == "8.00", "smoke invariant 12")
            _check("credit_memo_review" in details["TX200"]["status"], "smoke invariant 13")
            summary = {row["program"]: row for row in _rows(outputs[1])}
            _check(summary["G1"]["claimed"] == "68.00", "smoke invariant 14")
            _check(summary["G2"]["claimed"] == "40.00", "smoke invariant 15")
            _check("SHA-256" in outputs[2].read_text(encoding="utf-8"), "smoke invariant 16")
            # R66: a confidential unsupported claim type must fail before export.
            private_claims = _csv(root, "private-claims.csv",
                ("claim_id","amount","program","ledger_reference","claim_type","related_claim"), [
                ("Q1","100.00","G1","TX100","private-reimbursement-991","")])
            private_destination = root / "grant-private-output"
            private_destination.mkdir()
            try:
                engine.grant_audit(private_claims, linked_ledger, linked_budget,
                                   str(private_destination))
            except ValueError as error:
                _check("Unsupported claim_type at claim CSV physical row 2" in str(error),
                       "smoke invariant 40")
                _check("private-reimbursement-991" not in str(error), "smoke invariant 41")
            else:
                raise ValueError("smoke invariant 40")
            _check(not any(private_destination.iterdir()), "smoke invariant 42")
            # Exercise packaged premium human-review code using synthetic data.
            batch = exception_review.read_cases(outputs[0], "grants")
            _check(batch.cases, "smoke invariant 17")
            journal = root / "grant-review.jsonl"
            event = exception_review.append_review(
                outputs[0], "grants", journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="Smoke Reviewer", decision="needs_evidence",
                rationale="Request independent supporting reimbursement evidence.")
            _check(event["decision"] == "needs_evidence", "smoke invariant 18")
            register = exception_review.export_register(outputs[0], "grants", journal, root)
            _check(_rows(register)[0]["review_state"] == "needs_evidence", "smoke invariant 19")
            # Validate AES-GCM encrypted evidence backup inside the packaged EXE.
            passphrase = "Synthetic smoke-only passphrase 2026!"
            sealed = evidence_vault.seal_evidence(
                outputs[0], "grants", journal, root, passphrase)
            restored = check_scoped_vault_roundtrip(
                sealed, root, passphrase, "grants", outputs[0],
                journal, evidence_vault.restore_evidence)
            restored_report = restored / "exception-report.csv"
            restored_journal = restored / "exception-report.review.jsonl"
            restored_batch = exception_review.read_cases(restored_report, "grants")
            _check(restored_batch.report_sha256 == batch.report_sha256, "smoke invariant 20")
            _check(exception_review.read_journal(
                restored_journal, restored_batch)[0]["event_hash"] == event["event_hash"], "smoke invariant 21")
        elif app_id == "procurement":
            po = _csv(root, "po.csv", ("po_number", "line", "quantity", "unit_price"), [
                ("P1", "1", "4", "10")])
            invoices = _csv(root, "invoices.csv",
                            ("po_number", "line", "quantity", "unit_price"), [
                ("P1", "1", "5", "10")])
            receipts = _csv(root, "receipts.csv", ("po_number", "line", "quantity"), [
                ("P1", "1", "3")])
            outputs = engine.procure_guard(po, invoices, receipts, str(root))
            status = _rows(outputs[0])[0]["status"]
            _check("invoiced_above_order" in status, "smoke invariant 22")
            _check("invoiced_above_received" in status, "smoke invariant 23")
            _check(len(outputs) == 2, "smoke invariant 24")
            batch = exception_review.read_cases(outputs[0], "procurement")
            _check(batch.cases, "smoke invariant 25")
            journal = root / "procurement-review.jsonl"
            event = exception_review.append_review(
                outputs[0], "procurement", journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="Smoke Reviewer", decision="escalated",
                rationale="Escalate quantity mismatch for supporting evidence.")
            _check(event["decision"] == "escalated", "smoke invariant 26")
            register = exception_review.export_register(
                outputs[0], "procurement", journal, root)
            _check(_rows(register)[0]["review_state"] == "escalated", "smoke invariant 27")
            # A second premium product must include the same secure archive flow.
            passphrase = "Synthetic smoke-only passphrase 2026!"
            sealed = evidence_vault.seal_evidence(
                outputs[0], "procurement", journal, root, passphrase)
            restored = check_scoped_vault_roundtrip(
                sealed, root, passphrase, "procurement", outputs[0],
                journal, evidence_vault.restore_evidence)
            restored_report = restored / "exception-report.csv"
            restored_journal = restored / "exception-report.review.jsonl"
            restored_batch = exception_review.read_cases(restored_report, "procurement")
            _check(restored_batch.report_sha256 == batch.report_sha256, "smoke invariant 28")
            _check(exception_review.read_journal(
                restored_journal, restored_batch)[0]["event_hash"] == event["event_hash"], "smoke invariant 29")
        else:
            raise ValueError("Unsupported application for smoke test: " + app_id)

        _check(outputs and all(path.is_file() and path.stat().st_size > 0 for path in outputs), "smoke invariant 30")
        # Verify *which* reports were generated, not only that some files exist.
        # Premium manifests must occupy their exact final role and extension.
        verify_smoke_output_roles(app_id, outputs)
        return [Path(path.name) for path in outputs]
