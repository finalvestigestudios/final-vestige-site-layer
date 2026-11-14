// Source-only offline release validator; NO sending, no merchant activation.
export function evaluate(data) {
  const problems = [];
  const { subject, preheader, kind, html, plain, sourceLinks, ctaUrl, approval, mailingAddressVerified, unsubscribeVerified } = data;
  if (!subject || subject.length > 65) problems.push("subject: length/content");
  if (!preheader || preheader.length > 130) problems.push("preheader: length/content");
  if (kind !== "editorial") problems.push("this slot must remain editorial");
  if (!html?.includes('lang="en"') || !html?.includes('role="presentation"')) problems.push("HTML accessibility skeleton");
  if (!html?.includes('OFFLINE REVIEW ONLY') || !plain?.includes('HOLD_UNSENT')) problems.push("offline review safety labels");
  if (!html?.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]") || !html?.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")) problems.push("release placeholders missing");
  if (html?.includes("<img") || html?.includes("<script") || html?.includes("<form")) problems.push("unsupported embedded content");
  if ((html?.match(/<h1\b/g) || []).length !== 1) problems.push("HTML heading hierarchy");
  if (!plain?.includes(ctaUrl) || !html?.includes(`href="${ctaUrl}"`)) problems.push("single CTA alignment");
  if (!sourceLinks || sourceLinks.length < 3 || sourceLinks.some(u => !u.startsWith("https://"))) problems.push("source references");
  if (/(?:guaranteed results|cures|clinically proven|buy now)/i.test(plain || "")) problems.push("unsupported claims");
  if (approval !== false || mailingAddressVerified !== false || unsubscribeVerified !== false) problems.push("unverified gate cannot be asserted");
  return { status: "HOLD_UNSENT", problems };
}
