"""Export the supplied character plus exactly the twelve runtime/derived clips.

Prune unreferenced animation buffers left by Blender's all-actions exporter. The
standalone SKIP_EXPORT path can compact an already exported GLB without Blender.
"""
from pathlib import Path
import json,struct
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'assets/exchange/thief.glb'
if not globals().get('SKIP_EXPORT',False):
    import bpy,contextlib,io
    scene=bpy.data.scenes['LVH_AnimatedThief'];bpy.context.window.scene=scene
    for o in bpy.context.view_layer.objects:o.select_set(o.type in ('MESH','ARMATURE'))
    rig=next(o for o in scene.objects if o.type=='ARMATURE')
    bpy.context.view_layer.objects.active=rig
    props=bpy.ops.export_scene.gltf.get_rna_type().properties
    mode=next(e.identifier for e in props['export_animation_mode'].enum_items if e.identifier=='ACTIONS')
    opts={'filepath':str(path),'use_selection':True,'use_active_scene':True,
          'export_animations':True,'export_animation_mode':mode,'export_force_sampling':True,
          'export_yup':True,'export_skins':True,'export_apply':False}
    with contextlib.redirect_stdout(io.StringIO()):bpy.ops.export_scene.gltf(**opts)
data=path.read_bytes();assert data[:4]==b'glTF'
chunks=[];pos=12
while pos<len(data):
    size,kind=struct.unpack_from('<II',data,pos);pos+=8
    chunks.append((kind,data[pos:pos+size]));pos+=size
doc=json.loads(next(raw for kind,raw in chunks if kind==0x4e4f534a))
binary=next(raw for kind,raw in chunks if kind==0x004e4942)
names={'Walking':'Walk','Running':'Run','LVH_CrouchBackward':'CrouchBackward',
       'LVH_CrouchLeft':'CrouchLeft','LVH_CrouchRight':'CrouchRight',
       'FunnyDancing_02':'Dance','Cherish_Pop_Dance':'DanceLong','LVH_CrouchWalk':'CrouchWalk',
       'LVH_WalkBackward':'WalkBackward','LVH_Idle':'Idle','LVH_CrouchIdle':'CrouchIdle','LVH_Interact':'Interact'}
selected=[]
for base,name in names.items():
    options=[a for a in doc['animations'] if a['name']==base or
             (a['name'].startswith(base+'.') and a['name'][len(base)+1:].isdigit())]
    assert options,base
    a=max(options,key=lambda a:int(a['name'][len(base)+1:]) if a['name']!=base else 0)
    a['name']=name;selected.append(a)
doc['animations']=selected
refs=[]
for mesh in doc.get('meshes',[]):
    for prim in mesh['primitives']:
        refs += [(prim['attributes'],k) for k in prim['attributes']]
        if 'indices' in prim:refs.append((prim,'indices'))
        for target in prim.get('targets',[]):refs += [(target,k) for k in target]
for skin in doc.get('skins',[]):
    if 'inverseBindMatrices' in skin:refs.append((skin,'inverseBindMatrices'))
for anim in selected:
    for sampler in anim['samplers']:refs += [(sampler,'input'),(sampler,'output')]
used=sorted({o[k] for o,k in refs});amap={old:new for new,old in enumerate(used)}
for o,k in refs:o[k]=amap[o[k]]
accessors=[doc['accessors'][i] for i in used]
vrefs=[]
for a in accessors:
    if 'bufferView' in a:vrefs.append((a,'bufferView'))
    if 'sparse' in a:
        for key in ['indices','values']:vrefs.append((a['sparse'][key],'bufferView'))
for image in doc.get('images',[]):
    if 'bufferView' in image:vrefs.append((image,'bufferView'))
vused=sorted({o[k] for o,k in vrefs});vmap={old:new for new,old in enumerate(vused)}
views=[];out=bytearray()
for old in vused:
    v=doc['bufferViews'][old].copy();start=v.get('byteOffset',0);size=v['byteLength']
    while len(out)%4:out.append(0)
    v['byteOffset']=len(out);v['buffer']=0;out.extend(binary[start:start+size]);views.append(v)
for o,k in vrefs:o[k]=vmap[o[k]]
doc['accessors']=accessors;doc['bufferViews']=views;doc['buffers']=[{'byteLength':len(out)}]
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
out.extend(b'\x00'*((-len(out))%4))
blob=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(out))
blob+=struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(out),0x004e4942)+out
path.write_bytes(blob)
print('Exchange character:',len(blob),'bytes;',len(selected),'animations:',[a['name'] for a in selected])
