#include "world.hpp"
#include <cmath>
namespace lvh {
std::vector<Light> updateWorld(Scene &s, const Game &g, bool alarm) {
    for (int i = 0; i < 6; i++) {
        const auto &l = g.lasers[i];
        s.setLocal("Laser" + std::to_string(i), glm::scale(l.matrix, l.halfSize * 2.f));
        for (int side : {-1, 1})
            s.setLocal("EmitterRoot" + std::to_string(i) + "_" + std::to_string(side),
                       l.matrix *
                           glm::translate(glm::mat4(1), glm::vec3(side * l.halfSize.x, 0, 0)));
    }
    auto animate = [&](const std::string &n, const glm::mat4 &m) {
        int i = s.find(n);
        if (i >= 0)
            s.nodes[i].local = s.nodes[i].base * m;
    };
    animate("SafeWheel", glm::rotate(glm::mat4(1), std::min(g.safeTime, 1.f) * glm::radians(150.f),
                                     glm::vec3(0, 0, 1)));
    animate("SafeDoorPivot",
            glm::rotate(glm::mat4(1), -glm::smoothstep(1.f, 3.3f, g.safeTime) * glm::radians(100.f),
                        glm::vec3(0, 1, 0)));
    for (int i = 0; i < 3; i++)
        animate("SafeBolt" + std::to_string(i),
                glm::translate(glm::mat4(1),
                               glm::vec3(-.22f * glm::smoothstep(.5f, 1.15f, g.safeTime), 0, 0)));
    float angle = .65f * std::sin(g.time * .5f);
    for (int i = 0; i < 2; i++)
        animate("SpotPivot" + std::to_string(i),
                glm::rotate(glm::mat4(1), i ? -angle : angle, glm::vec3(0, 1, 0)));
    s.lampOn = g.lamp || alarm;
    s.updateWorld();
    glm::vec3 warm = alarm ? glm::vec3(1, .015f, .006f) : glm::vec3(1, .60f, .25f);
    glm::vec3 cool = alarm ? glm::vec3(1, .01f, .005f) : glm::vec3(.40f, .58f, 1);
    std::vector<Light> lights = {
        {{-3.30f, 2.37f, -5}, warm, {0, -1, 0}, .92f},
        {{3.30f, 2.37f, -4}, warm, {0, -1, 0}, 1.05f},
        {{-3.30f, 2.37f, -13.6f}, warm, {0, -1, 0}, 1.15f},
        {{3.30f, 2.37f, -13.6f}, warm, {0, -1, 0}, 1.15f},
        {{-3.5f, 2.7f, -2}, cool, {0, -1, 0}, .71f},
        {{-2.85f, 1.24f, -1.97f}, warm, {0, -1, 0}, s.lampOn ? .71f : 0.f}};
    if (g.safeOpened) {
        lights[2] = {{-2.0f, 2.7f, -11.4f}, warm, {0,-1,0}, 1.45f};
        lights[3] = {{2.3f, 2.4f, -11.2f}, warm, {0,-1,0}, 1.55f};
    }
    for (int i = 0; i < 2; i++) {
        int n = s.find("SpotPivot" + std::to_string(i));
        glm::mat4 m = n < 0 ? glm::mat4(1) : s.nodes[n].world;
        glm::vec3 direction =
            glm::normalize(glm::vec3(m * glm::vec4(0, -std::cos(.335f), -std::sin(.335f), 0)));
        glm::vec3 position = glm::vec3(m * glm::vec4(0, -.43f, -.13f, 1));
        lights.push_back({position, warm, direction, 3.0f, .93f, .83f});
    }
    return lights;
}
} // namespace lvh
