#include "route.hpp"
#include <algorithm>
#include <cmath>
namespace lvh {
void lookAt(Game &g, glm::vec3 point) {
    glm::vec3 d = glm::normalize(point - g.eyePosition());
    g.yaw = glm::degrees(std::atan2(d.z, d.x));
    g.pitch = glm::degrees(std::asin(std::clamp(d.y, -1.f, 1.f)));
}
Input walkTo(Game &g, glm::vec2 target, bool crouch) {
    glm::vec2 delta = target - glm::vec2(g.position.x, g.position.z);
    Input in;
    in.crouch = crouch;
    if (glm::length(delta) < .025f)
        return in;
    glm::vec2 direction = glm::normalize(delta);
    glm::vec3 f = g.forward();
    f.y = 0;
    f = glm::normalize(f);
    glm::vec3 r = glm::normalize(glm::cross(f, glm::vec3(0, 1, 0)));
    float speed = std::min(1.f, glm::length(delta) * 8.f);
    in.forward = glm::dot(direction, glm::vec2(f.x, f.z)) * speed;
    in.right = glm::dot(direction, glm::vec2(r.x, r.z)) * speed;
    return in;
}
Input Route::next(Game &g, bool allowFinal) {
    Input in;
    in.crouch = true;
    if (g.state != State::Playing)
        return in;
    g.yaw = -90;
    g.pitch = 0;
    if (beam < 6) {
        float z = g.lasers[beam].center.z;
        if (g.position.z > z + .37f)
            return walkTo(g, {0, z + .30f}, true);
        if (beam == 5 && !allowFinal)
            return in;
        if (!crossing) {
            Game prediction = g;
            Input crossingInput;
            crossingInput.forward = 1;
            crossingInput.crouch = true;
            bool safe = true;
            for (int i = 0; i < 160; i++) {
                prediction.update(1.f / 240, crossingInput);
                if (prediction.state == State::Alarm) {
                    safe = false;
                    break;
                }
            }
            if (!safe)
                return in;
            crossing = true;
        }
        in.forward = 1;
        if (g.position.z < z - .38f) {
            beam++;
            crossing = false;
        }
        return in;
    }
    if (g.position.z > -12.68f)
        return walkTo(g, {0, -12.74f}, true);
    in.crouch = false;
    lookAt(g, {0, 1.65f, Game::safeFront});
    if (!g.safeOpened)
        in.interact = true;
    if (g.safeOpened)
        complete = true;
    return in;
}
} // namespace lvh
