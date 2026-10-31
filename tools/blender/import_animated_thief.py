"""Import the user's Meshy character and supplied motions; export native GPU skinning data.

Run in Blender (native wm.fbx_import). Original authoring/export stays in art/source.
Forward crouching is the supplied backward cycle sampled in reverse, in place.
"""
import bpy, math, struct, json, hashlib, shutil
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'art/source/animated_thief'
FBX = next(SOURCE.glob('*.fbx'))
OUT = ROOT / 'assets'
C = Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
scene = bpy.data.scenes.get('LVH_AnimatedThief')
if scene:
    old = list(scene.objects)
    bpy.context.window.scene = next(s for s in bpy.data.scenes if s != scene)
    bpy.data.scenes.remove(scene)
    for o in old:
        if not o.users_scene: bpy.data.objects.remove(o)
scene = bpy.data.scenes.new('LVH_AnimatedThief')
bpy.context.window.scene = scene
raw_names={'Walking','Running','Cautious_Crouch_Walk_Backward_inplace',
           'Cautious_Crouch_Walk_Left_inplace','Cautious_Crouch_Walk_Right_inplace',
           'FunnyDancing_02','Cherish_Pop_Dance'}
derived_names={'LVH_'+n for n in ['CrouchWalk','CrouchBackward','CrouchLeft','CrouchRight',
                                  'WalkBackward','Idle','CrouchIdle','Interact']}
for a in list(bpy.data.actions):
    if a.name.split('.')[0] in raw_names|derived_names and a.users<=int(a.use_fake_user):
        bpy.data.actions.remove(a)
before = set(bpy.data.actions)
bpy.ops.wm.fbx_import(filepath=str(FBX), use_anim=True)
imported = [a for a in bpy.data.actions if a not in before]
rig = next(o for o in scene.objects if o.type == 'ARMATURE')
mesh = next(o for o in scene.objects if o.type == 'MESH')
fps = scene.render.fps / scene.render.fps_base
actions = {}
for name in ['Walking','Running','Cautious_Crouch_Walk_Backward_inplace',
             'Cautious_Crouch_Walk_Left_inplace','Cautious_Crouch_Walk_Right_inplace',
             'FunnyDancing_02','Cherish_Pop_Dance']:
    actions[name] = next(a for a in imported if a.name == name or a.name.startswith(name+'.'))

# Relink the explicit texture files instead of FBX exporter machine paths.
textures = {'baseColor':'texture_0.png','roughness':'texture_0_roughness.png',
            'metallic':'texture_0_metallic.png','normal':'texture_0_normal.png'}
for mat in mesh.data.materials:
    for n in mat.node_tree.nodes:
        if n.type != 'TEX_IMAGE' or not n.image: continue
        for key, suffix in textures.items():
            if key.lower() in n.image.name.lower():
                n.image = bpy.data.images.load(str(next(SOURCE.glob('*'+suffix))),check_existing=True)
                break
base = next(SOURCE.glob('*texture_0.png'))
dest = OUT/'textures/thief_meshy_basecolor.png';dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(base,dest)

# Retain weighted bones plus their ancestors. Terminal markers carry no weights.
used = {mesh.vertex_groups[g.group].name for v in mesh.data.vertices for g in v.groups if g.weight>1e-7}
for name in list(used):
    b = rig.data.bones.get(name)
    while b and b.parent:
        used.add(b.parent.name);b=b.parent
bones = [b for b in rig.data.bones if b.name in used]
assert len(bones)<=64, f'{len(bones)} required bones exceed the portable palette'
index = {b.name:i for i,b in enumerate(bones)}
R = C @ rig.matrix_world
inverse_bind=[(R@b.matrix_local).inverted() for b in bones]
# Shoe vertices are used to preserve sole contact after retargeting and deepening
# crouches. A two-bone leg solve preserves limb lengths instead of squashing skin.
shoe_points={'Left':[],'Right':[]}
for v in mesh.data.vertices:
    p=C@mesh.matrix_world@v.co
    if p.y>.22:continue
    pairs=sorted([(g.weight,index[mesh.vertex_groups[g.group].name]) for g in v.groups
                  if mesh.vertex_groups[g.group].name in index],reverse=True)[:4]
    total=sum(w for w,j in pairs)
    for side in shoe_points:
        if sum(w for w,j in pairs if bones[j].name in ('mixamorig:'+side+'Foot','mixamorig:'+side+'ToeBase'))>.45:
            shoe_points[side].append((p,[(w/total,j) for w,j in pairs]))
rig.data.pose_position = next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='REST')
bpy.context.view_layer.update()
mesh.data.calc_loop_triangles()
normal_matrix = (C @ mesh.matrix_world).to_3x3().inverted().transposed()
verts=[];indices=[];uv=mesh.data.uv_layers.active
for tri in mesh.data.loop_triangles:
    for li in tri.loops:
        v=mesh.data.vertices[mesh.data.loops[li].vertex_index]
        p=C @ mesh.matrix_world @ v.co
        n=(normal_matrix @ mesh.data.corner_normals[li].vector).normalized()
        t=uv.data[li].uv if uv else (0,0)
        pairs=sorted([(g.weight,index[mesh.vertex_groups[g.group].name]) for g in v.groups
                      if mesh.vertex_groups[g.group].name in index and g.weight>1e-7],reverse=True)[:4]
        assert pairs, 'Unweighted vertex in supplied mesh'
        total=sum(w for w,j in pairs)
        w=[v/total for v,j in pairs]+[0]*(4-len(pairs));j=[j for v,j in pairs]+[0]*(4-len(pairs))
        verts.append((*p,*n,*t,*w,*j));indices.append(len(indices))
