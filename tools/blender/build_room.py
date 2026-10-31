"""Build the approved room in Blender; preserve unrelated scenes."""
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'/'blender'))
import common as h
import importlib
importlib.reload(h)
from common import *
scene=new_scene('LVH_Vault')
wood=material('Oak',(1,1,1),'textures/wood.png',.14)
darkwood=material('Walnut',(1,1,1),'textures/darkwood.png',.18)
stone=material('Stone',(1,1,1),'textures/stone.png',.05)
plaster=material('Plaster',(1,1,1),'textures/plaster.png',.03)
metal=material('Metal',(1,1,1),'textures/metal.png',.55,64)
edge=material('MetalEdge',(.12,.16,.14),None,.5,48)
brass=material('Brass',(.46,.29,.105),None,.65,64)
rug=material('Rug',(1,1,1),'textures/rug.png',.02)
black=material('Black',(.012,.018,.017),None,.12)
red=material('Laser',(.95,.003,.001),None,0,16,7)
lampmat=material('LampGlass',(1,.58,.21),None,.1,32,2.3)
leafmats=[material('Leaf'+str(i),(.07+i*.025,.13+i*.035,.045+i*.012),None,.08) for i in range(3)]
potmat=material('Ceramic',(.30,.23,.14),None,.18)
painting=material('Landscape',(1,1,1),'textures/landscape.png',.03)
sky=material('NightSky',(.012,.035,.10),None,0,8,.6)
moon=material('Moon',(.55,.69,1),None,0,8,1.5)
# Individually bevelled planks; deliberate joints and broad painted grain.
for col in range(20):
 x=-3.8+col*.4
 for row in range(8):
  length=min(2,15-row*2);y=row*2+length/2
  o=cube(f'Floor_{col}_{row}',(x,y,-.04),(.389,length-.015,.08),wood,.008)
  # Orient grain along the long board.
  for p in o.data.uv_layers.active.data:p.uv=(p.uv.y*2,p.uv.x*.5)
cube('FloorUnderlay',(0,7.5,-.12),(8.15,15.1,.1),darkwood,.01)
cube('RightPlaster',(4.08,7.5,2),(.25,15,4),plaster,.02)
cube('BackPlaster',(0,15.08,2),(8.2,.25,4),plaster,.02)
cube('LeftFrontPlaster',(-4.08,.72,2),(.25,1.44,4),plaster,.02)
cube('LeftBackPlaster',(-4.08,9.98,2),(.25,10.04,4),plaster,.02)
cube('WindowSillWall',(-4.08,3.2,.54),(.25,3.52,1.08),stone,.02)
cube('WindowTopWall',(-4.08,3.2,3.92),(.25,3.52,.16),plaster,.02)
cube('Ceiling',(0,7.5,4.1),(8.2,15.2,.2),darkwood,.01)
for row in range(5):
 for col in range(10):
  x=-3.6+col*.8+(row%2)*.07
  cube(f'BackStone_{row}_{col}',(x,14.9,.38+row*.76),(.77,.18,.72),stone,.055)
for side in [-1,1]:
 cube('Skirting'+str(side),(side*3.92,7.5,.17),(.18,15,.32),darkwood,.015)
 for y in [.2,4.6,8.6,11.7,14.7]:
  cube('TimberUpright',(side*3.88,y,2),(.22,.24,4),darkwood,.025)
  cube('TimberFoot',(side*3.88,y,.15),(.32,.34,.30),wood,.02)
for y in [.2,4.6,8.6,11.7,14.7]:
 cube('CeilingBeam',(0,y,3.91),(8,.25,.28),darkwood,.035)
