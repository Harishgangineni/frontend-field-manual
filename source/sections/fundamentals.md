# Pillar: Core Web Fundamentals

At junior level, HTML/CSS/JS/TS interviews test whether you know what a tag or keyword *does*. At senior/staff level, the bar shifts entirely: interviewers assume you know the syntax and instead probe whether you can reason about **trade-offs at scale** — why semantic markup is an SEO and AI-indexing trust signal in 2026, why a rendering-pipeline choice costs 200ms of jank across a million sessions, why a type-system decision either prevents or enables an entire class of production incidents, and why a "correct" answer in a toy example becomes the wrong answer once three teams and a design system depend on it. This pillar is where you demonstrate that fundamentals aren't beginner topics you've outgrown — they're the substrate every architectural decision you'll defend in a staff-level interview sits on top of.

## HTML

### Semantic Structure & Document Architecture
- 🏗️ Semantic tags (`<article>`, `<section>`, `<nav>`, `<header>`, `<main>`) aren't stylistic sugar — they're a machine-readable contract. In 2026, AI-driven search and crawler agents lean on this structure as a "trust signal" to summarize and index pages correctly; a `<div>`-soup site is invisible to that layer regardless of how it looks to a human.
- `<article>` = self-contained/independently distributable (blog post, product card); `<section>` = thematic grouping that needs surrounding context; `<div>` = last resort, meaningless container. Exactly one visible `<main>` per page — assistive tech and crawlers use it to skip repeated chrome and find the actual content.
- `<b>`/`<i>` are purely visual; `<strong>`/`<em>` change what a screen reader *says* (tone, emphasis) — this is the classic senior trap question because both pairs render identically but are semantically opposite in intent.
- `<figure>`+`<figcaption>` explicitly binds an image to its caption for assistive tech, rather than relying on spatial proximity. `<address>` is scoped strictly to author/owner contact info — never a random address mentioned in body content.
- Document-level metadata carries real product weight: `<!DOCTYPE html>` forces Standards Mode (skipping it silently reintroduces Quirks Mode bugs); `<html lang>` drives screen-reader pronunciation and search locale targeting; `<title>` is simultaneously your tab label, SERP headline, and bookmark name — three UX surfaces from one tag.
- Void/self-closing elements (`<img>`, `<br>`, `<hr>`, `<input>`, `<meta>`) can't contain children — a common linting gotcha in generated markup pipelines.

```text
Landmark navigation model (screen-reader shortcut keys):
<header> → <nav> → <main> → <aside> → <footer>
        (press 'L'/'R' to jump landmark-to-landmark, skipping repeated chrome)
```

**Senior Perspective:**
- 🏗️ Semantic structure is a cross-cutting concern that simultaneously buys you SEO, accessibility compliance, and AI-agent indexability for free — three stakeholder asks solved by one architectural discipline, which is why it belongs in a linting/CI gate, not a style guide nobody reads.
- ⚖️ Choosing `<div>` over the correct semantic tag isn't neutral — you're trading a one-time authoring convenience for permanent, compounding accessibility and SEO debt that's expensive to retrofit once content teams have built on top of it.
- 👥 This is the one HTML topic non-engineering stakeholders (legal/compliance, SEO, content) actually care about — framing it as "risk reduction" rather than "code cleanliness" gets it prioritized on a roadmap.

### Accessibility & Assistive Technology
- ⚖️ The "First Rule of ARIA": if a native element already has the behavior you need, use it instead of `role="..."` on a `<div>`. Native `<button>` gets focus, Enter/Space handling, and screen-reader announcement for free; a `<div role="button">` requires you to hand-roll all of that in JS and you will eventually miss an edge case ARIA can only approximate.
- ARIA attributes layer meaning on top of markup: `aria-label` (inline text, no visible label exists), `aria-labelledby` (points to — and can combine — existing visible elements), `aria-describedby` (supplementary info, not the primary name). `role="alert"`/`"navigation"`/`"tablist"` identify *what* an element is when the tag itself is generic.
- Live regions (`aria-live="polite"` vs `"assertive"`) control interruption priority — polite waits for the current sentence to finish (save confirmations), assertive interrupts immediately (critical errors only). Overusing assertive is a common senior-review finding that makes screen-reader UX worse, not better.
- `tabindex="0"` joins natural tab order (custom interactive widgets), `tabindex="-1"` removes it but keeps `.focus()`-ability (modal containers), positive values should never ship — they hand-roll a tab order that breaks the moment the page layout changes.
- 📉 Focus management on modal open/close is a three-step contract: move focus in, trap it inside, restore it to the trigger element on close. Skipping the "restore" step is the most common accessibility regression in SPA modal libraries — keyboard users silently lose their place.
- `autofocus` looks helpful but actively harms screen-reader users (dropped into a field with zero page context) and mobile users (virtual keyboard eats half the viewport before content is seen) — treat it as opt-in per interaction, never default-on.
- `alt=""` (explicit empty string) vs. omitting `alt` entirely are not equivalent: empty tells the screen reader "skip this, it's decorative"; omitting it makes the reader announce the raw filename. `aria-hidden="true"` hides visible decorative content (icons) from AT; a `.sr-only`/visually-hidden CSS class does the inverse — hidden visually, readable by AT (icon-only buttons).
- The Accessibility Object Model (AOM) is the emerging API that lets you set accessibility properties directly in JS (`el.accessibleNode.role`) instead of accumulating `aria-*` attributes in markup — relevant for Canvas-heavy or highly dynamic UIs.

```text
Modal focus lifecycle:
Open → Focus first interactive element → Trap Tab/Shift+Tab inside → Close → Restore focus to trigger
```

**Senior Perspective:**
- 📉 Accessibility bugs rarely show up in manual QA because sighted engineers don't hit them — they surface as legal/compliance risk (ADA/WCAG lawsuits) and silent conversion loss from a user segment nobody is instrumenting, which is why senior engineers push for automated `axe`-style CI gates rather than "we'll get to it."
- ⚖️ Reaching for ARIA over native elements trades a small amount of markup verbosity now for an open-ended maintenance liability later — every ARIA attribute you add is a contract you now have to keep in sync with behavior by hand, forever.
- 👥 Accessibility work is one of the few technical decisions with a legally-exposed non-engineering owner (legal, compliance) — framing PRs in terms of WCAG conformance level gets faster sign-off than "best practice."

