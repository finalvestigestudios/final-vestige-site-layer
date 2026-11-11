"""R344: native procurement row snapshots and source-citation grammar.

Synthetic values only. This suite executes the *real* small R344 helper and
existing event_custody module; real engine integration has a separate suite.
"""
from __future__ import annotations

from collections import UserDict
import unittest

from fvs_suite.procurement_native_rows import owned_procurement_rows, physical_source_row


class HostileDict(dict):
    calls = 0

    def _forged(self, *args, **kwargs):
        HostileDict.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")

    get = __getitem__ = __iter__ = items = keys = values = copy = __contains__ = _forged


class HostileList(list):
    calls = 0

    def __iter__(self):
        HostileList.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class HostileKey(str):
    calls = 0

    def __str__(self):
        HostileKey.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class HostileSourceLabel(str):
    calls = 0

    def __str__(self):
        HostileSourceLabel.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")

    def __len__(self):
        HostileSourceLabel.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")

    def __lt__(self, other):
        HostileSourceLabel.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class NativeProcurementRowsR344(unittest.TestCase):
    def setUp(self):
        HostileDict.calls = HostileList.calls = HostileKey.calls = HostileSourceLabel.calls = 0

    def assert_private_rejection(self, callable_):
        with self.assertRaises(ValueError) as caught:
            callable_()
        self.assertNotIn("PRIVATE_CLIENT", str(caught.exception))
        self.assertEqual((HostileDict.calls, HostileList.calls,
                          HostileKey.calls, HostileSourceLabel.calls), (0, 0, 0, 0))
        self.assertIsNone(caught.exception.__cause__)

    def test_native_storage_not_virtual_quantity_get(self):
        row = HostileDict({"quantity": "10", "unit_price": "1.25", "row": "2"})
        owned = owned_procurement_rows([row])
        self.assertEqual(owned[0]["quantity"], "10")
        self.assertEqual(owned[0]["unit_price"], "1.25")
        self.assertEqual(HostileDict.calls, 0)

    def test_native_storage_not_virtual_event_type(self):
        row = HostileDict({"event_type": "credit", "related_document": "INV-1"})
        self.assertEqual(owned_procurement_rows([row])[0]["event_type"], "credit")
        self.assertEqual(HostileDict.calls, 0)

    def test_native_storage_not_virtual_source_row(self):
        row = HostileDict({"row": "9", "document_id": "INV-1"})
        self.assertEqual(owned_procurement_rows([row])[0]["row"], "9")
        self.assertEqual(HostileDict.calls, 0)

    def test_snapshot_is_plain_independent_list_and_dict(self):
        row = {"quantity": "2", "row": "12"}
        source = [row]
        owned = owned_procurement_rows(source)
        self.assertIs(type(owned), list)
        self.assertIs(type(owned[0]), dict)
        self.assertIsNot(owned, source)
        self.assertIsNot(owned[0], row)
        row["quantity"] = "999"
        source.append({"quantity": "88"})
        self.assertEqual(owned, [{"quantity": "2", "row": "12"}])

    def test_empty_native_list_is_valid(self):
        self.assertEqual(owned_procurement_rows([]), [])

    def test_preserves_original_native_unicode_and_decimal_text(self):
        row = {"quantity": "3.125", "unit_price": "0.00000001",
               "document_id": "ß-4", "related_document": "Ｓ-4", "row": "99"}
        self.assertEqual(owned_procurement_rows([row])[0], row)

    def test_uses_native_dict_keys_not_user_virtual_get(self):
        value = HostileDict({"document_id": "INV", "row": "2"})
        self.assertEqual(owned_procurement_rows([value]), [{"document_id": "INV", "row": "2"}])
        self.assertEqual(HostileDict.calls, 0)

    def test_reject_list_subclass_before_iterator_hook(self):
        self.assert_private_rejection(lambda: owned_procurement_rows(HostileList([{"row": "2"}])))

    def test_reject_generator_before_invoking_it(self):
        def raise_on_iteration():
            raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")
            yield {}
        self.assert_private_rejection(lambda: owned_procurement_rows(raise_on_iteration()))

    def test_reject_tuple_records(self):
        self.assert_private_rejection(lambda: owned_procurement_rows(({"row": "2"},)))

    def test_reject_userdict_record(self):
        self.assert_private_rejection(lambda: owned_procurement_rows([UserDict({"row": "2"})]))

    def test_reject_non_mapping_record(self):
        self.assert_private_rejection(lambda: owned_procurement_rows(["not a record"]))

    def test_reject_native_dict_with_subclass_key_without_calling_str(self):
        self.assert_private_rejection(lambda: owned_procurement_rows([{HostileKey("row"): "2"}]))

    def test_reject_nontext_dict_key(self):
        self.assert_private_rejection(lambda: owned_procurement_rows([{1: "2"}]))

    def test_two_rows_preserve_source_order(self):
        rows = [{"row": "9"}, {"row": "2"}]
        self.assertEqual(owned_procurement_rows(rows), rows)

    def test_no_source_mutation_for_dict_subclass(self):
        source = HostileDict({"row": "2", "quantity": "1"})
        first = owned_procurement_rows([source])[0]
        first["quantity"] = "100"
        self.assertEqual(dict.get(source, "quantity"), "1")
        self.assertEqual(HostileDict.calls, 0)

    def test_valid_physical_row_minimum(self):
        self.assertEqual(physical_source_row("2"), "2")

    def test_valid_physical_row_ordinary(self):
        self.assertEqual(physical_source_row("200001"), "200001")

    def test_valid_physical_row_maximum_grammar(self):
        self.assertEqual(physical_source_row("9999999999"), "9999999999")

    def test_bad_row_one_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("1"))

    def test_bad_row_zero_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("0"))

    def test_bad_row_leading_zero_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("002"))

    def test_bad_row_unicode_digit_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("٢"))

    def test_bad_row_fullwidth_digit_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("２"))

    def test_bad_row_newline_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("2\n3"))

    def test_bad_row_embedded_zero_width_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("2\u200b"))

    def test_bad_row_control_prefix_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("\x002"))

    def test_bad_row_white_space_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row(" 2"))

    def test_bad_row_signed_number_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("+2"))

    def test_bad_row_overlength_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row("10000000000"))

    def test_bad_row_blank_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row(""))

    def test_bad_row_integer_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row(2))

    def test_bad_row_none_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row(None))

    def test_bad_row_float_is_rejected(self):
        self.assert_private_rejection(lambda: physical_source_row(2.0))

    def test_bad_row_subclass_no_hook_is_invoked(self):
        self.assert_private_rejection(lambda: physical_source_row(HostileSourceLabel("2")))

    def test_bad_row_string_case_of_private_path_is_redacted(self):
        self.assert_private_rejection(lambda: physical_source_row("/CLIENT/FINANCE/2"))


if __name__ == "__main__":
    unittest.main()
