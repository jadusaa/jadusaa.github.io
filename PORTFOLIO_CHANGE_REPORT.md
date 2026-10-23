# PORTFOLIO CHANGE REPORT — 2026-10-23

Branch `portfolio-buyer-clarity` · baseline `main` @ `49e1501` · HEAD `59cd01f`
**Nothing pushed or published. `main` and the live site are unchanged.**

---

## 1. What changed and why it helps a buyer

| # | Change | Why a buyer is better off |
|---|---|---|
| 1 | **Hero shortened and made specific.** Headline `BUILD SYSTEMS THAT KEEP WORKING.` → `n8n WORKFLOWS BUILT AND REPAIRED.` Height cut from full viewport to ~520px desktop / 538px mobile. | The service is legible in the first two seconds instead of after a scroll. |
| 2 | **Hero stats strip removed** (23/23 · 9/9 · 22/22). | The old strip led with the unverified 22/22 figure. Numbers now sit *next to* the evidence they describe, not as a hero claim. |
| 3 | **Two explicit actions**: `Watch workflow demo` → the recording; `Discuss a workflow` → contact. | A buyer can either watch the proof or start the conversation, not hunt for a link. |
| 4 | **Three bounded offers moved above the case studies**, replacing four vague capability cards. | A buyer asking "can you do my thing?" answers that before reading long write-ups. |
| 5 | **Engagement sequence added** under "How we'll work together" — understand → agree a bounded paid milestone and acceptance checks → demonstrate and hand off. | Sets scope and acceptance expectations before money is discussed. |
| 6 | **Case studies cut to four buyer questions**: problem demonstrated, what it visibly does, what was tested, what is out of scope. Deep test detail moved into `<details>` disclosures. | A non-technical buyer reads a short summary; a technical buyer opens the disclosure and still finds specifics. |
| 7 | **The demo video is now embedded and playable** with a real poster frame, controls, no autoplay, `preload="metadata"`, and a direct download fallback. The narrated version replaced the silent one. | Previously the button was an unlabelled raw MP4 link called "Watch **Live** Workflow Demo" — on a recording. |
| 8 | **Opportunity Engine demoted to secondary evidence** with the stale metric deleted. | The strongest public proof (two inspectable demos) leads; an internal tool no longer implies client results. |
| 9 | **Contrast and mobile fixes** (see §3). | Text that failed WCAG AA is now legible, and the page no longer requires horizontal scrolling on a phone. |

---

## 2. Claims: retained, qualified, removed

### Retained (verified against the repos this session)
| Claim | Evidence checked |
|---|---|
| 23 acceptance checks, 23 passed, 0 failed | `evidence/acceptance-summary.json` in the reliability repo |
| Coverage: validation, idempotency, concurrency/atomic claim, retry+backoff, 429/503 classification, partial failure, safe replay, receipts | `coverage_categories` in the same file |
| 9 cases, 9 passed | `results.json` in the classifier repo |
| Forced 503 → 3 attempts (1 + 2 retries) with backoff, then clean failure | `results.json` T7 `attempts` array |
| Transient 503 recovered on the next attempt against the real API | `results.json` T9 `attempts`, `retry-evidence.json` |
| Malformed model output returns an error, never a fabricated classification | `results.json` T6 → `malformed_llm_output` |
| Video is 2:00, 1920×1080, has an audio track, and carries burned-in captions | `ffmpeg -i` on the asset; frame inspection |

### Qualified (weakened on purpose — these are the honesty edits)
| Now says | Because |
|---|---|
| "Independent demo • **synthetic data**" badge printed directly under each case-study title | Previously the disclosure was a footnote-ish line inside the Proof block. |
| "**Outside scope:** not a production deployment, no real client traffic, not tested at multi-tenant scale or against live third-party APIs, not universal recovery" | 23 passing tests describe the listed scenarios only. |
| "A schema-valid response is **not proof of classification accuracy** — synthetic messages, no accuracy rate claimed" | The tests check schema conformance, not correctness on real leads. |
| "**Recorded** walkthrough … recorded, not live" | The old button said "Watch **Live** Workflow Demo". |
| "The two public demos …" instead of "the projects below" | Projects now sit above the About section, so "below" was wrong. |

