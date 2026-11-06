"""Native Chromium before/after behavioral witness of WP Page 1579's real script.

Neither 'subscribe=success' nor `is-subscriber` proves an email-confirmed lead.
Runs offline in a local browser fixture; does NOT test Jetpack or actual WordPress.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
LIVE_SCRIPT = HERE / "focus_gift_live_20261106.js"
NEW_SCRIPT = HERE / "focus_gift_review_candidate.js"
REPORT = HERE / "focus_gift_state_browser_results.json"
EXPECTED_LIVE_SHA256 = "f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7"
CASE_VALUES = [
    ("no_query", "", False, False),
    ("valid_submission", "?subscribe=success", True, True),
    ("arbitrary_positive", "?subscribe=banana", True, False),
    ("undocumented_true", "?subscribe=true", True, False),
    ("known_invalid_email", "?subscribe=invalid_email", False, False),
    ("known_error", "?subscribe=error", False, False),
    ("spelling_case", "?subscribe=Success", True, False),
    ("empty_query", "?subscribe=", False, False),
    ("failure_typo", "?subscribe=blocked_mail", True, False),
]


def fixture(script):
    nojs = (HERE / "focus_nojs_fallback_block.html").read_text()
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Offline WordPress Focus behavior witness</title></head><body>'
            '<main class="fv-focus"><div class="wp-block-jetpack-subscriptions__container"></div>'
            '<section id="fvf-gift" hidden role="status">'
            '<p>Your fieldbook is ready to download.</p>'
            '<a href="#file">Download the Seven Day Focus Fieldbook</a></section>'
            '<script>' + script.replace('</script>', '<\\/script>') + '</script>'
            + nojs + '</main></body></html>')


def main():
    actual = LIVE_SCRIPT.read_text().strip()
    new = NEW_SCRIPT.read_text().strip()
    if hashlib.sha256(actual.encode()).hexdigest() != EXPECTED_LIVE_SHA256:
        raise SystemExit("FAIL CLOSED: source witness changed; re-read Page 1579 before requalification")
    fallback = (HERE / "focus_nojs_fallback_block.html").read_text()
    if "<noscript>" not in fallback or "Downloading here does not subscribe" not in fallback:
        raise SystemExit("FAIL CLOSED: PR #1270 accessible fallback missing or altered")
    report = {
        'scope': 'offline real Chromium fixture using exact verbatim live Page 1579 gift JS; not full WP or Jetpack',
        'wp_page_id': 1579,
        'wp_modified': '2026-11-05T17:44:02',
        'live_script_sha256': hashlib.sha256(actual.encode()).hexdigest(),
        'candidate_sha256': hashlib.sha256(new.encode()).hexdigest(),
        'cases': [], 'status': 'NOT_RUN', 'release_qualified': False
    }
    with sync_playwright() as pw:
        chromium = os.getenv('FV_CHROMIUM_BINARY') or shutil.which('chromium')
        browser = pw.chromium.launch(headless=True, executable_path=chromium, args=['--no-sandbox'])
        for label, script in [('published', actual), ('review_candidate', new)]:
            path = HERE / ('fixture_' + label + '.html')
            path.write_text(fixture(script))
            for n, query, before_should_show, after_should_show in CASE_VALUES:
                expected = before_should_show if label == 'published' else after_should_show
                for width in (320, 390, 1440):
                    page = browser.new_page(viewport={'width': width, 'height': 750})
                    page.goto("about:blank" + query)
                    page.set_content(fixture(script), wait_until="load")
                    actual_visible = page.locator('#fvf-gift').is_visible()
                    ok = actual_visible == expected
                    report['cases'].append({'script': label, 'case': n, 'width': width,
                                            'expected_panel_visible': expected, 'actual_panel_visible': actual_visible,
                                            'pass': ok})
                    page.close()
            # Assert real MutationObserver class-change behavior, queryless.
            page = browser.new_page(viewport={'width': 390, 'height': 750})
            page.goto("about:blank")
            page.set_content(fixture(script), wait_until="load")
            start = page.locator('#fvf-gift').is_visible()
            page.evaluate("document.querySelector('.wp-block-jetpack-subscriptions__container').classList.add('is-subscriber')")
            page.wait_for_timeout(50)
            end = page.locator('#fvf-gift').is_visible()
            report['cases'].append({'script': label, 'case': 'widget_observer', 'width': 390,
                                    'expected_panel_visible': True, 'actual_panel_visible': end,
                                    'pass': not start and end})
            page.close()
        # No-JS: panel stays hidden; earlier review PR #1270 proposes a separate no-JS download.
        page = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 750})
        page.goto("about:blank?subscribe=success")
        page.set_content(fixture(new), wait_until="load")
        nojs = page.locator('.fvf-nojs-fallback a')
        report['cases'].append({'script': 'review_candidate', 'case': 'javascript_disabled', 'width': 390,
                                'expected_panel_visible': False, 'actual_panel_visible': page.locator('#fvf-gift').is_visible(),
                                'fallback_visible': nojs.is_visible(),
                                'fallback_href': nojs.get_attribute('href'),
                                'pass': not page.locator('#fvf-gift').is_visible() and nojs.is_visible(),
                                'note': 'PR #1270 review-only fallback composited with new script in offline fixture'})
        page.close()
        for label, script in [('published',actual),('review_candidate',new)]:
            page=browser.new_page(viewport={'width':390,'height':750})
            page.goto('about:blank?subscribe=banana')
            page.set_content(fixture(script))
            page.screenshot(path=str(HERE / (label + '_arbitrary_query_390.png')), full_page=True)
            report['cases'].append({'script':label,'case':'nojs_fallback_hidden_with_js','width':390,
                                    'expected_panel_visible':False,
                                    'actual_panel_visible':page.locator('.fvf-nojs-fallback').is_visible(),
                                    'pass':not page.locator('.fvf-nojs-fallback').is_visible()})
            page.close()
        browser.close()
    report['pass_count'] = sum(i['pass'] for i in report['cases'])
    report['total'] = len(report['cases'])
    report['status'] = 'PASS' if report['pass_count'] == report['total'] else 'FAIL'
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['status']} {report['pass_count']}/{report['total']} native Chromium cases")
    print('Published live JS SHA256:', report['live_script_sha256'])
    print('Candidate JS SHA256:', report['candidate_sha256'])
    print('Published arbitrary query panel visible:', next(x for x in report['cases'] if x['script']=='published' and x['case']=='arbitrary_positive')['actual_panel_visible'])
    print('Candidate arbitrary query panel visible:', next(x for x in report['cases'] if x['script']=='review_candidate' and x['case']=='arbitrary_positive')['actual_panel_visible'])
    return report['status'] == 'PASS'

if __name__ == '__main__':
    raise SystemExit(0 if main() else 2)
