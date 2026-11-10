# Publishing investigations on Dekrov Insights

This is the repository's HTML publishing contract for humans and AI agents. Read the **current** `pages.json`, `pages/_template/index.html`, this guide and the shared scripts before every publication. The site is static GitHub Pages: no build, account, framework or backend is needed to read an article. The existing optional reaction service remains unchanged.

## 1. Research before writing

- Read the topic history and catalog; compare stories by meaning, not headline. Update the same URL for substantive follow-up facts. Never create another page just to repeat a topic.
- Use English for all public article content, captions, alt text and metadata. Explain the mechanism, dates, causes, changed behavior, shipped fix/version/commit, limitations and practical consequences where known. Do not invent missing details or your own tests.
- Read primary documents, relevant releases, exact commits/PRs/issues and research. Seek substantive independent tests and community objections when available. Community popularity is not verification.
- Keep provenance separate from confidence: `official` = vendor/project statement; `independent` = named external evaluation/research; `community` = discussion/opinion; `unconfirmed` = explicitly unverified report. These labels do not certify truth. State methodology, date, evaluator and limitations for numbers.
- If sources disagree, place their claims side by side, cite both and state whether methodology, version or dates explain the difference. If unresolved, say so. Never average incompatible benchmarks.
- Public availability does not grant reproduction rights. For images, verify a license, permission, ownership or other applicable basis. Otherwise link to the original. Never present generated illustrations as screenshots, photographs, experiments or real evidence.

## 2. Create or update one page

1. Choose a stable lowercase hyphenated slug (`[a-z0-9]+(?:-[a-z0-9]+)*`). Check both `pages.json` and `pages/` for existing coverage.
2. Copy `pages/_template/index.html` to `pages/<slug>/index.html`. Replace **all** `{{TOKENS}}`; HTML-escape text and attribute values. Do not publish the template itself.
3. Preserve header, sidebar `data-site-nav`, footer, theme switcher, `data-root="../../"`, script/style paths, and exactly one reactions block. Set `body[data-page]` to the slug. Never change an existing slug/counter key for a title update.
4. Preserve `article.article-body.research-article[data-article-version="2"]`. Keep `theme.js` in the head and `article.js`, `article-likes.js` and `site.js` near the end. Do not duplicate shared styles/scripts or add third-party libraries.
5. Fill title, description, OG title/description/type/url, canonical URL, Twitter card and real publication/update dates. Canonical and `og:url` must equal `https://dekrovdev.github.io/dekrov-insights/pages/<slug>/`. Only change the update date for meaningful edits; explain corrections near the changed material.
6. Add substantive sections, with explicit unique heading IDs. The required anchors are `overview`, `technical-deep-dive`, `explained-simply`, `conclusion`, `sources`. Headings can be phrased for the subject. `explained-simply` can be the section ID, with a separate heading ID. Keep the direct plain-English jump from the template so it works without JS.
7. Add optional Evidence Analysis, Community Reactions, Visual Evidence, timeline, FAQ or comparison sections **only when useful material exists**. Images may appear next to the claim they explain; they do not need their own section. Mention relevant research gaps in the conclusion instead of publishing empty headings.
8. `Explained Simply` is a standalone explanation of the same story from zero: define terms, use a concrete analogy, explain how people are affected, what now works or fails, what to do and what remains uncertain. Several substantive paragraphs are usually needed; it is not a one-line takeaway or a second technical summary. A short-content validator warning requires editorial review, not filler.
9. Put the complete numbered bibliography after Conclusion, before reactions. Evidence discussion may appear earlier. Link important claims to this bibliography next to the claim; the bibliography links directly to original sources.

`article.js` generates a compact table of contents, a prominent plain-English button, reading-navigation buttons and citation return links. It only lists headings that exist. Legacy articles get the navigation without invented plain-English content or changes to their claims.

## 3. Numbered sources and evidence

Use stable numbers in bibliography order. Repeated claims can cite the same source. Use precise URLs, including commit SHA, PR/issue number, documentation fragment or paper identifier. Prefer immutable permalinks for code; include exact version when discussing mutable documentation.

