function verified(p){return !!p&&p.status==="verified"&&typeof p.checked_at==="string"&&/^\d{4}-\d\d-\d\dT/.test(p.checked_at)&&typeof p.evidence_url==="string"&&/^https:\/\/(github\.com|finalvestige\.com|inspire3\.com|zen12\.com|hypnosislive\.com)\//.test(p.evidence_url)}

function evaluate(issue,p){const commercial=[3,5].includes(issue);if(![1,2,3,4,5,6].includes(issue))throw Error("invalid issue");const missing=(commercial?delivery.concat(merchant):delivery).filter(k=>!verified(p?.[k]));return{issue,type:commercial?"commercial":"editorial",status:missing.length?"HOLD_UNSENT":"PREVIEW_REVIEW_ONLY_NEVER_AUTHORIZES_SEND",missing}}

function signups(events){const seen=new Set();let n=0;for(const e of events||[]){if(e?.provider!=="jetpack"||e?.email_subscription!=="subscribed"||!["confirmed_email_link","verified_wp_account"].includes(e?.confirmation)||e?.suppressed||e?.bounced||!/^anon_[a-z0-9_-]{12,}$/i.test(e?.id||"")||seen.has(e.id))continue;seen.add(e.id);n++}return {confirmed_signup:n,privacy:"aggregated synthetic count only"}}

function revenue(c){if(!c||![7,30].includes(c.days)||c.session_source!=="verified_first_party"||!Number.isInteger(c.qualified_sessions)||c.qualified_sessions<1||!Array.isArray(c.orders)||!c.orders.length)return{status:"NOT_COMPUTABLE"};let net=0;const ids=new Set();for(const o of c.orders){if(!["settled_payhip_order","partner_confirmed_paid_conversion"].includes(o?.source)||o?.status!=="settled"||!o?.id||ids.has(o.id)||![o.gross,o.refunds,o.fees].every(x=>Number.isInteger(x)&&x>=0)||o.refunds>o.gross)return{status:"NOT_COMPUTABLE"};ids.add(o.id);net+=o.gross-o.refunds-o.fees}return{status:"INPUTS_VERIFIED_IN_SYNTHETIC_FIXTURE_ONLY",paid_orders:ids.size,net_cents:net,net_usd_per_1000:Number((net*10/c.qualified_sessions).toFixed(2))}}

function firstParty(u){return typeof u==="string"&&/^https:\/\/finalvestige\.com\/(mind|focus|free-resources)\//.test(u)&&!u.includes("[[")&&!u.includes("@")&&!/[?&](ref|aff|affiliate|email|uid)=/i.test(u)}

export {verified,evaluate,signups,revenue,firstParty};
