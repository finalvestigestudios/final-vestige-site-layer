/* Final Vestige R32 WordPress HTML renderer: offline only. No network or CMS calls.
   node render.cjs [investigation|A|B] [output-path]
   Requires local INVESTIGATION.md or ZEN12-INDEPENDENT-GUIDE.md next to this file.
   Inline style is fully scoped to .fv-mind32, no external scripts or fonts. */
'use strict';
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function inline(s){
  let text=esc(s);
  // Links are parsed after escaping; direct merchant URLs are always NON-CLICKABLE.
  text=text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,(_,label,href)=>{
    const host=new URL(href).hostname.toLowerCase();
    if(host==='zen12.com'||host.endsWith('.zen12.com')||host==='inspire3.com'||host.endsWith('.inspire3.com'))
      return '<span class="fv-mind32-seller" title="Seller source cited for research, not an active product link">'+label+' [seller source: '+esc(host)+']</span>';
    return '<a href="'+esc(href)+'" rel="noopener noreferrer">'+label+'</a>';
  });
  text=text.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>');
  return text;
}
function markdown(md){
 const L=md.replace(/\r\n/g,'\n').split('\n');let out=[],para=[],list=[],kind='',i=0;
 const flushPara=()=>{if(para.length){out.push('<p>'+inline(para.join(' '))+'</p>');para=[];}};
 const flushList=()=>{if(list.length){out.push('<'+kind+'>'+list.map(x=>'<li>'+inline(x)+'</li>').join('')+'</'+kind+'>');list=[];kind='';}};
 while(i<L.length){
  const s=L[i],t=s.trim(); if(!t){flushPara();flushList();i++;continue;}
  if(/^\|.*\|$/.test(t)&&/^\|[ -:|]+\|$/.test((L[i+1]||'').trim())){
    flushPara();flushList();const head=t.split('|').slice(1,-1).map(x=>x.trim());i+=2;const trs=[];
    while(i<L.length&&/^\|.*\|$/.test(L[i].trim())){trs.push(L[i].trim().split('|').slice(1,-1).map(x=>x.trim()));i++;}
    out.push('<div class="fv-mind32-tablewrap" tabindex="0" aria-label="Scrollable seller package comparison"><table><thead><tr>'+head.map(x=>'<th scope="col">'+inline(x)+'</th>').join('')+'</tr></thead><tbody>'+trs.map(row=>'<tr>'+row.map(x=>'<td>'+inline(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>');continue;
  }
  const h=t.match(/^(#{1,4})\s+(.+)$/);
  if(h){flushPara();flushList();const level=Math.min(h[1].length,3);out.push('<h'+level+'>'+inline(h[2])+'</h'+level+'>');i++;continue;}
  if(t==='---'){flushPara();flushList();out.push('<hr aria-hidden="true">');i++;continue;}
  const m=t.match(/^([-*]|\d+\.)\s+(.+)$/);
  if(m){flushPara();const k=m[1]==='-'||m[1]==='*'?'ul':'ol';if(list.length&&kind!==k)flushList();kind=k;list.push(m[2]);i++;continue;}
  flushList();para.push(t);i++;
 }
 flushPara();flushList();return out.join('\n');
}
const style=`<style>
.fv-mind32{--bg:#090a0a;--panel:#101211;--ink:#f4efe6;--body:#ded8cc;--muted:#b6b0a4;--gold:#c9a36d;--line:#444036;color:var(--body);background:var(--bg);font:400 1.0625rem/1.75 system-ui,-apple-system,"Segoe UI",sans-serif;padding:clamp(24px,5vw,70px) clamp(16px,3vw,38px);overflow-wrap:anywhere}
.fv-mind32 *{box-sizing:border-box}.fv-mind32 a{color:#e8c38c;text-decoration:underline;text-underline-offset:4px}.fv-mind32 a:hover{color:#fff}.fv-mind32 :focus-visible{outline:3px solid #fff;outline-offset:4px}
.fv-mind32 .fv-mind32-shell{max-width:1080px;margin:0 auto}.fv-mind32 .fv-mind32-kicker{font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);font-weight:800}
.fv-mind32 h1,.fv-mind32 h2,.fv-mind32 h3{font-family:Georgia,"Times New Roman",serif;font-weight:400;color:var(--ink);letter-spacing:-.022em;text-wrap:balance;line-height:1.17}
.fv-mind32 h1{font-size:clamp(2.6rem,7vw,5.6rem);margin:.35em 0 .45em}.fv-mind32 h2{font-size:clamp(1.8rem,3.7vw,2.75rem);margin:2.1em 0 .7em;padding-top:18px;border-top:1px solid var(--line)}.fv-mind32 h3{font-size:1.5rem;margin:1.6em 0 .55em}
.fv-mind32 p,.fv-mind32 li{max-width:73ch}.fv-mind32 p{margin:1.05em 0}.fv-mind32 ul,.fv-mind32 ol{padding-left:1.5rem}.fv-mind32 li+li{margin-top:.6em}
.fv-mind32 strong{color:var(--ink)}.fv-mind32 em{color:#f0e2cb}.fv-mind32 hr{border:0;border-top:1px solid var(--line);margin:3rem 0}
.fv-mind32 table{width:100%;border-collapse:collapse;font-size:.94rem;line-height:1.5}.fv-mind32 th,.fv-mind32 td{padding:15px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
.fv-mind32 th{color:var(--ink);background:#20211e}.fv-mind32 .fv-mind32-tablewrap{overflow-x:auto;max-width:100%;border:1px solid var(--line)}
.fv-mind32 .fv-mind32-seller{color:var(--muted);font-style:italic}
.fv-mind32 .fv-mind32-status{max-width:72ch;border:1px solid #7d6243;background:#16140e;padding:20px 24px;margin:2rem 0}
.fv-mind32 .fv-mind32-badge{display:inline-block;color:#f1d3a5;border:1px solid #8b714e;padding:6px 10px;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em}
.fv-mind32 .fv-mind32-action{border-left:4px solid var(--gold);padding:22px 26px;background:var(--panel);margin:2.5rem 0}
.fv-mind32 button[disabled]{min-height:52px;max-width:100%;padding:13px 24px;border:1px solid #696258;background:#373732;color:#f0e9da;cursor:not-allowed;font:700 1rem system-ui;opacity:1}
.fv-mind32 .fv-mind32-optional{border:1px solid #67543c;background:#101211;margin:1.5rem 0 2.5rem;padding:20px;max-width:760px}
.fv-mind32 .fv-mind32-optional .fv-mind32-poster{width:100%;max-height:410px;object-fit:contain;display:block}
.fv-mind32 .fv-mind32-optional summary{cursor:pointer;min-height:44px;color:var(--ink);padding:12px 0}
.fv-mind32 .fv-mind32-optional p{font-size:1rem}
.fv-mind32 .fv-mind32-small{font-size:.875rem;color:var(--muted)}
@media(min-width:900px){.fv-mind32 .fv-mind32-shell{padding-inline:clamp(0px,4vw,45px)}}
@media(max-width:390px){.fv-mind32{font-size:1rem}.fv-mind32 .fv-mind32-optional{padding:12px}}
@media(prefers-reduced-motion:reduce){.fv-mind32 *, .fv-mind32 *:before,.fv-mind32 *:after{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
@media(forced-colors:active){.fv-mind32 .fv-mind32-action,.fv-mind32 .fv-mind32-status{border:2px solid CanvasText}}
@media print{.fv-mind32{background:#fff;color:#000}.fv-mind32 :is(h1,h2,h3,strong,em,a){color:#000!important}}
</style>`;
function filmBlock(){
 return '<aside class="fv-mind32-optional" data-variant-only="B" aria-labelledby="fv-mind32-film-title"><span class="fv-mind32-badge">Optional film concept — not hosted</span><h2 id="fv-mind32-film-title">Forty seconds: The missed second signal</h2><img class="fv-mind32-poster" src="" alt="Storyboard concept: two letters appear one after the other; the second remains visible on paper while attention is processing the first" hidden><p>Original 40-second short-film storyboard and captions are source-controlled for review. There is no hosted film or playback control in this draft. The complete spoken-message transcript follows; the text guide works without any film.</p><details><summary>Read the 40-second transcript</summary><p>Two letters. One stream. Both hit the screen. But in experiments with rapid sequences, people who identify the first often fail to report the second. Researchers call this an attentional blink. It depends on timing and the task. Meditation research on attention is interesting, but it does not prove any particular audio recording works. Zen12 offers twelve-minute sessions in different packages. Read what is actually included. Try a free routine first. Examine the evidence before you buy.</p></details><p class="fv-mind32-small">Video release gate: only show an actual native video element after approved first-party hosting, an accurate poster URL, tested synced VTT captions, transcript parity and QA; no autoplay.</p></aside>';
}
function render(md,type='investigation'){
 const isGuide=type==='A'||type==='B',prefix='<section class="fv-mind32" data-content="'+(isGuide?'zen12-guide':'investigation')+'" data-variant="'+(isGuide?type:'none')+'"><div class="fv-mind32-shell">'+style+'<p class="fv-mind32-kicker">Final Vestige Studios / '+(isGuide?'Independent Tools Guide':'Mind &amp; Perception Investigation')+'</p>',
  top='<div class="fv-mind32-status"><strong>Unpublished source-controlled draft.</strong> '+(isGuide?'All merchant-earning links and affiliate actions disabled until verification and release approval.':'Historical/scientific research; no commercial recommendation in this investigation.')+'</div>';
 let body=markdown(md);
 // The source-only merchant URLs are plain text; this button is inert and has no href.
 if(isGuide){
   const disclosure='<section class="fv-mind32-action" aria-labelledby="fv-mind32-action-title"><h2 id="fv-mind32-action-title">Offer information — not yet available</h2><p>If you purchase through an approved earning link in the future, Final Vestige may earn a commission at no additional cost to you.</p><button type="button" disabled aria-disabled="true">Product link not yet authorized</button><p class="fv-mind32-small">No merchant checkout destination, click tracking or subscription form is connected.</p></section>';
   body=(type==='B'?filmBlock():'')+body+disclosure;
 }
 return prefix+top+'<article>'+body+'</article><p class="fv-mind32-small">Final Vestige editorial draft — not a live publication or product endorsement.</p></div></section>';
}
module.exports={render,markdown,inline,filmBlock};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),kind=process.argv[2]||'A',out=process.argv[3];
 const input=fs.readFileSync(path.join(__dirname,kind==='investigation'?'INVESTIGATION.md':'ZEN12-INDEPENDENT-GUIDE.md'),'utf8');
 const html=render(input,kind);
 if(out)fs.writeFileSync(out,html);else process.stdout.write(html);
}
