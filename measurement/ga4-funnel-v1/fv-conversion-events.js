/* Final Vestige — GA4 conversion signals v1 (STAGING ONLY).
 * Requires pre-existing, consent-governed gtag (Site Kit).
 * No new tag, cookies, changed links or personally identifying data.
 */
(function (root, doc) {
  "use strict";

  function pageGroup(pathname) {
    var path = String(pathname || "/").toLowerCase();
    if (path === "/focus/" || path === "/focus") return "focus";
    if (path.indexOf("/mini-museum-history-collectibles/") === 0) return "mini_museum";
    if (path.indexOf("/collection/") === 0) return "collection";
    if (path.indexOf("/free-resources/") === 0) return "library";
    if (/^\/[0-9]{4}\/[0-9]{2}\//.test(path)) return "article";
    if (path === "/") return "home";
    return "other";
  }

  function parseSafeUrl(href) {
    try {
      var url = new URL(String(href || ""), "https://finalvestige.com/");
      return (url.protocol === "https:" || url.protocol === "http:") ? url : null;
    } catch (error) {
      return null;
    }
  }

  function classifyHref(href, pathname) {
    var url = parseSafeUrl(href);
    if (!url) return null;
    var host = url.hostname.toLowerCase();
    var group = pageGroup(pathname);
    var params = { fv_page_group: group };

    if (host === "awin1.com" || host === "www.awin1.com") {
      var offer = "other_awin";
      if (url.searchParams.get("s") === "4236132" || group === "mini_museum") {
        offer = "mini_museum";
      } else if (url.searchParams.get("awinmid") === "125352") {
        offer = "suunto";
      }
      params.fv_offer = offer;
      return { event: "fv_affiliate_outbound", params: params };
    }
    if (host === "payhip.com" || host === "payhip.io" ||
        host.endsWith(".payhip.com") || host.endsWith(".payhip.io")) {
      return { event: "fv_checkout_handoff", params: params };
    }

    if (host !== "finalvestige.com" && host !== "www.finalvestige.com") return null;
    var path = url.pathname.replace(/\/+/g, "/");
    if (path === "/focus/" && group !== "focus") {
      return {
        event: group === "article" ? "fv_article_to_resource" : "fv_focus_entry",
        params: params
      };
    }
    if (path.indexOf("/wp-content/uploads/") === 0 &&
        /\/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition\.pdf$/i.test(path)) {
      return { event: "fv_fieldbook_pdf_click", params: params };
    }
    return null;
  }

  if (typeof module === "object" && module.exports) {
    module.exports = { pageGroup: pageGroup, classifyHref: classifyHref };
  }
  if (!root || !doc || typeof doc.addEventListener !== "function") return;
  if (root.__fvConversionTrackingV1Installed) return;
  root.__fvConversionTrackingV1Installed = true;

  function send(eventName, params) {
    // Existing Google tag is solely responsible for consent; never bypass it.
    if (typeof root.gtag !== "function") return;
    root.gtag("event", eventName, params);
  }

  doc.addEventListener("click", function (event) {
    if (!event || !event.target || typeof event.target.closest !== "function") return;
    var link = event.target.closest("a[href]");
    if (!link) return;
    var action = classifyHref(link.href, root.location && root.location.pathname);
    if (action) send(action.event, action.params);
    // Never delay or prevent merchant navigation.
  }, true);

  doc.addEventListener("submit", function (event) {
    var form = event && event.target;
    if (pageGroup(root.location && root.location.pathname) !== "focus" ||
        !form || typeof form.closest !== "function" ||
        !form.closest(".wp-block-jetpack-subscriptions")) return;
    // Attempt only: subscription confirmation or purchase is never inferred.
    send("fv_subscribe_submit_attempt", { fv_page_group: "focus" });
  }, true);
})(typeof window === "object" ? window : null,
   typeof document === "object" ? document : null);
