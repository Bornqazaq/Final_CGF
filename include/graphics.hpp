#pragma once
#include <filesystem>
#include <glad/gl.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <memory>
#include <string>
#include <vector>
namespace lvh {
namespace fs = std::filesystem;
struct Vertex {
    glm::vec3 position, normal;
    glm::vec2 uv;
    glm::vec4 weights{0}, joints{0};
};
class Shader {
  public:
    GLuint id = 0;
    Shader(const fs::path &vertex, const fs::path &fragment);
    ~Shader();
    Shader(const Shader &) = delete;
    void use() const;
    void set(const char *, int) const;
    void set(const char *, float) const;
    void set(const char *, glm::vec3) const;
    void set(const char *, const glm::mat4 &) const;
};
class Mesh {
  public:
    GLuint vao = 0, vbo = 0, ebo = 0, instances = 0;
    GLsizei count = 0, instanceCount = 0;
    Mesh(const std::vector<Vertex> &, const std::vector<unsigned> &);
    ~Mesh();
    Mesh(const Mesh &) = delete;
    void draw() const;
    void setInstances(const std::vector<glm::mat4> &);
    void drawInstances() const;
    static std::shared_ptr<Mesh> box();
    static std::shared_ptr<Mesh> load(const fs::path &);
};
GLuint loadTexture(const fs::path &, bool srgb = true);
struct Target {
    GLuint fbo = 0, color = 0, depth = 0;
    int width = 0, height = 0;
    void resize(int, int, bool hdr = false);
    void release();
    ~Target();
};
void saveFramebuffer(const fs::path &, int, int);
std::string readText(const fs::path &);
} // namespace lvh
