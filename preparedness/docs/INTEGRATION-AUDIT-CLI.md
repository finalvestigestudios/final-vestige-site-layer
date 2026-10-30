# Read-only integration report

The `audit_integration.py` command produces a deterministic JSON inventory of all 35 drafted articles, one local-only planner, their original cluster origins, word counts, safety/editorial states, per-article citations and exact source-reading origins. It distinguishes **machine-checked source URLs** from **human-click-checked** ones, and lists every unresolved cross-cluster URL collision. No network or CMS access is needed; it writes only when explicitly given a local `--output` path.

```bash
python -I preparedness/tools/audit_integration.py --output /tmp/preparedness-integration-report.json
python -I preparedness/tools/audit_integration.py --require-release-ready
```

The second command deliberately returns nonzero while any publication gate is still unmet (or returns 2 when the validator finds errors). This is NOT an automated certification of historical accuracy, medication safety, or regulatory compliance. Even if static checks eventually return clean, release still requires human source/safety review, rendered-browser QD, an exact-head review and separately authorized publishing.

To run the complete test and build pipeline, follow `docs/INTEGRATION-RELEASE-HOLD.md`.
