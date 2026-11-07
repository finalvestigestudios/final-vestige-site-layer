"""Actual-byte receipt unit controls; generated images are synthetic, NOT archives."""
import io
import unittest
from PIL import Image, ImageDraw
from verify_archival_provenance import MEDIA, ORIGIN, BASE, classify_source, verify_image_bytes, verify_receipt


def artificial(fmt, dims):
    output=io.BytesIO()
    im=Image.new('RGB',dims,(19,51,48))
    brush=ImageDraw.Draw(im)
    for x in range(0,dims[0],3):
        brush.line((x,0,(x*37)%dims[0],dims[1]-1),fill=((x*17)%256,(x*91)%256,(x*43)%256),width=2)
    im.save(output,format=fmt,quality=96)
    return output.getvalue()


class ArchivalByteReceiptTests(unittest.TestCase):
    def test_selected_cdn_derivative_decodes_then_validates(self):
        for i, spec in enumerate(MEDIA):
            dims=next(v for v in spec['candidates'] if v[0]>=644)
            url=('https://i0.wp.com/'+ORIGIN+BASE+spec['file']+
                 '?fit='+str(dims[0])+'%2C'+str(dims[1])+'&ssl=1')
            original='https://'+ORIGIN+BASE+spec['file']
            source=classify_source(original,url,i)
            data=artificial(spec['format'],dims)
            receipt=verify_receipt(source,verify_image_bytes(data,spec['format']),200,
                                   'image/'+('webp' if spec['format']=='WEBP' else 'jpeg'))
            self.assertEqual(receipt['transfer_bytes'],len(data))
            self.assertFalse(receipt['first_party'])
            self.assertEqual(len(receipt['sha256']),64)
    def test_offline_empty_bytes_cannot_be_admitted(self):
        with self.assertRaises(ValueError):verify_image_bytes(b'', 'JPEG')
    def test_wrong_encoded_format_rejected(self):
        with self.assertRaises(ValueError):verify_image_bytes(artificial('JPEG',(800,1200)), 'WEBP')
    def test_short_or_corrupt_payload_rejected(self):
        for payload in (b'A'*2000,artificial('JPEG',(800,1200))[:150]):
            with self.subTest(length=len(payload)),self.assertRaises(ValueError):
                verify_image_bytes(payload,'JPEG')
    def test_wrong_real_pixel_dimensions_rejected(self):
        spec=MEDIA[0]; source=classify_source('https://'+ORIGIN+BASE+spec['file'],
            'https://i0.wp.com/'+ORIGIN+BASE+spec['file']+'?fit=768%2C598&ssl=1',0)
        receipt=verify_image_bytes(artificial('WEBP',(100,100)),'WEBP')
        with self.assertRaises(ValueError):verify_receipt(source,receipt,200,'image/webp')
    def test_wrong_content_type_and_http_status_rejected(self):
        spec=MEDIA[0]; source=classify_source('https://'+ORIGIN+BASE+spec['file'],
            'https://'+ORIGIN+BASE+spec['file'],0)
        receipt=verify_image_bytes(artificial('WEBP',(1041,810)),'WEBP')
        for status,mime in [(404,'image/webp'),(200,'text/plain')]:
            with self.subTest(status=status,mime=mime),self.assertRaises(ValueError):
                verify_receipt(source,receipt,status,mime)


if __name__=='__main__':unittest.main(verbosity=2)
