#!/bin/bash
cd "$(dirname "$0")"; export PYTHONUTF8=1; H=saved_live_home_2026-11-02T22-46.html
while [ ! -f runs/queue2.done ]; do sleep 10; done
python harness.py --html $H --variants base,hoist_css --variant-file variants.py --runs 10 --mode rich --wait 1500 --enc gzip --out runs/e11_gzip_rich.jsonl > runs/e11.log 2>&1
python harness.py --html $H --variants live --live https://finalvestige.com/ --runs 10 --mode rich --wait 1500 --out runs/e12_live_rich.jsonl > runs/e12.log 2>&1
echo done > runs/queue3.done
