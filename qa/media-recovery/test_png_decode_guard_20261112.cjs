'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {verifiedPngGeometry}=require('./png_decode_guard_20261112.cjs');
const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
const sig=png.subarray(0,8);
const table=Array.from({length:256},(_,i)=>{let c=i;for(let k=0;k<8;k++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
function chunk(tag,data){
 const b=Buffer.alloc(data.length+12);b.writeUInt32BE(data.length,0);b.write(tag,4,'ascii');data.copy(b,8);
 let c=0xffffffff;for(let i=4;i<b.length-4;i++)c=table[(c^b[i])&255]^(c>>>8);
 b.writeUInt32BE((c^0xffffffff)>>>0,b.length-4);return b;
}
function make({width=1,height=1,depth=8,color=4,interlace=0,raw=Buffer.from([0,255,255]),idat=null,extra=[],split=false}={}){
 const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(width,0);ihdr.writeUInt32BE(height,4);ihdr[8]=depth;ihdr[9]=color;ihdr[12]=interlace;
 const compressed=idat??zlib.deflateSync(raw);
 const pieces=split?[compressed.subarray(0,2),compressed.subarray(2)]:[compressed];
 return Buffer.concat([sig,chunk('IHDR',ihdr),...extra,...pieces.map(d=>chunk('IDAT',d)),chunk('IEND',Buffer.alloc(0))]);
}
test('valid PNG with known 1x1 compressed scanline admits structural geometry',()=>assert.deepEqual(verifiedPngGeometry(png),{width:1,height:1,format:'png'}));
test('valid filtered 1x1 rows 0–4 admitted',()=>{for(let f=0;f<5;f++)assert.ok(verifiedPngGeometry(make({raw:Buffer.from([f,30,70])})));});
test('multiple contiguous IDAT chunks assembled correctly',()=>assert.ok(verifiedPngGeometry(make({split:true}))));
test('signed CRC-valid arbitrary IDAT bytes held instead of header-only admission',()=>assert.equal(verifiedPngGeometry(make({idat:Buffer.from('not-a-zlib-stream')})),null));
test('signed CRC-valid valid deflate with invalid filter 5 held',()=>assert.equal(verifiedPngGeometry(make({raw:Buffer.from([5,30,70])})),null));
test('signed CRC-valid decompressed short row held',()=>assert.equal(verifiedPngGeometry(make({raw:Buffer.from([0,0])})),null));
test('signed CRC-valid decompressed extra row held',()=>assert.equal(verifiedPngGeometry(make({raw:Buffer.from([0,0,0,0])})),null));
test('PNG unknown illegal bit depth held',()=>assert.equal(verifiedPngGeometry(make({depth:3})),null));
test('PNG unknown critical chunk held',()=>assert.equal(verifiedPngGeometry(make({extra:[chunk('ABCD',Buffer.from([1]))]})),null));
test('PNG invalid chunk CRC held',()=>{const b=Buffer.from(png);b[35]^=4;assert.equal(verifiedPngGeometry(b),null);});
test('PNG multiple noncontiguous IDAT held',()=>{const b=make();const ihdr=b.subarray(8,33),idat=b.subarray(33,b.length-12);assert.equal(verifiedPngGeometry(Buffer.concat([sig,ihdr,idat,chunk('tEXt',Buffer.from('x')),chunk('IDAT',Buffer.from([1])),chunk('IEND',Buffer.alloc(0))])),null);});
test('PNG indexed color without palette held',()=>assert.equal(verifiedPngGeometry(make({color:3,depth:8,raw:Buffer.from([0,0])})),null));
test('PNG decompression budget prevents enormous dimensions',()=>assert.equal(verifiedPngGeometry(make({width:100000,height:100000})),null));
test('PNG overlong appended data after IEND held',()=>assert.equal(verifiedPngGeometry(Buffer.concat([png,Buffer.from([0])])),null));
test('PNG Adam7 1x1 accepted',()=>assert.ok(verifiedPngGeometry(make({interlace:1}))));
test('PNG RGBA 2x1 accepted',()=>assert.ok(verifiedPngGeometry(make({width:2,color:6,raw:Buffer.alloc(1+2*4)}))));
