import csv
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
from fvs_suite import engine as e

class SuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def csvfile(self,name,headers,rows):
        p=self.root/name
        with p.open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f);w.writerow(headers);w.writerows(rows)
        return str(p)

    def read(self,path):
        with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

    def test_money_exact_and_invalid(self):
        self.assertEqual(e.money("($1,234.56)"),Decimal("-1234.56"))
        self.assertEqual(e.money("0.005"),Decimal("0.01"))
        for invalid in ("NaN","Infinity",""):
            with self.assertRaises(ValueError):e.money(invalid)

    def test_ledger_diff(self):
        a=self.csvfile("left.csv",["transaction_id","amount"],[["A","10.00"],["B","12"]])
        b=self.csvfile("right.csv",["id","amount"],[["A","10"],["B","11"]])
        rows=self.read(e.ledger_diff(a,b,self.root)[0])
        self.assertEqual({r["id"]:r["status"] for r in rows},{"A":"matched","B":"variance"})
        self.assertEqual(rows[1]["difference"],"1.00")

    def test_ledger_duplicates_never_silently_match(self):
        a=self.csvfile("left.csv",["id","amount"],[["A","5"],["A","5"]])
        b=self.csvfile("right.csv",["id","amount"],[["A","10"]])
        self.assertEqual(self.read(e.ledger_diff(a,b,self.root)[0])[0]["status"],"duplicate_id_review")

    def test_invoice_candidates(self):
        p=self.csvfile("invoices.csv",["vendor","invoice_number","amount","date"],[
            ["ACME","INV-1","10","2026-01-01"],["Acme","INV1","10","2026-01-02"],
            ["Acme","INV-2","10","2026-01-03"]])
        rows=self.read(e.invoice_twins(p,self.root)[0])
        self.assertIn("exact_invoice_key",{r["status"] for r in rows})
        self.assertIn("review_possible_duplicate",{r["status"] for r in rows})

    def test_spend_spike(self):
        p=self.csvfile("spend.csv",["vendor","amount","date","category"],[
            ["ACME","10","2026-01-01","Parts"],["ACME","10","2026-02-01","Parts"],
            ["ACME","10","2026-03-01","Parts"],["ACME","30","2026-04-01","Parts"]])
        rows=self.read(e.spend_map(p,self.root)[0])
        self.assertEqual(rows[-1]["flag"],"review_spike")

    def test_policy_diff(self):
        a=self.root/"old.txt";b=self.root/"new.txt"
        a.write_text("Rule A\n");b.write_text("Rule B\n")
        report=e.policy_delta(str(a),str(b),self.root)[0].read_text()
        self.assertIn("-Rule A",report);self.assertIn("+Rule B",report)

    def test_grant_budget(self):
        a=self.csvfile("claims.csv",["transaction_id","amount","program"],[["A","20","G1"]])
        b=self.csvfile("ledger.csv",["transaction_id","amount","program"],[["A","20","G1"]])
        c=self.csvfile("budgets.csv",["program","budget"],[["G1","10"]])
        outputs=e.grant_audit(a,b,c,self.root)
        self.assertEqual(self.read(outputs[1])[0]["status"],"over_budget_review")
        self.assertIn("SHA-256",outputs[2].read_text())

    def test_three_way_match(self):
        a=self.csvfile("po.csv",["po_number","line","quantity","unit_price"],[["P","1","10","5"]])
        b=self.csvfile("invoice.csv",["po_number","line","quantity","unit_price"],[["P","1","11","5"]])
        c=self.csvfile("receipts.csv",["po_number","line","quantity"],[["P","1","9"]])
        row=self.read(e.procure_guard(a,b,c,self.root)[0])[0]
        self.assertIn("invoiced_above_order",row["status"])
        self.assertIn("invoiced_above_received",row["status"])

    def test_bad_csv_rejected(self):
        p=self.csvfile("bad.csv",["foo"],[["x"]])
        with self.assertRaises(ValueError):e.table(p,("amount",))

if __name__=="__main__":unittest.main()