```html
<p>The project says version 2 contains the fix.
  <a class="citation" href="#source-1" aria-label="Source 1">[1]</a></p>
<aside class="evidence-note" data-evidence="official" aria-label="Evidence qualification">
  <span class="evidence-label">Official statement</span>
  <p>The release note confirms a shipped patch; it does not establish results in every environment.</p>
</aside>
<!-- At the end of the article: -->
<ol class="source-list">
  <li id="source-1" data-source-type="official">
    <span class="evidence-label">Official</span>
    <a href="https://github.com/OWNER/REPO/commit/FULL_SHA">Project — precise patch title</a>
    <span class="source-detail">Published YYYY-MM-DD. Supports: the changed code and patch version.</span>
    <time datetime="YYYY-MM-DD">Accessed YYYY-MM-DD</time>
  </li>
</ol>
```

Replace example URLs/dates; do not publish fictitious evidence. Allowed `data-source-type` values: `official`, `independent`, `community`, `unconfirmed`. Use the matching visible label. Put the qualifier next to claims too when readers could mistake a report for a verified result. Unknown cause, proposed workaround and released fix are different states. A working URL only establishes reachability, not truth or permission to reproduce.

## 4. Inline images, diagrams and comparisons

Store assets under `pages/<slug>/assets/`. Prefer local assets to fragile hotlinks. Use an appropriate size, lossless SVG for original diagrams, and WebP/AVIF with a fallback for photographs when beneficial. Never rasterize text-heavy evidence into an unreadable image. Avoid scripts, trackers and untrusted active SVG. Give charts an accessible data table and units/methodology/source. Give diagrams an equivalent text explanation.

```html
<figure class="article-figure" data-visual-kind="screenshot" data-rights="Permission from AUTHOR, YYYY-MM-DD">
  <a href="./assets/interface-full.webp" data-lightbox aria-label="Enlarge interface screenshot">
    <picture>
      <source type="image/webp" srcset="./assets/interface-640.webp 640w, ./assets/interface-1280.webp 1280w" sizes="(max-width: 700px) 100vw, 760px">
      <img src="./assets/interface.jpg" alt="Describe the relevant interface state and visible finding"
           width="1280" height="800" loading="lazy" decoding="async">
    </picture>
  </a>
  <figcaption>Figure 1. What this image establishes; date/version and any crop or redaction.
    <span class="figure-credit">AUTHOR — <a href="https://ORIGINAL-URL">Original source</a> ·
      <a href="https://LICENSE-URL">LICENSE or permission details</a></span>
  </figcaption>
</figure>
```

For original work use `data-visual-kind="diagram"` or `chart` and state “Original diagram by Dekrov; explanatory illustration, not observed evidence.” Record a real rights basis in `data-rights`, credit, and source/permalink. AI-assisted artwork must be visibly labeled as an illustration; it cannot establish real events. `data-rights` records the author's determination, **not an automatic legal check**.

Use a `div.figure-comparison` containing two complete `figure.article-figure` elements. Give each a visible `span.figure-label` (“Before · version/date”, “After · version/date”), its own alt text, source and rights. The pair sits side by side on desktop and stacks on mobile. Compare equivalent conditions and explain any difference. No slider or drag gesture is required.

Images open in an accessible native dialog: keyboard Enter, Escape, close button, focus return. Without JavaScript the anchor opens the original asset. Failed inline images show alt text and preserve caption/source links. Test errors deliberately in a temporary browser fixture; never ship an intentionally missing image. A source-only figure can contain a caption and original link, with an explanation that reproduction permission was unavailable.

### Tables, code and timelines

```html
<div class="table-scroll" role="region" aria-label="Evidence comparison" tabindex="0">
  <table class="research-table">
    <caption>What each observation supports</caption>
    <thead><tr><th scope="col">Claim</th><th scope="col">Evidence</th><th scope="col">Limit</th></tr></thead>
    <tbody><tr><th scope="row">One specific claim</th><td>Linked observation [1]</td><td>Scope of that observation</td></tr></tbody>
  </table>
</div>
<pre tabindex="0" aria-label="Code excerpt"><code>HTML-escape &lt;code&gt; and ampersands here.</code></pre>
<ol class="timeline">
  <li><time datetime="YYYY-MM-DD">YYYY-MM-DD</time>Documented event, with a citation.</li>
</ol>
```

Use real `a.citation` elements instead of literal `[1]` in published tables/timelines. Define technical terms inline, for example `<dfn>inference</dfn> — running a trained model to produce an answer`.

## 5. Register in the catalog

Keep exactly one Home object first. Insert a new article immediately after Home; catalog order is the archive order. Preserve all other entries. New v2 articles require all four fields:

```json
{"slug":"unique-slug","title":"Specific factual title","meta":"Investigation · Nov 10, 2026","summary":"A concise, honest description of the finding and its limits."}
```

