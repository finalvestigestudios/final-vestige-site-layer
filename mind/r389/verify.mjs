// FV Mind R389: offline, read-only, reproducible safety verifier.
// Run from repository root: node mind/r389/verify.mjs
// This does not connect to WordPress, track users, or activate an affiliate URL.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const load = (name) => readFileSync(new URL(name, import.meta.url), 'utf8');
const article = load('THE_BEAR_YOU_WERE_TOLD_NOT_TO_SEE.md');
const a = load('ZEN12_A_TEXT_GUIDE.html');
const b = load('ZEN12_B_OPTIONAL_42S.html');
const hub = load('MIND_HUB_WORDPRESS_LAYOUT_REVIEW_ONLY.html');
const vtt = load('R389_CAPTIONS.vtt');
const svg = load('R389_WHITE_BEAR_POSTER.svg');
const matrix = JSON.parse(load('CLAIMS_RIGHTS_RELEASE_MATRIX.json'));
const handoff = load('CONVERSION_ACCEPTANCE_CREATOR_HANDOFF.md');
const failures = [];
let count = 0;
function check(name, predicate) {
  ++count;
  if (!predicate) failures.push(name);
}
function core(page) {
  const match = page.match(/(<section id="research">[\s\S]*?)<\/main>/i);
  return match ? match[1] : '';
}
function safe(page, name) {
  const block = /<(?:script|iframe|form|video|audio|object|embed)\b|javascript:|\bon(?:load|click|error)\s*=|http-equiv\s*=\s*["']refresh/i;
  const merchant = /<a\s+[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)(?:\/|["'])/i;
  check(name+':no active script/iframe/form/media', !block.test(page));
  check(name+':no active merchant link', !merchant.test(page));
  check(name+':draft noindex', /name="robots" content="noindex,nofollow"/.test(page));
  check(name+':native disabled CTA', /<button\s+type="button" disabled aria-describedby="hold-reason">/.test(page));
  check(name+':plain affiliate disclosure', page.includes('Final Vestige may earn a commission at no additional cost to you'));
  check(name+':adjacent disclosure', /class="disclosure"[\s\S]{0,500}<\/p><button\s+type="button" disabled/.test(page));
  check(name+':free established route', page.includes('https://finalvestige.com/focus/'));
  check(name+':no duplicate list', !/type=["']email["']|action=["']https?:\/\//i.test(page));
  check(name+':no affiliate query tokens', !/\b(?:hop|aff_id|affiliate_id|tracking_id|click_id)=/i.test(page));
  check(name+':language and viewport', /<html lang="en">/.test(page) && /name="viewport"/.test(page));
  check(name+':keyboard focus style', /focus-visible/.test(page));
  check(name+':reduced motion', /prefers-reduced-motion/.test(page));
}
safe(a,'A'); safe(b,'B');
check('A and B identical editorial buyer body', core(a).length > 2500 && core(a) === core(b));
check('B contains original optional poster', b.includes('R389_WHITE_BEAR_POSTER.svg'));
check('A does not contain B poster', !a.includes('R389_WHITE_BEAR_POSTER.svg'));
check('B film clearly not playable', b.includes('No encoded playable video'));
check('B image has alt text and fixed dimensions', /<img[^>]*width="1280" height="720"[^>]*alt=/.test(b));
check('B transcript behind accessible details', /<details><summary>/.test(b));
check('Poster is 16:9 and original SVG', /viewBox="0 0 1280 720"/.test(svg) && /<title id="t">/.test(svg));
check('Six caption cues', (vtt.match(/-->/g)||[]).length===6);
check('Caption format', vtt.startsWith('WEBVTT\n'));
const cues = vtt.split(/\n\n/).slice(1).map(x=>x.split('\n').slice(2).join(' ').trim());
const transcript = (b.match(/<details><summary>Open full transcript<\/summary><p>(.*?)<\/p><\/details>/) || [,''])[1];
check('Caption and transcript word-identical', cues.join(' ')===transcript);
check('Transcript <=110 words and nonempty', transcript.split(/\s+/).length >=70 && transcript.split(/\s+/).length<=110);
check('Article >= 2000 words', article.trim().split(/\s+/).length>=2000);
check('Article cites original + later meta evidence', article.includes('10.1037/0022-3514.53.1.5') && article.includes('10.1177/1745691619898795'));
check('Article has historical consent boundary', article.includes('Puységur')&&article.includes('consent'));
check('Hub four streams and noindex', /Perception & Attention/.test(hub) && /History of Suggestion/.test(hub) && /Practice & Reflection/.test(hub)&&/Tools Under Review/.test(hub)&&/noindex,nofollow/.test(hub));
check('Hub has no active merchant or new email form', !/<form\b|href=["']https:\/\/zen12\.com/i.test(hub));
check('Matrix 35 claims', matrix.claims.length===35);
check('Matrix >=30 explicitly held gates', matrix.release_gates.length>=30 && matrix.release_gates.every(g=>g.status==='HARD_HOLD'));
check('Authorization remains unverified', matrix.claims.some(c=>c.text.includes('accepted as Inspire3')&&c.classification==='PERMISSION_UNVERIFIED'));
check('Handoff maintains net revenue unknown', handoff.includes('NOT COMPUTABLE'));
check('Handoff preserves the named owner PRs', handoff.includes('PR #49')&&handoff.includes('PR #172'));
for(const f of failures) console.error('FAIL '+f);
if(failures.length) {console.error('R389 FAILED '+failures.length+'/'+count+' checks'); process.exitCode=1;}
else console.log('R389 PASS '+count+'/'+count+' checks; 6 caption cues; no active earning link or video');
