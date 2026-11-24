const fs=require("node:fs"), assert=require("node:assert/strict");
const h=fs.readFileSync(__dirname+"/edition.html","utf8"),t=fs.readFileSync(__dirname+"/edition.txt","utf8");
const checks=[
()=>assert.match(h,/<html lang="en">/),
()=>assert.match(h,/name="viewport"/),
()=>assert.equal((h.match(/<h1\b/g)||[]).length,1),
()=>assert.equal((h.match(/data-role="primary-cta"/g)||[]).length,1),
()=>assert.equal((h.match(/<a href=|<a data-role=/g)||[]).length,3),
()=>assert.match(t,/Subject: The mysterious boat that traveled on paper/),
()=>assert.match(h,/Two Japanese archives reveal more about the story than the alleged landing/),
()=>assert.match(t,/not proof of an extraterrestrial encounter/),
()=>assert.match(h,/not proof of an extraterrestrial encounter/),
()=>assert.match(h,/utm_source=dispatch&amp;utm_medium=email&amp;utm_campaign=dispatch_2026_11&amp;utm_content=dispatch_002_utsuro/),
()=>assert.match(t,/utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_2026_11&utm_content=dispatch_002_utsuro/),
()=>assert.doesNotMatch(h,/<(?:script|iframe|form|img)\b/i),
()=>assert.doesNotMatch(h+t,/zen12\.com|hypnosislive\.com|refersion/i),
()=>assert.match(h,/\[\[VALID_POSTAL_ADDRESS_REQUIRED\]\]/),
()=>assert.match(t,/\[\[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED\]\]/),
()=>assert.match(h,/role="presentation"/),
()=>assert.match(h,/max-width:600px/),
()=>assert.match(h,/color:#ffffff/),
()=>assert.match(t,/Question of the week:/),
()=>assert.match(h,/https:\/\/www\.city\.kuki\.lg\.jp/),
()=>assert.match(t,/https:\/\/prtimes\.jp/)
];checks.forEach(f=>f());console.log(checks.length+" static checks passed");
