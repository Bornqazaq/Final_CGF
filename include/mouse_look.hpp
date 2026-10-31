#pragma once
#include <glm/glm.hpp>
#include <cmath>
namespace lvh {
struct MouseLook {
    float sensitivity = .02f;
    bool first = true;
    double x = 0, y = 0;
    void reset() { first = true; }
    glm::vec2 sample(double nextX, double nextY) {
        glm::vec2 delta(0);
        if (!std::isfinite(nextX) || !std::isfinite(nextY)) {
            reset();
            return delta;
        }
        if (!first)
            delta = glm::vec2(float(nextX-x),float(nextY-y))*sensitivity;
        first = false;
        x = nextX; y = nextY;
        return delta;
    }
};
} // namespace lvh
