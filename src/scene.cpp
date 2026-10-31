#include "scene.hpp"
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <stdexcept>
namespace lvh {
Scene::~Scene() {
    for (auto &m : materials)
        if (m.texture)
            glDeleteTextures(1, &m.texture);
    for (auto &b : batches)
        if (b.buffer)
            glDeleteBuffers(1, &b.buffer);
}
int Scene::find(const std::string &name) const {
    auto it = index.find(name);
    return it == index.end() ? -1 : it->second;
}
void Scene::setLocal(const std::string &name, const glm::mat4 &m) {
    int i = find(name);
    if (i >= 0)
        nodes[i].local = m;
}
void Scene::updateWorld() {
    for (size_t i = 0; i < nodes.size(); i++) {
        auto &n = nodes[i];
        if (n.parent >= int(i))
            throw std::runtime_error("Scene parent order invalid");
        n.world = n.parent < 0 ? n.local : nodes[n.parent].world * n.local;
    }
}
void Scene::buildBatches() {
    for (auto &b : batches)
        if (b.buffer)
            glDeleteBuffers(1, &b.buffer);
    batches.clear();
    updateWorld();
    std::map<std::pair<int, int>, size_t> groups;
    for (const auto &n : nodes) {
        if (n.mesh < 0 || n.dynamic || n.screen || n.character)
            continue;
        auto key = std::make_pair(n.mesh, n.material);
        auto it = groups.find(key);
        if (it == groups.end()) {
            groups[key] = batches.size();
            batches.push_back({n.mesh, n.material, {n.world}, 0});
        } else
            batches[it->second].matrices.push_back(n.world);
    }
    for (auto &b : batches) {
        glGenBuffers(1, &b.buffer);
        glBindBuffer(GL_ARRAY_BUFFER, b.buffer);
        glBufferData(GL_ARRAY_BUFFER, GLsizeiptr(b.matrices.size() * sizeof(glm::mat4)),
                     b.matrices.data(), GL_STATIC_DRAW);
    }
}
void Scene::load(const fs::path &path) {
    const int meshOffset = int(meshes.size()), materialOffset = int(materials.size()),
              nodeOffset = int(nodes.size());
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Missing scene manifest: " + path.string());
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream in(line);
        std::string type;
        in >> type;
        if (type.empty() || type[0] == '#')
            continue;
        if (type == "material") {
            Material m;
            std::string tex;
            in >> std::quoted(m.name) >> m.color.x >> m.color.y >> m.color.z >> m.specular >>
                m.shine >> m.emission >> std::quoted(tex);
            if (tex != "-")
                m.texture = loadTexture(path.parent_path() / tex);
            materials.push_back(m);
        } else if (type == "mesh") {
            std::string name, filename;
            in >> std::quoted(name) >> std::quoted(filename);
            meshes.push_back(Mesh::load(path.parent_path() / filename));
        } else if (type == "node") {
            Node n;
            int flags;
            in >> std::quoted(n.name) >> n.parent >> n.mesh >> n.material >> flags;
            n.dynamic = flags & 1;
            n.screen = flags & 2;
            n.character = flags & 4;
            for (int c = 0; c < 4; c++)
                for (int r = 0; r < 4; r++)
                    in >> n.local[c][r];
            if (n.mesh >= 0)
                n.mesh += meshOffset;
            n.material += materialOffset;
            if (n.parent >= 0)
                n.parent += nodeOffset;
            n.base = n.local;
            index[n.name] = int(nodes.size());
            nodes.push_back(n);
        } else
            throw std::runtime_error("Unknown scene record: " + type);
        if (!in)
            throw std::runtime_error("Malformed scene record: " + line);
    }
    if (materials.empty() || meshes.empty())
        throw std::runtime_error("Scene contains no renderable materials/meshes");
    updateWorld();
}
void Scene::greybox() {
    meshes.push_back(Mesh::box());
    materials.push_back({"Wood", {.3f, .18f, .09f}, .15f, 32, 0, 0});
    materials.push_back({"Stone", {.32f, .31f, .28f}, .12f, 24, 0, 0});
    materials.push_back({"Metal", {.08f, .12f, .11f}, .65f, 64, 0, 0});
    materials.push_back({"Laser", {1, .006f, .002f}, 0, 16, 7, 0});
    auto add = [&](const std::string &name, glm::vec3 p, glm::vec3 scale, int mat,
                   bool dynamic = false) {
        Node n;
        n.name = name;
        n.mesh = 0;
        n.material = mat;
        n.dynamic = dynamic;
        n.local = glm::scale(glm::translate(glm::mat4(1), p), scale);
        n.base = n.local;
        index[name] = int(nodes.size());
        nodes.push_back(n);
    };
    add("Floor", {0, -.12f, -7.5f}, {8, .2f, 15}, 0);
    add("LeftWall", {-4, 2, -7.5f}, {.2f, 4, 15}, 1);
    add("RightWall", {4, 2, -7.5f}, {.2f, 4, 15}, 1);
    add("BackWall", {0, 2, -15}, {8, 4, .2f}, 1);
    add("Safe", {0, 1.55f, -14.2f}, {2.8f, 3.1f, .6f}, 2);
    add("Desk", {-2.8f, .8f, -2.5f}, {1.5f, .15f, 2}, 0);
    for (int i = 0; i < 6; i++)
        add("Laser" + std::to_string(i), {0, 1.2f, -3.f - i}, {7.3f, .05f, .05f}, 3, true);
    updateWorld();
}
} // namespace lvh
