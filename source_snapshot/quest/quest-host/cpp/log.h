// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <android/log.h>

#define LOG_TAG "FgoVR"

/// Writes a line to the system log and, once SetLogFile was called, to that file too. The system
/// log is a ring shared with everything else on the headset: by the time somebody asks what
/// happened in a session, it has moved on.
void HostLog(int priority, const char* format, ...) __attribute__((format(printf, 2, 3)));
void SetLogFile(const char* path);

#define LOGI(...) HostLog(ANDROID_LOG_INFO, __VA_ARGS__)
#define LOGW(...) HostLog(ANDROID_LOG_WARN, __VA_ARGS__)
#define LOGE(...) HostLog(ANDROID_LOG_ERROR, __VA_ARGS__)
