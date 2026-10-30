# ui-galleries

A Claude Code skill plus a fact-only JSON index of eight UI inspiration
galleries. Ask your agent for "a dark fintech footer" or "SaaS sites with a
mega menu". It gets real, live references in one command.

| Source | What | Indexed |
|---|---|---|
| [navbar.gallery](https://www.navbar.gallery) | Navigation bars | every item page |
| [footer.design](https://www.footer.design) | Footers | every item page |
| [cta.gallery](https://www.cta.gallery) | Calls to action | every item page |
| [supahero.io](https://supahero.io) | Hero sections | every item page |
| [scrolltide.co](https://www.scrolltide.co) | Scroll / 3D templates, components, shaders | catalog metadata only |
| [3dicons.co](https://3dicons.co) | CC0 3D icons | every icon page |
| [styles.refero.design](https://styles.refero.design) | Real product styles | link only (its robots.txt blocks AI crawlers) |
| [glass.samasante.com](https://glass.samasante.com) | liquid-glass React component (MIT) | usage notes |

Counts and the crawl date are in [`data/MANIFEST.json`](data/MANIFEST.json).

## What is in the data, and what is not

Each record keeps facts only: the item name, the gallery URL, the live site
URL, and the gallery's own tags (type, style, industry, mode, tier, date).

The repo does **not** contain screenshots, preview videos, prompts, source code
or descriptions written by the galleries. That content belongs to the gallery
owners, and some of it is sold. Use the index to find the page, then visit
the gallery. That is where the work is, and visits help the people who make it.

If you own one of these galleries and want your entry changed or removed,
open an issue.

## Install as a Claude Code skill

```bash
git clone https://github.com/furyoktria/ui-galleries ~/.claude/skills/ui-galleries
```

## Search

```bash
python3 scripts/find.py --source navbar --tag mega-menu --tag saas
python3 scripts/find.py --source footer --tag dark --tag finance --limit 10
python3 scripts/find.py --source cta --tag pricing --tag dark
python3 scripts/find.py --source scrolltide --kind shader
python3 scripts/find.py --source 3dicons --q wallet
python3 scripts/find.py --source footer --facets --limit 60
```

Python 3.8+ only, no dependencies.

## Refresh

`tools/crawl.py` reads each site's sitemap and fetches item pages with
4 threads, about 0.4 s apart, with a local cache. `tools/parse.py` turns the
cache into `data/*.json`. It honours robots.txt: Refero is not crawled, and
3dicons download URLs are not touched.

```bash
python3 tools/crawl.py <raw-dir> <cache-dir>
python3 tools/parse.py <cache-dir> <raw-dir> data
```

`<raw-dir>` holds each site's home page and `sitemap.xml`. The scrolltide
template list comes from `crawl_list.py`.

## License

Code (`scripts/`, `tools/`): MIT. The index lists third-party sites. Names and
trademarks belong to their owners.
