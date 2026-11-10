import asyncio
import unittest
from playwright.async_api import async_playwright
from form_proof import inspect_browser_dom

STYLE = '<style>input,button {display:inline-block;width:175px;height:40px}</style>'

def wrap(inner):
    return STYLE + '<section class="wp-block-jetpack-subscriptions">' + inner + '</section>'

class OfflineBrowserProof(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        self.page = await self.browser.new_page()
    async def asyncTearDown(self):
        await self.browser.close(); await self.p.stop()
    async def check(self, markup, expected):
        await self.page.set_content(wrap(markup))
        result = await inspect_browser_dom(self.page)
        self.assertEqual(result['visible_form_binding_proven'], expected)
        self.assertFalse(result['submitted'])
        self.assertFalse(result['confirmed_signup'])
        self.assertFalse(result['revenue_verified'])
        return result
    async def test_valid_form(self):
        result=await self.check('<form><label>Email<input type="email"></label><button>Subscribe</button></form>',True)
        self.assertEqual(result['candidates'][0]['usable_submits'],1)
    async def test_unrelated_button_does_not_count(self):
        await self.check('<form><label>Email<input type="email"></label></form><button>Subscribe</button>',False)
    async def test_button_with_no_submit_action_does_not_count(self):
        await self.check('<form><label>Email<input type="email"></label><button type="button">Info</button></form>',False)
    async def test_missing_label_not_ready(self):
        await self.check('<form><input type="email" placeholder="Email"><button>Subscribe</button></form>',False)
    async def test_hidden_honeypot_not_ready(self):
        await self.check('<form><label>Email<input type="email" style="display:none"></label><button>Subscribe</button></form>',False)
    async def test_disabled_button_not_ready(self):
        await self.check('<form><label>Email<input type="email"></label><button disabled>Subscribe</button></form>',False)
    async def test_external_form_action_not_ready(self):
        await self.check('<form action="https://example.com/sub"><label>Email<input type="email"></label><button>Subscribe</button></form>',False)
    async def test_popup_form_recognized(self):
        await self.page.set_content(STYLE+'<div role="dialog"><form><label>Email<input type="email"></label><button>Subscribe</button></form></div>')
        result=await inspect_browser_dom(self.page)
        self.assertTrue(result['visible_form_binding_proven'])
    async def test_nonexistent_form_not_ready(self):
        await self.check('<a href="/focus/">Subscribe</a>',False)

if __name__=='__main__': unittest.main(verbosity=2)
