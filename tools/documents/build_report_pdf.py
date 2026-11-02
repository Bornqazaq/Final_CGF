"""Build the current project report from captured evidence and retained course sections."""
from pathlib import Path
import json, re, hashlib
from xml.sax.saxutils import escape
from reportlab.platypus import (BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from pypdf import PdfReader,PdfWriter

import sys
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
WORK=ROOT/'tmp/report-refresh';WORK.mkdir(parents=True,exist_ok=True)
SHOTS=WORK/'screenshots' if (WORK/'screenshots').exists() else ROOT/'evidence/screenshots/report-current'
OUT=WORK/'Laser_Vault_Heist_Report.pdf'
NAMES='Nurbek Yerbulekov, Makhmet Demesh, Nurassyl Nygmet'
for name,file in [('Times','times.ttf'),('Times-Bold','timesbd.ttf'),('Times-Italic','timesi.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Times',normal='Times',bold='Times-Bold',italic='Times-Italic',boldItalic='Times-Bold')
PAGE=(7560310/12700,10692130/12700);LEFT=1080135/12700;RIGHT=539750/12700;TOP=720090/12700;WIDTH=PAGE[0]-LEFT-RIGHT
styles={
 'body':ParagraphStyle('Body',fontName='Times',fontSize=14,leading=17.5,spaceAfter=8),
 'h1':ParagraphStyle('Chapter',fontName='Times-Bold',fontSize=18,leading=22,spaceAfter=13,keepWithNext=True),
 'h2':ParagraphStyle('Section',fontName='Times-Bold',fontSize=15,leading=19,spaceBefore=10,spaceAfter=8,keepWithNext=True),
 'caption':ParagraphStyle('Caption',fontName='Times-Italic',fontSize=12,leading=15,spaceAfter=10),
 'table':ParagraphStyle('Table',fontName='Times',fontSize=12,leading=14.5,spaceAfter=0),
 'title':ParagraphStyle('Title',fontName='Times-Bold',fontSize=24,leading=29,alignment=1,spaceAfter=18),
 'cover':ParagraphStyle('Cover',fontName='Times',fontSize=14,leading=20,alignment=1,spaceAfter=10),
 'equation':ParagraphStyle('Equation',fontName='Times',fontSize=14,leading=19,spaceAfter=10,leftIndent=12),
}
def clean(t):
 return t.replace('\u2011','-').replace('\u2010','-').replace('\u2013','-').replace('\u2014','-').replace('\u2018',"'").replace('\u2019',"'")
def P(t,style='body'):
 para=Paragraph(escape(clean(str(t))).replace('\n','<br/>'),styles[style])
 return KeepTogether([para]) if style=='equation' else para
class Report(BaseDocTemplate):
 def __init__(self,path):
  super().__init__(str(path),pagesize=PAGE,leftMargin=LEFT,rightMargin=RIGHT,topMargin=TOP,bottomMargin=TOP,title='Laser Vault Heist',author=NAMES)
  f=Frame(LEFT,TOP,WIDTH,PAGE[1]-2*TOP,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
  self.addPageTemplates(PageTemplate(id='Report',frames=f,onPage=self.furniture))
 def furniture(self,c,d):
  c.saveState();c.setFont('Times',10)
  if d.page>1:c.drawString(LEFT,PAGE[1]-34,'Laser Vault Heist | Computer Graphics Fundamentals')
  c.drawCentredString(PAGE[0]/2,32,str(d.page));c.restoreState()
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name in ('Chapter','Section'):
   level=0 if f.style.name=='Chapter' else 1
   key='section-'+str(self.page)+'-'+str(hash(f.getPlainText()))
   self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,level=level,closed=False)
   if f.getPlainText()!='Table of Contents':self.notify('TOCEntry',(level,f.getPlainText(),self.page,key))
story=[];figures=[]
def para(t):story.append(P(t))
def h(t,chapter=False):
 if chapter:story.append(PageBreak())
 story.append(P(t,'h1' if chapter else 'h2'))
def table(headers,rows,weights):
 data=[[P(x,'table') for x in headers]]+[[P(x,'table') for x in row] for row in rows]
 widths=[WIDTH*w/sum(weights) for w in weights]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf0f2')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#7d8589')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d0d4d6')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 block=[t]
 if len(rows)<=4 and story and isinstance(story[-1],Paragraph) and story[-1].style.name=='Section':block.insert(0,story.pop())
 story.extend([KeepTogether(block) if len(rows)<=4 else t,Spacer(1,10)])
def figure(name,caption,width=WIDTH):
 p=SHOTS/(name+'.png');im=PILImage.open(p);height=width*im.height/im.width
 num=len(figures)+1;figures.append({'number':num,'file':p.name,'caption':caption})
 block=[Image(str(p),width=width,height=height),Spacer(1,5),P(f'Figure {num}. {caption}','caption')]
 if story and isinstance(story[-1],Paragraph) and story[-1].style.name=='Section':block.insert(0,story.pop())
 story.append(KeepTogether(block))
 return num
refs=json.loads((ROOT/'docs/references-verified.json').read_text(encoding='utf-8'))
benchfile=WORK/'benchmarks/summary.json' if (WORK/'benchmarks/summary.json').exists() else ROOT/'evidence/benchmarks-current/summary.json'
bench=json.loads(benchfile.read_text())
rankings=json.loads((ROOT/'evidence/source-audit.json').read_text())['journal_rankings']

# Cover retains the supplied template logo, page geometry and black Times typography.
logo=ROOT/'tmp/documents/image1.png'
logoFlow=Image(str(logo),width=223,height=223*PILImage.open(logo).height/PILImage.open(logo).width) if logo.exists() else P('ASTANA IT UNIVERSITY','title')
story.extend([Spacer(1,25),logoFlow,Spacer(1,95),P('Laser Vault Heist','title'),P('Computer Graphics Fundamentals','cover'),P('Final Project Report','cover'),P('Students: '+NAMES,'cover'),P('Group: SE-2428','cover'),Spacer(1,25),P('Topic 12\nC++17 and OpenGL 3.3 Core','cover')])
story.extend([PageBreak(),P('Table of Contents','h1')])
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('Toc0',fontName='Times',fontSize=14,leading=19,spaceBefore=7),ParagraphStyle('Toc1',fontName='Times',fontSize=12,leading=16,leftIndent=14,spaceBefore=3)];story.append(toc)

