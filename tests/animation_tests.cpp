#include "animation.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <array>
using namespace lvh;
static void need(bool b,const char *m){if(!b)throw std::runtime_error(m);}
int main(int argc,char **argv){
    try {
        need(argc==2,"animation file argument required");
        Animator a;a.load(argv[1]);
        need(a.bones.size()<=64 && a.bones.size()==52,"weighted skeleton palette");
        for(auto n:{"Idle","Walk","WalkBackward","CrouchIdle","CrouchWalk","CrouchBackward","CrouchLeft","CrouchRight","Dance","DanceLong","Interact","Run"})
            need(a.duration(n)>0,"required animation absent");
        need(std::abs(a.duration("Dance")-7.5f)<.001f,"dance length must come from source");
        a.update("Dance",1,1);auto end=a.palette;
        a.update("Dance",2,1);
        for(size_t i=0;i<end.size();i++)for(int c=0;c<4;c++)for(int r=0;r<4;r++)
            need(std::abs(end[i][c][r]-a.palette[i][c][r])<.0001f,"dance wraps after its end");
        for(const auto &clip:a.clips)for(const auto &p:clip.samples){
            need(std::isfinite(p.translation.x)&&std::isfinite(p.translation.y)&&std::isfinite(p.translation.z),"nonfinite pose");
            need(std::abs(glm::length(p.rotation)-1.f)<.0001f,"invalid quaternion");
        }
        std::ifstream mesh(std::filesystem::path(argv[1]).parent_path()/"meshes/thief_meshy.lvhm",std::ios::binary);
        std::array<unsigned,4> header{};mesh.read(reinterpret_cast<char*>(header.data()),16);
        need(bool(mesh)&&header[1]==1,"runtime skin mesh header");
        std::vector<std::array<float,16>> vertices(header[2]);
        mesh.read(reinterpret_cast<char*>(vertices.data()),std::streamsize(vertices.size()*sizeof(vertices[0])));
        need(bool(mesh),"runtime skin mesh data");
        for(const auto &clip:a.clips){
            if(clip.name.rfind("Crouch",0)!=0)continue;
            float height=-100,sole=100;
            for(unsigned frame=0;frame<clip.frames;frame++){
                a.update(clip.name,float(frame)/(clip.frames-1),1);
                for(const auto &v:vertices){
                    glm::vec4 p(0),bind(v[0],v[1],v[2],1);
                    for(int influence=0;influence<4;influence++)
                        p+=(a.palette.at(size_t(v[12+influence]))*bind)*v[8+influence];
                    height=std::max(height,p.y);sole=std::min(sole,p.y);
                }
            }
            std::cout<<clip.name<<" height="<<height<<" sole="<<sole<<'\n';
            need(height<1.34f,"crouch hood exceeds collision clearance");
            need(sole>-.025f,"crouch shoes penetrate the floor");
        }
        std::cout<<"PASS imported clips, 52-bone palette, 7.5s one-shot dance and finite poses\n";
    } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
