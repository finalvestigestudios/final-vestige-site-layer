"""Local-first Final Vestige Labs desktop engines. All findings require human review."""
from __future__ import annotations
import csv, difflib, hashlib, os, re, statistics, unicodedata
from collections import defaultdict
from datetime import datetime, date
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from functools import wraps
from pathlib import Path

from .review import labels_for_report, normalized_collision, price_exceeds_tolerance, reconciliation_status
from .audit_display import _escape_source_character
from .csv_diagnostics import csv_input_error
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
    return number.copy_negate() if parenthesized or "-" in prefix else number


def _fractional_places(value: Decimal) -> int:
    """Exact significant fractional scale, ignoring permitted trailing zeroes.

    Decimal.normalize() rounds using the ambient context; a hostile low
    precision could erase the ninth fractional digit before validation.
    """
    digits = value.as_tuple().digits
    exponent = value.as_tuple().exponent
    if exponent >= 0 or not any(digits):
        return 0
    trailing_zeroes = 0
    for digit in reversed(digits):
        if digit != 0:
            break
        trailing_zeroes += 1
    return max(0, -exponent - trailing_zeroes)


def _cent_value(value: Decimal) -> Decimal:
    """Round bounded suite money with a fresh independent Decimal context."""
    # A 200,000-row import at up to 1 trillion per row has <= 20
    # integer digits. 64 digits retains cents, and avoids caller traps.
    with localcontext(Context(prec=64)):
        return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _exact_reconciliation_context(operation):
    """Protect ledger/grant aggregation against caller precision and traps."""
    @wraps(operation)
    def guarded(*args, **kwargs):
        with localcontext(Context(prec=64)):
            return operation(*args, **kwargs)
    return guarded


def money(value):
    return _cent_value(_exact_amount(value))


def unit_cost(value):
    """Unit prices may carry sub-cent precision; totals round only on display."""
    amount = _exact_amount(value)
    if _fractional_places(amount) > 8:
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
    if _fractional_places(number) > 8:
        raise ValueError("Quantity precision exceeds eight decimal places")
    return number

def key(value): return re.sub(r"[^A-Z0-9]+","",str(value).upper())
def dollars(value): return format(_cent_value(value), ".2f")
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

