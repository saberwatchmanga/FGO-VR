# Resolve an installed runtime without starting Steam/SteamVR or changing registration.
function Resolve-FgoOpenXrManifest {
    param(
        [ValidateSet('VDXR', 'SteamVR')][string]$Runtime,
        [string]$ManifestPath
    )
    $FgoCandidates = @()
    if ($ManifestPath) {
        $FgoCandidates += $ManifestPath
    } elseif ($Runtime -eq 'VDXR') {
        $FgoCandidates += Join-Path $env:ProgramFiles 'Virtual Desktop Streamer\OpenXR\virtualdesktop-openxr.json'
    } else {
        # OpenVR records the real SteamVR installation, including other Steam libraries.
        $FgoLocalRoots = @([Environment]::GetFolderPath('LocalApplicationData'))
        if ($env:USERPROFILE) {
            # Some desktop sandboxes redirect LocalAppData; the user's install remains here.
            $FgoLocalRoots += Join-Path $env:USERPROFILE 'AppData\Local'
        }
        foreach ($FgoLocalRoot in @($FgoLocalRoots | Select-Object -Unique)) {
            $FgoVrPathsFile = Join-Path $FgoLocalRoot 'openvr\openvrpaths.vrpath'
            if (Test-Path -LiteralPath $FgoVrPathsFile -PathType Leaf) {
                try {
                    $FgoVrPaths = Get-Content -LiteralPath $FgoVrPathsFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    foreach ($FgoVrRoot in @($FgoVrPaths.runtime)) {
                        $FgoCandidates += Join-Path $FgoVrRoot 'steamxr_win64.json'
                    }
                } catch { Write-Warning 'Unable to read OpenVR paths; checking other SteamVR locations.' }
            }
        }
        $FgoRegistered = Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Khronos\OpenXR\1' -ErrorAction SilentlyContinue
        if ($FgoRegistered -and $FgoRegistered.PSObject.Properties['ActiveRuntime'] -and
            (Split-Path -Leaf $FgoRegistered.ActiveRuntime) -eq 'steamxr_win64.json') {
            $FgoCandidates += $FgoRegistered.ActiveRuntime
        }
        $FgoSteamRoots = @()
        $FgoSteamKey = Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue
        if ($FgoSteamKey -and $FgoSteamKey.PSObject.Properties['SteamPath']) {
            $FgoSteamRoots += $FgoSteamKey.SteamPath
        }
        if (${env:ProgramFiles(x86)}) {
            $FgoSteamRoots += Join-Path ${env:ProgramFiles(x86)} 'Steam'
        }
        foreach ($FgoSteamRoot in @($FgoSteamRoots | Select-Object -Unique)) {
            $FgoCandidates += Join-Path $FgoSteamRoot 'steamapps\common\SteamVR\steamxr_win64.json'
            $FgoLibrariesFile = Join-Path $FgoSteamRoot 'steamapps\libraryfolders.vdf'
            if (Test-Path -LiteralPath $FgoLibrariesFile -PathType Leaf) {
                $FgoLibraries = Get-Content -LiteralPath $FgoLibrariesFile -Raw -Encoding UTF8
                foreach ($FgoLibrary in [regex]::Matches($FgoLibraries, '"path"\s+"([^"]+)"')) {
                    $FgoLibraryRoot = $FgoLibrary.Groups[1].Value.Replace('\\', '\')
                    $FgoCandidates += Join-Path $FgoLibraryRoot 'steamapps\common\SteamVR\steamxr_win64.json'
                }
            }
        }
    }
    $FgoFailures = @()
    foreach ($FgoCandidate in @($FgoCandidates | Select-Object -Unique)) {
        if (-not (Test-Path -LiteralPath $FgoCandidate -PathType Leaf)) { continue }
        try {
            $FgoResolvedManifest = (Resolve-Path -LiteralPath $FgoCandidate).ProviderPath
            $FgoManifest = Get-Content -LiteralPath $FgoResolvedManifest -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($Runtime -eq 'SteamVR' -and $FgoManifest.runtime.name -ne 'SteamVR') {
                throw 'The selected manifest is not a SteamVR runtime.'
            }
            if ($Runtime -eq 'VDXR' -and $FgoManifest.runtime.name -notlike 'VirtualDesktopXR*') {
                throw 'The selected manifest is not a VDXR runtime.'
            }
            $FgoLibrary = [string]$FgoManifest.runtime.library_path
            if ([string]::IsNullOrWhiteSpace($FgoLibrary)) { throw 'Runtime library_path is empty.' }
            if (-not [System.IO.Path]::IsPathRooted($FgoLibrary)) {
                $FgoLibrary = Join-Path (Split-Path -Parent $FgoResolvedManifest) $FgoLibrary
            }
            if (-not (Test-Path -LiteralPath $FgoLibrary -PathType Leaf)) { throw 'Runtime DLL is missing.' }
            return $FgoResolvedManifest
        } catch {
            $FgoFailures += ($FgoCandidate + ': ' + $_.Exception.Message)
        }
    }
    $FgoHint = if ($Runtime -eq 'SteamVR') {
        'Install SteamVR. If detection fails, pass -OpenXrManifest with the full path to steamxr_win64.json.'
    } else { 'Install/open Virtual Desktop Streamer first.' }
    throw ($Runtime + ' OpenXR runtime was not found or is invalid. ' + $FgoHint + ' ' + ($FgoFailures -join '; '))
}
