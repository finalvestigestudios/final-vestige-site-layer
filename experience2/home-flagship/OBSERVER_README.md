# The Observer Lab — homepage Experience 2.0 (draft-only)

Isolated source-controlled chapter stacked on PR #192, which stacks on #184 and #177. Frozen PR #49, Apollo Research Desk #158 and the live WordPress homepage remain unchanged.

## What visitors experience
Original cinematic on-page comparison titled **Two records. One missing detail.** Frame A includes a small circular FV seal on a CSS-drawn paper specimen; Frame B omits the seal. The specimens are explicitly **STUDIO ILLUSTRATIONS, NOT ARCHIVAL RECORDS**. Buttons let readers compare voluntarily; there is no score, timer, autoplay, commercial offer or mental-health claim. Native details explains the difference and limits of interpretation. JS-off shows both frames and the answer disclosure; JS-on adds two accessible 49px A/B buttons, polite status, keyboard support, pressed state and exception fail-open. Reduced-motion CSS and responsive design are included.

Scientific context: Rensink, O'Regan & Clark (1997), DOI https://doi.org/10.1111/j.1467-9280.1997.tb00427.x; Simons & Levin (1998), DOI https://doi.org/10.3758/BF03208840. This illustration does **not** replicate their experimental stimuli or provide any validated measure of user perception.

## Source and asset integrity
No third-party images, fonts, scripts, brand art or copied Blue Corridors effects. All visual geometry and treatment created with scoped CSS. The only links lead to peer-reviewed source records and the existing published historical Puységur article. Absolutely no affiliate URLs or unverified product claims. Additional first-party code: 5,344 HTML bytes, 8,895 CSS bytes, 1,807 JS bytes, and a seven-chapter navigation entry in `index.html`.

## Testing / hold
See `qa/OBSERVER_BROWSER_RESULTS.json`. Eight authored local static tests passed. Chromium exercised the exact module source with JS at 320,360,390,580,768,1024,1440,1920 and without JS at 390,1440; 10/10 runs passed. Screenshots at 1440/390 and full local browser harness are included in the founder's staging ZIP. The GitHub blobs match the locally tested bytes. The **complete combined standalone flagship and actual WordPress theme were not browser-tested**. Staging, axe-core, mobile Safari, VoiceOver/NVDA, independent QD, verified CI and p75 Core Web Vitals are still required. Do not merge/deploy or write WordPress/theme/nav/settings. Preserve 72 Margins, Focus Fieldbook and Jetpack.
