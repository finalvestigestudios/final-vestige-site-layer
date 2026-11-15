"""R452: real OSError slot must be read without subclass override execution."""
from __future__ import annotations

import errno
import unittest

from fvs_suite.csv_publish_guard import private_csv_failure

_SECRET = "SYNTHETIC_PRIVATE_ACCOUNT_R452"


class GetterTrap(PermissionError):
    def __getattribute__(self, name):
        if name == "errno":
            raise RuntimeError(_SECRET)
        return super().__getattribute__(name)


class GetterForgery(PermissionError):
    def __getattribute__(self, name):
        if name == "errno":
            return _SECRET
        return super().__getattribute__(name)


class PropertyTrap(PermissionError):
    @property
    def errno(self):
        raise RuntimeError(_SECRET)


class PropertyForgery(PermissionError):
    @property
    def errno(self):
        return errno.ENOENT


class CollisionTrap(FileExistsError):
    def __getattribute__(self, name):
        if name == "errno":
            raise RuntimeError(_SECRET)
        return super().__getattribute__(name)


class CSVErrnoDescriptorCustodyR452(unittest.TestCase):
    def assert_private(self, result: OSError, *, code: int):
        self.assertEqual(result.errno, code)
        self.assertIsInstance(result, OSError)
        self.assertNotIn(type(result), {GetterTrap, GetterForgery, PropertyTrap, PropertyForgery})
        self.assertNotIn(_SECRET, repr(result))
        self.assertIsNone(result.filename)
        self.assertIsNone(result.filename2)
        self.assertIsNone(result.__context__)
        self.assertIsNone(result.__cause__)

    def test_raised_getattribute_hook_cannot_abort_sanitization(self):
        self.assert_private(private_csv_failure(GetterTrap(errno.EACCES, _SECRET, _SECRET)), code=errno.EACCES)

    def test_forged_getattribute_hook_cannot_change_errno(self):
        self.assert_private(private_csv_failure(GetterForgery(errno.EACCES, _SECRET, _SECRET)), code=errno.EACCES)

    def test_property_hook_cannot_abort_sanitization(self):
        self.assert_private(private_csv_failure(PropertyTrap(errno.EACCES, _SECRET, _SECRET)), code=errno.EACCES)

    def test_property_hook_cannot_forge_errno(self):
        self.assert_private(private_csv_failure(PropertyForgery(errno.EACCES, _SECRET, _SECRET)), code=errno.EACCES)

    def test_base_errno_slot_boolean_falls_back_to_eio(self):
        source = GetterTrap(errno.EACCES, _SECRET, _SECRET)
        OSError.errno.__set__(source, True)
        self.assert_private(private_csv_failure(source), code=errno.EIO)

    def test_base_errno_slot_non_integer_falls_back_to_eio(self):
        source = GetterTrap(errno.EACCES, _SECRET, _SECRET)
        OSError.errno.__set__(source, _SECRET)
        self.assert_private(private_csv_failure(source), code=errno.EIO)

    def test_base_errno_slot_negative_falls_back_to_eio(self):
        source = PropertyTrap(errno.EACCES, _SECRET, _SECRET)
        OSError.errno.__set__(source, -errno.EACCES)
        self.assert_private(private_csv_failure(source), code=errno.EIO)

    def test_collision_subclass_ignores_hostile_errno(self):
        source = CollisionTrap(errno.EEXIST, _SECRET, _SECRET)
        clean = private_csv_failure(source)
        self.assertIs(type(clean), FileExistsError)
        self.assertEqual(str(clean), "CSV report destination already exists")
        self.assertIsNone(clean.__context__)
        self.assertIsNone(clean.__cause__)
        self.assertNotIn(_SECRET, repr(clean))

    def test_raised_source_context_is_not_transferred_to_sanitized_error(self):
        source = GetterTrap(errno.EACCES, _SECRET, _SECRET)
        source.__cause__ = RuntimeError(_SECRET)
        try:
            raise source
        except OSError as caught:
            clean = private_csv_failure(caught)
        try:
            raise clean
        except OSError as published:
            self.assertIsNone(published.__cause__)
            self.assertIsNone(published.__context__)
            self.assertNotIn(_SECRET, repr(published))


if __name__ == "__main__":
    unittest.main()
