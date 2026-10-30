import re,sys,os,time,hashlib,subprocess,concurrent.futures as cf
RAW,CACHE=sys.argv[1],sys.argv[2]
def locs(s): return re.findall(r'<loc>([^<]+)</loc>',open(f'{RAW}/{s}.sitemap',errors='ignore').read())
jobs=[]
for s,pat in [('navbar.gallery',r'/(navbar|style|type)/'),('footer.design',r'/(sites|types|styles)/'),('cta.gallery',r'/(cta|industry|categories|mode)/'),('3dicons.co',r'/(icons|collection)/'),('scrolltide.co',r'/(templates|components|sections|ui|shaders|free)')]:
    jobs+= [(s,u) for u in locs(s) if re.search(pat,u)]
h=open(f'{RAW}/supahero.io.html',errors='ignore').read()
jobs+= [('supahero.io','https://supahero.io'+p) for p in sorted(set(re.findall(r'href="(/hero/[^"]+)"',h)))]
print('jobs',len(jobs),flush=True)
def fetch(j):
    s,u=j; d=f'{CACHE}/{s}'; os.makedirs(d,exist_ok=True)
    f=f'{d}/{hashlib.sha1(u.encode()).hexdigest()[:16]}.html'
    if os.path.exists(f) and os.path.getsize(f)>500: return 'cached'
    for a in range(3):
        r=subprocess.run(['curl','-sL','-A','Mozilla/5.0 (Macintosh)','--max-time','30','-w','%{http_code}','-o',f,u],capture_output=True,text=True)
        if r.stdout=='200':
            open(f+'.url','w').write(u); time.sleep(0.4); return 'ok'
        time.sleep(3*(a+1))
    return 'fail '+r.stdout+' '+u
with cf.ThreadPoolExecutor(4) as ex:
    for i,res in enumerate(ex.map(fetch,jobs)):
        if res.startswith('fail'): print(res,flush=True)
        if i%200==0: print(i,res,flush=True)
print('done',flush=True)