for x in [-2,0,2]:cube('CeilingJoist',(x,7.5,4),(.16,15,.16),darkwood,.015)
# Entrance, visible when looking back.
for x in [-2.1,2.1]:cube('DoorJamb',(x,.1,1.85),(.35,.34,3.7),darkwood,.03)
cube('DoorLintel',(0,.1,3.63),(4.55,.36,.28),wood,.03)
for side in [-1,1]:cube('EntranceSide',(side*3.1,.1,1.9),(1.8,.22,3.8),stone,.03)
# Enclosed vestibule, locked security gate and a furnished corridor beyond it.
teal=material('HeritageTeal',(.055,.12,.115),None,.13)
ivory=material('SignIvory',(.75,.65,.43),None,.08,16,.25)
def label(name,body,loc,size=.13):
 bpy.ops.object.text_add(location=loc)
 ob=bpy.context.object;ob.name=name;ob.data.body=body;ob.data.size=size
 ob.data.align_x=enum_value(ob.data,'align_x','CENTER');ob.data.extrude=.001
 ob.rotation_euler=(math.pi/2,0,math.pi);assign(ob,ivory)
 bpy.ops.object.convert(target=next(e.identifier for e in bpy.ops.object.convert.get_rna_type().properties['target'].enum_items if e.identifier=='MESH'))
 return bpy.context.object
cube('VestibuleFloor',(0,-4,-.10),(4.15,8.2,.20),stone,.015)
cube('VestibuleCeiling',(0,-4,3.85),(4.3,8.4,.22),darkwood,.02)
cube('CorridorEndWall',(0,-8.1,1.9),(4.3,.22,3.8),plaster,.02)
for side in [-1,1]:
 cube('CorridorWall',(side*2.03,-4,1.9),(.22,8.2,3.8),plaster,.02)
 cube('CorridorWainscot',(side*1.90,-4,.62),(.08,8.1,1.24),teal,.01)
 for z in [.12,1.27,3.59]:cube('CorridorMoulding',(side*1.83,-4,z),(.12,8.1,.10),brass if z==1.27 else darkwood,.012)
 for y in [-.5,-2.65,-5,-7.85]:cube('CorridorPilaster',(side*1.83,y,1.9),(.18,.19,3.75),darkwood,.02)
 for y in [-4.1,-6.8]:
  cube('CorridorSconceBack',(side*1.79,y,2.45),(.10,.22,.40),brass,.02)
  cyl('CorridorSconceGlow',(side*1.65,y,2.45),.095,.25,lampmat,16)
  for z in [2.28,2.62]:cyl('CorridorSconceCap',(side*1.65,y,z),.14,.055,brass,16)
for y in [-2.65,-5,-7.85]:cube('CorridorCoffer',(0,y,3.65),(3.8,.2,.23),darkwood,.025)
for row in range(8):
 for col in range(4):
  cube('CorridorTile',(-1.48+col*.985,-.52-row*.99,.012),(.96,.96,.024),stone,.006)
for x in [-1.35,1.35]:cube('CorridorFloorInlay',(x,-4,.029),(.035,8.0,.012),brass,.003)
cube('CorridorRunner',(0,-5.3,.045),(1.8,4.9,.025),rug,.007)
# The grille is an actual physical boundary at runtime z=2.65 m.
for x in [-1.83,0,1.83]:cube('SecurityGateFrame',(x,-2.65,1.69),(.10,.14,3.38),edge,.016)
for z in [.10,1.1,3.32]:cube('SecurityGateCrossbar',(0,-2.65,z),(3.7,.14,.09),edge,.012)
for i in range(20):
 x=-1.71+i*.18
 cube('SecurityGateBar',(x,-2.65,1.70),(.035,.075,3.12),edge,.008)
 sphere('GateBrassCollar',(x,-2.65,1.1),(.038,.055,.065),brass,12,8)
