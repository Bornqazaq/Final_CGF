#include "director.hpp"
#include "fixed_step.hpp"
#include <iostream>
#include <stdexcept>
using namespace lvh;
void need(bool b, const char *s) {
    if (!b)
        throw std::runtime_error(s);
}
int main() {
    try {
        Game game;
        Director director;
        bool off = false, cam = false;
        for (int n = 0; n < int(Director::duration * 240); n++) {
            auto input = director.next(game, 1.f / 240);
            game.update(1.f / 240, input);
            off |= !game.lamp;
            cam |= game.cctvView == 1;
        }
        need(off && cam, "demo must exercise both desk interactions");
        need(director.sawAlarm && game.retries == 1, "demo must hit a laser and reset once");
        need(director.sawVictory && game.safeOpened,
             "demo must finish through the real win condition");
        std::cout << "PASS complete capture script, three interactions, alarm, reset, "
                     "uninterrupted victory\n";
        FixedStep clock;
        Input edge;
        edge.interact = true;
        int fired = 0;
        clock.advance(.0001, edge, [&](float, const Input &i) { fired += i.interact; });
        clock.advance(.009, Input{}, [&](float, const Input &i) { fired += i.interact; });
        need(fired == 1, "interaction edge lost or duplicated between render frames");
        Game fast, slow;
        Input move;
        move.forward = 1;
        FixedStep a, b;
        for (int i = 0; i < 600; i++)
            a.advance(1. / 120, move, [&](float dt, const Input &in) { fast.update(dt, in); });
        for (int i = 0; i < 30; i++)
            b.advance(1. / 6, move, [&](float dt, const Input &in) { slow.update(dt, in); });
        need(fast.state == State::Alarm && slow.state == State::Alarm,
             "slow frame tunneled through beam");
        need(glm::distance(fast.position, slow.position) < .02f,
             "collision depends on render rate");
        std::cout << "PASS retained input edges and collision at 6 versus 120 render FPS\n";
        return 0;
    } catch (const std::exception &e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
