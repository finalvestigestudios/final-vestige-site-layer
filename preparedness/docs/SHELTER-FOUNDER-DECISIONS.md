# Shelter, Power and Family Communication: founder decision sheet (fastest route to live)

Prepared 2026-11-01. **Nothing here is approved.** Only the founder can approve safety-gated pages, and only a human reviewer can set `safety_review.state` to `approved`. The validator refuses to publish any page while review is pending. This sheet turns the review package (`SHELTER-QD-PACKET.md`) into the shortest list of decisions that unlock the seven pages: four articles and three tools.

## The nine decisions that block publication

Each has a recommended default, which keeps the page conservative, and what the alternative would change. Answer "accept" or "change to: ...".

| # | Decision | Recommended default | If you choose otherwise |
|---|---|---|---|
| 1 | **Indoor fuel-burning heaters (R-12-4).** The CDC lists kerosene heaters as backup heat; no source gives a ventilation figure. | Accept: the guide gives no indoor fuel-heater procedure and says to leave if too cold. | Adding any procedure needs an official source we have not found. |
| 2 | **Generator distance (R-12-1).** 20 feet from windows, doors and vents is stated as a minimum, not a guarantee, with an "Uncertain" note that no source covers neighbors' openings, porches or wind. | Accept. | Remove the editor's caution; not recommended. |
| 3 | **Stranded-vehicle engine figure (R-12-6).** About 10 minutes per hour, window slightly open, exhaust clear (CDC and NWS agree). | Accept with attribution, or replace with "follow current NWS and CDC guidance" if you prefer no number. | Either is safe to publish; the second removes the number. |
| 4 | **Medication wording (R-12-7).** FEMA's Dec 2023 wording (replace; call your doctor or pharmacist; use only until new supply) plus "do not stop, skip or throw out a medicine you depend on without asking." | Accept. | A stricter version could drop the FEMA sentence and only say "call your pharmacist or prescriber." |
| 5 | **High-rise fire reading (R-13-2).** USFA and NFPA's high-rise sheet: leave by the stairs by default; seal in only if you cannot get out. NFPA's general "may be safer defending in place" is undefined and not repeated; the page tells no one to defend in place on their own judgment. | Accept. | Asking NFPA or a fire marshal to clarify would add time. |
| 6 | **Window when sealing in (R-13-3).** Documents differ (top and bottom, slightly, or not mentioned). The page tells no one to open a window. | Accept. | Delete the window sentence entirely. |
| 7 | **Shelter-or-evacuate framing (R-14-1).** Four deciding factors (hazard, warning time, location, official order) replace the removed "fast = shelter, slow = leave" shorthand; a diagram shows it. | Accept. | Rewrite wording; the structure is ours, the dependence is Ready.gov's. |
| 8 | **Chemical shelter in place (R-14-3).** CDC (June 2026) and Ready.gov (April 2023) differ slightly (turn off vs recirculate ventilation; highest floor vs few openings); no sealed-room duration anywhere. | Prefer CDC's wording; drop Ready.gov's recirculation option. | Keep both as now (already shown with their difference). |
| 9 | **Custody, pick-up and card privacy (R-15-4).** No source; the page defers to the school's rules, makes no legal claims, warns that a lost card exposes information, and offers a minimal version. | Accept, ideally after a quick read by a child-safety professional. | Remove the custody note. |

## What happens after you decide

1. A human reviewer records approval (name and date) in each page's `safety_review` and sets `status.editorial` to `reviewed`. Pages not yet approved stay draft. The three tools are gated in the taxonomy and need the same step.
2. Run `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py --public`, and the test suite.
3. The lead imports `build/wp/*.html` into WordPress as drafts and checks them in the real theme. **This has never been done.** WordPress writes are not part of this lane and need your separate go-ahead.
4. Publish after you view the drafts in WordPress.

## Not done yet, and not skippable

* **Integration:** this work does not sit on the R2-R48 chain. A trial merge conflicts in 10 files (the four shelter articles, `CLUSTER-shelter.md`, `shelter.json`). The lead has to reconcile it with the QD corrections already applied there before anything ships.
* **Independent QD** of these pages has not happened (the lead's cross-check was explicitly not QD).
* **In WordPress/Assembler:** never tested. Print scoping uses `:has()` and layouts use container queries; both need a check inside the theme.
* **Other browsers and assistive technology:** only Chromium (Edge) was run; no screen reader, Firefox or Safari.
* **Source links:** no human has opened any of the 45 sources; `human_link_check` is false for all.

## Honest estimate

The text and tools are ready for a human to review. The slow steps are the human approvals, the integration merge, and the first look inside WordPress. If decisions 1 to 9 are answered, the remaining engineering is small.