cube('SecurityGateKickplate',(0,-2.65,.24),(3.65,.12,.32),teal,.018)
cube('SecurityGateLockPlate',(0,-2.55,1.57),(.30,.10,.46),brass,.025)
cube('SecurityGateLock',(0,-2.46,1.47),(.16,.10,.18),black,.02)
torus('SecurityGateShackle',(0,-2.46,1.59),.075,.018,brass,None,(math.pi/2,0,0))
cube('SecurityNotice',(0,-2.55,2.52),(2.6,.08,.44),teal,.02)
label('GateNoticeText','SECURITY LOCKDOWN',(0,-2.50,2.53),.145)
label('GateNoticeSmall','ACCESS SEALED',(0,-2.50,2.36),.09)
cube('CorridorEndDoor',(0,-7.95,1.54),(2.35,.12,3.08),darkwood,.035)
for x in [-.58,.58]:
 cube('EndDoorInset',(x,-7.87,1.7),(.98,.035,2.35),teal,.02)
 cyl('EndDoorKnob',(x*.25,-7.79,1.42),.055,.10,brass,16,None,(math.pi/2,0,0))
cube('EndDoorCrown',(0,-7.84,3.18),(2.65,.22,.18),wood,.02)
label('CorridorArchiveLabel','PRIVATE ARCHIVES',(0,-7.75,3.43),.16)
# Layered wall panelling stays behind the security mounting rails.
for side in [-1,1]:
 cube('RoomWainscot',(side*3.95,8,.60),(.065,13.7,1.0),teal,.01)
 cube('RoomChairRail',(side*3.90,8,1.14),(.08,13.7,.075),darkwood,.01)
 for y in [1.2,3.5,5.0,6.25,7.55,10.5,12.9,14.2]:
  cube('PanellingStile',(side*3.90,y,.60),(.06,.055,.91),brass,.004)

# Tall blue window and its physical mullions.
cube('NightBeyondWindow',(-4.28,3.2,2.45),(.04,3.36,2.70),sky,0)
for y in [1.5,4.9]:cube('WindowVerticalFrame',(-3.94,y,2.45),(.25,.12,2.85),darkwood,.015)
for z in [1.04,3.88]:cube('WindowHorizontalFrame',(-3.94,3.2,z),(.28,3.5,.14),wood,.015)
for y in [2.32,3.2,4.08]:cube('WindowMullion',(-3.96,y,2.47),(.10,.055,2.75),edge,.008)
for z in [1.96,2.94]:cube('WindowCrossbar',(-3.96,3.2,z),(.10,3.4,.055),edge,.008)
sphere('MoonDisc',(-4.22,3.68,3.22),(.03,.26,.26),moon,24,16)
cube('WindowSill',(-3.85,3.2,1.02),(.55,3.65,.14),wood,.025)
# Carpet uses a continuous, non-repeating UV island.
carpet=cube('WovenCarpet',(0,6.55,.015),(4.45,6.3,.035),rug,.012)
# Desk and sturdy chair.
cube('DeskTop',(-2.9,2.65,.83),(1.65,2.15,.13),wood,.035)
cube('DeskApron',(-2.9,2.65,.65),(1.48,1.95,.20),darkwood,.02)
for x in [-3.55,-2.25]:
 for y in [1.8,3.5]:
  cube('DeskLeg',(x,y,.37),(.12,.13,.73),darkwood,.016)
  cube('DeskLegFoot',(x,y,.08),(.17,.18,.13),wood,.016)
for y in [2.1,2.63,3.16]:
 cube('DrawerFront',(-2.07,y,.62),(.05,.46,.19),wood,.012)
 rod('DrawerHandle',(-2.03,y-.08,.64),(-2.03,y+.08,.64),.017,brass)
cube('ChairSeat',(-2.66,1.0,.49),(.65,.62,.13),darkwood,.03)
cube('ChairCushion',(-2.66,1.0,.58),(.57,.52,.10),material('ChairFabric',(.25,.065,.035),None,.02),.03)
for x in [-2.91,-2.41]:
 for y in [.77,1.23]:cube('ChairLeg',(x,y,.24),(.075,.075,.48),darkwood,.008)
