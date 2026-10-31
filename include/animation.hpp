#pragma once
#include <filesystem>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>
#include <string>
#include <vector>
namespace lvh {
struct JointPose {
    glm::vec3 translation{0};
    glm::quat rotation{1, 0, 0, 0};
    glm::vec3 scale{1};
};
struct Bone {
    std::string name;
    int parent = -1;
    glm::mat4 inverseBind{1};
};
struct Clip {
    std::string name;
    float duration = 1;
    unsigned frames = 0;
    std::vector<JointPose> samples;
};
class Animator {
  public:
    std::vector<Bone> bones;
    std::vector<Clip> clips;
    std::vector<glm::mat4> palette;
    void load(const std::filesystem::path &);
    float duration(const std::string &) const;
    void update(const std::string &, float phase, float dt, bool rest = false,
                float interaction = -1);

  private:
    std::vector<JointPose> current, previous;
    std::string active;
    float blend = 1;
};
} // namespace lvh
