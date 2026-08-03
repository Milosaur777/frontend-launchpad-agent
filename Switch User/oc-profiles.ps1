# Switch between different opencode auth profiles under ~/.local/share/opencode/auth.json
# Profiles are saved as auth-<profile_name>.json in the same directory.
# The currently active profile name is tracked in current_profile.txt.
#
# Usage:
#   .\oc-profiles.ps1                     # interactive menu
#   .\oc-profiles.ps1 switch <profile>    # switch directly
#   .\oc-profiles.ps1 save <profile>      # save current auth to profile
#   .\oc-profiles.ps1 list                # list available profiles
#   .\oc-profiles.ps1 current             # show current profile

param(
    [string]$Command,
    [string]$ProfileName
)

$ErrorActionPreference = 'Stop'

# --------------------------------------------------------------------------- #
# Path / state setup
# --------------------------------------------------------------------------- #

$BaseDir = if ($env:OPENCODE_PROFILE_BASE_DIR) { $env:OPENCODE_PROFILE_BASE_DIR } else { "$env:USERPROFILE\.local\share\opencode" }
$AuthFile = Join-Path $BaseDir "auth.json"
$CurrentProfileFile = Join-Path $BaseDir "current_profile.txt"

# --------------------------------------------------------------------------- #
# Utility helpers
# --------------------------------------------------------------------------- #

function Write-Info($msg) { Write-Host $msg }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Die($msg) { Write-Error "Error: $msg"; exit 1 }

# --------------------------------------------------------------------------- #
# Core functions
# --------------------------------------------------------------------------- #

function Ensure-BaseDir {
    if (-not (Test-Path $BaseDir)) {
        New-Item -ItemType Directory -Path $BaseDir -Force | Out-Null
    }
}

function Get-Profiles {
    $profiles = @()
    Get-ChildItem -Path "$BaseDir\auth-*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        $name = $_.Name -replace '^auth-', '' -replace '\.json$', ''
        $profiles += $name
    }
    return ($profiles | Sort-Object)
}

function Get-CurrentStatus {
    if (Test-Path $CurrentProfileFile) {
        $recorded = (Get-Content $CurrentProfileFile -Raw).Trim()
        $profileFile = Join-Path $BaseDir "auth-$recorded.json"
        if ($recorded -and (Test-Path $profileFile)) {
            return @{ Name = $recorded; Valid = $true; Status = $recorded }
        } elseif ($recorded) {
            return @{ Name = $recorded; Valid = $false; Status = "$recorded (profile file missing)" }
        } else {
            return @{ Name = $null; Valid = $false; Status = "unset (empty tracking file)" }
        }
    } elseif (Test-Path $AuthFile) {
        return @{ Name = $null; Valid = $false; Status = "unknown (auth.json exists but no profile saved yet)" }
    } else {
        return @{ Name = $null; Valid = $false; Status = "unset (no auth.json)" }
    }
}

function Write-CurrentProfile($name) {
    Set-Content -Path $CurrentProfileFile -Value $name -NoNewline
}

function Validate-ProfileName($name) {
    if ([string]::IsNullOrEmpty($name)) {
        Write-Host "Profile name cannot be empty."
        return $false
    }
    if ($name -notmatch '^[A-Za-z0-9_-]+$') {
        Write-Host "Profile name may only contain letters, numbers, underscores, and hyphens."
        return $false
    }
    return $true
}

# --------------------------------------------------------------------------- #
# Core operations
# --------------------------------------------------------------------------- #

function Switch-ToProfile($profile) {
    $source = Join-Path $BaseDir "auth-$profile.json"
    if (-not (Test-Path $source)) {
        Die "Profile not found: '$profile'. Run with 'list' to see available profiles."
    }

    # Warn if opencode might be running
    $proc = Get-Process -Name "opencode" -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Warn "opencode appears to be running. Close it before switching profiles, then restart it."
    }

    Copy-Item -Path $source -Destination $AuthFile -Force
    Write-CurrentProfile $profile
    Write-Info "Switched to profile '$profile'."
}

function Save-ToProfile($profile) {
    if (-not (Test-Path $AuthFile)) {
        Die "No auth.json found at '$AuthFile'. Nothing to save."
    }

    $target = Join-Path $BaseDir "auth-$profile.json"
    if (Test-Path $target) {
        $ans = Read-Host "Profile '$profile' already exists. Overwrite? [y/N]"
        if ($ans -ne 'y' -and $ans -ne 'yes') {
            Write-Info "Aborted."
            return
        }
    }

    Copy-Item -Path $AuthFile -Destination $target -Force
    Write-CurrentProfile $profile
    Write-Info "Saved current auth.json to profile '$profile'."
}

# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

