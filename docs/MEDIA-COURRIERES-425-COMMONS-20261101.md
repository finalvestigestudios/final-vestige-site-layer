# Courrières 1906 — nine-image archival identity and conditional 960px QA

**Date:** November 1, 2026. **Scope:** Media Recovery draft PR #183, separate from Site QA #154 and homepage visual design. **Article:** https://finalvestige.com/2026/08/20/the-word-came-out-of-the-mine-courrieres/ (post 425).

## Evidence and limitations

The frozen authenticated WordPress-source inventory of October 30 records 9 inline images: 1 first-party (900×591 stored HTML dimensions) and 8 Wikimedia Commons Special:Redirect original-source references. This sprint compared all nine **exact stored source URLs and ALT strings** against the immutable inventory (blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`). No fresh WordPress authenticated read was performed. We opened **eight separate Commons HTML file catalog pages** through an independent text retriever on November 1. The canonical file titles match the original stored Special:Redirect path names, but **image binaries, hash identity, real visitor-image HTTP statuses, and transferred bytes were not verified**.

| FV slot | Archival source | Catalog dimensions | Conditional no-upscale derivative | Important qualification |
|---|---|---:|---:|---|
| 425:0 | Existing WordPress first-party | 900×591 in stored HTML | 900×591 | Already <960px wide; do not replace speculatively |
| 425:1 | [Commons: pit 2 rescue group](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_Groupe_de_Sauveteurs,_Fosse_n%C2%B0_2.jpg) | 1245×792 | **960×611** | Original photographer unknown |
| 425:2 | [Commons: victims brought up](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_La_remonte_des_victimes.jpg) | 1226×761 | **960×596** | Uploader credit not proof of 1906 original creator |
| 425:3 | [Commons: survivors treated](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_Les_rescap%C3%A9s_sont_soign%C3%A9s.jpg) | **798×1024** | **798×1024** | Stored redirect requests width=1280, greater than native width; no upscale |
| 425:4 | [Commons: German rescuers arrive](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_Arriv%C3%A9e_des_Sauveteurs_allemands.jpg) | 1244×791 | **960×610** | Author/title independently verify before reuse |
| 425:5 | [Commons: Guglielminetti-Dräger equipment](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_Appareil_Guglielminetti-Drager_(01).jpg) | **994×625** | **960×604** | Stored redirect requests width=1280, exceeds original; preserve device identity |
| 425:6 | [Commons: Le Petit Journal cover](https://commons.wikimedia.org/wiki/File:Courri%C3%A8res_1906_LeJ.jpg) | **924×1105** | **924×1105** | Stored redirect requests width=960; this is an **illustration** dated 25 March 1906, sourced to BnF/Gallica **bpt6k716688z/f1** |
| 425:7 | [Commons: last survivor](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_Berthou,_le_dernier_survivant,_24_jours_dans_la_Mine_en_feu.jpg) | 1227×783 | **960×613** | **Identity discrepancy:** archival filename spells **Berthou / 24 days**; FV ALT says **Berthon / approximately 25 days**. Resolve carefully; not a confirmed factual error |
| 425:8 | [Commons: miners strike](https://commons.wikimedia.org/wiki/File:Catastrophe_de_Courri%C3%A8res_-_La_gr%C3%A8ve_des_mineurs.jpg) | 5098×3193 | **960×601** | Commons attributes photograph to **E. Baron** in Douai |

Source cross-check: [Pas-de-Calais departmental archives](https://www.archivespasdecalais.fr/Recherche-par-commune/Lettre-C/Courrieres/Catastrophe-de-Courrieres) records the catastrophe and archival postcards; [French Ministry of Culture historical analysis](https://histoire-image.org/oeuvres/catastrophe-courrieres) identifies the 25 March 1906 BnF magazine illustration. Archive documentation does not mean blanket binary-republication permission.

## Rights, caching, browser and 76% measurement gates

Commons pages display public-domain claims, but many image records explicitly call for separate **US public-domain rationale**; a digitization, photograph of a printed image or uploader credit may involve distinct legal facts. All eight candidate masters remain **rights HOLD**. Do not hotlink-circumvent, download, mirror, transform or WordPress-upload any image without individually checking licensing, required attribution, creator/chronology and exact binary identity. No post block rewrites, production writes or spending occurred.

For verified missing images, Site QA should use its existing logged-out desktop/mobile browser workflow to capture the rendered image, its currentSrc URL, final redirect/network image GET status, content type, naturalWidth/Height, bytes and screenshot. A text retriever's ability to open a Commons HTML catalog is **not a successful browser image response**. If a rights-cleared copy is authorized later, create a controlled derivative capped at **960px width without upscaling**, preserve aspect ratio, compute SHA-256 and verify photo/credit visually before staging. Any measured percentage saving must be based on comparable same-page actual encoded image transfer totals and cache conditions, not summed library original bytes.

Current claims **42 browser-broken** and **76% transferred weight saved** remain **unverified**; 61 published posts, 355 source image references, 288 stored offsite references and 13 >1.5MiB WordPress originals remain the inventory baseline.

## Engineering evidence

- Machine-readable nine-slot ledger: `qa/media-recovery/courrieres_425_commons_20261101.json`.
- Strict source/rights/960px validator: `qa/media-recovery/validate_courrieres_425.cjs`.
- Regression: `qa/media-recovery/test_courrieres_425.cjs`, **31/31 negative-mutation checks passed** against exact committed GitHub source in isolated JS with Node compatibility shims. Native Node CI remains outstanding.
- Source census blob SHA: `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`. Guest-browser statuses, sha256 of master and actual encoded transfer bytes are **null**, not inferred.
