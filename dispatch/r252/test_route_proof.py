"""Chromium fixture tests only, NOT live finalvestige.com signup tests."""
import unittest
from playwright.async_api import async_playwright
from route_proof import inspect_route

STYLE='<style>input,button{display:inline-block;width:170px;height:42px}form{margin:12px}</style>'
START='<section class="wp-block-jetpack-subscriptions">'
END='</section>'
GOOD='<form action="/wp-json/jetpack/v1/subscribe" method="post"><label>Email<input type="email"></label><button type="submit">Subscribe</button></form>'

class RouteProof(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.driver=await async_playwright().start()
        self.browser=await self.driver.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        self.page=await self.browser.new_page(viewport={'width':900,'height':700})
    async def asyncTearDown(self):
        await self.browser.close();await self.driver.stop()
    async def verify(self,html,expected,dialog=False):
        await self.page.set_content('<base href="https://finalvestige.com/focus/">'+STYLE+(('<div role="dialog">' if dialog else START)+html+('</div>' if dialog else END)))
        r=await inspect_route(self.page)
        self.assertEqual(r['visuallyPlausiblePostForm'],expected,r)
        self.assertFalse(r['confirmedSignup']);self.assertFalse(r['formSubmitted']);self.assertFalse(r['releaseAuthorized'])
        return r
    async def test_normal_post_route(self):await self.verify(GOOD,True)
    async def test_get_route_rejected(self):await self.verify(GOOD.replace('method="post"','method="get"'),False)
    async def test_implicit_get_rejected(self):await self.verify(GOOD.replace(' method="post"',''),False)
    async def test_missing_explicit_action(self):await self.verify(GOOD.replace(' action="/wp-json/jetpack/v1/subscribe"',''),False)
    async def test_cross_origin_action(self):await self.verify(GOOD.replace('/wp-json/jetpack/v1/subscribe','https://example.com/collect'),False)
    async def test_javascript_uri_action(self):await self.verify(GOOD.replace('/wp-json/jetpack/v1/subscribe','javascript:alert(1)'),False)
    async def test_pointer_events_none(self):await self.verify(GOOD.replace('<button type="submit"','<button style="pointer-events:none" type="submit"'),False)
    async def test_unrelated_button(self):await self.verify('<form action="/sub" method="post"><label>Email<input type="email"></label></form><button>Subscribe</button>',False)
    async def test_click_overlaid(self):await self.verify(GOOD+'<div style="position:fixed;inset:0;background:#222;z-index:999"></div>',False)
    async def test_disabled_button(self):await self.verify(GOOD.replace('<button type="submit"','<button disabled type="submit"'),False)
    async def test_hidden_field(self):await self.verify(GOOD.replace('<input type="email"','<input type="email" style="display:none"'),False)
    async def test_missing_label(self):await self.verify(GOOD.replace('<label>Email<input type="email"></label>','<input type="email" placeholder="Email">'),False)
    async def test_readonly_field(self):await self.verify(GOOD.replace('<input type="email"','<input type="email" readonly'),False)
    async def test_unbound_button_form_attr(self):await self.verify(GOOD.replace('<button type="submit"','<button form="other" type="submit"'),False)
    async def test_js_only_classified_unknown(self):
        r=await self.verify('<button type="button">Open subscribe modal</button>',False)
        self.assertTrue(r['unknownJsOnlyForms'])
    async def test_dialog_post(self):await self.verify(GOOD,True,dialog=True)
    async def test_dialog_no_email(self):await self.verify('<button type="button">Close</button>',False,dialog=True)
    async def test_no_inert_signup(self):await self.verify('<div inert>'+GOOD+'</div>',False)

if __name__=='__main__':unittest.main(verbosity=2)
