#include "director.hpp"
#include <cmath>
namespace lvh {
Input Director::next(Game &g, float dt) {
    elapsed += dt;
    Input in;
    float t = elapsed;
    if (g.state == State::Alarm)
        sawAlarm = true;
    if (g.state == State::Victory)
        sawVictory = true;
    if (t < 16) {
        g.yaw = -90 + 16 * std::sin(t * .22f);
        g.pitch = 3 * std::sin(t * .3f);
        return in;
    }
    if (t < 29) {
        lookAt(g, {-2.85f, 1.24f, -1.97f});
        in = walkTo(g, {-1.5f, -1.25f}, false);
        if (t > 22 && !lampOff && g.interactionTarget() == 1) {
            in.interact = true;
            lampOff = true;
        }
        if (t > 26 && !lampOn && g.interactionTarget() == 1) {
            in.interact = true;
            lampOn = true;
        }
        return in;
    }
    if (t < 49) {
        lookAt(g, {-2.78f, 1.27f, -3.f});
        in = walkTo(g, {-1.55f, -2.4f}, true);
        if (t > 40 && !camera && g.interactionTarget() == 2) {
            in.interact = true;
            camera = true;
        }
        // The first camera sees the real rig during the approach and crouch.
        if (t > 35 && t < 38)
            in.crouch = false;
        return in;
    }
    if (t < 62) {
        in = walkTo(g, {0, -1.6f}, false);
        lookAt(g, {t < 56 ? -2.2f : 2.2f, 3.4f, -6.5f});
        return in;
    }
    if (t < 75) {
        g.yaw = -90;
        g.pitch = 0;
        return walkTo(g, {0, -5.f}, false);
    }
    if (t < 84)
        return in;
    if (!retried) {
        in.retry = true;
        retried = true;
        return in;
    }
    if (t < 100) {
        g.yaw = -90;
        g.pitch = 0;
        return in;
    }
    const float gates[] = {103, 120, 137, 154, 171, 192};
    // Pause before each crossing to make the hazard timing readable in the video.
    if (route.beam < 6 && t < gates[route.beam]) {
        in.crouch = true;
        g.yaw = -90 + 6 * std::sin(t * .3f);
        g.pitch = 0;
        return in;
    }
    return route.next(g, true);
}
std::string Director::caption() const {
    float t = elapsed;
    if (t < 8)
        return "LASER VAULT HEIST   |   Topic 12   |   OpenGL 3.3 Core";
    if (t < 16)
        return "An original Blender vault: wood, stone, brass and a cold night window.";
    if (t < 22)
        return "WASD + mouse. Approach the desk lamp and press E.";
    if (t < 29)
        return "Interaction 1 / 3: the local lamp changes both its light and visible glow.";
    if (t < 35)
        return "Hold CTRL to crouch. The eye height, collision body and rig change together.";
    if (t < 40)
        return "Live CCTV: a second camera renders the animated thief into a framebuffer.";
    if (t < 49)
        return "Interaction 2 / 3: E switches between two live security views.";
    if (t < 62)
        return "Two rotating guard spotlights share their direction with the visible mounts.";
    if (t < 75)
        return "A deliberate mistake: touching a thin moving laser triggers the alarm.";
    if (t < 84)
        return "All illumination turns red. R starts a real reset of the whole attempt.";
    if (t < 99)
        return "Actual source + runtime diagnostics. VAO / VBO / EBO and custom GLSL.";
    if (t < 120)
        return "Continuous final attempt: wait for clearance, then cross while crouched.";
    if (t < 137)
        return "Laser collision transforms sampled body points into the beam's local box.";
    if (t < 154)
        return "A rotating beam uses a left-wall pivot. Geometry and collision share its matrix.";
    if (t < 171)
        return "The controller advances at 240 Hz, including during slow render frames.";
    if (t < 192)
        return "Read the next gap. The CCTV keeps rendering while every laser continues moving.";
    if (t < 195)
        return "The last beam requires a crouch. This passage is continuous, without a cut.";
    if (t < 199)
        return "Interaction 3 / 3: turn the wheel, retract the bolts, swing the hinged door.";
    return "VAULT OPENED   |   Quiet steps. Clean execution.";
}
} // namespace lvh
