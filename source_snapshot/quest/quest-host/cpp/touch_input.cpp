// SPDX-License-Identifier: GPL-2.0-or-later
#include "touch_input.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>
#include "log.h"

namespace {
bool Ok(XrResult result, const char* call) {
    if (XR_FAILED(result)) { LOGE("Touch %s failed: %d", call, result); return false; }
    return true;
}
uint8_t Axis(float value) {
    return static_cast<uint8_t>(std::clamp(std::lround(128.0f + value * 127.0f), 0l, 255l));
}
}

bool TouchInput::Initialize(XrInstance instance_, XrSession session_, XrSpace local_) {
    instance = instance_; session = session_; local = local_;
    xrStringToPath(instance, "/user/hand/left", &hands[0]);
    xrStringToPath(instance, "/user/hand/right", &hands[1]);
    XrActionSetCreateInfo info{XR_TYPE_ACTION_SET_CREATE_INFO};
    std::snprintf(info.actionSetName, sizeof(info.actionSetName), "fgo_touch");
    std::snprintf(info.localizedActionSetName, sizeof(info.localizedActionSetName), "FGO Touch");
    if (!Ok(xrCreateActionSet(instance, &info, &set), "create set")) return false;
    const auto make = [&](XrAction& action, const char* name, XrActionType type, bool split) {
        XrActionCreateInfo create{XR_TYPE_ACTION_CREATE_INFO};
        create.actionType = type;
        std::snprintf(create.actionName, sizeof(create.actionName), "%s", name);
        std::snprintf(create.localizedActionName, sizeof(create.localizedActionName), "%s", name);
        create.countSubactionPaths = split ? 2 : 0;
        create.subactionPaths = split ? hands : nullptr;
        return Ok(xrCreateAction(set, &create, &action), name);
    };
    if (!make(aim, "aim", XR_ACTION_TYPE_POSE_INPUT, true) ||
        !make(sticks, "sticks", XR_ACTION_TYPE_VECTOR2F_INPUT, true) ||
        !make(triggers, "triggers", XR_ACTION_TYPE_FLOAT_INPUT, true) ||
        !make(grips, "grips", XR_ACTION_TYPE_FLOAT_INPUT, true) ||
        !make(clicks, "clicks", XR_ACTION_TYPE_BOOLEAN_INPUT, true) ||
        !make(menu, "menu", XR_ACTION_TYPE_BOOLEAN_INPUT, false)) return false;
    const char* names[] = {"cross", "square", "circle", "triangle"};
    for (int n = 0; n < 4; ++n)
        if (!make(faces[n], names[n], XR_ACTION_TYPE_BOOLEAN_INPUT, false)) return false;
    std::vector<XrActionSuggestedBinding> bindings;
    const auto bind = [&](XrAction action, const char* path) {
        XrPath binding{};
        if (Ok(xrStringToPath(instance, path, &binding), "binding path"))
            bindings.push_back({action, binding});
    };
    for (int hand = 0; hand < 2; ++hand) {
        const char* side = hand ? "right" : "left";
        char path[128];
        for (const auto& entry : {std::pair{aim, "aim/pose"}, {sticks, "thumbstick"},
                                 {triggers, "trigger/value"}, {grips, "squeeze/value"},
                                 {clicks, "thumbstick/click"}}) {
            std::snprintf(path, sizeof(path), "/user/hand/%s/input/%s", side, entry.second);
            bind(entry.first, path);
        }
    }
    bind(menu, "/user/hand/left/input/menu/click");
    bind(faces[0], "/user/hand/right/input/a/click");
    bind(faces[1], "/user/hand/right/input/b/click");
    bind(faces[2], "/user/hand/left/input/x/click");
    bind(faces[3], "/user/hand/left/input/y/click");
    XrPath profile{};
    xrStringToPath(instance, "/interaction_profiles/oculus/touch_controller", &profile);
    XrInteractionProfileSuggestedBinding suggested{XR_TYPE_INTERACTION_PROFILE_SUGGESTED_BINDING};
    suggested.interactionProfile = profile;
    suggested.countSuggestedBindings = static_cast<uint32_t>(bindings.size());
    suggested.suggestedBindings = bindings.data();
    if (!Ok(xrSuggestInteractionProfileBindings(instance, &suggested), "suggest bindings")) return false;
    XrSessionActionSetsAttachInfo attach{XR_TYPE_SESSION_ACTION_SETS_ATTACH_INFO};
    attach.countActionSets = 1; attach.actionSets = &set;
    if (!Ok(xrAttachSessionActionSets(session, &attach), "attach")) return false;
    for (int hand = 0; hand < 2; ++hand) {
        XrActionSpaceCreateInfo space{XR_TYPE_ACTION_SPACE_CREATE_INFO};
        space.action = aim; space.subactionPath = hands[hand]; space.poseInActionSpace.orientation.w = 1;
        if (!Ok(xrCreateActionSpace(session, &space, &aim_spaces[hand]), "aim space")) return false;
    }
    LOGI("Touch bridge ready: DS4 buttons, left stick directions, right aim pose; both stick clicks recenter");
    return true;
}

