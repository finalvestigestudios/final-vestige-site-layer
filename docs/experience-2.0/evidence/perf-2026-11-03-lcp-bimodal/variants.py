# One-change-at-a-time transforms of the SAVED live HTML (local copy only; nothing here touches production).
# Loaded by harness.py --variant-file; _rep is injected by the harness.
import re

HERO_OPEN = '<div class="fv-hf fv-hf--wp alignfull" data-fv-home-flagship>'


def _flagship_style_span(h):
    """(start, end) of the flagship's inline <style> (the 57 KB one that begins with :where(.fv-hf))."""
    k = h.index(":where(.fv-hf){--hf-bg")
    s = h.rindex("<style", 0, k)
    e = h.index("</style>", k) + len("</style>")
    return s, e


def hoist_css(h):
    """Move the flagship <style> element in front of the flagship markup (same bytes, same block, order only)."""
    s, e = _flagship_style_span(h)
    css = h[s:e]
    h2 = h[:s] + h[e:]
    i = h2.index(HERO_OPEN)
    return h2[:i] + css + "\n" + h2[i:]


def no_inter_preload(h):
    """Diagnostic only (founder rejected a plugin for this): drop the Inter preload link."""
    return re.sub(r'<link rel="preload" href="[^"]*InterVariable\.woff2"[^>]*>', "", h, count=1)


def scripts_deferred_flagship(h):
    """Diagnostic: flagship inline scripts are not render-blocking; included to show they are not the cause (no-op check)."""
    return h


VARIANTS = {"hoist_css": hoist_css, "no_inter_preload": no_inter_preload}


def strip_css_first(h):
    """Causal probe for the 'fast mode' (NOT a proposal; the strip belongs to the header, which is not ours):
    move the margin-strip <style> in front of the strip markup so the strip can never paint unstyled."""
    k = h.index(".fv-margin-strip{background:#0f100f")
    s = h.rindex("<style", 0, k)
    e = h.index("</style>", k) + len("</style>")
    css = h[s:e]
    h2 = h[:s] + h[e:]
    i = h2.index('<div class="fv-margin-strip')
    j = h2.rindex("<", 0, i) if False else i
    return h2[:j] + css + "\n" + h2[j:]


def strip_css_removed(h):
    """Measurement probe: strip CSS removed, to read the unstyled strip window's box (area) in an unthrottled load."""
    k = h.index(".fv-margin-strip{background:#0f100f")
    s = h.rindex("<style", 0, k)
    e = h.index("</style>", k) + len("</style>")
    return h[:s] + h[e:]


VARIANTS["strip_css_first"] = strip_css_first
VARIANTS["strip_css_removed"] = strip_css_removed
