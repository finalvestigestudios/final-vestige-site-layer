# Apollo R459 — unresolved source-link labels and print contrast (DRAFT / HARD HOLD)

Parent PR #3021 (R458), Issues #150, #820, #818; only `experience2/apollo-r457` files touched. Research Desk #158 and homepage PR #49 stay frozen.

## Trust correction
The existing source gallery displayed links labelled "NASA record for" even where (a) the `KSC-20170124-PH_KLS01_0129` catalogue link could not be independently retrieved, or (b) the NASA crew-portrait article for `S67-19766` is retrievable but the exact image-ID mapping has not been independently certified. R459 adds a prominent, always-rendered source-acceptance HOLD and adds qualifying suffixes on the two links. These remain clickable research leads, never accepted permission or proof of particular archival identity. All six source cards are readable without JS; no image is embedded.

## Print reliability
The print stylesheet previously made the section ink black and white but left card backgrounds dark and some card metadata gold, potentially printing black-on-dark when print background graphics is enabled. Print media now forces white card surfaces, black text and borders, visibly underlined links, hides only optional filters and preserves source disclosures. No hard-coded placement, map pins, analytics or paid CTA added.

## Verification
Run `php -l apollo_rights_gallery.php`, `python qa/test_contract.py`, and `python qa/browser_qa.py` plus `python qa/r459_print_qa.py` (new read-only print/contrast acceptance harness). Browser tests use PHP-rendered markup with `page.set_content`, not hosted WordPress. Hosted navigation/axe-core/navigated LCP/CLS and real device screen-reader remain HOLD_NOT_RUN. No production activation, WordPress change, Grok post, merch activation or tracking authorized.

## Conversion priority
Grok authenticated Apollo long-form asset -> evidence gallery -> **one free Apollo investigation link** -> only when a rights-cleared, checkout-and-delivery verified original educator kit exists, a separate founder-approved paid option. No sales attribution claims: paid order, returns/fees and 7/30-day qualified-human sessions remain unavailable. Independent founder/QD release gates still apply.