h('1 Introduction',True)
para('Laser Vault Heist is a real-time 3D stealth game built around a mansion vault. The player observes six moving laser barriers, walks or crouches through the room and opens a mechanical safe. Touching a beam triggers a red alarm and a retry. The completed version adds first- and third-person cameras, a locked entrance corridor, a skinned thief and a one-shot dance finale. The application renders through its own OpenGL pipeline rather than a game engine.')
n=figure('room','Current vault rendered by the application, with textured furniture, lasers and live CCTV')
para(f'Figure {n} shows the current room rather than the earlier prototype. The project brings together indexed geometry, model/view/projection transformations, hierarchical animation, per-fragment lighting, texture sampling and interactive state changes. These systems have to agree: a laser must collide where it is drawn, crouching must fit the visible character, and a camera must not look through a wall.')
para('This report follows the supplied course template. It compares graphics methods with eighteen journal articles, explains the implemented algorithms, and presents new captures and measurements from the current Windows executable. Tests and local measurements support the engineering claims; performance on the unknown TA machine and a live oral defense remain separate checks.')
h('1.1 Team responsibilities')
table(['Student','Responsibility'],[['Nurbek Yerbulekov','Project lead: game design, visual direction, models, animation and visual integration.'],['Makhmet Demesh','Gameplay mechanics: laser contact, progression and game states; rendering and technical integration.'],['Nurassyl Nygmet','Gameplay mechanics: controls and interactions; testing, build verification and documentation.']],[1.65,3.8])
para('The visual pipeline and gameplay systems were developed together: the character proportions, animation poses, hazard clearance and state feedback had to remain consistent. Each team member should be prepared to explain the complete project as well as their assigned area.')

