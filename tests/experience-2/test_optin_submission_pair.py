#!/usr/bin/env python3
"""Real offline Chromium checks; no real Jetpack signups and no network."""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools' / 'experience-2'))
from verify_optin_submission_pair import inspect_signup_pair

HEAD = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0;background:#121212;color:#fff;font-family:Arial">'
TAIL = '</body></html>'
FORM = '''<main class="wp-block-jetpack-subscriptions" style="padding:20px"><form id="f">
<label for="e">Email address</label><input id="e" type="email" style="display:block;width:240px;height:48px;background:white;color:black;margin-top:12px">
<button type="submit" style="display:block;width:240px;height:54px;background:#cba877;color:black;margin-top:10px">Subscribe</button></form></main>'''

def page(body):return HEAD+body+TAIL

def replace(a,b):return page(FORM.replace(a,b))

NEG = {
    'missing_button':replace('<button type="submit"', '<div type="submit"').replace('</button>', '</div>'),
    'wrong_button_type':replace('type="submit"', 'type="button"'),
    'disabled_button':replace('type="submit"', 'type="submit" disabled'),
    'button_disabled_fieldset':replace('<button type="submit"','<fieldset disabled><button type="submit"').replace('</button>', '</button></fieldset>'),
    'button_aria_hidden':replace('<button type="submit"','<button aria-hidden="true" type="submit"'),
    'button_inert':replace('<button type="submit"','<button inert type="submit"'),
    'button_readonly_input': replace('<button type="submit" style=','<input type="submit" readonly value="Subscribe" style=').replace('>Subscribe</button>', '/>'),
    'button_tabindex_minus_one':replace('<button type="submit"','<button tabindex="-1" type="submit"'),
    'button_covered':replace('</main>','</main><div style="position:fixed;top:145px;left:20px;width:240px;height:54px;z-index:9;background:#c33"></div>'),
    'button_half_covered':replace('</main>','</main><div style="position:fixed;top:145px;left:20px;width:90px;height:54px;z-index:9;background:#c33"></div>'),
    'button_offscreen':replace('<button type="submit"','<div style="height:1200px"></div><button type="submit"'),
    'button_opacity_zero':replace('background:#cba877;','background:#cba877;opacity:0;'),
    'button_pointer_events_none':replace('background:#cba877;','background:#cba877;pointer-events:none;'),
    'button_display_none':replace('display:block;width:240px;height:54px;','display:none;width:240px;height:54px;'),
    'button_no_name':replace('>Subscribe</button>','></button>'),
    'button_elsewhere':replace('<button type="submit"','</form></main><form><button type="submit"').replace('</button></form></main>','</button></form>'),
    'field_no_form':replace('<form id="f">','<div id="f">').replace('</form>','</div>'),
    'button_in_second_form':replace('<button type="submit"','</form><form><button type="submit"').replace('</button></form>','</button></form>'),
    'button_ancestor_clipped': replace('<button type="submit"','<div style="height:23px;overflow:hidden"><button type="submit"').replace('</button>', '</button></div>'),
    'email_no_name':replace('<label for="e">Email address</label>',''),
    'email_disabled': replace('id="e" type="email"','id="e" type="email" disabled'),
}
POS = {
    'ordinary_form': page(FORM),
    'submit_input_with_label': replace('<button type="submit" style=','<input type="submit" value="Subscribe" style=').replace('>Subscribe</button>','/>'),
    'button_aria_label': replace('>Subscribe</button>', ' aria-label="Send me the fieldbook"></button>'),
}

async def main():
    observed = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for width in (320, 360, 390, 768, 1440, 1920):
                for name, html in POS.items():
                    page_obj=await b.new_page(viewport={'width':width,'height':900}, reduced_motion='reduce')
                    await page_obj.set_content(html)
                    r=await inspect_signup_pair(page_obj)
                    observed.append({'scenario':name,'width':width,'expect':1,'got':r['main_document_pairs_ready']})
                    await page_obj.close()
            for name,html in NEG.items():
                page_obj=await b.new_page(viewport={'width':390,'height':900})
                await page_obj.set_content(html)
                r=await inspect_signup_pair(page_obj)
                observed.append({'scenario':name,'width':390,'expect':0,'got':r['main_document_pairs_ready']})
                await page_obj.close()
        finally: await b.close()
    result={'environment':'SYNTHETIC_OFFLINE_CHROMIUM_NOT_HOSTED_QA', 'checks':len(observed),
            'passed':sum(x['expect']==x['got'] for x in observed), 'failed':[x for x in observed if x['expect']!=x['got']],
            'no_forms_filled_or_submitted':True,'no_subscriptions_verified':True, 'checks_detail':observed}
    Path(__file__).resolve().parents[2].joinpath('docs/experience-2').mkdir(parents=True, exist_ok=True)
    Path(__file__).resolve().parents[2].joinpath('docs/experience-2/local_signup_pair_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('checks','passed','failed')}))
    if result['failed']: raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
