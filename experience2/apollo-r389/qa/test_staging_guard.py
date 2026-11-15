#!/usr/bin/env python3
"""Safety test for staging URL guard; no external connections."""
from staging_smoke import guard
prohibited=[
  ('https://finalvestige.com/apollo-1-evidence-atlas/','finalvestige.com'),
  ('https://www.finalvestige.com/','www.finalvestige.com'),
  ('http://stage.example.test/','stage.example.test'),
  ('https://other.example.test/','stage.example.test'),
  ('https://user:pass@stage.example.test/','stage.example.test'),
  ('https://stage.example.test/#somewhere','stage.example.test'),
]
for url,host in prohibited:
 try: guard(url,host)
 except ValueError: continue
 raise AssertionError('unsafe staging URL accepted: '+url)
assert guard('https://stage.example.test/review/','stage.example.test')=='stage.example.test'
print('staging URL guard: 7/7 PASS (six denied, one allowed); no network requests')
