#!/usr/bin/env python3
"""Fail-closed controls against source-label/URI/description/anchor swaps."""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from r236_patch import RECORDS

def check(html):
 s=BeautifulSoup(html,'html.parser');cards=s.select('li[data-fv-plate-source]')
 assert len(cards)==len(RECORDS)
 for li,(key,name,url,target,limit) in zip(cards,RECORDS):
  assert li.get('data-fv-plate-source')==key
  a,b=li.select('nav.fv-apollo-plate-links a');assert a.get('href')==url
  assert a.get('aria-label')=='Verify at NASA: '+name and a.get('aria-describedby')==limit
  assert b.get('href')==target and b.get('aria-label')=='Find '+name+' in the investigation'
  assert li.select_one('#'+limit) is not None and s.select_one(target) is not None
cases=[
 ('missing named action','aria-label="Verify at NASA: NASA photograph S66-58038"',''),
 ('source URL swap','href="https://www.nasa.gov/image-detail/amf-s67-21294/" rel="noopener noreferrer" aria-describedby="fv-apollo-plate-s67-21294-limit"','href="https://www.nasa.gov/image-detail/amf-s67-15717/" rel="noopener noreferrer" aria-describedby="fv-apollo-plate-s67-21294-limit"'),
 ('misleading record role','aria-label="Verify at NASA: NASA photograph S67-15717"','aria-label="Verify at NASA: Apollo 204 Review Board report"'),
 ('wrong narrative anchor','href="#fv-apollo-photo-1966" aria-label="Find NASA photograph S66-58038','href="#fv-apollo-photo-aftermath" aria-label="Find NASA photograph S66-58038'),
 ('missing evidence limitation','aria-describedby="fv-apollo-plate-s66-58038-limit"',''),
 ('missing source ID','data-fv-plate-source="S67-21294"','data-fv-plate-source="UNKNOWN"')]
if __name__=='__main__':
 html=Path(sys.argv[1]).read_text();check(html)
 for title,old,new in cases:
  assert html.count(old)==1,title
  try:check(html.replace(old,new,1))
  except AssertionError:pass
  else:raise AssertionError('unsafe mutation passed: '+title)
 print('PASS: baseline and 6/6 unsafe mutations rejected')
