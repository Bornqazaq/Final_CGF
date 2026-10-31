"""Download project-local build tools and pinned source dependencies from upstream."""
from pathlib import Path
import urllib.request, json, zipfile, shutil, hashlib, concurrent.futures
ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'.tools'
TOOLS.mkdir(exist_ok=True)
def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'LaserVaultHeist-build'})
    with urllib.request.urlopen(req,timeout=90) as r: return json.load(r)
def fetch(url,path):
    if not path.exists():
        print('Downloading',path.name,flush=True)
        req=urllib.request.Request(url,headers={'User-Agent':'LaserVaultHeist-build'})
        with urllib.request.urlopen(req,timeout=180) as r, path.open('wb') as f: shutil.copyfileobj(r,f)
    return path
def unpack(archive,dest,strip=False):
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            parts=Path(member.filename).parts[1:] if strip else Path(member.filename).parts
            if not parts or member.is_dir(): continue
            target=dest.joinpath(*parts).resolve()
            if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe archive path')
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(member) as src, target.open('wb') as dst: shutil.copyfileobj(src,dst)
def tool(repo,pattern,label):
    data=get_json('https://api.github.com/repos/'+repo+'/releases/latest')
    asset=next(a for a in data['assets'] if pattern(a['name']))
    archive=fetch(asset['browser_download_url'],TOOLS/asset['name'])
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if asset.get('digest','').startswith('sha256:') and digest!=asset['digest'].split(':')[1]:
        raise ValueError('Tool checksum mismatch: '+label)
    unpack(archive,TOOLS/label,strip=(label=='llvm'))
    print(label,data['tag_name'],digest,flush=True)
    return {'name':label,'version':data['tag_name'],'url':asset['browser_download_url'],'sha256':digest}
def source(name,repo,ref):
    url=f'https://codeload.github.com/{repo}/zip/{ref}'
    archive=fetch(url,TOOLS/(name+'.zip'))
    unpack(archive,ROOT/'third_party'/name,strip=True)
    return {'name':name,'repository':'https://github.com/'+repo,'ref':ref,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
jobs=[
    ('tool',lambda: tool('mstorsjo/llvm-mingw',lambda n:n.endswith('-ucrt-x86_64.zip'),'llvm')),
    ('tool',lambda: tool('cli/cli',lambda n:n.endswith('windows_amd64.zip'),'gh')),
    ('source',lambda: source('glfw','glfw/glfw','3.4')),
    ('source',lambda: source('glm','g-truc/glm','1.0.1')),
    ('source',lambda: source('imgui','ocornut/imgui','v1.91.9b')),
]
results={'tools':[],'sources':[]}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    futures={pool.submit(fn):kind for kind,fn in jobs}
    for f in concurrent.futures.as_completed(futures): results[futures[f]+'s' if futures[f]=='tool' else 'sources'].append(f.result())
sha=get_json('https://api.github.com/repos/nothings/stb/commits/master')['sha']
stb=ROOT/'third_party'/'stb'; stb.mkdir(exist_ok=True)
for name in ('stb_image.h','stb_image_write.h','LICENSE'):
    fetch(f'https://raw.githubusercontent.com/nothings/stb/{sha}/{name}',stb/name)
results['sources'].append({'name':'stb','repository':'https://github.com/nothings/stb','ref':sha})
(ROOT/'docs'/'dependency-lock.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('Bootstrap finished',flush=True)
