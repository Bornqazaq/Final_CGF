#pragma once
#include "graphics.hpp"
#include <unordered_map>
namespace lvh {
struct Material {
    std::string name;
    glm::vec3 color{1};
    float specular = .2f, shine = 32, emission = 0;
    GLuint texture = 0;
};
struct Node {
    std::string name;
    int parent = -1, mesh = -1, material = 0;
    glm::mat4 local{1}, base{1}, world{1};
    bool dynamic = false, screen = false, character = false;
};
struct Batch {
    int mesh, material;
    std::vector<glm::mat4> matrices;
    GLuint buffer = 0;
};
struct Scene {
    std::vector<std::shared_ptr<Mesh>> meshes;
    std::vector<Material> materials;
    std::vector<Node> nodes;
    bool lampOn = true, showCharacter = false, characterPresent = true;
    std::vector<glm::mat4> skinPalette;
    glm::mat4 characterModel{1};
    std::unordered_map<std::string, int> index;
    std::vector<Batch> batches;
    void load(const fs::path &);
    void greybox();
    void updateWorld();
    void buildBatches();
    void setLocal(const std::string &, const glm::mat4 &);
    int find(const std::string &) const;
    ~Scene();
};
struct Light {
    glm::vec3 position, color, direction{0, -1, 0};
    float power = 1, cutoff = -1, outer = -1;
};
class Renderer {
  public:
    Shader surface, post, depthShader, coneShader;
    std::shared_ptr<Mesh> cone;
    Target sceneTarget, cctv, cctvDisplay;
    GLuint quad = 0, shadowFbo = 0, shadowMap = 0, white = 0;
    glm::mat4 lightVP{1};
    int width = 1280, height = 720;
    bool characterPreview = false;
    explicit Renderer(const fs::path &);
    ~Renderer();
    void frame(Scene &, const glm::mat4 &, glm::vec3, const std::vector<Light> &, bool, int, float);
    void draw(Scene &, const glm::mat4 &, const glm::mat4 &, glm::vec3, const std::vector<Light> &,
              bool, bool);
};
} // namespace lvh