`site.js` builds the sidebar, homepage rows and Latest research from this list, deduplicating valid slugs. **Do not hand-edit homepage rows for routine articles.** Existing rows are a no-JavaScript/network-failure fallback; they are replaced in catalog order after a successful fetch. A newly published article is automatically listed for JS-enabled readers. For no-JS readers the direct article URL still works; the static homepage fallback is not auto-built. Do not claim automatic catalog discovery without a `pages.json` entry.

## 6. GitHub API publication (atomic and concurrency-safe)

1. Read the current `main` ref, commit and tree, plus current article/catalog blobs. Record the head SHA. Re-read at publication time; automated runs may overlap.
2. Assemble only the new/changed HTML, assets and `pages.json`. For UTF-8 files use Git Trees `content`; for binary assets create Git blobs with `encoding: base64`, then reference their blob SHAs in a tree. No credentials belong in files or HTML.
3. Create a tree using the **current base tree SHA**, changing only the intended paths; create one commit with the current head as its parent.
4. Update `refs/heads/main` as a fast-forward with an expected-head lease when supported. Never force-push over another author's commit. If rejected, inspect the fresh head, merge the catalog semantically, revalidate, and create a new commit on that head. Do not retry blindly or overwrite new entries.
5. A connector with only Contents API can create/update files with current blob SHAs, but that is not atomic. Prefer a branch plus a single tree/commit or a PR; avoid showing a catalog entry before its HTML/assets exist. Do not remove or replace unrelated files.
6. Check the validation workflow and **Pages deployment for that exact commit**. A successful push or unrelated previous run is not proof of deployment. The site keeps GitHub's existing branch-based Pages deployment; validation reports failures but does not gate that separate built-in deployment. Agents must validate before pushing.
7. Open the deployed article, asset URLs, homepage and sidebar; verify the new content/metadata rather than an old cached 200 response. Only then publish social links. Record the commit, workflow URLs, source-check results and any unverified links in the publisher's worklog.

## 7. Validation commands and release checklist

No installation or build is needed. Python 3.11+ runs the validator:

```sh
python scripts/validate_articles.py
python scripts/test_validation.py
python scripts/validate_articles.py --links --report /tmp/dekrov-link-report.json
```

The first command checks **all** existing article paths, catalog registration, duplicate IDs/slugs, shared scripts/reactions, and local assets/anchors. The v2 contract additionally checks required anchors/metadata, numbered citations, bibliography classifications/access dates, figure rights/source metadata, alt text, image dimensions and lazy loading. Legacy research is not retroactively certified or rewritten. Treat editorial warnings as review tasks, not proof of quality.

The optional link check probes unique external links on v2 articles with a timeout, redirect limit and HEAD→GET fallback. 404/410 fail validation. Rate limits, authorization responses, outages or network restrictions are reported **unverified**, never “working.” Review those manually, use a legitimate accessible source where possible, and disclose unresolved gaps. Checks do not validate remote fragments, factual support, image copyright, paywalled content or every legacy external URL. CI uploads an availability report; it does not put request timestamps into article prose automatically.

Before publication:

- Read the article end to end. Resolve placeholders, unsupported claims, conflicting evidence, empty sections, copied text and unclear qualifiers. Confirm that the simple explanation covers the same important facts and limitations.
- Test desktop and mobile widths (at least 390px; also 320px for overflow), light/dark theme, actual image loading and deliberate image failure, code/table scrolling, enlarged images with keyboard close/focus return, citations/return links, reading buttons, and direct plain-English jump.
- Test without JS: article, sources and plain-English jump must remain available. Test catalog failure: existing homepage fallback and Home link must survive.
- Ensure the new article appears once in the homepage and sidebar, current-page indicator is correct, and Latest research points to the first article. Preserve one reaction widget and its original key. Stub the external counter in automated tests; never increment production likes for a test.
- Verify exact-commit CI and Pages success and real public content. Report remaining reachability/editorial limitations honestly. Do not post a link to an undeployed article.

The public `pages/research-method/` article is a working example with original diagrams, comparison figures, evidence types, a timeline, code, a table and a standalone plain-English section. It is editorial methodology, not a new AI news investigation.

## 8. Synchronize the publisher runbook

Keep Google Drive's “04 — Dekrov Auto Publisher — Full Runbook” as the automation's operating instruction. Add a reference to this guide as its repository implementation contract, require the v2 template/anchors and components, and require the commands and exact-commit deployment checks above. Keep existing topic-history, English-language, anti-duplication, source-integrity and social-publication rules. Neither the schedule nor account destinations need to change.
