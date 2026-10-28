"""End-to-end deterministic checks for each packaged Windows executable.

Invoked with --smoke-test. Uses only temporary synthetic files, no network,
telemetry, external data, GUI, credentials, or production side effects.
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from . import engine, evidence_vault, exception_review


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
            assert {r["id"]: r["status"] for r in rows} == {
                "A": "matched", "B": "variance"}
        elif app_id == "invoices":
            source = _csv(root, "invoices.csv", ("vendor", "invoice_number", "amount", "date"), [
                ("ACME", "INV-100", "200.00", "2026-01-01"),
                ("Acme", "INV-100", "200", "2026-01-02")])
            outputs = engine.invoice_twins(source, str(root))
            assert _rows(outputs[0])[0]["status"] == "exact_invoice_key"
        elif app_id == "spend":
            source = _csv(root, "spend.csv", ("vendor", "amount", "date"), [
                ("ACME", "10", "2026-01-01"), ("ACME", "10", "2026-02-01"),
                ("ACME", "10", "2026-03-01"), ("ACME", "30", "2026-04-01")])
            outputs = engine.spend_map(source, str(root))
            assert _rows(outputs[0])[-1]["flag"] == "review_spike"
        elif app_id == "policy":
            before = root / "before.txt"
            after = root / "after.txt"
            before.write_text("Review within 30 days.\n", encoding="utf-8")
            after.write_text("Review within 15 days.\n", encoding="utf-8")
            outputs = engine.policy_delta(str(before), str(after), str(root))
            diff = outputs[0].read_text(encoding="utf-8")
            assert "-Review within 30 days." in diff
            assert "+Review within 15 days." in diff
        elif app_id == "grants":
            claims = _csv(root, "claims.csv", ("id", "amount", "program"), [
                ("C1", "20", "G1")])
            ledger = _csv(root, "ledger.csv", ("id", "amount", "program"), [
                ("C1", "20", "G1")])
            budget = _csv(root, "budget.csv", ("program", "budget"), [
                ("G1", "10")])
            outputs = engine.grant_audit(claims, ledger, budget, str(root))
            assert len(outputs) == 3
            assert _rows(outputs[1])[0]["status"] == "over_budget_review"
            assert "SHA-256" in outputs[2].read_text(encoding="utf-8")
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
            assert len(outputs) == 3
            assert "split_allocation_review" in details["TX100"]["status"]
            assert details["TX100"]["claim_amount"] == "100.00"
            assert details["TX200"]["net_claim_amount"] == "8.00"
            assert "credit_memo_review" in details["TX200"]["status"]
            summary = {row["program"]: row for row in _rows(outputs[1])}
            assert summary["G1"]["claimed"] == "68.00"
            assert summary["G2"]["claimed"] == "40.00"
            assert "SHA-256" in outputs[2].read_text(encoding="utf-8")
            # Exercise packaged premium human-review code using synthetic data.
            batch = exception_review.read_cases(outputs[0], "grants")
            assert batch.cases
            journal = root / "grant-review.jsonl"
            event = exception_review.append_review(
                outputs[0], "grants", journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="Smoke Reviewer", decision="needs_evidence",
                rationale="Request independent supporting reimbursement evidence.")
            assert event["decision"] == "needs_evidence"
            register = exception_review.export_register(outputs[0], "grants", journal, root)
            assert _rows(register)[0]["review_state"] == "needs_evidence"
            # Validate AES-GCM encrypted evidence backup inside the packaged EXE.
            passphrase = "Synthetic smoke-only passphrase 2026!"
            sealed = evidence_vault.seal_evidence(
                outputs[0], "grants", journal, root, passphrase)
            restored = evidence_vault.restore_evidence(sealed, root, passphrase)
            restored_report = restored / "exception-report.csv"
            restored_journal = restored / "exception-report.review.jsonl"
            restored_batch = exception_review.read_cases(restored_report, "grants")
            assert restored_batch.report_sha256 == batch.report_sha256
            assert exception_review.read_journal(
                restored_journal, restored_batch)[0]["event_hash"] == event["event_hash"]
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
            assert "invoiced_above_order" in status
            assert "invoiced_above_received" in status
            assert len(outputs) == 2
            batch = exception_review.read_cases(outputs[0], "procurement")
            assert batch.cases
            journal = root / "procurement-review.jsonl"
            event = exception_review.append_review(
                outputs[0], "procurement", journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="Smoke Reviewer", decision="escalated",
                rationale="Escalate quantity mismatch for supporting evidence.")
            assert event["decision"] == "escalated"
            register = exception_review.export_register(
                outputs[0], "procurement", journal, root)
            assert _rows(register)[0]["review_state"] == "escalated"
            # A second premium product must include the same secure archive flow.
            passphrase = "Synthetic smoke-only passphrase 2026!"
            sealed = evidence_vault.seal_evidence(
                outputs[0], "procurement", journal, root, passphrase)
            restored = evidence_vault.restore_evidence(sealed, root, passphrase)
            restored_report = restored / "exception-report.csv"
            restored_journal = restored / "exception-report.review.jsonl"
            restored_batch = exception_review.read_cases(restored_report, "procurement")
            assert restored_batch.report_sha256 == batch.report_sha256
            assert exception_review.read_journal(
                restored_journal, restored_batch)[0]["event_hash"] == event["event_hash"]
        else:
            raise ValueError("Unsupported application for smoke test: " + app_id)

        assert outputs and all(path.is_file() and path.stat().st_size > 0 for path in outputs)
        return [Path(path.name) for path in outputs]