meshout=OUT/'meshes/thief_meshy.lvhm'
with meshout.open('wb') as f:
    f.write(struct.pack('<4sIII',b'LVHM',1,len(verts),len(indices)))
    for v in verts:f.write(struct.pack('<16f',*v))
    f.write(struct.pack('<'+'I'*len(indices),*indices))
(OUT/'thief.scene').write_text('# User supplied Meshy character; metres, Y up, forward +Z\n'
    'material "MeshyThief" 1 1 1 0.055 20 0 "textures/thief_meshy_basecolor.png"\n'
    'mesh "MeshyThief" "meshes/thief_meshy.lvhm"\n'
    'node "MeshyThief" -1 0 0 4 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1\n',encoding='utf-8')
rig.data.pose_position = next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='POSE')

def activate(a):
    rig.animation_data.action=a
    if len(a.slots):rig.animation_data.action_slot=a.slots[0]

def sample(a,frame):
    activate(a);scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
    world=[R @ rig.pose.bones[b.name].matrix for b in bones]
    return world

def localize(world):
    return [(world[index[b.parent.name]].inverted()@world[i] if b.parent else world[i]).decompose()
            for i,b in enumerate(bones)]

def fit_feet(world,drop=0.):
    original=[w.copy() for w in world]
    palette=[w@inv for w,inv in zip(original,inverse_bind)]
    for w in world:w.translation.y-=drop
    for side,points in shoe_points.items():
        minimum=min(sum(weight*(palette[j]@p).y for weight,j in pairs) for p,pairs in points)
        dy=max(0.,.003-minimum)
        ti=index['mixamorig:'+side+'UpLeg'];ki=index['mixamorig:'+side+'Leg'];fi=index['mixamorig:'+side+'Foot']
        h=world[ti].translation.copy();oh=original[ti].translation;ok=original[ki].translation;oa=original[fi].translation
        target=oa+Vector((0,dy,0));axis=target-h;distance=axis.length;direction=axis.normalized()
        l1=(ok-oh).length;l2=(oa-ok).length;distance=max(.001,min(distance,l1+l2-.00001))
        along=(l1*l1-l2*l2+distance*distance)/(2*distance)
        bend=(ok-h)-direction*(ok-h).dot(direction)
        if bend.length<.00001:bend=Vector((0,0,1))
        knee=h+direction*along+bend.normalized()*math.sqrt(max(0,l1*l1-along*along))
        for j,oldv,newv,pos in [(ti,ok-oh,knee-h,h),(ki,oa-ok,target-knee,knee)]:
            correction=oldv.normalized().rotation_difference(newv.normalized()).to_matrix().to_4x4()
            world[j]=correction@original[j];world[j].translation=pos
        for bone in [side+'Foot',side+'ToeBase']:
            j=index['mixamorig:'+bone];world[j]=original[j].copy();world[j].translation.y+=dy
    return world

clips={};provenance={}
def source_clip(name,source,reverse=False,loop=True):
    a=actions[source];start,end=map(float,a.frame_range);count=round(end-start)+1
    first=sample(a,end if reverse else start)[0].translation
    last=sample(a,start if reverse else end)[0].translation
    frames=[]
    for i in range(count):
        u=i/(count-1);w=sample(a,end-u*(end-start) if reverse else start+u*(end-start))
        w=fit_feet(w,.14 if name.startswith('Crouch') else 0.)
        # Remove accumulated root travel while retaining the gait/dance's natural sway.
        drift=(last-first)*u
        for m in w:
            m.translation.x-=drift.x;m.translation.z-=drift.z
        frames.append(localize(w))
    if loop:frames[-1]=frames[0]
    clips[name]=((end-start)/fps,frames)
    provenance[name]={'source':source,'reverse_time':reverse,'loop':loop,'duration':(end-start)/fps}
    provenance[name]['retarget_adjustment']='sole contact via two-bone leg IK; pelvis lowered 0.14 m for crouching'
source_clip('Walk','Walking')
source_clip('WalkBackward','Walking',True)
source_clip('Run','Running')
back='Cautious_Crouch_Walk_Backward_inplace'
source_clip('CrouchBackward',back)
source_clip('CrouchWalk',back,True)
source_clip('CrouchLeft','Cautious_Crouch_Walk_Left_inplace')
source_clip('CrouchRight','Cautious_Crouch_Walk_Right_inplace')
source_clip('Dance','FunnyDancing_02',loop=False)
source_clip('DanceLong','Cherish_Pop_Dance',loop=False)