h('2 Literature Review and Background')
para('The review uses eighteen journal articles with DOI records retained in docs/references-verified.json. Sixteen remain after excluding the two Communications of the ACM entries. The accompanying source audit records the journal categories and public reproductions of SJR 2025 quartiles. Those rankings describe journals in that ranking year, not the historical quartile of every publication. Direct access to SCImago and Scopus was unavailable during the recorded audit, so direct verification of their databases is not claimed.')
table(['Journal','Recorded SJR category / quartile'],[[j,r['category']+'; '+r['quartile']] for j,r in rankings.items()],[2.4,3.5])
comparisons={
5:'The runtime keeps at most four normalized influences per vertex and a compact matrix palette. It imports the supplied skin weights and validates them rather than fitting them with this optimization.',
6:'Weight non-negativity and normalization are checked during export. The supplied skeleton is retained; no joint/weight recovery algorithm is implemented.',
18:'The current model has 52 weighted bones plus required ancestors, within the 64-matrix shader palette. No automatic discovery of bones or reconstruction of mesh sequences is performed.',
17:'The project separates editable Blender resources from sampled local transforms and indexed runtime meshes. The supplied rig and derived clips are exported directly rather than fitted from a physically simulated character.',
15:'Seeded environment textures are generated offline, while the thief uses the supplied base-color image. Neither uses this paper\'s neighborhood-matching synthesis at runtime.'}
groups=[('2.1 Lighting and material response',[1,2,3]),('2.2 Skinning and motion representation',[4,5,6,16,17,18]),('2.3 Collision and visibility',[7,8,13,9]),('2.4 Display mapping, shadows and textures',[10,11,12,14,15])]
for title,ids in groups:
 h(title)
 for idx in ids:
  a=refs[idx-1];para(f"{a['authors'][0].split()[-1]} et al. [{idx}]. {a['method_summary']} {comparisons.get(idx,a['project_comparison'])}")
 if ids[0]==1:para('Phong-style per-fragment evaluation is a shading strategy, while Cook-Torrance and Schlick address reflectance. The project chooses empirical Blinn-Phong for legibility and explicit controls. Its brass appearance is an artistic approximation; the shader is not described as a physically calibrated conductor model.')
 if ids[0]==4:para('Linear blend skinning offers a small and inspectable runtime. Dual quaternions and fitted deformation methods address stronger quality constraints, but would require different validation. The crouch export instead lowers the pelvis by 0.14 m and uses two-bone leg IK to preserve limb lengths and sole contact before sampling local transforms.')
 if ids[0]==7:para('Six oriented laser boxes and a few furniture proxies do not justify a full collision hierarchy. Fixed 240 Hz body sampling is inexpensive for the chosen movement speeds, while depth testing and static instancing handle the visual scene. This choice trades generality for a bounded problem rather than implementing the cited continuous or deformable solvers.')
 if ids[0]==10:para('Display readability motivates the HDR target, fitted tone curve and controlled laser glow. The glow filter now compares scene depth so distant emission does not spill over a nearer character. This is a screen-space visibility correction, not a physical volumetric scattering solution.')

h('3 Project Description',True)
h('3.1 Objective and problem statement')
para('The objective is a complete implementation of topic 12 with all Core features and all three Stretch goals: rotating guard spotlights, live CCTV and safe-opening victory. A player must be able to fail, retry and win through the same rules shown in the demonstration. The technical problem is keeping rendered transforms, sampled collision, eye height, skinned motion and framebuffer outputs consistent.')
h('3.2 Scope and environment')
para('The vault measures approximately 8 by 15 by 4 metres. An enclosed entrance vestibule leads to a locked archive corridor. The room contains wood and stone finishes, a window, a desk, chair, local lamp, monitor, deposit drawers, framed art, plants, a rug and an articulated safe. A visible barred gate with a padlock and lockdown sign explains the blocked exit; the player and camera stop before its surface.')
n=figure('entrance','Enclosed entrance corridor and locked security gate replacing the former empty opening')
para(f'Figure {n} shows a physical explanation for the movement limit. The decorative corridor continues behind the gate, but is outside the playable route. Painting frames, sconces and the relocated deposit cabinet are clear of the emitter hardware. Evaluated bounds are recorded in evidence/location-layout-validation.json.')
para('One player, one vault route and one finale are included. Guard characters, combat, weapons, multiplayer, shops and extra levels are excluded. Sound is optional in the brief and is not implemented. The source character and seven supplied actions came from the Meshy export; the skeleton names alone do not establish where each action was authored.')
h('3.3 Player controls and interactions')
n=figure('menu','Current menu with sensitivity and monitor-aware FPS controls')
para(f'Figure {n} shows the controls available before play. The same settings are accessible while paused; the FPS display remains visible during play.')
table(['Control','Effect'],[['WASD / mouse','Move relative to the view and look around'],['V','Switch first- and third-person view'],['Hold Ctrl or C','Crouch; lower the eye and body proxy'],['E','Use the lamp, CCTV selector or safe within 2.15 m'],['Esc / F1','Pause / controls help'],['R','Retry after alarm or victory']],[1.6,3.9])
para('In first person the character follows the view heading. In third person the mouse orbits independently; standing movement turns the body toward actual displacement and plays forward walking even for A/D or S. Crouching preserves heading and selects the matching forward/back/side clip. The lamp changes illumination and glow, the monitor switches between two live views, and the safe requires a real crossing of the final beam.')

