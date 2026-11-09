"""R311: verify exact restored evidence, not just parsed report and journal count."""
from __future__ import annotations

import errno
import os
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch
from fvs_suite.vault_restore_verify import verify_private_restore_members as verify
from fvs_suite.vault_restore_verify import _read_exact

_PRIVATE = "PRIVATE-FAMILY-OFFICE-CUSTOMER-2026"

class RestoreIntegrityR311(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r311-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / "private-restore"
        self.folder.mkdir(mode=0o700)
        self.folder_id = os.lstat(self.folder)
        self.members = [
            (self.folder / "exception-report.csv", b"claim,amount\nSYNTHETIC,12.30\n"),
            (self.folder / "exception-report.review.jsonl", b'{"synthetic":true}\n'),
            (self.folder / "sealed-evidence-manifest.json", b'{"product":"grants"}\n')]
        self.created=[]
        for path, data in self.members:
            with path.open("xb") as h:
                self.created.append((path, os.fstat(h.fileno())))
                h.write(data)

    def check(self):
        verify(self.folder, self.folder_id, self.created, self.members)

    def test_complete_three_member_restore(self):
        self.check()
    def test_no_journal_two_member_restore(self):
        self.check()
        self.members.pop(1); self.created.pop(1)
        (self.folder/"exception-report.review.jsonl").unlink()
        self.check()
    def test_all_members_must_match(self):
        for i in range(3):
            with self.subTest(index=i):
                self.members[i][0].write_bytes(b"bad")
                with self.assertRaisesRegex(ValueError, "Cannot verify"):
                    self.check()
                self.members[i][0].write_bytes(self.members[i][1])
    def test_equal_length_manifest_corruption_is_caught(self):
        name, data = self.members[2]
        name.write_bytes(data.replace(b"grants",b"grantX"))
        with self.assertRaises(ValueError): self.check()
    def test_persisted_append_fails(self):
        with self.members[0][0].open("ab") as h: h.write(b"EXTRA")
        with self.assertRaises(ValueError): self.check()
    def test_missing_member_fails(self):
        self.members[1][0].unlink()
        with self.assertRaises(ValueError): self.check()
    def test_identical_bytes_new_inode_fails(self):
        path,data=self.members[0]
        outside=self.root/"replacement"
        outside.write_bytes(data)
        os.replace(outside,path)
        with self.assertRaises(ValueError): self.check()
    def test_symlink_swap_rejected_no_follow(self):
        path,_=self.members[2]
        outside=self.root/"victim"
        outside.write_bytes(b"DO NOT TOUCH")
        path.unlink()
        try: path.symlink_to(outside)
        except (OSError,NotImplementedError): self.skipTest("symlinks not available")
        with self.assertRaises(ValueError): self.check()
        self.assertEqual(outside.read_bytes(),b"DO NOT TOUCH")
    def test_replaced_folder_not_followed(self):
        self.folder.rename(self.root/"old")
        self.folder.mkdir()
        with self.assertRaises(ValueError): self.check()
    def test_folder_symlink_not_followed(self):
        other=self.root/"old"
        self.folder.rename(other)
        try: self.folder.symlink_to(other, target_is_directory=True)
        except (OSError,NotImplementedError): self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError): self.check()
    def test_mismatched_member_order(self):
        with self.assertRaises(ValueError): verify(self.folder,self.folder_id,self.created,list(reversed(self.members)))
    def test_duplicate_member(self):
        duplicate=[self.members[0]]*3
        with self.assertRaises(ValueError): verify(self.folder,self.folder_id,self.created,duplicate)
    def test_extra_recorded_member(self):
        with self.assertRaises(ValueError): verify(self.folder,self.folder_id,self.created[:2],self.members)
    def test_unregistered_extra_file_rejected(self):
        stranger=self.folder/"unregistered-private.csv"
        stranger.write_bytes(b"unrelated file")
        with self.assertRaises(ValueError):self.check()
        self.assertEqual(stranger.read_bytes(),b"unrelated file")
    def test_unregistered_extra_symlink_rejected(self):
        outside=self.root/"other"
        outside.write_bytes(b"OTHER")
        try:(self.folder/"unexpected").symlink_to(outside)
        except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError):self.check()
        self.assertEqual(outside.read_bytes(),b"OTHER")
    def test_scandir_failure_privacy(self):
        with patch("fvs_suite.vault_restore_verify.os.scandir",side_effect=OSError(errno.EACCES,_PRIVATE,str(self.root/_PRIVATE))):
            with self.assertRaises(ValueError) as caught:self.check()
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(_PRIVATE,str(caught.exception))
    def test_expected_mutable_bytearray_rejected(self):
        data=list(self.members); data[0]=(data[0][0],bytearray(data[0][1]))
        with self.assertRaises(ValueError):verify(self.folder,self.folder_id,self.created,data)
    def test_missing_expected_member_rejected(self):
        with self.assertRaises(ValueError):verify(self.folder,self.folder_id,self.created,self.members[:2])
    def test_empty_members_rejected(self):
        with self.assertRaises(ValueError):verify(self.folder,self.folder_id,[],[])
    def test_os_error_redacted_without_exception_chain(self):
        secret=str(self.root / _PRIVATE)
        with patch("fvs_suite.vault_restore_verify.os.open",side_effect=PermissionError(errno.EACCES,_PRIVATE,secret)):
            with self.assertRaises(ValueError) as caught: self.check()
        err=caught.exception
        self.assertIsNone(err.__cause__)
        self.assertIsNone(err.__context__)
        self.assertNotIn(secret,"".join(traceback.format_exception(err)))
        self.assertNotIn(_PRIVATE,"".join(traceback.format_exception(err)))
    def test_failed_read_is_redacted(self):
        with patch("fvs_suite.vault_restore_verify.os.read",side_effect=OSError(errno.EIO,_PRIVATE,str(self.root/_PRIVATE))):
            with self.assertRaises(ValueError) as caught:self.check()
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(_PRIVATE,str(caught.exception))
    def test_short_os_reads_are_completed(self):
        actual=os.read
        with patch("fvs_suite.vault_restore_verify.os.read",side_effect=lambda fd,n:actual(fd,min(n,3))):self.check()
    def test_zero_progress_read_rejected(self):
        with patch("fvs_suite.vault_restore_verify.os.read",return_value=b""):
            with self.assertRaises(ValueError):self.check()
    def test_invalid_nonbytes_read_rejected(self):
        with patch("fvs_suite.vault_restore_verify.os.read",return_value=bytearray(b"x")):
            with self.assertRaises(ValueError):self.check()
    def test_large_multiblock_read(self):
        path,_=self.members[0]
        content=b"x"*(256*1024+71)
        path.write_bytes(content)
        self.members[0]=(path,content)
        self.check()
    def test_interrupt_propagates_for_caller_cleanup(self):
        with patch("fvs_suite.vault_restore_verify.os.read",side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):self.check()
    def test_does_not_change_archived_bytes(self):
        old=[p.read_bytes() for p,_ in self.members]
        self.check()
        self.assertEqual([p.read_bytes() for p,_ in self.members],old)
    def test_byte_reader_rejects_premature_eof(self):
        with tempfile.TemporaryFile() as h:
            h.write(b"abc");h.seek(0)
            with self.assertRaises(OSError):_read_exact(h.fileno(),4)
    def test_premature_close_errors_sanitized(self):
        with patch("fvs_suite.vault_restore_verify.os.close",side_effect=OSError(errno.EIO,_PRIVATE)):
            with self.assertRaises(ValueError) as caught:self.check()
        self.assertIsNone(caught.exception.__context__)

if __name__=="__main__":unittest.main()