bool TouchInput::Read(XrTime time, CoreProcess& core, Core::Vr::Protocol::PadPose& pose) {
    XrActiveActionSet active{set, XR_NULL_PATH};
    XrActionsSyncInfo sync{XR_TYPE_ACTIONS_SYNC_INFO};
    sync.countActiveActionSets = 1; sync.activeActionSets = &active;
    if (set == XR_NULL_HANDLE || xrSyncActions(session, &sync) != XR_SUCCESS) {
        core.SetTouchPad({}, true); recenter_held = false; return false;
    }
    bool available = false;
    const auto boolean = [&](XrAction action, int hand = -1) {
        XrActionStateGetInfo get{XR_TYPE_ACTION_STATE_GET_INFO};
        get.action = action; get.subactionPath = hand >= 0 ? hands[hand] : XR_NULL_PATH;
        XrActionStateBoolean state{XR_TYPE_ACTION_STATE_BOOLEAN};
        if (XR_FAILED(xrGetActionStateBoolean(session, &get, &state)) || !state.isActive) return false;
        available = true; return state.currentState == XR_TRUE;
    };
    const auto pull = [&](XrAction action, int hand) {
        XrActionStateGetInfo get{XR_TYPE_ACTION_STATE_GET_INFO}; get.action = action; get.subactionPath = hands[hand];
        XrActionStateFloat state{XR_TYPE_ACTION_STATE_FLOAT};
        if (XR_FAILED(xrGetActionStateFloat(session, &get, &state)) || !state.isActive) return 0.0f;
        available = true; return std::clamp(state.currentState, 0.0f, 1.0f);
    };
    const auto stick = [&](int hand) {
        XrActionStateGetInfo get{XR_TYPE_ACTION_STATE_GET_INFO}; get.action = sticks; get.subactionPath = hands[hand];
        XrActionStateVector2f state{XR_TYPE_ACTION_STATE_VECTOR2F};
        if (XR_FAILED(xrGetActionStateVector2f(session, &get, &state)) || !state.isActive) return XrVector2f{};
        available = true; return state.currentState;
    };
    PadState pad;
    const uint32_t bits[] = {0x4000, 0x8000, 0x2000, 0x1000};
    for (int n = 0; n < 4; ++n) if (boolean(faces[n])) pad.buttons |= bits[n];
    if (boolean(menu)) pad.buttons |= 0x8;
    const bool left_click = boolean(clicks, 0), right_click = boolean(clicks, 1);
    const bool recenter = left_click && right_click;
    if (recenter && !recenter_held)
        pose.flags |= Core::Vr::Protocol::PadPose::RecenterSeat | Core::Vr::Protocol::PadPose::RecenterYaw;
    recenter_held = recenter;
    if (!recenter) { if (left_click) pad.buttons |= 0x2; if (right_click) pad.buttons |= 0x4; }
    if (pull(grips, 0) > .5f) pad.buttons |= 0x400;
    if (pull(grips, 1) > .5f) pad.buttons |= 0x800;
    pad.left_trigger = static_cast<uint8_t>(std::lround(pull(triggers, 0) * 255));
    pad.right_trigger = static_cast<uint8_t>(std::lround(pull(triggers, 1) * 255));
    if (pad.left_trigger > 127) pad.buttons |= 0x100;
    if (pad.right_trigger > 127) pad.buttons |= 0x200;
    const auto left = stick(0), right = stick(1);
    pad.left_x = Axis(left.x); pad.left_y = Axis(-left.y);
    pad.right_x = Axis(right.x); pad.right_y = Axis(-right.y);
    if (left.x < -.55f) pad.buttons |= 0x80;
    if (left.x > .55f) pad.buttons |= 0x20;
    if (left.y > .55f) pad.buttons |= 0x10;
    if (left.y < -.55f) pad.buttons |= 0x40;
    core.SetTouchPad(available ? pad : PadState{}, true);
    XrActionStateGetInfo get{XR_TYPE_ACTION_STATE_GET_INFO}; get.action = aim; get.subactionPath = hands[1];
    XrActionStatePose state{XR_TYPE_ACTION_STATE_POSE};
    if (XR_FAILED(xrGetActionStatePose(session, &get, &state)) || !state.isActive) return false;
    XrSpaceVelocity velocity{XR_TYPE_SPACE_VELOCITY};
    XrSpaceLocation location{XR_TYPE_SPACE_LOCATION}; location.next = &velocity;
    constexpr XrSpaceLocationFlags needed = XR_SPACE_LOCATION_POSITION_VALID_BIT | XR_SPACE_LOCATION_ORIENTATION_VALID_BIT;
    if (XR_FAILED(xrLocateSpace(aim_spaces[1], local, time, &location)) || (location.locationFlags & needed) != needed) return false;
    pose.flags |= Core::Vr::Protocol::PadPose::PositionValid | Core::Vr::Protocol::PadPose::OrientationValid;
    pose.position[0] = location.pose.position.x; pose.position[1] = location.pose.position.y; pose.position[2] = location.pose.position.z;
    pose.orientation[0] = location.pose.orientation.x; pose.orientation[1] = location.pose.orientation.y;
    pose.orientation[2] = location.pose.orientation.z; pose.orientation[3] = location.pose.orientation.w;
    if (velocity.velocityFlags & XR_SPACE_VELOCITY_LINEAR_VALID_BIT) {
        pose.linear_velocity[0] = velocity.linearVelocity.x; pose.linear_velocity[1] = velocity.linearVelocity.y; pose.linear_velocity[2] = velocity.linearVelocity.z;
    }
    if (velocity.velocityFlags & XR_SPACE_VELOCITY_ANGULAR_VALID_BIT) {
        pose.angular_velocity[0] = velocity.angularVelocity.x; pose.angular_velocity[1] = velocity.angularVelocity.y; pose.angular_velocity[2] = velocity.angularVelocity.z;
    }
    if (!logged) { LOGI("Touch right aim pose valid; forwarding to DS4 tracker"); logged = true; }
    return true;
}

void TouchInput::Destroy() {
    for (auto& space : aim_spaces) { if (space) xrDestroySpace(space); space = XR_NULL_HANDLE; }
    if (set) xrDestroyActionSet(set);
    set = XR_NULL_HANDLE;
}
