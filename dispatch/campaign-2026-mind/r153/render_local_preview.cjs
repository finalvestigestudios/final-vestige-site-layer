'use strict';
// OFFLINE ONLY: renders an independent, NOT-Jetpack static reviewer mock
// from the optional R153 Markdown editorial. No network, email, DOM or send.
const SITE='https://finalvestige.com/focus/';
function escape(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function fmt(s){
 let safe=escape(s);
 safe=safe.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
 safe=safe.replace(/\*([^*]+)\*/g,'<em>$1</em>');
 return safe.replace(/https:\/\/[^\s<)]+/g, (url)=>{
   let suffix='';while(/[.,;:]$/.test(url)){suffix=url.slice(-1)+suffix;url=url.slice(0,-1);}
   return '<a style="color:#174a59;text-decoration:underline" href="'+url+'">'+url+'</a>'+suffix;
 });
}
function parse(markdown){
 if(typeof markdown!=='string'||markdown.length>20000)throw Error('bounded markdown required');
 const subject=markdown.match(/^\*\*Subject:\*\* (.+)$/m)?.[1];
 const preheader=markdown.match(/^\*\*Preheader:\*\* (.+)$/m)?.[1];
 if(!subject||!preheader)throw Error('subject/preheader required');
 const a=markdown.indexOf('\n---\n\nImagine');
 const b=markdown.indexOf('\n---\n**NOT-SENDABLE');
 if(a<0||b<a)throw Error('approved body delimiters missing');
 return {subject,preheader,body:markdown.slice(a+6,b).trim()};
}
function render(md){
 const x=parse(md);
 if(x.body.includes('[[APPROVED_')||x.body.includes('affiliates.inspire3.com'))
   throw Error('commercial destination forbidden');
 if((x.body.match(/\*\*Explore the Seven Day Focus Fieldbook:\*\*/g)||[]).length!==1)
   throw Error('one primary CTA required');
 const groups=x.body.split(/\n\s*\n/);
 const htmlParts=[];
 for(const group of groups){
  const s=group.trim();
  if(!s)continue;
  if(s.startsWith('**Explore the Seven Day Focus Fieldbook:**')){
   htmlParts.push('<p style="margin:22px 0 8px"><a href="'+SITE+'" style="display:inline-block;background:#b8955e;color:#090a0a;font-weight:700;text-decoration:none;padding:14px 20px;border-radius:2px;line-height:1.3">Explore the free Focus Fieldbook</a></p>');
  }else if(s==='**Sources and boundaries**'){
   htmlParts.push('<h2 style="font-family:Georgia,serif;font-size:22px;font-weight:400;margin:24px 0 8px;color:#111">Sources and boundaries</h2>');
  }else if(s.startsWith('- ')){
   htmlParts.push('<ul style="margin:8px 0 14px;padding-left:24px">'+s.split('\n').filter(y=>y.startsWith('- ')).map(y=>'<li style="margin:8px 0">'+fmt(y.slice(2))+'</li>').join('')+'</ul>');
  }else{
   htmlParts.push('<p style="margin:0 0 16px;line-height:1.65">'+fmt(s)+'</p>');
  }
 }
 const warning='REVIEW ONLY — NOT A JETPACK EMAIL PREVIEW — NEVER SEND. Physical address and native unsubscribe are NOT VERIFIED.';
 const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(x.subject)+' | UNSENT REVIEW</title></head>'+
 '<body style="margin:0;padding:0;background:#eae8e2;color:#1c1c1c;font-family:Arial,Helvetica,sans-serif">'+
 '<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent" aria-hidden="true">'+escape(x.preheader)+'</div>'+
 '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse"><tr><td align="center" style="padding:18px 12px">'+
 '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:640px;width:100%;border-collapse:collapse;background:#fff"><tr><td style="padding:28px 26px 24px">'+
 '<p style="font-size:11px;letter-spacing:2px;color:#755b2b;margin:0 0 18px">FINAL VESTIGE STUDIOS / THE DISPATCH</p>'+
 '<h1 style="font-family:Georgia,serif;font-weight:400;font-size:32px;line-height:1.12;margin:0 0 22px">'+escape(x.subject)+'</h1>'+
 htmlParts.join('')+
 '<p style="margin:30px 0 8px;padding:14px;background:#fff4e1;border:2px solid #8d5a14;color:#282015;font-size:14px"><strong>'+warning+'</strong></p>'+
 '<p style="font-size:12px;color:#4b4239">Publisher address: [[FV_VALID_PHYSICAL_POSTAL_ADDRESS_NOT_VERIFIED]]<br>Unsubscribe: [[JETPACK_DELIVERED_UNSUBSCRIBE_NOT_VERIFIED]]</p>'+
 '</td></tr></table></td></tr></table></body></html>';
 const txt='FINAL VESTIGE STUDIOS / THE DISPATCH\nREVIEW ONLY — NOT AN EMAIL. DO NOT SEND.\n\n'+
 'Subject: '+x.subject+'\nPreheader: '+x.preheader+'\n\n'+x.body+
 '\n\n'+warning+'\nPostal address: [[FV_VALID_PHYSICAL_POSTAL_ADDRESS_NOT_VERIFIED]]\nUnsubscribe: [[JETPACK_DELIVERED_UNSUBSCRIBE_NOT_VERIFIED]]\n';
 return {html,txt,subject:x.subject,preheader:x.preheader};
}
module.exports={parse,render};