def neutral(name,cycle):
    duration=2.;frames=[];src=clips[cycle][1];a=src[0];b=src[(len(src)-1)//2]
    base=[(ta.lerp(tb,.5),qa.slerp(qb,.5),sa.lerp(sb,.5)) for (ta,qa,sa),(tb,qb,sb) in zip(a,b)]
    world=[]
    for j,(bone,(tr,q,sc)) in enumerate(zip(bones,base)):
        local=Matrix.LocRotScale(tr,q,sc)
        world.append(world[index[bone.parent.name]]@local if bone.parent else local)
    base=localize(fit_feet(world))
    for i in range(61):
        t=i/60;row=[]
        for j,(tr,q,sc) in enumerate(base):
            tr=tr.copy();q=q.copy();sc=sc.copy()
            if j==0:tr.y+=.002*math.sin(t*math.tau)
            if bones[j].name=='mixamorig:Spine2':q=q@Quaternion((1,0,0),.004*math.sin(t*math.tau))
            row.append((tr,q,sc))
        frames.append(row)
    clips[name]=(duration,frames);provenance[name]={'derived':'average opposite gait phases with subtle breathing','source':cycle,'duration':duration}
neutral('Idle','Walk');neutral('CrouchIdle','CrouchBackward')
frames=[]
for i in range(43):
    u=i/42;reach=math.sin(math.pi*u);row=[]
    for b,(tr,q,sc) in zip(bones,clips['Idle'][1][0]):
        q=q.copy()
        if b.name=='mixamorig:RightArm':q=q@Quaternion((1,0,0),-.65*reach)
        if b.name=='mixamorig:RightForeArm':q=q@Quaternion((1,0,0),-.35*reach)
        row.append((tr.copy(),q,sc.copy()))
    frames.append(row)
clips['Interact']=(.7,frames);provenance['Interact']={'derived':'right-arm reach from neutral pose','duration':.7}

def string(f,value):
    data=value.encode();f.write(struct.pack('<I',len(data)));f.write(data)
def flat(m):return [m[r][c] for c in range(4) for r in range(4)]
with (OUT/'thief.lvanim').open('wb') as f:
    f.write(struct.pack('<4sIII',b'LVHA',1,len(bones),len(clips)))
    for b in bones:
        string(f,b.name);f.write(struct.pack('<i',index[b.parent.name] if b.parent else -1))
        f.write(struct.pack('<16f',*flat((R@b.matrix_local).inverted())))
    for name,(duration,frames) in clips.items():
        string(f,name);f.write(struct.pack('<fI',duration,len(frames)))
        for row in frames:
            for tr,q,sc in row:f.write(struct.pack('<10f',*tr,q.x,q.y,q.z,q.w,*sc))

# Bake derived motions as editable actions alongside all seven untouched source actions.
baked={}
for name in ['CrouchWalk','CrouchBackward','CrouchLeft','CrouchRight','WalkBackward','Idle','CrouchIdle','Interact']:
    duration,frames=clips[name]
    a=bpy.data.actions.new('LVH_'+name);baked[name]=a;activate(a)
    for i,row in enumerate(frames):
        world=[]
        for j,(b,(tr,q,sc)) in enumerate(zip(bones,row)):
            local=Matrix.LocRotScale(tr,q,sc)
            w=world[index[b.parent.name]]@local if b.parent else local;world.append(w)
            pb=rig.pose.bones[b.name];pb.rotation_mode='QUATERNION'
            # Key local basis directly; assigning evaluated world matrices would
            # otherwise use stale parent evaluation while baking children.
            pb.matrix_basis=(b.matrix_local.inverted()@b.parent.matrix_local@local
                             if b.parent else b.matrix_local.inverted()@R.inverted()@local)
            frame=1+duration*fps*i/(len(frames)-1)
            for channel in ['location','rotation_quaternion','scale']:pb.keyframe_insert(channel,frame=frame,group=b.name)
    a.use_fake_user=True
for a in imported:a.use_fake_user=True
activate(baked['Idle'])
scene.frame_set(1);scene.frame_start=1;scene.frame_end=451
rig['asset_origin']='User supplied Meshy model and merged animation FBX'
rig['forward_crouch']='Backward cycle played in reverse, with root drift removed'
(ROOT/'evidence/animated-thief-import.json').write_text(json.dumps({
    'source':FBX.name,'sha256':hashlib.sha256(FBX.read_bytes()).hexdigest(),
    'source_bones':len(rig.data.bones),'runtime_bones':len(bones),'triangles':len(indices)//3,
    'clips':provenance,'dance_duration':clips['Dance'][0],
    'source_fps':fps,'forward_axis':'+Z runtime','derived_actions_editable':True},indent=2),encoding='utf-8')
bpy.ops.file.pack_all()
bpy.data.libraries.write(str(ROOT/'art/blender/animated_thief.blend'),
                         {scene,*imported,*baked.values()},fake_user=True,compress=True)
print('ANIMATED_THIEF_READY',len(indices)//3,'triangles;',len(bones),'bones;',len(clips),'clips; Dance',clips['Dance'][0],'seconds')