for x in [-2.94,-2.38]:cube('ChairBackPost',(x,.73,.91),(.08,.08,.85),wood,.012)
for z in [.84,1.05,1.28]:cube('ChairBackSlat',(-2.66,.73,z),(.61,.07,.14),wood,.01)
# Desk lamp and CCTV screen.
cyl('DeskLampFoot',(-2.85,1.97,.94),.18,.045,brass)
rod('DeskLampStem',(-2.85,1.97,.95),(-2.85,1.97,1.31),.025,brass)
cyl('DeskLampShade',(-2.85,1.97,1.4),.25,.22,edge,24,radius2=.11)
cyl('DeskLampGlow',(-2.85,1.97,1.29),.215,.015,lampmat,24)['dynamic']=True
cube('MonitorCase',(-2.78,3.30,1.23),(.70,.52,.57),edge,.06)
cube('MonitorStand',(-2.78,3.35,.94),(.36,.33,.12),black,.02)
cube('MonitorBezel',(-2.78,3.025,1.25),(.65,.045,.49),black,.025)
screen=cube('CCTVScreen',(-2.78,2.996,1.27),(.54,.012,.36),material('CCTV',(.9,1,.94),None,0),.005);screen['screen']=True
for x in [-3.01,-2.89,-2.77]:cyl('MonitorButton',(x,2.988,1.04),.014,.012,brass,12,rotation=(math.pi/2,0,0))
# Deposit cabinet with repeated doors and distinct handles.
cube('DepositCabinet',(-3.55,11.5,1.35),(.68,2.7,2.7),black,.04)
for row in range(5):
 for col in range(4):
  y=10.54+col*.64;z=.3+row*.52
  cube('DepositDoor',(-3.18,y,z),(.065,.60,.48),metal,.015)
  cube('DepositLabel',(-3.137,y-.12,z+.08),(.012,.17,.065),brass,.003)
  rod('DepositHandle',(-3.10,y+.07,z-.06),(-3.10,y+.20,z-.06),.016,brass)
  cyl('DepositKeyhole',(-3.13,y-.14,z-.07),.015,.015,black,10,rotation=(0,math.pi/2,0))
# A hollow vault frame, inset shelving and an articulated door.
cube('SafeShadowBack',(0,14.72,1.66),(2.9,.12,3.2),black,.03)
for x in [-1.62,1.62]:cube('SafeSide',(x,14.45,1.65),(.32,.76,3.3),metal,.045)
for z in [.17,3.16]:cube('SafeFrame',(0,14.45,z),(3.56,.76,.31),metal,.04)
for z in [.8,1.55,2.3]:cube('VaultShelf',(0,14.65,z),(2.9,.55,.065),edge,.015)
for i in range(6):cube('VaultLedger',(-.9+i*.29,14.63,.99),(.20,.35,.32),darkwood,.015)
for i in range(4):cube('GoldIngot',(-.50+i*.32,14.61,1.67),(.28,.36,.15),brass,.025)
pivot=empty('SafeDoorPivot',(-1.36,14.02,.30));pivot['dynamic']=True
door=cube('SafeDoor',(1.36,0,1.36),(2.72,.26,2.72),metal,.06,pivot)
cube('SafeDoorInset',(1.36,-.148,1.36),(2.40,.06,2.40),edge,.035,pivot)
for x in [.25,2.47]:
 for z in [.25,2.47]:
  cyl('DoorRivet',(x,-.19,z),.047,.03,brass,12,pivot,(math.pi/2,0,0))
wheel=empty('SafeWheel',(1.36,-.27,1.36),pivot)
torus('WheelRing',(0,0,0),.43,.043,brass,wheel,(math.pi/2,0,0))
cyl('WheelHub',(0,0,0),.10,.20,brass,24,wheel,(math.pi/2,0,0))
for i in range(6):
 a=i*math.tau/6;rod('WheelSpoke',(0,0,0),(.40*math.cos(a),0,.40*math.sin(a)),.027,brass,wheel)
