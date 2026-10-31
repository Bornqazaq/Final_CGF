from pathlib import Path
import subprocess,json,csv
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[2]
ff=str(r/'.tools/py/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
moments={'lamp':24,'cctv':37,'cctv-reverse':44,'spotlights':56,'alarm':78,'diagnostics':90,'final-beam':193,'safe-opening':197,'victory':201}
for name,t in moments.items():
 subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(r/'deliverables/video/Laser_Vault_Heist_Demo.mp4'),'-frames:v','1',str(r/'evidence/screenshots'/f'{name}.png')],check=True)
canvas=Image.new('RGB',(1440,870),(18,20,24));draw=ImageDraw.Draw(canvas)
for i,(name,t) in enumerate(moments.items()):
 im=Image.open(r/'evidence/screenshots'/f'{name}.png');im.thumbnail((480,270));x=(i%3)*480;y=(i//3)*290;canvas.paste(im,(x,y));draw.text((x+8,y+272),f'{name}: {t}s',fill='white')
canvas.save(r/'evidence/screenshots/demo-contact-sheet.png')
rows=list(csv.DictReader((r/'evidence/demo-gameplay-trace.csv').open()))
for state in ['1','2']:
 found=next((a for a in rows if a['state']==state),None);print('State',state,found)
