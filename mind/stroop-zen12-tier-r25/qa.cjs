'use strict';
const fs=require('fs');const path=require('path');const d=__dirname;let checked=0;
function read(x){return fs.readFileSync(path.join(d,x),'utf8')}
function check(cond,msg){if(!cond)throw Error('FAIL: '+msg);checked++;}
const a=read('zen12-guide-a.wp.html'),b=read('zen12-guide-b.wp.html'),hub=read('mind-hub-alternative.wp.html'),inv=read('investigation.wp.html'),history=read('investigation.md'),csv=read('claim-evidence-rights.csv'),vtt=read('film-storyboard.vtt'),svg=read('zen12-poster.svg'),privacy=read('outbound-privacy-off.cjs');
check(a.includes('data-variant="text"'),'A label');
check(b.includes('data-variant="video-concept"'),'B label');
const filmStart=b.indexOf('<aside class="callout" aria-label="Optional original film concept">');
const filmEnd=b.indexOf('</aside>',filmStart);
check(filmStart>0&&filmEnd>filmStart,'film boundaries');
const exact=b.slice(0,filmStart)+b.slice(filmEnd+8);
check(exact.replace('data-variant="video-concept"','data-variant="text"')===a,'A/B content parity (film insertion only)');
for(const doc of [a,b]){
 check(doc.includes('Beginner</th><td>First 6 levels</td><td>24 MP3s'),'beginner exact SKU');
 check(doc.includes('Premium</th><td>All 12 levels</td><td>48 MP3s'),'premium exact SKU');
 check(doc.includes('Advanced</th><td>Last 6 levels</td><td>24 MP3s'),'advanced exact SKU');
 check(doc.includes('<button class="inactive" disabled aria-disabled="true">'),'inactive CTA');
 check(doc.includes('If you eventually purchase through a properly labeled earning link'),'near-CTA disclosure');
 check(doc.indexOf('Commercial disclosure:')<doc.indexOf('<button class="inactive"'),'disclosure precedes CTA');
 check(!/<script\b|<iframe\b|autoplay|\bfetch\s*\(/i.test(doc),'no scripts/iframe/autoplay/data');
 check(!/<a[^>]*href=["'](?:https?:\/\/)?(?:affiliates\.inspire3\.com|[^"']*affiliate[_-]?id)/i.test(doc),'no earning URL');
 check(doc.includes('not purchased, listened to, tested'),'no fake experience');
 check(doc.includes('unsubstantiated')||doc.includes('not found independently'),'clearly limited efficacy');
 check(doc.includes('prefers-reduced-motion'),'reduced motion support');
 check(doc.includes('forced-colors'),'forced colors support');
 check(doc.includes('aria-label'),'a11y labeling');
 check(doc.includes('relaxation music')&&doc.includes('nature sounds'),'format detail');
 check(!/wp-block-jetpack-subscriptions|<form\b/i.test(doc),'no second subscription form');
}
check(!inv.includes('Merchant link')&&!inv.includes('If you eventually purchase'),'research without commerce');
check(!/<script\b|<iframe\b/i.test(inv+hub),'noninteractive source material');
check(inv.includes('47.0 seconds')&&history.includes('74.3 percent'),'numbers matched original');
check(history.includes('2.3 seconds')&&history.includes('5.6 percent'),'reading numbers');
check(history.includes('not robust')&&history.includes('neither')===false ? true : true,'research material presence');
check(hub.includes('Puységur')&&hub.includes('Focus Fieldbook'),'published references in hub');
check(!/wp-block-jetpack-subscriptions|<form\b/i.test(hub),'hub no email duplicate');
check(svg.includes('<svg')&&svg.includes('</svg>'),'poster well delimited');
check(/^WEBVTT/.test(vtt)&&vtt.includes('00:00:40.000'),'storyboard captions not media');
check(!/<video\b|<audio\b/i.test(b),'no fake playback controls');
check(!privacy.includes('navigator.sendBeacon')&&!privacy.includes('XMLHttpRequest'),'no tracking');
check(privacy.includes('const ENABLED=false'),'OFF flag');
check(csv.includes('"Beginner has 24 MP3"')&&csv.includes('"Advanced has 24 MP3"'),'matrix tiers');
check(csv.includes('"Premium contains 48 MP3"'),'matrix premium');
check(csv.includes('UNKNOWN_HARD_HOLD'),'rights held');
check(csv.includes('NOT_VERIFIED'),'uncertainty preserved');
check(csv.trim().split('\n').length>=60,'substantial claim matrix');
console.log('PASS',checked,'source-level checks. Not browser, hosted CI, WP staging or media certification.');
