# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0 兼容预览

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Português](README.pt.md) | [Italiano](README.it.md)

本项目基于 AstroQuest/shadPS4，为 **Fate/Grand Order VR feat. Mash Kyrielight** 提供兼容支持，目标为日版 PS4 游戏 **CUSA09078**，版本 **01.00 / 01.01**。PC 通过 Virtual Desktop / VDXR 使用 OpenXR；Quest APK 则使用 ARM64 核心、FEX 和 Turnip 在头显本地运行。

本仓库目前为**私有预览**。兼容演示和后续游玩素材将一起制作发布视频；计划仓库、Release与视频一起公开。现在不自动公开。

## 视频预览

[观看兼容演示视频](https://youtu.be/zBSpUSqpUaw)。视频当前为YouTube私享，只有拥有者授权的观众可以观看；计划2026-10-10与GitHub项目一起公开，目前没有设置自动发布。

视频PCVR片段使用VDXR、内部1.50倍；Quest单机片段为头显本地1.00倍。有游戏PC时优先推荐Virtual Desktop串流，画质更好。本次八语言支持指README及视频资料，原版日语游戏和英文设置界面没有翻译。

## 用户实测（PC：2026-10-07；Quest：2026-10-06）

| 路线 / 档位 | 用户反馈 | 建议 |
| --- | --- | --- |
| PC / VDXR 1.50 | 画质效果很好 | 用户确认完整通关；重复运行稳定性与定量帧率未单独测试 |
| Quest 3 1.00 | 锯齿严重 | 原版回退档 |
| Quest 3 1.10 | 效果还行，仍有锯齿 | Quest优先尝试此档 |
| Quest 3 1.25 | 明显卡顿 | 性能测试档，卡顿时回退 |

用户已确认PCVR1.5倍完整通关，画质反馈为实际体感；没有新的定量FPS记录。测试PC记录为i5-13400F / RTX4070 / 64GB RAM。发布包默认**关闭（100）**，用户自行选择，支持原版回退。

已验证游戏内真实目标增长：每眼100=1408×1512、110=1536×1663、125=1792×1890、PC150=2048×2268。倍率补丁仅替换游戏已核实的1.4f请求，保留其他请求和Unity分配检查，避免读回/设置循环重复放大。VDXR显示的百分比与游戏内部倍率分别记录。

## PCVR 0.2.1 转场修复

高倍率曾在剧情转场申请图形内存失败，原游戏报错字符串又触发闪退。现在同步增长游戏图形池和模拟器本进程的配套内存预算，修正报错字符串；100关闭档保留原程序回退。临时预算不写入保存设置，沿用原存档。

用户2026-10-07先确认1.5倍转场复测通过，随后补充确认已完整通关；记录的VDXR会话正常退出。125/150短时桌面启动及100回退均通过。此修复增加PC内存需求；发布包仍默认100，由用户选择倍率。Quest APK与Quest源码沿用0.2.0，本次没有把PC修复套入Quest。详细边界见[验证摘要](TESTING.md)与[用户验收](docs/USER_ACCEPTANCE_20261007.md)。

## 下载与启动

默认说明与设置界面为英文，本页保留中文说明。维护者在Draft Release中准备Windows便携ZIP、Quest0.2.0 APK、源码ZIP和SHA256SUMS。APK与便携包不包含PS4游戏、PKG、固件、用户存档或密钥。

### Windows / PCVR

1. 解压 `FGO-VR-0.2.1-PCVR-Windows.zip`。
2. 将自己的已解包本体放入 `FGO-PC/games/CUSA09078`，其中包含 `eboot.bin`；可选1.01更新放入 `CUSA09078-UPDATE`。本体缺失时更新不能独立启动。
3. 安装并连接Virtual Desktop，启动Streamer。入口对子进程指定VDXR，不更改系统OpenXR注册。
4. 双击 `Launch-PCVR.cmd`（也保留原中文入口）。关闭模拟器窗口退出。
5. `Resolution-Settings.cmd` 提供设置窗口（需Python3/Tk）。没有Python也可编辑 `FGO-Resolution/settings.json`，或使用 `profiles` 内的直接档位入口。设置重启后生效。
6. `Launch-PCVR-Original.cmd` 强制使用原程序，沿用同一存档目录。

外部依赖：Windows64位、Vulkan显卡驱动、Microsoft Visual C++运行库、Virtual Desktop Streamer和头显端Virtual Desktop。可选系统字体按AstroQuest说明自行配置，未随包提供PS4系统文件。

存档位置：`FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`。先关闭游戏，再备份整个标题目录。

### Quest 3 本地

安装 `FGO-VR-0.2.0-Quest3.apk`（包名 `com.fgovr.quest`，版本码2）。同签名升级可保留数据。使用ADB将自己的本体解包目录放入第一项；只有持有可选1.01更新时才复制第二项：

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

将数据设为可读。具体命令见 [安装说明](docs/INSTALL_QUEST.md)。连接USB并允许调试后，可通过设置窗口推送Quest档位；工具只更新 `fgo_render_scale` 一行并保留其他配置，随后重启应用。默认100关闭，推荐先试110。

日志和设置位于 `/sdcard/Android/data/com.fgovr.quest/files/`；`vrhost.txt` 支持 `fgo_render_scale=100/110/125`。启动后无需PC或VD传输游戏帧。

## 控制

左Touch摇杆四向选择，左右握持为L1/R1、扳机为L2/R2，右A为Cross。右手aim姿态桥接普通DS4追踪，两摇杆同时按下归位。键盘Q/E确认、左右方向键选择。已验证基本操作；完整Move、精准空间指向和全部训练玩法仍需单独验证。

## 已知问题与验收边界

- Quest125用户报告明显卡顿，110仍有锯齿；不承诺稳定帧率或舒适性。
- PC0.2.1修复高倍率剧情转场的图形池不足及错误日志格式：图形池与本进程总Backing/Direct预算同步增长。用户确认PCVR1.5倍完整通关；1.25倍本次仅验证启动。
- 当前额外重投影层、完整Move与部分追踪接口尚有缺口。PCVR1.5倍完整通关已获用户确认；重复运行稳定性与定量帧率未单独测试。
- 另一次PC150会话在Unity预加载阶段发生访问异常，原因未定位，见[验证摘要](TESTING.md)；不将完整通关等同于每次运行稳定。
- 不支持任意PSVR游戏；其他标题需各自验证。

## 源码与构建

基线：[AstroQuest](https://github.com/bigmak94/AstroQuest) commit `9f42c44d4e838e3a0df67913e350c4f098110862`。底层来自 [shadPS4](https://github.com/shadps4-emu/shadPS4)。完整平台补丁位于 `patches`；它们包含前期FGO修改，**不要再叠加旧阶段补丁**。修改文件快照位于 `source_snapshot`。

`tools/prepare_source.py` 可克隆固定基线并应用选定平台的完整补丁。构建输入、固定依赖和开发脚本见 [构建说明](docs/BUILD.md)。开发脚本是现有验证流程快照，部分VS/Java路径需调整；不宣称干净机器上一键可重建。发布签名密钥不在仓库内。

项目按源码文件的GPL-2.0-or-later及各第三方许可证保留声明；见 [LICENSE](LICENSE)、[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) 和 `upstream` 中的原始说明。

## 支持项目

如果这个项目对你有帮助，欢迎通过 [Ko-fi / terry2418](https://ko-fi.com/terry2418) 支持后续开发。感谢你的支持。
