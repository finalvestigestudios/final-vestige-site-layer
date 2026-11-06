"""Synthetic, self-contained EX2 test fixture: never confuse with WordPress source."""
from pathlib import Path
p=Path(__file__).parent / 'fixture.html'
chapters=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EX2 simulated offline fixture — NOT live WordPress</title><style>body{margin:0;background:#121816;color:#e8d9bf;font:1.125rem/1.6 Georgia,serif}.fv-margin-strip{background:#182321;color:#c1ad83;padding:20px;max-height:42px;overflow:hidden}.fv-hf{max-width:1080px;margin:auto;padding:24px}.fv-hf__opening-actions{display:flex;flex-wrap:wrap;gap:24px;padding:24px 0}.fv-hf__opening-actions a{color:#edca79}section{padding:5rem 0;border-bottom:1px solid #51462c}a:focus-visible{outline:3px solid #edca79;outline-offset:4px}</style><body><div class="fv-margin-strip">'''
html+=''.join(f'<span class="fv-margin-strip__item" data-index="{i}">Archive note {i}</span>' for i in range(72))
html+='</div><main class="fv-hf" data-fv-home-flagship><section><h1 id="fv-hf-title">The evidence is the experience</h1><div class="fv-hf__opening-actions"><a href="#fv-hf-evidence">Enter the evidence room</a><a href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook</a></div></section>'
for i,c in enumerate(chapters[1:], start=2):
    html+=f'<section id="{c}"><h2>Chapter {i}</h2><p>Representative fixture for tool smoke-testing; not FV production source.</p></section>'
html+="""<div><button data-fv-chronicle-view='original' aria-pressed='false'>Original</button><button data-fv-case-button='franklin' aria-pressed='false'>Franklin</button><button data-fv-observer-switch='b' aria-pressed='false'>Frame B</button></div><script>document.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>b.setAttribute('aria-pressed','true')))</script></main></body></html>"""
p.write_text(html, encoding='utf-8')
print('synthetic fixture bytes',p.stat().st_size)
