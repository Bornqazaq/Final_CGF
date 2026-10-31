#include "recorder.hpp"
#include <glad/gl.h>
#include <stdexcept>
#include <string>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif
namespace lvh {
Recorder::Recorder(const std::filesystem::path &encoder, const std::filesystem::path &output, int w,
                   int h)
    : width(w), height(h) {
#ifdef _WIN32
    if (!std::filesystem::exists(encoder))
        throw std::runtime_error("FFmpeg executable does not exist");
    std::filesystem::create_directories(output.parent_path());
    pixels.resize(size_t(w) * h * 3);
    timing.open(output.string() + ".frames.csv");
    timing << "video_frame,wall_seconds,duplicate\n";
    SECURITY_ATTRIBUTES sa{sizeof(sa), nullptr, TRUE};
    HANDLE read = nullptr, write = nullptr;
    if (!CreatePipe(&read, &write, &sa, 0))
        throw std::runtime_error("Cannot create encoder pipe");
    SetHandleInformation(write, HANDLE_FLAG_INHERIT, 0);
    HANDLE errors =
        CreateFileW((output.wstring() + L".encoder.log").c_str(), GENERIC_WRITE, FILE_SHARE_READ,
                    &sa, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    std::wstring args =
        L"\"" + encoder.wstring() +
        L"\" -y -hide_banner -loglevel warning -f rawvideo -pixel_format rgb24 -video_size " +
        std::to_wstring(w) + L"x" + std::to_wstring(h) +
        L" -framerate 30 -i pipe:0 -vf vflip -an -c:v libx264 -preset veryfast -crf 19 -pix_fmt "
        L"yuv420p -movflags +faststart \"" +
        output.wstring() + L"\"";
    STARTUPINFOW si{};
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = read;
    si.hStdOutput = errors;
    si.hStdError = errors;
    PROCESS_INFORMATION pi{};
    BOOL ok = CreateProcessW(encoder.wstring().c_str(), args.data(), nullptr, nullptr, TRUE,
                             CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi);
    CloseHandle(read);
    if (!ok) {
        CloseHandle(write);
        CloseHandle(errors);
        throw std::runtime_error("Cannot start FFmpeg");
    }
    CloseHandle(pi.hThread);
    process = pi.hProcess;
    pipe = write;
    log = errors;
#else
    (void)encoder;
    (void)output;
    throw std::runtime_error(
        "Built-in capture is Windows-only. Use an external recorder on other platforms.");
#endif
}
Recorder::~Recorder() {
    try {
        close();
    } catch (...) {
    }
}
void Recorder::frame(double now, int w, int h) {
#ifdef _WIN32
    if (w != width || h != height)
        throw std::runtime_error("Recording size changed; stop capture before resizing");
    if (start < 0)
        start = now;
    int target = int((now - start) * 30) + 1;
    if (target <= frames)
        return;
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, pixels.data());
    // Duplicate a real frame only when a wall-clock interval was missed. Log every
    // duplicate; simulation always uses actual elapsed time, never offline stepping.
    bool duplicate = false;
    while (frames < target) {
        size_t offset = 0;
        while (offset < pixels.size()) {
            DWORD written = 0;
            if (!WriteFile(HANDLE(pipe), pixels.data() + offset, DWORD(pixels.size() - offset),
                           &written, nullptr) ||
                written == 0)
                throw std::runtime_error("Encoder pipe failed");
            offset += written;
        }
        timing << frames << ',' << (now - start) << ',' << int(duplicate) << '\n';
        duplicates += duplicate;
        duplicate = true;
        frames++;
    }
#else
    (void)now;
    (void)w;
    (void)h;
#endif
}
void Recorder::close() {
#ifdef _WIN32
    if (!process)
        return;
    CloseHandle(HANDLE(pipe));
    pipe = nullptr;
    DWORD wait = WaitForSingleObject(HANDLE(process), 30000), code = 1;
    if (wait == WAIT_OBJECT_0)
        GetExitCodeProcess(HANDLE(process), &code);
    CloseHandle(HANDLE(process));
    CloseHandle(HANDLE(log));
    process = log = nullptr;
    timing.close();
    if (code)
        throw std::runtime_error("FFmpeg did not finish successfully");
#endif
}
} // namespace lvh
