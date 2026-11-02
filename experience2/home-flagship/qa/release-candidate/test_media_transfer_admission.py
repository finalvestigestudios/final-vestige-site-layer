"""No network or production WordPress access: synthetic Playwright response contracts."""
import unittest
import base64
from media_transfer_admission import audit_image_payloads, archive_identity

APOLLO = 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
FRANKLIN = 'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg?fit=768%2C1221&ssl=1'
MAP = 'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?fit=768%2C519&ssl=1'
IMAGES = [{'url': x, 'complete': True, 'width': 50} for x in (APOLLO,FRANKLIN)]
# Real, self-contained 2x2 raster fixtures (generated once using Pillow).
# Runtime regression tests require only the Python standard library.
FIXTURE_BYTES = tuple(base64.b64decode(s) for s in (
    'UklGRi4AAABXRUJQVlA4ICIAAABwAQCdASoCAAIAAUAmJZQCdAFAAAD++U8tstEn9pEEAAAA',
    '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDl6KKK2Mj/2Q==',
    '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwAooorYyP/Z',
))

class Request:
    def __init__(self):self.resource_type='image'
class Response:
    def __init__(self,url,status=200,typ=None,body=None):
        idx=(APOLLO,FRANKLIN,MAP).index(url)
        self.url,self.status = url,status
        self.typ=typ if typ is not None else ('image/webp' if idx==0 else 'image/jpeg')
        self.payload=body if body is not None else FIXTURE_BYTES[idx]
        self.request=Request()
    def header_value(self,head):return self.typ if head=='content-type' else None
    def body(self):return self.payload
class Tests(unittest.TestCase):
    def responses(self):return [Response(a['url']) for a in IMAGES]

    def test_two_cleared_http_payloads_are_required(self):
        receipt=audit_image_payloads(IMAGES,self.responses())
        self.assertEqual(receipt['status'],'PASS')
        self.assertEqual([r['archive'] for r in receipt['images']],['apollo','franklin'])
        self.assertTrue(all(r['decoded_payload_bytes']>0 and len(r['payload_sha256'])==64 for r in receipt['images']))

    def test_missing_body_is_not_forgiven_by_naturalwidth(self):
        receipt=audit_image_payloads(IMAGES,self.responses()[:1])
        self.assertIn('franklin:IMAGE_HTTP_RESPONSE_MISSING',receipt['failure_codes'])

    def test_non_200_http_rejected(self):
        responses=self.responses();responses[1].status=403
        self.assertEqual(audit_image_payloads(IMAGES,responses)['status'],'HOLD')

    def test_non_image_type_rejected(self):
        r=self.responses();r[0].typ='text/html'
        self.assertIn('apollo:NOT_IMAGE_CONTENT_TYPE',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_empty_and_large_body_rejected(self):
        r=self.responses();r[1].payload=b''
        self.assertIn('franklin:IMAGE_BODY_SIZE_INVALID',audit_image_payloads(IMAGES,r)['failure_codes'])
        r[1].payload=b'x'*(8*1024*1024+1)
        self.assertEqual(audit_image_payloads(IMAGES,r)['status'],'HOLD')

    def test_duplicate_image_identity_rejected(self):
        receipt=audit_image_payloads([IMAGES[0], IMAGES[0]],self.responses())
        self.assertEqual(receipt['status'],'HOLD')

    def test_embargoed_map_fetched_as_extra_resource_fails(self):
        receipt=audit_image_payloads(IMAGES,self.responses()+[Response(MAP)])
        self.assertIn('NYPL_UNCLEARED_CAPTURE_HTTP_REQUEST_DETECTED',receipt['failure_codes'])

    def test_embargoed_map_in_expected_images_rejected(self):
        receipt=audit_image_payloads(IMAGES+[{'url':MAP,'complete':True,'width':100}],
                                    self.responses()+[Response(MAP)])
        self.assertEqual(receipt['status'],'HOLD')
        self.assertIsNone(archive_identity(MAP))

    def test_untrusted_host_and_scheme_rejected(self):
        for url in ('https://evil.example/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
                    'http://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
                    'https://finalvestige.com.evil.test/wp-content/uploads/2026/08/s67-19766.webp'):
            self.assertIsNone(archive_identity(url))

    def test_pinned_provenance_only(self):
        self.assertEqual([archive_identity(i['url']) for i in IMAGES],['apollo','franklin'])

    def test_read_error_fails_closed(self):
        class Broken(Response):
            def body(self):raise RuntimeError('body unavailable')
        r=self.responses();r[0]=Broken(APOLLO)
        self.assertIn('apollo:BODY_FETCH_FAILED',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_fetch_resource_type_does_not_pass(self):
        r=self.responses();r[1].request.resource_type='fetch'
        self.assertIn('franklin:IMAGE_HTTP_RESPONSE_MISSING',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_html_masquerading_as_jpeg_rejected(self):
        r=self.responses();r[1].payload=b'<html>fake</html>'
        self.assertIn('franklin:IMAGE_MAGIC_INVALID',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_forged_mime_rejected(self):
        r=[Response(i['url'],typ='image/jpeg',body=b'<html>fake</html>') for i in IMAGES]
        self.assertEqual(audit_image_payloads(IMAGES,r)['status'],'HOLD')

    def test_svg_mime_rejected(self):
        for mime in ('image/svg+xml','image/gif','image/unknown'):
            r=self.responses();r[0].typ=mime
            self.assertIn('apollo:NOT_SUPPORTED_RASTER_MIME',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_mime_mismatch_rejected(self):
        r=self.responses();r[0].typ='image/jpeg'
        self.assertIn('apollo:IMAGE_MIME_MISMATCH',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_duplicate_payload_rejected(self):
        r=self.responses();r[1].payload=r[0].payload
        self.assertIn('DUPLICATE_ARCHIVAL_IMAGE_PAYLOAD',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_corrupt_webp_and_truncated_jpeg_rejected(self):
        r=self.responses();bb=bytearray(r[0].payload);bb[4:8]=b'\\0\\0\\0\\0';r[0].payload=bytes(bb)
        self.assertIn('apollo:IMAGE_MAGIC_INVALID',audit_image_payloads(IMAGES,r)['failure_codes'])
        r=self.responses();r[1].payload=r[1].payload[:-2]
        self.assertIn('franklin:IMAGE_MAGIC_INVALID',audit_image_payloads(IMAGES,r)['failure_codes'])

    def test_receipt_reports_real_observed_formats(self):
        receipt=audit_image_payloads(IMAGES,self.responses())
        self.assertEqual(receipt['status'],'PASS')
        self.assertEqual([e['detected_raster_format'] for e in receipt['images']],['webp','jpeg'])

if __name__=='__main__':unittest.main()
