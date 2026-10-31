#pragma once
#include "game.hpp"
#include "scene.hpp"
namespace lvh {
std::vector<Light> updateWorld(Scene &, const Game &, bool alarm);
}
