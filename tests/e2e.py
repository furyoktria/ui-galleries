#!/usr/bin/env python3
"""End-to-end check of the published skill.

Clones the repo from GitHub into a fresh fake HOME, installs it as a skill,
runs real design queries through scripts/find.py, and checks the answers
against the live web. Writes tests/e2e-report.md and tests/e2e-report.json.

Usage: python3 tests/e2e.py [repo-url]
"""
import json, os, random, subprocess, sys, tempfile, time, urllib.parse

REPO = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/furyoktria/ui-galleries"
HERE = os.path.dirname(os.path.abspath(__file__))
FORBIDDEN = {"prompt", "promptContent", "code", "codeContent", "description", "image",
             "posterImage", "previewVideo", "screenshot", "sourceCodeFileUrl"}
results, failures = [], []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    if not ok:
        failures.append(name)
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""), flush=True)


def http_status(url):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-A",
                        "Mozilla/5.0 (Macintosh)", "-w", "%{http_code}", url], capture_output=True, text=True)
    return r.stdout.strip()


home = tempfile.mkdtemp(prefix="ui-galleries-e2e-")
skill = os.path.join(home, ".claude", "skills", "ui-galleries")
r = subprocess.run(["git", "clone", "--depth", "1", "-q", REPO, skill], capture_output=True, text=True)
check("clone public repo into fresh HOME", r.returncode == 0, r.stderr.strip()[:200])
if r.returncode:
    sys.exit(1)

# The skill must be loadable: frontmatter with name + description.
head = open(os.path.join(skill, "SKILL.md")).read().split("---")
fm = head[1] if len(head) > 2 else ""
check("SKILL.md frontmatter has name and description", "name: ui-galleries" in fm and "description:" in fm)

find = [sys.executable, "-I", os.path.join(skill, "scripts", "find.py")]


def q(*args):
    out = subprocess.run(find + list(args) + ["--json", "--limit", "500"], capture_output=True, text=True,
                         env={**os.environ, "HOME": home})
    if out.returncode:
        raise RuntimeError(out.stderr)
    return json.loads(out.stdout)


# Data integrity across every source.
man = json.load(open(os.path.join(skill, "data", "MANIFEST.json")))
for src, meta in man["sources"].items():
    rows = json.load(open(os.path.join(skill, "data", meta["file"])))
    check(f"{src}: row count matches manifest ({meta['items']})", len(rows) == meta["items"])
    bad = [r.get("slug") for r in rows if FORBIDDEN & set(r)]
    check(f"{src}: no forbidden fields (prompts, code, images, descriptions)", not bad, str(bad[:5]))
    dup = len(rows) - len({r["url"] for r in rows})
    check(f"{src}: gallery URLs unique", dup == 0, f"{dup} duplicates")
    if meta.get("min_expected"):
        check(f"{src}: at least {meta['min_expected']} items", len(rows) >= meta["min_expected"], str(len(rows)))

# Realistic design briefs, each with 2+ facets. Not the easy single-tag case.
briefs = [
    ("SaaS site with a mega menu", ["--source", "navbar", "--tag", "mega-menu", "--tag", "saas"], 3),
    ("dark, animated footer", ["--source", "footer", "--tag", "dark", "--tag", "animated"], 3),
    ("dark-mode pricing CTA", ["--source", "cta", "--tag", "pricing", "--tag", "dark"], 1),
    ("free scrolltide items only", ["--source", "scrolltide", "--tag", "free"], 3),
    ("three.js-based scrolltide shader or component", ["--source", "scrolltide", "--any", "shader", "--any", "component", "--tag", "three"], 1),
    ("CC0 3D icon about money", ["--source", "3dicons", "--any", "wallet", "--any", "money", "--any", "dollar", "--any", "coin"], 1),
    ("hero sections, keyword 'ai'", ["--source", "hero", "--q", "ai"], 1),
    ("cross-source: anything tagged finance", ["--q", "finance"], 5),
]
sampled = []
for label, args, min_n in briefs:
    res = q(*args)
    check(f"brief '{label}' returns >= {min_n}", res["total"] >= min_n, f"{res['total']} hits")
    # The facets asked for must really be on every hit.
    tags = [args[i + 1] for i, a in enumerate(args) if a == "--tag"]
    wrong = [i["name"] for i in res["items"] if not all(t in i["tags"] for t in tags)]
    check(f"brief '{label}': every hit carries the AND tags", not wrong, str(wrong[:3]))
    random.seed(label)
    sampled += random.sample(res["items"], min(2, len(res["items"])))

# Live web: the references must lead somewhere real.
live_ok = 0
rows_out = []
for it in sampled:
    g = http_status(it["url"])
    s = http_status(it["site_url"]) if it.get("site_url") else "-"
    rows_out.append((it["source"], it["name"], g, s, it["url"], it.get("site_url")))
    live_ok += g.startswith(("2", "3"))
    time.sleep(0.5)
check("sampled gallery pages respond 2xx/3xx", live_ok == len(sampled), f"{live_ok}/{len(sampled)}")
site_codes = [r[3] for r in rows_out if r[3] != "-"]
site_ok = sum(c.startswith(("2", "3")) for c in site_codes)
# Third-party live sites move or block bots; demand a strong majority, report the rest.
check("sampled live sites mostly respond (>= 70%)", site_codes and site_ok / len(site_codes) >= 0.7,
      f"{site_ok}/{len(site_codes)}")

# liquid-glass reference must match npm.
npm = json.loads(subprocess.run(["curl", "-s", "https://registry.npmjs.org/@samasante/liquid-glass/latest"],
                                capture_output=True, text=True).stdout or "{}")
check("liquid-glass is MIT on npm", npm.get("license") == "MIT", npm.get("version", ""))

stamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
json.dump({"when": stamp, "repo": REPO, "results": results, "samples": rows_out},
          open(os.path.join(HERE, "e2e-report.json"), "w"), indent=1)
with open(os.path.join(HERE, "e2e-report.md"), "w") as f:
    f.write(f"# E2E report\n\n- When: {stamp}\n- Repo: {REPO}\n- Result: "
            f"{'PASS' if not failures else 'FAIL'} ({len(results) - len(failures)}/{len(results)} checks)\n\n")
    f.write("| check | result | detail |\n|---|---|---|\n")
    for r in results:
        f.write(f"| {r['check']} | {'pass' if r['ok'] else '**FAIL**'} | {r['detail']} |\n")
    f.write("\n## Sampled references (HTTP status)\n\n| source | name | gallery | live site |\n|---|---|---|---|\n")
    for s, n, g, c, gu, su in rows_out:
        f.write(f"| {s} | {n} | [{g}]({gu}) | {'[' + c + '](' + su + ')' if su else '-'} |\n")
print("\nRESULT", "PASS" if not failures else "FAIL", f"{len(results) - len(failures)}/{len(results)}")
sys.exit(1 if failures else 0)
