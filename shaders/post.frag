#version 330 core
// Fitted curve: Krzysztof Narkowicz (2016), CC0. See LICENSES/Tone-mapping.txt.
// https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
in vec2 uv;out vec4 color;uniform sampler2D uScene;uniform vec3 uTint;
void main(){
 vec3 hdr=texture(uScene,uv).rgb;
 vec2 px=1.0/vec2(textureSize(uScene,0));
 vec3 glow=vec3(0);
 for(int x=-2;x<=2;x++)for(int y=-2;y<=2;y++){vec3 c=texture(uScene,uv+vec2(x,y)*px*2.4).rgb;glow+=max(c-1.1,0.0)/25.0;}
 hdr+=glow*.24;
 vec3 mapped=(hdr*(2.51*hdr+.03))/(hdr*(2.43*hdr+.59)+.14);
 mapped=pow(clamp(mapped,0.0,1.0),vec3(1.0/2.2));
 float vignette=1.0-.20*pow(length((uv-.5)*1.25),2.0);
 color=vec4(mapped*vignette*uTint,1);
}
