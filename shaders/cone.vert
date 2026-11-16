#version 330 core
layout(location=0)in vec3 aPosition;
uniform mat4 uModel,uView,uProjection;
out float distanceDown;
void main(){distanceDown=-aPosition.y/3.4;gl_Position=uProjection*uView*uModel*vec4(aPosition,1);}