for i,z in enumerate([.45,1.36,2.27]):
 bolt=cube('SafeBolt'+str(i),(2.68,.03,z),(.25,.16,.14),brass,.015,pivot)
 bolt.keyframe_insert('location',frame=13);bolt.location.x-=.22;bolt.keyframe_insert('location',frame=28)
 cyl('SafeHinge',(-1.53,14.04,z+.3),.11,.36,brass,20)
# Wall sconces with visible supports and warm glass.
for side,y in [(-1,5),(1,3.6),(-1,13.6),(1,13.6)]:
 x=side*3.76
 cube('SconcePlate',(x,y,2.30),(.08,.22,.38),brass,.025)
 rod('SconceArm',(x,y,2.2),(x-side*.24,y,2.18),.035,brass)
 cyl('SconceGlass',(x-side*.24,y,2.37),.09,.30,lampmat,12)
 for z in [2.19,2.55]:cyl('SconceCap',(x-side*.24,y,z),.13,.05,brass,12)
 light('SconceLight',(x-side*.46,y,2.37),(1,.60,.25),210)
# Rotating equipment; geometry and light both use the same mount hierarchy.
for i,x in enumerate([-2.2,2.2]):
 cube('SpotCeilingPlate',(x,6.5,3.86),(.36,.38,.10),edge,.025)
 rod('SpotStem',(x,6.5,3.82),(x,6.5,3.65),.045,brass)
 p=empty('SpotPivot'+str(i),(x,6.5,3.6));p['dynamic']=True
 cube('SpotYoke',(0,0,-.05),(.48,.15,.10),edge,.025,p)
 for dx in [-.22,.22]:cube('SpotBracket',(dx,0,-.18),(.07,.15,.30),edge,.015,p)
 cyl('SpotHousing',(0,.06,-.22),.19,.32,metal,24,p,(.335,0,0))
 cyl('SpotLens',(0,.113,-.38),.165,.015,lampmat,24,p,(.335,0,0))
 for frame,angle in [(1,0),(41,.65),(81,0),(121,-.65),(161,0)]:
  p.rotation_euler.z=angle;p.keyframe_insert('rotation_euler',frame=frame)
 p.rotation_euler.z=0
 l=light('GuardSpot'+str(i),(0,.13,-.43),(1,.64,.3),500,'SPOT');l.parent=p;l.rotation_euler=(.335,0,0);l.data.spot_size=.85;l.data.spot_blend=.35
# Emitters and the exact collision boxes share the same beam transforms.
for i,y in enumerate([2.9,4.2,5.6,6.9,8.15,9.5]):
 height=1.42 if i==5 else 1.35
 for side in [-1,1]:
  mount=empty('EmitterRoot'+str(i)+'_'+str(side),(side*3.65,y,height));mount['dynamic']=True
  cube('EmitterRail',(side*3.86,y,1.95),(.06,.12,3.25),edge,.012)
  cube('LaserMount',(side*.16,0,0),(.10,.22,.26),edge,.025,mount)
  cyl('LaserEmitter',(side*.03,0,0),.075,.14,black,16,mount,(0,math.pi/2,0))
  cyl('EmitterLens',(-side*.05,0,0),.039,.012,red,16,mount,(0,math.pi/2,0))
 beam=cube('Laser'+str(i),(0,y,height),(1,1,1),red,0);beam['dynamic']=True
 beam.scale=(7.3,.024,.024)
