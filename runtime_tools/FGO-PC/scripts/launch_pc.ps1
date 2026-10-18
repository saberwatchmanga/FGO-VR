param(
    [ValidateSet('01.00', '01.01')][string]$GameVersion = '01.01',
    [ValidateSet('Desktop', 'PcVr')][string]$Mode = 'Desktop',
    [ValidateRange(0, 600)][int]$HeadsetWaitSeconds = 60,
    [switch]$NoHeadsetPause,
    [ValidateSet('100', '110', '125', '150')][string]$RenderScale,
    [switch]$CrashDiagnostics,
    [switch]$TransitionFix,
    [ValidateSet('VDXR', 'SteamVR')][string]$OpenXrRuntime = 'VDXR',
    [string]$OpenXrManifest,
    [switch]$CheckOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$FgoInstallDir = Split-Path -Parent $PSScriptRoot
$FgoRuntimeDir = Join-Path $FgoInstallDir 'runtime'
if ($Mode -eq 'PcVr') { $FgoRuntimeDir = Join-Path $FgoInstallDir 'runtime-vr' }
$FgoExe = Join-Path $FgoRuntimeDir 'shadps4.exe'
$FgoResolutionExe = Join-Path (Split-Path -Parent $FgoInstallDir) 'FGO-Resolution\runtime-pc\shadps4.exe'
$FgoDiagnosticExe = Join-Path (Split-Path -Parent $FgoInstallDir) 'FGO-Resolution\runtime-pc\shadps4.exe'
$FgoTransitionExe = Join-Path (Split-Path -Parent $FgoInstallDir) 'FGO-Resolution\runtime-pc\shadps4.exe'
$FgoScale = '100'
if ($Mode -eq 'PcVr') {
    if ($RenderScale) {
        $FgoScale = $RenderScale
    } else {
        $FgoSettingsPath = Join-Path (Split-Path -Parent $FgoInstallDir) 'FGO-Resolution\settings.json'
        if (Test-Path -LiteralPath $FgoSettingsPath) {
            try {
                $FgoSettings = Get-Content -LiteralPath $FgoSettingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
                $FgoRequested = [string]$FgoSettings.pc_scale
                if ($FgoRequested -in @('100','110','125','150')) { $FgoScale = $FgoRequested }
                else { Write-Warning 'Unsupported resolution setting; using original resolution.' }
            } catch {
                Write-Warning 'Unable to read resolution settings; using original resolution.'
            }
        }
    }
    if ($FgoScale -ne '100') {
        if (Test-Path -LiteralPath $FgoResolutionExe) { $FgoExe = $FgoResolutionExe }
        else {
            Write-Warning 'Optional resolution runtime is missing; using the original runtime.'
            $FgoScale = '100'
        }
    }
}
if ($CrashDiagnostics) {
    if ($Mode -ne 'PcVr' -or -not (Test-Path -LiteralPath $FgoDiagnosticExe)) {
        throw 'The independent PCVR diagnostic runtime is missing.'
    }
    $FgoExe = $FgoDiagnosticExe
}
if ($TransitionFix) {
    if ($Mode -ne 'PcVr' -or -not (Test-Path -LiteralPath $FgoTransitionExe)) {
        throw 'The independent PCVR transition-fix runtime is missing.'
    }
    $FgoExe = $FgoTransitionExe
}
$FgoGame = Join-Path $FgoInstallDir 'games\CUSA09078\eboot.bin'
if (-not (Test-Path -LiteralPath $FgoExe) -or -not (Test-Path -LiteralPath $FgoGame)) {
    throw 'FGO PC runtime or game file is missing. Read FGO-PC/README.md.'
}
if (Get-Process -Name shadps4 -ErrorAction SilentlyContinue | Where-Object { $_.Path -in @((Join-Path $FgoRuntimeDir 'shadps4.exe'), $FgoResolutionExe, $FgoDiagnosticExe, $FgoTransitionExe) }) {
    throw 'This FGO PC runtime is already running. Close its game window first.'
}
foreach ($FgoEnvName in @(Get-ChildItem Env: | Where-Object Name -Like 'SHADPS4_*' | ForEach-Object Name)) {
    [Environment]::SetEnvironmentVariable($FgoEnvName, $null, 'Process')
}
$env:SHADPS4_VR = '1'
$env:SHADPS4_OPENXR = '0'
$env:SHADPS4_VR_DEMO = '0'
$env:SHADPS4_XR_WAIT = '0'
$env:SHADPS4_XR_PAUSE = '0'
$env:SHADPS4_TITLE_TIMESTEP = '0'
$env:SHADPS4_FGO_RENDER_SCALE = $FgoScale
if ($CrashDiagnostics) { $env:SHADPS4_FGO_CRASH_DIAGNOSTICS = '1' }
$FgoRuntimeManifest = $null
$FgoSteamVrRunning = $null
if ($Mode -eq 'PcVr') {
    . (Join-Path $PSScriptRoot 'openxr_runtime.ps1')
    $FgoRuntimeManifest = Resolve-FgoOpenXrManifest -Runtime $OpenXrRuntime -ManifestPath $OpenXrManifest
    if ($OpenXrRuntime -eq 'SteamVR') {
        $FgoSteamVrRunning = [bool](Get-Process -Name vrserver -ErrorAction SilentlyContinue)
        if (-not $CheckOnly -and -not $FgoSteamVrRunning) {
            throw 'Connect Steam Link and start SteamVR first, then run this launcher. It does not start SteamVR automatically.'
        }
    }
    # Process-local selection; never change the system OpenXR registration.
    $env:XR_RUNTIME_JSON = $FgoRuntimeManifest
    $env:SHADPS4_OPENXR = '1'
    $env:SHADPS4_XR_WAIT = [string]$HeadsetWaitSeconds
    $env:SHADPS4_XR_PAUSE = $(if ($NoHeadsetPause) { '0' } else { '1' })
    $env:SHADPS4_XR_HEAD = '1'
    $env:SHADPS4_XR_CONTROLLERS = '1'
    $env:SHADPS4_XR_DPAD = '1'
    $env:SHADPS4_XR_HANDS = '1'
    $env:SHADPS4_VR_REFRESH_RATE = '120'
    $env:SHADPS4_VR_FOV_OF = 'psvr'
    $env:SHADPS4_VR_FPS_CAP = '60'
}
$FgoArguments = @('-g', ('"' + $FgoGame + '"'), '-f', 'false')
if ($GameVersion -eq '01.00') { $FgoArguments += '--ignore-game-patch' }
$FgoSessionName = (Get-Date -Format 'yyyyMMdd_HHmmssfff') + '_' + $GameVersion
if ($Mode -eq 'PcVr') { $FgoSessionName += '_PCVR' }
if ($Mode -eq 'PcVr' -and $OpenXrRuntime -eq 'SteamVR') { $FgoSessionName += '_SteamVR' }
if ($TransitionFix) { $FgoSessionName += '_TRANSITIONFIX' }
if ($CrashDiagnostics) { $FgoSessionName += '_DIAGNOSTIC' }
$FgoSession = Join-Path $FgoInstallDir ('sessions\' + $FgoSessionName)
if (-not $CheckOnly) { New-Item -ItemType Directory -Path $FgoSession | Out-Null }
$FgoHashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
$FgoExeStream = [System.IO.File]::OpenRead($FgoExe)
try {
    $FgoExeHash = [System.BitConverter]::ToString($FgoHashAlgorithm.ComputeHash($FgoExeStream)).Replace('-', '')
} finally {
    $FgoExeStream.Dispose()
    $FgoHashAlgorithm.Dispose()
}
$FgoRecord = [ordered]@{
    game_version = $GameVersion
    executable = $FgoExe
    executable_sha256 = $FgoExeHash
    arguments = $FgoArguments
    working_directory = $FgoRuntimeDir
    started_at = $(if ($CheckOnly) { $null } else { (Get-Date).ToString('o') })
    mode = $Mode
    check_only = [bool]$CheckOnly
    resolution_percent_requested = [int]$FgoScale
    crash_diagnostics = [bool]$CrashDiagnostics
    transition_fix = [bool]$TransitionFix
    openxr_runtime_manifest = $FgoRuntimeManifest
    openxr_runtime_requested = $(if ($Mode -eq 'PcVr') { $OpenXrRuntime } else { $null })
    steamvr_server_running = $FgoSteamVrRunning
    environment = [ordered]@{}
}
foreach ($FgoEnv in @(Get-ChildItem Env: | Where-Object { $_.Name -like 'SHADPS4_*' -or $_.Name -eq 'XR_RUNTIME_JSON' })) {
    $FgoRecord.environment[$FgoEnv.Name] = $FgoEnv.Value
}
if ($CheckOnly) {
    # No game, runtime, session directory, or diagnostic-log mutation in preflight.
    $FgoRecord | ConvertTo-Json -Depth 4
    return
}
$FgoRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $FgoSession 'run.json') -Encoding UTF8
if ($CrashDiagnostics) {
    foreach ($FgoDiagnosticLogName in @('fgo_crash_context.txt', 'fgo_allocation_failure.txt', 'fgo_gfx_pool.txt')) {
        $FgoCrashLog = Join-Path $FgoRuntimeDir ('user\log\' + $FgoDiagnosticLogName)
        if (Test-Path -LiteralPath $FgoCrashLog) {
            Move-Item -LiteralPath $FgoCrashLog -Destination (Join-Path $FgoSession ('previous_' + $FgoDiagnosticLogName))
        }
    }
    Write-Host 'FGO PCVR diagnostic: normal-speed gameplay; crash context will be preserved automatically.'
}
if ($TransitionFix) { Write-Host ('Transition fix test: graphics memory budget follows resolution; original saves and ' + $OpenXrRuntime + '.') }
Write-Host ('FGO VR ' + $Mode + ' ' + $GameVersion + ' - Q / E: game confirm, arrows: menu selection, Enter: Options')
if ($Mode -eq 'PcVr') {
    Write-Host ('Internal resolution: ' + $FgoScale + '% of original dimensions (100 = OFF). Restart to change.')
    Write-Host ('OpenXR runtime: ' + $OpenXrRuntime + ' - ' + $FgoRuntimeManifest)
    if ($OpenXrRuntime -eq 'SteamVR') {
        Write-Host 'Connect Steam Link and keep SteamVR running before launch. SteamVR is not started by this script.'
    } else { Write-Host 'Connect Quest through Virtual Desktop and keep the Streamer running.' }
    Write-Host 'Touch LEFT grip / trigger: Q / E, LEFT stick: menu directions. Both stick clicks: recenter.'
    Write-Host 'The PC window remains a stereo preview; OpenXR presents each eye in the headset.'
}
Write-Host 'Loading may show a black screen or publisher logos. Use the game window; close it to exit.'
$FgoProcess = Start-Process -FilePath $FgoExe -ArgumentList $FgoArguments -WorkingDirectory $FgoRuntimeDir -PassThru -RedirectStandardOutput (Join-Path $FgoSession 'stdout.log') -RedirectStandardError (Join-Path $FgoSession 'stderr.log')
$FgoRecord['pid'] = $FgoProcess.Id
# Retain the native handle before the child exits (Windows PowerShell 5.1).
$null = $FgoProcess.Handle
$FgoRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $FgoSession 'run.json') -Encoding UTF8
$FgoProcess.WaitForExit()
$FgoRecord['exit_code'] = $FgoProcess.ExitCode
$FgoRecord['ended_at'] = (Get-Date).ToString('o')
Copy-Item -LiteralPath (Join-Path $FgoRuntimeDir 'user\log') -Destination (Join-Path $FgoSession 'emulator_log') -Recurse
$FgoRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $FgoSession 'run.json') -Encoding UTF8
exit $FgoProcess.ExitCode
