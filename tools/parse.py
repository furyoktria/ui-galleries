"""Turn cached gallery pages into fact-only JSON. No prompts, code, images or gallery copy."""
import re,os,sys,json,glob,html
CACHE,RAW,OUT=sys.argv[1:4]
os.makedirs(OUT,exist_ok=True)
INFRA=re.compile(r'(website-files\.com|framer(usercontent)?\.com|framer\.link|webflow\.com|googleapis|gstatic|googletagmanager|umami|substack|x\.com|twitter\.com|instagram|linkedin|youtube|dribbble|behance|supabase|r2\.dev|schema\.org|w3\.org|cdn-cgi|supercharged|screensdesign|lemonsqueezy|gumroad|vercel\.com/analytics|webestica|iconstica|plausible|polar\.sh)',re.I)
def pages(site):
    for f in sorted(glob.glob(f'{CACHE}/{site}/*.html')):
        if not os.path.exists(f+'.url'): continue  # fetch still running or failed
        u=open(f+'.url').read().strip()
        yield u,open(f,errors='ignore').read()
def txt(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def title(t):
    m=re.search(r'<title[^>]*>(.*?)</title>',t,re.S); return txt(m.group(1)) if m else ''
def slug(u): return u.rstrip('/').split('/')[-1]
def ext_links(t,own):
    return [x for x in dict.fromkeys(re.findall(r'href="(https?://[^"]+)"',t)) if own not in x and not INFRA.search(x)]
def ldjson(t):
    out=[]
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',t,re.S):
        try: out.append(json.loads(m.group(1)))
        except Exception: pass
    return out
def dump(name,rows):
    rows=sorted(rows,key=lambda r:r.get('slug',''))
    json.dump(rows,open(f'{OUT}/{name}.json','w'),indent=1,ensure_ascii=False)
    print(name,len(rows))

# navbar.gallery
rows=[];tax={'type':{},'style':{}}
for u,t in pages('navbar.gallery'):
    k=u.split('/')[3]
    if k in('type','style'): tax[k][slug(u)]=re.sub(r'\s*[–|-]\s*Navbar Gallery.*','',title(t)); continue
    if k!='navbar': continue
    r={'slug':slug(u),'url':u}
    tt=title(t); m=re.match(r'(.*?)\s+(.+?)\s+Navigation Design',tt)
    h=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S); r['name']=txt(h.group(1)) if h else (m.group(1) if m else tt.split(' – ')[0])
    cats=[]
    for d in ldjson(t):
        for it in (d.get('itemListElement') or []):
            if '/style/' in str(it.get('item','')): r['style']=it.get('name')
        ch=d.get('copyrightHolder')
        if isinstance(ch,dict) and ch.get('url'): r['site_url']=ch['url']
    # item card: "<type link>" then "Website Type" then style
    i=t.find('individual-info'); card=t[i:i+6000] if i>0 else ''
    r['type']=(lambda m:m.group(1).strip() if m else None)(re.search(r'Navbar Type</p>.*?simple-text">([^<]+)<',card,re.S))
    m=re.search(r'Website Type</p><a[^>]*>\s*<div[^>]*>([^<]+)<',card); r['style']=m.group(1).strip() if m else r.get('style')
    m=re.search(r'aria-label="Designed by" href="[^"]*"[^>]*><div[^>]*>([^<]+)<',card); r['designed_by']=m.group(1).strip() if m else None
    if 'site_url' not in r:
        m=re.search(r'href="(https?://[^"]+)"[^>]*>\s*<div>Visit Website',t); r['site_url']=m.group(1) if m else None
    rows.append(r)
dump('navbar-gallery',rows); json.dump(tax,open(f'{OUT}/navbar-gallery.taxonomy.json','w'),indent=1)

# footer.design
rows=[];tax={'types':{},'styles':{}}
for u,t in pages('footer.design'):
    k=u.split('/')[3]
    if k in('types','styles'): tax[k][slug(u)]=title(t).replace('Footer |','').strip(); continue
    if k!='sites': continue
    r={'slug':slug(u),'url':u,'name':title(t).replace('Footer |','').strip()}
    i=t.find('site_hero-bottom'); j=t.find('Date Added',i); blk=t[i:j] if i>0 and j>i else ''
    r['styles']=list(dict.fromkeys(re.findall(r'href="/styles/([a-z0-9-]+)"',blk)))
    r['types']=list(dict.fromkeys(re.findall(r'href="/types/([a-z0-9-]+)"',blk)))
    m=re.search(r'href="(https?://[^"]+)"[^>]*>\s*<div>View Website',t); r['site_url']=m.group(1) if m else None
    m=re.search(r'Date Added</div><div[^>]*>([^<]+)<',t); r['date_added']=m.group(1).strip() if m else None
    m=re.search(r'Designed By</div><div[^>]*>([^<]+)<',t); r['designed_by']=m.group(1).strip() if m else None
    rows.append(r)
# drop the global style list if every row has all styles (menu leak guard)
dump('footer-design',rows); json.dump(tax,open(f'{OUT}/footer-design.taxonomy.json','w'),indent=1)

