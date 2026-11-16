#pragma once
#include <filesystem>
#include <fstream>
#include <vector>
namespace lvh {
class Recorder {
    void *process = nullptr;
    void *pipe = nullptr;
    void *log = nullptr;
    std::vector<unsigned char> pixels;
    std::ofstream timing;
    double start = -1;
    int width = 0, height = 0, frames = 0, duplicates = 0;

  public:
    Recorder(const std::filesystem::path &encoder, const std::filesystem::path &output, int w,
             int h);
    ~Recorder();
    void frame(double now, int w, int h);
    void close();
};
} // namespace lvh
