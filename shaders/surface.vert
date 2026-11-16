#version 330 core
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec2 aUV;
layout(location=3) in vec4 aWeights;
layout(location=4) in vec4 aJoints;
layout(location=5) in mat4 aInstance;
uniform mat4 uModel,uView,uProjection,uLightVP;
uniform bool uInstanced,uSkinned;
uniform mat4 uBones[64];
out vec3 vWorld,vNormal;
out vec2 vUV;
out vec4 vShadow;
void main(){
 mat4 skin=mat4(1.0);
 if(uSkinned) skin=uBones[int(aJoints.x)]*aWeights.x+uBones[int(aJoints.y)]*aWeights.y+uBones[int(aJoints.z)]*aWeights.z+uBones[int(aJoints.w)]*aWeights.w;
 mat4 model=uInstanced?aInstance:uModel;
 vec4 p=model*skin*vec4(aPosition,1.0);
 vWorld=p.xyz;
 vNormal=normalize(transpose(inverse(mat3(model*skin)))*aNormal);
 vUV=aUV; vShadow=uLightVP*p;
 gl_Position=uProjection*uView*p;
}