h('4 Technical Implementation',True)
h('4.1 Languages, tools and build')
table(['Component','Use'],[['C++17 / GLSL 330','Gameplay, native input, resource ownership and custom GPU programs'],['GLFW / GLAD / GLM','Window/context, OpenGL loading and vector/matrix operations'],['Dear ImGui / stb','Menus/settings, PNG decode and framebuffer screenshots'],['Blender / Python','Model preparation, environment geometry, animation derivation and native export'],['CMake / LLVM-MinGW','Verified Windows Release build; dependencies are vendored'],['Python / FFmpeg','Evidence collection, PDF authoring and optional real-time recording']],[1.8,3.7])
para('Python is an offline authoring and verification tool. The game does not execute Python, open Blender or contact an asset service at startup. Geometry, transforms and hierarchy are loaded from native scene data; camera matrices, rendering, lights, collision and animation playback are evaluated in C++ and GLSL. The course starter was not supplied, so exact compatibility with that unknown setup is not asserted. Windows x64 is tested; Linux, macOS and MSVC instructions are provided without claiming an executed build there.')
h('4.2 Development and structure')
para('The code separates window/input orchestration, fixed-step game state, scene loading, GPU resources, world animation, skinning, UI and capture. Static mesh/material groups are uploaded once and drawn with instancing. Dynamic nodes include safe components, moving security hardware and the character. The renderer performs shadow, CCTV, main HDR and display passes; the monitor is omitted from its own security pass to avoid framebuffer feedback.')
table(['Module','Responsibility'],[['main.cpp / mouse_motion.hpp','Window, native mouse events, input consumption, orchestration'],['game.cpp / fixed_step.hpp','Player motion, contacts, interactions and state transitions'],['scene.cpp / graphics.cpp','Hierarchy, indexed meshes, textures, buffers and framebuffer ownership'],['animation.cpp / world.cpp','Bone palette and transforms for safe, lasers, spots and lights'],['renderer.cpp / shaders','Shadow map, CCTV, surface shading and display conversion'],['ui.cpp / frame_limiter.hpp','Menus, sensitivity/FPS choices and steady-clock pacing']],[2.1,3.4])
h('4.3 Transformations and collision')
para('For column vectors the world matrix is the parent world matrix multiplied by the local transform. The model, view and projection sequence places geometry in clip space. Normals use an inverse transpose so that non-uniform scale does not rotate lighting incorrectly.')
story.append(P('Mworld = Mparent × T × R × S\npclip = P × V × Mworld × plocal\nNworld = normalize(transpose(inverse(mat3(Mworld))) × Nlocal)','equation'))
para('Each moving beam provides the same model matrix to rendering and contact tests. A body point is transformed by the inverse beam matrix and compared against local half-extents. This avoids the false positives of a large world-aligned bounding box around a rotated beam.')
story.append(P('q = inverse(Mbeam) × (pbody, 1)\nhit when |qx| ≤ hx and |qy| ≤ hy and |qz| ≤ hz','equation'))
para('The controller tests upright body samples at 0.08 m intervals, with conservative margins. Simulation advances at 1/240 s; one-shot interact/retry inputs remain pending until a step consumes them. Movement is normalized diagonally and tested against room/furniture proxies. This is discrete sampling for the specified speeds, not a continuous collision guarantee for arbitrary motion.')
h('4.4 Camera, input and frame pacing')
n=figure('third-person','Third-person character view in the current vault')
para(f'Figure {n} demonstrates the third-person view. Its boom is swept against padded scene proxies and refined near obstructions; it contracts before walls, furniture or the entrance gate. Changing boom distance does not change look direction. A camera very close to the hood hides the body in the main view while CCTV and shadows retain it.')
para('Windows input uses WM_INPUT rather than repeatedly treating cursor position as fresh motion. Relative deltas are accumulated and consumed once per frame; absolute devices have separate per-device baselines. Focus/capture changes clear pending motion. Manual playtesting confirmed that this corrected the uncontrolled view drift. Mouse sensitivity is displayed on a Source-style multiplier scale using 0.022 degrees per count per unit; the previous physical default remains unchanged.')
para('An FPS limiter follows the refresh rate of the monitor containing the window. Presets include reported monitor modes, custom entry accepts 1-10000 FPS, and Unlimited disables pacing. Retry preserves the selected view, sensitivity and cap. Windows uses a high-resolution waitable timer and a short final wait. Pacing changes render frequency; simulation and mouse-delta interpretation keep their own time/input rules.')
h('4.5 Character and animation')
para('The current thief has 30,725 triangles, 52 weighted bones plus required ancestors and no more than four normalized influences per vertex. The shader palette is limited to 64 matrices. The input FBX and source textures are preserved; runtime uses an indexed LVHM mesh, a scene manifest and sampled local TRS animation in LVHA. Blender coordinates (x,y,z) map once to runtime (x,z,-y).')
story.append(P('pskinned = Σ wi × Bi × pbind, for i = 1...4\nΣ wi = 1, wi ≥ 0; Bi = Gpose,i × inverse(Gbind,i)','equation'))
para('Walking and running use supplied actions. Forward crouching reverses the supplied backward cycle; backward walking reverses Walking. Idle poses average opposing gait phases, and Interact adds a reach. Crouch export lowers the pelvis by 0.14 m and solves leg contact. Runtime selects clips from actual movement relative to body heading and advances gait phase by travelled distance.')
table(['Clip group','Runtime names'],[['Standing','Idle, Walk, WalkBackward, Run'],['Crouching','CrouchIdle, CrouchWalk, CrouchBackward, CrouchLeft, CrouchRight'],['Actions','Interact, Dance, DanceLong']],[1.4,4.1])
n=figure('crouch','Current skinned character in a crouch-forward animation review')
para(f'Figure {n} is rendered from the imported mesh and the derived forward clip. Tests skin actual runtime vertices over all crouch frames. The maximum checked crouch height is approximately 1.287 m, below the 1.33 m body proxy. Standing height is 1.78 m and eye heights are 1.57 m standing and 1.22 m crouched.')

