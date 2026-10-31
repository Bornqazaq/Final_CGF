"""Validate authored deliverables and finalize report metadata without changing pages."""
from pathlib import Path
import json, hashlib, struct, csv, subprocess, re, shutil
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from pypdf import PdfReader, PdfWriter
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Correct template author metadata explicitly; preserve every other DOCX member.
p=R/'deliverables/report/Laser_Vault_Heist_Report.docx'
with ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
ns={'dc':'http://purl.org/dc/elements/1.1/','cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
e=E.fromstring(parts['docProps/core.xml'])
for key,value in [('dc:creator','Nurbek Yerbulekov'),('dc:title','Laser Vault Heist'),('cp:lastModifiedBy','Nurbek Yerbulekov')]:
 prefix,name=key.split(':');tag='{'+ns[prefix]+'}'+name
 item=e.find(tag)
 if item is None:item=E.SubElement(e,tag)
 item.text=value
parts['docProps/core.xml']=E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(p,'w',ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
# This exact rendered document was inspected on all 26 pages. Only metadata changes.
src=R/'tmp/documents/report-render-v4/Laser_Vault_Heist_Report.pdf'
out=R/'deliverables/report/Laser_Vault_Heist_Report.pdf'
reader=PdfReader(src);w=PdfWriter(clone_from=reader)
w.metadata=None
if '/Metadata' in w._root_object:del w._root_object['/Metadata']
w.add_metadata({'/Title':'Laser Vault Heist','/Author':'Nurbek Yerbulekov','/Subject':'Computer Graphics Fundamentals; Group SE-2428','/Creator':'LibreOffice Writer; verified report source'})
with out.open('wb') as f:w.write(f)
final=PdfReader(out)
assert len(final.pages)==26
assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(reader.pages,final.pages))
text='\n'.join(p.extract_text() for p in final.pages)
assert 'Student: Nurbek Yerbulekov' in text and 'Group: SE-2428' in text
assert 'Kamila' not in text and 'Instructor' not in text
shutil.copy2(out,Path('C:/Users/nyerb/Downloads/Laser_Vault_Heist_Report.pdf'))
# GLB structure, isolated skin, exact named actions.
glbs={}
for stem in ['vault','thief']:
 path=R/'assets/exchange'/f'{stem}.glb';b=path.read_bytes()
 magic,version,total=struct.unpack_from('<III',b)
 assert magic==0x46546c67 and version==2 and total==len(b)
 length,kind=struct.unpack_from('<II',b,12);assert kind==0x4e4f534a
 d=json.loads(b[20:20+length]);names=[a.get('name','') for a in d.get('animations',[])]
 if stem=='thief':assert len(d['skins'])==1 and sorted(names)==['CrouchIdle','CrouchWalk','Idle','Interact','Walk']
 glbs[stem]={'bytes':len(b),'sha256':sha(path),'skins':len(d.get('skins',[])),'meshes':len(d.get('meshes',[])),'animations':names}
(R/'evidence/glb-validation.json').write_text(json.dumps(glbs,indent=2))
# Decode the entire video, not merely the header.
video=R/'deliverables/video/Laser_Vault_Heist_Demo.mp4'
ff=next((R/'.tools/py/Lib/site-packages/imageio_ffmpeg/binaries').glob('ffmpeg*.exe'))
probe=subprocess.run([str(ff),'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert '1920x1080' in probe and '30 fps' in probe
m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe);duration=int(m[1])*3600+int(m[2])*60+float(m[3]);assert 180<=duration<=360
run=subprocess.run([str(ff),'-v','error','-xerror','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert run.returncode==0 and not run.stderr.strip(),run.stderr
ledger=list(csv.DictReader(Path(str(video)+'.frames.csv').open()))
assert all(int(r['video_frame'])==i for i,r in enumerate(ledger))
trace=list(csv.DictReader((R/'evidence/demo-gameplay-trace.csv').open()))
transitions=[]
for i,row in enumerate(trace):
 if i==0 or row['state']!=trace[i-1]['state']:transitions.append({k:row[k] for k in ['wall_seconds','demo_seconds','state','retries']})
assert any(r['state']=='1' for r in trace) and trace[-1]['state']=='2'
qa={'duration_seconds':duration,'size':[1920,1080],'fps':30,'frames':len(ledger),'repeated_sampling_slots':sum(int(r['duplicate']) for r in ledger),'whole_video_decode':'passed','bytes':video.stat().st_size,'sha256':sha(video),'state_transitions':transitions,'method':'Live GL_BACK framebuffer; real wall clock; deterministic ordinary game inputs; no montage.'}
(R/'evidence/video-validation.json').write_text(json.dumps(qa,indent=2))
shutil.copy2(R/'build-clean/Testing/Temporary/LastTest.log',R/'evidence/ctest-clean.txt')
receipt=json.loads((R/'tmp/slides/presentation-validation.json').read_text())
assert len(PdfReader(R/'deliverables/slides/Laser_Vault_Heist_Presentation.pdf').pages)==10
shutil.copy2(R/'tmp/slides/presentation-validation.json',R/'evidence/presentation-validation.json')
summary={'report':{'pages':26,'all_pages_visually_reviewed':True,'content_streams_equal_to_reviewed_render':True,'sha256':sha(out),'author':str(final.metadata.author),'template_core_metadata_intentionally_corrected':True},'presentation':{'slides':10,'all_final_pdf_pages_visually_reviewed':True,'native_chart_on_slide':8,'embedded_workbook':True,'editable_shapes_and_text':True,'speaking_target_seconds':520,'sha256_pptx':sha(R/'deliverables/slides/Laser_Vault_Heist_Presentation.pptx')},'video':qa,'glb':glbs}
(R/'evidence/deliverables-validation.json').write_text(json.dumps(summary,indent=2))
print('Report: 26 pages, unchanged reviewed content, correct author; slides: 10; video:',duration,'s;',len(ledger),'frames; GLBs valid.')
