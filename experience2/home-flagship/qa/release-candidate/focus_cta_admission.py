"""Fail-closed, real-browser admission for the evidence-first homepage Focus entry.

Read-only: never clicks off-site, submits email, changes CMS, or records visitors.
The staging verifier owns exact Git SHA, private WordPress admission, axe and CWV.
"""

REQUIRED = (
    'two_noncompeting_hero_actions',
    'evidence_remains_primary',
    'contextual_free_fieldbook_offer',
    'focus_destination_exact',
    'focus_44px_touch_height',
    'focus_in_horizontal_viewport',
    'focus_early_in_reading_flow',
    'focus_unobstructed_at_center',
    'focus_keyboard_reachable',
    'focus_is_next_tab_after_evidence',
    'focus_visible_keyboard_indicator',
)


def inspect_focus_entry(frame, width):
    """Return Boolean checks for actual rendered iframe or top-level browser frame.

    This function is invoked *after* the first-screen capture because it may
    scroll the CTA into view to test hit-testing. A thrown browser exception
    fails all checks closed. It does not claim a conversion or a WCAG pass.
    """
    checks = {name: False for name in REQUIRED}
    try:
        actions = frame.locator('.fv-hf__opening-actions > a')
        if actions.count() != 2:
            return checks
        primary, secondary = actions.nth(0), actions.nth(1)
        checks['two_noncompeting_hero_actions'] = True
        checks['evidence_remains_primary'] = (primary.get_attribute('href') == '#fv-hf-evidence'
                and 'enter the evidence room' in primary.inner_text().lower())
        label = secondary.inner_text().strip().lower()
        checks['contextual_free_fieldbook_offer'] = (
            'free' in label and '52-page' in label and 'focus fieldbook' in label)
        checks['focus_destination_exact'] = (
            secondary.get_attribute('href') == 'https://finalvestige.com/focus/')
        loc = secondary.element_handle()
        if loc is None:
            return checks
        before = loc.evaluate('''el => {
          const r=el.getBoundingClientRect();
          return {top:r.top, viewportHeight:innerHeight};
        }''')
        checks['focus_early_in_reading_flow'] = (
            before['top'] >= 0 and before['top'] <= 1.5 * before['viewportHeight'])
        secondary.scroll_into_view_if_needed(timeout=4500)
        metrics = loc.evaluate('''el => {
          const r=el.getBoundingClientRect(), cs=getComputedStyle(el);
          const x=r.left+r.width/2, y=r.top+r.height/2;
          const hit=document.elementFromPoint(x,y);
          return {height:r.height,width:r.width,left:r.left,right:r.right,
             visible:cs.display!=='none' && cs.visibility!=='hidden' &&
                Number(cs.opacity)>0 && !el.closest('[hidden], [inert]'),
             overlap:!!hit && (hit===el || el.contains(hit)),
             viewportWidth:document.documentElement.clientWidth,
             tabbable:el.tabIndex>=0 && el.getAttribute('aria-disabled')!=='true'};
        }''')
        checks['focus_44px_touch_height'] = (metrics['visible'] and metrics['height'] >= 44
            and metrics['width'] >= 44)
        checks['focus_in_horizontal_viewport'] = (metrics['visible'] and metrics['left'] >= -1
            and metrics['right'] <= metrics['viewportWidth'] + 1)
        checks['focus_unobstructed_at_center'] = (metrics['visible'] and metrics['overlap'])
        # A scripted .focus() alone is not keyboard evidence: it can focus
        # controls in an unexpected order, with no visible keyboard indicator.
        # Use the browser's native Tab movement from the evidence-first action.
        if metrics['tabbable'] and metrics['visible'] and primary.is_visible():
            primary.focus(timeout=4500)
            frame.page.keyboard.press('Tab')
            keyboard = loc.evaluate('''el => {
              const cs=getComputedStyle(el);
              return {
                active:document.activeElement===el,
                visibleFocus:el.matches(':focus-visible'),
                outlineStyle:cs.outlineStyle,
                outlineWidth:parseFloat(cs.outlineWidth)||0
              };
            }''')
            checks['focus_keyboard_reachable'] = keyboard['active']
            checks['focus_is_next_tab_after_evidence'] = keyboard['active']
            checks['focus_visible_keyboard_indicator'] = (
                keyboard['active'] and keyboard['visibleFocus'] and
                keyboard['outlineStyle'] not in ('none','hidden') and
                keyboard['outlineWidth'] >= 2)
    except Exception:
        return checks
    return {key: bool(value) for key, value in checks.items()}
