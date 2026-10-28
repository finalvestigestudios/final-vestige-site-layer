"""Local-first Final Vestige Labs desktop engines. All findings require human review."""
from __future__ import annotations
import csv, difflib, hashlib, re, statistics
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from .review import labels_for_report, normalized_collision, price_exceeds_tolerance, reconciliation_status

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
}
MAX_ROWS = 200_000
CENT = Decimal("0.01")

def _exact_amount(value):
    """Parse accounting amounts exactly; never silently round unit costs."""
    raw = str(value).strip()
    if not raw: raise ValueError("Missing amount")
    negative = raw.startswith("(") and raw.endswith(")")
    raw = raw.strip("()").replace("$","").replace(",","").strip()
    try: number = Decimal(raw)
    except InvalidOperation as exc: raise ValueError("Invalid amount: "+str(value)) from exc
    if not number.is_finite() or abs(number) > Decimal("1000000000000"):
        raise ValueError("Nonfinite or out-of-range amount")
    return -number if negative else number


def money(value):
    return _exact_amount(value).quantize(CENT, rounding=ROUND_HALF_UP)


def unit_cost(value):
    """Unit prices may carry sub-cent precision; totals round only on display."""
    amount = _exact_amount(value)
    if amount.normalize().as_tuple().exponent < -8:
        raise ValueError("Unit price precision exceeds eight decimal places")
    return amount

def qty(value):
    try: n = Decimal(str(value).strip().replace(",",""))
    except InvalidOperation as exc: raise ValueError("Invalid quantity: "+str(value)) from exc
    if not n.is_finite() or n < 0 or n > 1_000_000_000: raise ValueError("Invalid quantity range")
    return n

def key(value): return re.sub(r"[^A-Z0-9]+","",str(value).upper())
def dollars(value): return format(value.quantize(CENT),".2f")
def parse_date(value):
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%m/%d/%y"):
        try: return datetime.strptime(str(value).strip(),fmt).date()
        except ValueError: pass
    raise ValueError("Invalid date (use YYYY-MM-DD or MM/DD/YYYY): "+str(value))

def table(path, required, optional=()):
    p = Path(path)
    if p.suffix.lower() != ".csv" or not p.is_file(): raise ValueError("Select an existing CSV: "+p.name)
    with p.open(encoding="utf-8-sig",newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames: raise ValueError("Missing headers: "+p.name)
        # Duplicate normalized headings can hide conflicting financial columns.
        normalized = [str(h).strip().lower().replace(" ", "_") for h in reader.fieldnames if h]
        if "" in normalized or len(normalized) != len(reader.fieldnames) or len(normalized) != len(set(normalized)):
            raise ValueError(f"{p.name}: blank or duplicate normalized CSV header")
        headers = dict(zip(normalized, reader.fieldnames))
        cols = {}
        for field in (*required,*optional):
            matches = [alias for alias in ALIASES.get(field,(field,)) if alias in headers]
            if len(matches) > 1:
                raise ValueError(f"{p.name}: ambiguous '{field}' aliases: {', '.join(matches)}")
            cols[field] = headers[matches[0]] if matches else None
            if field in required and cols[field] is None:
                raise ValueError(f"{p.name}: missing '{field}' column")
        out = []
        for i,r in enumerate(reader,2):
            if i > MAX_ROWS+1: raise ValueError("CSV exceeds 200,000 rows")
            if None in r: raise ValueError(f"{p.name}: malformed row {i}")
            out.append({"row":str(i),**{name:str(r.get(col) or "").strip() for name,col in cols.items() if col}})
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
    p=outpath(folder,stem)
    with p.open("x",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{k:safe_cell(v) for k,v in row.items()} for row in rows])
    return p

