import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/'tools'/'experience-2'/'verify_ex2_media_bytes.py'
spec=importlib.util.spec_from_file_location('ex2bytes',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FakeReply:
    status=200
    def __init__(self,record,data,redirect=None,mime=None):
        self._data=data
        self.url=redirect or m.media_url(record)
        self.headers={'Content-Type': mime or record['mime']}
    def __enter__(self): return self
    def __exit__(self,*args):pass
    def geturl(self):return self.url
    def read(self,n):
        part=self._data[:n];self._data=self._data[n:];return part

def fake_data(record):
    size=record['bytes']
    if record['mime']=='image/jpeg':return b'\xff\xd8\xff'+b'A'*(size-5)+b'\xff\xd9'
    return b'RIFF'+b'A'*4+b'WEBP'+b'A'*(size-12)

class TestCustody(unittest.TestCase):
    def test_all_three_good_bytes(self):
        for row in m.MEDIA:
            with self.subTest(row=row['wp_id']):
                result=m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row)))
                self.assertEqual(result['transfer'],'PASS')
                self.assertEqual(len(result['sha256']),64)
    def test_all_three_offline_not_claimed(self):
        result=m.run()
        self.assertFalse(result['all_pass'])
        self.assertFalse(result['network_attempted'])
        self.assertTrue(all(x['transfer']=='NOT_TESTED' for x in result['records']))
    def test_reject_different_host(self):
        with self.assertRaises(m.GateFailure):m.validate_location('https://untrusted.example/wp-content/uploads/2026/08/s67-19766.webp',m.media_url(m.MEDIA[0]))
    def test_reject_cdn_substitution(self):
        with self.assertRaises(m.GateFailure):m.validate_location('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',m.media_url(m.MEDIA[0]))
    def test_reject_unapproved_query(self):
        with self.assertRaises(m.GateFailure):m.validate_location(m.media_url(m.MEDIA[0])+'?fit=300%2C233',m.media_url(m.MEDIA[0]))
    def test_reject_redirect(self):
        row=m.MEDIA[0]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row),redirect='https://evil.example/abc'))
    def test_reject_wrong_type(self):
        row=m.MEDIA[0]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row),mime='text/html'))
    def test_reject_wrong_size(self):
        row=m.MEDIA[0]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row)[:-1]))
    def test_reject_oversize(self):
        row=m.MEDIA[0]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row)+b'X'))
    def test_reject_html_with_matching_length(self):
        row=m.MEDIA[0]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,b'<html>'+b'X'*(row['bytes']-6)))
    def test_reject_broken_image_trailer(self):
        row=m.MEDIA[1]
        with self.assertRaises(m.GateFailure):m.inspect(row,opener=lambda request,timeout:FakeReply(row,fake_data(row)[:-2]+b'AA'))
    def test_expected_wp_metadata(self):
        self.assertEqual([r['wp_id'] for r in m.MEDIA],[473,474,1258])
        self.assertEqual([r['bytes'] for r in m.MEDIA],[78346,466043,5553669])

if __name__=='__main__':unittest.main()