### Forms & Interactive Controls
- `<button type="submit">` (default, triggers form submission) vs `<button type="button">` (inert, JS-driven) — forgetting to set `type="button"` inside a `<form>` is the classic bug where a "open modal" button accidentally submits and refreshes the page.
- `<label for="id">` isn't optional polish: it's read aloud on focus (accessibility) and expands the clickable hit-area to the label text (usability), which matters disproportionately on small mobile checkboxes/radios.
- `<datalist>` (suggests, doesn't restrict — user can still submit free text) vs `<select>` (forces a value from the list) is a UX decision, not just a markup one: use `<datalist>` when you want to guide without gatekeeping.
- HTML5 native validation (`required`, `minlength`/`maxlength`, `min`/`max`, `step`, `pattern`) gets you a working validation UX with zero JS — the senior nuance is knowing this is a UX layer, not a security boundary; server-side validation is still mandatory.
- `<fieldset>`+`<legend>` groups related inputs and gives screen-reader users the "big picture" context (e.g., "Shipping Address") before they hit the first field in the group — losing this on a long checkout form measurably increases abandonment for AT users.
- `placeholder` is not a label substitute: it vanishes on input (losing context), is often skipped by screen readers, frequently fails contrast ratios, and adds cognitive load by forcing users to remember it. This is a very common front-end code-review finding.
- `<dialog>` gives native modal (`.showModal()` — traps focus, dims background, blocks page interaction) and non-modal (`.show()` — floats without blocking) behavior for free. The Popover API is the lighter-weight sibling: `popover` attribute + `::backdrop`, rendered in the browser's Top Layer, with automatic "light dismiss" (click-outside/Esc closes it) and no built-in focus trap.
- `<details>`/`<summary>` gives a fully native, keyboard-accessible accordion/disclosure widget with zero JavaScript — worth defaulting to before reaching for a component library.
- `<optgroup label="...">` creates unselectable visual category headers inside a `<select>` for long option lists. `data-*` attributes (accessed via `.dataset` in JS) pass small config values from markup into script without an extra API round-trip.

```text
Popover API            vs   <dialog>
Light dismiss                Requires explicit close / Esc
No focus trap                Traps focus (.showModal())
No default backdrop dim      ::backdrop dims background
Use: menus, tooltips          Use: critical/blocking UI
```

**Senior Perspective:**
- ⚖️ Native HTML5 validation and `<dialog>`/Popover buy you accessibility and browser-optimized UX for free, but you give up fine-grained control over error message styling and cross-browser animation timing — worth it for 90% of forms, not worth it the moment design has bespoke validation UX requirements.
- 🏗️ Reaching for `<dialog>`/`<details>`/`<datalist>` before a JS component library is a deliberate architectural bet: it shrinks your JS bundle and inherits browser-native accessibility, at the cost of less design flexibility — the right call for most CRUD forms, wrong call for a highly custom design system.

### Media, Images & Web Components
- `srcset` gives the browser multiple resolutions of the *same* image to pick based on viewport/DPI; `<picture>` is for **art direction** — swapping the actual image content (landscape desktop vs. cropped portrait mobile) or format (AVIF/WebP with JPEG fallback). Confusing these two is a common interview trap.
- 📉 `loading="lazy"` defers offscreen image/iframe downloads until near-viewport — a near-free performance win on image-heavy pages, since below-the-fold assets that are never scrolled to are never fetched at all. `decoding="async"` lets the browser decode image bytes off the main paint thread, reducing scroll jank on image-heavy 2026 apps.
- SVG (DOM-based, every shape is a stylable/clickable element, infinitely sharp) vs. Canvas (pixel-based, browser "forgets" what was drawn) is a scale decision: SVG for icons/logos/simple diagrams, Canvas for high-performance games, dense data-viz, or real-time image manipulation.
- Video/audio media has its own attribute vocabulary: `muted`+`autoplay` (most browsers require muted for autoplay to work at all), `playsinline` (critical on iOS to avoid the video hijacking the whole screen), `poster` (avoids showing a black box or blurry first-frame while downloading), and `<track kind="subtitles|captions">` pointing at WebVTT files for translations vs. hearing-impaired support (captions include non-speech cues like "[Music playing]"). Fallback content nested inside `<video>`/`<audio>` tags serves users on browsers that can't play the media at all.
- Shadow DOM gives Custom Elements true style/DOM encapsulation — a `<my-calendar>` component's internal CSS never leaks out, and the page's global CSS never leaks in. `<template>` holds inert markup you clone via JS for efficient repeated elements (list rows); `<slot>` is the placeholder inside a shadow root that lets consumers inject their own content into a component's layout.

```text
Web Component encapsulation:
Page CSS ──✕──> [ Shadow Root: internal styles + <slot> for consumer content ] ──✕──> leaks to page
```

**Senior Perspective:**
- ⚖️ `<picture>`'s art-direction flexibility costs you markup verbosity and more asset-pipeline complexity than plain `srcset` — reach for it only when the *content* of the image genuinely needs to change by viewport, not just its size.
- 📉 `loading="lazy"` and `decoding="async"` are the two cheapest, lowest-risk Core Web Vitals wins available — they should be default-on in any image-heavy page template, not something you retrofit after a Lighthouse audit flags LCP.

### Metadata, SEO & Resource Loading
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` is the literal on-switch for responsive design — without it, mobile browsers render at a virtual desktop width (~980px) and shrink-to-fit, making your carefully-built media queries never fire.
- `<link rel="canonical">` tells search engines which URL is the "master copy" when the same content is reachable at multiple paths, preventing your own pages from cannibalizing each other's SEO ranking.
- `<meta charset="UTF-8">` must be the very first element inside `<head>` so the browser can correctly parse every subsequent byte, including the `<title>` itself.
- `<noscript>` provides a degrade-gracefully path for JS-disabled environments — still relevant for accessibility tooling and restricted corporate/government environments even though JS-enabled usage is near-universal.
- Open Graph (`<meta property="og:*">`) tags control exactly which image/title/description a social platform shows in a link preview card — without them, the platform guesses, and the guess is frequently a broken or unprofessional-looking post.
- 📉 Resource hints form a cost/urgency ladder: `dns-prefetch` (IP resolution only, cheapest), `preconnect` (DNS + TLS handshake, use for critical third-party domains like your API/font provider), `preload` (forces immediate download of a specific high-priority asset you know you need this page load). Misusing `preload` on non-critical assets actively *hurts* performance by stealing bandwidth from what the page needs first.
- The 2026 favicon story is no longer a single `.ico`: SVG for scalability, an Apple Touch Icon variant, and a `manifest.json` for PWA icon sets — three declarations for one visual asset across desktop tabs, iOS home screens, and installed-app contexts.

**Senior Perspective:**
- 🏗️ The viewport meta tag, canonical links, and OG tags are the three highest-leverage, lowest-effort tags in the entire `<head>` — missing any one of them silently breaks an entire acquisition channel (mobile UX, organic search, social referral) that's invisible until someone asks "why is our bounce rate on social traffic so bad."
- ⚖️ Aggressive use of `preconnect`/`preload` trades faster perceived load for real bandwidth contention — over-hinting delays the assets that actually matter for this page's first paint, so it needs to be curated per-template, not applied blanket-wide.

### HTML5 Fundamentals: DOCTYPE, Canvas & SVG
- HTML5's `<!DOCTYPE html>` is deliberately the simplest doctype in the language's history: it needs no Document Type Definition (DTD) reference because HTML5 isn't SGML-based the way HTML 4.01 was — every HTML 4.01/XHTML doctype had to point at a specific DTD (**Strict**, **Transitional**, or **Frameset**) to tell the parser which rules applied, which is why those older doctype strings were long, easy to get wrong, and impossible to remember. Strict DTDs dropped presentational/deprecated elements (`<font>`) and disallowed framesets entirely; Transitional kept them for backward compatibility — legacy trivia today, but recognizing *why* HTML5 collapsed this into one doctype is the actual signal.
- `<canvas id="..." width="..." height="...">` gives JavaScript a pixel-addressable drawing surface via `getContext('2d')` — every drawing method (paths, arcs, `fillRect`, `drawImage`) mutates that pixel buffer directly. That's the mechanism underneath the SVG-vs-Canvas trade-off already covered in Media, Images & Web Components: SVG keeps a live, re-renderable DOM node per shape, while Canvas has no memory of what it drew and must redraw the entire scene from scratch the instant anything needs to move or update.
- SVG's practical advantages all compound from one architectural fact — it's XML text, not pixels: infinite zoom/print without quality loss, every shape independently scriptable/style-able via CSS or JS event handlers (it has its own DOM), and the markup itself is searchable, indexable, and diffable in source control in a way a `<canvas>` bitmap fundamentally can't be. SVG is a W3C recommendation with its own root `<svg>` element and shape primitives (`<circle>`, `<path>`, `<rect>`) rather than a JS drawing API.

```text
SVG vs Canvas, mechanism-level:
SVG:    shape → DOM node (kept) → change an attribute → browser re-renders that node
Canvas: shape → pixels (forgotten) → change anything → re-run the entire draw script
```

**Senior Perspective:**
- 🏗️ Knowing HTML5 dropped the DTD requirement because it isn't SGML-based signals a bigger fact: HTML5 standardized *parsing behavior itself* (how malformed markup gets error-corrected identically across browsers), not just new tags — that's the real reason "just add the doctype" fixed so many legacy rendering inconsistencies.
- ⚖️ Canvas's "browser forgets everything" model isn't a limitation to work around — it's the entire reason it's fast enough for games and dense data-viz; the moment a UI needs per-shape interactivity, hit-testing, or accessibility, that same property becomes the reason to reach for SVG instead.

### HTML5 Storage, Offline Capability & New Input Types
- `sessionStorage` and `localStorage` (the HTML5 Web Storage spec) exist to replace cookies for pure client-side data — nothing stored in either is auto-attached to outgoing server requests the way a cookie is, which is what makes them viable for meaningfully-sized data without a bandwidth tax on every request. The full persistence/capacity/transport trade-off table (plus IndexedDB and Cookies) is covered in depth in the JavaScript pillar's DOM, Events & Browser Platform APIs — the HTML5-era framing worth keeping here is that Web Storage was explicitly positioned as "cookies, but never sent to the server unless you ask."
- The Application Cache (`<html manifest="app.manifest">`) let a browser prefetch and store assets — including whole pages the user had *never visited* — purely from a declarative manifest file, a meaningfully different capability from the regular HTTP browser cache, which only ever caches what's actually been requested. It's since been fully deprecated and removed from the living standard: Service Workers (JavaScript pillar, Security, Delivery & Runtime Architecture) superseded it with a programmable, JS-driven network proxy instead of a fragile, near-impossible-to-invalidate manifest file — AppCache's failure mode was common enough in production to earn its own nickname ("AppCache Cache," for how permanently it could get stuck), which is the more interesting interview answer than the manifest syntax itself.
- HTML5's new `<input type="...">` values — `tel`, `search`, `url`, `email`, the `date`/`month`/`week`/`time`/`datetime-local` family, `number`, `range`, `color` — hand the browser semantic knowledge of *what kind* of value is expected. The payoff is automatic mobile keyboard switching (a numeric pad for `tel`/`number`, no shift-key hunting for `@` on `email`) and free native validation UX, both covered from the forms-architecture angle in Forms & Interactive Controls. Unsupported browsers fall back to a plain `type="text"` field automatically, which is exactly why adopting these has effectively zero downside.
- The other HTML5-era platform APIs worth naming by function, not syntax: Drag-and-Drop (native `draggable` attribute + `dragstart`/`drop` events, no library required), Cross-Document Messaging (`postMessage()` — the same mechanism the JS pillar covers for safe cross-origin `<iframe>` communication), Browser History Management (the History API's `pushState`/`popstate`, the foundation client-side SPA routing is built on), `contenteditable` document editing, and MIME type/protocol handler registration (`registerProtocolHandler()` — how a web app can register itself as the OS-level handler for `mailto:`-style links). HTML5's broader pitch was reducing reliance on plugin-based RIA technology (Flash, Silverlight, JavaFX) by giving the browser native equivalents of what those plugins used to provide.

```text
Application Cache → deprecated, manifest-file based, notoriously hard to invalidate
        ↓ superseded by
Service Worker → JS-programmable proxy, explicit cache control, offline-first PWAs
```

**Senior Perspective:**
- ⚖️ AppCache optimized for a simple declarative case (list the files, let the browser handle the rest) at the cost of near-impossible cache invalidation in practice; Service Workers trade that simplicity for full programmatic control, which is strictly more powerful but puts the invalidation strategy burden back on the engineer. Treating AppCache as a cautionary tale about that trade-off, not just a deprecated API, is the senior framing.
- 🏗️ The new input types are a rare "free" architectural win — semantic markup that costs nothing to adopt and pays off directly in mobile UX and native validation — which is exactly why a senior code review should flag any `type="text"` field that's actually collecting an email, phone number, or date.

### HTML5 New Structural, Text & Media Elements
```text
Structural/text elements HTML5 added beyond <article>/<section>/<nav>/<header>/<footer>:
<mark>        highlighted/relevant text (e.g. search-term highlighting)
<time>        machine-readable date/time, via a datetime="" attribute
<meter>       a scalar measurement within a known range (a gauge — quota used, a rating)
<progress>    completion progress of a task (determinate value, or indeterminate if omitted)
<details>/<summary>   native disclosure widget (see Forms & Interactive Controls)
<ruby>/<rt>/<rp>       East Asian typography annotations, with a fallback for browsers
                       that don't support ruby rendering
<bdi>         isolates text that may render right-to-left so it can't scramble
              surrounding left-to-right layout (user-generated content, mixed-locale UIs)
<wbr>         a suggested line-break point inside an otherwise unbreakable string
<hgroup>      groups multi-level headings (an <h1> title + <h2> subtitle) as one unit
```
- `<meter>` and `<progress>` look similar but answer different questions: `<meter>` communicates a static value *within a known range* (disk quota used, a star rating) and can render a warning color as it nears the max; `<progress>` communicates how far a task has gotten toward completion, and omitting its `value` attribute entirely gives an indeterminate "still working" state.
- `<command>` was part of the original HTML5 draft but was later dropped from the living standard entirely — a concrete example of why "which tags exist in HTML5" is a moving target, and citing the WHATWG living standard rather than a fixed circa-2014 spec is the technically correct framing to reach for in a senior interview.
- Media elements compose via `<source>`: a single `<video>`/`<audio>` tag lists multiple `<source src="..." type="...">` children in fallback order, and the browser plays the first format it can actually decode — the same "give the browser options, let it choose" pattern that `srcset`/`<picture>` later generalized to images (Media, Images & Web Components).

**Senior Perspective:**
- 👥 `<meter>`/`<progress>`/`<time>` are exactly the kind of unglamorous semantic elements that never come up unprompted but immediately signal depth when reached for correctly instead of a `<div>` plus a hand-rolled ARIA re-implementation — assistive tech support comes free.
- ⚖️ The `<source>` fallback-list pattern is the same underlying idea behind every "give the browser options" HTML5 API — `srcset`, `<picture>`, `<source>` in media — recognizing it as one recurring pattern rather than three unrelated syntaxes is what separates memorized syntax from architectural understanding.

**Predictive Interview Questions (HTML):**
1. Walk me through how you'd audit and fix an existing product page that scores poorly on both accessibility and SEO — where do semantic HTML, ARIA, and metadata each pull their own weight, and where do they overlap?
2. You're building a design system's modal component. Would you build it on native `<dialog>`, the Popover API, or a custom `<div>`-based implementation — and what does each choice cost you in accessibility, bundle size, and design flexibility?
3. Tell me about a time you pushed back on a design or PM decision because it would have broken accessibility or SEO at scale. What was the business risk you were mitigating, and how did you communicate it to a non-technical stakeholder?

**Executive Summary Cheat Sheet (HTML):** Semantic markup and ARIA aren't style choices — they're the shared substrate SEO, AI-indexing, legal accessibility compliance, and assistive-tech UX all depend on, so treat them as a CI-gated architectural concern, not a linting nicety. Native HTML (`<dialog>`, `<details>`, HTML5 validation, `srcset`/`<picture>`, resource hints) consistently out-performs a hand-rolled JS equivalent on accessibility and bundle size, and should be your default until a concrete design requirement forces you off it.

## CSS

### Box Model, Cascade & Specificity
- Every element is content → padding → border → margin. `box-sizing: border-box` (industry standard) makes a declared `width` the *total* width including padding/border; the legacy `content-box` default makes padding/border additive, which breaks predictable percentage-based layouts (two 50% boxes no longer fit side-by-side once padding is added).
- Specificity ranks inline-style > ID > class/pseudo-class/attribute > element/pseudo-element, with the universal selector (`*`) at zero. The Cascade resolves conflicts across three tiers in priority order: author styles → user styles (accessibility overrides like high-contrast mode) → user-agent defaults.
- ⚖️ Browsers match selectors **right-to-left**, not left-to-right — for `div .container p`, it first collects every `<p>`, then walks up checking ancestors. This is more efficient for the engine (fast rejection of non-matching leaf nodes) but means a selector that "reads" cheap on the left can still be expensive if the rightmost part matches thousands of elements.
- 📉 Margin collapsing (adjacent vertical margins merge to the larger value, not the sum) and Block Formatting Contexts (BFC — created via `display: flow-root`, `overflow: hidden`, `flex`, or `position: absolute`) are two sides of the same layout-isolation coin: BFC is the standard fix for float containment, margin collapse, and text-wrap-around-float bugs.
- `display: none` (removed from flow, no space, hidden from AT) vs. `visibility: hidden` (hidden, space preserved, hidden from AT) vs. `opacity: 0` (hidden, space preserved, still interactive and clickable, and — the trap — **still read by most screen readers**) are three distinct states with real accessibility and interaction consequences, not interchangeable "make it invisible" options.
- Modern selector/composition tools solve long-standing pain points: `:has()` is the long-awaited parent selector (`.card:has(img)`), `:is()`/`:where()` group selectors to cut repetition (`:where()` uniquely carries **zero specificity**, making it ideal for resets and design-system base styles that should always lose to a consumer's override), `@layer` (Cascade Layers) lets you group CSS into priority buckets independent of selector specificity — ending "specificity wars" without reaching for `!important` — and native CSS Nesting plus `@scope` (donut-scoping styles to a DOM subtree) bring Sass-like ergonomics and CSS Modules-like isolation natively, with zero build step.
- 📉 Uncontrolled `z-index` escalation ("z-index wars," stacking values like `999999`) is a symptom of missing architecture: fix it with centralized `--z-index-*` CSS variables defining the layering system explicitly, and `isolation: isolate` to give a component a fresh stacking context so its internals can't fight the rest of the page.

```text
Selector matching direction:  div .container p
Browser evaluates: <p> found → check ancestor has .container → check that has <div>
                    (right-to-left: cheapest rejection first)
```

**Senior Perspective:**
- ⚖️ `border-box` as a global reset is a near-zero-cost, high-value default — the only trade-off is remembering it when reading legacy code that assumes `content-box` math.
- 🏗️ Cascade Layers and `:where()` are the architectural fix for the "specificity wars" that historically forced teams into `!important` or brittle naming conventions like BEM — adopting them is a design-system-level decision, not a per-component one, because the layer order has to be established once, globally.
- 📉 Confusing `opacity: 0` with `display: none` is a recurring production bug class: an "invisible" element that's still tabbable, still clickable, and still announced by screen readers silently breaks keyboard navigation and creates confusing AT experiences — always ask "invisible to whom" before picking a hiding mechanism.

### Layout Systems: Flexbox & Grid
- The framing that scales: Flexbox is 1D (rows *or* columns — nav bars, button groups, single-axis alignment), Grid is 2D (rows *and* columns simultaneously — full-page layouts, galleries, bento-box designs). They compose freely — a Grid page layout with Flexbox inside the header for logo+nav alignment is a completely normal, expected pattern, and an element can be a flex child while itself being a grid parent to its own children.
- `justify-content` aligns along the **main axis**, `align-items` along the **cross axis** — and which physical direction each maps to *flips* with `flex-direction: column`, which is the source of "why does justify-content sometimes center vertically" confusion in code review.
- `flex-grow`/`flex-shrink`/`flex-basis` work together as starting-size + expand-to-fill + contract-if-needed; `fr` units in Grid divide *remaining* space after fixed-width tracks are accounted for, making proportional layouts trivial (`1fr 2fr` splits leftover space 1:2).
- `grid-template-areas` lets your CSS visually mirror your page layout as a text map — and a media query can completely rearrange the layout by only touching that map, not the individual item rules. `auto-fill` vs `auto-fit` differ only when there's leftover space: `auto-fill` leaves empty tracks (preserves the "slot"), `auto-fit` stretches existing items to fill it (fits items to container).
- `subgrid` solves the classic "align headers across sibling cards with variable text length" problem by letting a child inherit its parent's grid lines — previously impossible without JS measurement hacks.
- 📉 Flex/Grid items default to `min-width: auto`/`min-height: auto`, meaning a long word or oversized image can silently blow out the container and break the layout — explicitly setting `min-width: 0` is the standard, non-obvious fix that every senior CSS reviewer checks for.
- ⚖️ The `order` property changes visual position without touching the DOM — but screen readers and Tab-key navigation follow **source order**, not visual order. Reordering a "Submit" button to the top visually while it stays last in the DOM creates a jarring disconnect for AT and keyboard users; this is one of the highest-value "gotcha" questions in a senior CSS interview.
- Container Queries (`@container`) are the structural fix for the "component looks the same everywhere" problem Media Queries can't solve: a Card component can render as a compact list item in a narrow sidebar and a full featured layout in a wide content area — genuinely component-level responsiveness instead of viewport-level.
- `aspect-ratio` reserves layout space for media before it downloads, directly preventing Cumulative Layout Shift (CLS) — a Core Web Vital with real SEO and UX cost. Native `masonry` (via `grid-template-rows: masonry`) as of 2026 removes the need for JS libraries like Isotope for Pinterest-style layouts.

```text
Holy Grail layout, 3 lines of Grid:
grid-template-areas:
  "header header header"
  "nav    main   aside"
  "footer footer footer"
```

**Senior Perspective:**
- ⚖️ Container Queries let a component be genuinely reusable across contexts, but at the cost of an extra containment declaration and a mental model shift from "the viewport decides" to "the parent decides" — worth adopting for design-system components, overkill for one-off page sections.
- 📉 The `order`-property/DOM-order mismatch is a silent accessibility regression that never shows up in a visual QA pass — it's exactly the kind of bug that only a keyboard-only or screen-reader test catches, which is why senior teams bake it into their a11y test checklist rather than trusting code review alone.
- 🏗️ Grid vs. Flexbox isn't a "pick one" decision at the codebase level — the right senior default is Grid for page/section-level structure and Flexbox for component-internal alignment, composed together, rather than forcing one tool to do both jobs.

### Responsive Design, Units & Typography
- `rem` (relative to root `<html>` font-size) should be your default unit for almost everything — it respects user browser font-size preferences (accessibility), unlike `px` (absolute, breaks user zoom/font preferences) or `em` (relative to immediate parent, useful specifically for spacing that should scale with adjacent text, like button padding).
- The classic `html { font-size: 62.5% }` trick makes `1rem = 10px`, turning pixel-to-rem conversion into simple division by 10 — still a common pattern worth recognizing in legacy codebases.
- 📉 `100vh` is broken on mobile because browser chrome (URL bar) dynamically shows/hides, so the new small/large/dynamic viewport units — `svh` (UI visible), `lvh` (UI hidden), `dvh` (auto-adjusts) — exist specifically to fix the "mobile viewport is taller than what's actually visible" bug that caused years of mobile layout complaints.
- `clamp(min, preferred, max)` is the standard technique for fluid typography that scales smoothly between a watch and a 4K monitor without a stack of media queries — `min()`/`max()` are its simpler single-bound siblings.
- 🏗️ Mobile-first (write base styles for the smallest screen, layer complexity up via `min-width` media queries) is the industry default for three compounding reasons: mobile devices have less compute budget so simpler-first is cheaper, it forces prioritizing essential content, and the majority of 2026 traffic is mobile — scaling *up* a design is structurally easier than cramming a desktop layout *down*.
- Media Queries (`@media`) test environment (screen width, orientation, `prefers-color-scheme`, `prefers-reduced-motion`) while Feature Queries (`@supports`) test browser *capability* — conflating the two is a common junior mistake. `prefers-color-scheme` paired with CSS custom properties lets a single variable swap drive dark mode without rewriting every component. `prefers-reduced-motion` is an accessibility requirement, not a nice-to-have — heavy parallax/animation can trigger real physical symptoms (dizziness, nausea, in rare cases seizures) for users with vestibular disorders.
- Logical properties (`margin-inline-start` vs. physical `margin-left`) decouple your layout code from a specific reading direction — write once, and it correctly flips for RTL languages like Arabic/Hebrew, which is a hard requirement, not an optimization, for any globally-shipped product.
- Fluid layouts (relative units, smooth resize) vs. Adaptive layouts (fixed units, snap at breakpoints) is a deliberate trade-off, and breakpoints themselves should be chosen by **where content breaks**, not by specific device widths — device-targeted breakpoints guarantee your site looks broken on whatever device ships next year.
- `object-fit: cover` (fills box, crops to maintain aspect ratio) vs. `contain` (shows entire image, may letterbox) governs how `<img>`/`<video>` behave inside a fixed-aspect container — paired with `srcset`/`<picture>` for responsive image delivery.

**Senior Perspective:**
- 🏗️ `dvh`/`svh`/`lvh` existing at all is a tell about how much production pain the `100vh`-on-mobile bug caused industry-wide — recognizing and using them proactively signals you've actually shipped and debugged mobile layouts, not just read about them.
- ⚖️ Container Queries and logical properties both cost a small amount of extra CSS verbosity in exchange for structural correctness (true component reusability, true i18n-readiness) — the trade-off is worth it the moment you're building a design system or shipping to more than one locale, and premature the moment you're prototyping a single internal tool.
- 👥 `prefers-reduced-motion` is a rare CSS feature with direct legal/compliance and user-health stakes — framing it to design stakeholders as "some users experience physical symptoms from this animation" gets faster buy-in than "this is a best practice."

### Rendering, Performance & Animation
- 🏗️ The browser rendering pipeline is the mental model every CSS performance decision maps back to: layout-affecting properties (`width`, `top`, `padding`) force a full recalculation cascade, while `transform` and `opacity` are handled at the **Composite** stage on the GPU — which is why they're the only properties you should animate for consistently smooth 60/120fps.
- `will-change: transform` pre-warns the browser to allocate a dedicated compositor layer — but it's a scarce-resource hint, not a free performance button; overusing it on many elements exhausts GPU memory and can make things slower, not faster.
- The `contain` property (e.g., `contain: layout`) is a performance *promise* to the browser: "nothing inside this box affects anything outside it," which lets the engine scope layout recalculation to just that subtree instead of the whole document — a meaningful win on deep, complex 2026 DOM trees.
- 📉 Critical CSS (inlining above-the-fold styles directly in `<head>`, loading the rest async) removes the render-blocking wait on a full external stylesheet and directly improves First Contentful Paint — a standard technique on any performance-sensitive marketing or landing page.
- CLS (Cumulative Layout Shift, a Core Web Vital) is prevented by reserving space ahead of content arrival: `aspect-ratio` or explicit `width`/`height` on media, and `font-display: swap` to avoid the "flash of invisible text" shift when a custom web font finishes loading.
- Transitions (state A → state B, triggered, two endpoints) vs. `@keyframes` animations (multi-step, can auto-run/loop without a trigger) is a simple but frequently-confused distinction in interviews.
- The View Transitions API gives native, cinematic cross-state or cross-page transitions (snapshot old state, snapshot new state, auto-animate the diff) without hand-rolled FLIP-technique JS. Scroll-driven animations (`animation-timeline: scroll()`) link animation progress directly to scroll position for high-performance progress bars/parallax without a JS scroll listener — which historically was a major source of scroll jank.

```text
Rendering pipeline (what CSS property changes trigger):
Style Recalc → Layout (width/top/padding) → Paint → Composite (transform/opacity, GPU-only)
                      ^-- expensive, cascades           ^-- cheap, isolated
```

**Senior Perspective:**
- ⚖️ Animating `transform`/`opacity` instead of `top`/`left`/`width` isn't a micro-optimization — it's the difference between a Composite-only operation and a full Layout+Paint cascade, and at scale (dashboards, lists, 60fps interaction targets) this single choice determines whether your UI feels "native" or "janky."
- 📉 CLS and font-loading strategy are invisible in local dev on a fast machine and fast connection — they only show up as a Core Web Vitals regression in real-user monitoring, which is why senior teams gate PRs on Lighthouse/CWV budgets rather than trusting "it looked fine when I tested it."
- 🏗️ `contain` and `will-change` are targeted tools for a *known* bottleneck, not blanket-apply defaults — reaching for them without a profiler-identified hot path is premature optimization that adds GPU memory pressure for no measured benefit.

### Architecture, Theming & Ecosystem
- 🏗️ CSS Custom Properties (`--color`) are fundamentally different from Sass variables: Sass variables are compile-time and gone by the time CSS reaches the browser; CSS variables are live in the DOM, follow the Cascade (a child can override a parent's value), and can be read/written from JavaScript (`el.style.setProperty`) — the foundation of any runtime theming system (dark mode, white-labeling, live color pickers) that Sass variables structurally cannot support.
- BEM (`.block__element--modifier`) is a naming discipline that prevents "CSS spaghetti" by making component ownership legible from the class name alone — still relevant in codebases without CSS Modules/CSS-in-JS/Cascade Layers for scoping.
- ⚖️ Utility-first CSS (Tailwind-style) trades HTML readability (long class strings) for extremely fast iteration and tiny final CSS bundles with no "naming things" fatigue; CSS-in-JS (Emotion/Styled-Components) trades JS bundle size and minor runtime cost for perfect encapsulation and prop-driven, logic-based styling. Neither is strictly better — it's a team-velocity vs. bundle-size trade-off that should be made once, deliberately, at the framework level.
- CSS Reset (Eric Meyer-style — zero everything, blank canvas) vs. Normalize.css (fix cross-browser inconsistencies while keeping sensible defaults like bold `<b>`) is a philosophy choice about how much you want to rebuild from scratch versus inherit.
- The 2026 color story has moved past hex/RGB: `oklch()` is perceptually uniform (adjusting lightness doesn't accidentally shift hue, unlike RGB) and unlocks the wider P3 color gamut, with automatic graceful gamut-mapping to sRGB on unsupported screens — no broken colors, just slightly less vibrant ones. Typed OM (`el.attributeStyleMap.set('opacity', 0.5)`) replaces string-parsing CSSOM access with real numeric objects for faster, safer high-performance style manipulation from JS.
- The Popover API (native `popover` attribute, Top Layer rendering, automatic light-dismiss) is the modern default for non-critical floating UI (menus, tooltips) — reach for `<dialog>` only when you specifically need focus-trapping and a background dim for a truly blocking interaction.
- Accessibility testing for CSS specifically means: WCAG AA color contrast (4.5:1 minimum) verified in DevTools, never shipping `outline: none` without a high-visibility `:focus-visible` replacement, testing the layout at 200%/400% browser zoom, and — the most revealing test — disabling CSS entirely to confirm the raw HTML is still readable and logically ordered.

**Senior Perspective:**
- 🏗️ CSS variables being live and cascade-aware (unlike Sass variables) is the architectural reason every serious 2026 theming/dark-mode system is built on them — recommending Sass variables for a theme switcher in a design review is an immediate signal of outdated mental models.
- ⚖️ Utility-first vs. CSS-in-JS is a bundle-size/runtime-cost vs. developer-velocity trade-off that compounds across a codebase — it needs to be decided once at the architecture level with full awareness of the cost, not re-litigated component by component.
- 📉 `outline: none` without a `:focus-visible` replacement is simultaneously a WCAG failure and a support-ticket generator from power users who navigate by keyboard — it's flagged in essentially every senior CSS code review for exactly that reason.

### CSS Fundamentals: Syntax, Selectors & Style Sheet Integration
- CSS reaches a page through exactly three channels, each a real trade-off: **inline** (`style="..."` on an element — highest specificity, zero reusability, a code-review flag outside of JS-computed dynamic values); **embedded** (a `<style>` block in `<head>` — single-document convenience, no cross-document reuse); **external/linked** (`<link rel="stylesheet">`, or `@import` from within another sheet — one cacheable file governs every page referencing it, at the cost of an extra request and render-blocking until it loads). Production apps default to external for the same reason browser caching exists at all: pay the download cost once, reuse it across the whole site.
- A **ruleset** is a selector paired with a declaration block (`selector { property: value; }`); a **declaration block** is the brace-delimited list of `property: value;` pairs. CSS's whole cascade/specificity model (Box Model, Cascade & Specificity) is really just the rule set for which ruleset wins when more than one selector matches the same element.
- Selector vocabulary beyond the specificity tiers already covered: a **class selector** (`.name`) targets every element sharing that class — the reusable, many-to-many case; an **ID selector** (`#name`) targets exactly one element per page by contract, which is why it dominates specificity but scales badly as a general styling mechanism; an **attribute selector** (`[type="submit"]`) matches on any HTML attribute/value pair without needing a class at all; a **contextual/descendant selector** (`nav a`, space-separated) matches the rightmost element only when it has the stated ancestry — the browser's actual right-to-left matching order for these is covered in Box Model, Cascade & Specificity.
- **Pseudo-elements** (`::before`, `::after`, `::first-line`, `::first-letter`) target a sub-part of an element or inject generated content without adding extra markup — `content: ""` plus `::before`/`::after` is the standard mechanism behind decorative icons, custom list markers, and CSS-only tooltips. They're a different mechanism from **pseudo-classes** (`:hover`, `:focus`, `:nth-child()`), which target an element's *state* rather than a sub-part of it — conflating the two is a common junior-level mix-up.
- `@import` must appear before any other rule in a stylesheet (aside from `@charset`) because the cascade resolves in source order — a rule placed after other declarations would need to retroactively override rules the browser already parsed, which the spec disallows outright. That same source-order requirement is why `@import`-heavy sheets are a performance anti-pattern: each `@import` is a render-blocking request the browser can't even discover until it's already downloaded and parsed the parent stylesheet, serializing requests that separate `<link>` tags would fetch in parallel. `@import` is one instance of the broader **at-rule** category — any `@`-prefixed rule (`@media`, `@supports`, `@font-face`, `@keyframes`) that applies to the whole sheet or defines a resource rather than styling a selector.
- Two smaller, easy-to-forget fundamentals: selectors themselves are case-insensitive, but the values they reference often aren't — font-family names and image/font URLs are case-sensitive wherever the underlying filesystem is (Linux servers, most CDNs), so `url(Logo.PNG)` silently 404ing against an actual `logo.png` is a classic "works on Windows, breaks in production" bug. And despite older references claiming CSS has no way to restore a property's default, the modern language explicitly provides `initial` (the property's spec-defined default), `inherit` (force-inherit the parent's value), and `unset`/`revert` (context-sensitive resets) — no re-declaration guesswork required.

**Senior Perspective:**
- ⚖️ Inline styles are specificity-maximal and reusability-zero — the right call only for values a script computes at runtime (a drag-positioned element's `top`/`left`), never for anything a stylesheet could express, since every inline style is an override nothing else in the cascade can cleanly beat without `!important`.
- 🏗️ `@import`'s render-blocking, serialized-request behavior is a concrete, measurable reason to prefer multiple `<link>` tags — or a bundler-time merge — over runtime `@import` chains; it's a rare case where the "old" advice and the "new" build-tooling default point at exactly the same underlying mechanism.

### CSS3 Borders, Color & Image Delivery
- CSS3 introduced `border-radius`, `box-shadow`, and `border-image` as a dedicated Backgrounds & Borders module — the first native way to get rounded corners and soft drop shadows without slicing background images in Photoshop, which is easy to forget was ever the alternative. `box-shadow` takes offset-x/offset-y/blur-radius/spread-radius/color (plus an optional `inset` keyword for an interior shadow) and accepts comma-separated multiple shadows on one element; `border-image` slices a single image into a 9-part grid (corners preserved, edges tiled/stretched) to skin a border with art instead of a flat color. Their rollout is a textbook vendor-prefix story — early support required `-moz-`/`-webkit-`/`-o-` prefixes before browsers converged on the unprefixed property, the same adoption curve nearly every major CSS feature since (Grid, Container Queries, `:has()`) has followed to some degree.
- Color has two equivalent notations from this era: hex (`#ff0000`, six hex digits encoding red/green/blue) and functional `rgb(r, g, b)` (0–255 per channel, or percentages) — purely a syntax preference at this level, though the 2026 color story has moved well past both (`oklch()`, covered in Architecture, Theming & Ecosystem) for perceptually-uniform color manipulation.
- **Image sprites** — combining many small images into one file and positioning it with `background-position` offsets — were the standard pre-HTTP/2 technique for cutting a page's request count, since every individual image was a separate round trip under HTTP/1.1's connection-per-request limits. HTTP/2 multiplexing removed most of the *performance* justification for sprites, but the technique still shows up for icon systems where bundling genuinely simplifies asset management independent of request count. Legacy CSS also defined `media` attribute types beyond screen — `print`, `aural` (speech synthesizers), `handheld`, `projection` — that predate the modern `@media` feature-query model (Responsive Design, Units & Typography); most have been formally dropped from the spec except `print`, `screen`, and `speech` (aural's successor).

**Senior Perspective:**
- 📉 Image sprites are a preserved-in-amber example of optimizing for yesterday's transport protocol — recognizing that HTTP/2 and HTTP/3 multiplexing removed the original justification, while still knowing why the technique existed, is what separates "I copy what's in the codebase" from "I know when to retire a pattern."
- 🏗️ The border-radius/box-shadow vendor-prefix era is worth remembering not for the syntax but for the lesson it taught the ecosystem — it's the direct ancestor of Autoprefixer, Can I Use, and the modern default of shipping unprefixed and letting a build step handle compatibility instead of hand-writing three duplicate declarations.

### Float, Position & Legacy Layout Fundamentals
- `float` was CSS's original (pre-Flexbox/Grid) tool for pulling an element to one side and letting inline content wrap around it — genuinely still correct for its one surviving use case (wrapping text around an image) but for decades misused as a full page-layout system, which is exactly the float-based-layout migration scenario this pillar's Predictive Interview Questions references. A classic legacy quirk worth recognizing on sight: combining `width: 100%` with `float` under old (IE-era) box-model implementations could add a phantom pixel via the border calculation, silently breaking pixel-perfect layouts — one of many float rendering inconsistencies that made Flexbox/Grid (Layout Systems: Flexbox & Grid) an unambiguous upgrade rather than just a stylistic preference.
- `z-index` at the fundamental level: any positioned element (any `position` other than `static`) can take an integer `z-index` — higher values render on top, negative values are valid, and the default (`auto`, effectively 0) is what every element starts at. The advanced failure mode — stacking-context wars and the centralized-token fix — is covered in Box Model, Cascade & Specificity; the fundamental gotcha worth knowing here is that `z-index` does **nothing** on a `position: static` element, a frequent silent "why isn't this working" debugging trap.
- The foundational `position` values each imply a different containing-block model: `static` (default, normal document flow, ignores `top`/`left`/`z-index` entirely), `relative` (flow position preserved, but now a positioning anchor for `top`/`left` and a new containing block for absolutely-positioned descendants), `absolute` (removed from flow entirely, positioned against the nearest non-static ancestor), `fixed` (positioned against the viewport, ignores scrolling), and `inherit` (takes the parent's computed value). `position: sticky` — a scroll-dependent hybrid of relative and fixed — was standardized after this generation of the spec and is the value most answers from this era miss entirely.
- **Graceful degradation** designs top-down: build for the newest/most capable browser first, then provide a reduced-but-functional fallback for anything that can't keep up (`alt` text standing in when an image fails to load is the canonical example). **Progressive enhancement** inverts the direction: build a working baseline first — content and core functionality accessible to every browser — then layer richer behavior on top for browsers capable of it. Both target the same "not everyone has the latest browser" reality; they differ only in which end of the capability spectrum is the default you design from.

**Senior Perspective:**
- ⚖️ Graceful degradation and progressive enhancement produce similar end states but reflect opposite priorities — degradation treats the enhanced experience as the default and accessibility as the fallback, enhancement treats a working baseline as non-negotiable and richness as the bonus; most 2026 teams default to progressive enhancement because it fails safer.
- 📉 "Why isn't my `z-index` working" almost always traces back to a missing `position` declaration or a parent stacking context clipping the child — one of the highest-frequency CSS debugging tickets precisely because the failure is silent, never an error.
- 🏗️ Float-based layout isn't wrong knowledge to have — understanding its wrapping behavior and failure modes is exactly what lets you explain *to a non-expert* why a Grid/Flexbox migration is worth the engineering time, rather than just asserting "float is old."

### CSS3 Modularization, Animation & Text Wrapping
- Pre-CSS3, the entire language shipped as one monolithic spec; CSS3 split it into independent modules — Selectors, Box Model, Backgrounds & Borders, Text Effects, 2D/3D Transformations, Animations, Multiple Column Layout, User Interface, and more added since — that could each evolve and gain browser support on its own timeline. This is the direct explanation for why CSS feature support has always been so uneven across browsers: a browser could ship Selectors Level 3 in full while still lagging on Animations, something impossible under the old single-spec model.
- `@keyframes` animations bind to a selector through exactly two required properties — `animation-name` (which `@keyframes` block to run) and `animation-duration` (how long one cycle takes) — everything else (`iteration-count`, `direction`, `timing-function`) is optional refinement on top of that minimal contract. Their advantage over hand-rolled JavaScript animation isn't just less code to write: a declarative CSS animation is the browser's own job to optimize, letting the engine run it on the compositor thread independent of a potentially-busy main thread — the mechanism-level reason is covered in Rendering, Performance & Animation.
- `word-wrap` (standardized today as `overflow-wrap`) forces an otherwise-unbreakable string — a long URL, a hyphen-free identifier — to break mid-word rather than overflow its container. Its sibling `white-space` controls a different axis entirely — collapsing and line-wrapping of literal whitespace/newlines in the source: `normal` collapses whitespace and wraps normally, `nowrap` collapses whitespace but never wraps, `pre` preserves whitespace exactly and never wraps (the historical `<pre>` behavior), `pre-wrap` preserves whitespace but still wraps, `pre-line` collapses spaces/tabs but preserves explicit line breaks. Confusing the two is a common source of "why is this long string still overflowing" bugs: `white-space: nowrap` alone won't break a long word, and `word-wrap`/`overflow-wrap` alone won't stop ordinary text from wrapping.
- Flexbox (`display: flex`/`inline-flex`, flex containers plus flex items) shipped as one of these CSS3-era modules and is covered in full architectural depth in Layout Systems: Flexbox & Grid — worth noting here only as *which generation it belongs to*, since "is Flexbox part of CSS3" is a genuine trivia-adjacent interview question.
- Naming CSS's pre-modular limitations is itself a useful interview answer: no way to select an ancestor based on a descendant (no parent selector), no arithmetic in values, no way to target a specific run of text independent of markup, and pseudo-classes that couldn't respond to dynamic/scripted state. Nearly every one of these has since been solved — `:has()` is the parent selector, `calc()` is the expression engine, `:is()`/`:where()`/Cascade Layers are the specificity-control layer, all covered in Box Model, Cascade & Specificity — which makes naming the old gap *and* the modern fix a compact way to show you've tracked the language's evolution rather than learned it once and stopped.

**Senior Perspective:**
- 🏗️ CSS3's split into independent modules is the underlying reason "does this browser support CSS3" was never a meaningful question — the accurate senior answer is always "support for *which* module," and naming the module is what separates a real answer from a guess.
- ⚖️ CSS animations winning on performance over JS-driven animation isn't automatic — it's contingent on animating compositor-only properties (`transform`/`opacity`); a `@keyframes` block animating `width` or `top` gets none of that benefit and triggers the same expensive Layout recalculation a JS-driven version would.
- 👥 Being able to name CSS's historical gaps and then immediately name the modern feature that closed each one is a compact way to demonstrate you've tracked the language's evolution rather than memorized a snapshot of it.

**Predictive Interview Questions (CSS):**
1. You inherit a codebase using float-based layouts and no CSS architecture strategy for specificity control. Walk me through your migration plan to Grid/Flexbox and Cascade Layers without a "big bang" rewrite that risks visual regressions.
2. When would you reach for Container Queries over Media Queries, and what does that decision cost you in browser support, mental model complexity, and component API design?
3. Describe a situation where a CSS performance issue (jank, CLS, slow paint) was invisible in your local dev environment but showed up in production real-user monitoring. How did you diagnose it, and how did you prevent the same class of bug from recurring across the team?

**Executive Summary Cheat Sheet (CSS):** Senior CSS is about knowing which properties are cheap (Composite: `transform`/`opacity`) versus expensive (Layout: nearly everything else) and architecting specificity, theming, and responsiveness (Cascade Layers, CSS variables, Container Queries) so they scale across a team instead of accumulating into `!important` wars. Every modern CSS feature — `:has()`, `@scope`, native nesting, `clamp()`, logical properties — exists to solve a specific, historically painful production problem, and naming that problem is what separates "I know the syntax" from "I know why it exists."

## JavaScript

### V8 Engine & Execution Model
- 🏗️ JS source doesn't go straight from text to execution — V8 runs it through a specific pipeline worth naming precisely in an interview: the **Parser** tokenizes source into an AST, **Ignition** (a bytecode interpreter) runs a fast baseline pass immediately with no compile-wait, and **TurboFan** (the JIT compiler) profiles which functions run "hot" and recompiles just those into optimized machine code — "JS is interpreted" is technically incomplete; it's interpreted *first*, then selectively JIT-compiled.
- "Single-threaded" is a precise claim about the **Call Stack** specifically (exactly one frame executes at a time, LIFO — last pushed, first popped), not about the whole runtime: the browser/Node environment around V8 is multi-threaded (timers, network, file I/O run on separate threads via Web APIs/libuv), which is exactly why JS can be non-blocking without being multi-threaded — conflating the two is the most common way this question gets answered imprecisely.
- An Execution Context is created for every function invocation (plus exactly one Global Execution Context at startup), each carrying its own Variable Environment, Lexical Environment, and `this` binding — a "Maximum call stack size exceeded" error is literally this mechanism overflowing, contexts getting pushed by uncontrolled recursion faster than they're popped.
- Worth pre-empting a few junior-level myths directly, since interviewers sometimes probe exactly these: JS is not multi-threaded (concurrency comes from the Event Loop + Web APIs, not multiple threads executing JS itself); JS is not frontend-only (Node/Deno/Bun, React Native, Electron, and most AI-agent tooling run JS server-side or cross-platform); `setTimeout(fn, 0)` does not run "immediately" — it queues a macrotask that waits for the current call stack *and* the entire microtask queue to drain first.

- 🏗️ **Where it came from, and what "JavaScript" names today** (the usual warm-up question): Brendan Eich created it at Netscape in 1995, reportedly in about 10 days. It shipped as Mocha, was renamed LiveScript, then JavaScript (a marketing name with no technical link to Java). The language is standardised as **ECMAScript** (ECMA-262, evolved by the TC39 committee): ES5 (2009) → ES6/ES2015 (the big rewrite) → one edition a year since then (ES2016 … ES2025). Its defining traits are **dynamic typing** (types belong to values and are checked at runtime), **first-class functions** (functions are values you can store, pass and return), and an **event-driven, asynchronous** model built on the event loop. In the web trio, HTML is structure, CSS is presentation and JS is behaviour. Outside web pages it runs mobile apps (React Native), backends (Node.js), desktop apps (Electron), browser extensions, games, data visualisation, in-browser ML (TensorFlow.js), IoT and automation or test scripting.
- *Source note:* the Complete Notes call JS "a lightweight, **interpreted** language — no compilation step", and both decks' "What is JavaScript?" answers repeat "interpreted". That was true in 1995. Every modern engine (V8 in Chrome/Node/Deno, SpiderMonkey in Firefox, JavaScriptCore in Safari/Bun) parses to bytecode and JIT-compiles hot code, as the pipeline below shows. The accurate interview answer is "interpreted first, then selectively JIT-compiled."
- **Browser vs Node.js**: same language, and in Chrome and Node the same V8 engine, but a different host environment:
```text
                Browser (client-side)                     Node.js (server-side)
Runs where      inside a browser tab                      outside the browser: server, CLI, build tools
Host APIs       DOM + BOM (document, window, location)    no DOM/BOM by default; fs, http, process, Buffer
Threading       one JS thread + event loop                one JS thread + event loop (libuv pool for I/O)
Security        sandboxed, no raw file-system access      full system access (files, network, env, processes)
Typical use     UI, interactivity, client rendering       APIs, backends, databases, CLIs, tooling
Global object   window (also globalThis)                  global (also globalThis)
```
- The Complete Notes draw the browser "execution flow" as JS code → engine → Call Stack → Web APIs (long-running work) → Callback Queue → Event Loop → back onto the Call Stack once it's empty. That's the right shape for a first answer. *Source note:* the diagram has only one queue. Promise callbacks go to a separate **microtask queue** that drains completely before any timer or event callback runs, and that difference decides most output-ordering questions (see The Event Loop & Asynchronous JavaScript below).
- Practice tip from the notes: open DevTools (F12 or Ctrl+Shift+I), go to the Console tab, and experiment there. Each line is evaluated live against the current page.

```text
V8 pipeline:
Source → Parser (AST) → Ignition (bytecode interpreter, runs immediately)
                              │
                              ├─ profiles "hot" functions at runtime
                              ▼
                         TurboFan (JIT) → optimized machine code
```

**Senior Perspective:**
- 🏗️ Naming Ignition and TurboFan specifically — rather than "V8 compiles it" — is the difference between a surface-level answer and one that connects cleanly to the JIT deoptimization discussion under Performance, Memory & Engine Internals below: the same hot-path-profiling strategy explains both how V8 gets fast and why it can suddenly get slow again.
- ⚖️ Every later async question (Event Loop, microtasks vs. macrotasks) implicitly assumes this single-Call-Stack model — it's worth establishing explicitly rather than letting an interviewer infer whether you actually understand it or are pattern-matching on the word "asynchronous."

### Types, Coercion & Equality
- The 7 primitives (`String`, `Number`, `BigInt`, `Boolean`, `Undefined`, `Null`, `Symbol`) are immutable and stored by value; objects are stored by reference — which is the entire reason "pass by value" (primitives: function gets a copy, caller's variable is untouched) vs. "pass by reference" (objects/arrays: function gets a pointer, mutating a property inside the function mutates the caller's object) behaves differently, and it's a near-universal senior JS interview question.
- `null` (programmer explicitly says "this is empty") vs. `undefined` (system default for "not assigned yet") is a semantic distinction, not just two flavors of nothing — `typeof null === "object"` is a famous 1995-era engine bug (NULL pointer's type tag misread as an object tag) kept forever for backward compatibility.
- `==` performs type coercion before comparing (`5 == "5"` is true); `===` requires matching type and value with no coercion — the senior default is always `===`, reserving `==` only for the rare, intentional `x == null` idiom that checks both `null` and `undefined` at once.
- `NaN` is the only JS value not equal to itself (`NaN === NaN` is `false`); `Number.isNaN()` is the only reliable check — the global `isNaN()` coerces its argument first and returns false positives for any non-numeric value.
- The 6 falsy values are exhaustive and worth memorizing cold: `false`, `0` (incl. `-0`/`0n`), `""`, `null`, `undefined`, `NaN`. Everything else — including `[]` and `{}` — is truthy, which surprises engineers coming from other languages.
- Counts of "the falsy values" vary between sources (6, 7, 8) only because of how `-0`, `0n`, and one oddity get tallied. The oddity is `document.all`, a legacy browser object that is deliberately falsy for old-IE feature detection, and it's the only falsy *object* in the language. The truthy traps that actually cause bugs are strings: `'0'`, `'false'`, and `' '` (a single space) are all truthy, so a form value of `'0'` passes an `if (value)` check.
- `0.1 + 0.2 !== 0.3` isn't a JS bug — it's IEEE 754 binary floating-point representing certain decimal fractions as repeating binary fractions, identical to how `1/3` can't be represented exactly in decimal. This is a language-agnostic floating-point fact JS just happens to expose directly.
- `Symbol` creates guaranteed-unique property keys (used internally for well-known behaviors like `Symbol.iterator`) to avoid property-name collisions between independent code. `BigInt` (append `n`) represents integers beyond `2^53 - 1` safely, but cannot be mixed with `Number` in arithmetic without explicit conversion.
- Implicit coercion follows memorizable patterns rather than acting randomly: `+` falls back to string concatenation the moment *either* operand is a string (`'5' + 1` → `'51'`), while `-`/`*`/`/` always coerce toward numbers since there's no meaningful "string subtraction" (`'5' - 1` → `4`); `null` coerces to `0` in numeric context (`null + 1` → `1`) while `undefined` coerces to `NaN` (`undefined + 1` → `NaN`) — a frequent trap when defaulting a possibly-missing numeric field with `+` instead of `??`.
- `typeof` is reliable for most primitives but has two specific blind spots worth naming precisely: the legacy `typeof null === 'object'` bug above, and the fact that it cannot distinguish an array from a plain object (`typeof [] === 'object'`, identical to `typeof {}`) — `Array.isArray()` is the correct check, not `typeof`.

- The full type map with what `typeof` returns for each. `function` is the only kind of object that `typeof` singles out, and every other built-in object type (Array, Date, RegExp, Map, Set …) is a reference type that reports `"object"`:
```text
Type        Example              typeof        Note
String      "Hello"              "string"      text; immutable
Number      42, 3.14, NaN        "number"      64-bit float; integers exact only up to 2^53 - 1
BigInt      9007199254740993n    "bigint"      arbitrary-size integers (append n)
Boolean     true, false          "boolean"
Undefined   undefined            "undefined"   declared but not assigned
Null        null                 "object"      legacy bug; null is still a primitive
Symbol      Symbol("id")         "symbol"      unique, immutable property key
Object      { name: "John" }     "object"      reference type
Array       [1, 2, 3]            "object"      check with Array.isArray()
Function    function () {}       "function"    callable object
Date / RegExp / Map / Set …      "object"      reference types
```
```js
let big = 9007199254740991n;              // Number.MAX_SAFE_INTEGER as a BigInt
typeof big;                               // 'bigint'
9007199254740992 === 9007199254740993;    // true  — Number has run out of precision
9007199254740992n === 9007199254740993n;  // false — BigInt stays exact
1n + 1;                                   // TypeError: Cannot mix BigInt and other types

const id = Symbol('id'), id2 = Symbol('id');
id === id2;                               // false — every Symbol() is unique
Symbol.for('id') === Symbol.for('id');    // true  — the global registry is the exception
```
- *Source note:* the Top-20 deck's null/undefined key point says "undefined is a type. null is an object." Only half of that is right. Both `undefined` and `null` are primitive values, each the only value of its own type (Undefined and Null). `typeof null === "object"` is the legacy bug described above, not evidence that null is an object.
- *Source note:* the notes say reference types are "copied by reference". More precisely, JS always passes **by value**, and for objects the value being copied is a reference. This is often called *pass-by-sharing*. Mutating the object through the parameter is visible to the caller, but reassigning the parameter is not:
```js
function mutate(o)   { o.v = 2; }        // changes the shared object → caller sees it
function reassign(o) { o = { v: 3 }; }   // rebinds only the local copy of the reference
const obj = { v: 1 };
mutate(obj);    // obj.v === 2
reassign(obj);  // obj.v is still 2
```
- **Operators** (from the notes' reference page, every result checked in Node):
```text
Arithmetic   +  -  *  /  %  **         5+3→8  5-3→2  5*3→15  10/2→5  10%3→1  2**3→8
             ++  --                    change a variable by 1 (prefix vs postfix below)
Comparison   ==  !=   (coercing)       5 == "5" → true      5 != 3 → true
             === !==  (strict)         5 === "5" → false    5 !== "5" → true
             >  <  >=  <=              5 > 3 → true   5 < 3 → false   5 >= 5 → true   4 <= 5 → true
Logical      &&  ||  !                 true && false → false   true || false → true   !true → false
             short-circuit: && stops at the first falsy operand, || at the first truthy one
Assignment   =  +=  -=  *=  /=  %=  **=   x += 5 means x = x + 5 … x **= 2 means x = x ** 2
Ternary      cond ? a : b              (age >= 18) ? "Adult" : "Minor"  → "Adult" when age = 18
```
- *Source note:* the notes' operator table gives `a++` as "a + 1". The side effect is right, but the expression's **value** depends on position, and interviewers do test this:
```js
let a = 5;
const post = a++;   // post === 5, a === 6 — postfix returns the OLD value
let b = 5;
const pre = ++b;    // pre === 6,  b === 6 — prefix returns the NEW value
-7 % 3;             // -1 — % is a remainder that keeps the dividend's sign, not a true modulo
```
- **Explicit vs implicit conversion**, using the notes' examples plus the cases that usually trip people:
```js
// explicit — you convert on purpose
Number('123');   // 123        String(456);    // '456'
Boolean(0);      // false      Boolean(100);   // true
Number(true);    // 1          String(false);  // 'false'
Number('12px');  // NaN — Number() needs the whole string to be numeric
parseInt('12px', 10);   // 12 — parseInt/parseFloat read a leading number and stop (always pass the radix)
Number('');      // 0     Number(null);  // 0     Number(undefined);  // NaN
+'42';           // 42    (unary + is Number())     !!'hi';  // true  (!! is Boolean())

// implicit — the engine converts for you (coercion)
5 + '5';            // '55'   number + string → string concatenation
'5' - 2;            // 3      string → number
true + 1;           // 2      true → 1
false == 0;         // true   false → 0
null == undefined;  // true   special-cased by ==
1 + 2 + '3';        // '33'   evaluated left to right: 3 + '3'
'1' + 2 + 3;        // '123'
```
- *Source note:* both decks reduce the difference to "`==` compares values only, `===` compares value and type". That isn't what `==` does. `==` runs the Abstract Equality algorithm. When both operands have the same type it behaves exactly like `===`. Otherwise it converts by fixed rules: `null` and `undefined` equal only each other, strings and booleans become numbers, and objects are converted to primitives. So objects are still compared by reference, `null == 0` is `false` even though `null` becomes `0` in arithmetic, and `NaN == NaN` is `false`. A precise one-liner is "`===` compares without coercion; `==` coerces the operands by a fixed set of rules, then compares."
```js
[] == [];     // false — two different references
null == 0;    // false — null is only == to undefined
'' == 0;      // true    '0' == false;  // true    [] == false;  // true
NaN == NaN;   // false
```
- Truthy values worth listing next to the falsy ones: `true`, any non-zero number (including `-1`, `Infinity` and `-Infinity`), any non-empty string (including `"0"` and `"false"`), `[]`, `{}`, and every function. The two decks count the falsy set differently. The Complete Notes list 8 (`false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`) and the Top-20 bonus slide lists 6 (without `-0`/`0n`). Both are correct under the counting explained above; in any condition, falsy acts as `false` and everything else acts as `true`.

```text
Value semantics:
Primitive  → stored by VALUE   → function param is a copy      → caller untouched
Object/Arr → stored by REFERENCE → function param is a pointer → caller's object IS mutated
```

**Senior Perspective:**
- ⚖️ Defaulting to `===` everywhere trades the rare convenience of `==`'s coercion for eliminating an entire class of "silent wrong comparison" bugs — the convenience almost never outweighs the risk in production code.
- 📉 Pass-by-value vs. pass-by-reference confusion is the root cause of a huge share of "why did this state mutate unexpectedly" bugs in state-management code — understanding it precisely is what separates "my Redux reducer randomly breaks" from reliable immutable-update patterns.

### Control Flow & Loops
- Control-flow statements let a program make decisions and repeat work. They're rarely a senior question on their own, but they come up in live coding, and a few precise semantics (strict matching in `switch`, `for...in` vs `for...of`, what `continue` can target) separate careful answers from careless ones.
- **Branching.** Use `if / else if / else` for ranges and compound conditions (they're checked top to bottom, and the first match wins). Use the ternary for a single expression that produces a value. `switch` compares with **strict equality (`===`)**. Without `break`, execution **falls through** into the next `case`. `default` handles anything unmatched.
```js
let age = 18;
if (age >= 18) { console.log('Adult'); } else { console.log('Minor'); }        // Adult

let score = 75;
if (score >= 90) console.log('A');
else if (score >= 75) console.log('B');                                        // B
else console.log('C');

let day = 2;
switch (day) {
  case 1: console.log('Mon'); break;
  case 2: console.log('Tue'); break;                                           // Tue
  case 3: console.log('Wed'); break;
  default: console.log('Invalid');
}
switch ('2') { case 2: console.log('number'); break; default: console.log('no match'); }  // no match — === , no coercion
switch (1) { case 1: console.log('one'); case 2: console.log('two'); break; }             // one, two — fall-through
```
- **Loops.** Use `for` when you know the count, `while` when the condition is checked **before** each pass, and `do...while` when the body should run **at least once** because the condition is checked after it. Use `for...of` for the **values** of any iterable (Array, String, Map, Set, generators) and `for...in` for the **keys** of an object:
```js
for (let i = 1; i <= 5; i++) console.log(i);            // 1 2 3 4 5
let i = 1; while (i <= 5) { console.log(i); i++; }      // 1 2 3 4 5
let j = 1; do { console.log(j); j++; } while (j <= 5);  // 1 2 3 4 5
let k = 10; do { console.log(k); } while (k < 5);       // 10 — body ran once though the condition was false

for (const val of [10, 20, 30]) console.log(val);       // 10 20 30
const user = { name: 'John', age: 25 };
for (const key in user) console.log(key + ': ' + user[key]);   // name: John   age: 25

for (let n = 1; n <= 10; n++) { if (n === 5) break; console.log(n); }     // 1 2 3 4 — break exits the loop
for (let n = 1; n <= 5; n++) { if (n === 3) continue; console.log(n); }   // 1 2 4 5 — continue skips one pass
```
- 📉 `for...in` is the wrong tool for arrays. It yields **string** keys (`'0'`, `'1'` …), and includes inherited enumerable properties (for example, anything a library added to `Array.prototype`). Use `for...of`, a plain `for`, or an array method instead. The reverse mistake, `for...of` over a plain object, throws `TypeError: ... is not iterable`. Use `Object.keys/values/entries(obj)` to get something iterable.
- *Source note:* the notes' reminder says "break & continue work in loops and switch". `break` works in both, but `continue` only targets **loops**. A `continue` inside a `switch` that isn't inside a loop is a `SyntaxError`, and inside a loop it skips to the loop's next iteration rather than doing anything to the `switch`. To leave an outer loop from an inner one, use a label (`outer: for (...) { for (...) { break outer; } }`).
- A rule of thumb from the notes, extended: plain `for` for counts or index access, `for...of` for values, `for...in` only for plain-object keys, and array methods (`map`/`filter`/`reduce`) when you're transforming data rather than running side effects. Remember that `break`/`continue` can't be used inside `forEach`, and `forEach` never awaits an async callback (see the async pitfalls below).

**Senior Perspective:**
- ⚖️ Choosing between `for...of` and an array method is a readability call, not a performance one, in almost all real code. The meaningful differences are that `for...of` supports `break`, `continue` and a sequential `await`, while `map`/`filter` return new arrays and chain declaratively.
- 📉 A `switch` over a value read from user input or JSON silently misses when types differ (`'2'` vs `2`) because it compares with `===`. Normalising the type before the `switch`, or using an object/Map lookup table, prevents that bug and usually reads better once there are more than a few cases.

### Scope, Closures & Execution Context
- 🏗️ `var` (function-scoped, hoisted and initialized to `undefined`) vs. `let`/`const` (block-scoped, hoisted but left in the **Temporal Dead Zone** — accessing before declaration throws a `ReferenceError`, not a silent `undefined`) is the foundational scoping model every later async/closure question builds on.
```text
         Scope      Re-declare   Re-assign   Hoisting                     Use
var      function   yes          yes         hoisted, init'd undefined    legacy only — avoid
let      block      no           yes         hoisted, TDZ until the line  values that change
const    block      no           no*         hoisted, TDZ until the line  default choice
* const blocks re-binding the variable, not mutating the object it points to
```
- A closure is an inner function retaining access to its outer function's variables even after the outer function has returned — the mechanism behind private state (a counter with no external way to set `count = 500` directly) and, if misused, a common source of memory leaks: a closure referencing a large dataset or a DOM node keeps that entire scope alive as long as the closure itself is reachable.
- The classic `var` vs `let` `setTimeout`-in-a-loop interview question isn't really about timers — it's about scope: `var i` is one shared function-scoped binding all callbacks close over (all print the final value), while `let i` creates a fresh block-scoped binding *per iteration*, so each closure captures its own snapshot.
```js
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 1000);  // 3 3 3 (one shared i)
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i), 1000);  // 0 1 2 (new i per iteration)
```
- Hoisting differs by *declaration form*, which is the detail interviewers use to go past "hoisting moves things to the top": a **function declaration** (`function add(a, b) {}`) is hoisted with its entire body, so it can be called before the line it's written on; a **function expression** or **arrow function** assigned to a variable (`const add = (a, b) => a + b`) follows its variable's rules instead — `var` gives `TypeError: add is not a function` (it's `undefined`), `let`/`const` give a TDZ `ReferenceError`. Likewise `console.log(x); var x = 5;` logs `undefined`, while the same with `let` throws.
```js
sayHi();                      // ✅ works — declaration hoisted with its body
function sayHi() { console.log('hi'); }

greet();                      // ❌ ReferenceError (TDZ) — only the const binding is hoisted
const greet = () => console.log('hello');
```
- The closure-as-private-state pattern in its most-asked form: nothing outside can touch `balance` except through the returned methods, which is how encapsulation worked before `#private` fields and is still the shape of every custom hook and module factory:
```js
function bankAccount(balance) {
  return {
    getBalance: () => balance,
    deposit: (amount) => { balance += amount; },
  };
}
const account = bankAccount(1000);
account.deposit(500);
account.getBalance();   // 1500 — `balance` itself is unreachable from outside
```
- Execution context has two phases: Creation (hoisting, scope chain setup, `this` binding — no code has run yet) and Execution (line-by-line, values assigned, functions actually invoked). The Scope Chain resolves a variable lookup by walking outward from local scope to global, throwing a `ReferenceError` only once it exhausts every enclosing scope.
- 📉 "Shadowing" (an inner-scope variable reusing an outer scope's name) silently hides the outer variable for the block's duration — a readability hazard flagged by most linters for good reason.
- `this` inside a closure does **not** inherit the closure's lexical rules unless the closure is an arrow function — a plain nested function's `this` is redetermined by *how it's called*, which is the root cause of the classic `const self = this` workaround pattern that arrow functions made largely obsolete.
- IIFEs (`(function(){...})()`) were the pre-ES6-module technique for creating a private scope to avoid polluting globals — still worth recognizing in legacy code even though native modules have superseded the pattern. Memoization (caching expensive function results in a closure-private object) is a textbook practical application of closures that shows up constantly in real perf work.

- The notes' block-scope demo is the fastest way to show the `var`/`let` difference. It's also where the exact `const` error message comes from:
```js
function testVar() { var a = 10; if (true) { var a = 20; } console.log(a); }   // 20 — same function-scoped a
function testLet() { let b = 10; if (true) { let b = 20; } console.log(b); }   // 10 — the inner b is a separate block binding
const z = 30;
z = 40;   // TypeError: Assignment to constant variable.
```
- *Source note (hoisting):* the Complete Notes, their interview page, and Top-20 Q3 all define hoisting as JS "**moving** declarations to the top of their scope", and the notes label `let`/`const` "**Not hoisted**". Neither is accurate. No code moves. During the **creation phase** the engine registers every declaration in the scope's environment before line 1 runs. `var` bindings are initialised to `undefined`, function declarations are stored with their full body, and `let`/`const`/`class` bindings are created but left **uninitialised**, which is the Temporal Dead Zone. So `let`/`const` *are* hoisted; they just can't be read before their line. The notes' own "Rule" box (let/const stay in the TDZ until the line runs) contradicts their "not hoisted" heading. Top-20's key point, "only declarations are hoisted, not initializations", is the part to keep.
```js
console.log(a);   // undefined — the binding exists and was initialised to undefined
var a = 10;
console.log(a);   // 10

console.log(b);   // ReferenceError: Cannot access 'b' before initialization
let b = 20;       // (execution stops at the line above, so a following console.log(b) never runs)

// Proof that let IS hoisted: the inner v shadows the outer one from the top of its block
let v = 'outer';
{
  console.log(v); // ReferenceError, not 'outer' — the block's own v already exists, in its TDZ
  let v = 'inner';
}
```
- The two `ReferenceError` messages come from different situations. A TDZ access says "Cannot access 'b' before initialization", meaning the binding exists but hasn't been initialised. A name declared nowhere says "b is not defined". `typeof neverDeclared` safely returns `'undefined'`, while `typeof` on a TDZ binding still throws.
- **Lexical scope** means scope is fixed by where a function is *written*, not where it's *called*. That's the notes' "Key Point", and it's the counterpart to `this`, which depends on the call site:
```js
function outer() {
  let outerVar = 'I am outer';
  function inner() { console.log(outerVar); }  // inner can read its enclosing scope
  inner();
}
outer();                                        // I am outer

const lx = 'global';
function show() { return lx; }
function caller() { const lx = 'caller'; return show(); }
caller();                                       // 'global' — show() resolves lx where it was DEFINED
```
- The notes' **scope chain** is function scope → outer function scope → global scope → global object (`window`). One detail interviewers probe: in a classic browser script, a top-level `var` or function declaration becomes a property of `window`, but top-level `let`/`const`/`class` don't (they live in a separate global declarative record). ES modules add nothing to `window` at all. An assignment to an undeclared name in sloppy mode silently creates a `window` property (the accidental-global leak above); strict mode makes it a `ReferenceError`.
- The notes' canonical closure, with the three reasons they give for using closures (data privacy, function factories, state that persists between calls). Each call to the outer function creates an independent enclosed variable:
```js
function counter() {
  let count = 0;
  return function () { count++; console.log(count); };
}
const inc = counter();
inc(); inc(); inc();                  // 1 2 3 — every call sees the same enclosed count
const other = counter(); other();     // 1 — a new call to counter() creates a new count

const makeMultiplier = (n) => (x) => x * n;   // function factory: each result closes over its own n
makeMultiplier(3)(5);                         // 15
```

```text
Execution Context lifecycle:
Creation Phase: hoist declarations, build scope chain, bind `this`  (no code runs)
      ↓
Execution Phase: run line-by-line, assign real values, invoke functions
```

**Senior Perspective:**
- 🏗️ Closures aren't a JS trivia topic — they're the mechanism underneath React hooks (stale closure bugs), module-pattern encapsulation, memoization, and event-handler state, so a shaky mental model here cascades into bugs across the entire stack.
- 📉 A closure holding a reference to a large object or a detached DOM node is one of the few JS memory leaks that's genuinely hard to spot in code review — it only surfaces as a slow memory-growth "sawtooth" in a heap profiler, which is why senior engineers proactively null out long-lived closure references rather than trusting GC to figure it out.

### Functions, `this` & Functional Patterns
- Arrow functions have no own `this`/`arguments`/`prototype` — `this` is lexically inherited from the enclosing scope at definition time, which is why they can't be used as constructors (`new` requires a `[[Construct]]` internal method and a `prototype` they don't have) but are ideal for callbacks/timers inside class methods where you want the surrounding object's `this` without `.bind()`.
- `this` resolution follows four explicit rules in priority order: **New** binding (constructor call → new instance), **Explicit** binding (`.call()`/`.apply()`/`.bind()` → whatever you pass), **Implicit** binding (method call → the object before the dot), **Default** binding (standalone call → global object, or `undefined` in strict mode). Passing `null`/`undefined` to `.call()`/`.apply()` falls back to the global object in sloppy mode but stays `null`/`undefined` in strict mode.
- `call()`/`apply()` execute immediately (args individually vs. as an array); `bind()` returns a new function with `this` **permanently** locked — the standard fix for "losing `this`" when passing a class method as a callback/event handler ("hard binding").
```js
const obj  = { value: 100, get() { return this.value; } };
const obj2 = { value: 100, get: () => this.value };
obj.get();    // 100       — regular method, `this` = obj (implicit binding)
obj2.get();   // undefined — arrow captured the *enclosing* `this`, not obj2

function greet(city) { return `${this.name} from ${city}`; }
greet.call({ name: 'Abhi' }, 'Pune');       // args listed individually, runs now
greet.apply({ name: 'Abhi' }, ['Pune']);    // args as an array, runs now
const g = greet.bind({ name: 'Abhi' }, 'Pune');
g();                                        // runs later, `this` permanently locked
```
- Two more `this` contexts round out the table interviewers usually draw: in a DOM handler assigned as a regular function (`btn.onclick = function () {}` or `addEventListener` with a non-arrow callback), `this` is the element the listener is attached to (same as `e.currentTarget`); at the top level of a script, `this` is `window` in a classic browser script but `undefined` at module top level and `{}` (`module.exports`) at the top of a CommonJS file in Node. The rule of thumb is that `this` depends on the **call site**, not on where the function is written, except for arrows, which ignore the call site entirely. That's why arrows are the default for `map`/`filter`/`setTimeout` callbacks and a bug for object methods.
- A pure function always returns the same output for the same input and produces no side effects (no mutating arguments, no touching globals, no I/O) — side effects are necessary for a program to *do* anything, but isolating them makes the remaining logic trivially testable.
- Higher-order functions (take and/or return functions — `.map()`/`.filter()`/`.reduce()`) treat functions as first-class data, enabling function composition (`f(g(x))`, piping data through small single-purpose functions), currying (`f(a)(b)(c)` instead of `f(a,b,c)`, enabling specialized partial-application variants), and partial application generally.
- The `arguments` object (array-*like*, no `.map()`/`.filter()`, doesn't exist in arrow functions) is superseded by rest parameters (`...args`, a real array, and can capture only the *remaining* args after named ones) — a common "why does `arguments` break in my arrow function" debugging scenario.
- Callback Hell (deeply nested async callbacks forming a "Pyramid of Doom") is the historical motivation for Promises/async-await — recognizing *why* it was painful (error handling scattered across every nesting level) explains the design of what replaced it. JS has no native function overloading — you simulate it by branching on `arguments.length`/argument types inside a single function, unlike TypeScript's compile-time overload signatures.
- Generator functions (`function*`, `yield`) pause and resume execution, producing values lazily on-demand via `.next()` — essential for streaming large/infinite sequences without materializing them all in memory, and the low-level mechanism `async`/`await` is built on top of.
- The three ways to write a function, with the notes' examples. Parameters are the inputs and `return` sends a value back; with no `return` a function returns `undefined`. An arrow with an **expression body** returns implicitly, which is what Top-20 Q7 means by "no return keyword for single line". To return an object literal from an arrow, wrap it in parentheses, because a bare `{` is parsed as a block:
```js
function add(a, b) { return a + b; }                 // declaration — hoisted with its body
add(5, 3);                                           // 8
const multiply = function (a, b) { return a * b; };  // expression — stored in a variable, can be anonymous
multiply(4, 2);                                      // 8
const divide = (a, b) => { return a / b; };          // arrow with a block body — needs return
const square = x => x * x;                           // arrow with an expression body — implicit return
square(5);                                           // 25
const makeUser = () => ({ name: 'x' });              // { name: 'x' }
const broken   = () => { name: 'x' };                // undefined — { } was parsed as a block with a label
```
- **Default + rest parameters together**, from the notes. The rest parameter must come **last** (`function f(...a, b) {}` is a `SyntaxError`), and with nothing passed it's an empty array, never `undefined`:
```js
function greet(name = 'Guest') { return 'Hello, ' + name; }
greet();          // 'Hello, Guest'
greet('Alice');   // 'Hello, Alice'
greet(null);      // 'Hello, null' — defaults apply only to undefined

function sumAll(...nums) { return nums.reduce((acc, n) => acc + n, 0); }
sumAll(1, 2, 3, 4);   // 10
sumAll(5, 10);        // 15

function createUser(name = 'User', ...roles) { return { name, roles }; }
createUser('John');                     // { name: 'John', roles: [] }
createUser('Jane', 'admin', 'editor');  // { name: 'Jane', roles: ['admin', 'editor'] }
```
- **Callbacks**: a callback is a function passed as an argument to another (higher-order) function, which calls it back later. The notes' analogy is handing someone a task and asking them to notify you when it's done. Callbacks are how timers, events and older APIs deliver results. A callback isn't asynchronous by itself, though. The one below runs synchronously, while the same callback passed to `setTimeout`, `addEventListener` or `fs.readFile` runs later from a queue:
```js
function process(num, callback) {
  const result = num * 2;
  callback(result);                 // "calling back" the function we were given
}
function show(result) { console.log('Result is:', result); }
process(5, show);                   // Result is: 10
```

**Senior Perspective:**
- ⚖️ Arrow functions solve the "losing `this`" problem so cleanly that they've become the default — but the trade-off is losing the ability to use them as constructors or access their own `arguments`, so a class method that genuinely needs dynamic `this` (e.g., prototype-based mixins) still needs a regular function.
- 🏗️ Function composition and currying aren't academic FP trivia in a senior interview — they're the pattern underneath middleware chains (Express, Redux), and recognizing that lineage is what signals you understand *why* a framework is shaped the way it is, not just how to call its API.
- 📉 JS's lack of native function overloading forces runtime argument inspection, which is a real source of bugs when argument shapes drift — this is one of the concrete, practical reasons teams adopt TypeScript, where overload signatures are checked at compile time instead.

### Functional Patterns: Currying, Memoization & Composition
- Currying transforms a multi-argument function into a chain of single-argument functions (`add(a)(b)(c)` instead of `add(a, b, c)`), which enables **partial application** — pre-filling some arguments once to produce a specialized, reusable function instead of repeating the fixed arguments at every call site:
```js
const add = a => b => c => a + b + c;
const addFive = add(5);     // 5 is now "baked in"
addFive(3)(2);               // 10
```
- Memoization caches a function's return value keyed by its arguments, trading memory for CPU — the standard implementation wraps a function in a closure holding a cache, and only produces correct results for **pure** functions (same input always same output, no hidden dependency on mutable external state):
```js
function memoize(fn) {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}
```
- 📉 `JSON.stringify(args)` as a cache key is a common shortcut with real limits — it silently treats distinct inputs as identical when they stringify the same way (key order in an object, `undefined` values dropped, functions/circular references unsupported), and it doesn't work at all for non-serializable arguments like DOM nodes. A production memoizer keying on object identity typically reaches for a `WeakMap` instead, which also has the side benefit of letting a cache entry get garbage-collected once the key object itself is no longer referenced anywhere else.
- Function composition (`compose(f, g)(x) === f(g(x))`) shares currying's underlying motivation — building complex behavior by piping small, single-purpose functions together instead of writing one large function — and is the conceptual foundation Redux middleware, RxJS operator chains, and Express/Koa middleware pipelines are all built on.
- The notes' minimal higher-order function and currying examples. `map`, `filter`, `reduce`, `forEach` and `sort` are the built-in HOFs you use daily, since each takes a function as an argument:
```js
function operation(a, b, fn) { return fn(a, b); }   // takes a function as an argument
const add = (x, y) => x + y;
operation(5, 3, add);                               // 8

function multiply(a) {                              // curried: multiply(2) → fn(b) → fn(c)
  return function (b) { return function (c) { return a * b * c; }; };
}
multiply(2)(3)(4);                                  // 24
```
- *Source note:* the notes' `memoize` stores results in a plain object and checks `if (cache[key]) return cache[key];`. That's a **truthiness** check, so any result that is falsy (`0`, `''`, `false`, `null`) is never served from the cache and gets recomputed on every call. In Node, a memoized function returning `0` ran 3 times for 3 identical calls. Check for **presence** instead (`key in cache`, `Object.hasOwn(cache, key)`, or `cache.has(key)` with the `Map` version above). Their `fn.apply(this, args)` is worth keeping, because it forwards `this` when the memoized function is used as a method.
- **Iterators and generators in code.** An *iterable* is any object with a `[Symbol.iterator]()` method that returns an *iterator*, which is an object whose `next()` returns `{ value, done }`. `for...of`, spread, array destructuring, `Array.from`, `Promise.all` and `new Map(iterable)` all consume this protocol. A generator function (`function*`) produces an object that is both iterable and an iterator. It pauses at each `yield` and resumes on the next `next()` call, so it can describe infinite sequences lazily:
```js
function* numberGenerator() { yield 1; yield 2; yield 3; }
const gen = numberGenerator();
gen.next().value;         // 1
gen.next().value;         // 2
gen.next().value;         // 3
gen.next();               // { value: undefined, done: true }
[...numberGenerator()];   // [1, 2, 3]

const it = [10, 20, 30][Symbol.iterator]();
it.next();   // { value: 10, done: false }
it.next();   // { value: 20, done: false }
it.next();   // { value: 30, done: false }
it.next();   // { value: undefined, done: true }

// Making your own object iterable
const range = {
  from: 1, to: 3,
  [Symbol.iterator]() {
    let cur = this.from; const last = this.to;
    return { next: () => (cur <= last ? { value: cur++, done: false } : { value: undefined, done: true }) };
  },
};
[...range];   // [1, 2, 3]

function* idGen() { let id = 1; while (true) yield id++; }   // infinite, but only computed on demand
```

**Senior Perspective:**
- 🏗️ Memoization is the pattern underneath `useMemo`/`React.memo`/selector libraries like Reselect; currying is the pattern underneath `connect()`-style higher-order functions and partial-application utilities — naming that lineage is what turns "I know FP terminology" into "I know why my framework is shaped this way."
- ⚖️ Memoization is a pure time/memory trade, not a free win — an unbounded cache in a long-running process (e.g., memoizing per-request data on a server) is a real memory-leak vector; production memoizers need eviction (LRU, TTL, max size), not just a bare `Map` that grows forever.

### Prototypes, Objects & OOP Patterns
- 🏗️ Prototypal inheritance means objects inherit directly from other objects via a hidden link — when a property lookup misses on the object itself, the engine walks the **prototype chain** up to `Object.prototype` before returning `undefined`. This is the mechanism that lets every array share `.push()` without copying the method into every instance.
```js
function Person(name) { this.name = name; }
Person.prototype.greet = function () { return 'Hello ' + this.name; };
const p1 = new Person('Abhi');
p1.greet();   // 'Hello Abhi' — not on p1 itself, found one link up
```
```text
p1 {name}  →[[Prototype]]→  Person.prototype {greet}  →[[Prototype]]→  Object.prototype {toString, …}  →  null
             (own props)        (shared methods)                           (lookup ends; miss = undefined)
```
- `prototype` (a property that exists only on constructor functions — the "blueprint") is distinct from `__proto__` (the live link every *instance* uses at runtime to actually resolve inherited methods) — modern code should use `Object.getPrototypeOf()` instead of touching `__proto__` directly.
- `new` triggers a precise 4-step sequence: create an empty object → link it to the constructor's `.prototype` → invoke the constructor with `this` bound to the new object → return the new object unless the constructor explicitly returns its own object. `instanceof` walks the prototype chain to check this lineage, but can give surprising `false` results across iframe/multi-realm boundaries where each has its own global constructors.
- Shallow copy (`Object.assign`, spread) copies top-level properties only — nested objects remain **shared references**, so mutating a nested property in the "copy" mutates the original too. Deep copy (`structuredClone()` — the modern built-in, handles Dates/nested structures; `JSON.parse(JSON.stringify())` — the old hack, silently drops functions/`undefined`/Dates) fully decouples the two. This distinction is one of the most common sources of "why did my original state mutate" bugs in state-management code.
- `Object.freeze()` (fully immutable — no add/delete/modify) vs. `Object.seal()` (no add/delete, but existing values **can** still change) vs. `Object.preventExtensions()` (only blocks adding new keys, the lightest protection) form a graduated immutability ladder — and critically, `const` alone only prevents *reassigning the variable*, not mutating the object it points to, a very common misconception.
- Getters/setters let you expose computed or validated "virtual" properties that read like data but run logic on access/assignment — useful for derived values (`fullName` from `firstName`+`lastName`) and input validation at the point of assignment.
- 👥 Composition over inheritance ("has-a" via small pluggable behaviors, e.g. Mixins via `Object.assign`) avoids the deep, brittle class-hierarchy trees classical inheritance ("is-a") tends toward — swapping one component's behavior doesn't risk breaking a whole inheritance chain. Modifying built-in prototypes (`Array.prototype.myFeature = ...`) is "monkey patching" — it silently breaks the moment a third-party library or a future JS spec adds a method with the same name, a well-known production incident class.
- `#privateField` syntax (ES2020+) gives compiler-enforced private class state — a real upgrade over the old underscore-prefix convention (`_secret`), which was never actually enforced, only implied.
- Proxy + Reflect are the mechanism underneath modern fine-grained reactivity (Vue 3, Svelte-adjacent patterns): a Proxy intercepts get/set traps on an object, letting you run validation or UI-update logic transparently whenever a property is read or written, with Reflect providing the "default behavior" implementation the Proxy trap defers to.

**Senior Perspective:**
- ⚖️ Shallow vs. deep copy isn't a theoretical distinction — picking the wrong one is the single most common root cause of "immutable state that isn't actually immutable" bugs in Redux/React state, and `structuredClone()` finally makes deep copy a one-line, spec-correct built-in instead of a fragile `JSON.stringify` hack.
- 🏗️ Composition-over-inheritance is the architectural reason mixins and Proxy-based reactivity systems exist — recognizing this lineage is what lets you explain *why* Vue 3's reactivity or a plugin-based component API is designed the way it is, rather than treating it as magic.
- 📉 Monkey-patching built-in prototypes is exactly the kind of "clever" code that passes review from a junior engineer and causes a production incident six months later when a third-party dependency collides with it — a senior red flag in any PR.

### Classes, Inheritance & the OOP Pillars in Code
- A `class` is a blueprint and an object is an instance of it. `new` creates the instance and runs the `constructor`, and methods declared in the class body are stored **once on the prototype**, not copied into each instance. That's the same prototype-chain mechanism described in the previous subsection, with nicer syntax:
```js
class Person {
  constructor(name, age) { this.name = name; this.age = age; }
  introduce() { return `Hi, I'm ${this.name}`; }
}
const p1 = new Person('John', 25);
p1.introduce();                                      // "Hi, I'm John"
typeof Person;                                       // 'function'
Object.getPrototypeOf(p1) === Person.prototype;      // true — introduce lives there, not on p1
```
- *Source note:* "classes are just syntactic sugar over prototypes" (the notes' "Prototypes are the backbone of JS OOP" framing) is mostly true, but interviewers like to test where it breaks down. A class can't be called without `new` (`TypeError`). Class declarations are hoisted into the TDZ like `let`, so using one before its line throws a `ReferenceError`. A class body always runs in **strict mode**, so a method pulled off its instance (`const f = user.show; f()`) gets `this === undefined` and throws instead of silently reading `window`. Class methods are also non-enumerable.
- **Inheritance** uses `extends`, and `super` reaches the parent. In a subclass constructor you must call `super(...)` before touching `this` (otherwise `ReferenceError`), and `super.method()` calls the parent's version of an overridden method:
```js
class Animal { speak() { return 'Animal speaks'; } }
class Dog extends Animal { speak() { return 'Woof!'; } }
class Husky extends Dog { speak() { return 'Awoo!'; } }     // multi-level: Husky → Dog → Animal
new Husky() instanceof Animal;                              // true

class Puppy extends Dog { speak() { return super.speak() + ' (small)'; } }
new Puppy().speak();                                        // 'Woof! (small)'

class Base { constructor(n) { this.n = n; } }
class Derived extends Base {
  constructor(n) { super(n); this.twice = n * 2; }          // super() first, then this
}
```
- **Encapsulation** bundles data with the methods that guard it. `#private` fields are enforced by the language, so outside code can't read or write `#balance` at all (`acc.#balance` is a `SyntaxError` outside the class, and `acc['#balance']` is just `undefined`). The only way in is through the public methods, which can validate:
```js
class BankAccount {
  #balance = 0;                                   // private field
  constructor(owner) { this.owner = owner; }
  deposit(amount) { if (amount > 0) this.#balance += amount; }
  getBalance() { return this.#balance; }
}
const acc = new BankAccount('Asha');
acc.deposit(500);
acc.deposit(-50);                                 // rejected by the guard
acc.getBalance();                                 // 500
```
- **Polymorphism** means the same method name behaves differently per class, so calling code can treat them uniformly. **Abstraction** is the fourth pillar the notes don't name: exposing a simple interface (`deposit`, `speak`) while hiding the details. Together with encapsulation and inheritance, these are the "four pillars":
```js
class Animal2 { speak() { return 'Some sound'; } }
class Cat extends Animal2 { speak() { return 'Meow!'; } }
class Cow extends Animal2 { speak() { return 'Moo!'; } }
class Dog2 extends Animal2 { speak() { return 'Woof!'; } }
[new Cat(), new Cow(), new Dog2()].forEach(a => console.log(a.speak()));   // Meow!  Moo!  Woof!
```
- Inside a class method, `this` is the instance the method was called on (`user.show()` → `user`). It's the same implicit-binding rule from Functions, `this` & Functional Patterns above, with the strict-mode difference noted. `static` members belong to the class itself (`Temp.fromF(212)`), and `get`/`set` accessors expose computed properties that read like fields.

**Senior Perspective:**
- 👥 The notes' best practices (keep properties private, one responsibility per class, meaningful names) are the class-level version of composition over inheritance. Deep `extends` chains like `Husky → Dog → Animal` look tidy in a tutorial but couple every subclass to its parents' internals. Most production code keeps hierarchies to one level and composes behaviour instead.
- 📉 The "detached method loses `this`" bug is the most common class-related production error in UI code: passing `this.handleClick` as a callback without binding it. Knowing that class bodies are strict, so the result is a loud `TypeError` rather than a silent `window` read, helps you diagnose it quickly. The fixes are an arrow-function class field (`handleClick = () => {}`) or `.bind(this)` in the constructor.

### Objects, Arrays & Destructuring Patterns
- Destructuring extracts values positionally (arrays) or by key (objects) in one expression, and three independent mechanisms — renaming, default values, and skipping — compose together, which is why destructuring in a function signature (`function fn({ name: username, city, country = 'India' } = {})`) reads denser than it actually is once you separate the three:
```js
const { name: username, city, country = 'India' } = user;  // rename + default
const [first, , , fourth] = arr;                             // skip with empty commas
```
- Spread and rest use the identical `...` token to do opposite jobs depending on position: spread **expands** an iterable into individual elements (copying/merging arrays and objects, or passing an array as individual call arguments); rest **collects** remaining elements/arguments into a single array (`function sumAll(...nums)`, or `const [first, ...rest] = arr`). Both spread operations are shallow — the same shallow-copy caveat already covered under Prototypes, Objects & OOP Patterns above — nested objects remain shared references after `{...obj}`.
- The core array-method toolkit shares one property worth stating explicitly under interview pressure: `map`/`filter`/`reduce`/`find`/`some`/`every` never mutate the original array (unlike `sort`, `splice`, `push`/`pop`, which do in place) — and `reduce` is underused relative to its actual power, since a `map` or `filter` (or a `groupBy`) is really just a specific accumulator pattern applied through `reduce`. `some`/`every` short-circuit on the first decisive element, which matters when the predicate is expensive.
- 📉 `.map()` vs. `.forEach()` is a frequent tell in code review: `.forEach()` returns `undefined` and exists purely for side effects, while `.map()` returns a new array and is the correct tool whenever the transformed result is actually needed — building a new array by `push()`-ing inside a `.forEach()` works, but signals unfamiliarity with the more idiomatic `.map()`.
- Small ES6+ utilities that round out the toolkit: `Object.entries(obj)` converts an object to `[key, value]` pairs (the bridge that lets you run array methods over an object, and `Object.fromEntries()` converts back); `.includes()` on arrays and strings replaces the old `indexOf(x) !== -1` idiom (and, unlike `indexOf`, correctly finds `NaN`); `**` is the exponentiation operator (`2 ** 3` → `8`); and `&&`/`||` return the deciding *operand*, not a boolean (`true && 'Yes'` → `'Yes'`, `false || 'No'` → `'No'`), which is what makes short-circuit rendering patterns work.
- **Array CRUD basics.** Arrays are ordered, zero-indexed, can mix any types (`[1, 'Hello', true, null]`), and are mutable even when declared with `const`. Reading past the end gives `undefined`, and `.at(-1)` reads from the end. The two decks' comments show the array's **state** after each call, but the **return values** are what live-coding questions check:
```js
let arr = [1, 2, 3];
arr.push(4);      // arr → [1, 2, 3, 4]   returns 4 (the new length)
arr.pop();        // arr → [1, 2, 3]      returns 4 (the removed element)
arr.shift();      // arr → [2, 3]         returns 1 (the removed element)
arr.unshift(1);   // arr → [1, 2, 3]      returns 3 (the new length)

let r = [10, 20, 30];
r[0];  r[2];  r.length;   // 10  30  3   — length is a property, not a method
r[1] = 99;                // [10, 99, 30] — update by index

const s = [1, 2, 3, 4, 5];
s.slice(1, 3);            // [2, 3] — copy of indexes 1..2 (end excluded); s unchanged
s.splice(1, 2);           // [2, 3] — REMOVES 2 items from index 1; s is now [1, 4, 5]
const ins = [1, 4];
ins.splice(1, 0, 2, 3);   // inserts at index 1, deletes none; ins is now [1, 2, 3, 4]
```
- The notes' "most used" methods with their outputs: `[1, 2, 3].map(n => n * 2)` → `[2, 4, 6]`; `[1, 2, 3, 4].filter(n => n % 2 === 0)` → `[2, 4]`; `users.find(u => u.id === 2)` → the **first** match `{ id: 2 }` (or `undefined` if none; `findIndex` returns the index or `-1`); `[1, 2, 3, 4].reduce((acc, n) => acc + n, 0)` → `10`; `['A', 'B', 'C'].forEach(f => console.log(f))` logs A B C and returns `undefined`. Their rule of thumb: `map` to transform into a new array, `filter` to select matching items, `reduce` to calculate one value. `some` answers "does any element match?" and `every` answers "do all match?".
- *Source note:* the notes show `[3, 1, 4, 2].sort()` → `[1, 2, 3, 4]` "(as strings)". That output only works because every element is a single digit. The default sort converts elements to **strings** and compares them in UTF-16 order, so `[10, 1, 2, 25].sort()` gives `[1, 10, 2, 25]`. Always pass a comparator for numbers. `sort()` also **mutates** the array and returns the same array reference. `toSorted()` is the non-mutating version (see the ES2023 additions below).
```js
[10, 1, 2, 25].sort();                  // [1, 10, 2, 25]  — string order
[10, 1, 2, 25].sort((a, b) => a - b);   // [1, 2, 10, 25]  — numeric ascending (b - a for descending)
```
- **Objects**: key-value pairs where values can be any type, including functions (called *methods*, where `this` is the object the method was called on). Use dot access for fixed keys and brackets for dynamic or non-identifier keys (`user['first-name']`, `user[key]`). The notes' toolkit, checked in Node:
```js
const user = { name: 'John', age: 25, role: 'QA' };
Object.keys(user);      // ['name', 'age', 'role']
Object.values(user);    // ['John', 25, 'QA']
Object.entries(user);   // [['name', 'John'], ['age', 25], ['role', 'QA']]
user.hasOwnProperty('age');      // true
user.hasOwnProperty('salary');   // false
Object.hasOwn(user, 'age');      // true — modern replacement; also works on Object.create(null) objects
'toString' in user;              // true — `in` also sees inherited keys; hasOwn doesn't

const target = { a: 1 };
Object.assign(target, { b: 2 }); // target is now { a: 1, b: 2 } — mutates and returns target

const merged = { ...{ name: 'John', age: 25 }, ...{ role: 'Tester' } };   // { name: 'John', age: 25, role: 'Tester' }
```
- *Source note:* the notes say writes to a frozen object, and deletes or additions on a sealed one, are "ignored". That's only true in **sloppy mode**. In strict mode, which covers every ES module and class body, each of those writes throws a `TypeError`. Both `freeze` and `seal` are also **shallow**, so nested objects stay mutable:
```js
const fz = Object.freeze({ name: 'John' });
fz.name = 'Alice';   // sloppy: silently ignored (still 'John');  strict: TypeError
const sl = Object.seal({ name: 'John' });
sl.name = 'Mike';    // allowed — existing props can change
delete sl.name;      // ignored (strict: TypeError) — can't remove
sl.age = 25;         // ignored (strict: TypeError) — can't add
Object.freeze({ inner: { v: 1 } }).inner.v = 2;   // works — freeze is shallow
```
- *Source note:* the Objects page says "object keys are always strings". The notes' own cheat-sheet page gets it right: keys are **strings or Symbols**. Other key types are converted to strings (`{ 1: 'one' }` has the key `'1'`). Symbol keys are skipped by `Object.keys`/`for...in`/`JSON.stringify` but returned by `Object.getOwnPropertySymbols` and `Reflect.ownKeys`. If you need non-string keys such as objects or numbers kept as numbers, use a `Map`.

**Senior Perspective:**
- ⚖️ Spread's shallow-copy behavior is the same footgun as `Object.assign()` covered above — the fix isn't "avoid spread everywhere," it's being precise about which layer of a structure actually needs decoupling, and reaching for `structuredClone()` only when true nested-mutation independence matters.
- 🏗️ Treating `reduce()` as the general case that `map`/`filter`/`groupBy` all specialize is a useful mental model for reasoning about array pipelines quickly — even though reaching for the more specific, more readable method is still the right call in real code.
- 📉 Overusing destructuring (deeply nested patterns several levels into an API response) trades a few saved characters for code that breaks with an opaque `Cannot destructure property` error the moment an intermediate key is missing — one level of destructuring plus optional chaining is usually the more robust shape.

### Strings, Numbers, Math & Dates
- Strings are **immutable** primitives, so every string method returns a *new* string and `str.toUpperCase()` on its own changes nothing. The everyday toolkit: `length` (a **property**), `toUpperCase()`/`toLowerCase()`, `trim()` (also `trimStart`/`trimEnd`), `slice(a, b)`/`substring(a, b)` (extract), `replace(old, new)` (first match only; `replaceAll` for every match), `includes(str)` (true/false), `indexOf(str)` (first index or `-1`), and `split(sep)` (to an array). Template literals are covered under Modern JavaScript below.
- *Source note:* the notes list `length()` among the string **methods**. `length` is a property. `'abc'.length` is `3`, and `'abc'.length()` throws `TypeError: 'abc'.length is not a function`. Arrays behave the same way.
- *Source note:* the notes' string example can't produce all of its claimed outputs. It shows `text.slice(2, 7)` → `"Hello"` **and** `text.split(" ")` → `["", "Hello", "JavaScript", ""]`, but no single string gives both. The `split` result requires exactly one leading space, and then `slice(2, 7)` is `"ello "`. With two leading spaces `slice(2, 7)` is `"Hello"`, but `split(" ")` returns six items (`['', '', 'Hello', 'JavaScript', '', '']`). The corrected, Node-checked version:
```js
let text = ' Hello JavaScript ';        // one space on each side
text.trim().toUpperCase();              // 'HELLO JAVASCRIPT'
text.slice(1, 6);                       // 'Hello'   (slice(2, 7) would be 'ello ')
text.includes('Java');                  // true
text.split(' ');                        // ['', 'Hello', 'JavaScript', '']
'JavaScript'.slice(-6);                 // 'Script'  — slice accepts negative indexes
'JavaScript'.substring(4, 0);           // 'Java'    — substring swaps reversed args (slice(4, 0) → '')
'a-a-a'.replace('a', 'b');              // 'b-a-a'   — first match only
'a-a-a'.replaceAll('a', 'b');           // 'b-b-b'
'Hello'.indexOf('l');                   // 2         ('Hello'.indexOf('z') → -1)
' Hello JS '.replace('JS', 'World');    // ' Hello World '  (cheat-sheet example)
```
- **Number methods**, from the notes: `(123.4567).toFixed(2)` → `"123.46"` and `.toPrecision(4)` → `"123.5"`. Both return **strings**, so convert back with `Number()` before doing more arithmetic. `Number.isInteger(10)` → `true`.
- *Source note:* the notes show `Number.isNaN('abc')` → `true`. It returns **`false`**. `Number.isNaN` doesn't coerce and returns `true` only for the actual `NaN` value, while the **global** `isNaN('abc')` coerces `'abc'` to `NaN` first and returns `true`. That coercion is exactly why `Number.isNaN` was added, as described under Types, Coercion & Equality above. To validate user input, use `Number.isNaN(Number(input))`.
```js
Number.isNaN('abc');          // false — no coercion: 'abc' is a string, not NaN
isNaN('abc');                 // true  — coerces first (the legacy global)
Number.isNaN(Number('abc'));  // true  — explicit conversion, then the strict check
(1.005).toFixed(2);           // '1.00' — 1.005 is really 1.00499999… in binary floating point
new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.5);   // '$1,234.50'
```
- 📉 The notes recommend `toFixed()` for currency. It's fine for display, but it inherits binary floating-point error (`(1.005).toFixed(2)` is `'1.00'`), and it doesn't add locale separators or currency symbols. Real money calculations should use **integer minor units** (cents), and display should use `Intl.NumberFormat`.
- **Math** is a static namespace, not a constructor. `Math.PI` → `3.141592653589793`, `Math.abs(-7)` → `7`, `Math.round(4.6)` → `5`, `Math.floor(4.6)` → `4`, `Math.ceil(4.1)` → `5`, `Math.max(10, 20, 5)` → `20` (use `Math.max(...arr)` for arrays), `Math.min(...)`, and `Math.random()` → a float in **[0, 1)**. Two edge cases that come up: `Math.round(-2.5)` is `-2` (halves round toward +∞), and `Math.floor(-4.6)` is `-5` while `Math.trunc(-4.6)` is `-4`.
```js
const dice = Math.floor(Math.random() * 6) + 1;   // integer 1..6
```
- 📉 The notes say to use `Math.random()` "carefully for fair randomness". Specifically, it isn't cryptographically secure, so never use it for tokens, IDs or anything security-related. Use `crypto.getRandomValues()` or `crypto.randomUUID()` instead (both exist in browsers and Node).
- **Dates.** `new Date()` is the current date and time. The getters are `getFullYear()`, `getMonth()` (**0–11**, 0 = January), `getDate()` (day of the month), `getDay()` (weekday, 0 = Sunday), plus `toLocaleDateString()`/`toLocaleTimeString()` for readable output.
- *Source note:* the notes' birthday example claims `birth.getMonth() + 1` → `4 (May)`. It prints **`5`**. `getMonth()` already returns `4` for May, and the `+ 1` converts it to the human month number. The other outputs are right, and they hold in every time zone because a date-time string without `Z` is parsed as **local** time:
```js
let birth = new Date('2000-05-10T10:30:00');   // no "Z" → local time
birth.getFullYear();                   // 2000
birth.getMonth();                      // 4  (May, zero-based)
birth.getMonth() + 1;                  // 5  (the source says 4, which is wrong)
birth.getDate();                       // 10
birth.toDateString();                  // 'Wed May 10 2000'
birth.toTimeString().slice(0, 8);      // '10:30:00'

new Date('2000-05-10').toISOString();  // '2000-05-10T00:00:00.000Z' — a DATE-ONLY string is parsed as UTC
new Date(2024, 0, 32).getMonth();      // 1 — out-of-range days roll over into February
```
- 📉 The notes' "always consider timezone" advice, made concrete: `Date` is **mutable** (`setDate` changes the object in place), month numbers are zero-based, and date-only vs date-time strings are parsed in different zones (UTC vs local). Together these cause most date bugs. Store and send timestamps as UTC ISO strings, format at the edge with `Intl.DateTimeFormat`/`toLocale*String`, and see the note on Temporal under Modern JavaScript below.

**Senior Perspective:**
- ⚖️ `toFixed`, `Math.random` and `Date` all look fine in a demo and then fail in production (money rounding, predictable tokens, timezone shifts). Knowing the specific failure mode of each, and the replacement (integer cents plus `Intl`, `crypto`, UTC plus `Intl.DateTimeFormat` or Temporal), is what makes a basic-API question into a senior answer.
- 📉 String and number output-prediction questions (`slice` vs `substring`, `Number.isNaN` vs `isNaN`, `getMonth()` off-by-one) are exactly where prep material tends to contain errors. Three appear in this source alone. When a claimed output looks surprising, check it in a console before memorising it.

### The Event Loop & Asynchronous JavaScript
- 🏗️ JavaScript is single-threaded (one Call Stack, LIFO, one thing executes at a time) — but the *environment* (browser/Node) is multi-threaded, running timers/network/file-I/O on separate threads via Web APIs and handing results back to the main thread through the Event Loop. This split is the entire reason JS can feel "concurrent" without actually being multi-threaded, and it's the foundational mental model every async question builds on.
- The Event Loop's only job: check if the Call Stack is empty, and if so, pull the next item from a queue onto the stack. Two queues exist with different priority: the **Microtask Queue** (Promise `.then()` callbacks, `queueMicrotask`) is fully drained before the engine touches the **Macrotask/Task Queue** (`setTimeout`, DOM events) at all — which is why `setTimeout(fn, 0)` still runs *after* a resolved Promise's `.then()`, and why a recursively-scheduling microtask chain can cause **event loop starvation**, freezing UI updates and timers entirely.
- Promises have exactly three states (Pending → Fulfilled or Rejected, and once settled, permanently locked), and `.then()` chaining works because every `.then()` returns a **new** Promise — the mechanism that lets you write flat sequential async code instead of nested Callback Hell.
- `async`/`await` is syntactic sugar over Promise chains: `await` pauses the async function (saving its stack frame), lets the rest of the program continue, and schedules resumption as a microtask once the awaited Promise settles — making async code *read* synchronously while remaining fully non-blocking. Errors are handled with ordinary `try/catch`, which is strictly more ergonomic than mixing `.catch()` chains with synchronous error handling.
- `Promise.all()` is fail-fast (one rejection kills the whole batch, you lose the other results) vs. `Promise.allSettled()` (waits for everything, gives you a per-promise fulfilled/rejected breakdown) — pick `allSettled` whenever partial success from independent tasks is acceptable. `Promise.race()` settles on whichever promise finishes first, success *or* failure (useful for timeouts); `Promise.any()` ignores rejections and resolves on the first *success*, only rejecting if everything fails (useful for redundant/mirror-server fetches).
- 📉 Race conditions in JS come from unpredictable async **completion order**, not from true concurrent thread access — two requests can return out-of-order and the second-sent-but-first-returned response can silently overwrite newer data with stale data unless you guard with request IDs/flags or `AbortController`.
- Promisification (wrapping an old Node "error-first callback" API in `new Promise(...)`) lets you bring legacy async APIs into modern `async`/`await` code. Concurrency-limited execution (a "Promise Pool" pattern capping N simultaneous in-flight tasks) is the practical fix for the "1,000 `Promise.all()` requests crashed the server" failure mode. `for await...of` (async iterators) extends the same pause-per-item ergonomics to streamed/paginated data sources.

- The notes' async progression (callbacks → Promises → async/await → `fetch` → the event loop) with their examples. The callback version `getData(cb)` with `setTimeout(() => cb('Data Loaded'), 1000)` logs "Data Loaded". A `new Promise` that calls `resolve('Success!')` after 1s logs "Success!" through `.then`. `async function loadData()` wraps `await fetch('data.json')` and `await res.json()` in `try/catch`. All of these ran in Node and printed the stated output. Their queue inventory is right, with one addition: the **microtask** queue holds Promise reactions (`.then/.catch/.finally`, code resumed after an `await`), `queueMicrotask`, and `MutationObserver` callbacks. The **macrotask** (task) queue holds `setTimeout`, `setInterval`, I/O completion, and DOM/UI events (plus `setImmediate` in Node). Their four-step order is correct: run the current call stack → when it's empty, run **all** microtasks (including ones queued by microtasks) → take **one** macrotask → repeat.
- *Source note:* the notes put "UI rendering" in the macrotask queue. In browsers, rendering (style → layout → paint) is its own step of the event loop. The browser gets a chance to render **after** a task and its microtasks finish, typically once per frame, and it runs `requestAnimationFrame` callbacks just before painting. That's why a long synchronous task, or a microtask chain that never ends, freezes the screen: the loop never reaches the rendering step. Treating rendering as "just another macrotask" hides that.
```js
// Verified in Node: a microtask queued by a microtask still runs before the next timer
console.log('sync1');
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => {
  console.log('micro1');
  Promise.resolve().then(() => console.log('micro-nested'));
});
queueMicrotask(() => console.log('micro2'));
console.log('sync2');
// sync1 → sync2 → micro1 → micro2 → micro-nested → timeout
```

```text
Event Loop priority:
Call Stack empty? → drain ENTIRE Microtask Queue (Promises) → run ONE Macrotask (setTimeout/DOM event) → repeat
                     ^-- microtasks are fully starved out before a single macrotask runs
```

**Senior Perspective:**
- 🏗️ Microtask-vs-macrotask ordering is the single most tested "gotcha" in senior JS interviews precisely because it's counter-intuitive and directly explains real production bugs — a `setTimeout(fn, 0)` "immediately" scheduled callback that somehow runs after three Promise chains is not a bug, it's the spec working as designed.
- ⚖️ `Promise.all` vs `allSettled` vs `race` vs `any` are four distinct failure-tolerance policies, not interchangeable syntax — picking the wrong one either silently discards a partial success (using `all` when you wanted `allSettled`) or fails too eagerly (using `race` when you wanted `any`).
- 📉 Race conditions from out-of-order async responses are a top cause of "the UI showed stale data" bugs in production — the fix (request IDs, `AbortController`, last-write-wins guards) is standard, but only if the team recognizes the class of bug in code review rather than treating each occurrence as a one-off.

### Async Patterns in Practice: Ordering, Fetch & Common Pitfalls
- A worked example turns the abstract microtask-before-macrotask rule above into something you can trace line-by-line under interview pressure — narrate it exactly this way out loud:
```js
console.log('1 Start');
setTimeout(() => console.log('2 setTimeout'), 0);          // macrotask
Promise.resolve().then(() => console.log('3 Promise'));     // microtask (queued first)
queueMicrotask(() => console.log('4 queueMicrotask'));      // microtask (queued second)
console.log('5 End');
// Output: 1 Start → 5 End → 3 Promise → 4 queueMicrotask → 2 setTimeout
// Sync code runs to completion; then the ENTIRE microtask queue drains in FIFO
// registration order (.then and queueMicrotask share one queue); then ONE macrotask.
```
- 📉 Some prep material (including infographic-style cheat sheets) prints this exact snippet with `queueMicrotask` firing *before* `Promise.then` — that's wrong per spec. Both land in the same FIFO microtask queue, so registration order decides; an interviewer who asks this is often checking precisely whether you know there's one queue, not two.
- `setTimeout(fn, ms)`/`setInterval(fn, ms)` delays are a **minimum**, not a guarantee — the callback is a macrotask that still waits for the Call Stack and the microtask queue to empty, so a long synchronous task or a microtask flood can push it arbitrarily late (and browsers clamp nested timers to ≥4ms and throttle background tabs further). Always keep the ID and `clearTimeout`/`clearInterval` it on teardown; a forgotten `setInterval` is one of the most common leaks listed under Performance below.
- The Promise constructor itself is worth writing from memory, since "promisify this callback API" is a common live-coding warm-up — `resolve`/`reject` settle it exactly once, and `.finally()` runs regardless of outcome (cleanup: hide spinners, release locks) without receiving or altering the settled value:
```js
const p = new Promise((resolve, reject) => {
  setTimeout(() => (ok ? resolve('Success!') : reject(new Error('Failed'))), 1000);
});
p.then(console.log).catch(console.error).finally(() => console.log('Done'));
```
- `fetch()`'s one specific gotcha (introduced under DOM, Events & Browser Platform APIs below) is worth a concrete checklist, because it's easy to get wrong even after "knowing" it abstractly: `fetch()` only rejects on genuine network failure, so a 404/500 is still a *successful* Promise resolution — check `res.ok` manually, wrap in `try/catch`, and give the UI explicit loading/empty/error states rather than assuming "no throw" means "good data":
```js
async function getUsers() {
  try {
    const res = await fetch('/api/users');
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Fetch error:', err.message);
    throw err;   // re-throw so the caller can still drive loading/error UI state
  }
}
```
- A checklist of async pitfalls that show up constantly in real code review:
  - Forgetting `await` — you silently end up holding a pending `Promise` object instead of its resolved value, and the resulting bug usually surfaces far from the actual mistake (`if (user.isAdmin)` on a Promise is just `undefined`, which is falsy, so it fails without an error).
  - Not handling rejections at all, producing an `UnhandledPromiseRejection` (which terminates the process by default in modern Node).
  - 📉 **`async` inside `Array.prototype.forEach()`** — a genuine, easy-to-miss footgun: `forEach` ignores its callback's return value, so it never awaits the Promise each async callback returns. Every iteration kicks off concurrently, the outer function continues immediately, and any rejection escapes the surrounding `try/catch`. Use `for...of` when you need sequential async work, or `await Promise.all(items.map(asyncFn))` when parallel is actually fine.
  - Not `return`-ing a promise inside a `.then()` chain, which silently breaks sequencing — the next `.then()` fires immediately with `undefined` instead of waiting on the nested work.
  - Blocking the main thread with heavy synchronous work between two `await`s — `await` only yields at genuine async boundaries, so a tight synchronous loop inside an `async` function freezes the UI just as badly as one outside it.
```js
// ❌ outer function returns before any save completes; errors escape try/catch
items.forEach(async (item) => { await save(item); });

// ✅ sequential
for (const item of items) { await save(item); }

// ✅ parallel, and awaited
await Promise.all(items.map(save));
```
- Three small utilities worth recognizing instantly, since "implement retry/timeout from scratch" is a common live-coding ask built directly on closures and `Promise.race`:
```js
// Delay / sleep
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Retry a failing async function up to N more times
async function retry(fn, retries = 3) {
  try {
    return await fn();
  } catch (err) {
    if (retries === 0) throw err;
    await delay(1000);
    return retry(fn, retries - 1);
  }
}

// Reject if a promise takes longer than `ms`
function timeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), ms)),
  ]);
}
```
- Two follow-ups interviewers commonly push on with these: `retry` should usually use **exponential backoff with jitter** (`delay(base * 2 ** attempt + random)`) rather than a fixed 1s, so many clients recovering from the same outage don't retry in synchronized waves; and `timeout` only stops *waiting* — the underlying request keeps running. Truly cancelling it requires passing an `AbortSignal` (e.g. `fetch(url, { signal: AbortSignal.timeout(ms) })`).
- Debugging async code specifically: `console.table()` for arrays of records, `console.group()`/`console.groupEnd()` to nest logs per request, the `debugger;` statement to pause at a line whenever DevTools is open, and the DevTools "async" stack traces, which stitch together the call chain across `await` boundaries that a plain stack trace would lose.

**Senior Perspective:**
- 🏗️ The `forEach` + `async` footgun is a strong "have you actually shipped async code" signal — it passes a quick review from anyone pattern-matching on "there's an `await` in there" and only breaks at runtime, which is exactly what separates candidates who've written this code from candidates who've only read about it.
- ⚖️ `timeout()` uses the same "first to settle wins" mechanism as the `Promise.race()` covered above — recognizing that a timeout wrapper and a redundant-mirror-fetch are the *same* primitive applied to different problems is a stronger signal than memorizing them as unrelated recipes. Knowing that `race` alone doesn't cancel anything (hence `AbortController`) is the staff-level follow-through.
- 📉 An unchecked `res.ok` is invisible in the happy path and only surfaces when a backend starts returning errors, which is the worst time to learn your error handling doesn't work. That's why the fetch checklist, retry policy, and timeout belong in one shared API-client wrapper instead of being reimplemented (or forgotten) at every call site.

### Error Handling & Debugging
- `try...catch...finally` handles **runtime** errors in synchronous code, or in async code after an `await`, so a failure doesn't crash the app. `catch` receives the error object (`error.name`, `error.message`, `error.stack`), and `finally` **always** runs, whether the `try` succeeded, threw, or even `return`ed. That makes it the place for cleanup such as hiding spinners, closing handles and releasing locks. A `try/catch` can't catch syntax errors in the same script, because the script never starts running, and it can't catch errors thrown later inside a callback (`setTimeout`, an event handler, a non-awaited Promise). Those need their own `try/catch` or a `.catch()`.
```js
try {
  const result = riskyFunction();          // throws new Error('bad input')
  console.log(result);
} catch (error) {
  console.log('Error:', error.message);    // Error: bad input
} finally {
  console.log('Cleanup always runs');      // Cleanup always runs
}

function f() { try { return 'try'; } finally { console.log('finally ran'); } }
f();   // logs 'finally ran', returns 'try'  (a `return` inside finally would override it — avoid that)
try { JSON.parse('{'); } catch { /* optional catch binding (ES2019) — omit (err) when unused */ }
```
- **`throw` and custom errors.** Throw `Error` objects, never bare strings, because only `Error` objects carry a `stack`. Subclass `Error` so callers can branch on `instanceof` or `name` instead of parsing message text. Chain the underlying failure with `cause` (ES2022) so the original stack isn't lost:
```js
function validateAge(age) {
  if (age < 18) throw new Error('Age must be 18+');
  return 'Valid Age';
}

class ValidationError extends Error {
  constructor(msg) { super(msg); this.name = 'ValidationError'; }
}
try {
  throw new ValidationError('Email invalid');
} catch (e) {
  e instanceof ValidationError;   // true (and e instanceof Error is true too)
  String(e);                      // 'ValidationError: Email invalid'
}

try { JSON.parse(raw); }
catch (err) { throw new Error('Config load failed', { cause: err }); }   // err is kept on .cause
```
- The built-in error types to name when asked "what errors have you seen?": `ReferenceError` (undeclared name, or a TDZ access), `TypeError` (calling a non-function, reading a property of `null`/`undefined`, assigning to a `const`), `SyntaxError` (invalid code, or `JSON.parse` on bad input), and `RangeError` (`new Array(-1)`, or unbounded recursion's "Maximum call stack size exceeded").
- **Console methods** from the notes: `console.log` (general), `info`, `warn`, `error` (with a stack trace and red styling in DevTools), `table` (arrays and objects as a grid, e.g. `console.table([{ a: 1 }, { a: 2 }])`), `assert(condition, msg)`, `clear`, and `group('User Details')`/`groupEnd()` to nest related logs. Note that `console.assert` prints **only when the condition is false** (`console.assert(2 > 1, 'Not true!')` prints nothing, while `console.assert(1 > 2, 'Not true!')` prints "Assertion failed: Not true!"), and it never throws or stops execution.
- **DevTools debugging** (the notes' Sources-panel walkthrough): open **Sources**, find the file in the navigator, click a line number to set a **breakpoint**, then reload or trigger the code. Execution pauses there, and you can step over, into or out of calls, read the **Call Stack**, inspect **Scope** variables, and add **Watch** expressions (in the notes' screenshot, `result` shows `undefined` because line 6 hasn't run yet). Conditional breakpoints, `debugger;` statements, and "pause on caught/uncaught exceptions" cover most of the rest.
- Practices from the notes: never swallow errors silently (an empty `catch {}` hides bugs); keep `try` blocks **small and specific** so you know which call failed; write meaningful messages; test edge cases and failure paths; **don't expose internal error details** (stack traces, SQL, file paths) to end users in production; send errors to a monitoring service such as **Sentry** or **LogRocket**; and remove debug `console.log`s before shipping (a lint rule or a build step that strips them is more reliable than remembering).

**Senior Perspective:**
- 🏗️ Error boundaries are an architecture decision. Decide where errors are **caught** (at the edges: request handlers, top-level UI boundaries, job runners), where they're only **annotated** and rethrown (`cause`), and where they're **reported**. Catching everywhere produces duplicate logs and hidden failures; catching nowhere produces crashes. Typed error classes are what let the edge layer map failures to the right user message or HTTP status.
- 📉 An unhandled Promise rejection is the async equivalent of an uncaught exception. Modern Node terminates the process for one by default, and browsers fire an `unhandledrejection` event. A global handler that reports to monitoring is a safety net, not a replacement for awaiting and handling at the call site.

### DOM, Events & Browser Platform APIs
- The DOM (page structure as a manipulable object tree) and the BOM (`window`, `location`, `history`, `screen` — everything *around* the page) are distinct APIs serving different purposes: content manipulation vs. browser-environment interaction.
- Events travel in two phases: **Capturing** (top-down, window → target) then **Bubbling** (target → back up to window); most listeners default to the bubbling phase. **Event Delegation** exploits bubbling — one listener on a parent handles all current *and future* children by checking `event.target`, which is dramatically more memory-efficient than attaching hundreds of individual listeners and automatically works for dynamically-added elements. `event.target` (what was actually clicked) vs. `event.currentTarget` (what the listener is physically attached to) is a frequent source of delegation bugs when confused.
- `stopPropagation()` halts an event's journey through capturing/bubbling entirely; `preventDefault()` stops the browser's *default* behavior (form submission, link navigation) without stopping propagation — these solve different problems and are often needed together, not interchangeably.
- 📉 Passive event listeners (`{ passive: true }`) tell the browser upfront "I will never call `preventDefault()`," letting it start scrolling immediately on a separate thread instead of waiting to see if your scroll-listener JS will block it — a meaningful mobile-scroll-performance fix that's easy to forget on touch/wheel listeners.
- `DOMContentLoaded` (HTML parsed, DOM ready) fires much earlier than `window.onload` (every resource — images, iframes — fully loaded); defaulting to `DOMContentLoaded` for script initialization avoids blocking on a slow background image just to attach a click handler.
- `localStorage` (no expiry, ~5-10MB, string-only, never sent to server) vs. `sessionStorage` (cleared on tab close) vs. Cookies (~4KB, automatically sent with every request — the only one of the three actually usable for server-side session auth) is a capacity/persistence/transport trade-off, not just "three ways to store stuff." IndexedDB is the step up for anything gigabyte-scale or structured — an actual async NoSQL database in the browser, the standard storage layer for offline-capable PWAs.
- IntersectionObserver (efficient viewport-entry detection — lazy loading, infinite scroll, scroll-triggered animation — without expensive high-frequency scroll listeners), ResizeObserver (detects an *element's* own size change, not just the window — essential for genuinely responsive components), and MutationObserver (batched, async DOM-change detection, replacing the old synchronous Mutation Events) are the three observer APIs that replaced expensive polling/listener patterns with efficient native primitives.
- CORS (server opts a specific origin in via `Access-Control-Allow-Origin`) is a deliberate security boundary, not a bug to work around — it's exactly what stops a malicious site from silently querying your bank's API using your logged-in session cookie. Complex cross-origin requests (custom headers, non-simple methods) trigger a browser-automatic **Preflight** `OPTIONS` request first, asking permission before sending the real one. JSONP is the legacy, now-obsolete `<script>`-tag workaround CORS fully superseded.
- `fetch()` (Promise-based, cleaner async/await integration, does **not** reject on HTTP error status like 404/500 — only on true network failure) vs. `XMLHttpRequest` (older, event-based, verbose) — a common interview trap is assuming `fetch` treats a 404 as a rejected promise; it doesn't, you must check `response.ok` yourself.
- Custom Elements + Shadow DOM (covered in the HTML section) are equally a JS API surface — `customElements.define()` plus lifecycle hooks like `connectedCallback` are how Web Components become framework-agnostic, reusable UI primitives.

**Senior Perspective:**
- 🏗️ Event Delegation is the pattern that separates "works fine in a demo" from "works at scale" — a data table with 10,000 rows and 10,000 individual click listeners will visibly lag on initial render; one delegated listener on the container won't.
- ⚖️ `fetch` not rejecting on HTTP error codes is a deliberate spec design (network failure and application-level error are different concerns) that costs you an extra `if (!response.ok)` check on every call site — worth building into a shared API-client wrapper once rather than re-litigating it in every component.
- 📉 CORS misconfiguration is one of the most common "why is this broken in production but works locally" tickets — understanding it as a *server-declared trust boundary* rather than a client-side bug to route around is what stops engineers from reaching for dangerous workarounds like disabling browser security.

### Event Delegation, Debounce & Throttle in Code
- The capture/bubble model above in concrete terms: `addEventListener(type, handler)` registers for the bubbling phase by default; passing `true` (or `{ capture: true }`) as the third argument registers for the capturing phase instead, so an ancestor's capturing listener fires *before* the target's own handler. Forgetting that flag is the usual reason a "run this first" listener fires last.
```text
Capturing (3rd arg true):  window → document → grandparent → parent → target
Bubbling (default):        target → parent → grandparent → document → window
```
- Delegation in code — one listener on the container, `e.target` to identify which child was actually hit. It works for `<li>`s added later with no re-binding. Prefer `e.target.closest('li')` over a raw `tagName` check once list items contain nested markup, because a click on a `<span>` inside the `<li>` would otherwise be missed:
```js
document.getElementById('list').addEventListener('click', (e) => {
  const li = e.target.closest('li');
  if (!li) return;
  console.log('Clicked:', li.textContent);
});
```
- Debounce and throttle are conceptually distinguished under Performance, Memory & Engine Internals below. What the source adds is the actual implementation, which is a recurring live-coding ask:
```js
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, delay) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= delay) {
      last = now;
      fn.apply(this, args);
    }
  };
}

input.addEventListener('input', debounce(() => search(input.value), 500));  // fire after typing stops
window.addEventListener('scroll', throttle(onScroll, 1000));                 // fire at most once/second
```
- Debounce's core trick is that every call cancels the pending timer (`clearTimeout`) before scheduling a new one, so `fn` fires only once the caller has gone quiet for a full `delay`. Throttle instead gates on a timestamp, guaranteeing at most one execution per `delay` window however often it's called. They are different mechanisms for different UX intents: debounce for search boxes, resize-end, and input validation; throttle for scroll, `mousemove`, and infinite-scroll position checks. Using a `function` wrapper with `fn.apply(this, args)` (rather than an arrow) preserves `this` when the debounced function is used as a method or a non-arrow event handler.
- Common interview follow-ups to have ready: **leading vs. trailing edge** (this debounce fires on the trailing edge; a leading-edge variant fires immediately, then suppresses), a **`cancel()`** method so a component can clear a pending call on unmount, and the fact that this simple throttle *drops* the final call inside a window. Production versions like lodash's add a trailing call so the last scroll position is never lost.
- Element-selection APIs are worth knowing precisely: `getElementById` returns one element; `getElementsByClassName`/`getElementsByTagName` return **live** `HTMLCollection`s that update as the DOM changes; `querySelector` returns the first CSS-selector match and `querySelectorAll` returns a **static** `NodeList` snapshot. The CSS-selector methods are the modern default because they're more expressive, not because the older ones are deprecated (`getElementById` is still marginally faster for a single id lookup).
- Core mutation APIs, for completeness: `createElement()` + `appendChild()`/`append()` to insert, `removeChild()`/`element.remove()` to delete, `classList.add/remove/toggle()` for styling state, and `setAttribute()` for attributes. The senior-level point is batching: build new nodes inside a `DocumentFragment` (or a single `innerHTML`/`replaceChildren()` call on sanitized content) so the browser reflows once rather than once per inserted node.
- **The DOM as a tree** (Top-20 Q13): the browser parses HTML into a tree of objects that JS can read and change. That's what lets JS add, remove and update elements and makes pages dynamic. *Source note:* the Q13 diagram draws `html`, `head` and `body` as siblings under `document`. The real structure nests them: `document` → `<html>` → `<head>` and `<body>` → `<div>`, `<p>` …, so `document.documentElement` is `<html>` and `document.body.parentNode` is `<html>`.
- **Changing content, attributes, styles and classes**, the notes' toolkit. `textContent` sets plain text and is safe with user input because it never parses HTML. `innerHTML` **parses** its value as HTML, so passing it user input is an XSS hole (see Security below). Prefer `classList` over reassigning `className` or setting many inline `style`s, so styling stays in CSS:
```js
const box = document.querySelector('.box');
box.innerHTML = '<b>Hello QA!</b>';     // parsed as HTML — never with untrusted input
box.textContent = 'Hello QA!';          // literal text — the safe default
box.setAttribute('data-id', '123');     // box.dataset.id === '123'
box.style.color = 'blue';               // inline style (camelCase property names)
box.classList.add('active');
box.classList.remove('hidden');
```
- **Events and forms.** The common event types are `click` (element clicked), `input` (fires on every keystroke or value change), `change` (fires when the value is committed, e.g. on blur or when a select changes), and `submit` (form submitted). A submit handler almost always calls `preventDefault()` to stop the full-page reload and handle the data in JS:
```js
const form = document.querySelector('#myForm');
form.addEventListener('submit', function (e) {
  e.preventDefault();                  // stop the browser's default navigation/reload
  console.log('Form Submitted!');
  const data = new FormData(form);     // e.g. data.get('email')
});
```
- Both decks' delegation examples test the target with `e.target.matches('li')` (Top-20 Q9 logs `'Item clicked: ' + e.target.innerText`). *Source note:* `matches()` only checks the exact element clicked. If the `<li>` contains markup such as `<li><span>Item 2</span></li>`, a click on the span fails the check and is silently ignored. In a Node check with a mocked DOM, `matches('li')` missed the nested-span click and `closest('li')` caught it. That's why the delegation example earlier in this subsection uses `e.target.closest('li')`. The Q9 `e.target &&` guard is harmless but unnecessary, because a dispatched event always has a target.
- The notes' DOM best practices, several covered above: cache element lookups in variables instead of querying inside loops, delegate events, batch DOM writes to avoid excessive reflow and repaint, keep JS, HTML and CSS separate (toggle classes rather than hard-coding styles), and use `querySelector()` for one element and `querySelectorAll()` for many.

**Senior Perspective:**
- 🏗️ Writing debounce/throttle from scratch, live, is a common senior-frontend exercise precisely because it's small enough to finish in ten minutes but touches closures (the shared `timer`/`last`), timers, and `this`/argument forwarding all at once. The leading/trailing-edge follow-up is where the conversation usually separates levels.
- 📉 A live `HTMLCollection` silently changing length mid-loop is a real, hard-to-spot bug class: removing elements inside `for (let i = 0; i < coll.length; i++)` skips every other item as the collection shrinks under you. Converting to a static array first (`Array.from(coll)` or `[...coll]`) is the standard defensive fix.
- 📉 Every listener you add is a listener you own: attaching per-element handlers without delegation, and never calling `removeEventListener` (or using an `AbortController` signal) on teardown, is both the performance problem and the memory-leak problem covered below.

### Web Storage & Cookies in Code
- `localStorage`/`sessionStorage` (already contrasted with cookies under DOM, Events & Browser Platform APIs above) store **strings only**, so anything structured needs `JSON.stringify`/`JSON.parse` at both ends. `getItem` returns `null` for a missing key, and `JSON.parse` throws on corrupted data, so production reads are typically wrapped in `try/catch`. Both APIs are synchronous and run on the main thread, so they should not be used as a hot-path cache:
```js
localStorage.setItem('user', JSON.stringify({ name: 'Abhi' }));
const user = JSON.parse(localStorage.getItem('user') ?? 'null');
localStorage.removeItem('user');
localStorage.clear();                         // wipes everything for this origin

sessionStorage.setItem('draft', 'abc123');    // gone when this tab closes
```
- Cookies (~4KB each) are sent automatically with every matching request. That's why they're the natural fit for server session auth, and also why they're a CSRF surface (see Security, Delivery & Runtime Architecture below). The client-side API is just string assignment; each assignment sets or overwrites *one* cookie, and deletion means expiring it:
```js
document.cookie = `user=Abhi; max-age=${60 * 60 * 24 * 7}; path=/; Secure; SameSite=Lax`;  // set, 7 days
console.log(document.cookie);                                                             // read all as "a=1; b=2"
document.cookie = 'user=; max-age=0; path=/';                                             // delete
```
- 📉 `HttpOnly` (which hides the cookie from JavaScript entirely and is the standard defense against auth-token theft via XSS) can only be set **server-side** through a `Set-Cookie` response header. Writing `HttpOnly` into `document.cookie` does nothing. `Secure` restricts the cookie to HTTPS, and `SameSite=Strict|Lax|None` controls whether it is sent on cross-site requests, which is the browser-level CSRF mitigation layered under anti-CSRF tokens. Never put sensitive data in a readable, non-`HttpOnly` cookie.
- **`localStorage` vs `sessionStorage`**, as Top-20 Q20 frames it (lifetime, scope, use case), with the precise scoping rules added:
```text
                 localStorage                                  sessionStorage
Lifetime         until removed by code or the user              until that tab (or window) is closed; survives reloads
Scope            shared by every tab/window of the same origin  only the tab that wrote it (a duplicated tab gets a copy)
Use case         long-term prefs: theme, language, drafts       temporary per-tab state: wizard step, one-off filters
Cross-tab sync   'storage' event fires in the OTHER tabs        none
```
```js
localStorage.setItem('name', 'Mahesh');    // stored until removed manually
sessionStorage.setItem('user', 'Admin');   // cleared when the tab is closed
```
- *Source note:* Q20 describes localStorage as "permanent" and "shared across tabs". Both need qualifying. It is scoped per **origin** (protocol + host + port), so `http://` and `https://` versions of a site don't share it. Users can clear it, private/incognito windows discard it when they close, and browsers may evict it under storage pressure unless the site calls `navigator.storage.persist()`. Neither storage is a safe place for critical secrets (the notes' own security page says the same), because any script running on the page can read both.

**Senior Perspective:**
- ⚖️ Where to keep an auth token is an architecture decision, not a storage-API detail. In `localStorage` it is readable by any injected script (XSS-exposed, but never auto-sent, so immune to CSRF). In an `HttpOnly; Secure; SameSite` cookie it cannot be stolen by script but is auto-sent, so CSRF needs its own mitigation. No location is free of both threats; you pick the trade-off and defend it.
- 🏗️ Naming which flag stops which threat (`HttpOnly` → XSS token theft, `Secure` → network eavesdropping, `SameSite` → CSRF) turns "use secure cookies" from a platitude into an answer an interviewer can actually probe.

### Performance, Memory & Engine Internals
- Debouncing (wait until the user *stops* triggering an action for X ms, then fire once — search-as-you-type autocomplete) vs. throttling (fire immediately, then rate-limit to at most once per X ms — scroll/resize/mouse-tracking) solve different UX problems and are frequently confused in interviews; picking the wrong one either over-fires network requests or makes an interaction feel laggy.
- 📉 Memory leaks (forgotten timers, detached event listeners, closures holding large objects) are diagnosed with Chrome DevTools Heap Snapshots — take one, perform the suspect action, take another, and compare for objects that keep growing without shrinking; a "sawtooth" pattern in the Performance tab's memory graph is the visual tell.
- Tree Shaking (dead-code elimination at build time, only possible because ES Modules are statically analyzable — unlike CommonJS's dynamic `require()`) and Bundle Splitting (separating rarely-changing "Vendor" code from frequently-changing "App" code so browsers can cache the vendor bundle indefinitely) are the two build-time levers that most directly control real-world load performance.
- Under the hood, V8 (and comparable engines) use Mark-and-Sweep garbage collection (mark everything reachable from global "roots," sweep everything unmarked — correctly handles circular references that naive reference-counting can't), Hidden Classes + Inline Caching (objects with identical property-addition order share an internal "shape," letting repeated property access skip a dictionary lookup entirely), and a JIT compiler that promotes "hot" functions to optimized machine code — but **deoptimizes** back to the slow path the moment a function's actual argument types violate its earlier assumption (e.g., a function tuned for integers suddenly receiving a string). Keeping argument/property types consistent within a hot function isn't superstition — it's a direct lever on whether V8 can keep it optimized.
- Chrome DevTools' Performance tab (flame charts, identifying "Long Tasks" blocking the main thread) and Memory tab (heap snapshots, detached DOM node detection) turn performance work from guesswork into measurement — the senior discipline is profiling before optimizing, not optimizing by intuition.
- The five concrete leak causes worth naming individually rather than saying "memory leaks happen": (1) accidental globals, which are rooted on `window` and never collected (`'use strict'` turns an undeclared assignment into a `ReferenceError`); (2) event listeners that are added and never removed; (3) `setInterval`/`setTimeout` left running after the feature that started them is gone; (4) closures holding large data longer than needed; (5) **detached DOM nodes**, meaning elements removed from the page but still referenced from JS, which keeps the whole subtree alive. The classic repro is an `init()` that runs on every route change:
```js
// ❌ each call stacks ANOTHER listener on the same button; closures pile up
function init() {
  document.getElementById('btn').addEventListener('click', () => console.log('Clicked'));
}

// ✅ one AbortController tears down every listener registered with its signal
const controller = new AbortController();
btn.addEventListener('click', onClick, { signal: controller.signal });
// on teardown / unmount:
controller.abort();
```
- GC is reachability-based: once nothing reachable from a root references an object, it becomes eligible for collection. Setting `user = null` doesn't free memory directly; it drops *one* reference, which only matters if it was the last. Modern mark-and-sweep handles circular references on its own, so "avoid circular references" is legacy advice from the reference-counting era of old IE. The real modern discipline is not letting long-lived structures (caches, global stores, closures, listener registries) accidentally retain short-lived data.
- **Lazy loading** defers a resource until it's needed. For images and iframes it's native with no JS (`<img src="photo.jpg" loading="lazy" alt="…">`); for custom behavior (data-src swapping, loading a widget's data only when scrolled into view), use `IntersectionObserver`, and call `unobserve` once the element has loaded so it doesn't keep firing:
```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.src = entry.target.dataset.src;
      observer.unobserve(entry.target);
    }
  });
}, { rootMargin: '200px' });   // start loading slightly before it scrolls into view
document.querySelectorAll('img[data-src]').forEach((img) => observer.observe(img));
```
- 📉 Never lazy-load the LCP (Largest Contentful Paint) hero image above the fold. It delays the most important paint of the page and is one of the most common self-inflicted Core Web Vitals regressions.
- **Code splitting** applies the same idea to JS: a dynamic `import()` returns a Promise, and bundlers (Vite/webpack/Rollup) emit that module as a separate chunk fetched only when the code path runs. The result is a smaller initial bundle and faster first load. `React.lazy()` and route-level splitting are built on exactly this primitive:
```js
button.addEventListener('click', async () => {
  const { sayHello } = await import('./module.js');   // own chunk, fetched on first click
  sayHello();
});
```
- Tree shaking (above) has two practical preconditions candidates often miss. The code must use ESM `import`/`export` all the way through (a CommonJS dependency in the chain defeats it), and the package must be marked side-effect-free (`"sideEffects": false` in `package.json`), because the bundler cannot safely drop a module whose import might run top-level code.
- A practical performance checklist beyond the items above: batch DOM reads before DOM writes to avoid **layout thrashing** (reading `offsetHeight` between writes forces a synchronous reflow each time); keep individual tasks under ~**50ms**, the Long Task threshold that directly drives INP; animate `transform`/`opacity` in CSS (compositor/GPU-friendly) instead of `top`/`left` in JS; serve correctly sized images in modern formats (WebP/AVIF); and delete unused code rather than relying on the bundler to catch it.

```text
V8 optimization lifecycle:
Function runs repeatedly with consistent argument shapes → JIT compiles to fast machine code
Argument shape changes unexpectedly → Deoptimization → falls back to slow interpreted path
```

**Senior Perspective:**
- ⚖️ Debounce vs. throttle is a UX-intent decision disguised as a technical one — debounce says "I only care about the final state," throttle says "I need steady updates throughout" — picking based on the interaction's actual requirement, not habit, is what separates senior usage from cargo-culting whichever one you remember.
- 📉 V8 deoptimization is invisible without profiling — a function can *look* fine and still be silently running 10x slower than it should because a single call site occasionally passes an unexpected type, which is exactly the kind of bug that only surfaces under a Performance-tab flame chart, not in casual testing.
- 🏗️ Tree shaking only works because ES Modules are statically analyzable — this is a concrete, interview-relevant reason to prefer `import`/`export` over `require()` in any code that ships to a browser bundle, beyond stylistic preference.

### Modern JavaScript & Language Evolution (ES6+)
- ES6 (2015) was the language's biggest single update: `let`/`const`, arrow functions, template literals (backtick interpolation + true multi-line strings, replacing `+`-concatenation), classes, destructuring, Promises, and native modules (`import`/`export`) — module scope is private by default (unlike Global Scope, where anything defined leaks to every script on the page), which alone eliminated a huge class of naming-collision bugs the old Module Pattern (an IIFE returning a public API, the pre-ES6 workaround) and CommonJS (`require`/`module.exports`, synchronous, server-oriented) both had to work around manually.
- Optional chaining (`?.`, short-circuits to `undefined` instead of throwing on a missing intermediate property) and nullish coalescing (`??`, only falls back on `null`/`undefined` — critically, unlike `||`, it does **not** treat `0`/`""`/`false` as "missing") solve two of the most common defensive-coding pain points; spread (`...`, unpacks an iterable) and rest (`...`, packs remaining args/elements into an array) share syntax but do opposite jobs depending on position.
```js
const city = user.address?.city;        // undefined instead of "Cannot read properties of undefined"
user.getProfile?.();                    // optional call — only invoked if the method exists

const qty = 0;
qty || 18;    // 18 — || treats 0 as "missing" and silently overwrites a valid value
qty ?? 18;    // 0  — ?? only falls back on null/undefined
```
- Default parameters (`function greet(name = 'Guest', msg = 'Hello!') {}`) retire the old `name = name || 'Guest'` boilerplate, and they are closer to `??` than to `||` but stricter than both: a default activates **only for `undefined`**. Passing `null` or `0` explicitly does *not* trigger it (`greet(null)` gives `name === null`), which is a frequent point of confusion. Defaults are also evaluated at call time, so `fn(ts = Date.now())` gets a fresh value on every call.
- Template literals (backticks) give `${expression}` interpolation (any expression, e.g. `` `Today is ${new Date().toDateString()}` ``) plus real multi-line strings without `\n` concatenation. Modules follow a simple convention: **named exports** for multiple values (`export const add = …`, imported with braces, rename-safe and tree-shakeable per binding) and **one default export** for a module's main thing (`export default function mul() {}`), imported without braces as `import mul, { add, PI } from './math.js'`. Many teams ban default exports outright, because the importer can name them anything, which hurts grep-ability and automated refactors.
- `Map` (any key type, preserves insertion order, built-in `.size`) beats a plain `Object` for dictionary-style data with non-string or dynamic keys; `WeakMap`/`WeakSet` hold their entries with **weak references**, letting the Garbage Collector reclaim a key (and its associated metadata) the moment nothing else references it — ideal for attaching private metadata to DOM nodes or objects without creating an accidental memory leak.
- `Object.groupBy()`/`Map.groupBy()` (2024) replace manual `.reduce()`-based grouping boilerplate natively; `Set` gained `union`/`intersection`/`difference` methods (2024) for direct set-math without converting to arrays first. `Record`/`Tuple` (deeply immutable, value-compared primitives) and branded/nominal-style patterns address the long-standing "how do I get truly immutable, comparable-by-value data" gap in a structurally-typed, reference-compared language.
- `AbortController`/`AbortSignal` gives a standard way to cancel an in-flight `fetch()` or event listener — critical for avoiding "update a UI that no longer exists" bugs when a user navigates away mid-request. Import Maps let you alias long module paths to short bare-specifier "nicknames" declared once in HTML, so a file-path or version change doesn't require touching every importing file.
- Tagged template literals (parsing a template string through a function before interpolation) are the mechanism underneath `styled-components` and safe-HTML-escaping utilities. Iterator Helpers (`.map()`/`.filter()`/`.take()` directly on generators, 2024/2025) let you stream-transform large or infinite sequences without materializing them into an array first — a direct memory-efficiency win. The Temporal API is the spec-level replacement for the notoriously mutable, timezone-poor legacy `Date` object, providing immutable, timezone-aware date/time handling natively.
- Decorators (`@decorator`, standardized 2024/2025, aspect-oriented class/method annotation) and Signals (fine-grained reactivity primitives underneath Solid.js/Preact/Vue-style frameworks — updates target only the specific DOM nodes that depend on a changed value, bypassing full Virtual DOM diffing) represent where the language and its surrounding frameworks are converging on 2026.
- The Complete Notes' ES6+ page (template literals, object/array destructuring, spread/rest, modules with `export default` for the one main export per file, `?.`, and `??`, which "works only for null or undefined, NOT for 0, "", false, NaN") is covered by the bullets above and by Objects, Arrays & Destructuring Patterns. All of its outputs were checked in Node, for example `const [a, b, ...rest] = [1, 2, 3, 4, 5]` → `1`, `2`, `[3, 4, 5]`, and `0 ?? 100` → `0`.
- **ES2023–ES2025 additions (plus the ES2021–22 staples interviewers still probe)**. Every line below was run in Node 22.18 (V8 12.4):
```js
// ES2023 — change-array-by-copy: non-mutating twins of sort / reverse / splice / arr[i] = v
const nums = [3, 1, 2];
nums.toSorted();              // [1, 2, 3]     nums is still [3, 1, 2]; takes a comparator like sort
nums.toReversed();            // [2, 1, 3]
nums.toSpliced(1, 1, 9, 9);   // [3, 9, 9, 2]
nums.with(0, 7);              // [7, 1, 2]
// ES2023 — search from the end
[1, 2, 3, 4].findLast(n => n % 2);        // 3
[1, 2, 3, 4].findLastIndex(n => n % 2);   // 2   (-1 when nothing matches)

// ES2024 — native grouping
const people = [{ n: 'A', age: 17 }, { n: 'B', age: 30 }, { n: 'C', age: 40 }];
Object.groupBy(people, p => (p.age >= 18 ? 'adult' : 'minor'));
// { minor: [A], adult: [B, C] } — a null-prototype object, keys in first-seen order
Map.groupBy(people, p => p.age > 25);     // Map { false => [A], true => [B, C] } — keys can be any type
// ES2024 — a promise plus its resolve/reject, without the constructor-callback dance
const { promise, resolve, reject } = Promise.withResolvers();
setTimeout(() => resolve('done'), 100);
await promise;                            // 'done'

// ES2025 — Set algebra
const a = new Set([1, 2, 3]), b = new Set([2, 3, 4]);
a.union(b);                  // Set {1, 2, 3, 4}
a.intersection(b);           // Set {2, 3}
a.difference(b);             // Set {1}
a.symmetricDifference(b);    // Set {1, 4}
new Set([2, 3]).isSubsetOf(a);   // true   (also isSupersetOf, isDisjointFrom)
// ES2025 — iterator helpers: lazy map/filter/take on ANY iterator, no intermediate arrays
function* naturals() { let i = 1; while (true) yield i++; }
naturals().filter(n => n % 2).map(n => n * 10).take(3).toArray();   // [10, 30, 50]
// also .drop() .flatMap() .reduce() .some() .every() .find() .forEach(), and Iterator.from(iterable)

// Array.fromAsync — collect an async iterable (or an array of promises) into an array
async function* pages() { yield 1; yield 2; }
await Array.fromAsync(pages());           // [1, 2]

// ES2022 staples
await fetchConfig();                      // top-level await — ES modules only (not CommonJS or classic scripts)
new Error('Config load failed', { cause: err });   // error chaining; the original is on .cause
Object.hasOwn(obj, 'key');                // safer hasOwnProperty (works on Object.create(null) objects)
[1, 2, 3].at(-1);  'hello'.at(-1);        // 3   'o' — negative indexing

// ES2021 — logical assignment (the right side only runs if an assignment will happen)
cfg.retries ||= 3;      // assigns when falsy — careful: replaces a legitimate 0
cfg.timeout ??= 5000;   // assigns only when null/undefined — keeps 0
cfg.on &&= 'yes';       // assigns only when truthy

// structuredClone — a web-platform (HTML) API rather than ECMAScript; all modern browsers and Node 17+
const copy = structuredClone({ d: new Date(0), m: new Map([['k', 1]]) });   // deep copy; keeps Date/Map; handles cycles
structuredClone({ f() {} });   // DataCloneError — functions and DOM nodes can't be cloned
```
- Why these matter in an interview. `toSorted`/`toReversed`/`toSpliced`/`with` finally give arrays immutable updates without spread-and-copy boilerplate, which is exactly what React/Redux state updates need. `Object.groupBy` replaces the hand-written `reduce` grouping. `Promise.withResolvers` removes the "hoist `resolve` out of the executor" pattern used for deferreds and event-to-promise adapters. Iterator helpers make lazy pipelines over generators and `Map.entries()` practical. `structuredClone` has one catch to mention: class instances come back as **plain objects** (their prototype isn't preserved).
- **Status check on items mentioned earlier in this subsection**, checked against Node 22 where possible. **Decorators** are still a Stage 3 proposal, not part of a published ECMAScript edition. `@dec class A {}` is a `SyntaxError` in Node 22, so today you get them through TypeScript 5+ or Babel. The **Record & Tuple** proposal was withdrawn from TC39 in 2025, so don't present it as upcoming. **Temporal** is a Stage 3 proposal that has started shipping in some browsers but isn't in Node 22 (`typeof Temporal === 'undefined'`), so production code still uses a polyfill. The **Set methods**, which browsers shipped in 2024, are formally part of the ES2025 edition. ES2025 also finalised `Promise.try`, `RegExp.escape` and `Float16Array`, but none of them exist in Node 22 (they arrived in later V8 versions). Check your target runtime, or use a polyfill, before relying on them.

**Senior Perspective:**
- ⚖️ `??` over `||` for defaults is a one-character difference with real production consequences — using `||` to default a numeric `quantity` or boolean `enabled` field silently overwrites legitimate `0`/`false` values, a bug class `??` eliminates by design.
- 🏗️ `WeakMap`/`WeakSet` existing at all signals a specific, recurring problem the language needed to solve: attaching metadata to objects (especially DOM nodes) without creating a memory leak that a regular `Map` would guarantee — recognizing that motivation is what separates "I know the syntax" from "I know why to reach for it."
- 👥 Native ES Modules replacing the Module Pattern and CommonJS isn't just a syntax preference — it's what makes tree shaking, static analysis, and cross-runtime portability (browser + Node) possible, which is a concrete architectural argument to bring to a team still debating module systems.

### Security, Delivery & Runtime Architecture
- XSS (attacker-injected script executed in another user's browser, typically via unsanitized user input rendered into the page) is prevented by sanitizing/escaping all user input before render — modern frameworks like React auto-escape text content by default, but a Content Security Policy (CSP header restricting which script sources the browser will trust) is the necessary defense-in-depth layer on top, not a replacement for sanitization.
- CSRF (tricking an already-authenticated user's browser into firing an unwanted request against a site they're logged into, exploiting the browser's automatic cookie-attachment) is mitigated with anti-CSRF tokens — unique secrets that must accompany state-changing requests to prove they originated from the real site's own UI, not a malicious third-party page.
- Subresource Integrity (`integrity` hash attribute on a CDN-hosted script tag) protects against a supply-chain attack where a compromised CDN silently swaps a trusted library for a malicious one — the browser refuses to execute the script if the computed hash doesn't match.
- Polyfill (adds a *missing runtime method* the browser lacks — e.g., `Array.prototype.includes`) vs. Transpiler/Babel (converts *modern syntax* like arrow functions into an older equivalent) solve two different backward-compatibility problems and are typically used together, not interchangeably.
- Hydration is the process where a client framework "wakes up" server-rendered static HTML by attaching event listeners and reconnecting reactive state — the HTML is visually complete but functionally inert until hydration finishes, which is the direct explanation for why an SSR page can look interactive but not respond to the first click for a brief window.
- Service Workers run on a separate thread with no DOM access, acting as a programmable network proxy that intercepts requests and serves from cache — the enabling technology for offline-first PWAs, background sync, and push notifications, communicating with the main thread exclusively via `postMessage()` since they share no memory. Web Workers generally (including Shared Workers, accessible across multiple tabs from the same origin) offload CPU-heavy work off the main thread, keeping the UI responsive during expensive computation — `postMessage()`'s structured-clone semantics (deep-copying data across the boundary) is also the security-relevant mechanism behind safe cross-origin `<iframe>` communication, since the sender must specify a trusted target origin.
- The notes' **security basics** checklist, with the reason behind each item:
  - Never trust user input. **Validate** it (right type, length and format) and **sanitise or escape** it before inserting it into the DOM. `textContent` is safe by construction. If you must render user-supplied HTML, run it through a sanitiser such as DOMPurify (or the Trusted Types / Sanitizer APIs where available). `innerHTML` with raw user input is the textbook DOM-XSS sink. Client-side validation is for UX only, and the server must validate again.
  - Avoid `eval()`, `new Function(string)`, and string arguments to `setTimeout`/`setInterval`. All of them compile arbitrary strings as code, so any attacker-influenced input becomes code execution. They also block engine optimisations and are refused by a strict CSP (no `'unsafe-eval'`).
  - Use **HTTPS** for every request. Without it, tokens and cookies can be read or modified in transit, and `Secure` cookies and many modern APIs (service workers, geolocation, clipboard) require a secure context anyway.
  - Store sensitive data securely and keep critical secrets out of `localStorage`, which any script on the page can read (see the token-storage trade-off under Web Storage & Cookies above). Never ship API secrets in front-end code at all; anything in the bundle is public.

**Senior Perspective:**
- 👥 XSS/CSRF/CSP are the three security topics a senior frontend engineer is expected to own without prompting — a security review or compliance stakeholder will assume you can explain the threat model, not just name the mitigation.
- ⚖️ Service Workers buy you offline capability and instant repeat-load performance at the cost of a genuinely tricky caching-invalidation problem ("how do I ship an update when there's an aggressive cache in the way") — it's a deliberate architectural commitment, not a drop-in performance win.
- 📉 Hydration's "visually done, functionally not" gap is a real, measurable UX cost (Time to Interactive) on SSR sites — recognizing it is what lets you correctly diagnose "the button did nothing when I clicked it immediately after page load" as expected behavior of the architecture, not a bug.

### Clean Code, Naming & Project Structure
- **Clean code**, from the notes' best-practices page: keep functions small and focused on one job; give variables, functions and classes meaningful names; avoid duplication; write self-explanatory code and comment the *why*, not the *what*; keep formatting and indentation consistent. Their "good" example, plus a version with named inputs and no magic numbers:
```js
function calculateTotal(price, tax) {
  const total = price + price * tax;
  return total;
}
calculateTotal(100, 0.18);   // 118

const GST_RATE = 0.18;                                        // named constant instead of a magic number
const totalWithTax = (price, rate = GST_RATE) => price * (1 + rate);
```
- **Naming conventions:**
```text
Kind                     Convention          Examples
Variable / function      camelCase           userName, getUserData()
Class / constructor      PascalCase          UserProfile, UserService
Constant (fixed config)  UPPER_SNAKE_CASE    MAX_RETRY_COUNT, API_BASE_URL
Boolean                  is/has/can/should   isLoggedIn, hasAccess, canEdit
Private class member     #name               #balance
```
- Names should be pronounceable and searchable. Functions are verbs (`fetchOrders`), values are nouns (`orders`), and booleans read as a yes/no question.
- **Folder structure**: keep components, pages, services (API calls), utils, constants and assets separate, use `index.js` as the entry point, and avoid deeply nested folders. The notes' tree:
```text
project/
└── src/
    ├── assets/        images, fonts, static files
    ├── components/    reusable UI pieces
    ├── pages/         route-level screens
    ├── services/      API / data-access code
    ├── utils/         pure helpers
    ├── constants/     config values, enums
    └── index.js       entry point
```
- *Source note:* the notes advise organising files **by feature**, but the tree they show is organised **by type** (components/, services/, utils/). Both are legitimate and they scale differently. By-type is simple for small apps. By-feature (`features/cart/{CartPage, cartService, cartSlice}`) keeps everything for one feature together, so larger teams can own and delete a feature in one place. Many codebases combine the two: feature folders for domain code plus shared `components/` and `utils/`. Be ready to say which you'd choose and why.
- **Code organisation**: follow the single-responsibility principle, group related code, use ES modules (`export`/`import`), keep business logic separate from UI, and write reusable, testable units. The notes' separation-of-concerns example keeps data access in a service module so the component only imports it:
```js
// userService.js
export const getUser = (id) => { /* API call */ };

// userComponent.js
import { getUser } from './userService.js';
```
- **Performance tips** from the same page (avoid unnecessary globals and re-renders, prefer `const`/`let` over `var`, debounce or throttle expensive handlers, lazy-load modules and images, use array methods and `Set`/`Map` for lookups) are covered in depth under Performance, Memory & Engine Internals. Their arrow-function debounce, `const debounce = (fn, delay) => { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); }; }`, works for plain callbacks. However, it doesn't forward `this`, so for methods or non-arrow event handlers use the `function`/`fn.apply(this, args)` version under Event Delegation, Debounce & Throttle in Code.
- **Tooling and habits** (the notes' pro tips and cheat-sheet reminders): lint with **ESLint** and format with **Prettier** so style never comes up in code review; write unit tests for important logic; refactor regularly in small steps; use `const` by default; avoid global variables; prefer `===`; test in every browser you support; and use DevTools for debugging instead of guesswork.

**Senior Perspective:**
- 👥 Conventions only matter if they're enforced by tools rather than by memory. An ESLint + Prettier config, a pre-commit hook and CI checks turn "please follow our naming rules" from a review argument into something automatic. At staff level, the interesting question is how you'd roll that out to an existing codebase without one giant reformat commit that breaks `git blame`.
- ⚖️ Folder structure is a decision about coupling. Choose the layout that keeps things that change together close together. In a growing product that's usually the feature, which is why by-type layouts tend to get reorganised into feature folders once a team passes a handful of engineers.

### Interview Q&A: JavaScript Quick-Fire
- A rapid-revision list of the 20 questions from the "Top 20 JavaScript Interview Questions & Answers" deck, in the deck's order, followed by its bonus slide and the three questions from the Complete Notes' interview page that the Top-20 doesn't cover. Answers are kept short, and each points to the subsection with the full treatment. Every snippet was run in Node, with DOM-only snippets syntax-checked and their logic run against a small mock. Where the deck's own answer was imprecise, the corrected version is given and flagged.

**Q1. What is JavaScript?**
A high-level, dynamically typed language with first-class functions, used to make web pages dynamic and interactive. It runs in the browser and, through Node.js (or Deno/Bun), on servers. The deck calls it a "scripting" language and the notes call it "interpreted". Modern engines interpret first and then JIT-compile hot code (→ V8 Engine & Execution Model).
```js
console.log("Hello, JavaScript!");   // Hello, JavaScript!
```

**Q2. Difference between `var`, `let` and `const`?**
```text
Feature          var                        let                   const
Scope            function                   block                 block
Redeclaration    allowed                    not allowed           not allowed
Reassignment     allowed                    allowed               not allowed
Hoisting         yes, initialised undefined yes, TDZ until line   yes, TDZ until line
```
`const` blocks reassignment of the *binding*, not mutation of the object it points to (→ Scope, Closures & Execution Context).
```js
let age = 25;
const PI = 3.14;
```

**Q3. What is hoisting?**
Before code runs, the engine registers every declaration in its scope during the creation phase. `var` is initialised to `undefined`, function declarations are stored with their body, and `let`/`const`/`class` stay uninitialised in the TDZ. Only declarations are hoisted, not initialisations. *Source note:* the deck says declarations are "moved to the top". Nothing moves (→ the hoisting source note under Scope, Closures & Execution Context).
```js
console.log(a);   // undefined
var a = 10;
```

**Q4. Difference between `==` and `===`?**
`===` compares without coercion (type and value). `==` coerces the operands by the Abstract Equality rules and then compares. *Source note:* the deck's "`==` compares values only" is imprecise, because `[] == []` is `false` and `null == 0` is `false` (→ Types, Coercion & Equality). Always prefer `===`; the one idiomatic exception is `x == null`.
```js
5 == "5";    // true
5 === "5";   // false
```

**Q5. What is a closure?**
A function that keeps access to the variables of the scope it was created in, even after the outer function has returned. It's used for private state, function factories and memoization, and it's also the source of stale-closure bugs and leaks (→ Scope, Closures & Execution Context).
```js
function outer() {
  let count = 0;
  return function () { count++; return count; };
}
const next = outer();
next(); next();   // 1, 2
next();           // 3 — count lives on between calls
```

**Q6. Difference between `null` and `undefined`?**
`undefined` means declared but not assigned (the engine's default). `null` is an intentional "no value" set by the developer. *Source note:* the deck's key point "null is an object" is wrong. `null` is a primitive, and `typeof null === 'object'` is a legacy bug (→ Types, Coercion & Equality).
```js
let a;            // a is undefined
let b = null;     // b is null
typeof a;         // 'undefined'
typeof b;         // 'object' (legacy bug)
a == b;           // true
a === b;          // false
```

**Q7. What is an arrow function?**
A shorter function syntax. It has no `function` keyword, returns implicitly when the body is a single expression, and has no own `this`, `arguments` or `prototype`, so it can't be used with `new`. `this` comes from the enclosing scope, which suits callbacks but not object methods (→ Functions, `this` & Functional Patterns).
```js
const add = (a, b) => a + b;
add(2, 3);   // 5
```

**Q8. What is event bubbling?**
After the event fires on the target, it travels **up** through the ancestors (button → div → body → html → document → window), triggering matching listeners on the way. It's the opposite of the capturing phase, and `e.stopPropagation()` stops it (→ DOM, Events & Browser Platform APIs; Event Delegation, Debounce & Throttle in Code).
```text
body   ↑  third
div    ↑  second
button    target — fires first
```

**Q9. What is event delegation?**
Attaching one listener to a parent to handle events for many children, including children added later, by inspecting `e.target`. The benefits are better performance and less memory. *Source note:* `e.target.matches('li')` misses clicks on markup nested inside the `<li>`; `closest('li')` is the robust check (→ Event Delegation, Debounce & Throttle in Code).
```js
document.getElementById('list').addEventListener('click', function (e) {
  if (e.target && e.target.matches('li')) {                 // deck version
    console.log('Item clicked: ' + e.target.innerText);
  }
});
// robust: const li = e.target.closest('li'); if (li) { … }
```

**Q10. What is a callback function?**
A function passed as an argument to another function, which calls it later. It enables async work (timers, events, older APIs) and reuse. Callbacks aren't inherently async; this one runs synchronously (→ Functions, `this` & Functional Patterns).
```js
function greet(callback) {
  console.log('Hello!');
  callback();
}
greet(function () { console.log('Callback executed'); });
// Hello!
// Callback executed
```

**Q11. What is a Promise?**
An object representing the eventual completion or failure of an async operation. Its states are **pending** → **fulfilled** *or* **rejected**. It settles exactly once, and after that it never changes. *Source note:* the Complete Notes' interview-page diagram chains Pending → Fulfilled → Rejected as if one led to the next; a fulfilled promise can never become rejected (→ The Event Loop & Asynchronous JavaScript).
```js
fetch(url)
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

**Q12. Difference between async/await and Promises?**
`async/await` is syntax on top of Promises. An `async` function always returns a Promise, and `await` pauses that function (resuming it as a microtask) without blocking the thread. The benefits are linear code, ordinary `try/catch` and easier debugging. `.then()` chains are still handy for simple one-off transformations. *Source note:* both of the deck's snippets log the raw **`Response`** object, not the data, because `fetch` resolves to a `Response` that still needs `await res.json()`. Neither checks `res.ok`, and `fetch` doesn't reject on 404/500 (→ Async Patterns in Practice).
```js
// Promise chain
fetch(url).then(res => res.json()).then(data => console.log(data)).catch(err => console.log(err));

// async/await (corrected)
async function getData() {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.log(err);
  }
}
```

**Q13. What is the DOM?**
The Document Object Model is the browser's tree of objects representing the HTML document. JS reads and changes it to add, remove and update elements, which is what makes pages dynamic. *Source note:* in the real tree, `<head>` and `<body>` are children of `<html>`, not its siblings (→ Event Delegation, Debounce & Throttle in Code).
```js
document.getElementById("demo");   // selects the element with id "demo" (or null)
```

**Q14. Difference between `map()` and `forEach()`?**
```text
Feature        map()                          forEach()
Return value   a new array (same length)      undefined
Purpose        transform each element         side effect per element
Use case       you need the new array         you only want to iterate
```
Neither can `break`, and neither awaits async callbacks (→ Objects, Arrays & Destructuring Patterns; Async Patterns in Practice).
```js
const arr = [1, 2, 3];
const doubled = arr.map(x => x * 2);   // [2, 4, 6]
arr.forEach(x => console.log(x));      // 1 2 3 — returns undefined
```

**Q15. What is a higher-order function?**
A function that takes a function as an argument, returns a function, or both. Built-in examples are `map`, `filter`, `reduce`, `forEach` and `sort`. `debounce` and curried functions are examples of HOFs that return functions (→ Functional Patterns: Currying, Memoization & Composition).
```js
function operation(arr, fn) { return arr.map(fn); }
const result = operation([1, 2, 3], x => x * 2);   // [2, 4, 6]
```

**Q16. What is the spread operator?**
`...` expands an iterable into elements, or an object into its properties. It's used for copying and merging, and when merging objects, later keys win. It only makes a **shallow** copy. Rest uses the same `...` syntax to collect items instead (→ Objects, Arrays & Destructuring Patterns).
```js
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4];         // [1, 2, 3, 4]
const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 };    // { a: 1, b: 2, c: 3 }
```

**Q17. What is destructuring?**
A concise way to unpack values from arrays (by position) or objects (by key) into variables. It supports renaming, defaults, skipping and rest (→ Objects, Arrays & Destructuring Patterns).
```js
const person = { name: "John", age: 25 };
const { name, age } = person;      // 'John', 25
const arr = [10, 20, 30];
const [a, b, c] = arr;             // a = 10, b = 20, c = 30
```

**Q18. Difference between `let` and `const`?**
Both are block-scoped, can't be redeclared, and sit in the TDZ until their line. `let` can be reassigned; `const` can't, so use `let` for values that change and `const` for everything else (the recommended default). A `const` object or array can still be mutated.
```js
let count = 1;
count = 2;         // allowed
const PI = 3.14;
PI = 4;            // TypeError: Assignment to constant variable.
const list = [];
list.push(1);      // allowed — mutation, not reassignment
```

**Q19. Difference between `setTimeout()` and `setInterval()`?**
`setTimeout` runs a callback **once** after a delay, and `setInterval` runs it **repeatedly** at a fixed interval. Both return an ID for `clearTimeout`/`clearInterval`, and both delays are *minimums* (they're macrotasks that wait for the call stack and the microtasks). Clear intervals on teardown to avoid leaks. For precise repeated work, a recursive `setTimeout` avoids overlapping runs (→ Async Patterns in Practice).
```js
setTimeout(() => { console.log("Hello"); }, 1000);                  // once, after ≥1s
const id = setInterval(() => { console.log("Hello"); }, 1000);      // every ~1s
clearInterval(id);                                                  // stop it
```

**Q20. Difference between localStorage and sessionStorage?**
localStorage lasts until it's removed and is shared by every tab of the same origin. sessionStorage is cleared when the tab closes and is visible only to that tab. Both store strings only, are synchronous, hold roughly 5–10 MB, and are readable by any script on the page (→ Web Storage & Cookies in Code).
```js
localStorage.setItem("name", "Mahesh");    // stored until manually removed
sessionStorage.setItem("user", "Admin");   // cleared when the tab is closed
```

**Bonus B1. JavaScript data types?**
Primitives: `string`, `number`, `boolean`, `undefined`, `null`, `symbol`, `bigint`. Non-primitive: `object`, a category that includes arrays, functions, dates and regexes (→ the type map under Types, Coercion & Equality).

**Bonus B2. Truthy and falsy values?**
The deck lists 6 falsy values: `false`, `0`, `""`, `null`, `undefined`, `NaN`. Add `-0` and `0n` for the complete list of 8. Everything else is truthy, including `"0"`, `"false"`, `[]`, `{}`, `function () {}` and any non-zero number (→ Types, Coercion & Equality).

**Bonus B3. Array methods cheat sheet?**
`push` adds to the end, `pop` removes the last element, `shift` removes the first, `unshift` adds to the start, `slice(1, 3)` returns a copy of a portion, and `splice(1, 2)` removes or inserts in place. The deck's comments show the array's state; the return values differ (→ Objects, Arrays & Destructuring Patterns).
```js
let arr = [1, 2, 3];
arr.push(4);      // [1, 2, 3, 4]   returns 4 (new length)
arr.pop();        // [1, 2, 3]      returns 4 (removed item)
arr.shift();      // [2, 3]         returns 1 (removed item)
arr.unshift(1);   // [1, 2, 3]      returns 3 (new length)
```

**Bonus B4. How does `this` work?**
Global context: `window` in a classic browser script. Object method: the object before the dot. Plain function: `window` in non-strict mode, `undefined` in strict mode. Arrow function: inherited from the surrounding scope. Event handler (non-arrow): the element the listener is attached to. *Source note:* "global `this` is `window`" holds only in classic browser scripts. It's `undefined` at the top level of an ES module and `module.exports` at the top level of a Node CommonJS file (→ Functions, `this` & Functional Patterns).
```js
const obj = {
  name: "John",
  sayHello: function () { console.log(this.name); },
};
obj.sayHello();   // John
```

**Notes N1. What is the event loop?**
The mechanism that lets single-threaded JS stay non-blocking. When the call stack is empty, it drains **all** microtasks (Promise callbacks), then runs **one** macrotask (timer, I/O, event), then gives the browser a chance to render, and repeats (→ The Event Loop & Asynchronous JavaScript).

**Notes N2. Difference between `call`, `apply` and `bind`?**
`call` and `apply` invoke the function **immediately** with a given `this`; `call` takes the arguments individually and `apply` takes them as an array. `bind` returns a **new function** with `this` (and optionally leading arguments) permanently set (→ Functions, `this` & Functional Patterns).

**Notes N3. What is a prototype?**
An object that other objects inherit properties and methods from through the `[[Prototype]]` link. Lookups walk the chain up to `Object.prototype`, and `class` syntax is built on the same mechanism (→ Prototypes, Objects & OOP Patterns; Classes, Inheritance & the OOP Pillars in Code).

- Answering technique, from both decks' tips: listen to the whole question and ask a clarifying question if it's ambiguous; think out loud and structure the answer (definition → example → trade-off or pitfall); give a real-world example from code you've shipped; explain concepts rather than reciting syntax; and stay calm. When a question asks for output, trace the code step by step out loud instead of guessing.

**Senior Perspective:**
- 🏗️ These 20 questions are screening-level. At senior level, the same questions come back with a follow-up that probes the mechanism: "why does `==` behave like that?", "what does `await` actually schedule?", "why does `matches` miss that click?". The answers above flag the follow-up each question usually gets, and the linked subsections hold the depth.
- 📉 Four of the deck's own answers contain errors (hoisting "moves" code, `==` "compares values only", "null is an object", and Q12's snippets logging a `Response` instead of the data). This is a reminder to verify memorised prep material in a console before relying on it in an interview.

**Predictive Interview Questions (JavaScript):**
1. Walk through exactly what gets logged and in what order for a snippet mixing `console.log`, `setTimeout(fn, 0)`, and a resolved `Promise.then()` — and explain *why* the event loop produces that order, not just what the order is.
2. You're debugging a slow-growing memory leak in a long-running single-page app. Walk through your diagnostic process using Chrome DevTools, and describe two different root causes (one closure-related, one DOM-related) you'd specifically look for.
3. Tell me about a time you had to choose between a callback-based, Promise-based, or async/await-based approach for a piece of asynchronous logic in production — what drove the decision, and what did you trade off (readability, error handling, backward compatibility) to get there?

**Executive Summary Cheat Sheet (JavaScript):** The event loop's strict microtask-before-macrotask ordering, and the reference-vs-value semantics of objects versus primitives, are the two mental models that explain the majority of "surprising" JS behavior — master those and closures, async bugs, and mutation bugs stop being mysterious. Modern JS features (optional chaining, `Map`/`WeakMap`, native modules, Proxies, Signals) each exist to solve a specific, historically painful production problem, and naming that problem is what a staff-level answer sounds like.

## TypeScript

### Type System Fundamentals & Structural Typing
- 🏗️ TypeScript is a strict syntactic superset of JavaScript adding a compile-time, erased type layer — every valid JS file is valid TS, but the reverse isn't true, and critically, browsers **cannot** run TypeScript directly; it must be transpiled (via `tsc`, Babel, esbuild, or SWC) to plain JS first, with all type information stripped away (type erasure) and zero runtime cost or validation.
- `any` disables type checking entirely (an escape hatch, generally avoided in production); `unknown` is its type-safe counterpart — it accepts any value but **blocks all property access and method calls until you explicitly narrow it**, which is the correct default for untyped external data like API responses. `never` represents an impossible code path (used for exhaustiveness checks and functions that always throw); `void` marks the absence of a return value.
- Union types (`|`, an "OR" relationship — ideal for modeling finite state like `"idle" | "loading" | "success" | "error"`) and intersection types (`&`, an "AND" relationship — ideal for composing reusable interfaces, e.g. `Identifiable & Timestamps`) are the two fundamental composition operators every other type-level feature builds on.
- 🏗️ TypeScript's type system is **structural**, not nominal (unlike Java/C++): compatibility is determined entirely by an object's *shape*, not its declared name — two unrelated interfaces with identical properties are freely assignable to each other. This is frequently described as "compile-time duck typing," and it's the single biggest conceptual shift engineers coming from nominally-typed languages need to make.
- Standard arrays (`T[]`/`Array<T>`, dynamic length, homogeneous type) vs. tuples (`[T, U]`, fixed length, per-index typing) matters for structured positional data — React's `useState` return signature is the canonical real-world tuple example.
- `keyof` extracts a union of an object type's property keys as a string/number/symbol literal type — the foundation of generic property-lookup functions (`getProp<T, K extends keyof T>`) and index signature design. The `typeof` keyword operates in two completely separate layers depending on context: at **runtime** it's the familiar JS operator returning a type-name string; in a **type position** it queries and extracts the compile-time TypeScript type of an existing value or function, generating zero runtime code.

**Senior Perspective:**
- 🏗️ TypeScript being structurally typed rather than nominally typed is *the* conceptual fact that explains almost every other TS design decision — declaration merging, `satisfies`, branded types, and duck-typed generic constraints all exist either because of or in spite of structural typing.
- ⚖️ `unknown` over `any` costs you an explicit narrowing step at every consumption site, but that cost is exactly the point — it converts "hope the shape is right" into a compiler-enforced checkpoint, which is why senior teams ban `any` in linting rules and treat `unknown` as the mandatory default for external data.

### Interfaces, Type Aliases & Object Contracts
- `interface` (object-shape contracts, supports declaration merging — multiple same-named interface declarations in scope automatically combine into one, and `extends`) vs. `type` alias (a flexible name for *anything* — primitives, unions, tuples, function signatures — but does **not** support declaration merging; a duplicate `type` name is a compile error). The senior default: `interface` for public library APIs and object-oriented class contracts; `type` for unions, primitives, and advanced mapped/conditional type work.
- Declaration merging extends beyond same-file interfaces into **Module Augmentation** (`declare module "package-name" { ... }`, re-opening a third-party library's types) and **Global Augmentation** (`declare global { ... }` inside a module file, extending native globals like `Window` or `ProcessEnv`) — the standard way to safely add types to code you don't own without forking it.
- Optional properties (`key?: string`, the key itself can be **omitted**) are a different contract than a required-but-possibly-undefined property (`key: string | undefined`, the key **must** be present, but its value can be `undefined`) — the `exactOptionalPropertyTypes` compiler flag makes this distinction strict, rejecting an explicit `undefined` assignment to an optional key.
- Call signatures (describing an object callable like a function, `(param: string): number`) and construct signatures (describing something instantiable with `new`, `new (param: string): TargetClass`) let you type callable objects that also carry attached properties, or factory functions accepting class constructors as arguments.
- `readonly T[]` and `ReadonlyArray<T>` are the exact same type expressed two ways (shorthand vs. generic syntax) — both block `.push()`/`.pop()`/index-assignment; `readonly` can additionally prefix tuple syntax, which `ReadonlyArray` alone cannot express.
- Ambient declaration files (`.d.ts`) carry type metadata with zero runtime JS output, used to describe external code, global variables, or untyped legacy libraries via `declare`. When a third-party package ships no types, the escalation path is: install community `@types/package-name` first, fall back to a bare `declare module "package-name";` (treats all its imports as `any`, unblocks compilation), or author precise local ambient interfaces for the specific methods your app actually uses.
- Namespaces (the legacy "Internal Modules" feature, compiling to IIFE-wrapped global objects) are superseded by native ES Modules in virtually every modern codebase — recognizing them is mostly about not reaching for them in new code.

**Senior Perspective:**
- ⚖️ Choosing `interface` for a public API buys you declaration merging (useful for allowing consumers to extend your types) at the cost of it *not* working for unions or primitives — this is a genuinely load-bearing decision for library authors, not a style preference.
- 🏗️ Module and global augmentation are the sanctioned way to extend types you don't own — recommending a fork of a third-party package's type definitions instead, when augmentation would work, is a signal of unfamiliarity with the pattern.

### Generics & Type-Level Programming
- 🏗️ Generics (`<T>`) let you write logic that's reusable across data types while preserving the *relationship* between input and output types — the canonical example, `identity<T>(arg: T): T`, guarantees the return type exactly matches whatever was passed in, unlike `any` which would discard that relationship entirely.
- Generic constraints (`<T extends { id: string }>`) restrict which types are acceptable, guaranteeing a minimum structural shape so the function body can safely access `.id` — combined with `keyof` (`<K extends keyof T>`) to guarantee a key parameter is actually a valid property name on the object being indexed.
- Conditional types (`T extends U ? X : Y`) are a compile-time ternary — and critically, when `T` is a **naked** generic type parameter instantiated with a union, the conditional **distributes** automatically across each union member (`(A|B) extends U` evaluates as `(A extends U) | (B extends U)`), which is the source of a lot of "why did my conditional type produce a union I didn't expect" confusion. Wrapping both sides in `[T] extends [U]` disables distribution when you need the union treated as one unit.
- `infer` (usable only inside a conditional type's `extends` clause) introduces an inline type variable the compiler extracts automatically — it's the single mechanism powering `ReturnType<T>`, `Parameters<T>`, `Awaited<T>`, and `InstanceType<T>` under the hood, so understanding `infer` is really understanding how *all* of those utility types work.
- Mapped types (`{ [K in keyof T]: ... }`) build new object types by iterating a key union, optionally adding/stripping modifiers (`-readonly`, `-?`); the `as` remapping clause lets you rename, template-literal-transform, or filter keys to `never` (which strips them from the result) — the mechanism for filtering an object's keys down to only those whose *value type* matches a target.
- Template literal types compute every possible string permutation when a union is embedded in a template position — the basis for typed event-name unions (`"onClick" | "onHover"`) or strongly-typed dot-path strings.
- Recursive/self-referential types let you model tree-like or arbitrarily nested structures (JSON values, file-system trees) — bounded ultimately by TypeScript's internal recursion depth limit, which becomes a real practical constraint on deeply nested generic utilities.
- Variance describes how subtyping propagates through compound types: return types are **covariant** (preserve subtype direction), function parameters are **contravariant** under `strictFunctionTypes` (reverse direction), and method-shorthand syntax in interfaces is **bivariant** by default for legacy backward compatibility — a subtle but real correctness gap between two visually similar ways of typing a method.
- 📉 Complex generic/conditional/mapped type chains have a real performance cost: excessive recursion depth or large union permutations can produce "Type instantiation is excessively deep and possibly infinite" errors and measurably slow the IDE and `tsc` — the practical fix is preferring `interface` over `&` intersections for base shapes (interfaces cache property lookups), and breaking monolithic generic expressions into named intermediate types.

**Senior Perspective:**
- 🏗️ `infer` is the one keyword that, once understood, demystifies half of TypeScript's "magic" utility types — `ReturnType`, `Parameters`, `Awaited`, and `InstanceType` aren't special compiler built-ins, they're ordinary conditional types you could write yourself.
- ⚖️ Deep, heavily-recursive generic/mapped-type utilities buy you compile-time correctness for genuinely complex domains, but the cost is real: IDE lag, slower CI type-checks, and cryptic error messages — a senior engineer scopes this kind of type-level programming deliberately, not by default on every utility.
- 📉 Distributive conditional types producing an unexpected union instead of a single type is a recurring "why is my type wrong" debugging session — recognizing distribution as the cause (versus assuming the conditional logic itself is broken) saves real time.

### Utility Types & Practical Type Transformations
- The core utility-type toolkit transforms an existing type without hand-rewriting it: `Partial<T>`/`Required<T>` (all properties optional/required — ideal for PATCH-style update payloads), `Readonly<T>` (immutable properties), `Pick<T, K>`/`Omit<T, K>` (select or drop specific keys — e.g., `Omit`-ing a `passwordHash` field before sending a user object to the client), `Record<K, V>` (a dictionary type that, when `K` is a literal union, **forces every key to be implemented** — exhaustive key-value mapping), `Exclude<T, U>`/`Extract<T, U>` (union difference/intersection), `NonNullable<T>` (strips `null`/`undefined`), and `ReturnType<T>`/`Parameters<T>`/`ConstructorParameters<T>`/`InstanceType<T>` (extract a function or class's signature pieces via `infer`).
- `Awaited<T>` (TS 4.5+) recursively unwraps nested `Promise` layers (`Promise<Promise<string>>` → `string`) and passes non-Promise types through unchanged — essential for extracting the real resolved payload type from async utilities.
- 📉 The most common utility-type pitfall: standard utilities are **shallow**. `Partial<T>`/`Readonly<T>` only touch top-level properties — nested objects remain fully mutable/required unless you author a custom recursive (deep) version. Building `DeepPartial<T>`/`DeepReadonly<T>` requires a recursive mapped type that checks whether each property value is itself an object and, if so, recurses into it.
- Re-implementing `Pick`/`Omit` yourself is a common interview exercise: `MyPick<T, K extends keyof T> = { [P in K]: T[P] }`, and `MyOmit` combines a mapped type with `as`-clause key remapping to `never` for excluded keys — demonstrating you understand the utility types aren't magic, just applied mapped-type mechanics.
- Building a type-safe `Object.keys` wrapper addresses a real gap: native `Object.keys()` returns `string[]`, not `(keyof T)[]`, because JS objects can receive extra runtime properties without violating their declared interface — a cast-based wrapper trades a small amount of unsoundness for meaningfully better autocomplete in controlled contexts.

**Senior Perspective:**
- ⚖️ Reaching for `Partial<T>` to model a form or PATCH payload is convenient, but it silently permits *invalid partial states* where fields that logically must exist together are individually optional — for state with real invariants, a discriminated union usually models the domain more honestly than a blanket `Partial`.
- 🏗️ Being able to re-derive `Pick`/`Omit` from `keyof` + mapped types on the spot (rather than just naming them) is the concrete signal that distinguishes "has used utility types" from "understands the type system they're built on" in a live interview.

### Narrowing, Safety & Modern Guard Patterns
- The non-null assertion operator (`!`) is a compile-time-only directive with **zero runtime effect** — it suppresses the type checker's complaint but does nothing to prevent an actual runtime crash if the value really is `null`/`undefined`. Defensive narrowing (optional chaining `?.`, explicit `if` guards) is strictly safer and should be the default; `!` is a code-review red flag, not a routine tool.
- Type guards narrow a broad type within a conditional branch: `typeof` (primitives), `instanceof` (class instances via the prototype chain), the `in` operator (property-existence check — the standard way to narrow **untagged** object unions that lack a shared discriminator), and user-defined type predicates (`function isX(arg): arg is TargetType`, a custom boolean-returning function the compiler trusts to narrow the caller's branch).
- 🏗️ Discriminated (tagged) unions — variants sharing a common literal "tag" property (`status: "idle" | "loading" | "success" | "error"`) — are the single most important pattern for safely modeling state, because they eliminate impossible intermediate states that independent boolean flags (`isLoading`, `isError` alongside optional `data`) allow by construction. Pairing this with an exhaustive `switch` where the `default` case is assigned to a `never`-typed variable turns "a teammate adds a new state variant and forgets to handle it somewhere" into a **compile-time error** instead of a silent runtime gap — arguably TypeScript's single highest-leverage safety pattern for real product state.
- `any` vs. `unknown` in practice: `any` should be used almost never in production (a temporary escape hatch during JS-to-TS migration at most); `unknown` is the correct default for genuinely unpredictable external data (raw API responses, dynamic third-party payloads), forcing explicit validation before any property access.
- `as const` locks the narrowest possible literal type for an expression (preventing `string` from widening away from `"GET"`), recursively marks object literal properties `readonly`, and turns array literals into fixed `readonly` tuples — all with zero runtime cost. The `satisfies` operator (TS 4.9+) validates that an expression matches a target type **without** widening its inferred type the way a direct type annotation would — you keep the object's exact literal types and full autocomplete while still catching missing-key or wrong-type errors at compile time.
- Branded/nominal types simulate Java/C++-style nominal typing inside TypeScript's structural system by intersecting a primitive with a unique tag property — preventing a `UserId` string from being accidentally accepted where an `OrderId` string was expected, or enforcing that a value has actually passed through runtime validation (`SanitizedHTML` vs. a plain `string`).
- The most common interview-observed mistakes: overusing `any`/`!` as an escape hatch instead of writing a real guard; typing inputs as `object`/`{}` instead of an explicit interface (losing autocomplete); accessing properties on a union/`unknown` before narrowing; confusing when `interface` merging vs. `type` union composition is appropriate; and writing redundant explicit annotations on primitives inference already handles cleanly.

```text
Discriminated union + exhaustive check:
switch (state.status) {
  case "idle": ...
  case "loading": ...
  case "success": ...
  case "error": ...
  default: const _exhaustive: never = state;  // compile error if a variant is ever added and unhandled
}
```

**Senior Perspective:**
- 🏗️ Discriminated unions with `never`-based exhaustiveness checking is the pattern that most directly demonstrates senior-level TypeScript judgment — it converts an entire category of "forgot to handle the new state" production bugs into a build failure, which is a categorically different guarantee than disciplined code review.
- ⚖️ `satisfies` costs nothing (it's purely additive validation) but requires TS 4.9+ and unlearning the habit of reaching for an explicit type annotation, which widens types and loses literal precision — worth actively introducing in code review once the team's TS version supports it.
- 📉 The non-null assertion operator is a compile-time-only lie to the type checker — every `!` in a codebase is a spot where a real runtime crash is possible and the type system has been told to stop watching for it, which is exactly why senior reviewers flag it on sight.

### Classes, OOP & Decorators
- Access modifiers (`public` default, `private` — declaring class only, `protected` — declaring class and subclasses, `readonly` — no reassignment after init) build on ES6 classes with compile-time-enforced visibility; **parameter properties** syntax (`constructor(private readonly capacity: number) {}`) lets you declare and initialize a field in one line inside the constructor signature.
- Numeric enums (auto-incrementing, support reverse value→key lookup at runtime) vs. string enums (must be explicitly initialized, no reverse mapping, but clearer debug logs/serialization) both compile to **real runtime JS objects** — unlike a type alias. The modern-TS nuance: string literal unions (`"RED" | "GREEN" | "BLUE"`) are increasingly preferred over enums specifically because unions compile to **zero** runtime JS, which enums do not.
- Abstract classes (cannot be instantiated with `new`) mix concrete, inherited implementation with `abstract`-prefixed method declarations that subclasses are compiler-forced to implement — a middle ground between a plain class (all concrete) and an interface (zero implementation).
- Method overriding (a subclass replacing a parent's runtime implementation via `extends` + matching signature) is a different mechanism from method overloading (multiple compile-time-only call signatures without bodies, followed by one broad implementation signature that's hidden from callers) — TypeScript's overloading is purely a compile-time typing feature, unlike JS which has no native overloading at all and must branch on `arguments` manually at runtime.
- Mixins simulate multiple inheritance via factory functions that accept a base-class constructor (typed with a `GConstructor<T>` generic constraint) and return an extended inline class — chaining multiple mixins composes an instance type combining every mixin's features without a rigid inheritance tree.
- Decorators (`@decorator`, aligned with the TC39 proposal) apply to classes, methods, accessors, fields, and parameters — enabling aspect-oriented patterns like logging, caching, or access control without repeating the same wrapper logic across every method, and are the mechanism underneath dependency-injection frameworks like NestJS.
- `implements` (forces a class to satisfy an interface's structural contract, supplying **zero** runtime code itself) is fundamentally different from `extends` (inherits real, concrete implementation) — a class can `implements` multiple interfaces simultaneously but can only `extends` one base class.
- `.ts` vs `.tsx` matters specifically for angle-bracket syntax: in `.ts`, `<Type>value` is a legacy type assertion; in `.tsx`, angle brackets are reserved exclusively for JSX parsing, which is why `as Type` is the syntax that works consistently in both file types and is the modern default.

**Senior Perspective:**
- ⚖️ String literal unions over enums is a real, if subtle, modern-TS trade-off: you give up runtime reverse-mapping (rarely needed) in exchange for **zero** added runtime JavaScript — for a large enough enum surface across a codebase, that's a measurable bundle-size difference, not just a style preference.
- 🏗️ Decorators being the mechanism behind dependency injection in frameworks like NestJS is the concrete reason a senior engineer would reach for them rather than a plain factory function — they let cross-cutting concerns (logging, auth, caching) be declared once and applied uniformly instead of manually repeated at every call site.

### Tooling, Config & Project-Scale Architecture
- 🏗️ The `strict` flag in `tsconfig.json` is a master switch bundling `noImplicitAny` (errors when a type can't be inferred and silently defaults to `any`), `strictNullChecks` (forces `null`/`undefined` to be distinct, explicitly-unioned types instead of universally assignable), `strictFunctionTypes` (contravariant parameter checking), `strictPropertyInitialization` (class properties must be initialized), and `noImplicitThis` — enabling it late in a project is dramatically more painful than enabling it from day one, which is why senior teams treat it as non-negotiable for any new codebase.
- `tsc` performs three distinct jobs in one pass: type-checking (reports errors without executing anything), type erasure (strips every annotation/interface/generic, leaving pure JS), and transpilation (downlevels modern syntax to a target JS version) — plus emitting `.js`, `.d.ts`, and `.js.map` outputs. `noEmit` runs type-checking *only*, the standard setup when a separate bundler (esbuild/SWC/Vite) already handles actual compilation.
- Source maps (`.map` files) connect transpiled/minified output back to original `.ts` source — essential for meaningful breakpoints in DevTools and for production error-tracking tools (Sentry-style) to report a crash's *actual* TypeScript file and line, not a mangled bundle position.
- JSX support has five distinct compiler modes (`jsx` config): `preserve` (leaves JSX untouched for a downstream bundler), `react` (legacy `React.createElement` calls), `react-jsx`/`react-jsxdev` (React 17+ automatic transform, no explicit `import React` needed), and `react-native`. Getting this wrong produces either bloated output or a broken build depending on your actual bundler pipeline.
- Migrating an existing JS codebase to TS is explicitly incremental, never a rewrite: initialize with relaxed settings (`allowJs`, `checkJs: false`, `strict: false`) → rename files `.js`→`.ts` starting from leaf utility functions outward to UI components → fix structural errors as they surface → only then progressively harden (`noImplicitAny` → eventually full `strict`). Attempting `strict: true` on day one of a large legacy migration is a common, avoidable cause of migration stalls.
- Best practices at scale: enforce `strict` early, ban `any` in favor of `unknown` paired with a runtime validation library (Zod/ArkType — critically, these can also *infer* the TS type directly from the runtime schema, closing the type-erasure gap where compile-time types provide zero actual runtime protection against untrusted data), use TypeScript Project References (`composite: true`) in monorepos to split large apps into independently-compilable type modules, prefer explicit `import type { ... }` for better bundler tree-shaking and to avoid circular runtime dependencies, and reserve slow `tsc --noEmit` full type-checks for CI while using fast transpilers (esbuild/SWC) for local dev loop speed.
- Triple-slash directives (`/// <reference path="..."/>`, `types="..."`, `lib="..."`) are legacy but still-relevant file-level compiler instructions for including declaration files, ambient type packages, or specific built-in lib definitions (like `"dom"`).
- TypeScript's known limitations are worth being able to name unprompted: zero runtime type checking (type erasure means erased types provide no protection against genuinely untrusted external data unless paired with runtime validation), an added compilation/build step, real learning-curve and boilerplate cost for advanced generics, and gaps when consuming legacy JS packages without published types.

**Senior Perspective:**
- 🏗️ "TypeScript types are erased at compile time and provide zero runtime protection" is the single most important limitation to be able to state unprompted — it's the concrete argument for pairing TS with a runtime validation library (Zod) at every external trust boundary (API responses, form input, `localStorage`), rather than treating the type system as a security net it was never designed to be.
- ⚖️ Enabling `strict` mode late in a mature codebase's life is dramatically more expensive than enabling it on day one — this is a case where the "small, boring" architectural decision made early has compounding leverage, and it's a legitimate thing to push for even against short-term velocity pressure.
- 👥 Framing "ban `any`, require `unknown` + Zod at trust boundaries" as a security/reliability policy — not a style preference — is what gets it adopted as a team linting rule rather than a suggestion people route around.

### Practical Interview Patterns & Async Typing
- Async code is typed via generic `Promise<T>` (`T` is the resolved value's shape); an `async` function automatically wraps its return in `Promise<T>`. In strict mode, an error caught in `try/catch` defaults to `unknown`, not `Error` — forcing an explicit type guard (`error instanceof Error`) before accessing `.message`, which is a frequent source of TS compile errors for engineers used to JS's implicit `any`-typed catch clauses.
- A type-safe event system constrains its `on`/`emit` methods with a generic bounded by `keyof EventMap`, guaranteeing a given event name's payload always matches its declared shape — eliminating an entire class of "wrong payload for this event" bugs that a plain untyped `EventEmitter` allows silently.
- A type-safe fluent builder pattern threads state through the generic type parameter itself: each chained setter method returns a builder re-parameterized with an updated "which fields are set" flag type, so the final `.build()` call can be constrained (via a conditional on `this`) to only compile once every required field has actually been supplied — catching "forgot to call `.setEmail()`" at compile time instead of runtime.
- Deeply nested configuration/theme objects are typed with custom recursive `DeepPartial<T>`/`DeepReadonly<T>` utilities (a conditional mapped type that recurses into any property that's itself an object, skipping functions and primitives) — the standard shape for typing a partial user-theme-override object against a full, strict base theme.
- Common hands-on interview exercises worth being fluent in without notes: implementing a generic `Stack<T>`/`Queue<T>`/`LRUCache<K,V>` with full type safety (an `LRUCache` typically backed by a `Map`, exploiting its insertion-order guarantee for eviction), writing your own `pick`/`omit` helper functions, modeling API loading/success/error state as a discriminated union with exhaustive handling, and writing a generic function that preserves literal types via a `const` type parameter (TS 5.0+) instead of requiring callers to append `as const` manually.

**Senior Perspective:**
- 🏗️ Being asked to implement a generic `LRUCache<K, V>` isn't really testing whether you remember LRU eviction logic — it's testing whether you can express "the cache works correctly for any key/value type combination, and callers get full autocomplete on what they get back," which is the whole point of generics applied to a real data structure.
- ⚖️ A type-driven fluent builder that blocks `.build()` until required fields are set is elegant but adds real generic-type complexity to the codebase — worth it for a config object assembled across many call sites with easy-to-forget required fields, overkill for a three-field constructor.

**Predictive Interview Questions (TypeScript):**
1. Design the type for an API client's response state that must be `idle`, `loading`, `success` (with data), or `error` (with an error object) — and explain why you'd model it as a discriminated union instead of a single interface with optional fields and boolean flags.
2. Walk through what `ReturnType<T>` actually does under the hood using `infer` — then implement a simplified version of it live.
3. You're leading the incremental migration of a large, actively-shipping JavaScript codebase to TypeScript. What's your rollout sequence, how do you decide when to flip on `strict` mode, and how do you keep the team shipping features without the migration stalling out?

**Executive Summary Cheat Sheet (TypeScript):** TypeScript's structural type system, discriminated unions with `never`-based exhaustiveness checks, and the `unknown`-plus-runtime-validation pattern are the three tools that convert entire classes of production bugs into compile-time errors — the senior skill isn't knowing utility-type names, it's knowing when a type-level guarantee is worth its complexity cost versus when it's over-engineering. Remember always: types are fully erased at compile time and provide zero protection against genuinely untrusted runtime data, so every external trust boundary still needs real runtime validation.
