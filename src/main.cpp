#include "animation.hpp"
#include "director.hpp"
#include "fixed_step.hpp"
#include "game.hpp"
#include "mouse_look.hpp"
#include "mouse_motion.hpp"
#include "recorder.hpp"
#include "scene.hpp"
#include "ui.hpp"
#include "world.hpp"
#include <GLFW/glfw3.h>
#include <imgui.h>
#ifdef _WIN32
#define NOMINMAX
#define WIN32_LEAN_AND_MEAN
#define GLFW_EXPOSE_NATIVE_WIN32
#include <GLFW/glfw3native.h>
#endif
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <thread>
namespace {
struct Mouse {
    lvh::Game *game;
    bool locked = true, focused = true;
    lvh::MouseLook look;
    GLFWcursor *hiddenCursor = nullptr;
    lvh::MouseMotion motion;
#ifdef _WIN32
    WNDPROC previousProc = nullptr;
#endif
};
void focus(GLFWwindow *w, int focused) {
    auto *m=static_cast<Mouse *>(glfwGetWindowUserPointer(w));
    if (!m) return;
    m->focused=focused==GLFW_TRUE;
    m->look.reset();
    m->motion.reset();
}
#ifdef _WIN32
LRESULT CALLBACK mouseMessages(HWND window,UINT message,WPARAM wparam,LPARAM lparam) {
    auto *mouse=reinterpret_cast<Mouse *>(GetPropW(window,L"LVH.Mouse"));
    if (!mouse) return DefWindowProcW(window,message,wparam,lparam);
    if (message==WM_INPUT && mouse->locked && mouse->focused) {
        RAWINPUT input{};UINT size=sizeof(input);
        if (GetRawInputData(reinterpret_cast<HRAWINPUT>(lparam),RID_INPUT,&input,&size,sizeof(RAWINPUTHEADER))!=UINT(-1)
            && input.header.dwType==RIM_TYPEMOUSE) {
            auto &m=input.data.mouse;
            if (m.usFlags & MOUSE_MOVE_ABSOLUTE) {
                bool desktop=(m.usFlags & MOUSE_VIRTUAL_DESKTOP)!=0;
                float width=float(GetSystemMetrics(desktop ? SM_CXVIRTUALSCREEN : SM_CXSCREEN));
                float height=float(GetSystemMetrics(desktop ? SM_CYVIRTUALSCREEN : SM_CYSCREEN));
                mouse->motion.absolutePosition(reinterpret_cast<std::uintptr_t>(input.header.hDevice),
                    float(m.lLastX)*width/65535.f,float(m.lLastY)*height/65535.f);
            } else mouse->motion.relative(float(m.lLastX),float(m.lLastY));
        }
    }
    return CallWindowProcW(mouse->previousProc,window,message,wparam,lparam);
}
void installMouseEvents(GLFWwindow *window,Mouse &mouse) {
    HWND native=glfwGetWin32Window(window);
    RAWINPUTDEVICE device{1,2,0,native};
    if (!RegisterRawInputDevices(&device,1,sizeof(device)))
        throw std::runtime_error("Cannot register relative mouse input");
    if (!SetPropW(native,L"LVH.Mouse",&mouse))
        throw std::runtime_error("Cannot attach mouse input");
    mouse.previousProc=reinterpret_cast<WNDPROC>(SetWindowLongPtrW(native,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(mouseMessages)));
    if (!mouse.previousProc) throw std::runtime_error("Cannot install mouse input");
}
#endif
void captureMouse(GLFWwindow *w, Mouse &mouse, bool locked) {
    mouse.locked=locked;
    mouse.look.reset();
    mouse.motion.reset();
    if (glfwRawMouseMotionSupported())
        glfwSetInputMode(w,GLFW_RAW_MOUSE_MOTION,GLFW_FALSE);
    // CAPTURED confines the physical cursor without GLFW's virtual/recenter loop.
#ifdef _WIN32
    glfwSetInputMode(w,GLFW_CURSOR,locked ? GLFW_CURSOR_CAPTURED : GLFW_CURSOR_NORMAL);
#else
    glfwSetInputMode(w,GLFW_CURSOR,locked ? GLFW_CURSOR_DISABLED : GLFW_CURSOR_NORMAL);
    if (glfwRawMouseMotionSupported()) glfwSetInputMode(w,GLFW_RAW_MOUSE_MOTION,locked);
#endif
    glfwSetCursor(w,locked ? mouse.hiddenCursor : nullptr);
    if (ImGui::GetCurrentContext()) {
        auto &flags=ImGui::GetIO().ConfigFlags;
        if (locked) flags |= ImGuiConfigFlags_NoMouse | ImGuiConfigFlags_NoMouseCursorChange;
        else flags &= ~(ImGuiConfigFlags_NoMouse | ImGuiConfigFlags_NoMouseCursorChange);
    }

}
void error(int code, const char *msg) {
    std::cerr << "GLFW " << code << ": " << msg << '\n';
}
} // namespace
int main(int argc, char **argv) {
    using namespace lvh;
    bool grey = false, hidden = false, help = false, preview = false, facePreview = false,
         restPose = false, demo = false, autoRoute = false, finalePreview = false, thirdPerson = false;
    double duration = 0;
    std::string previewClip = "Idle";
    int maxFrames = 0, wantedWidth = 1280, wantedHeight = 720;
    fs::path encoder, record, captureWait, screenshot, root = fs::absolute(argv[0]).parent_path();
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--greybox")
            grey = true;
        else if (arg == "--character-preview")
            preview = true;
        else if (arg == "--face-preview") {
            preview = facePreview = true;
        } else if (arg == "--rest-pose")
            restPose = true;
        else if (arg == "--clip" && i + 1 < argc)
            previewClip = argv[++i];
        else if (arg == "--record" && i + 1 < argc)
            record = argv[++i];
        else if (arg == "--ffmpeg" && i + 1 < argc)
            encoder = argv[++i];
        else if (arg == "--capture-wait" && i + 1 < argc)
            captureWait = argv[++i];
        else if (arg == "--demo")
            demo = true;
        else if (arg == "--third-person")
            thirdPerson = true;
        else if (arg == "--finale-preview")
            finalePreview = true;
        else if (arg == "--auto-route")
            autoRoute = true;
        else if (arg == "--seconds" && i + 1 < argc)
            duration = std::stod(argv[++i]);
        else if (arg == "--hidden")
            hidden = true;
        else if (arg == "--frames" && i + 1 < argc)
            maxFrames = std::stoi(argv[++i]);
        else if (arg == "--screenshot" && i + 1 < argc)
            screenshot = argv[++i];
        else if (arg == "--root" && i + 1 < argc)
            root = argv[++i];
        else if (arg == "--1080p") {
            wantedWidth = 1920;
            wantedHeight = 1080;
        } else {
            std::cerr << "Unknown argument: " << arg << '\n';
            return 2;
        }
    }
    if (preview) {
        wantedWidth = 1100;
        wantedHeight = 1100;
    }
    glfwSetErrorCallback(error);
    if (!glfwInit())
        return 1;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif
    glfwWindowHint(GLFW_VISIBLE, hidden ? GLFW_FALSE : GLFW_TRUE);
    glfwWindowHint(GLFW_SAMPLES, 0);
    GLFWwindow *window =
        glfwCreateWindow(wantedWidth, wantedHeight, "Laser Vault Heist", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return 1;
    }
    glfwMakeContextCurrent(window);
    glfwSwapInterval(0);
    if (!gladLoadGL(reinterpret_cast<GLADloadfunc>(glfwGetProcAddress))) {
        glfwDestroyWindow(window);
        glfwTerminate();
        return 1;
    }
    int result = 0;
    try {
        std::string gpu = reinterpret_cast<const char *>(glGetString(GL_RENDERER));
        std::string version = reinterpret_cast<const char *>(glGetString(GL_VERSION));
        std::cout << "OpenGL " << version << "\nGPU " << gpu << "\n";
        fs::create_directories(root / "evidence");
        std::ofstream(root / "evidence" / "runtime-info.txt")
            << "OpenGL: " << version << "\nGPU: " << gpu << "\n";
        Game game;
        game.thirdPerson=thirdPerson;
        Director director;
        Route route;
        FixedStep clock;
        bool menu = !hidden && !preview && !demo && !autoRoute && !finalePreview;
        Mouse mouse{};
        mouse.game=&game;
        mouse.locked=false;
        mouse.focused = glfwGetWindowAttrib(window,GLFW_FOCUSED)==GLFW_TRUE;
        glfwSetWindowUserPointer(window, &mouse);
        glfwSetWindowFocusCallback(window,focus);
#ifdef _WIN32
        installMouseEvents(window,mouse);
#endif
        unsigned char transparent[4]={0,0,0,0};
        GLFWimage cursorImage{1,1,transparent};
        mouse.hiddenCursor=glfwCreateCursor(&cursorImage,0,0);
        if (!mouse.hiddenCursor) throw std::runtime_error("Cannot create gameplay cursor");
        fs::current_path(root);
        Scene scene;
        Animator animator;
        if (grey)
            scene.greybox();
        else {
            if (!preview)
                scene.load(root / "assets" / "vault.scene");
            scene.load(root / "assets" / "thief.scene");
            animator.load(root / "assets" / "thief.lvanim");
            game.danceDuration = animator.duration("Dance");
        }
        if (finalePreview) {
            game.position = {0,0,-12.74f};
            game.lastCrossed = game.safeOpened = true;
            game.state = State::Finale;
        }
        scene.buildBatches();
        Renderer renderer(root / "shaders");
        renderer.characterPreview = preview;
        initUI(window);
        captureMouse(window,mouse,!menu && !demo && !autoRoute && !hidden);
        double started = glfwGetTime(), last = started, fpsTime = last;
        int frame = 0, fpsFrames = 0;
        float fps = 0;
        bool wasE = false, wasR = false, wasV = false, wasEsc = false, wasF1 = false, wasF12 = false;
        State beforePause = State::Playing;
        std::ofstream timings(root / "evidence" / "frame-times.csv");
        timings << "frame,seconds,frame_ms,state\n";
        std::ofstream trace(root / "evidence" / "gameplay-trace.csv");
        trace << "wall_seconds,demo_seconds,x,z,crouching,body_height,lamp,cctv,state,safe_time,"
                 "retries\n";
        std::ofstream mouseTrace(root / "evidence" / "mouse-input.csv");
        mouseTrace << "seconds,x,y,delta_yaw,delta_pitch,yaw,pitch,sensitivity\n";
        double lastTrace = -1;
        std::unique_ptr<Recorder> recorder;
        if (!record.empty())
            recorder = std::make_unique<Recorder>(encoder, record, wantedWidth, wantedHeight);
        std::string source = readText(root / "assets" / "renderer-source.txt");
        while (!glfwWindowShouldClose(window)) {
            double now = glfwGetTime(), elapsed = now - last;
            last = now;
            glfwPollEvents();
            // Consume fresh movement events once; never warp the Windows cursor.
            if (mouse.locked && mouse.focused) {
                double x=0,y=0;
#ifdef _WIN32
                const auto counts=mouse.motion.take();
                x=counts.x;y=counts.y;
                const auto delta=counts*game.mouseSensitivity;
#else
                glfwGetCursorPos(window,&x,&y);
                mouse.look.sensitivity=game.mouseSensitivity;
                const auto delta=mouse.look.sample(x,y);
#endif
                game.yaw=std::remainder(game.yaw+delta.x,360.f);
                float limit=game.thirdPerson ? 60.f : 85.f;
                game.pitch=std::clamp(game.pitch-delta.y,-limit,limit);
                if (delta.x!=0 || delta.y!=0)
                    mouseTrace << now-started << ',' << x << ',' << y << ',' << delta.x << ','
                               << delta.y << ',' << game.yaw << ',' << game.pitch << ','
                               << game.mouseSensitivity << '\n';
            }
            auto key = [&](int k) { return glfwGetKey(window, k) == GLFW_PRESS; };
            bool esc = key(GLFW_KEY_ESCAPE);
            if (esc && !wasEsc && !menu && !demo) {
                if (game.state == State::Pause)
                    game.state = beforePause;
                else {
                    beforePause = game.state;
                    game.state = State::Pause;
                }
                captureMouse(window,mouse,game.state != State::Pause);
            }
            wasEsc = esc;
            if (menu && key(GLFW_KEY_ENTER))
                menu = false;
            bool f1 = key(GLFW_KEY_F1);
            if (f1 && !wasF1)
                help = !help;
            wasF1 = f1;
            bool v=key(GLFW_KEY_V);
            if(v && !wasV && !menu && !preview && !demo) game.toggleCamera();
            wasV=v;
            Input input;
            input.forward = float(key(GLFW_KEY_W)) - float(key(GLFW_KEY_S));
            input.right = float(key(GLFW_KEY_D)) - float(key(GLFW_KEY_A));
            input.crouch = key(GLFW_KEY_LEFT_CONTROL) || key(GLFW_KEY_C);
            bool e = key(GLFW_KEY_E), r = key(GLFW_KEY_R);
            input.interact = e && !wasE;
            input.retry = r && !wasR;
            wasE = e;
            wasR = r;
            if (!menu && (!recorder || now - started > .5) &&
                (captureWait.empty() || fs::exists(captureWait)))
                clock.advance(elapsed, input, [&](float dt, const Input &pending) {
                    Input applied = demo        ? director.next(game, dt)
                                    : autoRoute ? route.next(game)
                                                : pending;
                    if (autoRoute && (game.state == State::Victory || game.state == State::Alarm)) {
                        applied.retry = true;
                        route = Route();
                    }
                    game.update(dt, applied);
                });
            bool alarm = game.state == State::Alarm ||
                         (game.state == State::Pause && beforePause == State::Alarm);
            auto lights = updateWorld(scene, game, alarm);
            bool locked = !menu && !demo && !autoRoute && !hidden && game.state == State::Playing;
            if (mouse.locked != locked) {
                captureMouse(window,mouse,locked);
            }
            int width, height;
            glfwGetFramebufferSize(window, &width, &height);
            if (width <= 0 || height <= 0) {
                glfwWaitEventsTimeout(.05);
                last = glfwGetTime();
                continue;
            }
            renderer.width = width;
            renderer.height = height;
            if (!grey) {
                bool moving = game.moveSpeed > .02f && game.state == State::Playing;
                std::string clip = "Idle";
                if (preview) clip = previewClip;
                else if (game.safeOpened) clip = game.safeTime >= Game::safeOpenDuration ? "Dance" : "Idle";
                else clip = game.locomotionClip();
                float phase = game.time / animator.duration(clip);
                if (!preview) {
                    if (clip == "Dance") phase = (game.safeTime - Game::safeOpenDuration) / game.danceDuration;
                    else if (clip == "Interact") phase = 1.f - game.interactionTime / .7f;
                    else if (moving) phase = game.stepDistance / (game.crouching ? .85f : 1.2f);
                }
                animator.update(clip, phase, game.state == State::Pause ? 0.f : float(elapsed),
                                preview && restPose,
                                game.crouching && game.interactionTime > 0
                                    ? 1.f - game.interactionTime / .7f
                                    : -1.f);
                scene.skinPalette = animator.palette;
                scene.showCharacter = game.safeOpened || game.thirdPersonVisible();
                // Reveal the performer only after the door has cleared the stage.
                scene.characterPresent = !game.safeOpened || game.safeTime >= Game::safeOpenDuration;
                float facing = game.characterFacing();
                scene.characterModel = preview ? glm::mat4(1)
                    : game.safeOpened ? glm::translate(glm::mat4(1),glm::vec3(.55f,0,-12.3f)) *
                          glm::rotate(glm::mat4(1),glm::radians(35.f),glm::vec3(0,1,0))
                    : glm::translate(glm::mat4(1),game.position) *
                          glm::rotate(glm::mat4(1),facing,glm::vec3(0,1,0));
            }
            glm::vec3 eyePos = game.camera();
            glm::mat4 view = game.view();
            if (preview) {
                eyePos = facePreview ? glm::vec3(0, 1.69f, .58f) : glm::vec3(0, 1.02f, 2.05f);
                view = glm::lookAt(eyePos,
                                   facePreview ? glm::vec3(0, 1.69f, 0) : glm::vec3(0, .98f, 0),
                                   glm::vec3(0, 1, 0));
                lights = {{{-1.2f, 2.3f, 2}, glm::vec3(1, .85f, .72f), {0, -1, 0}, 1.2f},
                          {{1.4f, 1.9f, 1.2f}, glm::vec3(.65f, .78f, 1), {0, -1, 0}, .9f},
                          {{0, 2, -1}, glm::vec3(1, .7f, .4f), {0, -1, 0}, 1.f}};
            }
            renderer.frame(scene, view, eyePos, lights, alarm, game.cctvView, game.time);
            fpsFrames++;
            if (now - fpsTime > .35) {
                fps = float(fpsFrames / (now - fpsTime));
                fpsFrames = 0;
                fpsTime = now;
            }
            beginUI();
            UIAction action = drawUI(
                game, fps, width, height, gpu, help, menu, demo ? director.caption() : "",
                demo && director.diagnostics()
                    ? ("OpenGL: " + version + "\\nGPU: " + gpu + "\\n\\n" + source)
                    : "",
                preview,
                demo && director.elapsed >= 33 && director.elapsed < 49 ? renderer.cctvDisplay.color
                                                                        : 0);
            finishUI();
            if (action == UIAction::Begin)
                menu = false;
            if (action == UIAction::Resume)
                game.state = beforePause;
            if (action == UIAction::Retry) {
                game.reset();
                route = Route();
            }
            if (action == UIAction::Quit)
                glfwSetWindowShouldClose(window, true);
            bool f12 = key(GLFW_KEY_F12);
            if (f12 && !wasF12)
                saveFramebuffer(root / "evidence" / ("capture-" + std::to_string(frame) + ".png"),
                                width, height);
            wasF12 = f12;
            if (now - lastTrace >= .1) {
                lastTrace = now;
                trace << now - started << ',' << director.elapsed << ',' << game.position.x << ','
                      << game.position.z << ',' << game.crouching << ',' << game.bodyHeight << ','
                      << game.lamp << ',' << game.cctvView << ',' << int(game.state) << ','
                      << game.safeTime << ',' << game.retries << '\n';
            }
            frame++;
            timings << frame << ',' << now << ',' << elapsed * 1000.0 << ',' << int(game.state)
                    << '\n';
            if ((maxFrames && frame >= maxFrames) || (duration > 0 && now - started >= duration) ||
                (demo && director.elapsed >= Director::duration)) {
                if (!screenshot.empty())
                    saveFramebuffer(screenshot, width, height);
                glfwSetWindowShouldClose(window, true);
            }
            if (recorder && now - started > .5)
                recorder->frame(now, width, height);
            glfwSwapBuffers(window);
            GLenum glError = glGetError();
            if (glError != GL_NO_ERROR)
                throw std::runtime_error("OpenGL error " + std::to_string(glError));
        }
        if (recorder)
            recorder->close();
        stopUI();
#ifdef _WIN32
        SetWindowLongPtrW(glfwGetWin32Window(window),GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(mouse.previousProc));
        RemovePropW(glfwGetWin32Window(window),L"LVH.Mouse");
#endif
        glfwDestroyCursor(mouse.hiddenCursor);
        std::cout << "Rendered " << frame << " frames without GL errors\n";
    } catch (const std::exception &e) {
        std::cerr << "FATAL: " << e.what() << '\n';
        result = 1;
    }
    glfwDestroyWindow(window);
    glfwTerminate();
    return result;
}