def table(path, required, optional=(), *, include_headers=False, include_digest=False,
          id_column=None, amount_column=None, include_columns=False):
    # Explicit LedgerDiff identity/amount mappings are opt-in; only the
    # LedgerDiff caller supplies them, preserving other engines' contracts.
    # Normalize exactly like imported CSV headers; reject unbounded, unsafe
    # or visually ambiguous names without reflecting private input values.
    override_id = None
    override_amount = None
    if id_column is not None:
        if type(id_column) is not str or "id" not in required:
            raise ValueError("Invalid explicit ledger match column")
        override_id = id_column.strip().lower().replace(" ", "_")
        if re.fullmatch(r"[a-z_][a-z0-9_]{0,127}", override_id) is None:
            raise ValueError("Invalid explicit ledger match column")
    if amount_column is not None:
        if type(amount_column) is not str or "amount" not in required:
            raise ValueError("Invalid explicit ledger amount column")
        override_amount = amount_column.strip().lower().replace(" ", "_")
        if re.fullmatch(r"[a-z_][a-z0-9_]{0,127}", override_amount) is None:
            raise ValueError("Invalid explicit ledger amount column")
    p = Path(path)
    if p.suffix.lower() != ".csv" or not p.is_file(): raise csv_input_error("select_file")
    # Parse a verified single-descriptor snapshot: no source can change between
    # CSV header and row parsing, and symlinks/path swaps fail closed.
    from io import BytesIO, TextIOWrapper
    from .csv_snapshot import read_csv_snapshot
    source_bytes = read_csv_snapshot(p, MAX_IMPORT_BYTES)
    with TextIOWrapper(BytesIO(source_bytes), encoding="utf-8-sig", newline="") as f:
        # csv.reader exposes physical line counts after each complete record.
        # DictReader's enumerate() only counts logical records, and gives
        # incorrect audit citations after quoted newlines or blank lines.
        reader = csv.reader(f, strict=True)
        try:
            fieldnames = next(reader, None)
        except (csv.Error, UnicodeError) as exc:
            raise csv_input_error("bad_header") from None
        if not fieldnames: raise csv_input_error("missing_headers")
        if any("\x00" in name for name in fieldnames):
            raise csv_input_error("nul_header")
        normalized = [str(h).strip().lower().replace(" ", "_") for h in fieldnames if h]
        if "" in normalized or len(normalized) != len(fieldnames) or len(normalized) != len(set(normalized)):
            raise csv_input_error("duplicate_header")
        headers = dict(zip(normalized, fieldnames))
        cols = {}
        for field in (*required,*optional):
            if field == "id" and override_id is not None:
                matches = [override_id] if override_id in headers else []
            elif field == "amount" and override_amount is not None:
                matches = [override_amount] if override_amount in headers else []
            else:
                matches = [alias for alias in ALIASES.get(field,(field,)) if alias in headers]
            if len(matches) > 1:
                raise csv_input_error("alias_ambiguous", field=field)
            cols[field] = headers[matches[0]] if matches else None
            if field in required and cols[field] is None:
                raise csv_input_error("column_missing", field=field)
        # Scope this new restriction to explicit LedgerDiff mappings; other
        # applications retain their pre-existing alias resolution contract.
        # Identity and amount cannot both reference the same physical column.
        if (override_id is not None or override_amount is not None) and cols.get("id") == cols.get("amount"):
            raise ValueError("Ledger match and amount must use distinct CSV columns")
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
                    raise csv_input_error("bad_row_shape", line=source_line,
                                          expected=len(fieldnames), actual=len(values))
                # Even an ignored, extra data column must not smuggle NUL bytes
                # into an evidence-bearing financial import.
                if any("\x00" in cell for cell in values):
                    raise csv_input_error("nul_record", line=source_line)
                row = dict(zip(fieldnames, values))
                out.append({"row":str(source_line),**{name:str(row.get(col) or "").strip()
                       for name,col in cols.items() if col}})
        except (csv.Error, UnicodeError) as exc:
            raise csv_input_error("bad_record", line=reader.line_num) from None
        # Hash precisely the bytes already parsed, not a later path read.
        # The caller can bind this value to a later evidence inventory.
        # Existing tuple return contracts remain unchanged for all callers.
        # The new optional selection map records the actual imported header
        # for each logical field, so mapping choices remain reviewable.
        details = []
        if include_headers:
            details.append(set(normalized))
        if include_digest:
            details.append(hashlib.sha256(source_bytes).hexdigest())
        if include_columns:
            details.append(dict(cols))
        return (out, *details) if details else out

def outpath(folder,stem,suffix=".csv"):
    p=Path(folder)
    if not p.is_dir(): raise ValueError("Choose an existing output folder")
    return p/(stem+"-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f")+suffix)

def safe_cell(value):
    """Conservatively neutralize spreadsheet formulas behind invisible prefixes.

    Spreadsheet importers can ignore leading format, bidi, control, combining
    or exotic whitespace characters that Python str.lstrip() does not.
    Quote ALL labels with such a leading character, even benign labels.
    Ordinary ASCII-space prefixes and exact negative decimals remain intact.
    The original input SHA and source rows remain the audit authority.
    """
    s = str(value)
    index = 0
    invisible_prefix = False
    while index < len(s):
        character = s[index]
        if character == " ":
            index += 1
            continue
        if (character.isspace() or _escape_source_character(character)
                or unicodedata.category(character) in ("Mn", "Me")):
            invisible_prefix = True
            index += 1
            continue
        break
    token = s[index:]
    if (invisible_prefix or token.startswith(("=", "+", "@"))
            or (token.startswith("-") and
                re.fullmatch(r"-[0-9]+(?:\.[0-9]+)?", token) is None)):
        return "'" + s
    return s

