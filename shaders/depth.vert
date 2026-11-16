#version 330 core
layout(location=0)in vec3 aPosition;
layout(location=3)in vec4 aWeights;
layout(location=4)in vec4 aJoints;
layout(location=5)in mat4 aInstance;
uniform mat4 uModel,uLightVP,uBones[64];
uniform bool uInstanced,uSkinned;
void main(){
 mat4 skin=mat4(1);
 if(uSkinned)skin=uBones[int(aJoints.x)]*aWeights.x+uBones[int(aJoints.y)]*aWeights.y+uBones[int(aJoints.z)]*aWeights.z+uBones[int(aJoints.w)]*aWeights.w;
 gl_Position=uLightVP*(uInstanced?aInstance:uModel)*skin*vec4(aPosition,1);
}
