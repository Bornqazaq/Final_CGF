#include "scene.hpp"
#include <cmath>
#include <stdexcept>
namespace lvh {
static void drawBatch(Scene &s, const Batch &b) {
    const auto &m = s.meshes[b.mesh];
    glBindVertexArray(m->vao);
    glBindBuffer(GL_ARRAY_BUFFER, b.buffer);
    for (int k = 0; k < 4; k++) {
        glEnableVertexAttribArray(5 + k);
        glVertexAttribPointer(5 + k, 4, GL_FLOAT, GL_FALSE, sizeof(glm::mat4),
                              reinterpret_cast<void *>(size_t(k) * sizeof(glm::vec4)));
        glVertexAttribDivisor(5 + k, 1);
    }
    glDrawElementsInstanced(GL_TRIANGLES, m->count, GL_UNSIGNED_INT, nullptr,
                            int(b.matrices.size()));
}
Renderer::Renderer(const fs::path &root)
    : surface(root / "surface.vert", root / "surface.frag"),
      post(root / "post.vert", root / "post.frag"),
      depthShader(root / "depth.vert", root / "depth.frag"),
      coneShader(root / "cone.vert", root / "cone.frag") {
    std::vector<Vertex> cv;
    std::vector<unsigned> ci;
    cv.push_back({glm::vec3(0), {0, 1, 0}, {0, 0}});
    for (int i = 0; i < 40; i++) {
        float a = float(i) * 6.2831853f / 40;
        cv.push_back({{2.25f * std::cos(a), -3.4f, 2.25f * std::sin(a)}, {0, 1, 0}, {0, 0}});
        ci.insert(ci.end(), {0u, unsigned(i + 1), unsigned((i + 1) % 40 + 1)});
    }
    cone = std::make_shared<Mesh>(cv, ci);
    glGenVertexArrays(1, &quad);
    unsigned char pixel[] = {255, 255, 255, 255};
    glGenTextures(1, &white);
    glBindTexture(GL_TEXTURE_2D, white);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glGenFramebuffers(1, &shadowFbo);
    glGenTextures(1, &shadowMap);
    glBindTexture(GL_TEXTURE_2D, shadowMap);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, 2048, 2048, 0, GL_DEPTH_COMPONENT,
                 GL_FLOAT, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    float border[] = {1, 1, 1, 1};
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border);
    glBindFramebuffer(GL_FRAMEBUFFER, shadowFbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, shadowMap, 0);
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
        throw std::runtime_error("Shadow framebuffer incomplete");
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    cctv.resize(640, 360);
    cctvDisplay.resize(640, 360);
    lightVP = glm::ortho(-11.f, 11.f, -11.f, 11.f, .1f, 40.f) *
              glm::lookAt(glm::vec3(-6, 4, -2), glm::vec3(1, 0, -8.f), glm::vec3(0, 1, 0));
}
Renderer::~Renderer() {
    glDeleteVertexArrays(1, &quad);
    glDeleteTextures(1, &white);
    glDeleteTextures(1, &shadowMap);
    glDeleteFramebuffers(1, &shadowFbo);
}
void Renderer::draw(Scene &s, const glm::mat4 &view, const glm::mat4 &proj, glm::vec3 eyePos,
                    const std::vector<Light> &lights, bool alarm, bool security) {
    glEnable(GL_DEPTH_TEST);
    glDepthMask(GL_TRUE);
    glDepthFunc(GL_LESS);
    surface.use();
    surface.set("uView", view);
    surface.set("uProjection", proj);
    surface.set("uLightVP", lightVP);
    surface.set("uEye", eyePos);
    surface.set("uAlarm", int(alarm));
    surface.set("uTexture", 0);
    surface.set("uShadow", 1);
    surface.set("uLightCount", int(lights.size()));
    surface.set("uSkinned", 0);
    surface.set("uInstanced", 0);
    glActiveTexture(GL_TEXTURE1);
    glBindTexture(GL_TEXTURE_2D, shadowMap);
    glActiveTexture(GL_TEXTURE0);
    for (size_t i = 0; i < lights.size(); i++) {
        std::string prefix = "uLights[" + std::to_string(i) + "].";
        const auto &l = lights[i];
        surface.set((prefix + "position").c_str(), l.position);
        surface.set((prefix + "color").c_str(), l.color);
        surface.set((prefix + "direction").c_str(), l.direction);
        surface.set((prefix + "power").c_str(), l.power);
        surface.set((prefix + "cutoff").c_str(), l.cutoff);
        surface.set((prefix + "outer").c_str(), l.outer);
    }
    surface.set("uInstanced", 1);
    for (const auto &b : s.batches) {
        const auto &m = s.materials[b.material];
        surface.set("uColor", alarm && m.emission > 0 ? glm::vec3(1, .008f, .002f) : m.color);
        surface.set("uSpecular", m.specular);
        surface.set("uShine", m.shine);
        surface.set("uEmission", m.emission);
        surface.set("uScreen", 0);
        glBindTexture(GL_TEXTURE_2D, m.texture ? m.texture : white);
        drawBatch(s, b);
    }
    surface.set("uInstanced", 0);
    if (!s.skinPalette.empty())
        glUniformMatrix4fv(glGetUniformLocation(surface.id, "uBones[0]"), int(s.skinPalette.size()),
                           GL_FALSE, glm::value_ptr(s.skinPalette[0]));
    for (auto &n : s.nodes) {
        if (n.mesh < 0 || (!n.dynamic && !n.screen && !n.character && !s.batches.empty()) ||
            (n.character && (!s.characterPresent || (!security && !s.showCharacter))) || (n.screen && security))
            continue;
        surface.set("uSkinned", int(n.character));
        const auto &m = s.materials.at(n.material);
        surface.set("uModel", n.character ? s.characterModel : n.world);
        surface.set("uColor", alarm && m.emission > 0 ? glm::vec3(1, .008f, .002f) : m.color);
        surface.set("uSpecular", m.specular);
        surface.set("uShine", m.shine);
        surface.set("uEmission", n.name == "DeskLampGlow" && !s.lampOn ? 0.f : m.emission);
        surface.set("uScreen", int(n.screen));
        glBindTexture(GL_TEXTURE_2D, n.screen ? cctv.color : (m.texture ? m.texture : white));
        s.meshes.at(n.mesh)->draw();
    }
    // Lightweight dust-cone visualization; real surface lighting uses the same vector.
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE);
    glDepthMask(GL_FALSE);
    glDisable(GL_CULL_FACE);
    coneShader.use();
    coneShader.set("uView", view);
    coneShader.set("uProjection", proj);
    for (const auto &l : lights) {
        if (l.cutoff <= 0)
            continue;
        glm::vec3 y = -l.direction, x = glm::normalize(glm::cross(y, glm::vec3(0, 0, 1))),
                  z = glm::cross(x, y);
        glm::mat4 model(1);
        model[0] = glm::vec4(x, 0);
        model[1] = glm::vec4(y, 0);
        model[2] = glm::vec4(z, 0);
        model[3] = glm::vec4(l.position, 1);
        coneShader.set("uModel", model);
        coneShader.set("uColor", l.color);
        cone->draw();
    }
    glDepthMask(GL_TRUE);
    glDisable(GL_BLEND);
    glEnable(GL_CULL_FACE);
}
void Renderer::frame(Scene &s, const glm::mat4 &view, glm::vec3 eyePos,
                     const std::vector<Light> &lights, bool alarm, int cameraIndex, float time) {
    (void)time;
    s.updateWorld();
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);
    glBindFramebuffer(GL_FRAMEBUFFER, shadowFbo);
    glViewport(0, 0, 2048, 2048);
    glClear(GL_DEPTH_BUFFER_BIT);
    depthShader.use();
    depthShader.set("uLightVP", lightVP);
    depthShader.set("uInstanced", 0);
    glEnable(GL_POLYGON_OFFSET_FILL);
    glPolygonOffset(2, 4);
    depthShader.set("uSkinned", 0);
    depthShader.set("uInstanced", 1);
    for (const auto &b : s.batches)
        drawBatch(s, b);
    depthShader.set("uInstanced", 0);
    if (!s.skinPalette.empty())
        glUniformMatrix4fv(glGetUniformLocation(depthShader.id, "uBones[0]"),
                           int(s.skinPalette.size()), GL_FALSE, glm::value_ptr(s.skinPalette[0]));
    for (auto &n : s.nodes) {
        if (n.mesh < 0 || (!n.dynamic && !n.character && !s.batches.empty()) || n.screen ||
            (n.character && !s.characterPresent))
            continue;
        depthShader.set("uSkinned", int(n.character));
        depthShader.set("uModel", n.character ? s.characterModel : n.world);
        s.meshes[n.mesh]->draw();
    }
    glDisable(GL_POLYGON_OFFSET_FILL);
    glm::vec3 securityEye =
        cameraIndex == 0 ? glm::vec3(-3.5, 3.35, -.5) : glm::vec3(3.5, 3.25, -14.4);
    glm::mat4 securityView = glm::lookAt(securityEye, glm::vec3(0, .8, -7.5), glm::vec3(0, 1, 0));
    glBindFramebuffer(GL_FRAMEBUFFER, cctv.fbo);
    glViewport(0, 0, cctv.width, cctv.height);
    glClearColor(.025f, .035f, .05f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    draw(s, securityView, glm::perspective(glm::radians(72.f), 16.f / 9.f, .08f, 35.f), securityEye,
         lights, alarm, true);
    glBindFramebuffer(GL_FRAMEBUFFER, cctvDisplay.fbo);
    glDisable(GL_DEPTH_TEST);
    glDisable(GL_CULL_FACE);
    post.use();
    post.set("uScene", 0);
    post.set("uTint", glm::vec3(1));
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, cctv.color);
    post.set("uSceneDepth", 1);
    post.set("uNear", .08f);post.set("uFar", 35.f);
    glActiveTexture(GL_TEXTURE1);
    glBindTexture(GL_TEXTURE_2D, cctv.depth);
    glActiveTexture(GL_TEXTURE0);
    glBindVertexArray(quad);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    sceneTarget.resize(width, height, true);
    glBindFramebuffer(GL_FRAMEBUFFER, sceneTarget.fbo);
    glViewport(0, 0, width, height);
    glClearColor(.018f, .025f, .045f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    draw(s, view, glm::perspective(glm::radians(68.f), float(width) / height, .06f, 50.f), eyePos,
         lights, alarm, characterPreview);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0, 0, width, height);
    glDisable(GL_DEPTH_TEST);
    glDisable(GL_CULL_FACE);
    post.use();
    post.set("uScene", 0);
    post.set("uTint", glm::vec3(1));
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, sceneTarget.color);
    post.set("uSceneDepth", 1);
    post.set("uNear", .06f);post.set("uFar", 50.f);
    glActiveTexture(GL_TEXTURE1);
    glBindTexture(GL_TEXTURE_2D, sceneTarget.depth);
    glActiveTexture(GL_TEXTURE0);
    glBindVertexArray(quad);
    glDrawArrays(GL_TRIANGLES, 0, 3);
}
} // namespace lvh
