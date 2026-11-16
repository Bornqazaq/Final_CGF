#pragma once
#include "game.hpp"
#include <algorithm>
namespace lvh {
// Input edges are retained even when a render frame contains no simulation step.
class FixedStep {
    double accumulated = 0;
    bool interact = false, retry = false;

  public:
    static constexpr double seconds = 1.0 / 240.0;
    template <class Step> void advance(double elapsed, Input input, Step step) {
        interact |= input.interact;
        retry |= input.retry;
        accumulated += std::clamp(elapsed, 0.0, 1.0);
        while (accumulated >= seconds) {
            input.interact = interact;
            input.retry = retry;
            step(float(seconds), input);
            interact = retry = false;
            accumulated -= seconds;
        }
    }
};
} // namespace lvh
