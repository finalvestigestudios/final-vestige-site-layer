/** R320 review-only UI decision contract. NOT a WordPress plugin, auth boundary, or deployable provider adapter.
 * The attestation is an interface placeholder: a caller can forge these inputs unless Claude
 * verifies it against actual Jetpack post-submit behavior. Never use it for lead metrics. */
export function evaluateGiftReview(input={}){
  if(input===null||typeof input!=="object"||Array.isArray(input))throw Error("BAD_INPUT");
  const keys=Object.keys(input);
  if(keys.some(k=>/(^|_)(email|phone|address|name|ip|recipient|contact|subscriber)(_|$)/i.test(k)))throw Error("PII_FIELD_REJECTED");
  const trustedUI= input.user_action==="submitted_subscribe_form" &&
    input.widget_response==="acknowledged_attempt" &&
    input.adapter_attestation===true &&
    input.adapter_origin==="validated_jetpack_ui_adapter";
  return Object.freeze({
    gift_visible:Boolean(trustedUI),
    reason:trustedUI?"WIDGET_ATTEMPT_ACKNOWLEDGED_NOT_CONFIRMED":"NO_TRUSTED_UI_ATTEMPT",
    confirmed_signup:null, email_delivery_eligible:null, welcome_received:null,
    counted_as_lead:false, counted_as_sale:false, send_authorized:false
  });
}
