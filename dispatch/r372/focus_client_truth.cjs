"use strict";
/**
 * READ-ONLY REFERENCE for /focus/, NOT a drop-in deployment or a real confirmation API.
 * Browser query strings and Jetpack CSS classes are not authoritative subscription receipts.
 * A deliberately free PDF remains free regardless of newsletter eligibility.
 */
const PROBLEM = new Set(["error", "failed", "invalid_email", "blocked_email", "opted_out", "blocked"]);
const PENDING = new Set(["unconfirmed", "pending", "success", "subscribed", "confirmed", "true", "1"]);
function classifyFocusClient(search = "", className = "") {
  const params = new URLSearchParams(String(search).replace(/^\?/, ""));
  const values = params.getAll("subscribe");
  const value = values.length === 1 ? String(values[0]).trim().toLowerCase() : "";
  const classToken = /(?:^|\s)is-subscriber(?:\s|$)/.test(String(className));
  let state = "public_free_resource";
  if (values.length > 1) state = "ambiguous_client_signal";
  else if (values.length === 1 && PROBLEM.has(value)) state = "subscription_not_verified";
  else if (values.length === 1 && value) state = "await_provider_confirmation";
  else if (classToken) state = "reader_ui_signal_only";
  return Object.freeze({
    state,
    show_free_download: true,
    newsletter_status: "unknown_not_verified",
    confirmed_signup: false,
    emit_confirmed_signup: false,
    copy: state === "subscription_not_verified"
      ? "The newsletter signup has not been verified. You can still download the free Fieldbook below."
      : state === "await_provider_confirmation" || state === "ambiguous_client_signal"
      ? "If you requested The Dispatch, check your inbox for any confirmation message. The free Fieldbook is available below either way."
      : "The free Fieldbook is available below. Joining The Dispatch is optional and separate from downloading."
  });
}
module.exports = { classifyFocusClient };
