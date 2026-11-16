#include "game.hpp"
#include <algorithm>
#include <cmath>
namespace lvh {
// IMPORT M2 5 18
Game::Game() {
    updateLasers();
}
void Game::reset() {
    int attempts = retries + 1;
    float danceLength = danceDuration;
    bool preferredView = thirdPerson;
    float preferredSensitivity = mouseSensitivity;
    auto rates=refreshRates;int limit=fpsLimit,custom=customFPS,refresh=monitorHz;
    *this = Game();
    refreshRates=std::move(rates);fpsLimit=limit;customFPS=custom;monitorHz=refresh;
    danceDuration = danceLength;
    thirdPerson = preferredView;
    mouseSensitivity = preferredSensitivity;
    retries = attempts;
}
// IMPORT N2 35 126
void Game::updateLasers() {
    const float depths[] = {-2.9f, -4.2f, -5.6f, -6.9f, -8.15f, -9.5f};
    for (int i = 0; i < 6; i++) {
        auto &l = lasers[i];
        float height = 1.35f;
        float angle = 0;
        if (i == 0)
            height = 2.35f + .55f * std::sin(time * .65f);
        if (i == 1)
            height = 1.0f + .62f * std::sin(time * .8f + .8f);
        if (i == 2) {
            height = 2.35f;
            angle = glm::radians(10.f) * std::sin(time * .7f);
        }
        if (i == 3)
            height = 1.1f + .60f * std::sin(time * .6f + 1.3f);
        if (i == 4) {
            height = 1.65f;
            angle = glm::radians(7.f) * std::sin(time * .75f);
        }
        if (i == 5)
            height = 1.42f;
        l.center = {0, height, depths[i]};
        l.angle = angle;
        // A left-wall pivot makes the rotating beam's origin explicit.
        glm::vec3 pivot(-3.65f, height, depths[i]);
        l.halfSize.x = 3.65f / std::cos(angle);
        l.matrix = glm::translate(glm::mat4(1), pivot) *
                   glm::rotate(glm::mat4(1), angle, glm::vec3(0, 0, 1)) *
                   glm::translate(glm::mat4(1), glm::vec3(l.halfSize.x, 0, 0));
    }
}
// IMPORT N1 159 170
// IMPORT M2 171 176
// IMPORT N3 177 197
void Game::interact() {
// IMPORT N3 199 209
// IMPORT M3 210 218
}
void Game::update(float dt, const Input &i) {
// IMPORT M3 221 236
// IMPORT N1 237 271
// IMPORT M3 272 277
// IMPORT N3 278 293
}
} // namespace lvh
