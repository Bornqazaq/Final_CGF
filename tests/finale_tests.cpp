#include "game.hpp"
#include <iostream>
#include <stdexcept>
using namespace lvh;
static void need(bool b,const char *m){if(!b)throw std::runtime_error(m);}
int main(){try{
    Game g;g.position={0,0,-12.74f};g.lastCrossed=true;g.danceDuration=1.25f;
    need(g.interactionTarget()==3,"safe interaction was not moved with the room");
    g.interact();need(g.state==State::Finale,"safe must begin a cinematic");
    auto p=g.position;Input move;move.forward=move.right=1;move.interact=move.retry=true;
    for(int i=0;i<816;i++)g.update(1.f/240,move);
    need(g.state==State::Finale && g.position==p,"opening must lock gameplay input");
    for(int i=0;i<280;i++)g.update(1.f/240,move);
    need(g.state==State::Finale,"victory appeared before the dance ended");
    auto t=g.safeTime;g.state=State::Pause;g.update(1,move);
    need(g.safeTime==t,"pause must stop the cinematic");g.state=State::Finale;
    for(int i=0;i<30;i++)g.update(1.f/240,Input{});
    need(g.state==State::Victory,"full dance did not finish the cinematic");
    t=g.safeTime;g.update(2,Input{});need(g.safeTime==t,"dance must hold its final pose");
    g.reset();need(g.state==State::Playing&&!g.safeOpened&&g.safeTime==0&&g.danceDuration==1.25f,"retry failed to reset/preserve asset duration");
    need(g.blocked({0,0,-14.7f})&&!g.blocked({0,0,-12.74f}),"room bounds mismatch");
    std::cout<<"PASS moved safe, input lock, full dance duration, pause, final hold, retry, room bounds\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
