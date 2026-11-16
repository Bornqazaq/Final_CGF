#pragma once
#include "game.hpp"
namespace lvh {
// Reproducible input driver, using the same controller/collision code as a player.
// It never teleports the player or disables a laser.
class Route {
  public:
    int beam = 0;
    bool crossing = false;
    bool complete = false;
    Input next(Game &, bool allowFinal = true);
};
Input walkTo(Game &, glm::vec2 target, bool crouch);
void lookAt(Game &, glm::vec3 target);
} // namespace lvh