h('5 Graphics and Rendering',True)
h('5.1 Pipeline and live CCTV')
n=figure('cctv','Live security camera showing the current animated character')
para(f'Figure {n} shows the security view rendered into a 640 × 360 framebuffer. It contains the current room and animated thief, not a prerecorded image. A separate display target applies tone and gamma conversion for the enlarged UI view. The physical screen samples the linear security image as part of ordinary surface rendering.')
para('Meshes use VAO/VBO/EBO and custom vertex/fragment programs. Instanced static objects share mesh/material groups. The main target is RGBA16F with a depth texture; the shadow target is a 2048 × 2048 depth map. Framebuffer completeness is checked. Depth testing and back-face culling reject hidden opaque fragments.')
h('5.2 Lighting and shading')
n=figure('lamp','Desk-lamp interaction captured during actual gameplay')
para(f'Figure {n} records the local lamp toggle: both the light contribution and visible glow follow its state. The other scene lights continue to operate.')
para('Blinn-Phong shading is evaluated per fragment. Eight point lights cover the vault and corridor; two spotlights rotate with their equipment hierarchy. Ambient and directional moon terms establish the night palette. A lamp can be toggled. Alarm recolors illumination and emissive security fixtures red. The shader has capacity for twelve local lights.')
story.append(P('L = ka * C + Σ attenuation × cone × lightColor\n      * [C × max(N·L, 0) + ks × max(N·H, 0)^n]\nH = normalize(L + V)\nattenuation = power / (1 + 0.20d + 0.095d²)','equation'))
para('The implemented equation uses a normalized half-vector and material shininess. Soft spotlight edges interpolate between inner and outer cone limits. A 3 × 3 PCF kernel filters the directional shadow map; the spotlights do not each have a shadow map. Additive dust-cone geometry is a visualization rather than volumetric light transport.')
n=figure('spotlights','Rotating spotlight equipment and illumination in the actual runtime')
para(f'Figure {n} connects the visible fixture hierarchy with the light direction used by the shader. Rotation is applied to the mount, and the light vector is derived from the same world transform. Hierarchical wheel, bolt and door transforms use the same parent/child principle.')
h('5.3 Textures and post-processing')
para('Environment assets use exported UV coordinates and seeded painted textures. The thief uses the supplied base-color image; additional source maps are retained without claiming that runtime implements normal/metallic/roughness PBR. PNGs are uploaded once, decoded from sRGB for lighting, and given generated mipmaps with trilinear minification.')
para('A fitted filmic tone curve maps HDR color to display range, followed by gamma encoding and a restrained vignette. The curve coefficients are credited to Narkowicz [19]. Laser glow samples nearby bright pixels, but rejects samples farther than the current surface by a depth tolerance. Linear eye distance is reconstructed from the depth texture before that comparison.')
story.append(P('zndc = 2 × depth - 1\ndeye = 2 × near × far / (far + near - zndc × (far - near))','equation'))
para('This correction removed a measured 114-pixel glow spill onto the foreground character in the GPU regression fixture; the updated fixture reports zero such pixels. A foreground beam remains visible. The result demonstrates the tested occlusion case, not a universal promise of artifact-free rendering at every camera angle.')
h('5.4 Failure, safe opening and finale')
n=figure('final-beam','Crouched view below the last laser before the final passage')
para(f'Figure {n} shows the crouched position below the last beam before crossing. The following passage uses the ordinary body proxy and contact tests; reaching the far side enables safe interaction.')
n=figure('alarm','Actual alarm state following contact with a laser')
para(f'Figure {n} shows a real failure under the same rules as the final route. Retry reconstructs initial game state and laser phases while retaining player settings. The safe remains locked until the player has actually crossed the last beam.')
n=figure('dance','Open safe and the current character performing the one-shot victory dance')
para(f'Figure {n} shows the finale. The wheel rotates, bolts retract and the door opens over 3.4 s. The character is revealed after the door sweep and plays the 7.5 s Dance clip once. Gameplay is locked during Finale, pause freezes it, and Victory follows the entire 10.9 s sequence. The room extension keeps the door at least 1.70 m clear of the last laser.')