### Removed
| Removed | Reason |
|---|---|
| `22/22 live regression tests passed` (Opportunity Engine) | Superseded and stale. Deleted from `portfolio.json` (`proof`, `build`, `flow`, `bullets`, `reliability`, `metric`, `metric_label`) and confirmed absent from `index.html`. |
| `25–30 hrs/week` capacity chip | The owner directive is to omit numeric capacity when no authoritative current statement resolves it. Replaced with a neutral `Remote work` chip. |
| Hero `22/22` badge | Not replaced with `33/33` — deliberately no hero metric for the internal tool. |
| "Watch Live Workflow Demo" | Inaccurate label. |
| `<track kind="captions">` element | **Correction made this pass:** burned-in captions do not populate a `<track>`, and there is no `.vtt` file. An empty track renders a broken captions menu, so the element and the code path that emitted it were both removed. The video keeps its visible burned-in captions. |
| "This is the process I propose … not a record of past client work." | **Correction made this pass:** unnecessarily defensive. Section retitled **"How we'll work together"**, which describes a proposed process without the apology. |

### Never claimed
No accuracy rate, revenue, hours saved, conversion, client count, testimonials, certifications, years of experience, or start dates. No price. No RAG, WhatsApp, telephony, video-pipeline or SaaS-platform capability.

---

## 3. Checks actually performed

### Build
```
python3 scripts/build_portfolio.py  → Built index.html with 3 public projects (case-study mode)
python3 scripts/validate_portfolio.py → VALIDATION PASS   (exit 0)
```
Template markers `AUTO_PROJECTS_START/END` and `AUTO_HOWIBUILD_START/END` all present and matched; no marker repair needed.

### Layout — measured in the DOM, not eyeballed
Real emulated viewport via CDP, `documentElement.scrollWidth` vs `clientWidth`:

| Width | Overflow | H1 size | Hero height | CTA above fold | Video width | Elements past viewport |
|---|---|---|---|---|---|---|
| 390px | **0** | 34px | 538px | yes | 312px | 0 |
| 768px | **0** | 58px | 510px | yes | 690px | 0 |
| desktop 1440 | **0** | 84px | 521px | yes | 469px | 0 |

**Two real layout bugs were found and fixed during this pass** (neither was visible in the previous report):
1. The `<video>` rendered at its intrinsic **1920px** width and was clipped — no width rule existed. Fixed with `width:100%; max-width:100%; height:auto` → 312 / 690 / 469px.
2. The mobile media queries overrode the new headline with `18vw` / `17vw`, making the H1 **66px** at 390px. Retuned to `clamp(32px,8.2vw,58px)` / `clamp(30px,8.6vw,44px)` → **34px**, and `.accent-line` from `.47em` to `.92em` (it had been shrinking the second line). Hero shortened from `min-height:92svh` to `auto`.

### Video playback — actually played, not just HTTP 200
Headless Chrome, real media pipeline:
```json
{"t":0.65,"paused":false,"ready":4,"dur":120,"err":null,"w":1920,"h":1080,
 "poster":"lead-routing-poster.jpg"}
```
`currentTime` advanced, `paused:false`, `readyState:4`, `mediaError:null`, poster resolved.

### Links — all 19 anchors resolved
- 6 in-page anchors (`#top`, `#work`, `#services`, `#about`, `#contact` ×2): all targets exist
- 2 `mailto:` → `jawadsabir150@gmail.com`
- 6 GitHub links: **HTTP 200** each (2 repos, acceptance-summary, docs tree, results.json, ARCHITECTURE.md, profile)
- 1 local video: 200, 5,509,979 B

### Accessibility (runtime audit)
- 20 headings, **0 hierarchy jumps**
- `lang="en"`, one `<main>`, 1 video with a figcaption label
- 12 `.button` elements, **0 under 44px** tall
- 3 `<details>` disclosures, all with summary text
- `prefers-reduced-motion` block present
- 0 `<img>` elements on the page — the visual system is inline SVG/CSS, so there are no missing alt attributes

### Claim scan on generated HTML
`22/22`=0 · `33/33`=0 · `25–30`=0 · `Watch Live`=0 · `1 min 60 s`=0 · `RAG`=0 · `WhatsApp`=0 · `telephony`=0 · `senior`=0 · `expert `=0 · `guarantee`=1 (the word appears only inside the disclaimer "not an open-ended guarantee").

### Duration label corrected
The asset is 119.97 s. The label said "1 min 60 s"; it now reads **"2 min"**.

---

## 4. Remaining limitations

