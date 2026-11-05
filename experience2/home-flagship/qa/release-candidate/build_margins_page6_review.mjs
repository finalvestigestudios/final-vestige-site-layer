#!/usr/bin/env node
/**
 * Offline only. Turns a PUBLIC Page 6 Gutenberg JSON export into review-only
 * blocks HTML, with source drift and preservation guards. Never calls WP APIs.
 *
 * node build_margins_page6_review.mjs --in public-page-6.json \
 *      --out page-6-margins.review.blocks.html --review-only
 */
import { readFile, writeFile, realpath } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { patchPage6 } from "./margins_page6_native_patch.mjs";

const PINNED_PUBLIC_MODIFIED = "2026-11-04T14:39:24";
const hash = text => createHash("sha256").update(text, "utf8").digest("hex");
const args = process.argv.slice(2);
const flag = name => args[args.indexOf(name) + 1];
const die = msg => { console.error("REVIEW HOLD:", msg); process.exitCode = 1; };
const permitted = new Set(["--in", "--out", "--review-only"]);
const seen = new Set(args.filter(s => s.startsWith("--")));
if (!seen.has("--review-only") || [...seen].some(s => !permitted.has(s)) ||
    args.indexOf("--in") === -1 || args.indexOf("--out") === -1 ||
    args.length !== 5 || args[args.indexOf("--in") + 1]?.startsWith("--") ||
    args[args.indexOf("--out") + 1]?.startsWith("--")) {
  die("requires only --in <public-page6.json> --out <name.review.blocks.html> --review-only");
} else {
  const input = resolve(flag("--in")), output = resolve(flag("--out"));
  if (input === output || !output.endsWith(".review.blocks.html"))
    die("review output must be a different .review.blocks.html path");
  else {
    try {
      const envelope = JSON.parse(await readFile(input, "utf8"));
      const page = envelope.structuredContent?.data || envelope.data || envelope;
      const forbidden = ["password", "meta", "author", "email", "users", "subscribers", "_crdt_document"];
      if (forbidden.some(k => Object.hasOwn(page, k)))
        throw Error("export contains private/edit-context metadata; provide ONLY id, modified, status, content, title");
      if (page.id !== 6 || page.status !== "publish" || page.modified !== PINNED_PUBLIC_MODIFIED)
        throw Error("page ID/status/modified drift; re-review current Page 6 before updating the pin");
      const html = typeof page.content === "string" ? page.content : page.content?.raw;
      if (typeof html !== "string") throw Error("missing public Gutenberg content");
      const result = patchPage6(html);
      const receipt = {
        release_gate: "HOLD", environment: "LOCAL_REVIEW_ONLY", source_site: "finalvestige.com",
        source_page_id: page.id, source_modified: page.modified,
        source_sha256: hash(html), proposed_sha256: hash(result.html),
        preserved: result.receipt,
        network_calls: 0, production_writes: 0,
        open_gates: ["independent QD", "current exact-source WordPress/Assembler integration",
          "axe WCAG 2.2 AA and manual zoom/touch/keyboard/no-JS", "measured current Lighthouse",
          "media/rights and conversion verification", "CI green exact SHA", "founder release approval"]
      };
      // Output is a REVIEW ARTIFACT, not an API upload. Keep it out of production.
      await writeFile(output, result.html, { encoding: "utf8", flag: "wx", mode: 0o600 });
      await writeFile(output + ".receipt.json", JSON.stringify(receipt, null, 2) + "\n",
        { encoding: "utf8", flag: "wx", mode: 0o600 });
      console.log(JSON.stringify({review_file: output, receipt_file: output + ".receipt.json",
        records: result.receipt.record_count, unchanged_tail_bytes: result.receipt.unchanged_tail_bytes,
        source_sha256: receipt.source_sha256, proposed_sha256: receipt.proposed_sha256,
        release_gate: "HOLD"}, null, 2));
    } catch(e) { die(e.message); }
  }
}