# Faceted plants with curved leaves, rather than intersecting solid cones.
def plant(loc,scale):
 x,y,z=loc
 cyl('PlantPot',(x,y,z+.24*scale),.24*scale,.48*scale,potmat,16,radius2=.32*scale)
 torus('PotLip',(x,y,z+.47*scale),.31*scale,.025*scale,potmat)
 cyl('PotSoil',(x,y,z+.46*scale),.285*scale,.02,black,16)
 for i in range(9):
  angle=i*2.4;length=(.62+.12*(i%3))*scale
  start=Vector((x,y,z+.45*scale));tip=start+Vector((math.cos(angle)*length*.65,math.sin(angle)*length*.65,length*.72))
  mid=start.lerp(tip,.55)+Vector((0,0,length*.3));rod('PlantStalk',start,mid,.012*scale,leafmats[0])
  tangent=Vector((-math.sin(angle),math.cos(angle),0))*.16*scale
  verts=[tuple(start),tuple(mid-tangent),tuple(mid+Vector((0,0,.045*scale))),tuple(mid+tangent),tuple(tip)]
  ob=face_mesh('BroadLeaf',verts,[(0,1,2),(0,2,3),(1,4,2),(2,4,3)],leafmats[i%3])
  # Give leaves real thickness with an explicitly validated modifier enum.
  sol=ob.modifiers.new('Leaf thickness',next(e.identifier for e in bpy.types.Modifier.bl_rna.properties['type'].enum_items if e.identifier=='SOLIDIFY'));sol.thickness=.004
for loc,scale in [((3.1,1.3,0),1.2),((3.12,13.4,0),1.1),((-2.65,13.1,0),.85)]:plant(loc,scale)
# Framed original landscapes.
for y in [1.65,10.8]:
 cube('PaintingCanvas',(3.86,y,2.35),(.025,1.2,1.0),painting,0)
 for yy in [y-.66,y+.66]:cube('PictureSide',(3.83,yy,2.35),(.13,.11,1.18),brass,.018)
 for zz in [1.79,2.91]:cube('PictureTop',(3.83,y,zz),(.13,1.4,.11),brass,.018)
 cube('PictureLight',(3.65,y,3.07),(.12,.80,.07),brass,.015)
# Small side table provides variety without blocking the central route.
cube('SideTableTop',(3.0,8.9,.79),(1.15,1.5,.12),wood,.025)
for x in [2.53,3.47]:
 for y in [8.3,9.5]:cube('SideTableLeg',(x,y,.38),(.09,.09,.76),darkwood,.012)
for i in range(3):cube('ClosedBook',(3,8.8,.9+i*.065),(.47,.32,.055),darkwood,.009)
# Demonstration keys retained in the editable source.
wheel.rotation_euler.y=0;wheel.keyframe_insert('rotation_euler',frame=1);wheel.rotation_euler.y=math.radians(150);wheel.keyframe_insert('rotation_euler',frame=25)
pivot.rotation_euler.z=0;pivot.keyframe_insert('rotation_euler',frame=25);pivot.rotation_euler.z=math.radians(-100);pivot.keyframe_insert('rotation_euler',frame=85)
scene.frame_set(1)
world=bpy.data.worlds.new('VaultNight');world.use_nodes=True
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');background.inputs['Color'].default_value=(.08,.13,.25,1);background.inputs['Strength'].default_value=.25;scene.world=world
light('WindowFill',(-3.7,3.2,2.6),(.35,.53,1),230)
light('DeskLamp',(-2.85,1.97,1.24),(1,.63,.30),35)
bpy.ops.object.camera_add(location=(0,-.15,1.68));cam=bpy.context.object;cam.name='VaultPresentationCamera';cam.rotation_euler=(Vector((0,8,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24;scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format=enum_value(scene.render.image_settings,'file_format','PNG')
scene.frame_end=161
bpy.context.view_layer.update()
# Export before packing to keep explicit relative runtime texture paths.
import export_scene
importlib.reload(export_scene);export_scene.export(scene)
bpy.ops.file.pack_all()
bpy.data.libraries.write(str(ROOT/'art'/'blender'/'vault.blend'),{scene},fake_user=True,compress=True)
print('Vault created:',len(scene.objects),'objects; editable source saved')
