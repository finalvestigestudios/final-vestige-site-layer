"""Invoice matching scale, complete-report and provenance regression tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine
from fvs_suite.invoice_match import candidate_pairs, review_flags


class InvoiceScaleR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-invoice-scale-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def invoice_file(self, entries):
        p = self.folder / "invoices.csv"
        with p.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(("vendor", "invoice_number", "amount", "date"))
            writer.writerows(entries)
        return str(p)

    @staticmethod
    def rows(path):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def candidate(row, inv, dt, amt="10.00", vendor="ACME"):
        return {"row":str(row), "v":"ACME", "vendor":vendor,
                "inv":inv.replace("-","").upper(), "invoice_number":inv,
                "amt":Decimal(amt), "dt":dt}

    def test_same_vendor_amount_over_200_rows_no_longer_rejected(self):
        base = date(2026, 1, 1)
        entries=[("ACME",f"INV{i:04d}","10.00",(base+timedelta(days=i)).isoformat())
                 for i in range(300)]
        report=self.rows(engine.invoice_twins(self.invoice_file(entries), self.folder)[0])
        self.assertEqual(len(report),2072)
        self.assertTrue(all(row["status"]=="review_possible_duplicate" for row in report))

    def test_sliding_window_inclusive_seven_days(self):
        base=date(2026,1,1)
        records=[
            self.candidate(2,"A",base),
            self.candidate(3,"B",base+timedelta(days=7)),
            self.candidate(4,"C",base+timedelta(days=8))]
        results=candidate_pairs(records)
        self.assertEqual([(a["row"],b["row"]) for a,b,*_ in results],[("2","3"),("3","4")])

    def test_unsorted_input_still_detects_chronological_window(self):
        base=date(2026,1,1)
        records=[
            self.candidate(2,"C",base+timedelta(days=20)),
            self.candidate(3,"A",base),
            self.candidate(4,"B",base+timedelta(days=3))]
        results=candidate_pairs(records)
        self.assertEqual([(a["row"],b["row"]) for a,b,*_ in results],[("3","4")])

    def test_exact_duplicates_match_across_distant_dates(self):
        a=self.candidate(2,"INV-1",date(2024,1,1))
        b=self.candidate(3,"INV-1",date(2026,1,1))
        result=candidate_pairs([a,b])
        self.assertEqual(len(result),1)
        self.assertEqual(result[0][2],"exact_invoice_key")
        self.assertIn("distant_dates_review",review_flags(a,b,result[0][2]))

    def test_same_invoice_number_not_repeated_in_near_scan(self):
        base=date(2026,1,1)
        records=[self.candidate(i+2,"INV-1",base+timedelta(days=i)) for i in range(3)]
        result=candidate_pairs(records)
        self.assertEqual(len(result),2)  # stable anchor, not all three pair combinations
        self.assertTrue(all(tag=="exact_invoice_key" for _,_,tag,_ in result))

    def test_candidate_cap_fails_closed_with_explicit_message(self):
        base=date(2026,1,1)
        records=[self.candidate(i+2,f"INV{i}",base) for i in range(10)]
        with self.assertRaisesRegex(ValueError,"no incomplete report was saved"):
            candidate_pairs(records,max_candidates=6)

    def test_engine_raises_without_partial_output_for_too_many_pairs(self):
        base=date(2026,1,1)
        entries=[("ACME",f"INV-{i}","10.00",base.isoformat()) for i in range(450)]
        with self.assertRaisesRegex(ValueError,"Too many invoice review candidates"):
            engine.invoice_twins(self.invoice_file(entries), self.folder)
        self.assertEqual(list(self.folder.glob("invoice-twins-*.csv")),[])

    def test_exact_invoice_amount_mismatch_is_explicit_flag(self):
        entries=[
            ("ACME","N-1","10.00","2026-01-01"),
            ("ACME","N-1","11.00","2026-01-02")]
        row=self.rows(engine.invoice_twins(self.invoice_file(entries), self.folder)[0])[0]
        self.assertEqual(row["status"],"exact_invoice_key")
        self.assertIn("amount_variance_review",row["review_flags"])
        self.assertEqual((row["amount_a"],row["amount_b"]),("10.00","11.00"))

    def test_original_source_vendor_and_number_collision_visible(self):
        entries=[
            ("Acme, Inc.","INV-001","10.00","2026-01-01"),
            ("ACME INC","INV001","10.00","2026-01-02")]
        row=self.rows(engine.invoice_twins(self.invoice_file(entries), self.folder)[0])[0]
        self.assertEqual(row["status"],"exact_invoice_key")
        self.assertIn("normalized_vendor_key_review",row["review_flags"])
        self.assertIn("normalized_invoice_key_review",row["review_flags"])
        self.assertEqual(row["vendor_b"],"ACME INC")
        self.assertEqual(row["date_b"],"2026-01-02")
        self.assertEqual((row["row_a"],row["row_b"]),("2","3"))

    def test_case_only_differences_are_not_normalization_collision(self):
        entries=[("ACME","AbC","10","2026-01-01"),
                 ("acme","abc","10","2026-01-02")]
        row=self.rows(engine.invoice_twins(self.invoice_file(entries), self.folder)[0])[0]
        self.assertEqual(row["review_flags"],"")

    def test_distinct_vendors_and_amounts_are_not_compared(self):
        p=self.invoice_file([("ACME","A","10","2026-01-01"),
                             ("BETA","B","10","2026-01-01"),
                             ("ACME","C","11","2026-01-01")])
        self.assertEqual(self.rows(engine.invoice_twins(p,self.folder)[0]),[])

    def test_candidate_limit_validated(self):
        with self.assertRaisesRegex(ValueError,"positive integer"):
            candidate_pairs([],max_candidates=0)
        with self.assertRaisesRegex(ValueError,"between 0 and 365"):
            candidate_pairs([],window_days=-1)

    def test_no_data_has_headers_only(self):
        p=self.invoice_file([])
        result=engine.invoice_twins(p,self.folder)[0]
        self.assertEqual(self.rows(result),[])
        self.assertIn("review_flags",result.read_text(encoding="utf-8-sig").splitlines()[0])

    def test_nonfinite_invoice_amount_is_rejected_before_any_report(self):
        p=self.invoice_file([("ACME","X","NaN","2026-01-01")])
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            engine.invoice_twins(p,self.folder)
        self.assertEqual(list(self.folder.glob("invoice-twins-*.csv")),[])


if __name__=="__main__":
    unittest.main()
