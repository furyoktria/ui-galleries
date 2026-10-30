#!/usr/bin/env python3
"""Search the gallery index.

Examples:
  find.py --source navbar --tag mega-menu --tag saas
  find.py --source footer --tag dark --tag fintech --limit 10
  find.py --source cta --tag pricing --tag dark
  find.py --source scrolltide --kind shader
  find.py --source 3dicons --q wallet
  find.py --q "finance" --json
"""
import argparse, json, os, re, sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SOURCES = {
    "navbar": "navbar-gallery.json",
    "footer": "footer-design.json",
    "cta": "cta-gallery.json",
    "hero": "supahero.json",
    "scrolltide": "scrolltide.json",
    "3dicons": "3dicons.json",
}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def tags_of(src, r):
    """Flatten every facet of a record into one tag list."""
    t = []
    for k in ("type", "style", "styles", "types", "industry", "mode", "category",
              "kind", "tier", "tags", "angles"):
        v = r.get(k)
        if isinstance(v, list):
            t += v
        elif v:
            t.append(v)
    return sorted({norm(x) for x in t if x})


def load(sources):
    out = []
    for src in sources:
        path = os.path.join(DATA, SOURCES[src])
        if not os.path.exists(path):
            continue
        for r in json.load(open(path)):
            out.append({"source": src, "name": r.get("name"), "url": r.get("url"),
                        "site_url": r.get("site_url"), "tags": tags_of(src, r)})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", action="append", choices=sorted(SOURCES))
    p.add_argument("--tag", action="append", default=[], help="all tags must match (repeatable)")
    p.add_argument("--any", action="append", default=[], help="at least one of these tags must match")
    p.add_argument("--kind", help="scrolltide kind: template, component, section, ui, shader")
    p.add_argument("--q", help="substring of name, url or tag")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--json", action="store_true")
    p.add_argument("--facets", action="store_true", help="list tag counts instead of items")
    a = p.parse_args()

    rows = load(a.source or sorted(SOURCES))
    want = [norm(t) for t in a.tag]
    anyw = [norm(t) for t in a.any]
    if a.kind:
        want.append(norm(a.kind))
    rows = [r for r in rows if all(w in r["tags"] for w in want)]
    if anyw:
        rows = [r for r in rows if any(w in r["tags"] for w in anyw)]
    if a.q:
        q = a.q.lower()
        rows = [r for r in rows if q in " ".join([str(r["name"]), str(r["url"]), str(r["site_url"]), *r["tags"]]).lower()]

    if a.facets:
        from collections import Counter
        c = Counter(t for r in rows for t in r["tags"])
        for t, n in c.most_common(a.limit):
            print(f"{n:5}  {t}")
        return
    total = len(rows)
    rows = rows[: a.limit]
    if a.json:
        json.dump({"total": total, "items": rows}, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return
    print(f"{total} match(es), showing {len(rows)}\n")
    print("| source | name | live site | gallery page | tags |")
    print("|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['source']} | {r['name']} | {r['site_url'] or '-'} | {r['url']} | {', '.join(r['tags'][:8])} |")


if __name__ == "__main__":
    main()
