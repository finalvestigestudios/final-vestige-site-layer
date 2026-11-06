"""Construct an OFFLINE WordPress editor-source preview; never calls a WordPress API.

Usage: python stage_patch.py input-editor.txt preview.html
Rejects any unrecognized chronology script rather than silently installing competing controllers.
"""
from pathlib import Path
import sys

START = '        /* Historical context views: these photos are NOT time-stamped fire evidence. */'
END = '      };\n      range.addEventListener(\'input\', update);'
OLD_NOTE = 'Moving the slider changes the archival view for exploration only.'
NEW_NOTE = 'These three archival photographs are independent of the chronology slider; each retains its original NASA source record.'
EXPECTED = (
    'const photos = box.querySelectorAll(\'[data-fvx-chrono-photo]\');',
    'const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);',
    "position.textContent = 'Context photo '")

def patch(source: str, js: str, css: str) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('Source drift: original gallery chronology block not found exactly once')
    start = source.index(START)
    end = source.index(END, start)
    block = source[start:end]
    if not all(term in block for term in EXPECTED):
        raise ValueError('Source drift: original gallery chronology controller changed')
    for term in ('data-fvx-chrono-gallery', 'data-fvx-chrono-photo="0"', 'data-fvx-chrono-photo="1"', 'data-fvx-chrono-photo="2"'):
        if term not in source: raise ValueError('Source drift: missing ' + term)
    if source.count(OLD_NOTE) != 1:
        raise ValueError('Source drift: original gallery explanation changed')
    # Only remove photographic switching. Retain the historical timeline text/status.
    result = (source[:start] + source[end:]).replace(OLD_NOTE, NEW_NOTE)
    return result + '\n<style>\n' + css + '\n</style>\n<script>\n' + js + '\n</script>\n'

if __name__ == '__main__':
    if len(sys.argv) != 3: raise SystemExit('usage: stage_patch.py editor.txt preview.html')
    folder = Path(__file__).resolve().parent
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    output = patch(source, (folder/'gallery-independent.js').read_text(), (folder/'gallery-independent.css').read_text())
    Path(sys.argv[2]).write_text(output, encoding='utf-8')
    print('STAGING ONLY: wrote', sys.argv[2], '(no WordPress network writes)')
