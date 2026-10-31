#pragma once
#include <glm/glm.hpp>
namespace lvh {
struct MouseLook {
    static constexpr float sensitivity = .045f;
    bool first = true;
    double x = 0, y = 0;
    void reset() { first = true; }
    glm::vec2 sample(double nextX, double nextY) {
        glm::vec2 delta(0);
        if (!first)
            delta = glm::vec2(float(nextX-x),float(nextY-y))*sensitivity;
        first = false;
        x = nextX; y = nextY;
        return delta;
    }
};
} // namespace lvh