def save(folder,stem,fields,rows):
    """Stage and sync complete CSV bytes before exposing a final report path."""
    from .atomic_reports import write_csv_report
    return write_csv_report(outpath(folder,stem), fields, rows, safe_cell)

def manifest(folder,inputs,outputs, *, expected_inputs=None):
    """Publish private grant evidence inventory only after source verification.

    Reject duplicate basenames, links and files that change during hashing.
    Inventory bytes remain descriptive, not eligibility/approval evidence.
    """
    from .atomic_text import publish_text
    from .manifest_guard import inventory_text
    contents = inventory_text(inputs, outputs, expected_input_digests=expected_inputs)
    return publish_text(outpath(folder,"evidence-manifest",".txt"), contents)

@_exact_reconciliation_context
def ledger_diff(left,right,folder, *, left_match_column=None, right_match_column=None,
                left_amount_column=None, right_amount_column=None):
    """Reconcile on auto-detected IDs or independently chosen CSV key headers.

    Only explicit, bounded column names may override automatic ID or amount aliases.
    Per-side mappings stay independent; original financial sources remain immutable.
    The actual mapped headers and separate gross charge/credit magnitudes
    appear in each report row; original byte digests identify the two imports.
    Matching net amounts with different gross flows are explicitly flagged
    for independent human review rather than silently declared matched.
    """
    from .ledger_provenance import attach_ledger_provenance
    groups=[defaultdict(list),defaultdict(list)]
    digests=[]
    selected_headers=[]
    selected_amount_headers=[]
    for source,d,override,amount_override in (
            (left,groups[0],left_match_column,left_amount_column),
            (right,groups[1],right_match_column,right_amount_column)):
        records, source_sha256, columns=table(
            source,("id","amount"), include_digest=True,
            id_column=override, amount_column=amount_override, include_columns=True)
        digests.append(source_sha256)
        selected_headers.append(columns["id"])
        selected_amount_headers.append(columns["amount"])
        for r in records:
            k=key(r["id"])
            if not k: raise csv_input_error("blank_ledger_id", line=int(r["row"]))
            d[k].append(r)
    def gross_flows(items):
        """Keep charge and credit magnitudes independent of their net balance.

        The source importer has already pinned each input to a byte snapshot;
        re-parsing each amount once here retains the suite's exact cents and
        private 64-digit Decimal context, including signed zero neutrality.
        """
        charges = Decimal(0)
        credits = Decimal(0)
        for item in items:
            amount = money(item["amount"])
            if amount > 0:
                charges += amount
            elif amount < 0:
                credits += amount.copy_negate()
        return charges, credits, charges - credits

    rows=[]
    for k in sorted(set(groups[0])|set(groups[1])):
        a,b=groups[0][k],groups[1][k]
        left_charges,left_credits,x=gross_flows(a)
        right_charges,right_credits,y=gross_flows(b)
        status=reconciliation_status(
            a,b,x,y,missing_left="missing_left",missing_right="missing_right")
        # Equal NET totals can conceal offsetting charges, credits and
        # reversals on one side. A reviewer must see the unmatched GROSS
        # movement; neither this flag nor 'matched' authorizes payment.
        if (a and b and x == y and
                (left_charges != right_charges or left_credits != right_credits)):
            status += (";" if status else "") + "gross_flow_mismatch_review"
        rows.append({"id":k,"status":status,"left_amount":dollars(x),"right_amount":dollars(y),
                     "difference":dollars(x-y),"left_rows":";".join(r["row"] for r in a),
                     "right_rows":";".join(r["row"] for r in b),
                     "left_ids":labels_for_report(a,"id"),
                     "right_ids":labels_for_report(b,"id"),
                     "left_gross_charges":dollars(left_charges),
                     "left_gross_credits":dollars(left_credits),
                     "right_gross_charges":dollars(right_charges),
                     "right_gross_credits":dollars(right_credits),
                     "left_match_column":selected_headers[0],
                     "right_match_column":selected_headers[1],
                     "left_amount_column":selected_amount_headers[0],
                     "right_amount_column":selected_amount_headers[1]})
    rows=attach_ledger_provenance(
        rows, left_sha256=digests[0], right_sha256=digests[1])
    return [save(folder,"ledger-diff",(
        "id","status","left_amount","right_amount","difference",
        "left_rows","right_rows","left_ids","right_ids",
        "left_gross_charges","left_gross_credits",
        "right_gross_charges","right_gross_credits",
        "left_match_column","right_match_column",
        "left_amount_column","right_amount_column",
        "left_source_sha256","right_source_sha256","input_identity_review"),rows)]

