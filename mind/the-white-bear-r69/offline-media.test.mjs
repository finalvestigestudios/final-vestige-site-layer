import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url));
const video=path.join(dir,'the-white-bear-40s.mp4');
const hasVideo=existsSync(video);
const read=n=>readFileSync(path.join(dir,n),'utf8');
test('original film exists offline',{skip:!hasVideo},()=>assert.ok(hasVideo));
test('H.264 dimensions, duration and 480 frames',{skip:!hasVideo},()=>{
 const p=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',video],{encoding:'utf8'}));
 const v=p.streams.find(x=>x.codec_type==='video');
 assert.equal(v.codec_name,'h264');assert.equal(v.width,540);assert.equal(v.height,960);assert.equal(+v.nb_frames,480);
 assert.ok(Math.abs(+p.format.duration-40)<.02);
});
test('caption timeline covers full 40 seconds without gaps',()=>{
 const raw=read('captions.vtt');const cues=[...raw.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
 assert.equal(cues.length,6);const s=t=>{const n=t.split(':').map(Number);return n[0]*3600+n[1]*60+n[2]};
 assert.equal(s(cues[0][1]),0);assert.equal(s(cues.at(-1)[2]),40);for(let i=1;i<6;i++)assert.equal(s(cues[i-1][2]),s(cues[i][1]));
});
test('local player is optional, captioned, without autoplay or networking',()=>{
 const h=read('review.html');assert.match(h,/<video controls preload="none"/);assert.match(h,/<track kind="captions"/);
 assert.doesNotMatch(h,/<script|\sautoplay(?:\s|=|>)|https?:\/\//);
});
test('all six original frame designs and poster are present',()=>{
 for(let i=1;i<=6;i++)assert.ok(existsSync(path.join(dir,'scene-'+String(i).padStart(2,'0')+'.png')));
 assert.ok(existsSync(path.join(dir,'contact-sheet.jpg')));
});
