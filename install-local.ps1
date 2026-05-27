$ErrorActionPreference = "Stop"

$Source = Join-Path $PSScriptRoot "mutsumi"
$Destination = Join-Path $env:USERPROFILE ".codex\pets\mutsumi"

if (-not (Test-Path $Source)) {
  throw "Missing source pet folder: $Source"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force

Write-Host "Installed Mutsumi pet to $Destination"
Get-ChildItem -File $Destination | Sort-Object Name | Format-Table Name, Length -AutoSize