n=figure('victory','Victory appears after the complete safe-opening and dance sequence')
para(f'Figure {n} confirms the completed state after the one-shot finale. The demonstration retains the final result rather than cutting to a fabricated success screen.')

h('6 Testing and Evaluation',True)
h('6.1 Verification method')
table(['CTest suite','Coverage'],[['laser_character_occlusion','Real GPU baseline/behind/front beam comparisons; depth-aware glow; 2 cm inner-door/bolt clearance'],['gameplay_math','Oriented point-box contact, crouch clearance, states and interactions'],['complete_gameplay_route','Normal movement through six lasers and safe interaction'],['demo_and_slow_frames','Demo state progression, retained input edges, slow-frame consistency'],['imported_animation_clips','Actual runtime skinning, clip durations, weights and all crouch-frame bounds'],['complete_victory_cinematic','Door/dance duration, movement lock, pause, final frame and retry'],['player_camera_modes','Camera orbit, directional movement, native motion consumption, gate/prop obstruction, settings and complete third-person route']],[2.15,3.6])
para('All seven tests passed on the current Windows build. New screenshots were captured from the executable, and the updated demonstration records real framebuffer frames. Its deterministic controller supplies ordinary movement and interaction inputs; it does not disable collision or teleport the player through the final route. Manual feedback also confirmed the corrected mouse behavior and the refreshed room. This feedback is a practical check, not a formal multi-user usability study.')
h('6.2 Performance evaluation')
para('Hardware: Intel Core i5-13400F, NVIDIA GeForce RTX 5060, approximately 32 GiB RAM, Windows x64. Runtime reports OpenGL 3.3.0 NVIDIA 617.42. Three new visible 1280 × 720 runs use the current scene, repeated legal routes, live CCTV and skinning. Each run lasts 25 s; the first 5 s are warm-up. VSync, FPS cap and recording are disabled during measurement.')
table(['Run','Avg FPS','1% low','p50 ms','p95 ms','p99 ms'],[[str(b['run']),f"{b['average_fps']:.1f}",f"{b['one_percent_low_fps']:.1f}",f"{b['p50_ms']:.3f}",f"{b['p95_ms']:.3f}",f"{b['p99_ms']:.3f}"] for b in bench['runs']],[.5,1,1,1,1,1])
para('Average FPS is 1000 divided by mean frame time in milliseconds. The 1% low is 1000 divided by the mean of the slowest 1% of frame times. Percentiles use nearest rank. Timing covers the complete loop, including simulation, draw submission, UI, telemetry and presentation; it is not an isolated GPU timestamp. Desktop activity and OS scheduling can affect the tail.')
table(['Run','Frames measured','Peak working set','Peak private'],[[str(b['run']),str(b['frames']),f"{b['peak_working_set_mib']:.1f} MiB",f"{b['peak_private_mib']:.1f} MiB"] for b in bench['runs']],[.6,1.5,1.5,1.5])
para('These figures describe this computer and this route only. The course target is evaluated on the TA machine, whose hardware has not been supplied. The FPS setting normally defaults to the active display refresh rate; the limiter was separately measured at 60, 144 and a custom 237 FPS. A cap is an upper bound and does not guarantee that expensive frames will meet it.')
h('6.3 Issues found and corrected')
table(['Issue','Cause and correction'],[['Uncontrolled mouse rotation','Cursor positions could be re-counted as motion. Windows WM_INPUT accumulation and one-time consumption replaced that path; device baselines and focus resets are explicit.'],['Laser visible across character edges','Screen-space bloom ignored foreground depth. Depth-aware rejection removed the measured spill.'],['Flicker inside the safe door','Retracted brass bolts ended exactly on the inner door plane. Their rear faces are now 2 cm inside the slab.'],['Decorative intersections','Frames and deposit furniture overlapped security rails. Paintings and cabinet were relocated; evaluated bounds show no targeted decoration/security overlaps.'],['Empty entrance','The opening exposed the background clear color. An enclosed corridor, visible locked gate and matching collision now close the route.'],['Safe door touching the last laser','The room and safe approach were extended; the full door sweep now has 1.70 m minimum clearance.']],[1.65,4.0])