function Cmd-List {
    $profiles = Get-Profiles
    $status = Get-CurrentStatus

    Write-Info "Current profile: $($status.Status)"
    Write-Info ""

    if ($profiles.Count -eq 0) {
        Write-Info "No saved profiles found in $BaseDir"
        Write-Info "Tip: run with 'save <name>' to save your current auth.json as a profile."
    } else {
        Write-Info "Available profiles:"
        foreach ($p in $profiles) {
            if ($p -eq $status.Name -and $status.Valid) {
                Write-Host "  * $p  (active)"
            } else {
                Write-Host "    $p"
            }
        }
    }
}

function Cmd-Current {
    $status = Get-CurrentStatus
    Write-Info $status.Status
}

function Cmd-Switch($target) {
    if ([string]::IsNullOrEmpty($target)) { Die "Usage: .\oc-profiles.ps1 switch <profile_name>" }
    if (-not (Validate-ProfileName $target)) { exit 1 }
    Switch-ToProfile $target
}

function Cmd-Save($name) {
    if ([string]::IsNullOrEmpty($name)) { Die "Usage: .\oc-profiles.ps1 save <profile_name>" }
    if (-not (Validate-ProfileName $name)) { exit 1 }
    Save-ToProfile $name
}

# --------------------------------------------------------------------------- #
# Interactive menu
# --------------------------------------------------------------------------- #

function Show-InteractiveMenu {
    while ($true) {
        $profiles = Get-Profiles
        $status = Get-CurrentStatus

        Write-Host ""
        Write-Host "=== OpenCode Profile Switcher ==="
        Write-Host "Base directory : $BaseDir"
        Write-Host "Current profile: $($status.Status)"
        Write-Host ""
        Write-Host "1) Switch to a profile"
        Write-Host "2) Save current auth.json to a profile"
        Write-Host "3) List all profiles"
        Write-Host "q) Quit"
        Write-Host ""
        $action = Read-Host "Choose an action [1-3, q]"
        Write-Host ""

        switch ($action) {
            '1' {
                if ($profiles.Count -eq 0) {
                    Write-Info "No saved profiles found. Use option 2 to save the current auth.json first."
                    continue
                }
                for ($i = 0; $i -lt $profiles.Count; $i++) {
                    $p = $profiles[$i]
                    if ($p -eq $status.Name -and $status.Valid) {
                        Write-Host "$($i+1)) $p  (active)"
                    } else {
                        Write-Host "$($i+1)) $p"
                    }
                }
                $sel = Read-Host "Select a profile [1-$($profiles.Count), q]"
                if ($sel -eq 'q' -or $sel -eq 'quit') { continue }
                $idx = 0
                if ([int]::TryParse($sel, [ref]$idx)) {
                    if ($idx -ge 1 -and $idx -le $profiles.Count) {
                        Switch-ToProfile $profiles[$idx - 1]
                    } else {
                        Write-Info "Please enter a number from 1 to $($profiles.Count)."
                    }
                } else {
                    Write-Info "Please enter a number or q."
                }
            }
            '2' { Save-CurrentProfile }
            '3' { Cmd-List }
            { $_ -eq 'q' -or $_ -eq 'quit' } { Write-Info "Goodbye."; exit 0 }
            default { Write-Info "Invalid choice. Please enter 1, 2, 3, or q." }
        }
    }
}

function Save-CurrentProfile {
    if (-not (Test-Path $AuthFile)) {
        Write-Info "No auth.json found. Nothing to save."
        return
    }
    $status = Get-CurrentStatus
    $default = if ($status.Valid) { $status.Name } else { "" }
    $name = if ($default) { Read-Host "Profile name [$default]" } else { Read-Host "Profile name" }
    if ($name -eq 'q' -or $name -eq 'quit') { return }
    if ([string]::IsNullOrEmpty($name) -and $default) { $name = $default }
    if (-not (Validate-ProfileName $name)) { return }
    Save-ToProfile $name
}

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

Ensure-BaseDir

switch ($Command) {
    'switch'  { Cmd-Switch $ProfileName }
    'save'    { Cmd-Save $ProfileName }
    'list'    { Cmd-List }
    'current' { Cmd-Current }
    ''        { Show-InteractiveMenu }
    '--help'  {
        Write-Host "Usage: .\oc-profiles.ps1 [switch|save|list|current] [profile_name]"
        Write-Host ""
        Write-Host "  (no args)        interactive menu"
        Write-Host "  switch <name>    switch to a saved profile"
        Write-Host "  save <name>      save current auth.json as a profile"
        Write-Host "  list             list all profiles"
        Write-Host "  current          print current profile name"
    }
    default { Die "Unknown command: '$Command'. Run with --help for usage." }
}
