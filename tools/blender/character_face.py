"""Refined, human facial planes and a deep open hood for the thief character."""
import math
from common import *
from character_mesh import weighted,constant,tube

def build_face(skin,lip,brow,eye,iris,pupil,nostril_mat,cloth,lining):
    # A smooth ring-built head keeps the chin, cheeks and jaw readable in profile.
    verts=[];uvs=[];faces=[];rings=49;segments=64
    profile=[
        (1.515,.050,.051),(1.55,.072,.073),(1.60,.096,.087),
        (1.65,.112,.097),(1.70,.112,.103),(1.75,.105,.107),
        (1.79,.083,.089),(1.805,.035,.045)
    ]
    for j in range(rings):
        t=j/(rings-1);z=1.515+t*.29
        for pi in range(len(profile)-1):
            za,xa,ya=profile[pi];zb,xb,yb=profile[pi+1]
            if za<=z<=zb+1e-6:
                q=(z-za)/(zb-za);rx=xa+(xb-xa)*q;ry=ya+(yb-ya)*q
                break
        for k in range(segments):
            a=math.tau*k/segments;x=rx*math.cos(a);y=ry*math.sin(a)
            front=max(0,-math.sin(a))**12
            # Soft sculpted bridge and cheekbones, with a shallow eye socket.
            bridge=.008*math.exp(-(x/.010)**2-((z-1.681)/.024)**2)
            tip=.005*math.exp(-(x/.014)**2-((z-1.658)/.010)**2)
            nose=bridge+tip
            mouth=.0035*math.exp(-(x/.032)**4-((z-1.608)/.010)**2)
            cheeks=.005*math.exp(-((abs(x)-.060)/.027)**2-((z-1.660)/.028)**2)
            sockets=.0045*math.exp(-((abs(x)-.043)/.023)**2-((z-1.704)/.014)**2)
            y-=front*(nose+mouth+cheeks-sockets)
            verts.append((x,y,z));uvs.append((k/segments,t))
    for j in range(rings-1):
        for k in range(segments):
            q=(k+1)%segments
            faces.append((j*segments+k,j*segments+q,(j+1)*segments+q,(j+1)*segments+k))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple((rings-1)*segments+k for k in range(segments)))
    weighted(face_mesh('Face',verts,faces,skin,uvs),constant('Head'))

    # Eyes sit within the face instead of floating on it; thin lids follow each eyeball.
    for side in [-1,1]:
        x=side*.040
        eye_y=-.097;eye_z=1.704
        eye_rx=.0135;eye_ry=.0046;eye_rz=.0048
        weighted(sphere('Eye',(x,eye_y,eye_z),(eye_rx,eye_ry,eye_rz),eye,28,16),constant('Head'))
        weighted(sphere('Iris',(x,-.1021,eye_z),(.0048,.0014,.0045),iris,24,12),constant('Head'))
        weighted(sphere('Pupil',(x,-.1034,eye_z),(.0021,.0007,.0025),pupil,20,12),constant('Head'))
        for upper in [True,False]:
            points=[]
            for i in range(13):
                t=i/12;dx=(t-.5)*.025;dz=(1 if upper else -1)*.0047*math.sin(t*math.pi)
                surface=eye_y-eye_ry*math.sqrt(max(0,1-(dx/eye_rx)**2-(dz/eye_rz)**2))-.0005
                points.append((x+dx,surface,eye_z+dz))
            tube('Eyelid',points,[.00115]*len(points),skin,constant('Head'),10)

        # A soft, slightly serious brow follows the rounded forehead.
        points=[];radii=[]
        for i in range(11):
            t=i/10;local_x=.020+.050*t;bx=side*local_x
            bz=1.715+.005*t+.001*math.sin(math.pi*t)
            rx=.108;ry=.105
            by=-ry*math.sqrt(max(.10,1-(local_x/rx)**2))-.002
            points.append((bx,by,bz))
            radii.append(.00135+.00075*math.sin(math.pi*t))
        tube('Eyebrow',points,radii,brow,constant('Head'),10)

        # Small, warm nostril shadows; the nose itself remains part of the face sculpt.
        weighted(sphere('Nostril',(side*.0065,-.1070,1.655),(.0015,.0007,.0011),nostril_mat,18,10),constant('Head'))

        # Ears are tucked partly under the hood, as in the approved reference.
        weighted(sphere('Ear',(side*.101,.004,1.668),(.012,.012,.024),skin,24,16),constant('Head'))

    # Gentle closed mouth: one clear lip line and a subtle lower lip.
    weighted(sphere('NoseBridge',(0,-.108,1.667),(.014,.012,.023),skin,32,20),constant('Head'))
    points=[]
    for i in range(13):
        t=i/12;mx=(t-.5)*.046
        z=1.608-.0018*abs(2*t-1)
        base_ry=.090;base_rx=.100
        y=-base_ry*math.sqrt(max(.05,1-(mx/base_rx)**2))
        y-=.0035*math.exp(-(mx/.032)**4)
        points.append((mx,y-.002,z))
    tube('MouthLine',points,[.00135]*len(points),lip,constant('Head'),10)
    lower=[]
    for i in range(9):
        t=i/8;mx=(t-.5)*.040
        z=1.604+.0006*math.sin(math.pi*t)
        y=-.090*math.sqrt(max(.05,1-(mx/.100)**2))
        lower.append((mx,y-.0015,z))
    tube('LowerLip',lower,[.0010+.00035*math.sin(math.pi*i/8) for i in range(9)],skin,constant('Head'),10)

    # The hoodie remains deep and open around the face.
    verts=[];uvs=[];faces=[];n=56
    for j in range(9):
        t=j/8;y=-.146+t*.285;rx=.148*(1-.27*t);rz=.185*(1-.18*t)
        for k in range(n):
            a=math.tau*k/n;x=rx*math.sin(a);z=1.674+rz*math.cos(a)
            z+=.025*max(0,math.cos(a))**12*(1-t)
            yy=y-.030*max(0,math.cos(a))**6*(1-t)
            verts.append((x,yy,z));uvs.append((k/n,t))
    for j in range(8):
        for k in range(n):
            q=(k+1)%n
            faces.append((j*n+k,(j+1)*n+k,(j+1)*n+q,j*n+q))
    faces.append(tuple(8*n+k for k in range(n)))
    outer_count=len(verts)
    outer_faces=[tuple(reversed(f)) for f in faces]
    inner=[(x*.96,y+.004,1.674+(z-1.674)*.96) for x,y,z in verts]
    combined=outer_faces+[tuple(i+outer_count for i in f) for f in faces]
    for k in range(n):
        q=(k+1)%n;combined.append((k,q,q+outer_count,k+outer_count))
    weighted(face_mesh('HoodShell',verts+inner,combined,cloth,uvs+uvs),constant('Head'))
    for row in range(2):
        points=[]
        for k in range(n+1):
            a=math.tau*k/n
            points.append((.148*math.sin(a),-.146-.030*max(0,math.cos(a))**6+row*.008,1.674+.185*math.cos(a)+.025*max(0,math.cos(a))**12))
        tube('HoodBinding',points,[.007]*len(points),lining,constant('Head'),8)