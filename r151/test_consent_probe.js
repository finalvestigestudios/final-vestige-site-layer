/* Offline R151 regression / V8 + native Node compatible. Synthetic pseudonyms only. */
(function () {
  const lib = typeof require === "function" ? require("./consent_probe.js") : globalThis.FVConsent;
  function run() {
    let passed=0; const failures=[];
    const snap = {total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0,imported_last_24h:0,
      follower_wpcom:3,follower_email:0,newsletter_enabled:true,new_posts_auto_send:false,
      format:"full",as_of:"2026-11-06T02:38:05Z"};
    const key = n => String(n).padStart(32,"a");
    const valid = (n,status="Subscribed",confirmed=true,consent=true,date="2026-11-05T20:00:00Z") =>
      ({opaque_key:key(n),email_subscription:status,confirmation_proof:confirmed,consent_proof:consent,confirmed_at_utc:date});
    function check(name,fn) {try {if(!fn())throw Error("assertion false");passed++;} catch(e){failures.push(name+": "+e.message)}}
    function throws(fn) {try{fn();return false}catch{return true}}
    const a=lib.audit(snap,null,false);
    check("aggregate only unknown eligibility",()=>a.exact_email_eligible_count===null);
    check("confirmed dashboard not event",()=>a.confirmed_signup_count===null);
    check("wpcom followers not zero eligible",()=>!a.email_only_zero_proves_zero_eligible);
    check("overlapping counts preserved",()=>a.reasons.includes("DASHBOARD_CATEGORIES_OVERLAP_OR_DIFFERENT_DENOMINATORS"));
    check("never send",()=>a.release==="HOLD_UNSENT"&&a.commercial_release==="HOLD_MERCHANT");
    check("partial unknown eligibility",()=>lib.audit(snap,[valid(1)],false).exact_email_eligible_count===null);
    check("partial count known reviewed only",()=>lib.audit(snap,[valid(1)],false).provider_reviewed_count===1);
    check("complete known count",()=>lib.audit(snap,[valid(1)],true).exact_email_eligible_count===1);
    check("complete zero valid not proof all time",()=>lib.audit(snap,[valid(1,"Not confirmed",false,false,null)],true).confirmed_signup_count===0);
    check("no event without time",()=>lib.audit(snap,[valid(1,"Subscribed",true,true,null)],true).confirmed_signup_count===0);
    check("not confirmed excluded",()=>lib.audit(snap,[valid(1,"Not confirmed")],true).exact_email_eligible_count===0);
    check("reader only excluded",()=>lib.audit(snap,[valid(1,"Not subscribed")],true).exact_email_eligible_count===0);
    check("paused excluded",()=>lib.audit(snap,[valid(1,"Emails paused")],true).exact_email_eligible_count===0);
    check("bounced excluded",()=>lib.audit(snap,[valid(1,"Bounced")],true).exact_email_eligible_count===0);
    check("not sending excluded",()=>lib.audit(snap,[valid(1,"Not sending")],true).exact_email_eligible_count===0);
    check("suppressed excluded",()=>lib.audit(snap,[valid(1,"Suppressed")],true).exact_email_eligible_count===0);
    check("no consent excluded",()=>lib.audit(snap,[valid(1,"Subscribed",true,false)],true).exact_email_eligible_count===0);
    check("no confirmation proof excluded",()=>lib.audit(snap,[valid(1,"Subscribed",false,true)],true).exact_email_eligible_count===0);
    check("complete mixed states",()=>lib.audit(snap,[valid(1),valid(2,"Bounced"),valid(3)],true).exact_email_eligible_count===2);
    check("duplicate identity rejected",()=>throws(()=>lib.audit(snap,[valid(1),valid(1)],true)));
    check("raw email rejected",()=>throws(()=>lib.audit(snap,[{...valid(1),email:"person@example.com"}],true)));
    check("email in key rejected",()=>throws(()=>lib.audit(snap,[{...valid(1),opaque_key:"person@example.com"}],true)));
    check("unsafe URL rejected",()=>throws(()=>lib.audit(snap,[{...valid(1),utm_campaign:"https://bad/"}],true)));
    check("unsafe asset rejected",()=>throws(()=>lib.audit(snap,[{...valid(1),source_asset_id:"other person"}],true)));
    check("bad time rejected",()=>throws(()=>lib.audit(snap,[{...valid(1),confirmed_at_utc:"yesterday"}],true)));
    check("not a full export rejected",()=>throws(()=>lib.audit(snap,null,true)));
    check("wrong snapshot negative rejected",()=>throws(()=>lib.audit({...snap,total:-1},null,false)));
    check("bad snapshot missing count",()=>throws(()=>lib.audit({...snap,paid:undefined},null,false)));
    check("no write promoted if all synthetic checks true",()=>lib.audit(snap,[valid(1)],true).release==="HOLD_UNSENT");
    check("auto send flagged",()=>lib.audit({...snap,new_posts_auto_send:true},null,false).reasons.includes("AUTO_SEND_ENABLED_RELEASE_STOP"));
    check("source tags do not equal paid orders",()=>!Object.keys(lib.audit(snap,[{...valid(1),source_asset_id:"yt_481",utm_campaign:"mind_pilot_2026_11"}],true)).includes("paid_orders"));
    const summary={passed, failed:failures.length,failures};
    if(typeof module!=="undefined"&&module.exports){module.exports={run}; if(require.main===module){console.log(JSON.stringify(summary));if(failures.length)process.exitCode=1;}}
    return summary;
  }
  globalThis.FV_TEST_RESULT=run();
})();
