'use strict';
/** Offline, bounded PNG image-data validation; no URL reads, content copies, or CMS writes. */
const zlib=require('node:zlib');
const MAX_INPUT=32*1024*1024;
const MAX_DECOMPRESSED=64*1024*1024;
const SIGNATURE=Buffer.from('89504e470d0a1a0a','hex');
const COLOR_BITS={0:[1,2,4,8,16],2:[8,16],3:[1,2,4,8],4:[8,16],6:[8,16]};
const CHANNELS={0:1,2:3,3:1,4:2,6:4};
const PASSES=[[0,0,8,8],[4,0,8,8],[0,4,4,8],[2,0,4,4],[0,2,2,4],[1,0,2,2],[0,1,1,2]];
const crcTable=Array.from({length:256},(_,i)=>{
 let c=i;for(let j=0;j<8;j++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);return c>>>0;
});
function validCRC(buffer,start,end,stored){
 let c=0xffffffff;
 for(let i=start;i<end;i++)c=crcTable[(c^buffer[i])&255]^(c>>>8);
 return ((c^0xffffffff)>>>0)===stored;
}
const lengthOnAxis=(total,start,step)=>total<=start?0:Math.ceil((total-start)/step);
function scanlinePasses(width,height,channels,depth,interlace){
 const passSpecs=interlace===0?[[0,0,1,1]]:PASSES;
 let total=0;
 const passes=[];
 for(const [x0,y0,dx,dy] of passSpecs){
  const w=lengthOnAxis(width,x0,dx),h=lengthOnAxis(height,y0,dy);
  if(w===0||h===0)continue;
  const rowBytes=Math.ceil(w*channels*depth/8);
  total+=(rowBytes+1)*h;
  if(!Number.isSafeInteger(total)||total>MAX_DECOMPRESSED)return null;
  passes.push({rowBytes,height:h});
 }
 return {total,passes};
}
function verifiedPngGeometry(b){
 if(!Buffer.isBuffer(b)||b.length<57||b.length>MAX_INPUT||
    !b.subarray(0,8).equals(SIGNATURE))return null;
 let off=8,width=0,height=0,depth=0,color=0,interlace=0;
 let ihdr=false,plte=false,idat=false,afterIdat=false,iend=false;
 const data=[];
 while(off+12<=b.length){
  const size=b.readUInt32BE(off);
  if(size>b.length-off-12)return null;
  const tag=b.toString('ascii',off+4,off+8);
  const start=off+8,end=start+size,next=end+4;
  if(!validCRC(b,off+4,end,b.readUInt32BE(end)))return null;
  if(!ihdr){
   if(tag!=='IHDR'||size!==13)return null;
   width=b.readUInt32BE(start);height=b.readUInt32BE(start+4);
   depth=b[start+8];color=b[start+9];interlace=b[start+12];
   if(width<1||height<1||width>100000||height>100000||
      !COLOR_BITS[color]?.includes(depth)||
      b[start+10]!==0||b[start+11]!==0||interlace>1)return null;
   ihdr=true;
  }else if(tag==='IHDR')return null;
  else if(tag==='PLTE'){
   if(plte||idat||size<3||size>768||size%3!==0||color===0||color===4)return null;
   if(color===3&&size/3>2**depth)return null;
   plte=true;
  }else if(tag==='IDAT'){
   if(afterIdat||size===0)return null;
   data.push(b.subarray(start,end));idat=true;
  }else if(tag==='IEND'){
   if(size!==0||!idat||next!==b.length)return null;
   iend=true;break;
  }else{
   if(tag==='iCCP'||tag==='tEXt'||tag==='zTXt'||tag==='iTXt'||tag==='gAMA'||
      tag==='sRGB'||tag==='cHRM'||tag==='pHYs'||tag==='tIME'||tag==='bKGD'||
      tag==='sBIT'||tag==='tRNS'||tag==='hIST'||tag==='sPLT'||tag==='eXIf'){
     // Allowed ancillary metadata; never trusted as permission/identity evidence.
   }else if(tag[0]&&tag[0]===tag[0].toUpperCase())return null; // unknown critical
   if(idat)afterIdat=true;
  }
  off=next;
 }
 if(!ihdr||!idat||!iend||(color===3&&!plte))return null;
 const layout=scanlinePasses(width,height,CHANNELS[color],depth,interlace);
 if(!layout)return null;
 let inflated;
 try{
  inflated=zlib.inflateSync(Buffer.concat(data),{maxOutputLength:layout.total+1});
 }catch{return null;}
 if(inflated.length!==layout.total)return null;
 let cursor=0;
 for(const pass of layout.passes){
  for(let row=0;row<pass.height;row++){
   if(inflated[cursor]>4)return null;
   cursor+=pass.rowBytes+1;
  }
 }
 return cursor===inflated.length?{width,height,format:'png'}:null;
}
module.exports={verifiedPngGeometry};
