#pragma once
#include <chrono>
#include <thread>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif
namespace lvh {
struct FrameLimiter {
    using Clock=std::chrono::steady_clock;
    static void wait(Clock::time_point start,int rate) {
        if(rate<=0)return;
        auto deadline=start+std::chrono::duration_cast<Clock::duration>(std::chrono::duration<double>(1.0/rate));
        auto now=Clock::now();
        auto sleepTime=deadline-now-std::chrono::microseconds(1000);
        if(sleepTime>Clock::duration::zero()) {
#ifdef _WIN32
            struct Timer {
                HANDLE handle=CreateWaitableTimerExW(nullptr,nullptr,CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,TIMER_ALL_ACCESS);
                ~Timer(){if(handle)CloseHandle(handle);}
            };
            static Timer timer;
            LARGE_INTEGER due;
            due.QuadPart=-std::chrono::duration_cast<std::chrono::duration<long long,std::ratio<1,10000000>>>(sleepTime).count();
            if(timer.handle && SetWaitableTimer(timer.handle,&due,0,nullptr,nullptr,FALSE))
                WaitForSingleObject(timer.handle,INFINITE);
            else std::this_thread::sleep_for(sleepTime);
#else
            std::this_thread::sleep_for(sleepTime);
#endif
        }
        while(Clock::now()<deadline)std::this_thread::yield();
    }
};
} // namespace lvh