h('7 Conclusion and Future Work',True)
para('The current implementation integrates all mandatory technical areas and all three topic stretch goals in a playable vault route. It uses custom buffers and shaders, model/view/projection transformations, articulated objects, dynamic per-fragment illumination, UV textures with mipmaps, keyboard/mouse controls, three interactions and a visible FPS counter. The updated visual scene and character are supported by source assets, reproducible exports and seven passing tests.')
para('The project demonstrates that consistency across systems matters more than a feature list. Render transforms must match contact volumes; camera motion must consume fresh input only once; an emissive post-process must respect depth; and a mechanical assembly must avoid coincident surfaces. Recent fixes address each of these concrete failures and are represented in the new evidence.')
para('Future work should first test the exact TA machine and rehearse the live presentation with all three members. Technical extensions could include continuous collision for higher speeds, more stable shadow filtering, stronger deformation for extreme poses and accessibility or sound settings. Additional levels and combat are outside the current scope. Actual oral understanding, each member\'s account history, Moodle submission and the assigned grade cannot be established by local automated checks.')

h('8 References',True)
for a in refs:
 authors=', '.join(a['authors']);detail=f", vol. {a['volume']}" if a.get('volume') else ''
 if a.get('issue'):detail+=f", no. {a['issue']}"
 if a.get('pages'):detail+=f", pp. {a['pages']}"
 para(f"[{a['id']}] {authors}, \"{a['title']}\", {a['journal']}{detail}, {a['year']}. DOI: {a['doi']}.")
 story.append(P(a['url'],'caption'))
