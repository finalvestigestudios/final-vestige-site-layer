"""Reviewed byte ceiling shared by the four independent desktop CI preflights.

R292: the real six-app workflow exceeded the earlier 128 KiB ceiling before
runner execution. The reviewed ceiling is deliberately finite (192 KiB),
UTF-8 byte based, and does not relax action pins, artifact allowlists,
source-gate ordering, YAML-key shape or any release/QD approval.
"""

MAX_WORKFLOW_BYTES = 192 * 1024
