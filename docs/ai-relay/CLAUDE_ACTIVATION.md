# Claude activation: FV AI Relay

**Production ownership:** Claude exclusively owns final video creative output, editing, narration, motion graphics, thumbnails, and professional packaging. ChatGPT coordinates QA and attribution; Grok handles distribution preparation.

**1. Read authoritative public links:**
- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/3090
- https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/ai-relay/README.md
- https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/ai-relay/handoff.schema.json
- Existing Flannan briefing: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/3089

**2. Write-access proof:** Using the GitHub login/app authenticated for Claude, post a short issue comment on #3090 with exactly: `ACK CLAUDE FV-HANDOFF-V1 — GitHub identity: <actual account login>`. Do not paste passwords, API tokens, Drive download signatures or unreleased research. If you lack the ability to comment, record that limitation to the founder instead of falsely claiming success. The owner must independently confirm this identity; public ACK text alone is insufficient.

**3. Automated polling:** In Claude's available orchestration environment, arrange a scheduled check of #3090 issue updates and any Claude-owned linked issues at a sensible cadence (ideally hourly or after release milestones). The ChatGPT hourly monitor does not automatically run Claude. Use existing authorized GitHub tools or a runtime already under the owner's control; do not require the owner to paste every status message.

**4. When a package is completed:** Write `MANIFEST.json`, `SOURCE_LEDGER.csv`, `RIGHTS_LEDGER.csv`, `SHA256_CHECKSUMS.txt`, final MP4s, clips, thumbnails, subtitles, platform copy and approved Drive or object-store references. Only link public-safe metadata from issue comments. Use a new `fv-handoff-v1` event with status READY_FOR_QA, next_owner chatgpt. Do not mark rights PASS without evidence.

**5. After QA HOLD:** Read the exact defects from the relay issue and resolve with versioned assets; post one update with new asset references, never overwrite without revision.

**6. Never:** Auto-publish social posts, share all of Drive publicly, write passwords, modify another assistant's campaign queue, bypass the owner's required platform approval, publish as personal Facebook, or assume other assistants received a message before they actually acknowledged it.

**Success test:** Your account-authenticated HELLO is observed; ChatGPT responds; later one non-public test handoff goes from Claude → QA → Grok with verified attribution and zero accidental posts.
