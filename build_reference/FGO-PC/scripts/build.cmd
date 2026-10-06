@echo off
setlocal
for %%I in ("%~dp0..\..") do set "FGOVR_ROOT=%%~fI"
call "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 exit /b 1
set "PATH=%FGOVR_ROOT%\tools\llvm-21.1.8\bin;%PATH%"
set "GIT_CONFIG_COUNT=1"
set "GIT_CONFIG_KEY_0=safe.directory"
set "GIT_CONFIG_VALUE_0=*"
set "FGOVR_CMAKE=D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set "FGOVR_NINJA=D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
"%FGOVR_CMAKE%" -S "%FGOVR_ROOT%\source\AstroQuest\shadps4-arm64-main" -B "%FGOVR_ROOT%\FGO-PC\build" -G Ninja "-DCMAKE_MAKE_PROGRAM=%FGOVR_NINJA%" -DCMAKE_C_COMPILER=clang-cl -DCMAKE_CXX_COMPILER=clang-cl -DCMAKE_BUILD_TYPE=Release -DENABLE_DISCORD_RPC=OFF -DENABLE_UPDATER=OFF -DENABLE_TESTS=OFF -DENABLE_OPENXR=ON -DCMAKE_POLICY_VERSION_MINIMUM=3.5
if errorlevel 1 exit /b 1
"%FGOVR_CMAKE%" --build "%FGOVR_ROOT%\FGO-PC\build" --parallel 10
exit /b %errorlevel%
