#pragma once
#include "game.hpp"
struct GLFWwindow;
namespace lvh {
enum class UIAction { None, Begin, Resume, Retry, Quit };
void initUI(GLFWwindow *);
void stopUI();
void beginUI();
UIAction drawUI(Game &, float fps, int width, int height, const std::string &gpu, bool help,
                bool menu = false, const std::string &caption = "",
                const std::string &diagnostics = "", bool preview = false, unsigned liveCamera = 0);
void finishUI();
} // namespace lvh
