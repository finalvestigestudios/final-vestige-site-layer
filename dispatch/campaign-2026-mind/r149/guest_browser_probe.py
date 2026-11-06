"""Non-submitting signed-out Jetpack first-click probe (DRAFT / READ-ONLY).

Use: python -I guest_browser_probe.py --mode fixture --out ./proof
     python -I guest_browser_probe.py --mode live --out ./proof
Requires python-playwright and Chromium installed. Never types, clicks submit,
accepts consent, creates subscribers, records emails, or calls the WP API.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

VIEWPORTS = ((320, 740), (390, 844), (768, 900), (1440, 900))
TARGETS = (
    ("dispatch", "https://finalvestige.com/dispatch/"),
    ("focus", "https://finalvestige.com/focus/"),
)

# Deliberately omit form values, email addresses, cookies, local storage,
# external hosts, user-identifiable URL query strings, and request bodies.
JS_AUDIT = """() => {
  const visible = n => !!(n && n.getClientRects().length &&
    getComputedStyle(n).visibility !== 'hidden' &&
    getComputedStyle(n).display !== 'none');
  const containers = [...document.querySelectorAll('.wp-block-jetpack-subscriptions')];
  const forms = [...document.querySelectorAll('form')];
  const formEvidence = forms.map(f => {
    const emails = [...f.querySelectorAll('input[type=email]')];
    const submitters = [...f.querySelectorAll('button[type=submit],input[type=submit],button:not([type])')];
    const e = emails.find(visible);
    const button = submitters.find(visible);
    return { visible: visible(f), email_visible: !!e,
      email_enabled: !!(e && !e.disabled && !e.readOnly),
      email_labelled: !!(e && (e.labels?.length || e.getAttribute('aria-label') || e.getAttribute('aria-labelledby'))),
      submit_visible: !!button, submit_enabled: !!(button && !button.disabled),
      within_jetpack: !!f.closest('.wp-block-jetpack-subscriptions') };
  });
  const emailInputs = [...document.querySelectorAll('input[type=email]')].map(e => ({
    visible: visible(e), enabled: !e.disabled && !e.readOnly,
    labelled: !!(e.labels?.length || e.getAttribute('aria-label') || e.getAttribute('aria-labelledby')),
    within_jetpack: !!e.closest('.wp-block-jetpack-subscriptions')
  }));
  const buttons = [...document.querySelectorAll('button,input[type=submit]')].map(b => ({
    visible: visible(b), enabled: !b.disabled,
    within_jetpack: !!b.closest('.wp-block-jetpack-subscriptions')
  }));
  const subscribeLinks = [...document.querySelectorAll('a')].filter(a =>
    /subscribe/i.test((a.textContent||'').trim()) && visible(a));
  const samePageSubscribeLinks = subscribeLinks.filter(a => {
    try { if ((a.getAttribute('href')||'').includes('p=523')) return true; const u = new URL(a.href, location.href);
      return u.hostname === location.hostname &&
        ((u.pathname.replace(/\\/$/,'') === location.pathname.replace(/\\/$/,'')) ||
        (u.searchParams.get('p') === '523'));
    } catch { return false; }
  }).length;
  const focusGift = document.querySelector('.fvf-gift');
  const status = {jetpack_blocks: containers.length, forms:formEvidence,
    emails:emailInputs,buttons,visible_subscribe_links:subscribeLinks.length,
    same_page_subscribe_links:samePageSubscribeLinks,
    focus_success_panel_visible:!!(focusGift && visible(focusGift)),
    title_length:document.title.length};
  return status;
}"""


def classify(evidence: dict) -> str:
    """Only classify visible UI, NEVER subscriber confirmation or deliverability."""
    forms = evidence.get("forms", [])
    if any(f.get("visible") and f.get("email_visible") and
           f.get("email_enabled") and f.get("submit_visible") and
           f.get("submit_enabled") for f in forms):
        return "VISIBLE_SUBSCRIPTION_FORM_NOT_SUBMITTED"
    # Some Jetpack forms may render div-based controls. Do not call those broken.
    if evidence.get("same_page_subscribe_links", 0) > 0 and not any(
            e.get("visible") and e.get("enabled") for e in evidence.get("emails", [])):
        return "SELF_LINK_WITHOUT_VISIBLE_EMAIL_INPUT"
    return "INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW"


def inspect_page(browser, label: str, target: str, width: int, height: int, out: Path) -> dict:
    ctx = browser.new_context(viewport={"width":width,"height":height},
                              service_workers="block", accept_downloads=False)
    page = ctx.new_page()
    page.on("dialog", lambda dialog: dialog.dismiss())
    result = {"page":label, "viewport":f"{width}x{height}",
              "mode":"read_only_get_navigation", "submitted":False,
              "confirmed_signup":"UNVERIFIED", "welcome_received":"UNVERIFIED",
              "paid_order":"UNVERIFIED"}
    try:
        if target.startswith('file:'):
            # The container's Chromium security policy blocks file: navigation.
            # set_content executes the same DOM audit without any network request.
            from urllib.request import url2pathname
            html = Path(url2pathname(urlsplit(target).path)).read_text(encoding='utf-8')
            page.set_content(html, wait_until="domcontentloaded")
        else:
            page.goto(target, wait_until="domcontentloaded", timeout=18000)
            page.wait_for_timeout(1600)  # allow Jetpack runtime to mount
        evidence = page.evaluate(JS_AUDIT)
        result.update({"navigation":"OK", "host":urlsplit(page.url).hostname,
                       "path":urlsplit(page.url).path, "evidence":evidence,
                       "classification":classify(evidence)})
        screenshot_name = f"{label}-{width}.png"
        page.screenshot(path=str(out / screenshot_name), full_page=True,
                        animations="disabled", timeout=12000)
        result["screenshot"] = screenshot_name
    except Exception as e:
        # Sanitized error string only: do not record arbitrary URLs/PII.
        result.update({"navigation":"INDETERMINATE", "error_type":type(e).__name__,
                       "classification":"INDETERMINATE_NOT_VERIFIED"})
    finally:
        ctx.close()
    return result


def fixtures(out: Path) -> list[tuple[str,str]]:
    d = out / "fixtures"; d.mkdir(exist_ok=True)
    templates = {
      "self_link": '<html lang="en"><body><main><h1>The Dispatch</h1><div class="wp-block-jetpack-subscriptions"><a href="/?post_type=page&p=523">Subscribe</a></div></main></body></html>',
      "valid_form": '<html lang="en"><body><main><h1>The Dispatch</h1><div class="wp-block-jetpack-subscriptions"><form><label for="email">Email</label><input id="email" type="email"><button type="submit">Subscribe</button></form></div></main></body></html>',
      "hidden_form": '<html lang="en"><body><main><h1>The Dispatch</h1><div class="wp-block-jetpack-subscriptions"><form style="display:none"><label for="email">Email</label><input id="email" type="email"><button>Subscribe</button></form></div><a href="/?post_type=page&p=523">Subscribe</a></main></body></html>',
      "disabled_form": '<html lang="en"><body><main><div class="wp-block-jetpack-subscriptions"><form><label>Email<input type="email" disabled></label><button type="submit">Subscribe</button></form></div></main></body></html>',
    }
    targets=[]
    for name, html in templates.items():
        path=d/f"{name}.html";path.write_text(html,encoding="utf-8")
        targets.append((name,path.resolve().as_uri()))
    return targets


def execute(mode: str, out: Path, chromium_executable: str | None=None) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    targets = TARGETS if mode == "live" else fixtures(out)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path=chromium_executable,
                              args=["--no-sandbox"] if chromium_executable else [])
        try:
            results=[inspect_page(b,name,url,w,h,out) for name,url in targets for w,h in VIEWPORTS]
        finally:
            b.close()
    report={"mode":mode,"browser":"Chromium", "did_submit":False,
            "actual_subscriber_confirmation":"UNVERIFIED",
            "actual_jetpack_received_email":"UNVERIFIED",
            "results":results}
    (out/"results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report


if __name__ == "__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["fixture","live"],default="fixture")
    ap.add_argument("--out",type=Path,default=Path("./guest-probe-proof"))
    ap.add_argument("--chromium",default=None)
    a=ap.parse_args()
    report=execute(a.mode,a.out,a.chromium)
    print(json.dumps({"mode":a.mode,"classifications":{x["page"]+"/"+x["viewport"]:x["classification"] for x in report["results"]},"non_submitting":True},indent=2))
