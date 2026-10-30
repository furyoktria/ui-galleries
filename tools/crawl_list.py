import sys,os,time,hashlib,subprocess
site,listfile,CACHE=sys.argv[1:4]
d=f'{CACHE}/{site}'; os.makedirs(d,exist_ok=True); n=0
for u in open(listfile).read().split():
    f=f'{d}/{hashlib.sha1(u.encode()).hexdigest()[:16]}.html'
    if os.path.exists(f) and os.path.getsize(f)>500: continue
    r=subprocess.run(['curl','-sL','-A','Mozilla/5.0 (Macintosh)','--max-time','30','-w','%{http_code}','-o',f,u],capture_output=True,text=True)
    if r.stdout=='200': open(f+'.url','w').write(u); n+=1
    else: print('fail',r.stdout,u)
    time.sleep(0.6)
print('done',n)