para('[19] K. Narkowicz, "ACES Filmic Tone Mapping Curve", 2016. Fitted tone-mapping expression, CC0 option. https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/')
h('8.1 Asset and technical credits')
para('The character source package contains the Meshy-exported thief, textures, skeleton and seven supplied motions. They are retained in art/source/animated_thief. Derived clips and retargeting are recorded in docs/animated-thief-integration.md. Bone names use the Mixamo convention, which is not proof that every motion came from Mixamo. The room, furniture, corridor and environment textures were created for this project with the retained Blender/Python scripts. The referenced game Just Another Night Shift is a style reference, not a source of extracted meshes or code.')
para('Third-party components: GLFW (zlib/libpng), GLM (MIT option), Dear ImGui (MIT), stb (MIT option), generated GLAD declarations (CC0 plus registry/generator notices), and Karla by Jonathan Pinhorn (SIL OFL 1.1). Exact versions, upstream links and license copies are in CREDITS.md, docs/dependency-lock.json and LICENSES/. The supplied course documents and concept images remain local and are not republished as project artwork.')
para('Primary technical sources include https://www.glfw.org/documentation.html, https://github.com/g-truc/glm, https://github.com/ocornut/imgui, https://github.com/nothings/stb, https://github.com/Dav1dde/glad and https://github.com/ValveSoftware/source-sdk-2013. The latter documents the Source mouse yaw/pitch coefficient; the project uses its own input implementation.')
h('8.2 Journal ranking provenance')
for j,r in rankings.items():
 para(j+': SJR '+str(r.get('year',2025))+' '+r['quartile']+', '+r['category']+'.')
 for url in r['sources']:story.append(P(url,'caption'))

h('9 Appendix',True)
h('9.1 Requirement coverage')
table(['ID','Implemented evidence'],[['R1','C++17, OpenGL 3.3 core, VAO/VBO/EBO and separate GLSL programs'],['R2','Vault, corridor, furniture, security hardware, safe and animated character'],['R3','Custom MVP and parent/child transforms for safe and rotating equipment'],['R4','Per-fragment Blinn-Phong, toggleable lamp, moving spots and alarm'],['R5','UV-mapped environment/character textures with generated mipmaps'],['R6','Two camera modes, keyboard/mouse controls and three interactions'],['R7','Visible counter and current hardware/FPS table; TA-machine check remains'],['R8','Vendored CMake build and exact README commands; course starter unavailable']],[.5,5.0])
h('9.2 Reproduction')
para('Build with the README commands and run CTest. Standard startup discovers assets and shaders beside the executable. Use --root PATH for an authoring checkout, --entrance-preview for the new gate view, --character-preview --clip CrouchWalk for the rig, and --finale-preview for the actual finale. --fps 0 disables the cap for benchmarks; --fps auto follows the monitor. The ordinary release needs no Python, Blender, compiler or network connection.')
para('The report figure files are fresh runtime captures in evidence/screenshots/report-current. Raw current benchmark CSVs and the summary are in evidence/benchmarks-current. The previous benchmark folder remains historical. A release archive attached to an earlier tag may predate the latest source, so reviewers should use the current tagged release or build the branch identified in README.')
h('9.3 Defense preparation')
para('Nurbek should present the visual direction, model/animation pipeline and how the art stays consistent with gameplay. Makhmet should explain inverse-transform laser contact, state transitions and rendering stages. Nurassyl should explain fresh input consumption, interactions, tests, reproduction and measurements. This is a presentation plan, not a claim that the oral defense has already happened. Every member should also explain MVP, the Blinn half-vector, normalized skin weights, framebuffer feedback avoidance and the continuous final route.')

Report(OUT).multiBuild(story)
# Remove generated creation timestamps from distribution metadata.
reader=PdfReader(OUT);writer=PdfWriter();writer.clone_document_from_reader(reader)
writer.add_metadata({'/Title':'Laser Vault Heist','/Author':NAMES,'/Subject':'Computer Graphics Fundamentals; Group SE-2428','/Creator':'Project report'})
for key in ['/CreationDate','/ModDate']:
 if writer.metadata and key in writer.metadata:del writer._info.get_object()[key]
with OUT.with_suffix('.clean.pdf').open('wb') as f:writer.write(f)
OUT.with_suffix('.clean.pdf').replace(OUT)
pages=PdfReader(OUT).pages;text='\n'.join(p.extract_text() or '' for p in pages)
for name in NAMES.split(', '):assert name in text
assert 'Group: SE-2428' in text and 'Student: Nurbek' not in text
assert all(f'[{i}]' in text for i in range(1,19))
(WORK/'report-validation.json').write_text(json.dumps({'pages':len(pages),'figures':figures,'students':NAMES,'reference_count':len(refs),'pdf_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'template_page_geometry':PAGE,'body_font_pt':14,'table_font_pt':12},indent=2))
print('Created',OUT,'pages',len(pages),'figures',len(figures))
