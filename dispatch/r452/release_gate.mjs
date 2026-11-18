// R452 pure, read-only draft QA. No network, subscriber access, email or commerce execution.
export function reconcileAudience(s) {
 const a=s?.subscribers?.stats_list,b=s?.subscribers?.stats_rollup,n=s?.subscribers?.newsletter;
 if(!a||!b||!n)throw Error("Missing first-party classified feeds");
 for(const v of [a.all,a.email_subscriber,a.reader_subscriber,a.unconfirmed_subscriber,b.email,b.wpcom,b.total,n.total,n.confirmed,n.unconfirmed_additional])if(!Number.isInteger(v)||v<0)throw Error("Invalid provider count");
 const deviations=[];
 if(a.email_subscriber!==b.email)deviations.push("email_subscriber_rows_vs_follower_email");
 if(a.reader_subscriber!==b.wpcom)deviations.push("reader_subscriber_rows_vs_follower_wpcom");
 if(n.confirmed!==a.email_subscriber)deviations.push("newsletter_confirmed_vs_subscriber_email");
 if(n.total!==a.all)deviations.push("newsletter_total_vs_subscriber_all");
 return {classification_conflicts:deviations,eligible_by_newsletter:n.confirmed,unconfirmed_additional:n.unconfirmed_additional,verified_new_external_signups:null,received_welcome_proved:false,stats_follower_email:b.email,stats_follower_wpcom:b.wpcom};
}

export function evaluateRelease(s) {
 if(!s||!Array.isArray(s.commercial_positions)||!Array.isArray(s.editorial_positions))throw Error("Missing campaign allocation");
 const errors=[];
 if(s.commercial_positions.join(",")!=="3,5"||s.editorial_positions.join(",")!=="1,2,4,6")errors.push("founder_4_to_2_allocation_changed");
 const a=s.affiliate||{},e=s.email||{};
 for(const k of ["account_approved","email_channel_permission","issued_earning_url","current_checkout_verified","published_approved_buyer_guide"])if(a[k]!==true)errors.push("merchant_"+k);
 for(const k of ["founder_final_approval","postal_address_verified","rendered_unsubscribe_verified","actual_jetpack_preview_verified","received_welcome_verified","send_authorized"])if(e[k]!==true)errors.push("email_"+k);
 if(s.release_status!=="FOUNDER_APPROVED_FINAL")errors.push("explicit_final_status_missing");
 const audience=reconcileAudience(s);
 if(audience.classification_conflicts.length)errors.push("provider_classifications_conflict");
 if(!Number.isInteger(s?.subscribers?.confirmed_new_external_acquisitions)||s.subscribers.confirmed_new_external_acquisitions<0)errors.push("new_signup_proof_missing");
 return {status:errors.length?"HOLD_UNSENT":"RELEASE_GATES_LOGICALLY_SATISFIED_NOT_SENT",holds:errors,audience};
}

export function inspectOfflineEmail(html,text) {
 const errors=[];
 if(!/<!doctype html>/i.test(html)||!/<html[^>]+lang="en"/i.test(html))errors.push("semantic_html_missing");
 if(!/<table[^>]+role="presentation"/i.test(html)||!/<h1\b/i.test(html))errors.push("email_layout_missing");
 if(/<script\b|<iframe\b|<img\b/i.test(html))errors.push("nonessential_active_media");
 if(/utm_(source|medium|campaign|content)=|tracking\.gif/i.test(html))errors.push("tracking_in_review");
 if(!/RENDERED_JETPACK_UNSUBSCRIBE_REQUIRED/.test(html)||!/VALID_FV_POSTAL_ADDRESS_REQUIRED/.test(html))errors.push("hard_hold_footer_missing");
 if(!/NOT AVAILABLE/.test(html)||/<a[^>]*href=["'][^"']*(?:\/guide\/|\/checkout\/|refersion\.com\/click)/i.test(html))errors.push("unapproved_offer_link_or_missing_hold");
 if(!/may earn a commission/i.test(html)||!/may earn a commission/i.test(text))errors.push("proximity_disclosure_missing");
 if(/<button\b|aria-hidden="true"/i.test(html))errors.push("email_control_or_hidden_text");
 if(!/Source|Sources/i.test(html))errors.push("source_section_missing");
 if(!/DO NOT COPY INTO A LIVE POST/.test(text))errors.push("plaintext_not_hard_held");
 return errors;
}

export function realizedNetPerThousand({qualified_human_sessions,orders}={}) {
 if(!Number.isInteger(qualified_human_sessions)||qualified_human_sessions<=0||!Array.isArray(orders)||!orders.length)return null;
 if(!orders.every(o=>o&&o.verified_settled===true&&[o.gross,o.refunds,o.fees].every(v=>typeof v==="number"&&Number.isFinite(v)&&v>=0)))return null;
 return 1000*orders.reduce((sum,o)=>sum+o.gross-o.refunds-o.fees,0)/qualified_human_sessions;
}
