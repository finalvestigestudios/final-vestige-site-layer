# WordPress staging blocker - diagnosis and correction

**Environment used:** Windows 11, Node v24.11.0, `@wp-playground/cli` 3.1.61 (free, `npx`), PHP 8.3.33, WordPress "latest" resolved by Playground on 2026-11-02, official Assembler 0.0.126 (`public-api.wordpress.com/rest/v1/themes/download/assembler.zip`, sha256 `c7bf7da02463f1c75e715107f346a26799c8cd0bd89b4ef26d8b25fa1ff354f0`, only the top folder renamed `assembler-wpcom/` -> `assembler/`). No subscription, no account, no import from finalvestige.com except public pages.

## 1. The 302 and 502 are real, and they are normal start-up states

Clean boot, polled once per second with full headers (`evidence/boot_trace_playground_cli.txt`):

```
01:58:37  HTTP/1.1 502 Bad Gateway   X-Powered-By: Express      (x22, about 30 s)
01:59:07  HTTP/1.1 302 Found         X-Powered-By: Express   content-length: 0   location: /
01:59:08  HTTP/1.1 200 OK            x-powered-by: PHP/8.3.33
          200, 200, 200 ... stable afterwards
```

- Both the 502 and the 302 are produced by the **Playground CLI's own Express front end**, not by WordPress or PHP. The 502 is the front end answering while its PHP workers are still booting; the single 302 has `Location: /` (a redirect to the same URL, zero-length body) and is followed by the first 200.
- It is **not** a site-URL/home-URL problem, HTTPS enforcement, canonical redirect, reverse-proxy assumption, theme initialisation or front-page routing issue: after the first 200 the same URL returns 200 every time, `home_url` and the request host are both `127.0.0.1:9400`, and no `Set-Cookie`/`Location` to another host was ever seen.
- Consequence: a readiness probe that treats "first non-200" as failure, refuses to follow the one self-redirect, or has a short budget will report exactly "repeated 302 and intermittent 502". Correct policy (used in the probe loop for this sprint; `run_stage.py` itself only prepares and launches): 502 and one self-redirect mean "still booting" while the process is alive; ready only on a non-empty 200; a dead process or a `critical error` body is a hard failure.

## 2. The faults that actually killed instances (each reproduced)

| # | Symptom | Cause | Correction |
|---|---|---|---|
| a | 502 forever, then connection refused | Git Bash (MSYS) rewrote the VFS target `/wordpress/...` into `C:/Program Files/Git/wordpress/...`, so the theme/plugin never existed and activation failed | Use `--mount-dir <host> <vfs>` (also required for drive letters) and `MSYS_NO_PATHCONV=1` |
| b | Blueprint step fails with `READBACK MISMATCH`, then "critical error", server exits | `runPHP` runs with no current user, so KSES silently rewrote the seeded markup | `wp_set_current_user(1)` (disposable local admin, has `unfiltered_html`) before the insert, and a byte-for-byte readback |
| c | Fatal during the seed step | Seeding page ID 6 after the parity templates, which had already consumed ID 6 | Seed the page first, then the parity step |
| d | Site CSS missing (white page) | WordPress drops `styles.css` from a seeded `wp_global_styles` record | Ship the identical public CSS as a stylesheet (stage-only) |
| e | Layout of the preserved sections wrong | Live CSS is keyed to `.page-id-6`; per-block layout CSS (`wp-container-...`) is only emitted for blocks WordPress renders | Page seeded as ID 6; public inline block-support CSS captured in `snapshot/live-block-support.css`. Result: the preserved Dispatch/Jetpack section renders at exactly the live height (444.08 px both). |

## 3. The failed CI run (#580)

Run 41407578279, job `ephemeral-wordpress`: step "Launch ephemeral local WordPress ..." exited 2 after 4 m 16 s (07:39:22 -> 07:43:38) with no diagnostic lines in the job log. Observed in the same log: Node **v22.23.4** while `@wp-playground/cli@3.1.61` declares `node >=24.18.0` / `npm >=11.16.0` (EBADENGINE warnings, step 9).

**Status: cause NOT proven.** I did not reproduce the CI run. Node 24.11 (below the declared 24.18) worked here, so the engine mismatch is a suspect, not a finding. Recommended for that lane when it resumes: Node >= 24.18, `--mount-dir`, the 502/302-as-booting probe policy above, and capture the Playground stdout on failure.

## 4. Correction delivered

`wp-candidate/run_stage.py` + `build_candidate.py` start one isolated WordPress with the real Assembler theme, the public-safe template parity and the composed page seeded as ID 6, in one command, with the preserved Jetpack form made inert (CSP `form-action 'self'`) so nobody can subscribe an address to the production list from the local copy. It replaced the staging-abstraction stack for this release; that stack was not imported.

```
python experience2/home-flagship/wp-candidate/run_stage.py --work <dir outside repo> --assembler-zip <assembler.zip> --delivery inline --launch
```
On Windows from Git Bash: `export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'`.

**Limits (still true):** this is WordPress + Assembler on Playground, not WordPress.com Atomic. It cannot show Jetpack behaviour, WordPress.com cache/CSP/proxy behaviour or real-user Core Web Vitals.
