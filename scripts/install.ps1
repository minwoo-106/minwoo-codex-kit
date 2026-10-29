#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('User', 'Project')][string]$Scope = 'User',
    [string]$ProjectPath,
    [string]$CodexHome,
    [string]$SkillsRoot,
    [string[]]$Skills = @(),
    [string[]]$Profiles = @(),
    [switch]$ListProfiles,
    [switch]$SkipRules,
    [switch]$DryRun,
    [switch]$ReplaceExisting
)
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install.py'
$installArgs = @($installer, '--scope', $Scope.ToLowerInvariant())
if ($ProjectPath) { $installArgs += @('--project', $ProjectPath) }
if ($CodexHome) { $installArgs += @('--codex-home', $CodexHome) }
if ($SkillsRoot) { $installArgs += @('--skills-root', $SkillsRoot) }
foreach ($skill in $Skills) { $installArgs += @('--skill', $skill) }
foreach ($profile in $Profiles) { $installArgs += @('--profile', $profile) }
if ($ListProfiles) { $installArgs += '--list-profiles' }
if ($SkipRules) { $installArgs += '--skip-rules' }
if ($DryRun) { $installArgs += '--dry-run' }
if ($ReplaceExisting) { $installArgs += '--replace-existing' }

# Python이 없어도 Windows 앱 실행 별칭만 존재할 수 있다.
$pythonCommand = $null
foreach ($candidate in @('python', 'python3', 'py')) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $probeArgs = @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)')
        if ($candidate -eq 'py') { $probeArgs = @('-3') + $probeArgs }
        & $candidate @probeArgs 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $pythonCommand = $candidate; break }
    }
}
if (-not $pythonCommand) { throw 'Python 3.10 이상을 설치한 뒤 다시 실행해 줘.' }
if ($pythonCommand -eq 'py') { $installArgs = @('-3') + $installArgs }
& $pythonCommand @installArgs
exit $LASTEXITCODE