# cta.gallery
rows=[];tax={'industry':{},'categories':{},'mode':{}}
for u,t in pages('cta.gallery'):
    k=u.split('/')[3]
    if k in tax: tax[k][slug(u)]=title(t).split('|')[0].strip(); continue
    if k!='cta': continue
    r={'slug':slug(u),'url':u,'name':title(t).split('|')[0].strip()}
    i=t.find('View website'); 
    r['industry']=list(dict.fromkeys(re.findall(r'href="\.\./industry/([a-z0-9-]+)"',t)))
    r['mode']=list(dict.fromkeys(re.findall(r'href="\.\./mode/([a-z0-9-]+)"',t)))
    j=t.find('>Category<'); cblk=t[j:j+4000] if j>0 else ''
    r['category']=[c for c in dict.fromkeys(re.findall(r'href="\.\./categories/([a-z0-9-]+)"',cblk)) if c!='all-types']
    # the live-site link is the last outbound href before the "View website" label
    seg=t[max(0,i-4000):i] if i>0 else ''
    near=[x for x in re.findall(r'href="(https?://[^"]+)"',seg) if 'cta.gallery' not in x and not re.search(r'framer(usercontent)?\.com',x)]
    ex=ext_links(t,'cta.gallery'); r['site_url']=near[-1] if near else (ex[0] if ex else None)
    rows.append(r)
dump('cta-gallery',rows); json.dump(tax,open(f'{OUT}/cta-gallery.taxonomy.json','w'),indent=1)

# supahero.io
rows=[]
for u,t in pages('supahero.io'):
    r={'slug':slug(u),'url':u,'name':re.sub(r'\s*Hero Section - Supahero$','',title(t))}
    m=re.search(r'href="(https?://[^"]+)"[^>]*>\s*Visit Website',t) or re.search(r'href="(https?://[^"]+)"[^>]*>[^<]*Visit Website',t)
    ex=ext_links(t,'supahero'); r['site_url']=m.group(1) if m else (ex[0] if ex else None)
    m=re.search(r'((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})',txt(t)); r['date_added']=m.group(1) if m else None
    rows.append(r)
dump('supahero',rows)

# 3dicons.co (CC0)
rows=[];cols={}
for u,t in pages('3dicons.co'):
    k=u.split('/')[3]
    if k=='collection': cols[slug(u)]=title(t).split(' - ')[0]; continue
    if k!='icons': continue
    s=slug(u); r={'slug':s,'url':u,'name':re.sub(r'\s*3d icon - 3dicons$','',title(t),flags=re.I),'license':'CC0'}
    body=txt(re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S))
    m=re.search(r'Edit\s+'+re.escape(r['name'])+r'\s+(.*?)\s+LICENSE',body,re.I); r['tags']=list(dict.fromkeys(m.group(1).lower().split())) if m else []
    r['styles']=sorted(set(re.findall(rf'/sizes/{re.escape(s)}/[a-z-]+/\d+/([a-z]+)\.webp',t)))
    r['angles']=sorted(set(re.findall(rf'/sizes/{re.escape(s)}/([a-z-]+)/\d+/',t)))
    m=re.search(rf'(https://[^"\s]+/sizes/{re.escape(s)}/)',t); r['preview_base']=m.group(1) if m else None
    rows.append(r)
dump('3dicons',rows); json.dump(cols,open(f'{OUT}/3dicons.collections.json','w'),indent=1)

# scrolltide.co: catalog objects from listing + item pages (metadata only)
cat={}
def objs(t):
    t=t.replace('\\"','"')
    for m in re.finditer(r'\{"id":(\d+),"slug":"([^"]+)","name":"([^"]+)","kind":"([^"]+)","category":"([^"]*)"',t):
        seg=t[m.end():m.end()+6000]; nxt=seg.find('{"id":'); seg=seg[:nxt] if nxt>0 else seg
        tier=re.search(r'"minTier":"([a-z]+)"',seg); tags=re.search(r'"tags":\[([^\]]*)\]',seg)
        yield {'id':int(m.group(1)),'slug':m.group(2),'name':m.group(3),'kind':m.group(4),'category':m.group(5),
               'tier':tier.group(1) if tier else None,'tags':re.findall(r'"([^"]+)"',tags.group(1)) if tags else []}
srcs=[open(f,errors='ignore').read() for f in glob.glob(f'{RAW}/st_*.html')]+[t for _,t in pages('scrolltide.co')]
for t in srcs:
    for o in objs(t):
        base={'template':'templates','component':'components','section':'sections','ui':'ui','shader':'shaders'}.get(o['kind'],o['kind'])
        # only templates have their own page; other kinds open in a modal on the listing page
        o['url']=f"https://www.scrolltide.co/{base}/{o['slug']}" if o['kind']=='template' else f"https://www.scrolltide.co/{base}"
        old=cat.get(o['slug'],{}); cat[o['slug']]={**o,**{k:v for k,v in old.items() if v}}
for u,t in pages('scrolltide.co'):
    s=slug(u)
    if '/templates/' in u and s not in cat:
        tt=title(t).replace(' · Scrolltide',''); nm,_,sub=tt.partition(' — ')
        cat[s]={'slug':s,'name':nm,'kind':'template','category':None,'tier':None,'tags':[],'url':u}
    if s in cat and '/templates/' in u:
        b=t.replace('\\"','"')
        if cat[s].get('tier') is None: cat[s]['tier']='premium' if '>Premium<' in t else ('free' if '>Free<' in t else None)
        m=re.search(r'— (Animated|Scroll[- ]driven)?\s*([^·<]{3,90}?) template for ([^·<]{3,80}?) ·',title(t))
        if m: cat[s]['use_case']=m.group(3).strip()
dump('scrolltide',list(cat.values()))