def manifest(folder,inputs,outputs):
    p=outpath(folder,"evidence-manifest",".txt")
    with p.open("x",encoding="utf-8") as f:
        f.write("SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n")
        for source in [*map(Path,inputs),*outputs]:
            h=hashlib.sha256()
            with source.open("rb") as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk)
            f.write(f"{source.name}\t{h.hexdigest()}\n")
    return p

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
    records=table(source,("vendor","invoice_number","amount","date"))
    exact=defaultdict(list);by_amount=defaultdict(list);pairs={}
    for r in records:
        r["v"]=key(r["vendor"]);r["inv"]=key(r["invoice_number"])
        r["amt"]=money(r["amount"]);r["dt"]=parse_date(r["date"])
        if not r["v"] or not r["inv"]: raise ValueError("Blank vendor/invoice at row "+r["row"])
        exact[(r["v"],r["inv"])].append(r)
        by_amount[(r["v"],r["amt"])].append(r)
    for items in exact.values():
        for i in range(1,len(items)):
            a,b=items[0],items[i]
            pairs[(a["row"],b["row"])]=(a,b,"exact_invoice_key","same normalized vendor and invoice number")
    for items in by_amount.values():
        if len(items)>200: raise ValueError("More than 200 same-vendor/same-amount rows; split input for safe review")
        for i,a in enumerate(items):
            for b in items[i+1:]:
                if abs((a["dt"]-b["dt"]).days)<=7 and a["inv"]!=b["inv"]:
                    pairs.setdefault((a["row"],b["row"]),(a,b,"review_possible_duplicate","same vendor and amount within seven days"))
    rows=[{"row_a":a["row"],"row_b":b["row"],"status":status,"vendor":a["vendor"],
           "invoice_a":a["invoice_number"],"invoice_b":b["invoice_number"],
           "amount_a":dollars(a["amt"]),"amount_b":dollars(b["amt"]),"reason":reason}
          for a,b,status,reason in pairs.values()]
    return [save(folder,"invoice-twins",("row_a","row_b","status","vendor","invoice_a","invoice_b","amount_a","amount_b","reason"),rows)]

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
    for path in (old,new):
        p=Path(path)
        if not p.is_file() or p.suffix.lower() not in (".txt",".md",".csv"):
            raise ValueError("Policy comparison supports TXT, MD and CSV files")
        if p.stat().st_size>10*1024*1024:raise ValueError("Policy file exceeds 10 MB")
    a=Path(old).read_text(encoding="utf-8-sig").splitlines(keepends=True)
    b=Path(new).read_text(encoding="utf-8-sig").splitlines(keepends=True)
    diff="".join(difflib.unified_diff(a,b,fromfile=Path(old).name,tofile=Path(new).name))
    p=outpath(folder,"policy-delta",".txt")
    with p.open("x",encoding="utf-8") as f:
        f.write("Text differences only. Not legal advice or a compliance determination.\n\n")
        f.write(diff or "No textual differences found.\n")
    return [p]

def grant_audit(claims,ledger,budgets,folder):
    claims_rows=table(claims,("id","amount","program"))
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

def procure_guard(po,invoices,receipts,folder):
    sources=[table(po,("po_number","line","quantity","unit_price")),
             table(invoices,("po_number","line","quantity","unit_price")),
             table(receipts,("po_number","line","quantity"))]
    grouped=[defaultdict(list) for _ in range(3)]
    for rows,d in zip(sources,grouped):
        for r in rows:
            k=(key(r["po_number"]),key(r["line"]))
            if not all(k):raise ValueError("Blank PO or line at row "+r["row"])
            d[k].append(r)
    checks=[]
    for po_key,line in sorted(set().union(*(set(g) for g in grouped))):
        k=(po_key,line);a,b,c=(g[k] for g in grouped)
        flags=[]
        source_records=[*a,*b,*c]
        if len(a)!=1:flags.append("missing_or_duplicate_po")
        if normalized_collision(source_records,"po_number"):
            flags.append("normalized_po_key_review")
        if normalized_collision(source_records,"line"):
            flags.append("normalized_line_key_review")
        po_qty=qty(a[0]["quantity"]) if len(a)==1 else Decimal(0)
        po_price=unit_cost(a[0]["unit_price"]) if len(a)==1 else Decimal(0)
        inv_qty=sum((qty(r["quantity"]) for r in b),Decimal(0))
        rec_qty=sum((qty(r["quantity"]) for r in c),Decimal(0))
        inv_prices=[(qty(r["quantity"]),unit_cost(r["unit_price"])) for r in b]
        inv_total=sum((amount*price for amount,price in inv_prices),Decimal(0))
        if len(b)>1 and len(set(inv_prices))<len(b):
            flags.append("possible_duplicate_invoice_line")
        if not b:flags.append("missing_invoice")
        if not c:flags.append("missing_receipt")
        if len(a)==1 and inv_qty>po_qty:flags.append("invoiced_above_order")
        if inv_qty>rec_qty:flags.append("invoiced_above_received")
        if po_price<0 or any(price<0 for _amount,price in inv_prices):
            flags.append("negative_unit_price_review")
        if len(a)==1 and b:
            expected=inv_qty*po_price
            if (price_exceeds_tolerance(inv_total,expected) or
                    any(price_exceeds_tolerance(price,po_price) for _amount,price in inv_prices)):
                flags.append("price_variance_above_2pct")
        checks.append({"po":po_key,"line":line,"po_qty":str(po_qty),"invoiced_qty":str(inv_qty),
                       "received_qty":str(rec_qty),"po_unit_price":format(po_price,"f"),
                       "invoice_total":dollars(inv_total),"status":";".join(flags) or "matched",
                       "po_rows":";".join(r["row"] for r in a),
                       "invoice_rows":";".join(r["row"] for r in b),
                       "receipt_rows":";".join(r["row"] for r in c),
                       "po_ids":labels_for_report(a,"po_number"),
                       "invoice_po_ids":labels_for_report(b,"po_number"),
                       "receipt_po_ids":labels_for_report(c,"po_number"),
                       "line_labels":labels_for_report(source_records,"line")})
    paths=[save(folder,"procurement-three-way",("po","line","po_qty","invoiced_qty","received_qty",
           "po_unit_price","invoice_total","status","po_rows","invoice_rows","receipt_rows","po_ids","invoice_po_ids","receipt_po_ids","line_labels"),checks)]
    return paths+[manifest(folder,[po,invoices,receipts],paths)]
