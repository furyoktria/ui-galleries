---
name: ui-galleries
description: Searchable fact-only index of 8 UI inspiration galleries — navbar.gallery (navigation bars), footer.design (footers), cta.gallery (calls to action), supahero.io (hero sections), scrolltide.co (scroll/3D templates, components, shaders), 3dicons.co (CC0 3D icons), Refero Styles (link only) and the MIT liquid-glass React component. Use when designing or building a landing page, marketing site or web UI and you need real-world references for a navbar, mega menu, footer, CTA, pricing block, newsletter form, hero section, scroll animation, WebGL/shader background, 3D icon or glass effect; when asked "show me examples of X", "find a dark fintech footer", "which sites have a full-screen menu", "a free 3D wallet icon", or "how do I add liquid glass in React". Not a source of code or prompts to copy.
---

# UI galleries index

This skill gives you real references fast. It indexes item pages from eight
galleries. Each record has only facts: the name, the gallery page, the live
site, and the gallery's own tags. It has no screenshots, prompts, code or
gallery-written descriptions.

## Rules

1. Use the index to find references. Then open the **live site** or the
   **gallery page** to look at the design. Do not say that a design looks a
   certain way if you did not look at it.
2. Do not copy the code, prompts, screenshots or text of these galleries into a
   project. Scrolltide and Supahero sell their content. Refero blocks AI crawlers.
3. Take ideas (layout, pattern, motion type, hierarchy). Build your own version
   with the project's own design tokens.
4. 3dicons.co icons are **CC0**. You can download and ship them. Link the icon
   page so a person can pick the angle and style.
5. liquid-glass is **MIT**. You can install it from npm. See
   `references/liquid-glass.md`.

## Search

```bash
python3 ~/.claude/skills/ui-galleries/scripts/find.py --help
```

Common queries:

```bash
# Mega menus on SaaS sites
find.py --source navbar --tag mega-menu --tag saas
# Dark footers for finance
find.py --source footer --tag dark --tag finance
# Pricing CTAs in dark mode
find.py --source cta --tag pricing --tag dark
# Free scrolltide items only
find.py --source scrolltide --tag free
# WebGL / shader backgrounds
find.py --source scrolltide --kind shader
# A CC0 3D icon
find.py --source 3dicons --q wallet
# Which tags exist for a source
find.py --source footer --facets --limit 60
```

`--tag` is AND. `--any` is OR. `--q` is a substring search over name, URLs and
tags. Add `--json` for machine output.

## Sources and facets

| Source key | Site | What it holds | Main facets |
|---|---|---|---|
| `navbar` | navbar.gallery | Navigation bars | type (mega-menu, dropdown, full-screen, static, side-bar, search-bar, breadcrumbs, progress-bar, tabs), style = site category (saas, ai, studio, finance, …), designed_by |
| `footer` | footer.design | Footers | styles (dark, minimal, animated, bento-box, large-type, …), types = industry, date_added |
| `cta` | cta.gallery | Calls to action | category (button, newsletter, pricing, download, call-to-buy, form, modal-pop-up), industry, mode (light/dark) |
| `hero` | supahero.io | Hero sections | name, live site, date_added |
| `scrolltide` | scrolltide.co | Scroll and 3D templates, components, sections, UI screens, shaders | kind, category, tier (free / paid / pro), tags (three, gsap, canvas, …) |
| `3dicons` | 3dicons.co | CC0 3D icons | tags, styles (clay, color, gradient, premium), angles |
| — | styles.refero.design | Real product styles with DESIGN.md | Link only. robots.txt blocks AI crawlers, so it is not indexed. Open it in a browser yourself. |
| — | glass.samasante.com | liquid-glass React component | `references/liquid-glass.md` |

Item counts and the crawl date are in `data/MANIFEST.json`.

## Workflow for a design task

1. Name the component and the context (for example: "pricing CTA, dark, fintech").
2. Run 1–3 queries. Pick 5–8 references with different approaches.
3. Open the live sites. Note the pattern of each one in one line: layout,
   hierarchy, motion, mobile behaviour.
4. Propose 2–3 directions. Build the chosen one with the project tokens.

## Refresh the data

The crawler and parser are in `tools/`. They read sitemaps, fetch item pages
slowly (4 threads, about 0.4 s apart) and keep facts only. See README.md.
