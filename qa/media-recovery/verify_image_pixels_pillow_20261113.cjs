'use strict';
/**
 * Offline FULL-RASTER check for already-authorized JPEG/WebP candidate bytes.
 * Python 3 + Pillow is an optional, audited local decoder dependency: absent,
 * timed out, truncated, animated, unusually oriented or oversized => HOLD.
 * No URL input, image caching, output files, network requests or WP writes.
 */
const {spawnSync}=require('node:child_process');
const MAX_INPUT=32*1024*1024;
const MAX_PIXELS=40_000_000;
const PY=String.raw`
import io, json, sys, warnings
try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
except ImportError:
    pass
from PIL import Image, ImageFile
Image.MAX_IMAGE_PIXELS = 40000000
ImageFile.LOAD_TRUNCATED_IMAGES = False
warnings.simplefilter('error', Image.DecompressionBombWarning)
raw = sys.stdin.buffer.read(33554433)
if not raw or len(raw) > 33554432:
    sys.exit(2)
with Image.open(io.BytesIO(raw), formats=['JPEG', 'WEBP']) as im:
    if im.format not in ('JPEG', 'WEBP'):
        sys.exit(3)
    w, h = im.size
    if not (0 < w <= 100000 and 0 < h <= 100000 and w*h <= 40000000):
        sys.exit(4)
    if getattr(im, 'n_frames', 1) != 1:
        sys.exit(5)
    if im.getexif().get(274, 1) != 1:
        sys.exit(6)
    im.load() # force decompression rather than trusting SOF/VP8X dimensions
    print(json.dumps({'width':w, 'height':h, 'format': im.format.lower()}, separators=(',', ':')))
`;
function fullyDecodedJpegWebpGeometry(bytes){
 if(!Buffer.isBuffer(bytes)||bytes.length<16||bytes.length>MAX_INPUT)return null;
 let result;
 try{
  result=spawnSync('python3',['-I','-B','-c',PY],{
   input:bytes,encoding:'utf8',timeout:5000,maxBuffer:4096,
   windowsHide:true,env:{...process.env,PYTHONNOUSERSITE:'1',PYTHONDONTWRITEBYTECODE:'1'}
  });
 }catch{return null;}
 if(result.error||result.status!==0||result.signal||!result.stdout||result.stdout.length>200)return null;
 let v;try{v=JSON.parse(result.stdout.trim());}catch{return null;}
 if(!v||!['jpeg','webp'].includes(v.format)||
    !Number.isSafeInteger(v.width)||!Number.isSafeInteger(v.height)||
    v.width<1||v.height<1||v.width*v.height>MAX_PIXELS)return null;
 return {width:v.width,height:v.height,format:v.format};
}
module.exports={fullyDecodedJpegWebpGeometry};
