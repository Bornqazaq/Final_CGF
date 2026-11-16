#pragma once
#include "route.hpp"
namespace lvh {
// Reproducible demo inputs use the normal controller and collision system.
// This is a capture/test aid, not an alternative game mode or a prerecorded scene.
class Director {
    Route route;
    bool lampOff = false, lampOn = false, camera = false, retried = false;

  public:
    float elapsed = 0;
    bool sawAlarm = false, sawVictory = false;
    Input next(Game &, float dt);
    std::string caption() const;
    bool diagnostics() const {
        return elapsed >= 84 && elapsed < 99;
    }
    static constexpr float duration = 225;
};
} // namespace lvh
