#version 330 core
in float distanceDown;out vec4 color;uniform vec3 uColor;
void main(){float fade=pow(1.0-clamp(distanceDown,0.0,1.0),1.5);color=vec4(uColor,fade*.035);}
