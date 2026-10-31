"""Publish this authorized public project using Git Credential Manager."""
import subprocess, urllib.request, urllib.error, json, os
from pathlib import Path
root=Path(__file__).resolve().parents[2]
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
credential=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\nusername=Bornqazaq\n\n',text=True,capture_output=True,env=env)
if credential.returncode: raise SystemExit('GitHub authentication is unavailable; local work remains intact.')
fields=dict(line.split('=',1) for line in credential.stdout.splitlines() if '=' in line)
token=fields.get('password')
if not token: raise SystemExit('GitHub credential is missing.')
def api(path,body=None):
    req=urllib.request.Request('https://api.github.com'+path,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'LaserVaultHeist-project','X-GitHub-Api-Version':'2022-11-28'})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
user=api('/user')['login']
if user.lower()!='bornqazaq': raise SystemExit('Unexpected GitHub account; publication stopped.')
try:
    existing=api('/repos/'+user+'/laser-vault-heist')
except urllib.error.HTTPError as e:
    if e.code!=404:raise
else:
    raise SystemExit('Repository already exists; inspect before using: '+existing['html_url'])
repo=api('/user/repos',{'name':'laser-vault-heist','description':'Laser Vault Heist — standalone C++17 / OpenGL stealth game. Computer Graphics Fundamentals.','private':False,'auto_init':False})
subprocess.run(['git','remote','add','origin',repo['clone_url']],cwd=root,check=True)
subprocess.run(['git','push','-u','origin','main'],cwd=root,env=env,check=True)
print('Public repository:',repo['html_url'])
