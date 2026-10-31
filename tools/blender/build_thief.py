"""Create the supplied everyday-clothes thief, its editable rig and own clips."""
import sys,math,importlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'/'blender'))
import common,character_mesh,character_rig,character_face
for module in [common,character_mesh,character_rig,character_face]:importlib.reload(module)
from common import *
from character_mesh import *
from character_rig import create_rig,animate,pose
from character_face import build_face
scene=new_scene('LVH_Thief')
skin=material('Skin',(.66,.43,.32),None,.045,24)
leather=material('Jacket',(1,1,1),'textures/leather.png',.065,24)
cloth=material('Hoodie',(1,1,1),'textures/cloth.png',.06,20)
denim=material('Jeans',(1,1,1),'textures/denim.png',.045,20)
lining=material('HoodBinding',(.075,.038,.022),None,.06)
stitch=material('Stitching',(.24,.14,.080),None,.08)
sole=material('ShoeRubber',(.075,.054,.038),None,.04)
laces=material('Laces',(.24,.19,.14),None,.02)
shoes=material('Sneakers',(.55,.50,.43),'textures/leather.png',.045,24)
metal=material('ZipMetal',(.28,.23,.16),None,.45,64)
lip=material('Lip',(.28,.12,.09),None,.08)
brow=material('Brows',(.12,.068,.043),None,.02)
pupil=material('Pupils',(.025,.015,.010),None,.08)
nostril_mat=material('Nostrils',(.38,.23,.17),None,.08)
eye=material('EyeWhite',(.60,.56,.47),None,.3,48)
iris=material('Iris',(.10,.055,.027),None,.3,48)
# Closed zip hoodie and open leather jacket have separate, continuous shells.
profile=[(.92,.215,.125),(1.00,.218,.128),(1.08,.225,.13),(1.16,.225,.13),(1.24,.24,.135),(1.32,.255,.13),(1.39,.25,.115),(1.44,.205,.10),(1.49,.088,.076)]
loft('ZipHoodie',[(z,rx,ry,0,0) for z,rx,ry in profile],cloth,torso_weights,40)
loft('HoodieWaist',[(.95,.187,.116,0,0),(1.00,.201,.121,0,0)],lining,torso_weights,40)
loft('LeatherJacket',[(z,rx+.017,ry+.021,0,.006) for z,rx,ry in profile],leather,torso_weights,48,.27)
tube('ZipTrack',[(0,-.122,.99),(0,-.141,1.2),(0,-.133,1.38),(0,-.094,1.46)],[.004]*4,metal,torso_weights,8)
weighted(cube('ZipPull',(0,-.143,1.35),(.014,.008,.028),metal,.002),constant('Chest'))
for side,s in [('L',1),('R',-1)]:
 # Lapels are folded pieces of ordinary jacket collar.
 verts=[(s*.055,-.11,1.48),(s*.14,-.13,1.445),(s*.22,-.125,1.39),(s*.12,-.17,1.35),(s*.073,-.154,1.40)]
 weighted(face_mesh('JacketCollar'+side,verts,[(0,1,4),(1,2,3,4)],leather),constant('Chest'))
 # Sleeves include elbow rings, folded cuffs and subdued seam lines.
 xs=[.16,.22,.29,.34,.40,.455,.48,.50,.52,.55,.59,.64,.68,.72,.75]
 radii=[(.075,.075),(.101,.095),(.10,.095),(.095,.09),(.088,.087),(.087,.084),(.091,.088),(.085,.083),(.09,.085),(.083,.08),(.080,.076),(.076,.074),(.075,.070),(.072,.067),(.071,.064)]
 centers=[(s*x,0,1.40-.007*math.sin(j*.8)) for j,x in enumerate(xs)]
 tube('JacketSleeve'+side,centers,radii,leather,arm_weights(side),32)
 tube('HoodieCuff'+side,[(s*.745,0,1.42),(s*.785,0,1.42)],[(.065,.057),(.062,.052)],lining,constant('Forearm.'+side),24)
 tube('SleeveSeam'+side,[(s*x,-r[0]*.92,1.45) for x,r in zip(xs,radii)],[.002]*len(xs),stitch,arm_weights(side),6)
 # Hands have an actual palm, four separate fingers and an opposed thumb.
 tube('Palm'+side,[(s*.777,0,1.42),(s*.82,-.002,1.42),(s*.87,-.002,1.42),(s*.9,-.002,1.42)],[(.035,.022),(.045,.025),(.041,.023),(.032,.020)],skin,constant('Hand.'+side),24)
 for finger,(offset,length) in enumerate([(-.029,.084),(-.010,.105),(.010,.099),(.029,.080)]):
  points=[(s*.87,offset,1.42),(s*(.91+length*.28),offset*1.12,1.416),(s*(.91+length*.65),offset*1.22,1.410),(s*(.91+length),offset*1.3,1.405)]
  tube('Finger'+side+str(finger),points,[.010,.009,.008,.005],skin,constant('Hand.'+side),12)
 tube('Thumb'+side,[(s*.808,-.031,1.407),(s*.838,-.061,1.392),(s*.873,-.084,1.388),(s*.894,-.092,1.392)],[.014,.013,.011,.006],skin,constant('Hand.'+side),14)
 # Jeans retain shaped thighs and knees, not skin-tight tubes.
 zs=[.145,.19,.25,.32,.39,.435,.47,.51,.56,.63,.70,.77,.84,.89,.94,.99]
 leg=[]
 for z in zs:
  rx=.074+.035*max(0,min(1,(z-.4)/.5));ry=.078+.042*max(0,min(1,(z-.4)/.5))
  if .43<z<.56:rx+=.006
  leg.append((z,rx,ry,s*.12,.005))
 loft('JeansLeg'+side,leg,denim,leg_weights(side),36)
 tube('DenimSideSeam'+side,[(s*(.12+r[1]),.005,r[0]) for r in leg],[.0018]*len(leg),stitch,leg_weights(side),6)
 # Low everyday sneakers: flat flexible soles, toe boxes and heel counters.
 loft('ShoeSole'+side,[(.004,.087,.174,s*.12,-.06),(.045,.091,.180,s*.12,-.06),(.060,.087,.174,s*.12,-.06)],sole,constant('Foot.'+side),36)
 loft('Sneaker'+side,[(.058,.085,.170,s*.12,-.06),(.09,.083,.166,s*.12,-.06),(.13,.072,.145,s*.12,-.048),(.145,.065,.105,s*.12,-.018),(.16,.061,.065,s*.12,.005)],shoes,constant('Foot.'+side),36)
 for j in range(5):
  y=-.10+j*.024;z=.17
  tube('Shoelace'+side+str(j),[(s*.12-.046,y,z),(s*.12+.046,y+.014,z)],[.0035,.0035],laces,constant('Foot.'+side),8)
 # Small ordinary pockets, without straps or armour.
 points=[(s*.075,-.135,1.11),(s*.18,-.130,1.16),(s*.205,-.118,1.13)]
 tube('JacketPocket'+side,points,[.004,.004,.004],stitch,torso_weights,8)
