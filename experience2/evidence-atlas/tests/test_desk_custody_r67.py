#!/usr/bin/env python3
"""R67 reviewed R38 five-field desk-custody cross-component bridge contract."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ATLAS=Path(__file__).resolve().parents[1]
DESK=ATLAS.parent/'research-desk/templates/ledger.html'
JS=ATLAS/'atlas.js'
SUITE=ATLAS/'integration/fv-ex2-apollo-suite.php'


def git_blob(contents):
    return hashlib.sha1(b'blob '+str(len(contents)).encode()+b'\0'+contents).hexdigest()


class DeskCustodyR67(unittest.TestCase):
    def test_exact_original_source_is_unchanged(self):
        self.assertEqual(git_blob(DESK.read_bytes()),
          '4842afb84b4c993cfc4861ce7f5a7a4d7b451871')

    def test_every_original_custody_field_is_pinned_in_runtime(self):
        text=DESK.read_text()
        records=re.findall(r'<details class="fv-ex2-ledger__custody" '
          r'data-fvx-photo-record="(\d\d)">.*?<dl>(.*?)</dl>',text,re.S)
        self.assertEqual([r[0] for r in records],['01','02','03','04','05','06'])
        values=[]
        for _,fragment in records:
            pairs=re.findall(r'<(dt|dd)>(.*?)</\1>',fragment,re.S)
            self.assertEqual([tag for tag,_ in pairs],['dt','dd']*5)
            values.append([v.replace('&amp;','&') for _,v in pairs])
        js=JS.read_text()
        anchor=re.search(r'const pinnedDeskCustody=(\[\[.*?\]\]);',js,re.S)
        self.assertIsNotNone(anchor)
        self.assertEqual(json.loads(anchor.group(1)),values)
        self.assertIn('!deskCustodyIntact(records)',js)
        self.assertIn('withdrawDesk(true)',js)
        self.assertIn('cells[j].textContent.trim()===value',js)

    def test_suite_admits_exact_new_atlas_runtime(self):
        blob=git_blob(JS.read_bytes())
        self.assertIn("'assets/atlas.js' => '"+blob+"'",SUITE.read_text())
        self.assertNotIn('wp_insert_post(',SUITE.read_text())


if __name__=='__main__': unittest.main()
