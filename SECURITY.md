# Release safety

Production changes must identify an exact pull-request head SHA. QD review, delegated approval, merge, deployment, and live verification are distinct states. A successful merge or deploy is never by itself `IMPLEMENTED + VERIFIED`.

The `production` branch must not be used to bypass separate founder gates for whole-site launch/indexing, spending or billing, account/permission changes, private-user processing, public Scout release, real-money trading, or destructive/high-consequence actions.
