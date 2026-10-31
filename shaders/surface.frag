#version 330 core
in vec3 vWorld,vNormal; in vec2 vUV; in vec4 vShadow;
out vec4 fragColor;
struct Light{vec3 position,color,direction;float power,cutoff,outer;};
uniform Light uLights[8]; uniform int uLightCount;
uniform sampler2D uTexture,uShadow;
uniform vec3 uColor,uEye; uniform float uSpecular,uShine,uEmission,uTime;
uniform bool uScreen,uAlarm;
float shadow(){
 vec3 q=vShadow.xyz/vShadow.w*.5+.5;
 if(q.z>1.0||q.x<0.0||q.x>1.0||q.y<0.0||q.y>1.0)return 0.0;
 vec2 size=1.0/vec2(textureSize(uShadow,0)); float value=0.0;
 for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++)
 value+=q.z-.0007>texture(uShadow,q.xy+vec2(x,y)*size).r?1.0:0.0;
 return value/9.0;
}
void main(){
 vec3 base=texture(uTexture,vUV).rgb*uColor;
 if(uScreen){base*=.93+.07*sin(vUV.y*520.0);fragColor=vec4(base,1);return;}
 vec3 N=normalize(vNormal),V=normalize(uEye-vWorld);
 vec3 ambient=uAlarm?vec3(.15,.018,.012):vec3(.095,.082,.067);
 vec3 result=base*ambient;
 vec3 moon=uAlarm?vec3(.12,.008,.004):vec3(.19,.28,.46);
 result+=base*moon*max(dot(N,normalize(vec3(-.75,.45,.4))),0.0)*(1.0-.8*shadow());
 for(int i=0;i<8;i++){
 if(i>=uLightCount)break;
 vec3 delta=uLights[i].position-vWorld;
 float dist=length(delta);vec3 L=delta/max(dist,.001);
 float cone=1.0;
 if(uLights[i].cutoff>0.0)cone=smoothstep(uLights[i].outer,uLights[i].cutoff,dot(-L,uLights[i].direction));
 float att=uLights[i].power/(1.0+.20*dist+.095*dist*dist);
 float diff=max(dot(N,L),0.0);
 float spec=diff>0.0?pow(max(dot(N,normalize(L+V)),0.0),uShine)*uSpecular:0.0;
 result+=(base*diff+vec3(spec))*uLights[i].color*att*cone;
 }
 result+=base*uEmission;
 fragColor=vec4(result,1.0);
}
