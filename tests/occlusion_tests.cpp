#include "animation.hpp"
#include "scene.hpp"
#include <GLFW/glfw3.h>
#include <iostream>
#include <stdexcept>
using namespace lvh;
int main(int argc,char **argv){
    if(argc!=2 || !glfwInit())return 1;
    glfwWindowHint(GLFW_VISIBLE,GLFW_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT,GLFW_TRUE);
#endif
    auto *window=glfwCreateWindow(640,480,"Occlusion test",nullptr,nullptr);
    if(!window)return 1;
    glfwMakeContextCurrent(window);
    if(!gladLoadGL(reinterpret_cast<GLADloadfunc>(glfwGetProcAddress)))return 1;
    int result=0;
    try{
        fs::path root=argv[1];Scene scene;scene.load(root/"assets/thief.scene");
        Animator animator;animator.load(root/"assets/thief.lvanim");animator.update("Idle",0,1);
        scene.skinPalette=animator.palette;scene.showCharacter=true;
        scene.meshes.push_back(Mesh::box());
        scene.materials.push_back({"Laser",{1,.003f,.001f},0,16,7,0});
        Node beam;beam.name="TestBeam";beam.mesh=int(scene.meshes.size())-1;
        beam.material=int(scene.materials.size())-1;beam.dynamic=true;
        beam.local=glm::scale(glm::translate(glm::mat4(1),glm::vec3(0,1.05f,-1)),glm::vec3(4,.024f,.024f));
        scene.nodes.push_back(beam);
        Renderer renderer(root/"shaders");renderer.width=640;renderer.height=480;
        std::vector<Light> lights={{{0,2,3},{1,1,1},{0,-1,0},1}};
        auto render=[&](int mesh,const char *name){
            scene.nodes.back().mesh=mesh;
            renderer.frame(scene,glm::lookAt(glm::vec3(0,1.05f,3),glm::vec3(0,1.05f,0),glm::vec3(0,1,0)),{0,1.05f,3},lights,false,0,0);
            saveFramebuffer(root/"evidence/screenshots"/name,640,480);
            std::vector<unsigned char> pixels(640*480*3);glReadPixels(0,0,640,480,GL_RGB,GL_UNSIGNED_BYTE,pixels.data());
            return pixels;
        };
        scene.characterPresent=false;
        auto empty=render(-1,"laser-occlusion-empty.png");
        scene.characterPresent=true;
        auto baseline=render(-1,"laser-occlusion-baseline.png");
        auto behind=render(beam.mesh,"laser-occlusion-behind.png");
        int differences=0;
        for(int y=235;y<245;y++)for(int x=310;x<330;x++)for(int c=0;c<3;c++)
            if(std::abs(int(baseline[(y*640+x)*3+c])-int(behind[(y*640+x)*3+c]))>2)differences++;
        std::cout<<"Occluded character interior differences: "<<differences<<"\n";
        if(differences)throw std::runtime_error("beam visible through character");
        int glowLeaks=0;
        for(int y=225;y<255;y++)for(int x=250;x<390;x++){
            int i=(y*640+x)*3;
            bool body=std::abs(int(baseline[i])-int(empty[i]))+
                      std::abs(int(baseline[i+1])-int(empty[i+1]))+
                      std::abs(int(baseline[i+2])-int(empty[i+2]))>20;
            if(body && behind[i]>baseline[i]+3)glowLeaks++;
        }
        std::cout<<"Glow leaking onto foreground character: "<<glowLeaks<<" pixels\n";
        if(glowLeaks)throw std::runtime_error("laser bloom leaks across character silhouette");
        scene.nodes.back().local[3].z=1;
        auto front=render(beam.mesh,"laser-occlusion-front.png");
        int center=(240*640+320)*3;
        if(front[center]<150 || front[center]<=front[center+1]*1.4f)
            throw std::runtime_error("unoccluded beam not visible");
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("OpenGL error");
        std::cout<<"PASS actual GPU character occlusion and visible foreground laser\n";
    }catch(const std::exception &e){std::cerr<<e.what()<<'\n';result=1;}
    glfwDestroyWindow(window);glfwTerminate();return result;
}
