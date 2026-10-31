#include "game.hpp"
#include <algorithm>
#include <cmath>
namespace lvh {
bool pointInBox(glm::vec3 point, const glm::mat4 &model, glm::vec3 halfSize) {
    glm::vec3 p = glm::vec3(glm::inverse(model) * glm::vec4(point, 1));
    return glm::all(glm::lessThanEqual(glm::abs(p), halfSize + glm::vec3(1e-6f)));
}
bool sampledBodyHits(const Laser &l, glm::vec3 feet, float height) {
    // Local-space point/box tests sample the player's upright body. The small
    // local margin is conservative for our beam roll limits (at most 14 degrees).
    for (float h = .12f; h <= height + .001f; h += .08f)
        if (pointInBox(feet + glm::vec3(0, h, 0), l.matrix,
                       l.halfSize + glm::vec3(.16f, .055f, .16f)))
            return true;
    return pointInBox(feet + glm::vec3(0, height, 0), l.matrix,
                      l.halfSize + glm::vec3(.16f, .055f, .16f));
}
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
glm::vec3 Game::forward() const {
    float y = glm::radians(yaw);
    float p = glm::radians(thirdPerson ? std::clamp(pitch,-60.f,60.f) : pitch);
    return glm::normalize(glm::vec3(cos(y) * cos(p), sin(p), sin(y) * cos(p)));
}
void Game::toggleCamera() {
    if (state != State::Playing || safeOpened) return;
    // Enter orbit mode with the body's current first-person heading.
    if (!thirdPerson) bodyYaw = yaw;
    thirdPerson = !thirdPerson;
    if (thirdPerson) pitch = std::clamp(pitch,-60.f,60.f);
    else bodyYaw = yaw;
}

float Game::characterFacing() const {
    return glm::radians(90.f - (thirdPerson ? bodyYaw : yaw));
}

std::string Game::locomotionClip() const {
    bool moving = moveSpeed > .02f && state == State::Playing;
    if (crouching) {
        if (!moving) return "CrouchIdle";
        if (std::abs(localRight) > std::abs(localForward))
            return localRight > 0 ? "CrouchRight" : "CrouchLeft";
        return localForward < 0 ? "CrouchBackward" : "CrouchWalk";
    }
    if (interactionTime > 0) return "Interact";
    if (!moving) return "Idle";
    return thirdPerson || localForward >= -.5f ? "Walk" : "WalkBackward";
}
glm::vec3 Game::eyePosition() const {
    return position + glm::vec3(0,eye,0);
}
bool Game::cameraBlocked(glm::vec3 p) const {
    // 0.18 m safety radius around the boom. The entrance remains an open doorway.
    if (p.x < -3.77f || p.x > 3.77f || p.z < -14.77f || p.z > 2.40f ||
        p.y < .18f || p.y > 3.55f) return true;
    if (p.z > -.25f && p.z < 2.65f && (std::abs(p.x)>1.72f || p.y>3.27f)) return true;
    auto box = [&](glm::vec3 lo,glm::vec3 hi) {
        lo-=glm::vec3(.18f);hi+=glm::vec3(.18f);
        return glm::all(glm::greaterThanEqual(p,lo)) && glm::all(glm::lessThanEqual(p,hi));
    };
    for(float depth : {.2f,4.6f,8.6f,11.7f,14.7f})
        for(float side : {-1.f,1.f})
            if(box({side*3.88f-.16f,0,-depth-.17f},{side*3.88f+.16f,4,-depth+.17f}))
                return true;
    return box({-3.73f,0,-3.8f},{-2.05f,.94f,-1.5f}) ||
           box({-3.0f,0,-1.35f},{-2.32f,1.36f,-.65f}) ||
           box({-3.89f,0,-12.85f},{-3.21f,2.72f,-10.15f}) ||
           box({-1.8f,0,-14.9f},{1.8f,3.34f,-13.7f}) ||
           box({2.43f,0,-9.65f},{3.57f,.9f,-8.15f}) ||
           box({2.77f,0,-1.65f},{3.43f,1.5f,-.95f}) ||
           box({2.79f,0,-13.73f},{3.45f,1.4f,-13.07f}) ||
           box({-2.91f,0,-13.36f},{-2.39f,1.2f,-12.84f});
}
glm::vec3 Game::camera() const {
    if (safeOpened) {
        float t = glm::clamp((safeTime - safeOpenDuration) / danceDuration, 0.f, 1.f);
        return {2.65f - .30f * t, 1.9f, -10.15f};
    }
    glm::vec3 anchor=eyePosition();
    if (!thirdPerson) return anchor;
    glm::vec3 f=forward();
    glm::vec3 right=glm::normalize(glm::cross(f,glm::vec3(0,1,0)));
    glm::vec3 boom=-f*2.8f+right*.38f+glm::vec3(0,.22f,0);
    int steps=int(std::ceil(glm::length(boom)/.025f));
    float clear=0;
    for(int i=1;i<=steps;++i){
        float t=float(i)/steps;
        if(cameraBlocked(anchor+boom*t)) {
            float lo=clear,hi=t;
            for(int j=0;j<10;++j) {
                float mid=(lo+hi)*.5f;
                if(cameraBlocked(anchor+boom*mid)) hi=mid; else lo=mid;
            }
            clear=lo;
            break;
        }
        clear=t;
    }
    return anchor+boom*clear;
}
bool Game::thirdPersonVisible() const {
    // A contracted boom hides the head/body before the camera enters the hood.
    return thirdPerson && !safeOpened && glm::distance(camera(),eyePosition())>.65f;
}
glm::mat4 Game::view() const {
    if (safeOpened)
        return glm::lookAt(camera(), glm::vec3(0, 1.42f, -13.1f), glm::vec3(0, 1, 0));
    glm::vec3 target=camera()+forward();
    return glm::lookAt(camera(),target,glm::vec3(0,1,0));
}
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
bool Game::blocked(glm::vec3 p) const {
    if (p.x < -3.65f || p.x > 3.65f || p.z > 2.35f || p.z < roomBack)
        return true;
    if (p.z > -.25f && std::abs(p.x)>1.70f) return true;
    auto box = [&](float x0, float x1, float z0, float z1) {
        return p.x > x0 - .22f && p.x < x1 + .22f && p.z > z0 - .22f && p.z < z1 + .22f;
    };
    return box(-3.7f, -2.05f, -3.8f, -1.5f) || box(-3.89f, -3.21f, -12.85f, -10.15f) ||
           box(-1.8f, 1.8f, -14.9f, -13.7f) || box(2.43f, 3.57f, -9.65f, -8.15f) ||
           box(2.77f, 3.43f, -1.65f, -.95f) || box(2.79f, 3.45f, -13.73f, -13.07f) ||
           box(-2.91f, -2.39f, -13.36f, -12.84f);
}
bool Game::playerHit() const {
    for (auto &l : lasers)
        if (sampledBodyHits(l, position, bodyHeight))
            return true;
    return false;
}
int Game::interactionTarget() const {
    const glm::vec3 points[] = {
        {-2.85f, 1.24f, -1.97f}, {-2.78f, 1.27f, -3.0f}, {0, 1.65f, safeFront}};
    int target = 0;
    float best = -100;
    for (int i = 0; i < 3; i++) {
        glm::vec3 delta = points[i] - eyePosition();
        float distance = glm::length(delta);
        if (distance > 2.15f)
            continue;
        float alignment = glm::dot(forward(), delta / std::max(.001f, distance));
        if (alignment < .40f)
            continue;
        float score = alignment * 3 - distance;
        if (score > best) {
            best = score;
            target = i + 1;
        }
    }
    return target;
}
void Game::interact() {
    if (state != State::Playing)
        return;
    int target = interactionTarget();
    if (target == 1) {
        lamp = !lamp;
        interactionTime = .6f;
    }
    if (target == 2) {
        cctvView = 1 - cctvView;
        interactionTime = .6f;
    }
    if (target == 3 && lastCrossed) {
        safeOpened = true;
        safeTime = 0;
        moveSpeed = 0;
        localForward = localRight = 0;
        hint.clear();
        state = State::Finale;
        interactionTime = .7f;
    }
}
void Game::update(float dt, const Input &i) {
    if (i.retry && (state == State::Alarm || state == State::Victory)) {
        reset();
        return;
    }
    if (state == State::Finale) {
        time += dt;
        updateLasers();
        safeTime = std::min(safeOpenDuration + danceDuration, safeTime + dt);
        if (safeTime >= safeOpenDuration + danceDuration)
            state = State::Victory;
        return;
    }
    if (state != State::Playing)
        return;
    time += dt;
    updateLasers();
    interactionTime = std::max(0.f, interactionTime - dt);
    crouching = i.crouch;
    bodyHeight += ((crouching ? 1.33f : 1.78f) - bodyHeight) * std::min(1.f, dt * 20.f);
    float target = crouching ? 1.22f : 1.57f;
    eye += (target - eye) * std::min(1.f, dt * 13.f);
    glm::vec3 f = forward();
    f.y = 0;
    f = glm::normalize(f);
    glm::vec3 right = glm::normalize(glm::cross(f, glm::vec3(0, 1, 0)));
    glm::vec3 motion = f * i.forward + right * i.right;
    if (glm::length(motion) > 1)
        motion = glm::normalize(motion);
    motion *= dt * (crouching ? 1.25f : 2.45f);
    glm::vec3 old = position, p = position;
    p.x += motion.x;
    if (!blocked(p))
        position.x = p.x;
    p = position;
    p.z += motion.z;
    if (!blocked(p))
        position.z = p.z;
    moveSpeed = glm::length(position - old) / std::max(dt, .00001f);
    float distance = glm::length(position - old);
    stepDistance += distance;
    if (!thirdPerson) bodyYaw = yaw;
    else if (!crouching && distance > .000001f) {
        // Use actual displacement, including wall sliding, rather than mouse yaw.
        glm::vec3 direction = (position-old)/distance;
        bodyYaw = glm::degrees(std::atan2(direction.z,direction.x));
    }
    float heading = glm::radians(thirdPerson ? bodyYaw : yaw);
    glm::vec3 bodyForward(std::cos(heading),0,std::sin(heading));
    glm::vec3 bodyRight = glm::cross(bodyForward,glm::vec3(0,1,0));
    localForward = distance > .000001f ? glm::dot((position-old)/distance, bodyForward) : 0;
    localRight = distance > .000001f ? glm::dot((position-old)/distance, bodyRight) : 0;
    if (playerHit()) {
        state = State::Alarm;
        return;
    }
    if (position.z < -9.74f)
        lastCrossed = true;
    if (i.interact)
        interact();
    if (state == State::Finale)
        return;
    hint = "";
    switch (interactionTarget()) {
    case 1:
        hint = lamp ? "E   Switch desk lamp off" : "E   Switch desk lamp on";
        break;
    case 2:
        hint = "E   Switch security camera";
        break;
    case 3:
        hint = lastCrossed ? "E   Open the vault" : "Cross the final laser to unlock the vault";
        break;
    }
}
} // namespace lvh
