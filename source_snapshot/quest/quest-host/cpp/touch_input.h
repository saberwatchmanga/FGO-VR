// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <openxr/openxr.h>
#include "core_process.h"

// A tracked Touch controller acts as the game's single DS4, not as a fabricated Move device.
class TouchInput {
public:
    bool Initialize(XrInstance instance, XrSession session, XrSpace local);
    bool Read(XrTime time, CoreProcess& core, Core::Vr::Protocol::PadPose& pose);
    void Destroy();
private:
    XrInstance instance{};
    XrSession session{};
    XrSpace local{};
    XrActionSet set{};
    XrPath hands[2]{};
    XrAction aim{}, sticks{}, triggers{}, grips{}, clicks{}, menu{};
    XrAction faces[4]{};
    XrSpace aim_spaces[2]{};
    bool recenter_held{};
    bool logged{};
};
