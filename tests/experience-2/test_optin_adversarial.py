#!/usr/bin/env python3
"""Adversarial Chromium validation for review-only first-viewport opt-in geometry.

Synthetic fixtures intentionally include misleading forms that MUST NOT be
counted as conversion-ready. No network, form entry, submission or PII.
"""
import asyncio
import json
from pathlib import Path
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools' / 'experience-2'))
from verify_optin_viewport_geometry import inspect_optin_viewport

BASE = '''<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;background:#111;color:#eed;font-family:Arial"><main class="wp-block-jetpack-subscriptions" style="padding:20px"><form><label for="signup">Email address</label><input id="signup" type="email" style="display:block;width:240px;height:48px;margin-top:12px;background:#fff;color:#111"></form></main></body></html>'''

def swap(a, b):
    return BASE.replace(a, b)

CASES = [
    ('ancestor_aria_hidden', swap('<main class=', '<main aria-hidden="true" class=')),
    ('ancestor_inert', swap('<main class=', '<main inert class=')),
    ('fieldset_disabled', swap('<form>', '<form><fieldset disabled>').replace('</form>', '</fieldset></form>')),
    ('readonly', swap('id="signup"', 'id="signup" readonly')),
    ('tabindex_minus_one', swap('id="signup"', 'id="signup" tabindex="-1"')),
    ('ancestor_opacity_zero', swap('<main class=', '<main style="opacity:0" class=')),
    ('ancestor_visibility_hidden', swap('<main class=', '<main style="visibility:hidden" class=')),
    ('ancestor_pointer_events_none', swap('<main class=', '<main style="pointer-events:none" class=')),
    ('single_center_uncovered_partial_overlay', swap('</body>', '<div style="position:fixed;top:49px;left:20px;width:107px;height:55px;background:#222;z-index:10"></div></body>')),
    ('full_overlay', swap('</body>', '<div style="position:fixed;inset:0;background:#222;z-index:10"></div></body>')),
    ('ancestor_clips_right_half', swap('style="padding:20px"', 'style="padding:20px;overflow:hidden;width:130px"')),
    ('no_label', swap('<label for="signup">Email address</label>', '')),
    ('aria_hidden_label', swap('<label for="signup">', '<label aria-hidden="true" for="signup">')),
    ('offscreen', swap('<form>', '<div style="height:1400px"></div><form>')),
    ('opacity_zero_field', swap('background:#fff;', 'background:#fff;opacity:0;')),
    ('pointer_events_none_field', swap('background:#fff;', 'background:#fff;pointer-events:none;')),
    ('display_none_field', swap('display:block;width:240px;', 'display:none;width:240px;')),
    ('hidden_nested_iframe', '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><iframe style="display:none" srcdoc="' + BASE.replace('"', '&quot;') + '"></iframe></body></html>'),
]

async def main():
    receipts = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for width in (320, 390, 768, 1440, 1920):
                page = await browser.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
                await page.set_content(BASE)
                result = await inspect_optin_viewport(page)
                assert result['labeled_unobstructed_first_viewport'] == 1, (width, result)
                receipts.append({'scenario':f'healthy_{width}', 'pass':True, 'fields_seen':result['fields_seen']})
                await page.close()
            for name, markup in CASES:
                page = await browser.new_page(viewport={'width':390,'height':900}, reduced_motion='reduce')
                await page.set_content(markup)
                if name == 'hidden_nested_iframe':
                    await page.wait_for_timeout(100)
                result = await inspect_optin_viewport(page)
                assert result['labeled_unobstructed_first_viewport'] == 0, (name, result)
                receipts.append({'scenario':name, 'pass':True, 'fields_seen':result['fields_seen'], 'positive':0,
                                 'embedded_unverified':result['embedded_frame_fields_unverified']})
                await page.close()
            positive_variants = {
                'accessible_aria_label': swap('<label for="signup">Email address</label>', '').replace('id="signup"','id="signup" aria-label="Email address"'),
                'accessible_labelledby': swap('<label for="signup">Email address</label>', '<span id="signup-label">Email address</span>').replace('id="signup"','id="signup" aria-labelledby="signup-label"'),
            }
            for name, markup in positive_variants.items():
                page = await browser.new_page(viewport={'width':390,'height':900}, reduced_motion='reduce')
                await page.set_content(markup)
                result = await inspect_optin_viewport(page)
                assert result['labeled_unobstructed_first_viewport'] == 1,(name,result)
                receipts.append({'scenario':name, 'pass':True, 'fields_seen':result['fields_seen']})
                await page.close()
        finally:
            await browser.close()
    report = {'scope':'OFFLINE_SYNTHETIC_CHROMIUM_ONLY','checks':len(receipts),'passed':sum(int(x['pass']) for x in receipts),
              'hosted_wordpress_verified':False, 'jetpack_confirmation_verified':False, 'no_form_submission':True, 'scenarios':receipts}
    dest=Path(__file__).resolve().parents[2]/'docs'/'experience-2'/'local_adversarial_optin_receipt.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report, indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('checks','passed','hosted_wordpress_verified','no_form_submission')},indent=2))

if __name__ == '__main__':
    asyncio.run(main())
