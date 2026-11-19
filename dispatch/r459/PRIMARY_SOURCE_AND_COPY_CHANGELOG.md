# R459 — NASA primary-record adjudication and editorial conversion review

## Actual conflict avoided
Original PR [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) Issue 04 uses **“Fourteen seconds. A much longer explanation.”** This is a plausible *approximate* interval between first fire indication and the pressure-vessel rupture, **not** a proven time from ignition to death, or the precise full fire duration. The official [preliminary NASA account of February 3, 1967](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/seamans.html) warned station timestamps might differ by one to two seconds. The new alternative removes false precision from the email SUBJECT while preserving the meaningful physics in the body.

## Primary evidence / what it supports / what it does not

| Source | Supported finding | Overreach to reject |
|---|---|---|
| [Apollo 204 Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html) | Electrical arc judged *most probable* ignition initiator. No single source conclusively identified; 100% O2 at 16.7 psia; hazards from combustibles and pressure-hatch design | “Investigators proved which exact wire started it” |
| [Review Board emergency reconstruction](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) | First fire voice at ~23:31:04.7 GMT; loss of voice/data at ~23:31:22.4 GMT; observed attempts consistent with hatch handling | “A precisely timed eighteen-second entire fire” |
| [NASA preliminary Seamans statement, February 3, 1967](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/seamans.html) | Roughly fourteen seconds first indication to rupture; explicitly preliminary and possible 1–2 s station-sync mismatch | “Fourteen exact seconds from first spark to final outcome” |
| [NASA Safety and Mission Assurance](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) | Board could not identify a specific source; three-part hatch took ~90 seconds in ideal circumstances and was blocked by cabin pressure | “The hatch alone caused the accident” |

## Editorial decisions
- **Original unchanged:** source Issue04 SHA `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`; PR #175 exact HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`.
- **New optional subject:** “The spark NASA could not prove”; **preheader:** “Apollo 1's official findings tell a bigger story than a single suspected wire.” It is accurate because the specific ignition source remains inconclusive; this does NOT say there was no evidence of arcing.
- **One principal CTA:** original first-party investigation [The Hatch Opened Inward](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/), confirmed as **published** via authenticated WordPress post ID 434, modified 2026-11-15; web reader encountered an access error for the permalink, so external HTTP delivery still needs an independently successful network/browser check before approval.
- **No commercial CTA**. The original 4 editorial / 2 reserved commercial campaign is not revised; no recommendation of audio or medical benefits is embedded here.
- **Email treatment:** HTML/plaintext are offline review renderings, not native Jetpack; hidden preheader cannot prove WordPress preheader control; both display unsent/legal holds. Source references live as ordinary readable text links, secondary to one main CTA.
- **Claim ethics:** do not use the three deceased crew as emotional sales leverage, do not introduce gore or conjecture, do not treat NASA report as a warrant for product efficacy.

## Legal source
Commercial-primary-purpose review, sender identification, valid publisher postal address and functional unsubscribe are checked against [FTC CAN-SPAM business guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). For safety all six Dispatch editions remain blocked on the same renderer/address/opt-out witness, regardless of their editorial labels.

## Needed independent proofs
External navigation of the first-party Apollo article, exact WordPress post-to-email subject and body mapping in a non-sending native preview, FV-owned postal address in actual rendered email, working opt-out, explicit founder approval.
