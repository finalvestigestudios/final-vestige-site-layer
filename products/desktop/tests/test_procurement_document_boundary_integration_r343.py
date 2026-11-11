"""R343: real ProcureGuard review_line and provenance callback-custody tests.

Run from the full repository on Ubuntu/Windows CI. Synthetic financial records
only; nothing here approves a credit, return, invoice or payment.
"""
from __future__ import annotations

from decimal import Decimal
import json
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line, offset_source_line_links


class HostileText(str):
    invoked = 0
    def __str__(self):
        HostileText.invoked += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")
    def upper(self):
        HostileText.invoked += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")
    def __hash__(self):
        HostileText.invoked += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class HostileObject:
    invoked = 0
    def __str__(self):
        HostileObject.invoked += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


def record(quantity="10", *, kind="", document="", related="", row="2", cost="10"):
    return {"quantity": quantity, "unit_price": cost, "event_type": kind,
            "document_id": document, "related_document": related, "row": row}


def run(invoices, receipts, identifier=normalize_key):
    return review_line([record()], invoices, receipts,
                       quantity=Decimal, unit_cost=Decimal,
                       identifier=identifier, policy=PricePolicy())


class ProcurementDocumentBoundaryIntegrationR343(unittest.TestCase):
    def setUp(self):
        HostileText.invoked = HostileObject.invoked = 0

    def assert_reject(self, operation):
        with self.assertRaises(ValueError) as context:
            operation()
        self.assertNotIn("PRIVATE_FINANCIAL_PATH", str(context.exception))
        self.assertIsNone(context.exception.__cause__)
        self.assertEqual((HostileText.invoked, HostileObject.invoked), (0, 0))

    def test_unlinked_invoice_document_subclass_rejected_before_display(self):
        self.assert_reject(lambda: run([record(document=HostileText("INV1"))], [record()]))

    def test_unlinked_invoice_related_subclass_rejected_before_display(self):
        self.assert_reject(lambda: run([record(related=HostileText("INV1"))], [record()]))

    def test_unlinked_receipt_document_object_rejected(self):
        self.assert_reject(lambda: run([record()], [record(document=HostileObject())]))

    def test_unlinked_receipt_related_object_rejected(self):
        self.assert_reject(lambda: run([record()], [record(related=HostileObject())]))

    def test_invoice_integer_is_not_a_csv_document_label(self):
        self.assert_reject(lambda: run([record(document=12)], [record()]))

    def test_invoice_boolean_is_not_a_csv_document_label(self):
        self.assert_reject(lambda: run([record(document=True)], [record()]))

    def test_receipt_number_is_not_a_csv_document_label(self):
        self.assert_reject(lambda: run([record()], [record(document=123)]))

    def test_credit_reference_subclass_rejected_before_normalizing(self):
        self.assert_reject(lambda: run([record(document="INV1"),
                                        record("2", kind="credit", related=HostileText("INV1"))],
                                       [record()]))

    def test_return_reference_subclass_rejected_before_normalizing(self):
        self.assert_reject(lambda: run([record()], [record(document="RC1"),
                                                          record("2", kind="return", related=HostileText("RC1"))]))

    def test_injected_identifier_exception_is_private(self):
        def bad(_):
            raise OSError("PRIVATE_FINANCIAL_PATH")
        self.assert_reject(lambda: run([record(document="INV1")], [record()], identifier=bad))

    def test_injected_identifier_untrusted_result_rejected(self):
        self.assert_reject(lambda: run([record(document="INV1")], [record()],
                                       identifier=lambda _: HostileText("INV1")))

    def test_injected_identifier_boolean_result_rejected(self):
        self.assert_reject(lambda: run([record(document="INV1")], [record()],
                                       identifier=lambda _: False))

    def test_credit_normalized_match_remains_human_review(self):
        output, flags = run([record(document="INV-1"),
                             record("2", kind="credit", document="CM1", related="INV1")],
                            [record()])
        self.assertIn("normalized_credit_link_review", flags)
        self.assertIn("credit_memo_review", flags)
        self.assertEqual(output["invoice_total_exact"], "80")

    def test_return_normalized_match_remains_human_review(self):
        output, flags = run([record()], [record(document="RC-1"),
                                               record("2", kind="return", document="RT1", related="RC1")])
        self.assertIn("normalized_return_link_review", flags)
        self.assertIn("return_review", flags)
        self.assertEqual(output["received_qty"], "8")

    def test_ascii_case_source_identity_has_no_spurious_normalized_flag(self):
        _, flags = run([record(document="InV1"),
                        record("2", kind="credit", document="CM1", related="inv1")],
                       [record()])
        self.assertNotIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)
        self.assertIn("credit_memo_review", flags)

    def test_wrong_credit_reference_remains_unlinked(self):
        _, flags = run([record(document="INV1"),
                        record("2", kind="credit", document="CM1", related="WRONG")],
                       [record()])
        self.assertIn("unlinked_credit_review", flags)

    def test_offset_citation_blocks_hostile_original_id(self):
        self.assert_reject(lambda: offset_source_line_links(
            [record(document=HostileText("INV1")), record("2", kind="credit", related="INV1")],
            source="invoice", offset="credit", identifier=normalize_key))

    def test_offset_citation_callback_exception_is_private(self):
        def bad(_):
            raise RuntimeError("PRIVATE_FINANCIAL_PATH")
        self.assert_reject(lambda: offset_source_line_links(
            [record(document="INV1")], source="invoice", offset="credit", identifier=bad))

    def test_offset_citation_callback_forgery_rejected(self):
        self.assert_reject(lambda: offset_source_line_links(
            [record(document="INV1")], source="invoice", offset="credit",
            identifier=lambda _: HostileText("INV1")))

    def test_offset_citations_include_physical_rows_only(self):
        data = offset_source_line_links(
            [record(document="INV-1", row="9"),
             record("2", kind="credit", document="CM1", related="INV1", row="10")],
            source="invoice", offset="credit", identifier=normalize_key)
        self.assertEqual(json.loads(data), [{"offset_row": "10", "target_rows": ["9"]}])
        self.assertNotIn("INV", data)


if __name__ == "__main__":
    unittest.main()
