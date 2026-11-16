#include "game.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace lvh;
void require(bool value, const char *label) {
    if (!value)
        throw std::runtime_error(label);
    std::cout << "PASS " << label << '\n';
}
int main() {
    try {
        glm::mat4 identity(1);
        require(pointInBox({0, 0, 0}, identity, {1, 1, 1}), "box center");
        require(pointInBox({1, 0, 0}, identity, {1, 1, 1}), "box boundary");
        require(!pointInBox({1.01f, 0, 0}, identity, {1, 1, 1}), "outside box");
        auto rotated = glm::translate(identity, glm::vec3(2, 1, 0)) *
                       glm::rotate(identity, glm::radians(45.f), glm::vec3(0, 0, 1));
        glm::vec3 local(.9f, 0, 0);
        auto world = glm::vec3(rotated * glm::vec4(local, 1));
        require(pointInBox(world, rotated, {1, .03f, .03f}), "rotated thin box true hit");
        require(!pointInBox({2.7f, .3f, 0}, rotated, {1, .03f, .03f}),
                "world AABB false positive rejected");
        Game g;
        const auto &last = g.lasers[5];
        require(sampledBodyHits(last, {0, 0, -9.5f}, 1.67f), "standing body hits last beam");
        require(!sampledBodyHits(last, {0, 0, -9.5f}, .88f), "crouching body clears last beam");
        g.position = {0, 0, -9.5f};
        Input idle;
        g.update(1.f / 240, idle);
        require(g.state == State::Alarm, "laser causes alarm");
        Input retry;
        retry.retry = true;
        g.update(1.f / 240, retry);
        require(g.state == State::Playing && g.time == 0 && g.position.z == -.85f && !g.safeOpened,
                "retry resets simulation");
        g.state = State::Pause;
        auto pos = g.position;
        g.update(1, idle);
        require(g.time == 0 && g.position == pos, "pause freezes simulation");
        Game fast, slow;
        Input move;
        move.forward = -1;
        for (int j = 0; j < 120; j++)
            fast.update(1.f / 120, move);
        for (int j = 0; j < 30; j++)
            slow.update(1.f / 30, move);
        require(glm::distance(fast.position, slow.position) < .09f,
                "movement independent of render rate");
        Game safe;
        safe.position = {0, 0, -12.74f};
        safe.lastCrossed = true;
        safe.interact();
        require(safe.safeOpened, "reachable safe interaction");
        for (int j = 0; j < 2640; j++)
            safe.update(1.f / 240, idle);
        require(safe.state == State::Victory, "safe opening leads to victory");
        std::cout << "All logic tests passed\n";
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "FAIL " << e.what() << '\n';
        return 1;
    }
}
