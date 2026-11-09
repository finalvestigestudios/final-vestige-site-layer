'use strict';const assert=require('node:assert/strict');
const {inspect}=require('../../tools/experience-2/verify_archival_media_custody.cjs');
const img=(file,host,w,h,src)=>'<img src="https://'+host+file+src+'" alt="Documented historical archive source photograph or map." width="'+w+'" height="'+h+'" srcset="archive 768w" sizes="100vw" loading="lazy">';
const base=[
 img('s67-19766.webp','finalvestige.com/wp-content/uploads/','1041','810',''),
 img('Franklinexpeditionnote.jpg','finalvestige.com/wp-content/uploads/','960','1526',''),
 img('edit-017-v02-nypl-5003296-original.jpg','i0.wp.com/finalvestige.com/','1536','1038','?fit=1024%2C692'),
 'https://www.nasa.gov/ https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg',
 'https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0',
 'EDITORIAL TYPESETTING · NOT A FACSIMILE https://finalvestige.com/focus/',
 '<!-- wp:jetpack/subscriptions /-->',
 ...Array(72).fill('class="fv-margin-strip__item"')
].join('\n');
assert.equal(inspect(base).pass,true);
const bad=[
 x=>x.replace('s67-19766.webp','missing.webp'),
 x=>x.replace('alt="Documented historical archive source photograph or map."','alt=""'),
 x=>x.replace('width="1041"','width="0"'),
 x=>x.replace('srcset="archive 768w"',''),
 x=>x.replace('loading="lazy"','loading="eager"'),
 x=>x.replace('fit=1024%2C692','fit=5667%2C3831'),
 x=>x.replace('commons.wikimedia.org','bad.invalid'),
 x=>x.replace('digitalcollections.nypl.org','bad.invalid'),
 x=>x.replace('www.nasa.gov','bad.invalid'),
 x=>x.replace('EDITORIAL TYPESETTING · NOT A FACSIMILE',''),
 x=>x.replace('wp:jetpack/subscriptions','wp:other/subscriptions'),
 x=>x.replace('class="fv-margin-strip__item"','class="tampered"'),
 x=>x.replace('finalvestige.com/focus/','bad.invalid/focus/')
];
for(let i=0;i<bad.length;i++)assert.equal(inspect(bad[i](base)).pass,false,'negative #'+i);
console.log('PASS '+(1+bad.length)+' synthetic source checks (no network/browser)');
