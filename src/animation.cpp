#include "animation.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <glm/gtc/matrix_transform.hpp>
#include <stdexcept>
namespace lvh {
template <class T> static T read(std::istream &f) {
    T x{};
    f.read(reinterpret_cast<char *>(&x), sizeof(T));
    if (!f)
        throw std::runtime_error("Truncated animation");
    return x;
}
static std::string readName(std::istream &f) {
    auto n = read<unsigned>(f);
    if (n > 256)
        throw std::runtime_error("Animation name too long");
    std::string name(n, ' ');
    f.read(name.data(), n);
    return name;
}
void Animator::load(const std::filesystem::path &p) {
    std::ifstream f(p, std::ios::binary);
    if (!f)
        throw std::runtime_error("Missing animation: " + p.string());
    char magic[4];
    f.read(magic, 4);
    unsigned version = read<unsigned>(f), n = read<unsigned>(f), nc = read<unsigned>(f);
    if (std::memcmp(magic, "LVHA", 4) || version != 1 || n > 64 || nc > 32)
        throw std::runtime_error("Unsupported animation header");
    for (unsigned i = 0; i < n; i++) {
        Bone b;
        b.name = readName(f);
        b.parent = read<int>(f);
        if (b.parent >= int(i))
            throw std::runtime_error("Invalid bone parent");
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                b.inverseBind[c][r] = read<float>(f);
        bones.push_back(b);
    }
    for (unsigned ci = 0; ci < nc; ci++) {
        Clip clip;
        clip.name = readName(f);
        clip.duration = read<float>(f);
        clip.frames = read<unsigned>(f);
        if (clip.frames < 2 || clip.frames > 10000 || clip.duration <= 0)
            throw std::runtime_error("Invalid animation clip");
        clip.samples.resize(size_t(clip.frames) * n);
        for (auto &s : clip.samples) {
            s.translation = {read<float>(f), read<float>(f), read<float>(f)};
            float x = read<float>(f), y = read<float>(f), z = read<float>(f), w = read<float>(f);
            s.rotation = glm::normalize(glm::quat(w, x, y, z));
            s.scale = {read<float>(f), read<float>(f), read<float>(f)};
        }
        clips.push_back(std::move(clip));
    }
    palette.resize(n, glm::mat4(1));
    current.resize(n);
    previous.resize(n);
}
float Animator::duration(const std::string &name) const {
    auto it=std::find_if(clips.begin(),clips.end(),[&](const Clip &c){return c.name==name;});
    if(it==clips.end()) throw std::runtime_error("Missing clip: "+name);
    return it->duration;
}
static JointPose mixPose(const JointPose &a, const JointPose &b, float t) {
    return {glm::mix(a.translation, b.translation, t),
            glm::normalize(glm::slerp(a.rotation, b.rotation, t)), glm::mix(a.scale, b.scale, t)};
}
void Animator::update(const std::string &name, float phase, float dt, bool rest,
                      float interaction) {
    if (rest) {
        std::fill(palette.begin(), palette.end(), glm::mat4(1));
        return;
    }
    auto it =
        std::find_if(clips.begin(), clips.end(), [&](const Clip &c) { return c.name == name; });
    if (it == clips.end())
        throw std::runtime_error("Missing clip: " + name);
    if (name != active) {
        previous = current;
        blend = active.empty() ? 1.f : 0.f;
        active = name;
    }
    blend = std::min(1.f, blend + dt / .20f);
    float t = ((name == "Interact" || name == "Dance" || name == "DanceLong") ? std::clamp(phase, 0.f, 1.f) : phase - std::floor(phase)) *
              (it->frames - 1);
    unsigned f0 = unsigned(t), f1 = std::min(f0 + 1, it->frames - 1);
    float alpha = t - f0;
    std::vector<glm::mat4> world(bones.size());
    for (size_t i = 0; i < bones.size(); i++) {
        JointPose target =
            mixPose(it->samples[f0 * bones.size() + i], it->samples[f1 * bones.size() + i], alpha);
        if (interaction >= 0 && (bones[i].name == "UpperArm.R" || bones[i].name == "Forearm.R" ||
                                 bones[i].name == "Hand.R" || bones[i].name == "mixamorig:RightArm" ||
                                 bones[i].name == "mixamorig:RightForeArm" || bones[i].name == "mixamorig:RightHand")) {
            const auto &reach = *std::find_if(clips.begin(), clips.end(),
                                              [](const Clip &c) { return c.name == "Interact"; });
            float f = std::clamp(interaction, 0.f, 1.f) * (reach.frames - 1);
            unsigned a = unsigned(f), b = std::min(a + 1, reach.frames - 1);
            target = mixPose(reach.samples[a * bones.size() + i],
                             reach.samples[b * bones.size() + i], f - a);
        }
        current[i] =
            blend < 1 ? mixPose(previous[i], target, glm::smoothstep(0.f, 1.f, blend)) : target;
        auto &p = current[i];
        glm::mat4 local = glm::translate(glm::mat4(1), p.translation) * glm::mat4_cast(p.rotation) *
                          glm::scale(glm::mat4(1), p.scale);
        world[i] = bones[i].parent < 0 ? local : world[bones[i].parent] * local;
        palette[i] = world[i] * bones[i].inverseBind;
    }
}
} // namespace lvh
