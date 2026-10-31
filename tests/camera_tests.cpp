#include "game.hpp"
#include "mouse_look.hpp"
#include "mouse_motion.hpp"
#include "route.hpp"
#include <iostream>
#include <stdexcept>
using namespace lvh;
static void need(bool ok,const char *message){if(!ok)throw std::runtime_error(message);}
int main(){try{
    MouseMotion events;
    events.relative(12,-4);
    need(events.take()==glm::vec2(12,-4),"relative input was changed or smoothed");
    for(int n=0;n<1000;++n)
        need(events.take()==glm::vec2(0),"consumed movement was replayed on idle frames");
    events.absolutePosition(1,521,433);
    need(events.take()==glm::vec2(0),"absolute device initial position caused turn");
    for(int n=0;n<1000;++n){
        events.absolutePosition(1,521,433);
        need(events.take()==glm::vec2(0),"stationary absolute device causes endless rotation");
    }
    events.absolutePosition(1,525,433);
    need(events.take()==glm::vec2(4,0),"absolute movement used distance from screen centre");
    events.absolutePosition(2,900,700);
    need(events.take()==glm::vec2(0),"second mouse polluted first device origin");
    events.relative(3,7);events.relative(-1,-2);
    need(events.take()==glm::vec2(2,5),"batched input was not summed once");
    events.relative(10,10);events.reset();
    need(events.take()==glm::vec2(0),"focus change retained movement");
    MouseLook mouse;
    need(glm::length(mouse.sample(5000,-4000))==0,"initial cursor position turned the camera");
    auto delta=mouse.sample(5100,-3900);
    need(glm::distance(delta,glm::vec2(2.f))<.0001f,"unexpected mouse sensitivity");
    mouse.reset();
    need(glm::length(mouse.sample(-9000,8000))==0,"focus/capture reset caused a camera jump");
    MouseLook whole,split;whole.sample(0,0);split.sample(0,0);
    auto one=whole.sample(100,50);auto many=split.sample(40,20);many+=split.sample(100,50);
    need(glm::distance(one,many)<.0001f,"mouse rotation depends on event frequency");
    need(glm::length(split.sample(100,50))==0,"stationary mouse causes drift");
    // Physical recentering must establish a fresh origin, never become look input.
    MouseLook captured;captured.rebase(640,360);
    for(int n=0;n<1000;++n){
        need(glm::length(captured.sample(640,360))==0,"recenter feedback causes idle drift");
        captured.rebase(640,360);
    }
    auto rightTurn=captured.sample(740,360);
    captured.rebase(640,360);
    need(rightTurn.x>0 && rightTurn.y==0,"horizontal motion changed camera pitch");
    need(glm::length(captured.sample(640,360))==0,"turn continued after physical motion stopped");
    split.sensitivity=.01f;
    need(glm::distance(split.sample(200,50),glm::vec2(1,0))<.0001f,"sensitivity setting ignored");
    Game setting;setting.mouseSensitivity=.007f;setting.reset();
    need(std::abs(setting.mouseSensitivity-.007f)<.000001f,"retry lost mouse setting");
    Game g;
    need(!g.thirdPerson && glm::distance(g.camera(),g.eyePosition())<.0001f,"default first-person view");
    const auto pos=g.position;const auto time=g.time;
    g.toggleCamera();
    need(g.thirdPerson && g.thirdPersonVisible(),"third person must reveal the character");
    need(glm::distance(g.camera(),g.eyePosition())>2.f && !g.cameraBlocked(g.camera()),"spawn boom through the open doorway");
    need(g.position==pos && g.time==time,"switching view changed gameplay");
    g.toggleCamera();need(!g.thirdPerson,"return to first person");
    // Orbiting at rest must never turn the body, even while crouched.
    Game orbit;orbit.toggleCamera();
    float originalFacing=orbit.characterFacing();
    orbit.yaw=35;orbit.update(1.f/240,{});
    need(std::abs(orbit.characterFacing()-originalFacing)<.0001f,"orbit turned idle character");
    Input crouch;crouch.crouch=true;
    orbit.yaw=150;orbit.update(1.f/240,crouch);
    need(std::abs(orbit.characterFacing()-originalFacing)<.0001f,"orbit turned crouched character");
    // Every standing direction uses a forward cycle, facing actual movement.
    for(float viewYaw : {-90.f,25.f,170.f})
        for(auto axes : {glm::vec2(1,0),glm::vec2(-1,0),glm::vec2(0,-1),glm::vec2(0,1),glm::vec2(1,1)}){
            Game walk;walk.toggleCamera();walk.yaw=viewYaw;
            Input input;input.forward=axes.x;input.right=axes.y;
            glm::vec3 before=walk.position;walk.update(1.f/240,input);
            glm::vec3 facing(std::sin(walk.characterFacing()),0,std::cos(walk.characterFacing()));
            need(glm::dot(facing,glm::normalize(walk.position-before))>.999f,"body not facing movement");
            need(walk.locomotionClip()=="Walk","standing direction lacks forward walk cycle");
            float stopped=walk.characterFacing();walk.yaw+=60;walk.update(1.f/240,{});
            need(std::abs(walk.characterFacing()-stopped)<.0001f,"stopped body snapped to camera");
        }
    for(float side : {-1.f,1.f}){
        Game sneak;sneak.toggleCamera();Input input;input.crouch=true;input.right=side;
        sneak.update(1.f/240,input);
        need(sneak.locomotionClip()==(side>0 ? "CrouchRight" : "CrouchLeft"),"lost directional crouch clips");
        need(std::abs(sneak.bodyYaw+90)<.0001f,"crouch strafe rotated body");
    }
    Game firstLook;firstLook.yaw=40;
    need(std::abs(firstLook.characterFacing()-glm::radians(50.f))<.0001f,"first-person body did not follow mouse");
    firstLook.toggleCamera();firstLook.yaw=100;
    need(std::abs(firstLook.characterFacing()-glm::radians(50.f))<.0001f,"first-to-third heading jumped");
    firstLook.toggleCamera();
    need(std::abs(firstLook.characterFacing()-glm::radians(-10.f))<.0001f,"third-to-first did not follow look");
    g.thirdPerson=true;g.position={3.55f,0,-6};g.yaw=180;g.pitch=0;
    need(g.camera().x<3.77f && !g.cameraBlocked(g.camera()),"boom penetrated side wall");
    need(glm::distance(g.camera(),g.eyePosition())<.65f && !g.thirdPersonVisible(),"near-wall head visibility");
    g.position={3.3f,0,-4.6f};
    need(g.camera().x<3.55f,"boom penetrated a timber post");
    g.position={2.2f,0,-14};g.yaw=90;
    need(g.camera().z> -14.77f && !g.cameraBlocked(g.camera()),"boom penetrated rear wall/safe");
    g.position={-2.8f,0,-6};g.yaw=0;
    need(glm::distance(g.camera(),g.eyePosition())<.65f,"cabinet did not contract the boom");
    g.position={-1.7f,0,-2.5f};
    need(g.camera().x< -2.4f,"camera should pass over the low desk");
    g=Game();g.position={-1.5f,0,-1.25f};lookAt(g,{-2.85f,1.24f,-1.97f});
    const auto firstTarget=g.interactionTarget();g.toggleCamera();
    need(firstTarget==1 && g.interactionTarget()==1,"lamp reach changed with view");
    g.position={0,0,-12.74f};lookAt(g,{0,1.65f,Game::safeFront});
    need(g.interactionTarget()==3,"safe reach changed with view");
    g.pitch=85;g.thirdPerson=false;g.toggleCamera();
    need(g.pitch==60 && !g.cameraBlocked(g.camera()),"third-person vertical limits");
    g.state=State::Pause;g.toggleCamera();need(g.thirdPerson,"camera switched in pause");
    g.reset();need(g.thirdPerson,"retry discarded camera preference");
    Game first,third;third.thirdPerson=true;Input move;move.forward=1;
    for(int i=0;i<60;i++){first.update(1.f/240,move);third.update(1.f/240,move);}
    need(glm::distance(first.position,third.position)<.0001f,"movement depends on visual camera");
    Game routeGame;routeGame.thirdPerson=true;Route route;
    for(int i=0;i<24000 && routeGame.state!=State::Victory;i++)
        routeGame.update(1.f/240,route.next(routeGame));
    need(routeGame.state==State::Victory,"third-person route did not reach victory");
    auto cinematic=routeGame.camera();routeGame.toggleCamera();
    need(routeGame.thirdPerson && routeGame.camera()==cinematic,"V changed the finale camera");
    std::cout<<"PASS camera modes, room/prop obstruction, reach, movement, retry and complete third-person route\n";
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
