"""No network or production WordPress access: synthetic Playwright response contracts."""
import unittest
from media_transfer_admission import audit_image_payloads, archive_identity

APOLLO = 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
FRANKLIN = 'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg?fit=768%2C1221&ssl=1'
MAP = 'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?fit=768%2C519&ssl=1'
IMAGES = [{'url': x, 'complete': True, 'width': 50} for x in (APOLLO,FRANKLIN,MAP)]
class Request:
    def __init__(self):self.resource_type='image'
class Response:
    def __init__(self,url,status=200,typ='image/jpeg',body=b'not-a-real-image-fixture'):
        self.url,self.status,self.typ,self.payload = url,status,typ,body
        self.request=Request()
    def header_value(self,head):return self.typ if head=='content-type' else None
    def body(self):return self.payload
class Tests(unittest.TestCase):
    def responses(self):return [Response(a['url']) for a in IMAGES]
    def test_three_real_http_body_receipts_are_required(self):
        r=audit_image_payloads(IMAGES,self.responses())
        self.assertEqual(r['status'],'PASS'); self.assertEqual(len(r['images']),3)
        self.assertTrue(all(x['decoded_payload_bytes']>0 and len(x['payload_sha256'])==64 for x in r['images']))
    def test_missing_response_is_not_substituted_with_natural_width(self):
        r=audit_image_payloads(IMAGES,self.responses()[:2])
        self.assertEqual(r['status'],'HOLD');self.assertIn('malbone:IMAGE_HTTP_RESPONSE_MISSING',r['failure_codes'])
    def test_error_http_is_rejected(self):
        responses=self.responses();responses[1].status=403
        self.assertEqual(audit_image_payloads(IMAGES,responses)['status'],'HOLD')
    def test_non_image_content_type_rejected(self):
        responses=self.responses();responses[0].typ='text/html'
        self.assertIn('apollo:NOT_IMAGE_CONTENT_TYPE',audit_image_payloads(IMAGES,responses)['failure_codes'])
    def test_empty_and_oversize_rejected(self):
        r=self.responses();r[2].payload=b''
        self.assertIn('malbone:IMAGE_BODY_SIZE_INVALID',audit_image_payloads(IMAGES,r)['failure_codes'])
        r[2].payload=b'x'*(8*1024*1024+1)
        self.assertEqual(audit_image_payloads(IMAGES,r)['status'],'HOLD')
    def test_duplicate_source_does_not_fake_three_archives(self):
        r=audit_image_payloads([IMAGES[0],IMAGES[0],IMAGES[1]],self.responses())
        self.assertEqual(r['status'],'HOLD')
    def test_untrusted_host_cannot_spoof_valid_path(self):
        self.assertIsNone(archive_identity('https://evil.example/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'))
        self.assertIsNone(archive_identity('http://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'))
        self.assertIsNone(archive_identity('https://finalvestige.com.evil.test/wp-content/uploads/2026/08/s67-19766.webp'))
    def test_individual_valid_images_are_recognized(self):
        self.assertEqual([archive_identity(i['url']) for i in IMAGES],['apollo','franklin','malbone'])
    def test_response_body_exception_fails_closed(self):
        class Broken(Response):
            def body(self):raise RuntimeError('body access denied')
        r=self.responses();r[0]=Broken(APOLLO)
        self.assertIn('apollo:BODY_FETCH_FAILED',audit_image_payloads(IMAGES,r)['failure_codes'])
    def test_non_image_resource_type_does_not_count(self):
        r=self.responses();r[2].request.resource_type='fetch'
        self.assertIn('malbone:IMAGE_HTTP_RESPONSE_MISSING',audit_image_payloads(IMAGES,r)['failure_codes'])
if __name__=='__main__':unittest.main()