def invoice_window_days(text):
    """Parse user-entered day limits without coercion or untrusted error echoes."""
    if (type(text) is not str
            or re.fullmatch(r"(?:0|[1-9][0-9]{0,2})", text, re.ASCII) is None):
        raise ValueError("Invoice near-match days must be a whole number from 0 to 365")
    days = int(text)
    if days > 365:
        raise ValueError("Invoice near-match days must be a whole number from 0 to 365")
    return days


def invoice_twins(source,folder, *, window_days=7):
    """Produce a bounded, provenance-rich review report without internet access.

    Date-window scanning is chronological rather than all-history quadratic.
    The output is never partial: excess candidate density raises ValueError
    before creating a report. Findings are possible duplicates, not fraud.
    """
    from .invoice_provenance import attach_invoice_provenance
    records, source_sha256=table(source,("vendor","invoice_number","amount","date"),
                                 include_digest=True)
    for r in records:
        r["v"]=key(r["vendor"])
        r["inv"]=key(r["invoice_number"])
        r["amt"]=money(r["amount"])
        r["dt"]=parse_date(r["date"])
        if not r["v"] or not r["inv"]:
            raise ValueError("Blank vendor/invoice at row "+r["row"])
    rows=[]
    for a,b,status,reason in candidate_pairs(records, window_days=window_days):
        # B-minus-A measures the exact difference between the displayed
        # cent-rounded source amounts, independent of caller Decimal traps.
        # Candidate ordering and source/candidate fingerprints stay unchanged.
        with localcontext(Context(prec=64)):
            amount_delta = dollars(b["amt"] - a["amt"])
        rows.append({
            "row_a":a["row"],"row_b":b["row"],"status":status,
            "vendor":a["vendor"],"invoice_a":a["invoice_number"],
            "invoice_b":b["invoice_number"],
            "amount_a":dollars(a["amt"]),"amount_b":dollars(b["amt"]),
            "amount_delta_b_minus_a":amount_delta,
            "date_gap_days":str(abs((b["dt"] - a["dt"]).days)),
            "reason":reason,"vendor_b":b["vendor"],
            "date_a":a["dt"].isoformat(),"date_b":b["dt"].isoformat(),
            "review_flags":invoice_review_flags(a,b,status,window_days=window_days),
            "review_window_days":str(window_days)
        })
    rows=attach_invoice_provenance(rows,source_sha256=source_sha256)
    return [save(folder,"invoice-twins",(
        "row_a","row_b","status","vendor","invoice_a","invoice_b",
        "amount_a","amount_b","amount_delta_b_minus_a","date_gap_days",
        "reason","vendor_b","date_a","date_b","review_flags",
        "review_window_days","source_sha256","candidate_ref"
    ),rows)]

def spend_map(source,folder):
    """Expose exact net/gross spend, credit offsets, source rows and spikes."""
    from .spend_analysis import summarize_spend
    records, source_sha256=table(source,("vendor","amount","date"),("category",),
                                include_digest=True)
    rows=summarize_spend(
        records, normalize_vendor=key, parse_date=parse_date,
        parse_money=money, format_money=dollars,
        source_sha256=source_sha256)
    return [save(folder,"spend-map",(
        "vendor_key","month","category","amount","flag",
        "vendor_month_total","baseline_median","history_months",
        "category_history_months","category_baseline_median","category_review_flag",
        "gross_charges","gross_credits","credit_offset_review",
        "source_rows","source_vendor_labels","vendor_label_variants",
        "source_sha256"
    ),rows)]