loft('JeansSeat',[(.83,.18,.11,0,.008),(.9,.21,.12,0,0),(.98,.20,.115,0,0),(1.01,.195,.112,0,0)],denim,constant('Pelvis'),40)
loft('Neck',[(1.43,.061,.060,0,0),(1.55,.062,.060,0,0)],skin,constant('Neck'),32)
build_face(skin,lip,brow,eye,iris,pupil,nostril_mat,cloth,lining)
meshes=[o for o in scene.objects if o.type=='MESH']
rig=create_rig()
for ob in meshes:
 ob.parent=rig
 mod=ob.modifiers.new('Skin deformation',next(e.identifier for e in bpy.types.Modifier.bl_rna.properties['type'].enum_items if e.identifier=='ARMATURE'));mod.object=rig
clips=animate(rig)
rig.data.pose_position=enum_value(rig.data,'pose_position','REST')
# Neutral inspection setup emphasizes the visible face under the open hood.
world=bpy.data.worlds.new('CharacterStudio');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.35,.35,.35,1);bg.inputs['Strength'].default_value=.3;scene.world=world
for name,loc,power,size in [('Key',(1.3,-2.5,2.6),120,3),('Fill',(-1.8,-1.4,1.8),85,2),('Rim',(0,1.8,2.6),120,2)]:
 l=light(name,loc,(1,.88,.74) if name=='Key' else (.75,.84,1),power,'AREA');l.data.shape=enum_value(l.data,'shape','DISK');l.data.size=size;l.rotation_euler=(Vector((0,0,1.1))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-3.0,1.13));cam=bpy.context.object;cam.name='ThiefQACamera';cam.rotation_euler=(Vector((0,0,.98))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=enum_value(cam.data,'type','ORTHO');cam.data.ortho_scale=2.25;scene.camera=cam
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format=enum_value(scene.render.image_settings,'file_format','PNG')
scene.render.fps=24;scene.frame_start=0;scene.frame_end=48
bpy.context.view_layer.update()
import export_character
importlib.reload(export_character);export_character.export(scene,rig,meshes,clips)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art'/'blender'/'thief.blend'))
print('Thief created:',len(meshes),'mesh pieces;',len(rig.data.bones),'bones;',len(clips),'clips')
