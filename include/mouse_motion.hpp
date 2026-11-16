#pragma once
#include <glm/glm.hpp>
#include <cstdint>
#include <unordered_map>
namespace lvh {
// Motion events are consumed once, independently of cursor capture or frame rate.
class MouseMotion {
    glm::vec2 pending{0};
    std::unordered_map<std::uintptr_t,glm::vec2> absolute;
public:
    void relative(float x,float y) { pending+=glm::vec2(x,y); }
    void absolutePosition(std::uintptr_t device,float x,float y) {
        auto [it,inserted]=absolute.emplace(device,glm::vec2(x,y));
        if (!inserted) { pending+=glm::vec2(x,y)-it->second; it->second={x,y}; }
    }
    glm::vec2 take() { auto result=pending;pending=glm::vec2(0);return result; }
    void reset() { pending=glm::vec2(0);absolute.clear(); }
};
}