1. **No human visual review this pass.** The image-analysis service returned connection errors for most renders, so layout was verified by DOM geometry and screenshots that could not all be re-read visually. Geometry is conclusive for overflow/position; it is **not** a judgement on visual polish. A human should glance at `/Users/lg96/PORTFOLIO_REVIEW_PREVIEW/` before publishing.
2. **Captions are burned into the video, not a caption track.** The recording therefore has no selectable/translatable caption track, and screen-reader users get the figcaption only. Producing a `.vtt` is possible from the existing audio but was not done (out of scope for this pass and it would require transcription).
3. **No mobile device testing.** Headless emulation at three widths is not the same as a real phone (touch targets, iOS Safari video behaviour).
4. **The Opportunity Engine card still exists** as a secondary example. It is labelled "Private internal tool • not client work", has no repository or screenshot links, and claims only that "a regression suite … 33 checks, all passing" was run. If it is not wanted at all, it is one deletion in `portfolio.json`.
5. **GA4 instrumentation was not reviewed.** Existing `gtag` `cta_click` handlers are still on the GitHub/evidence buttons but the new hero and video buttons have none. Not a defect, but click tracking is now inconsistent.
6. **No accessibility score is claimed.** The audit above reports specific properties, not a Lighthouse or axe score; neither tool was run.

---

## 5. Files, preview, rollback

### Changed files (vs `main` @ `49e1501`)
```
template.html                        | 123 +++++++++--------
portfolio.json                       | 135 ++++++++++++-------
scripts/build_portfolio.py           |  90 +++++++++----
index.html                           | 198 ++++++++++++++--------  (generated)
assets/video/lead-routing-poster.jpg | new, 64,805 B
assets/video/poster-candidate.jpg    | new, 118,581 B  ← unused; see note
```

> **Note on `poster-candidate.jpg`:** an earlier uncropped frame. The used poster is `lead-routing-poster.jpg` (browser chrome cropped out). `poster-candidate.jpg` can be deleted before publishing.

### Where the work lives
- **Branch repo:** `/Users/lg96/PORTFOLIO_SITE` (same clone as the real working copy; your unrelated untracked media files were left alone)
- **Review worktree:** `/Users/lg96/PORTFOLIO_REVIEW`
- **Static preview (no server needed):** `/Users/lg96/PORTFOLIO_REVIEW_PREVIEW/index.html`
- Originally built in `/tmp/portfolio_work`; copied to the above, verified (16 source files, commit `6b938f0` present), so the `/tmp` copy is now disposable.

### Preview
```bash
open /Users/lg96/PORTFOLIO_REVIEW_PREVIEW/index.html
# or, if the local file blocks the video:
cd /Users/lg96/PORTFOLIO_REVIEW_PREVIEW && python3 -m http.server 8899
# then open http://127.0.0.1:8899/index.html
```
A local server is recommended — `file://` can block MP4 playback in some browsers.

### Rollback
```bash
cd /Users/lg96/PORTFOLIO_SITE
git worktree remove /Users/lg96/PORTFOLIO_REVIEW --force   # discard the review copy
git branch -D portfolio-buyer-clarity                      # delete the branch
rm -rf /Users/lg96/PORTFOLIO_REVIEW_PREVIEW
```
`main` is at `49e1501`, untouched by this work. A rollback deletes only the branch; the live site was never modified.

### Publishing (not done — awaiting approval)
```bash
cd /Users/lg96/PORTFOLIO_SITE
git checkout main && git merge --ff-only portfolio-buyer-clarity && git push origin main
```
GitHub Pages then redeploys `index.html`. Requesting approval for **this one action only**.


---

# ADDENDUM — verification pass on the two flagged gaps

Requested checks: reconcile the anchor count, confirm the contrast fixes, then look at the preview.
Both gaps were real. **The contrast gap was the more serious one: the previous report claimed contrast fixes that had never been re-measured, and the accent gradient was still failing.**

## A1. Anchor count reconciled — 19 elements, 15 unique destinations

The "19" and the 15-row list were both correct but measured different things, which was not stated:

| Measure | Count |
|---|---|
| `<a href>` elements in the DOM | **19** |
| Unique `href` destinations | **15** |
| Destinations verified | **15 / 15** |

Duplicates that account for the difference:
- `#contact` × **3** (nav link, "Available for remote work" pill, "Discuss a workflow")
- `media/lead-routing-proof-walkthrough-narrated.mp4` × **3** (hero CTA, video element, download fallback)

Re-verified this pass, every unique destination:
- 5 in-page anchors — all targets exist
- 6 GitHub links — all **HTTP 200**
- 2 `mailto:` → `jawadsabir150@gmail.com`
- 1 local MP4 — 200, 5,509,979 B

