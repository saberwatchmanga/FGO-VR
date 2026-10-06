param(
    [ValidateSet('01.00', '01.01')][string]$GameVersion = '01.01',
    [ValidateSet('Desktop', 'PcVr')][string]$Mode = 'Desktop',
    [ValidateRange(0, 600)][int]$HeadsetWaitSeconds = 60,
    [switch]$NoHeadsetPause,
    [ValidateSet('100', '110', '125', '150')][string]$RenderScale
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$FgoInstallDir = Split-Path -Parent $PSScriptRoot
$FgoRuntimeDir = Join-Path $FgoInstallDir 'runtime'
if ($Mode -eq 'PcVr') { $FgoRuntimeDir = Join-Path $FgoInstallDir 'runtime-vr' }
$FgoExe = Join-Path $FgoRuntimeDir 'shadps4.exe'
$FgoResolutionExe = Join-Path (Split-Path -Parent $FgoInstallDir) 'FGO-Resolution\runtime-pc\shadps4.exe'
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
$FgoGame = Join-Path $FgoInstallDir 'games\CUSA09078\eboot.bin'
if (-not (Test-Path -LiteralPath $FgoExe) -or -not (Test-Path -LiteralPath $FgoGame)) {
    throw 'FGO PC runtime or game file is missing. Read FGO-PC/README.md.'
}
if (Get-Process -Name shadps4 -ErrorAction SilentlyContinue | Where-Object { $_.Path -in @((Join-Path $FgoRuntimeDir 'shadps4.exe'), $FgoResolutionExe) }) {
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
$FgoRuntimeManifest = $null
if ($Mode -eq 'PcVr') {
    $FgoRuntimeManifest = Join-Path $env:ProgramFiles 'Virtual Desktop Streamer\OpenXR\virtualdesktop-openxr.json'
    if (-not (Test-Path -LiteralPath $FgoRuntimeManifest)) {
        throw 'Virtual Desktop VDXR runtime was not found. Install/open Virtual Desktop Streamer first.'
    }
    $FgoManifestData = Get-Content -LiteralPath $FgoRuntimeManifest -Raw | ConvertFrom-Json
    $FgoRuntimeLibrary = Join-Path (Split-Path -Parent $FgoRuntimeManifest) $FgoManifestData.runtime.library_path
    if (-not (Test-Path -LiteralPath $FgoRuntimeLibrary)) {
        throw 'VDXR manifest exists but its runtime DLL is missing.'
    }
    # A process-local override selects VDXR without changing the system OpenXR registration.
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
$FgoSession = Join-Path $FgoInstallDir ('sessions\' + $FgoSessionName)
New-Item -ItemType Directory -Path $FgoSession | Out-Null
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
    started_at = (Get-Date).ToString('o')
    mode = $Mode
    resolution_percent_requested = [int]$FgoScale
    openxr_runtime_manifest = $FgoRuntimeManifest
    environment = [ordered]@{}
}
foreach ($FgoEnv in @(Get-ChildItem Env: | Where-Object { $_.Name -like 'SHADPS4_*' -or $_.Name -eq 'XR_RUNTIME_JSON' })) {
    $FgoRecord.environment[$FgoEnv.Name] = $FgoEnv.Value
}
$FgoRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $FgoSession 'run.json') -Encoding UTF8
Write-Host ('FGO VR ' + $Mode + ' ' + $GameVersion + ' - Q / E: game confirm, arrows: menu selection, Enter: Options')
if ($Mode -eq 'PcVr') {
    Write-Host ('Internal resolution: ' + $FgoScale + '% of original dimensions (100 = OFF). Restart to change.')
    Write-Host 'Connect Quest through Virtual Desktop. Touch LEFT grip / trigger: Q / E, LEFT stick: menu directions.'
    Write-Host 'Both stick clicks: recenter. The PC window remains a stereo preview; VDXR presents each eye in the headset.'
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
