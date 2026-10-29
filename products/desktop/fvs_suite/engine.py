"""Local-first Final Vestige Labs desktop engines. All findings require human review."""
from __future__ import annotations
import csv, difflib, hashlib, os, re, statistics
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from .review import labels_for_report, normalized_collision, price_exceeds_tolerance, reconciliation_status
from .invoice_match import candidate_pairs, review_flags as invoice_review_flags

ALIASES = {
 "id": ("transaction_id","id","reference","ref","document_id","claim_id"),
 "amount": ("amount","total","paid","claim_amount","invoice_amount"),
 "vendor": ("vendor","supplier","vendor_name","supplier_name","payee"),
 "invoice_number": ("invoice_number","invoice_no","invoice_id","invoice","inv_no"),
 "date": ("date","invoice_date","transaction_date","payment_date"),
 "category": ("category","spend_category","expense_type"),
 "program": ("program","grant","grant_id","project","project_code"),
 "budget": ("budget","authorized_budget","approved_budget","award_amount"),
 "po_number": ("po_number","po","purchase_order","purchase_order_number"),
 "line": ("line","line_number","po_line","item"),
 "quantity": ("quantity","qty","received_qty","invoiced_qty"),
 "unit_price": ("unit_price","price","unit_cost"),
 "event_type": ("event_type","transaction_type","movement_type"),
 "document_id": ("document_id","invoice_number","invoice_id","receipt_number","credit_memo_id"),
 "related_document": ("related_document","applies_to","original_invoice","related_invoice"),
 "ledger_reference": ("ledger_reference","ledger_ref","source_transaction_id"),
 "claim_type": ("claim_type","allocation_type"),
 "related_claim": ("related_claim","original_claim_id","reverses_claim_id"),
}
MAX_ROWS = 200_000
# Bound user-provided exports before parsing (premium review reports use the same cap).
MAX_IMPORT_BYTES = 64 * 1024 * 1024
CENT = Decimal("0.01")

_AMOUNT_FORMAT = re.compile(
    r"(?P<prefix>(?:[+-]?\$|\$[+-]?|[+-]?))"
    r"(?P<number>(?:(?:[0-9]{1,3}(?:,[0-9]{3})+)|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)\Z"
)


