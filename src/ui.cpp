#include "ui.hpp"
#include <GLFW/glfw3.h>
#include <algorithm>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
namespace lvh {
void initUI(GLFWwindow *w) {
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    auto &io = ImGui::GetIO();
    io.IniFilename = nullptr;
    if (!io.Fonts->AddFontFromFileTTF("assets/fonts/Karla-Regular.ttf", 22.f))
        io.Fonts->AddFontDefault();
    ImGui::StyleColorsDark();
    auto &s = ImGui::GetStyle();
    s.WindowRounding = 8;
    s.FrameRounding = 4;
    s.WindowPadding = {28, 24};
    s.ItemSpacing = {12, 13};
    s.Colors[ImGuiCol_WindowBg] = {.035f, .032f, .026f, .96f};
    s.Colors[ImGuiCol_Text] = {.94f, .9f, .81f, 1};
    s.Colors[ImGuiCol_Button] = {.34f, .24f, .11f, 1};
    s.Colors[ImGuiCol_ButtonHovered] = {.5f, .35f, .15f, 1};
    ImGui_ImplGlfw_InitForOpenGL(w, true);
    ImGui_ImplOpenGL3_Init("#version 330");
}
void stopUI() {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
}
void beginUI() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();
}
void finishUI() {
    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}
UIAction drawUI(Game &g, float fps, int width, int height, const std::string &gpu, bool help,
                bool menu, const std::string &caption, const std::string &diagnostics, bool preview,
                unsigned liveCamera) {
    (void)width;
    (void)height;
    // ImGui coordinates use logical window pixels, not framebuffer pixels (HiDPI).
    auto display = ImGui::GetIO().DisplaySize;
    float w = display.x, h = display.y;
    auto *dl = ImGui::GetForegroundDrawList();
    ImU32 ivory = IM_COL32(239, 227, 202, 245), gold = IM_COL32(207, 166, 92, 255);
    UIAction action = UIAction::None;
    if (!menu) {
        dl->AddRectFilled({24, 24}, {395, 106}, IM_COL32(10, 12, 12, 195), 5);
        dl->AddRectFilled({24, 24}, {27, 106}, gold);
        dl->AddText({43, 37}, gold, "LASER VAULT HEIST");
        dl->AddText({43, 70}, ivory,
                    preview ? "CHARACTER / RIG REVIEW" : g.safeOpened ? "THE VAULT IS YOURS" : "Reach the vault. Leave no alarm.");
    }
    char counter[64];
    if (fps > 0)
        snprintf(counter, 64, "%.0f FPS  |  OPENGL 3.3", fps);
    else
        snprintf(counter, 64, "MEASURING FPS");
    auto sz = ImGui::CalcTextSize(counter);
    dl->AddRectFilled({w - sz.x - 56, 24}, {w - 24, 66}, IM_COL32(10, 12, 12, 220), 5);
    dl->AddText({w - sz.x - 40, 34}, ivory, counter);
    if (!menu && !preview && g.state == State::Playing) {
        dl->AddCircleFilled({w * .5f, h * .5f}, 2, ivory);
        std::string posture=std::string(g.crouching ? "CROUCHED" : "STANDING")+
                            (g.thirdPerson ? " | THIRD PERSON" : " | FIRST PERSON");
        dl->AddText({30,h-42},gold,posture.c_str());
        const char *controls = "WASD  Move   CTRL/C  Crouch   E  Interact   V  View   F1  Help";
        auto cs = ImGui::CalcTextSize(controls);
        dl->AddText({w - cs.x - 30, h - 42}, ivory, controls);
        if (!g.hint.empty() && caption.empty()) {
            auto s = ImGui::CalcTextSize(g.hint.c_str());
            dl->AddRectFilled({(w - s.x) * .5f - 18, h - 112}, {(w + s.x) * .5f + 18, h - 70},
                              IM_COL32(8, 10, 11, 230), 5);
            dl->AddText({(w - s.x) * .5f, h - 103}, ivory, g.hint.c_str());
        }
    }
    if (!caption.empty()) {
        auto s = ImGui::CalcTextSize(caption.c_str());
        dl->AddRectFilled({(w - s.x) * .5f - 22, h - 112}, {(w + s.x) * .5f + 22, h - 66},
                          IM_COL32(8, 10, 11, 235), 5);
        dl->AddText({(w - s.x) * .5f, h - 101}, ivory, caption.c_str());
    }
    if (menu || g.state == State::Alarm || g.state == State::Victory || g.state == State::Pause) {
        if (g.state != State::Victory)
            ImGui::GetBackgroundDrawList()->AddRectFilled({0, 0}, {w, h}, IM_COL32(3, 5, 6, 95));
        ImGui::SetNextWindowPos({w * .5f, h * .5f}, ImGuiCond_Always, {.5f, .5f});
        ImGui::SetNextWindowSize({560, menu ? 460.f : g.state == State::Pause ? 370.f : 315.f});
        if (g.state == State::Victory) {
            ImGui::SetNextWindowPos({24, h - 345}, ImGuiCond_Always);
            ImGui::SetNextWindowSize({420, 315});
        }
        ImGui::Begin("Heist", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove);
        ImGui::TextColored(
            g.state == State::Alarm ? ImVec4(1, .25f, .18f, 1) : ImVec4(.88f, .72f, .4f, 1), "%s",
            menu                        ? "LASER VAULT HEIST"
            : g.state == State::Alarm   ? "ALARM TRIGGERED"
            : g.state == State::Victory ? "VAULT OPENED"
                                        : "PAUSED");
        ImGui::Separator();
        ImGui::TextWrapped(
            "%s", menu ? "An old vault. Six moving lasers. One clean way through. Read the timing, "
                         "stay low, and open the safe."
                  : g.state == State::Alarm
                      ? "A laser touched you. Watch its timing and use the low passages."
                  : g.state == State::Victory ? "Quiet steps. Clean execution. The vault is yours."
                                              : "The room will wait. Take a breath.");
        if (menu) {
            ImGui::Text("WASD + mouse    Move and look");
            ImGui::Text("CTRL / C    Crouch     E    Interact");
            ImGui::Text("V    Camera     F1    Help     ESC    Pause");
        }
        if (menu || g.state == State::Pause) {
            ImGui::SetNextItemWidth(300);
            ImGui::SliderFloat("Mouse sensitivity", &g.mouseSensitivity, .002f, .12f,
                               "%.3f", ImGuiSliderFlags_Logarithmic | ImGuiSliderFlags_AlwaysClamp);
        }
        if (ImGui::Button(menu                      ? "Begin heist  [ENTER]"
                          : g.state == State::Pause ? "Resume  [ESC]"
                                                    : "Retry  [R]",
                          {300, 45}))
            action = menu                      ? UIAction::Begin
                     : g.state == State::Pause ? UIAction::Resume
                                               : UIAction::Retry;
        if (ImGui::Button("Exit", {100, 36}))
            action = UIAction::Quit;
        ImGui::End();
    }
    if (help && !menu) {
        ImGui::SetNextWindowPos({24, 125}, ImGuiCond_Always);
        ImGui::SetNextWindowSize({460, 420});
        ImGui::Begin("FIELD NOTES", nullptr, ImGuiWindowFlags_NoResize);
        ImGui::Text("WASD       Walk");
        ImGui::Text("Mouse      Look");
        ImGui::Text("V          First / third person");
        ImGui::Text("CTRL / C   Hold to crouch");
        ImGui::Text("E          Interact");
        ImGui::Text("R          Retry after alarm / victory");
        ImGui::Text("ESC        Pause");
        ImGui::Text("F1         Toggle guide");
        ImGui::Text("F12        Screenshot");
        ImGui::TextWrapped("Desk lamp, CCTV selector and safe wheel are interactive. Touching any "
                           "laser turns every light red.");
        ImGui::TextWrapped("%s", gpu.c_str());
        ImGui::End();
    }
    if (liveCamera) {
        ImGui::SetNextWindowPos({w - 690, 112}, ImGuiCond_Always);
        ImGui::SetNextWindowSize({660, 416});
        ImGui::Begin("LIVE CCTV / ENLARGED MONITOR VIEW", nullptr,
                     ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize |
                         ImGuiWindowFlags_NoCollapse);
        ImGui::Image(ImTextureID(liveCamera), {604, 340}, {0, 1}, {1, 0});
        ImGui::End();
    }
    if (!diagnostics.empty()) {
        ImGui::SetNextWindowPos({w * .5f, h * .46f}, ImGuiCond_Always, {.5f, .5f});
        ImGui::SetNextWindowSize({940, 520});
        ImGui::Begin("RENDERER / ACTUAL SOURCE", nullptr,
                     ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);
        ImGui::TextWrapped("%s", diagnostics.c_str());
        ImGui::End();
    }
    return action;
}
} // namespace lvh
