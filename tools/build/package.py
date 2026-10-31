"""Package the verified executable, then assemble a full deliverable ZIP from tracked files."""
from pathlib import Path
import argparse, shutil, zipfile, hashlib, subprocess, json
r=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser();a.add_argument('mode',choices=['portable','complete']);args=a.parse_args()
d=r/'dist';d.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def zipdir(folder,output,prefix):
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(folder.rglob('*')):
   if p.is_file():z.write(p,Path(prefix)/p.relative_to(folder))
if args.mode=='portable':
 out=d/'Windows-x64';out.mkdir(exist_ok=True)
 shutil.copy2(r/'build-clean/LaserVaultHeist.exe',out/'LaserVaultHeist.exe')
 for folder in ['assets','shaders','LICENSES']:
  shutil.copytree(r/folder,out/folder,dirs_exist_ok=True)
 for file in ['README.md','CREDITS.md']:shutil.copy2(r/file,out/file)
 (out/'RUN.txt').write_text('Laser Vault Heist\n\nRun LaserVaultHeist.exe. Keep assets and shaders beside it.\nWindows x64 and an OpenGL 3.3 driver are required.\nEnter: begin; WASD: move; mouse: look; V: first/third person; hold Ctrl/C: crouch; E: interact; Esc: pause; R: retry.\nNo Blender, compiler or network is needed.\n',encoding='utf-8')
 manifest={str(p.relative_to(out)).replace('\\','/'):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
 (out/'SHA256.json').write_text(json.dumps(manifest,indent=2))
 zipdir(out,d/'LaserVaultHeist-Windows-x64.zip','LaserVaultHeist')
 print('Portable archive:',(d/'LaserVaultHeist-Windows-x64.zip').stat().st_size,'bytes')
else:
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=r).decode().split('\0')
 with zipfile.ZipFile(d/'LaserVaultHeist-Complete.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in tracked:
   if name and (r/name).is_file():z.write(r/name,'LaserVaultHeist/'+name)
  for p in sorted((d/'Windows-x64').rglob('*')):
   if p.is_file():z.write(p,'LaserVaultHeist/play/'+p.relative_to(d/'Windows-x64').as_posix())
  video=r/'deliverables/video/Laser_Vault_Heist_Demo.mp4';z.write(video,'LaserVaultHeist/deliverables/video/'+video.name)
 print('Complete archive:',(d/'LaserVaultHeist-Complete.zip').stat().st_size,'bytes')
