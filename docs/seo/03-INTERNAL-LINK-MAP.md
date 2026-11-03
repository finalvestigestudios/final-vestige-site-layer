# 03 - Internal-linking map and content architecture

Principle: every link goes from a page that already covers the topic to another page that covers it, using the target's own title as anchor text. Nothing here makes a claim; links are navigation. Source of the link lists: `tools/build_changeset.py` (the exact markup is in `04-CHANGESET-DIFFS.md`).

## Cluster 1 - Engineering failure case studies  (hub: The Failure Chain, page 1029)

Hub: `/the-failure-chain/` (a method guide whose worked cases are Quebec Bridge, Hyatt Regency and others). Before: 3 links in content (the Library and one post). After: "Worked examples on Final Vestige" block with 9 case studies.

| Post (ID) | Gets guide link + these posts |
|---|---|
| Teton Dam (291) | St. Francis Dam, Vajont, Quebec Bridge |
| St. Francis Dam (166) | Teton Dam, Vajont, Silver Bridge |
| Vajont (146) | Teton Dam, St. Francis Dam, Silver Bridge |
| Silver Bridge (258) | Quebec Bridge, Sunshine Skyway, Teton Dam |
| Quebec Bridge (276) | Silver Bridge, Sunshine Skyway, St. Francis Dam |
| Sunshine Skyway (287) | Silver Bridge, Quebec Bridge, Three Mile Island |
| Three Mile Island (285) | SL-1, Sunshine Skyway, Silver Bridge |
| SL-1 (221) | Three Mile Island, Teton Dam, Silver Bridge |

The hub also lists Malbone Street (621), which already linked to the guide.

## Cluster 2 - Disputed or incomplete records  (hub: The Archive Trail, page 189)

Hub: `/the-archive-trail/` ("Verify Historical Claims"; 2 content links before). Posts: Apollo 1 (434; ignition source not proved), Halifax Explosion (269; whether Coleman saved the train is disputed), Franklin Expedition (433). Each links to the guide and to the other two; the guide lists all three.

## Cluster 3 - The Public Record (accountability tree)

Five case pages had 0 in-content internal links and 1 inbound each. Each gets a "More from The Public Record" block: its category hub, sibling case where one exists, Evidence Room, The Public Record.

| Case page | Links to |
|---|---|
| Watergate (1313) | Abuse of Power hub, Iraq WMD, Evidence Room, The Public Record |
| Iraq WMD (1314) | Abuse of Power hub, Watergate, Evidence Room, The Public Record |
| Andrew Do (1316) | Public Money & Private Power hub, Maximus, Evidence Room, The Public Record |
| Maximus (1315) | Public Money & Private Power hub, Andrew Do, Evidence Room, The Public Record |
| Gabriel Fernandez (1312) | Failures to Protect hub, Evidence Room, The Public Record |

## Not done in this change set (and why)

- **Other 22 "the-..." guides** (Lost Landscape, Weather Window, Findspot, etc.): each has one inbound content link. They need posts that genuinely use their method; the keyword-package work is the natural source. Candidate pairings are listed in the ledger as next waves, not forced into unrelated posts.
- **Remaining ~40 posts** (e.g. Galveston, Port Chicago, USS Thresher, General Slocum): no matching hub exists yet. A new "Fire, Ship and Submarine Safety" or "Dams" hub would be a new page; deferred until the founder chooses whether to publish new hub pages (drafts only otherwise).
- **Menu / footer changes**: not touched (Appearance > Menus is a site-wide change).
- **Category and tag archives** (`/category/catastrophe/` etc.) are already linked from posts; not edited.
