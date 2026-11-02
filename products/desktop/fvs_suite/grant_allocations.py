"""Linked grant reimbursements, split allocations and explicit claim reversals.

Never equate an apparent numeric match with audit approval. This is an offline,
review-only exception engine; a claimed reimbursement is not necessarily eligible.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Context, Decimal, localcontext
from functools import wraps
from pathlib import Path
from typing import Iterable, Mapping

from .review import labels_for_report, normalized_collision
from .grant_input import claim_kind as classify_grant_claim_kind


REPORT_FIELDS = (
    "program", "id", "status", "claim_amount", "ledger_amount", "difference",
    "claim_rows", "ledger_rows", "claim_ids", "ledger_ids",
    "claim_programs", "ledger_programs", "gross_claim_amount",
    "credit_amount", "net_claim_amount", "ledger_reference_labels",
    "allocation_count", "allocation_program_count", "claim_types",
    "related_claim_ids", "claim_lineage",
)
BUDGET_FIELDS = (
    "program", "claimed", "budget", "status", "source_programs",
    "gross_claimed", "credit_total", "claim_rows", "budget_rows",
    "claim_source_sha256", "ledger_source_sha256", "budget_source_sha256",
)


def _unique_flags(flags: Iterable[str]) -> str:
    return ";".join(dict.fromkeys(flags)) or "matched"


def _as_positive_money(raw: str, *, engine, row: str, field: str) -> Decimal:
    amount = engine.money(raw)
    if amount < 0:
        remedy = "use claim_type=credit for a reversal" if field == "amount" else "provide a nonnegative authorized budget"
        raise ValueError(
            f"Linked grant {field} in CSV row {row} must be nonnegative; {remedy}")
    return amount


def _claim_kind(row: Mapping[str, str]) -> str:
    # Preserve the internal helper entry point, but never echo private source cells.
    return classify_grant_claim_kind(row)


def _parse_claims(claim_rows: list[dict[str, str]], engine):
    """Validate *all* linked allocations before any report is written."""
    refs = defaultdict(list)
    claim_id_counter: Counter[str] = Counter()
    raw_claim_id_labels = defaultdict(set)
    for row in claim_rows:
        for field in ("id", "program", "ledger_reference"):
            if not engine.key(row.get(field, "")):
                raise ValueError(f"Missing {field} at claim CSV row {row['row']}")
        amount = _as_positive_money(row["amount"], engine=engine, row=row["row"], field="amount")
        kind = _claim_kind(row)
        if kind == "credit" and not engine.key(row.get("related_claim", "")):
            raise ValueError(
                f"Credit at claim CSV row {row['row']} must specify related_claim")
        if kind == "claim" and row.get("related_claim", "").strip():
            raise ValueError(
                f"Claim at claim CSV row {row['row']} must not specify related_claim")
        copy = dict(row, _kind=kind, _amount=amount)
        refs[engine.key(row["ledger_reference"])].append(copy)
        normalized_id = engine.key(row["id"])
        claim_id_counter[normalized_id] += 1
        raw_claim_id_labels[normalized_id].add(row["id"].casefold())
    return refs, claim_id_counter, raw_claim_id_labels


def _validate_ledger(rows: list[dict[str, str]], engine):
    grouped = defaultdict(list)
    for row in rows:
        reference = engine.key(row["id"])
        if not reference:
            raise ValueError(f"Missing ledger ID at ledger CSV row {row['row']}")
        entry = dict(row, _amount=engine.money(row["amount"]))
        grouped[reference].append(entry)
    return grouped


def _exact_linked_grant_context(operation):
    """Keep direct linked-grant API calls independent of ambient Decimal state."""
    @wraps(operation)
    def guarded(*args, **kwargs):
        # 200k bounded source rows at <= 1 trillion each fit exactly in
        # 64 significant digits, including cents and gross/credit totals.
        with localcontext(Context(prec=64)):
            return operation(*args, **kwargs)
    return guarded


@_exact_linked_grant_context
def reconcile_allocations(
    claims: str, ledger: str, budgets: str, folder: str,
    *, claim_rows: list[dict[str, str]] | None = None,
    claim_digest: str | None = None,
) -> list[Path]:
    """Join claim lines via explicit ledger_reference across distinct programs.

    Three output files preserve the legacy return contract: exceptions, budgets,
    SHA256 evidence manifest. Every split and credit stays visibly reviewable.
    """
    from . import engine

    if not Path(folder).is_dir():
        raise ValueError("Choose an existing output folder")
    if claim_rows is None:
        claim_rows, claim_digest = engine.table(
            claims, ("id", "amount", "program"),
            ("ledger_reference", "claim_type", "related_claim"), include_digest=True)
    elif claim_digest is None:
        # A caller must not inject unproven claim records into an evidence manifest.
        raise ValueError("Linked claim rows require source-byte provenance")
    if any("ledger_reference" not in row for row in claim_rows):
        raise ValueError("Linked claim rows require a ledger_reference column")
    ledger_rows, ledger_digest = engine.table(
        ledger, ("id", "amount", "program"), include_digest=True)
    budget_rows, budget_digest = engine.table(
        budgets, ("program", "budget"), include_digest=True)
    by_ref, claim_id_counts, raw_claim_id_labels = _parse_claims(claim_rows, engine)
    ledgers = _validate_ledger(ledger_rows, engine)

    limits: dict[str, Decimal] = {}
    budget_rows_by_program: dict[str, str] = {}
    program_sources = defaultdict(list)
    for source in (claim_rows, ledger_rows, budget_rows):
        for row in source:
            name = engine.key(row.get("program", ""))
            if name:
                program_sources[name].append(row)
    for row in budget_rows:
        program = engine.key(row["program"])
        if not program or program in limits:
            raise ValueError("Blank or duplicate budget program at row " + row["row"])
        limits[program] = _as_positive_money(
            row["budget"], engine=engine, row=row["row"], field="budget")
        budget_rows_by_program[program] = row["row"]

    program_gross = defaultdict(lambda: Decimal(0))
    program_credits = defaultdict(lambda: Decimal(0))
    program_rows = defaultdict(list)
    report = []
    for ledger_id in sorted(set(by_ref) | set(ledgers)):
        allocated = by_ref[ledger_id]
        source_ledger = ledgers[ledger_id]
        flags: list[str] = []
        if not allocated:
            flags.append("missing_claim")
        if not source_ledger:
            flags.append("missing_ledger")
        if len(source_ledger) > 1:
            flags.append("duplicate_ledger_id_review")
        if normalized_collision([*allocated, *source_ledger], "id") and not allocated:
            # Duplicate ledger rows can themselves carry punctuation-collided IDs.
            flags.append("normalized_ledger_id_review")
        refs = {row["ledger_reference"].casefold() for row in allocated}
        source_ids = {row["id"].casefold() for row in source_ledger}
        if len(refs | source_ids) > 1:
            flags.append("normalized_ledger_reference_review")

        claim_programs = {engine.key(row["program"]) for row in allocated}
        if len(claim_programs) > 1:
            flags.append("split_allocation_review")
        if len(claim_programs) == 1 and source_ledger:
            ledger_programs = {engine.key(row["program"]) for row in source_ledger if row["program"].strip()}
            if ledger_programs and ledger_programs != claim_programs:
                flags.append("program_mismatch_review")
            elif engine.normalized_collision([*allocated, *source_ledger], "program"):
                flags.append("normalized_program_review")
        if len(claim_programs) > 1 and source_ledger:
            # Ledger's program is accounting context, not evidence of allocation.
            flags.append("ledger_program_context_review")

        original_ids = {engine.key(row["id"]) for row in allocated if row["_kind"] == "claim"}
        original_raw = {row["id"].casefold() for row in allocated if row["_kind"] == "claim"}
        original_programs = defaultdict(set)
        for original in allocated:
            if original["_kind"] == "claim":
                original_programs[engine.key(original["id"])].add(engine.key(original["program"]))
        credits_by_parent = defaultdict(lambda: Decimal(0))
        gross_by_parent = defaultdict(lambda: Decimal(0))
        for row in allocated:
            if claim_id_counts[engine.key(row["id"])] > 1:
                flags.append("repeated_claim_id_review")
            if len(raw_claim_id_labels[engine.key(row["id"])]) > 1:
                flags.append("normalized_claim_id_review")
            amount = row["_amount"]
            if amount == 0:
                flags.append("zero_claim_amount_review")
            program = engine.key(row["program"])
            program_rows[program].append(row)
            if row["_kind"] == "claim":
                program_gross[program] += amount
                gross_by_parent[engine.key(row["id"])] += amount
            else:
                program_credits[program] += amount
                flags.append("credit_memo_review")
                parent_id = engine.key(row["related_claim"])
                credits_by_parent[parent_id] += amount
                if parent_id not in original_ids:
                    flags.append("unlinked_credit_review")
                else:
                    if row["related_claim"].casefold() not in original_raw:
                        flags.append("normalized_credit_link_review")
                    if program not in original_programs[parent_id]:
                        flags.append("cross_program_credit_review")
        if any(amount > gross_by_parent.get(parent_id, Decimal(0))
               for parent_id, amount in credits_by_parent.items()):
            flags.append("credit_exceeds_claim_review")

        gross = sum((r["_amount"] for r in allocated if r["_kind"] == "claim"), Decimal(0))
        credits = sum((r["_amount"] for r in allocated if r["_kind"] == "credit"), Decimal(0))
        net = gross - credits
        if credits > gross:
            flags.append("credit_exceeds_gross_review")
        ledger_total = sum((r["_amount"] for r in source_ledger), Decimal(0))
        if allocated and source_ledger and net != ledger_total:
            flags.append("variance")
            if net >= 0 and net < ledger_total:
                flags.append("partial_allocation_review")
        claim_lineage = " | ".join(
            f"row={r['row']}:id={r['id']}:program={r['program']}:type={r['_kind']}:amount={engine.dollars(r['_amount'])}"
            for r in allocated)
        fallback_programs = {engine.key(r["program"]) for r in source_ledger if r["program"].strip()}
        report.append({
            "program": ";".join(sorted(claim_programs or fallback_programs)),
            "id": ledger_id, "status": _unique_flags(flags),
            "claim_amount": engine.dollars(net),
            "ledger_amount": engine.dollars(ledger_total),
            "difference": engine.dollars(net-ledger_total),
            "claim_rows": ";".join(r["row"] for r in allocated),
            "ledger_rows": ";".join(r["row"] for r in source_ledger),
            "claim_ids": labels_for_report(allocated, "id"),
            "ledger_ids": labels_for_report(source_ledger, "id"),
            "claim_programs": labels_for_report(allocated, "program"),
            "ledger_programs": labels_for_report(source_ledger, "program"),
            "gross_claim_amount": engine.dollars(gross),
            "credit_amount": engine.dollars(credits),
            "net_claim_amount": engine.dollars(net),
            "ledger_reference_labels": labels_for_report(allocated, "ledger_reference"),
            "allocation_count": str(len(allocated)),
            "allocation_program_count": str(len(claim_programs)),
            "claim_types": ";".join(sorted({r["_kind"] for r in allocated})),
            "related_claim_ids": labels_for_report(allocated, "related_claim"),
            "claim_lineage": claim_lineage,
        })

    summaries = []
    for program in sorted(set(limits) | set(program_gross) | set(program_credits)):
        gross = program_gross[program]
        credits = program_credits[program]
        net = gross - credits
        limit = limits.get(program)
        flags = []
        if normalized_collision(program_sources[program], "program"):
            flags.append("normalized_budget_program_review")
        if limit is None:
            flags.append("missing_budget")
        elif net > limit:
            flags.append("over_budget_review")
        else:
            flags.append("within_budget")
        if credits:
            flags.append("credit_memo_review")
        if credits > gross:
            flags.append("credit_exceeds_gross_review")
        summaries.append({
            "program": program, "claimed": engine.dollars(net),
            "budget": "" if limit is None else engine.dollars(limit),
            "status": ";".join(flags),
            "source_programs": labels_for_report(program_sources[program], "program"),
            "gross_claimed": engine.dollars(gross),
            "credit_total": engine.dollars(credits),
            "claim_rows": ";".join(r["row"] for r in program_rows[program]),
            "budget_rows": budget_rows_by_program.get(program, ""),
            "claim_source_sha256": claim_digest,
            "ledger_source_sha256": ledger_digest,
            "budget_source_sha256": budget_digest,
        })

    from .grant_bundle import publish_grant_bundle
    def build(staging):
        files = [
            engine.save(staging, "grant-audit-exceptions", REPORT_FIELDS, report),
            engine.save(staging, "grant-budget-check", BUDGET_FIELDS, summaries),
        ]
        return files + [engine.manifest(
            staging, [claims, ledger, budgets], files,
            expected_inputs={claims: claim_digest, ledger: ledger_digest,
                             budgets: budget_digest})]
    return publish_grant_bundle(folder,build)
