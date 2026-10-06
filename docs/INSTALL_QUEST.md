# Quest 3 本地版安装

先开启开发者模式，通过USB连接并在头显中允许USB调试；只连接一台设备。使用Windows包内的ADB或自己安装的官方platform-tools。

```powershell
adb devices
adb install -r FGO-VR-0.2.0-Quest3.apk
adb shell mkdir -p /data/local/tmp/fgovr/games
adb push CUSA09078 /data/local/tmp/fgovr/games/
adb push CUSA09078-UPDATE /data/local/tmp/fgovr/games/
adb shell chmod -R a+rX /data/local/tmp/fgovr/games
adb shell am start -n com.fgovr.quest/.MainActivity
```

游戏目录需包含自己的本体数据，更新不是独立游戏。APK没有游戏资产。已有同签名版本用 `install -r` 升级；不要为升级而卸载清空应用数据。自己构建的不同签名APK不能直接覆盖发布APK。

调整分辨率：打开Windows包内的设置工具、选Quest110并点击USB推送，然后关闭并重新打开应用。也可自行编辑外部配置文件：

```text
/sdcard/Android/data/com.fgovr.quest/files/vrhost.txt
fgo_render_scale=110
```

100关闭，110推荐先试，125用户报告明显卡顿。保留已有其他设置，只更改这一行。推送工具会备份原配置，不会自动关闭游戏。
