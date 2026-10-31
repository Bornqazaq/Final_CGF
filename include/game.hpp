#pragma once
#include <array>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <string>
#include <vector>
namespace lvh {
enum class State { Playing, Alarm, Victory, Pause, Finale };
struct Input {
    float forward = 0, right = 0;
    bool crouch = false, interact = false, retry = false;
};
struct Laser {
    glm::vec3 center{0};
    glm::vec3 halfSize{3.65f, .012f, .012f};
    glm::mat4 matrix{1};
    float angle = 0;
};
struct Game {
    static constexpr float safeOpenDuration = 3.4f;
    static constexpr float roomBack = -14.55f, safeFront = -13.9f;
    static constexpr glm::vec3::value_type dancerX = .55f;
    State state = State::Playing;
    glm::vec3 position{0, 0, -.85f};
    float yaw = -90, pitch = 0, eye = 1.57f, bodyHeight = 1.78f, time = 0, safeTime = 0,
          stepDistance = 0, moveSpeed = 0, interactionTime = 0;
    float danceDuration = 7.5f, localForward = 0, localRight = 0;
    bool crouching = false, lamp = true, safeOpened = false, lastCrossed = false;
    bool thirdPerson = false;
    float bodyYaw = -90;
    int cctvView = 0, retries = 0;
    std::array<Laser, 6> lasers;
    std::string hint;
    Game();
    void reset();
    void update(float, const Input &);
    void updateLasers();
    bool playerHit() const;
    bool blocked(glm::vec3) const;
    int interactionTarget() const;
    void interact();
    glm::vec3 forward() const;
    float characterFacing() const;
    std::string locomotionClip() const;
    void toggleCamera();
    glm::vec3 eyePosition() const;
    bool cameraBlocked(glm::vec3) const;
    bool thirdPersonVisible() const;
    glm::vec3 camera() const;
    glm::mat4 view() const;
};
bool pointInBox(glm::vec3 point, const glm::mat4 &model, glm::vec3 halfSize);
bool sampledBodyHits(const Laser &, glm::vec3 feet, float height);
} // namespace lvh
