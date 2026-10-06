# 固定源码与构建输入

上游AstroQuest固定commit：`9f42c44d4e838e3a0df67913e350c4f098110862`。

```powershell
python tools/prepare_source.py pc C:\work\fgo-pc-source
python tools/prepare_source.py quest C:\work\fgo-quest-source
```

每个平台只应用自己的complete.patch；core.patch为审阅增量，不再叠加。保留源码快照和子模块清单，不提交嵌套Git目录。

开发构建记录：Windows LLVM21.1.8、VS2022 SDK，VS2026提供CMake/Ninja；Java17；Android NDKr27d、SDK36、build-tools36；固定Debian ARM64 sysroot；FEX `f2b679f6028ce1c38875233aecfcf5d3f8ebecec`，FFmpeg `94dde08c8a9e4271a93a2a7e4159e9fb05d30c0a`。

`upstream/arm64-sysroot-lock.json` 记录本次实际使用的Debian包版本、下载地址和SHA256；重建时按此锁定清单取得包，不以当前滚动仓库最新包替代。现有prepare_arm64_sysroot.py是构建流程参考，并非完整锁定依赖的安装器。FEX另需固定上面的提交，按上游runtime流程及 `patches/build-support/fex-fexcore-only.patch` 准备；prepare_source.py只准备AstroQuest及其Git子模块。

Windows原版回退核心对应 `patches/baseline/fgo-pcvr.patch`；可选分辨率核心对应 `patches/fgo-resolution-pc-complete.patch`。baseline目录中的loading补丁只保留早期桌面实现来源，不与PCVR或complete补丁叠加。

`build_reference` 保存必要构建脚本和当前流程。PC编译开启OpenXR。Quest宿主为Android OpenXR/EGL，核心为ARM64/glibc，使用FEX执行原x86游戏，Turnip处理Vulkan；APK构建复用维护者提供的AstroQuest0.13运行库，并打包自行构建的核心。

脚本中的VS/Java路径是开发机路径快照，工具目录需按自己的环境调整。Quest还需上游AstroQuest APK运行库、LLVM、sysroot以及PC字体嵌入工具。脚本不含游戏数据、发布签名私钥或GitHub凭据；自行签名的APK不能直接覆盖不同签名的已安装版本。

完整历史构建/设备日志不上传；公开可用的摘要在TESTING.md，文件校验在SHA256SUMS和artifact-manifest.json。