def _exact_amount(value):
    """Parse accounting amounts without silently deleting punctuation.

    Accept conventional signed or parenthesized negatives, optional leading
    currency symbol, and correctly grouped thousands. Reject mixed signs,
    malformed grouping, scientific notation, and partial parentheses.
    """
    if isinstance(value, (float, bool)):
        raise ValueError("Invalid amount format")
    raw = str(value).strip()
    if not raw or len(raw) > 80:
        raise ValueError("Invalid amount format")
    parenthesized = raw.startswith("(") or raw.endswith(")")
    if parenthesized:
        if not (raw.startswith("(") and raw.endswith(")")):
            raise ValueError("Invalid amount format: unmatched accounting parentheses")
        raw = raw[1:-1].strip()
    match = _AMOUNT_FORMAT.fullmatch(raw)
    if match is None:
        raise ValueError("Invalid amount format")
    prefix = match.group("prefix")
    if parenthesized and ("+" in prefix or "-" in prefix):
        raise ValueError("Invalid amount format: conflicting signs")
    try:
        number = Decimal(match.group("number").replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError("Invalid amount format") from exc
    if not number.is_finite() or number > Decimal("1000000000000"):
        raise ValueError("Nonfinite or out-of-range amount")
    return -number if parenthesized or "-" in prefix else number


def money(value):
    return _exact_amount(value).quantize(CENT, rounding=ROUND_HALF_UP)


def unit_cost(value):
    """Unit prices may carry sub-cent precision; totals round only on display."""
    amount = _exact_amount(value)
    if amount.normalize().as_tuple().exponent < -8:
        raise ValueError("Unit price precision exceeds eight decimal places")
    return amount

_QUANTITY_FORMAT = re.compile(
    r"[+]?(?:(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)\Z"
)


def qty(value):
    """Parse exact, nonnegative quantities without deleting misplaced commas.

    Reject exponent forms, mixed punctuation, excessive precision, and binary
    floats; these change the interpretation of invoice/receipt movements.
    """
    if isinstance(value, (float, bool)):
        raise ValueError("Invalid quantity format")
    raw = str(value).strip()
    if not raw or len(raw) > 80 or _QUANTITY_FORMAT.fullmatch(raw) is None:
        raise ValueError("Invalid quantity format")
    try:
        number = Decimal(raw.replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError("Invalid quantity format") from exc
    if not number.is_finite() or number < 0 or number > Decimal("1000000000"):
        raise ValueError("Invalid quantity range")
    if number.normalize().as_tuple().exponent < -8:
        raise ValueError("Quantity precision exceeds eight decimal places")
    return number

def key(value): return re.sub(r"[^A-Z0-9]+","",str(value).upper())
def dollars(value): return format(value.quantize(CENT),".2f")
_DATE_FORMATS = (
    (re.compile(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}\Z"), "%Y-%m-%d"),
    (re.compile(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}\Z"), "%m/%d/%Y"),
    (re.compile(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}\Z"), "%m/%d/%y"),
)

def parse_date(value):
    """Validate exact ASCII calendar text; never echo private input on failure."""
    raw = str(value).strip()
    if not raw or len(raw) > 32:
        raise ValueError("Invalid date (use YYYY-MM-DD, MM/DD/YYYY, or MM/DD/YY)")
    for pattern, fmt in _DATE_FORMATS:
        if pattern.fullmatch(raw):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                break
    raise ValueError("Invalid date (use YYYY-MM-DD, MM/DD/YYYY, or MM/DD/YY)")

def table(path, required, optional=()):
    p = Path(path)
    if p.suffix.lower() != ".csv" or not p.is_file(): raise ValueError("Select an existing CSV: "+p.name)
    with p.open(encoding="utf-8-sig",newline="") as f:
        # Inspect the opened descriptor, not a potentially substituted pathname.
        if os.fstat(f.fileno()).st_size > MAX_IMPORT_BYTES:
            raise ValueError("CSV input exceeds 64 MiB file-size limit")
        # csv.reader exposes physical line counts after each complete record.
        # DictReader's enumerate() only counts logical records, and gives
        # incorrect audit citations after quoted newlines or blank lines.
        reader = csv.reader(f, strict=True)
        try:
            fieldnames = next(reader, None)
        except (csv.Error, UnicodeError) as exc:
            raise ValueError(f"{p.name}: invalid CSV header") from exc
        if not fieldnames: raise ValueError("Missing headers: "+p.name)
        if any("\x00" in name for name in fieldnames):
            raise ValueError(f"{p.name}: CSV header contains a NUL character")
        normalized = [str(h).strip().lower().replace(" ", "_") for h in fieldnames if h]
        if "" in normalized or len(normalized) != len(fieldnames) or len(normalized) != len(set(normalized)):
            raise ValueError(f"{p.name}: blank or duplicate normalized CSV header")
        headers = dict(zip(normalized, fieldnames))
        cols = {}
        for field in (*required,*optional):
            matches = [alias for alias in ALIASES.get(field,(field,)) if alias in headers]
            if len(matches) > 1:
                raise ValueError(f"{p.name}: ambiguous '{field}' aliases: {', '.join(matches)}")
            cols[field] = headers[matches[0]] if matches else None
            if field in required and cols[field] is None:
                raise ValueError(f"{p.name}: missing '{field}' column")
        out = []
        previous_end_line = reader.line_num
        row_count = 0
        try:
            for values in reader:
                # Count physical start lines, not the ordinal of parsed records.
                source_line = previous_end_line + 1
                previous_end_line = reader.line_num
                if not values:  # csv.DictReader historically skips blank lines.
                    continue
                row_count += 1
                if row_count > MAX_ROWS: raise ValueError("CSV exceeds 200,000 rows")
                if len(values) != len(fieldnames):
                    raise ValueError(f"{p.name}: malformed CSV record at physical line {source_line} "
                                     f"(expected {len(fieldnames)} columns, got {len(values)})")
                # Even an ignored, extra data column must not smuggle NUL bytes
                # into an evidence-bearing financial import.
                if any("\x00" in cell for cell in values):
                    raise ValueError(f"{p.name}: CSV record contains a NUL character "
                                     f"at physical line {source_line}")
                row = dict(zip(fieldnames, values))
                out.append({"row":str(source_line),**{name:str(row.get(col) or "").strip()
                       for name,col in cols.items() if col}})
        except (csv.Error, UnicodeError) as exc:
            raise ValueError(f"{p.name}: invalid CSV near physical line {reader.line_num}") from exc
        # Fail closed if another local process expanded the file during import.
        if os.fstat(f.fileno()).st_size > MAX_IMPORT_BYTES:
            raise ValueError("CSV input exceeds 64 MiB file-size limit")
        return out

def outpath(folder,stem,suffix=".csv"):
    p=Path(folder)
    if not p.is_dir(): raise ValueError("Choose an existing output folder")
    return p/(stem+"-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f")+suffix)

def safe_cell(value):
    """Neutralize spreadsheet formulas in user-controlled text fields."""
    s=str(value)
    trimmed=s.lstrip()
    if trimmed.startswith(("=","+","@","\t","\r","\n")) or (trimmed.startswith("-") and not re.fullmatch(r"-[0-9]+(?:\.[0-9]+)?",trimmed)):
        return "\x27"+s
    return s

def save(folder,stem,fields,rows):
    """Stage and sync complete CSV bytes before exposing a final report path."""
    from .atomic_reports import write_csv_report
    return write_csv_report(outpath(folder,stem), fields, rows, safe_cell)

def manifest(folder,inputs,outputs):
    """Publish private grant evidence inventory only after source verification.

    Reject duplicate basenames, links and files that change during hashing.
    Inventory bytes remain descriptive, not eligibility/approval evidence.
    """
    from .atomic_text import publish_text
    from .manifest_guard import inventory_text
    contents = inventory_text(inputs, outputs)
    return publish_text(outpath(folder,"evidence-manifest",".txt"), contents)

def ledger_diff(left,right,folder):
    groups=[defaultdict(list),defaultdict(list)]
    for source,d in ((left,groups[0]),(right,groups[1])):
        for r in table(source,("id","amount")):
            k=key(r["id"])
            if not k: raise ValueError(f"Blank transaction ID in {Path(source).name}, row {r['row']}")
            d[k].append(r)
    rows=[]
    for k in sorted(set(groups[0])|set(groups[1])):
        a,b=groups[0][k],groups[1][k]
        x=sum((money(r["amount"]) for r in a),Decimal(0))
        y=sum((money(r["amount"]) for r in b),Decimal(0))
        status=reconciliation_status(
            a,b,x,y,missing_left="missing_left",missing_right="missing_right")
        rows.append({"id":k,"status":status,"left_amount":dollars(x),"right_amount":dollars(y),
                     "difference":dollars(x-y),"left_rows":";".join(r["row"] for r in a),
                     "right_rows":";".join(r["row"] for r in b),
                     "left_ids":labels_for_report(a,"id"),
                     "right_ids":labels_for_report(b,"id")})
    return [save(folder,"ledger-diff",("id","status","left_amount","right_amount","difference","left_rows","right_rows","left_ids","right_ids"),rows)]

def invoice_twins(source,folder):
    """Produce a bounded, provenance-rich review report without internet access.

    Date-window scanning is chronological rather than all-history quadratic.
    The output is never partial: excess candidate density raises ValueError
    before creating a report. Findings are possible duplicates, not fraud.
    """
    records=table(source,("vendor","invoice_number","amount","date"))
    for r in records:
        r["v"]=key(r["vendor"])
        r["inv"]=key(r["invoice_number"])
        r["amt"]=money(r["amount"])
        r["dt"]=parse_date(r["date"])
        if not r["v"] or not r["inv"]:
            raise ValueError("Blank vendor/invoice at row "+r["row"])
    rows=[]
    for a,b,status,reason in candidate_pairs(records):
        rows.append({
            "row_a":a["row"],"row_b":b["row"],"status":status,
            "vendor":a["vendor"],"invoice_a":a["invoice_number"],
            "invoice_b":b["invoice_number"],
            "amount_a":dollars(a["amt"]),"amount_b":dollars(b["amt"]),
            "reason":reason,"vendor_b":b["vendor"],
            "date_a":a["dt"].isoformat(),"date_b":b["dt"].isoformat(),
            "review_flags":invoice_review_flags(a,b,status)
        })
    return [save(folder,"invoice-twins",(
        "row_a","row_b","status","vendor","invoice_a","invoice_b",
        "amount_a","amount_b","reason","vendor_b","date_a","date_b","review_flags"
    ),rows)]

def spend_map(source,folder):
    records=table(source,("vendor","amount","date"),("category",))
    grouped=defaultdict(lambda:Decimal(0))
    for r in records:
        vendor=key(r["vendor"])
        if not vendor: raise ValueError("Blank vendor at row "+r["row"])
        month=parse_date(r["date"]).strftime("%Y-%m")
        grouped[(vendor,month,r.get("category","Uncategorized") or "Uncategorized")]+=money(r["amount"])
    totals=defaultdict(lambda:defaultdict(lambda:Decimal(0)))
    for (vendor,month,category),amount in grouped.items():totals[vendor][month]+=amount
    flags={}
    for vendor,months in totals.items():
        history=[]
        for month,amount in sorted(months.items()):
            baseline=Decimal(str(statistics.median(history))) if len(history)>=3 else None
            flags[(vendor,month)]="review_spike" if baseline and baseline>0 and amount>=2*baseline else ""
            history.append(amount)
    rows=[{"vendor_key":v,"month":m,"category":c,"amount":dollars(a),"flag":flags[(v,m)]}
          for (v,m,c),a in sorted(grouped.items())]
    return [save(folder,"spend-map",("vendor_key","month","category","amount","flag"),rows)]

def policy_delta(old,new,folder):
    """Compare two bounded local policy files with source-byte provenance."""
    from .policy_diff import compare_policy_files
    return compare_policy_files(old, new, folder, outpath)

def grant_audit(claims,ledger,budgets,folder):
    """Legacy one-to-one reconciliation or explicit linked allocations.

    A claim_type/related_claim column without ledger_reference is an error:
    otherwise old logic would silently count credits as positive claims.
    """
    claims_rows=table(claims,("id","amount","program"),
                      ("ledger_reference","claim_type","related_claim"))
    with Path(claims).open(encoding="utf-8-sig",newline="") as stream:
        fields={str(h).strip().lower().replace(" ","_")
                for h in next(csv.reader(stream),[])}
    has_link=bool(fields & set(ALIASES["ledger_reference"]))
    advanced=bool(fields & set((*ALIASES["claim_type"],*ALIASES["related_claim"])))
    if advanced and not has_link:
        raise ValueError("Grant claim_type/related_claim requires ledger_reference; "
                         "legacy mode cannot safely interpret credits")
    if has_link:
        from .grant_allocations import reconcile_allocations
        return reconcile_allocations(claims,ledger,budgets,folder,claim_rows=claims_rows)
    ledger_rows=table(ledger,("id","amount","program"))
    budget_rows=table(budgets,("program","budget"))
    program_sources=defaultdict(list)
    for source_rows in (claims_rows,ledger_rows,budget_rows):
        for entry in source_rows:
            program_sources[key(entry["program"])].append(entry)
    grouped=[defaultdict(list),defaultdict(list)]
    for rows,d in ((claims_rows,grouped[0]),(ledger_rows,grouped[1])):
        for r in rows:
            k=(key(r["program"]),key(r["id"]))
            if not all(k):raise ValueError("Blank program or ID at row "+r["row"])
            d[k].append(r)
    checks=[];claimed=defaultdict(lambda:Decimal(0))
    for (program,id_) in sorted(set(grouped[0])|set(grouped[1])):
        a,b=grouped[0][(program,id_)],grouped[1][(program,id_)]
        x=sum((money(r["amount"]) for r in a),Decimal(0))
        y=sum((money(r["amount"]) for r in b),Decimal(0))
        claimed[program]+=x
        status=reconciliation_status(
            a,b,x,y,missing_left="missing_claim",missing_right="missing_ledger",
            fields=(("id","normalized_id_review"),("program","normalized_program_review")))
        checks.append({"program":program,"id":id_,"status":status,"claim_amount":dollars(x),
                       "ledger_amount":dollars(y),"difference":dollars(x-y),
                       "claim_rows":";".join(r["row"] for r in a),
                       "ledger_rows":";".join(r["row"] for r in b),
                       "claim_ids":labels_for_report(a,"id"),
                       "ledger_ids":labels_for_report(b,"id"),
                       "claim_programs":labels_for_report(a,"program"),
                       "ledger_programs":labels_for_report(b,"program")})
    limits={}
    for r in budget_rows:
        program=key(r["program"])
        if not program or program in limits:raise ValueError("Blank/duplicate budget program at row "+r["row"])
        limits[program]=money(r["budget"])
    budget_checks=[]
    for program in sorted(set(limits)|set(claimed)):
        total=claimed[program];limit=limits.get(program)
        status="missing_budget" if limit is None else "over_budget_review" if total>limit else "within_budget"
        if normalized_collision(program_sources[program],"program"):
            status="normalized_budget_program_review;"+status
        budget_checks.append({"program":program,"claimed":dollars(total),
                              "budget":"" if limit is None else dollars(limit),"status":status,
                              "source_programs":labels_for_report(program_sources[program],"program")})
    paths=[save(folder,"grant-audit-exceptions",("program","id","status","claim_amount","ledger_amount","difference","claim_rows","ledger_rows","claim_ids","ledger_ids","claim_programs","ledger_programs"),checks),
           save(folder,"grant-budget-check",("program","claimed","budget","status","source_programs"),budget_checks)]
    return paths+[manifest(folder,[claims,ledger,budgets],paths)]

def procure_guard(po,invoices,receipts,folder,policy_path=None):
    """Run the conservative, typed, traceable offline three-way review.

    Optional JSON policy changes only review thresholds, never authorizes payments.
    """
    from .procurement import reconcile_procurement
    return reconcile_procurement(po,invoices,receipts,folder,policy_path=policy_path)
