# Install the Quest 3 Local Version

Enable Developer Mode, connect the headset by USB, and allow USB debugging in the headset. Connect only one device.

    adb devices
    adb install -r FGO-VR-0.2.0-Quest3.apk
    adb shell mkdir -p /data/local/tmp/fgovr/games
    adb push CUSA09078 /data/local/tmp/fgovr/games/
    adb push CUSA09078-UPDATE /data/local/tmp/fgovr/games/
    adb shell chmod -R a+rX /data/local/tmp/fgovr/games
    adb shell am start -n com.fgovr.quest/.MainActivity

Use your own game data in the game folders. The update folder is not a standalone game. The APK does not include game assets. Use install -r to update an existing build signed with the same key; do not uninstall the app just to update it, since that clears app data. An APK you build with a different signing key cannot directly replace the release APK.

To change render scale, open Resolution-Settings.cmd in the Windows package, choose Quest 110, and select **Push Quest settings (USB)**. Close and reopen the app for the change to take effect. You can also edit the external configuration file yourself:

    /sdcard/Android/data/com.fgovr.quest/files/vrhost.txt
    fgo_render_scale=110

At 100, scaling is off. 110 is the suggested first setting. The user reported noticeable stutter at 125. Preserve other settings and change only the fgo_render_scale line. The push tool backs up the existing configuration and does not close the game automatically.