**No anchor was missed.** Two new anchors appeared since the earlier audit (the video's download fallback and the in-card "Watch recorded demo"), which is why the element count moved from 17 to 19.

## A2. Contrast — the claim was false; now measured and fixed

A proper audit was run this time: every rendered text run, composited against its real background, WCAG relative luminance, large-text rule applied (≥24px, or ≥18.66px bold → 3:1; otherwise 4.5:1).

**Result before the fix — one genuine failure that the earlier report had claimed was fine:**

`.accent-line` — the second headline line — is **gradient text** (`background-clip:text`), so it has `color: transparent` and cannot be measured by a naive colour check. Measuring the gradient stops:

| Stop | Colour | Contrast on `#08090b` | Verdict (needs ≥3:1 large) |
|---|---|---|---|
| 0% | `#f5f6f8` | 18.42:1 | pass |
| 52% | `#7b818b` | 5.08:1 | pass |
| **96%** | **`#262a31`** | **1.38:1** | **FAIL — nearly invisible** |

So "BUILT AND REPAIRED." faded out into the background at its right end. Fixed by raising the stops to `#9aa1ab` (7.65:1) and `#646a74` (3.66:1).

**Re-measured after the fix, at both widths:**

| Viewport | Text runs measured | Failures |
|---|---|---|
| 390px | 168 | **0** |
| 1440px | 168 | **0** |

The originally-failing surface colours, now confirmed in the DOM:

| Element | Before | Now | Ratio |
|---|---|---|---|
| `footer` | `#606874` 3.54:1 | `#8d95a1` | 6.05:1 |
| `.project-number` | `#69717d` 4.04:1 | `#8d95a1` | 6.05:1 |
| `.services-grid span` (now `.offer-num`) | `#6c7480` 4.22:1 | `#8d95a1` | 6.05:1 |
| `.terminal-top small` | `#5d6672` 3.42:1 | `#8d95a1` | 6.05:1 |
| `.metric-grid small` | `#68717d` 4.03:1 | `#8d95a1` | 6.05:1 |
| `.accent-line` gradient end | 1.38:1 | `#646a74` | 3.66:1 |

## A3. Two layout defects found during the visual review

The DOM geometry checks had passed, but they were measuring the wrong things. Looking at the render exposed:

1. **Case-study grid collapse.** `.project-content` was a **two-column grid** inherited from the old design. The rewritten case study places 10 children in it, so they scattered across two columns: video 469px, paragraphs 590/621px, alternating — visually incoherent. Replaced with a single-column `.project-body` (max 860px). Video is now **860px** on desktop.
2. **Video distorted.** With `object-fit:contain` and an `auto 1920/1080` intrinsic ratio inside a grid cell, the box rendered **2.16:1** instead of **1.78:1** — the video was letterboxed inside a wrong-shaped frame. Fixed with an explicit `aspect-ratio:16/9`.

**Verified after both fixes:**

| Width | Overflow | Video | Aspect | Truncated text | Off-screen elements |
|---|---|---|---|---|---|
| 390px | 0 | 312×176 | **1.778** | 0 | 0 |
| 768px | 0 | 675×380 | **1.778** | 0 | 0 |
| 1440px | 0 | 860×484 | **1.778** | 0 | 0 |

## A4. Visual review — what a human eye actually saw

| Screen | Verdict |
|---|---|
| Mobile hero (390px) | **Pass.** Headline fully visible, both buttons full-width and clearly differentiated (filled primary / outlined secondary), balanced rhythm, nothing clipped except the intentional marquee. |
| Desktop case study | **Pass.** Widescreen video with real poster, native controls rendering `0:00 / 1:58`, clear hierarchy, comfortable spacing. |
| Mobile case study | **Not visually confirmed.** The image-analysis service returned connection errors repeatedly for this view. Geometry is conclusive (312×176, 1.778, controls present, poster set, caption 9px below the player, 44px tap targets, body 312px wide, 0 truncation) but **this one view has not been seen by an eye.** |

## A5. Remaining limitation, stated plainly

The vision service failed on roughly half the frames this pass, including the mobile case-study view. Everything measurable was measured and passes; **one mobile view rests on geometry rather than sight.** That is the only thing standing between this and a fully eyeballed sign-off.

Branch `portfolio-buyer-clarity` is now at **`5e167e0`**. `main` still `49e1501`. Live site untouched.
