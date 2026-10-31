#include "route.hpp"
#include <iostream>
#include <stdexcept>
using namespace lvh;
void need(bool x, const char *m) {
    if (!x)
        throw std::runtime_error(m);
}
static void move(Game &g, glm::vec2 target, bool crouch) {
    for (int i = 0; i < 5000; i++) {
        g.update(1.f / 240, walkTo(g, target, crouch));
        need(g.state == State::Playing, "unexpected alarm during interaction approach");
        if (glm::distance(glm::vec2(g.position.x, g.position.z), target) < .028f)
            return;
    }
    throw std::runtime_error("could not reach interaction");
}
int main() {
    try {
        Game g;
        move(g, {-1.5f, -1.25f}, false);
        lookAt(g, {-2.85f, 1.24f, -1.97f});
        need(g.interactionTarget() == 1, "lamp targeting");
        g.interact();
        need(!g.lamp, "actual lamp toggle");
        move(g, {-1.55f, -2.40f}, true);
        lookAt(g, {-2.78f, 1.27f, -3.0f});
        need(g.interactionTarget() == 2, "CCTV targeting");
        g.interact();
        need(g.cctvView == 1, "CCTV camera changes");
        g.yaw = -90;
        g.pitch = 0;
        for (int i = 0; i < 5000 && g.state == State::Playing; i++)
            g.update(1.f / 240, walkTo(g, {0, -5.0f}, false));
        need(g.state == State::Alarm, "standing collision triggers alarm");
        Input retry;
        retry.retry = true;
        g.update(1.f / 240, retry);
        need(g.state == State::Playing && g.lamp && g.cctvView == 0, "full retry reset");
        Route route;
        float seconds = 0;
        while (seconds < 100 && (g.state == State::Playing || g.state == State::Finale)) {
            Input in = route.next(g);
            g.update(1.f / 240, in);
            seconds += 1.f / 240;
        }
        std::cout << "Route result: state=" << int(g.state) << " beam=" << route.beam
                  << " z=" << g.position.z << " t=" << seconds << " safe=" << g.safeOpened << "\\n";
        need(g.state == State::Victory, "continuous legal route reaches victory");
        need(g.lastCrossed && g.safeOpened && route.beam == 6,
             "all six lasers and final safe gate");
        std::cout << "PASS lamp, CCTV, alarm, retry, six lasers, crouch, safe hierarchy trigger, "
                     "victory in "
                  << seconds << " seconds\n";
        // Repeat from several initial laser phases; no phase is specially arranged for the bot.
        for (float start : {0.f, 2.f, 4.f, 7.f, 11.f, 17.f}) {
            Game trial;
            trial.time = start;
            trial.updateLasers();
            Route path;
            float duration = 0;
            while (duration < 100 && (trial.state == State::Playing || trial.state == State::Finale)) {
                trial.update(1.f / 240, path.next(trial));
                duration += 1.f / 240;
            }
            need(trial.state == State::Victory, "route fails for alternate initial phase");
        }
        std::cout << "PASS six alternate initial phases\n";
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "FAIL " << e.what() << '\n';
        return 1;
    }
}
