"""Record the visible application's real framebuffer at real wall-clock speed."""
from pathlib import Path
import argparse, subprocess, shutil
r=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser();a.add_argument('--ffmpeg',type=Path);args=a.parse_args()
ff=args.ffmpeg or next(iter((r/'.tools/py/Lib/site-packages/imageio_ffmpeg/binaries').glob('ffmpeg*.exe')),None) or shutil.which('ffmpeg')
if not ff:raise SystemExit('Pass --ffmpeg PATH. The encoder is an optional authoring tool, not a game dependency.')
out=r/'deliverables/video/Laser_Vault_Heist_Demo.mp4';out.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([str(r/'build/LaserVaultHeist.exe'),'--root',str(r),'--demo','--1080p','--record',str(out),'--ffmpeg',str(ff)],check=True)
for stem in ['frame-times','gameplay-trace']:
 shutil.copyfile(r/'evidence'/f'{stem}.csv',r/'evidence'/f'demo-{stem}.csv')
print(out)