def policy_delta(old,new,folder):
    """Compare two bounded local policy files with source-byte provenance."""
    from .policy_diff import compare_policy_files
    return compare_policy_files(old, new, folder, outpath)

@_exact_reconciliation_context
def grant_audit(claims,ledger,budgets,folder):
    """Legacy one-to-one reconciliation or explicit linked allocations.

    A claim_type/related_claim column without ledger_reference is an error:
    otherwise old logic would silently count credits as positive claims.
    """
    # Detect linked allocation columns from the *same validated snapshot*
    # as the claim rows; never reopen a potentially changed claim CSV header.
    claims_rows, fields, claims_digest=table(claims,("id","amount","program"),
                              ("ledger_reference","claim_type","related_claim"),
                              include_headers=True, include_digest=True)
    has_link=bool(fields & set(ALIASES["ledger_reference"]))
    advanced=bool(fields & set((*ALIASES["claim_type"],*ALIASES["related_claim"])))
    if advanced and not has_link:
        raise ValueError("Grant claim_type/related_claim requires ledger_reference; "
                         "legacy mode cannot safely interpret credits")
    if has_link:
        from .grant_allocations import reconcile_allocations
        return reconcile_allocations(claims,ledger,budgets,folder,claim_rows=claims_rows, claim_digest=claims_digest)
    ledger_rows, ledger_digest=table(ledger,("id","amount","program"), include_digest=True)
    budget_rows, budget_digest=table(budgets,("program","budget"), include_digest=True)
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
    # Physical CSV start lines are the budget report's audit navigation,
    # never a reconstructed ordinal after quoted-newline records.
    claim_rows_by_program=defaultdict(list)
    for claim_row in claims_rows:
        claim_rows_by_program[key(claim_row["program"])].append(claim_row["row"])
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
    budget_rows_by_program={}
    for r in budget_rows:
        program=key(r["program"])
        if not program or program in limits:raise ValueError("Blank/duplicate budget program at row "+r["row"])
        limits[program]=money(r["budget"])
        budget_rows_by_program[program]=r["row"]
    budget_checks=[]
    for program in sorted(set(limits)|set(claimed)):
        total=claimed[program];limit=limits.get(program)
        status="missing_budget" if limit is None else "over_budget_review" if total>limit else "within_budget"
        if normalized_collision(program_sources[program],"program"):
            status="normalized_budget_program_review;"+status
        budget_checks.append({"program":program,"claimed":dollars(total),
                              "budget":"" if limit is None else dollars(limit),"status":status,
                              "source_programs":labels_for_report(program_sources[program],"program"),
                              "claim_rows":";".join(claim_rows_by_program[program]),
                              "budget_rows":budget_rows_by_program.get(program, ""),
                              "claim_source_sha256":claims_digest,
                              "ledger_source_sha256":ledger_digest,
                              "budget_source_sha256":budget_digest})
    from .grant_bundle import publish_grant_bundle
    def build(staging):
        paths=[save(staging,"grant-audit-exceptions",("program","id","status","claim_amount","ledger_amount","difference","claim_rows","ledger_rows","claim_ids","ledger_ids","claim_programs","ledger_programs"),checks),
               save(staging,"grant-budget-check",(
                   "program","claimed","budget","status","source_programs",
                   "claim_rows","budget_rows","claim_source_sha256",
                   "ledger_source_sha256","budget_source_sha256"),budget_checks)]
        return paths+[manifest(staging,[claims,ledger,budgets],paths,
                               expected_inputs={claims: claims_digest, ledger: ledger_digest,
                                                budgets: budget_digest})]
    return publish_grant_bundle(folder,build)

def procure_guard(po,invoices,receipts,folder,policy_path=None):
    """Run the conservative, typed, traceable offline three-way review.

    Optional JSON policy changes only review thresholds, never authorizes payments.
    """
    from .procurement import reconcile_procurement
    return reconcile_procurement(po,invoices,receipts,folder,policy_path=policy_path)
