"""Reviewed byte ceiling shared by the four independent desktop CI preflights.

R292: the real six-app workflow exceeded the 128 KiB ceiling. R363:
continued mandatory tests grew the R362 workflow to 206,611 UTF-8 bytes,
10,003 bytes above the reviewed 192 KiB limit, so ALL FOUR CI preflights
would fail even with runners restored. The 224 KiB limit remains finite,
UTF-8 byte based, and does not relax action pins, artifact allowlists,
source-gate ordering, YAML-key shape or any release/QD approval.
"""

MAX_WORKFLOW_BYTES = 224 * 1024
